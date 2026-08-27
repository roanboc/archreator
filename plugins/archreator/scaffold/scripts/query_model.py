#!/usr/bin/env python3
"""Ask the projection the two questions a model is kept for.

`build_model.py` writes the model as nodes and edges so that a consumer which
cannot read Markdown can use it. This is one of two such consumers — the other
is the navigator, and **they read the same database with the same query.**

Two questions, because these are the two that a table cannot answer:

    python3 scripts/query_model.py trace CAP3      # what would this touch?
    python3 scripts/query_model.py coverage        # what is not grounded, and
                                                   # what is not yet approved?

**`trace` is a traversal, and the traversal lives in `neighbourhood.sql`.**
"What does retiring this capability affect?" is not a lookup — the answer is
reached by following relationships across layers, and following them by hand
across a hundred Markdown files is how a real dependency gets missed.
`stack-selection` § A persisted projection needs one of four triggers names a
genuinely transitive question as one of the four, and says how to answer it:
"a `nodes`/`edges` pair traversed with recursive CTEs. At the scale a model
reaches, SQLite *is* the graph database."

That query is in a file rather than in this one because a browser has to run
it too. A walk implemented once here and once in JavaScript would drift, and
the copy that drifted would be the one in the browser, which nothing tests.

`coverage` also separates what a Requester has approved from what has only
been written down. A catalogue of elements somebody mentioned in a meeting and
a layer approved at a gate are the same shape on the page, and an agent that
reads the second kind out of the first will build confidently on nothing. The
document's own declared status is what tells them apart, and it is carried
through the projection onto every element defined there.

**`coverage` is a report, and deliberately not a gate.** Every element must
name what realizes it, and that rule is the one the validators do not enforce:
telling a repository path from a team name is fuzzy, and a check that fails
wrongly teaches people to ignore the checks that do not. So this prints what
looks ungrounded and **always exits 0**. A person reads the list and decides.
Wiring it into CI as a gate would recreate exactly the failure mode the method
argues against, which is why no `--strict` flag is offered.

Both commands read `.model/model.db`. When it is absent the projection is
built first, so a caller never has to run two commands to ask one question.

**One caveat inherited from the projection.** `realized_by` is the single
language-dependent field in the whole pipeline: it is matched against a short
list of column headings and left empty when none matches. An element reported
as ungrounded may therefore be a model written in a language that list has not
learned. The report says which case it cannot tell apart rather than implying a
finding it has not earned.
"""
import argparse
import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

from model_graph import PENDING_MARKERS, REPO_ROOT

DEFAULT_OUT = REPO_ROOT / ".model"
# `PENDING_MARKERS` comes from `model_graph` rather than being restated here:
# the projection reads the same convention to decide whether a relationship is
# live, and one convention written down twice drifts.
#
# How far `trace` walks by default. Two hops crosses one layer boundary in each
# direction, which is the blast radius a person can still hold in their head.
DEFAULT_DEPTH = 2
# The traversal, shared with the navigator. See the module docstring.
NEIGHBOURHOOD_SQL = Path(__file__).resolve().parent / "neighbourhood.sql"


def connect(out_dir: Path) -> sqlite3.Connection | None:
    """The projection, built first if it is not there yet."""
    path = out_dir / "model.db"
    if not path.is_file():
        import build_model

        projects = build_model.collect()
        if not projects:
            return None
        out_dir.mkdir(parents=True, exist_ok=True)
        build_model.write_json(projects, out_dir / "model.json")
        build_model.write_sqlite(projects, path)
        print(f"(projection was missing — built {path.relative_to(REPO_ROOT)})\n")
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def find(connection: sqlite3.Connection, wanted: str, scope: str) -> list[sqlite3.Row]:
    """Every element whose ID or local ID matches, case-insensitively.

    A model is scoped per project and two projects may each own a `G1`, so this
    returns every match and the caller decides what to do with more than one.
    """
    needle = wanted.strip().strip("`").upper()
    return connection.execute(
        "SELECT * FROM nodes WHERE (upper(id) = ? OR upper(local) = ?)"
        " AND project LIKE ? ORDER BY project, id",
        (needle, needle, f"%{scope}%"),
    ).fetchall()


def label(element_id: str, name: str, kind: str) -> str:
    if not kind and not name:
        # An edge may name an ID the parse never saw defined; check_model.py is
        # what reports that, so here it is shown rather than swallowed.
        return f"{element_id} (undefined)"
    return f"{element_id} · {kind or '?'} · {name or '—'}"


def trace(connection: sqlite3.Connection, wanted: str, depth: int, scope: str) -> int:
    matches = find(connection, wanted, scope)
    if not matches:
        print(f"No element `{wanted}` in any project. Try `coverage` for what is there.")
        return 0
    if len(matches) > 1:
        print(f"`{wanted}` is defined in {len(matches)} projects:")
        for row in matches:
            print(f"  {row['project']}: {label(row['id'], row['name'], row['type'])}")
        print("\nNarrow it with --project, naming any part of the path above.")
        return 0

    element = matches[0]
    print(label(element["id"], element["name"], element["type"]))
    print(f"  defined in {element['doc']}")
    if element["status"] and element["status"] != "validated":
        print(f"  {element['status'].upper()} — not approved at a gate")
    if element["realized_by"]:
        print(f"  realized by {element['realized_by']}")
    if element["retired"]:
        print("  RETIRED")
    print()

    rows = connection.execute(
        NEIGHBOURHOOD_SQL.read_text(encoding="utf-8"),
        {"project": element["project"], "root": element["id"], "depth": depth},
    ).fetchall()

    # The query returns the subgraph; this arranges it into rings, so the
    # nearest is printed before the far one and a reader can stop at the depth
    # they trust.
    rings: dict[int, list[str]] = defaultdict(list)
    seen: set[str] = {element["id"]}
    for row in rows:
        for near, far, arrow in (
            ("src", "dst", "→"),
            ("dst", "src", "←"),
        ):
            if row[f"{near}_hop"] >= row[f"{far}_hop"] or row[far] in seen:
                continue
            marker = " (pending)" if row["pending"] else ""
            rings[row[f"{far}_hop"]].append(
                f"  {arrow} {row['rel']}{marker} {arrow} "
                f"{label(row[far], row[f'{far}_name'], row[f'{far}_type'])}"
            )
            seen.add(row[far])

    for hop in sorted(rings):
        print(f"Hop {hop} — {len(rings[hop])} element(s):")
        for line in sorted(rings[hop]):
            print(line)
        print()

    docs = [
        row["doc"]
        for row in connection.execute(
            "SELECT DISTINCT doc FROM mentions WHERE project = ? AND element = ?"
            " AND doc <> ? ORDER BY doc",
            (element["project"], element["id"], element["doc"]),
        )
    ]
    if docs:
        print(f"Named in {len(docs)} other document(s):")
        for doc in docs:
            print(f"  {doc}")
        print()

    print(
        f"{len(seen) - 1} element(s) within {depth} hop(s). An edge label is the column "
        f"header or the relationship cell it was declared in, carried through unmapped — "
        f"the projection does not guess at ArchiMate relationship types."
    )
    print(
        "The walk is undirected: a catalogue states a connection from whichever end "
        "owns the row, so an arrow here shows which way it was written, not which "
        "way it matters."
    )
    return 0


def is_pending(element: dict) -> bool:
    """Does the element say out loud that nothing realizes it yet?

    Checked across every column rather than only the realization one, because
    the marker is routinely written in a State or Status cell instead.
    """
    haystack = " ".join([element["realized_by"], *element["attrs"].values()]).lower()
    return any(marker in haystack for marker in PENDING_MARKERS)


def catalogue_of(element: dict) -> tuple[str, frozenset]:
    """Which catalogue table an element was defined in.

    The projection carries every column of a row under its own header, so two
    elements share a table exactly when they share a header set. That is the
    unit realization has to be judged in: one document routinely holds several
    catalogues — capabilities with a realization column, resources with a state
    column — and judging them together reports every resource as ungrounded.

    Language-independent, because it compares the shape of the row rather than
    the words in its headers.
    """
    return element["doc"], frozenset(element["attrs"])


def coverage(connection: sqlite3.Connection) -> int:
    """What is grounded, what says it is not yet, and what neither.

    **The unit is the catalogue table, not the element and not the document.**
    Whether an element owes a realization is decided by the table it sits in: a
    table where some rows name what realizes them and others leave it blank has
    a real omission. A table with no realization column at all is not modeling
    realization — the canvases of `0_business-design/` hold no ArchiMate
    elements and owe nothing, and a motivation table may ground its elements in
    prose instead.

    Reporting every element of the second kind is how a check becomes noise,
    and a noisy check is the one people learn to skip. So a table that grounds
    nothing is reported once, as a table.

    **One question deliberately not answered: what nothing points at.** An
    element no other element references would be worth knowing about, and this
    cannot tell. The projection drops a reference made inside the document that
    defines the element — correctly, since that is a definition talking about
    itself — so a driver named by five stakeholders in its own motivation
    document looks unreferenced. Answering it would mean re-reading the
    Markdown, which is the one thing a consumer of the projection should not
    do. An honest silence beats a confident list of non-findings.
    """
    projects = [
        row["project"]
        for row in connection.execute("SELECT DISTINCT project FROM nodes ORDER BY project")
    ]
    if not projects:
        print("No model found — nothing to report.")
        return 0

    for project in projects:
        rows = [
            dict(row, attrs=json.loads(row["attrs"] or "{}"))
            for row in connection.execute("SELECT * FROM nodes WHERE project = ?", (project,))
        ]
        live = [e for e in rows if not e["retired"]]
        retired = len(rows) - len(live)

        # Which tables model realization at all: the ones where at least one row
        # filled the column in.
        grounds: dict[tuple[str, frozenset], bool] = defaultdict(bool)
        for element in live:
            if element["realized_by"]:
                grounds[catalogue_of(element)] = True

        grounded = [e for e in live if e["realized_by"] and not is_pending(e)]
        pending = [e for e in live if is_pending(e)]
        gaps = [
            e for e in live
            if grounds[catalogue_of(e)] and not e["realized_by"] and not is_pending(e)
        ]
        silent = sorted({e["doc"] for e in live if not grounds[catalogue_of(e)]})

        draft = [e for e in live if e["status"] and e["status"] != "validated"]
        undeclared = [e for e in live if not e["status"]]

        print(f"{project} — {len(live)} live element(s), {retired} retired")
        print(f"  validated             {len(live) - len(draft) - len(undeclared):4d}")
        print(f"  draft, not approved   {len(draft):4d}")
        if undeclared:
            print(f"  status undeclared     {len(undeclared):4d}")
        print(f"  grounded              {len(grounded):4d}")
        print(f"  pending, on purpose   {len(pending):4d}")
        print(f"  blank beside grounded {len(gaps):4d}")
        print()

        if draft:
            by_status: dict[str, set[str]] = defaultdict(set)
            for element in draft:
                by_status[element["status"]].add(element["doc"])
            print("  Not approved at any gate. Nothing here may be built on, and")
            print("  every identifier in it can still be renumbered:")
            for status in sorted(by_status):
                print(f"    {status}")
                for doc in sorted(by_status[status]):
                    count = sum(1 for e in draft if e["doc"] == doc)
                    print(f"      {doc}  ({count} element(s))")
            print()

        if gaps:
            print("  Their own catalogue grounds other rows and leaves these blank.")
            print("  This is the closest thing to a finding the report has:")
            by_doc: dict[str, list[dict]] = defaultdict(list)
            for element in gaps:
                by_doc[element["doc"]].append(element)
            for doc in sorted(by_doc):
                print(f"    {doc}")
                for element in sorted(by_doc[doc], key=lambda e: e["id"]):
                    print(f"      {label(element['id'], element['name'], element['type'])}")
            print()

        if pending:
            print("  Explicitly pending — the list a Requester can work through:")
            for element in sorted(pending, key=lambda e: e["id"]):
                print(f"    {label(element['id'], element['name'], element['type'])}")
            print()

        if silent:
            print(f"  {len(silent)} document(s) ground nothing, which is usually correct —")
            print("  canvases hold no ArchiMate elements, and a motivation table may")
            print("  ground its elements in prose. Worth a glance only if one of these")
            print("  is a layer that should be naming artifacts:")
            for doc in silent:
                print(f"    {doc}")
            print()

    print("A report, not a gate. Nothing here fails a build.")
    return 0


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):  # pragma: no cover
            pass

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="directory holding model.db (default: .model/)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    walk = sub.add_parser("trace", help="what a change to one element would touch")
    walk.add_argument("element", help="an element ID, qualified or not — CAP3, SALES.BSVC1")
    walk.add_argument(
        "--depth", type=int, default=DEFAULT_DEPTH, help=f"hops to follow (default: {DEFAULT_DEPTH})"
    )
    walk.add_argument(
        "--project",
        default="",
        help="when one repository holds several models and they share an ID, "
        "any part of the model's path — two projects may each own a `G1`",
    )

    sub.add_parser("coverage", help="what is grounded, pending, unfound or unreferenced")

    args = parser.parse_args()
    connection = connect(args.out)
    if connection is None:
        print("No model found — nothing to query.")
        return 0
    try:
        if args.command == "trace":
            return trace(connection, args.element, max(1, args.depth), args.project)
        return coverage(connection)
    finally:
        connection.close()


if __name__ == "__main__":
    sys.exit(main())
