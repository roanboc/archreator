#!/usr/bin/env python3
"""Read the model, and answer the questions a table cannot.

The Markdown under `architecture/` is the source of truth, and this reads it
fresh on every run. There is no second store: no database to rebuild, no cache
to invalidate, nothing that can answer from a revision the model has moved on
from.

    model.py --project . trace CAP3     # what would a change here touch?
    model.py --project . coverage       # what is not grounded, and what
                                        # is not yet approved?
    model.py --project . inventory      # one line per element
    model.py --project . export         # write .model/model.json

The tool lives in the plugin and reads a project named with `--project`.

**Why there is no database any more.** There was one, and in the largest real
model built on this method it was stale — it answered from a projection built
before a course of action had been added, confidently and with no way for the
reader to tell. Parsing every document of that model takes well under a
second, which is not a cost worth a cache, and certainly not one worth a cache
that can be wrong. `export` still writes JSON for a consumer that genuinely
cannot read Markdown — a dashboard, a report — but nothing in the method reads
it back.

`inventory` is the point of this script for anyone doing a large edit: diffing
the inventory of two commits says exactly which elements were added, dropped or
renamed, which reading a hundred files does not.

**`realized_by` is the one place language leaks in.** Every other field is read
from the identifier, the folder or the notation, all of which survive
translation. Which *column* holds a realization is fixed by no rule, so it is
matched against a short list of headings and left empty when none matches.
`attrs` always carries every column verbatim, so nothing is lost when the guess
fails — consult it rather than teaching this list a new language.
"""
import argparse
import os
import json
import sys
from collections import defaultdict
from pathlib import Path

# --------------------------------------------------------------------------
# This tool runs from the plugin and reads a project. The parse it needs -
# `model_graph.py` - lives in that project's `scripts/`, beside the two
# validators, because a project has to be able to check itself with no plugin
# installed and no network.
#
# **One copy of the parse, not two.** Shipping a second copy here would put the
# document convention in two files that drift apart silently, which is the
# thing `model_graph.py` exists to prevent one level down. So this imports the
# project's copy, and says plainly what to do when there is none.
# --------------------------------------------------------------------------
def _project_root(argv: list[str]) -> Path:
    for index, argument in enumerate(argv):
        if argument == "--project" and index + 1 < len(argv):
            return Path(argv[index + 1]).resolve()
        if argument.startswith("--project="):
            return Path(argument.split("=", 1)[1]).resolve()
    return Path.cwd().resolve()


def _find_parse(root: Path) -> Path | None:
    """The project's parse — beside it, or at the enclosing repository root.

    A repository that holds one model keeps `scripts/` beside `architecture/`.
    A repository that holds several trees keeps one `scripts/` at its root —
    the worked-models layout — so `--project <tree>` walks up to find it. The
    walk stops at the repository boundary: what sits above a `.git` belongs to
    somebody else. And a tree served by a root it walked up to must carry a
    model of its own (`architecture/`, hard-coded here because the parse that
    names the constant is what this function is looking for) — otherwise a
    mistyped `--project` would silently bind to the repository root and
    answer for the whole repository.
    """
    if not root.is_dir():
        return None
    for candidate in (root, *root.parents):
        parse = candidate / "scripts" / "model_graph.py"
        if parse.is_file():
            if candidate != root and not (root / "architecture").is_dir():
                return None
            return parse
        if (candidate / ".git").exists():
            return None
    return None


_ROOT = _project_root(sys.argv[1:])
_PARSE = _find_parse(_ROOT)
if _PARSE is None:
    if {"-h", "--help"} & set(sys.argv[1:]):
        print(__doc__)
        sys.exit(0)
    sys.exit(
        f"No archreator project at {_ROOT}: expected a directory holding "
        f"architecture/, with scripts/model_graph.py beside it or at the "
        f"enclosing repository root.\n"
        f"Run this from a project's root, or pass --project <path>."
    )
sys.path.insert(0, str(_PARSE.parent))

from model_graph import (
    MODEL_DIR,
    PENDING_MARKERS,
    REPO_ROOT,
    find_projects,
    neighbourhood,
    parse_project,
    project_key,
    qualified,
)

# Column headings that name what realizes an element. Best-effort, and the
# only language-dependent reading in the projection — see the module docstring.
REALIZATION_HEADERS = {
    "realized by",
    "realised by",
    "realizada por",
    "realizado por",
    "realizadas por",
    "realizados por",
}

# The interchange format's version. A second project fetching this file is
# reading something it does not control, built by a version of the method it
# may not have — so it gets a number to compare rather than a shape to guess
# at. Bump it when a consumer that knew the old shape would misread the new
# one; adding a field nobody has to read is not that.
SCHEMA_VERSION = 3



def realized_by(attrs: dict[str, str]) -> str:
    for header, value in attrs.items():
        if header.strip().lower() in REALIZATION_HEADERS:
            return value
    return ""


def project_name(project: Path) -> str:
    """How a project is named in the projection: its path, or "." at the root."""
    if project == REPO_ROOT:
        return "."
    return str(project.relative_to(REPO_ROOT)).replace("\\", "/")


def collect() -> list[dict]:
    """Every project in the repository, parsed in full."""
    collected = []
    for project in find_projects():
        parsed = parse_project(project, detail=True)
        if not parsed.elements:
            # An unfilled scaffold. Its layer READMEs are illustrative by
            # design, so projecting them would publish examples as elements.
            continue
        collected.append(
            {
                "project": project_name(project),
                "model": f"{project_name(project)}/{MODEL_DIR}".lstrip("./"),
                "elements": [
                    {
                        "id": element.id,
                        "local": element.local,
                        "prefix": element.prefix,
                        "type": element.type,
                        "group": element.group,
                        "domain": element.domain,
                        "parent": element.parent,
                        "name": element.name,
                        "doc": element.doc,
                        "layer": element.layer,
                        "layer_no": element.layer_no,
                        "status": element.status,
                        "retired": element.retired,
                        "realized_by": realized_by(element.attrs),
                        "attrs": element.attrs,
                    }
                    for element in sorted(parsed.elements.values(), key=lambda e: e.id)
                ],
                "edges": [
                    {
                        "src": edge.src,
                        "dst": edge.dst,
                        "rel": edge.rel,
                        "doc": edge.doc,
                        "origin": edge.origin,
                        "pending": edge.pending,
                        "dst_project": edge.dst_project,
                    }
                    for edge in parsed.edges
                ],
                "mentions": [list(mention) for mention in parsed.mentions],
                "excerpts": [
                    {
                        "element": excerpt.element,
                        "doc": excerpt.doc,
                        "heading": excerpt.heading,
                        "body": excerpt.text,
                    }
                    for excerpt in parsed.excerpts
                ],
            }
        )
    return collected


def revision() -> str:
    """The commit this projection was built from, or "" outside a checkout.

    Published, a projection is a claim about a repository at a moment. Without
    the revision a consumer can tell that two fetches differ and not which is
    newer, which is the question they will actually have.
    """
    import subprocess

    try:
        result = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10, check=False,
        )
    except (OSError, subprocess.SubprocessError):  # pragma: no cover
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def write_json(projects: list[dict], path: Path) -> None:
    from datetime import datetime, timezone

    payload = {
        "_comment": (
            "Generated by the plugin's scripts/model.py from the Markdown "
            "under architecture/. Regenerated, never hand-edited; the "
            "Markdown is the source of truth."
        ),
        "schema": SCHEMA_VERSION,
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "revision": revision(),
        "projects": projects,
    }
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def suspect_names(projects: list[dict]) -> list[str]:
    """Catalogue rows that do not appear to name their element.

    `architecture-document-style` puts the name in the cell after the ID, and
    the projection reads it there rather than guessing which column is a name
    — guessing produces a confident wrong answer, which is worse than none.
    So the deviation is reported instead: when two elements defined in the
    same document come out with the same name, that column is almost always
    holding something else, a priority or a status that repeats down the rows.

    Language-independent, because it compares values rather than headers.
    """
    notes: list[str] = []
    for project in projects:
        by_doc: dict[tuple[str, str], list[str]] = {}
        for element in project["elements"]:
            if element["name"]:
                by_doc.setdefault((element["doc"], element["name"]), []).append(element["id"])
        for (doc, name), ids in sorted(by_doc.items()):
            if len(ids) > 1:
                notes.append(
                    f"{doc}: {', '.join(ids)} all read as \"{name}\" — the cell "
                    f"after the ID may not be the name column"
                )
    return notes


def label_census(projects: list[dict]) -> list[str]:
    """How many distinct words the model uses for a relationship, and how thinly.

    The projection carries a relationship label verbatim and maps it onto
    nothing — see the module docstring, and `stack-selection` on why a guess at
    ArchiMate's vocabulary is worse than an honest string. That decision is
    right and it has a cost: nothing stops one model calling the same
    relationship four things.

    So this **reports** and never enforces. A controlled list would have to be
    translated into every language a model can be written in, which is the one
    thing the parse refuses to do. A count, printed where the author will see
    it, is enough for somebody to converge on their own — and a label used once
    is not a defect, it is just the thing worth looking at first.
    """
    counts: dict[str, int] = {}
    for project in projects:
        for edge in project["edges"]:
            if edge["origin"] == "identifier":
                continue  # structure, not a word anybody chose
            counts[edge["rel"]] = counts.get(edge["rel"], 0) + 1
    if not counts:
        return []
    once = sorted(label for label, n in counts.items() if n == 1)
    lines = [
        f"{sum(counts.values())} stated relationship(s) using "
        f"{len(counts)} distinct label(s); {len(once)} used exactly once."
    ]
    if once:
        shown = ", ".join(once[:8])
        lines.append(f"  used once: {shown}{', …' if len(once) > 8 else ''}")
    return lines


def print_inventory(projects: list[dict]) -> None:
    """One line per element, stable enough to diff between two commits."""
    for project in projects:
        for element in project["elements"]:
            print(
                " · ".join(
                    (
                        project["project"],
                        element["layer"] or "-",
                        element["id"],
                        element["type"] or "?",
                        element["name"] or "-",
                        element["status"] or "?",
                        element["doc"],
                    )
                )
                + (" · RETIRED" if element["retired"] else "")
            )


def label(element_id: str, name: str, kind: str) -> str:
    if not kind and not name:
        # An edge may name an ID the parse never saw defined; check_model.py is
        # what reports that, so here it is shown rather than swallowed.
        return f"{element_id} (undefined)"
    return f"{element_id} · {kind or '?'} · {name or '—'}"


def find(parsed_all: list, wanted: str, scope: str) -> list[tuple]:
    """Every (project, element) whose local or qualified ID matches `wanted`."""
    hits = []
    for parsed in parsed_all:
        key = project_key(parsed.project)
        if scope and scope not in key:
            continue
        for element in parsed.elements.values():
            if wanted in (element.id, element.local):
                hits.append((parsed, element))
    return hits


def trace(parsed_all: list, wanted: str, depth: int, scope: str) -> int:
    """What a change to one element would touch.

    Not a lookup: the answer is reached by following relationships across
    layers, and following them by hand across a hundred Markdown files is how a
    real dependency gets missed.
    """
    matches = find(parsed_all, wanted, scope)
    if not matches:
        print(f"No element `{wanted}` in any project. Try `coverage` for what is there.")
        return 0
    if len(matches) > 1:
        print(f"`{wanted}` is defined in {len(matches)} projects:")
        for parsed, element in matches:
            print(f"  {project_key(parsed.project)}: "
                  f"{label(element.id, element.name, element.type)}")
        print("\nNarrow it with --scope, naming any part of the path above.")
        return 0

    parsed, element = matches[0]
    home = project_key(parsed.project)
    print(label(element.id, element.name, element.type))
    print(f"  defined in {element.doc}")
    if element.status and element.status != "validated":
        print(f"  {element.status.upper()} — not approved at a gate")
    if realized_by(element.attrs):
        print(f"  realized by {realized_by(element.attrs)}")
    if element.retired:
        print("  RETIRED")
    print()

    others = [q for q in parsed_all if q is not parsed]
    reached, edges = neighbourhood(
        parsed, qualified(home, element.id), depth, extra=others
    )

    # Every element the walk saw, wherever it was defined, so a far end can be
    # named rather than printed as a bare identifier.
    known = {}
    for source in parsed_all:
        key = project_key(source.project)
        for other in source.elements.values():
            known[qualified(key, other.id)] = (key, other)

    rings: dict[int, list[str]] = defaultdict(list)
    seen = {qualified(home, element.id)}
    for a, b, edge in edges:
        for near, far, arrow in ((a, b, "→"), (b, a, "←")):
            if reached[near] >= reached[far] or far in seen:
                continue
            marker = " (pending)" if edge.pending else ""
            far_key, far_element = known.get(far, (None, None))
            # A neighbour in another model is shown as being in one. Printing a
            # bare identifier would make a federated walk read as though
            # everything it found were local.
            elsewhere = f"  [{far_key}]" if far_key and far_key != home else ""
            shown = (
                label(far_element.local, far_element.name, far_element.type)
                if far_element
                else label(far.split("::", 1)[-1], "", "")
            )
            rings[reached[far]].append(
                f"  {arrow} {edge.rel}{marker} {arrow} {shown}{elsewhere}"
            )
            seen.add(far)

    for hop in sorted(rings):
        print(f"Hop {hop} — {len(rings[hop])} element(s):")
        for line in sorted(rings[hop]):
            print(line)
        print()

    docs = sorted({
        doc for doc, named in parsed.mentions
        if named == element.id and doc != element.doc
    })
    if docs:
        print(f"Named in {len(docs)} other document(s):")
        for doc in docs:
            print(f"  {doc}")
        print()

    print(
        f"{len(seen) - 1} element(s) within {depth} hop(s). An edge label is the column "
        f"header or the relationship cell it was declared in, carried through unmapped — "
        f"nothing here guesses at ArchiMate relationship types."
    )
    print(
        "The walk is undirected: a catalogue states a connection from whichever end "
        "owns the row, so an arrow here shows which way it was written, not which "
        "way it matters. It crosses models: a neighbour in another one carries its "
        "name in brackets."
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


def coverage(projects: list[dict]) -> int:
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
    does not say. A reference made inside the document that defines the element
    is not an edge — correctly, since that is a definition talking about itself
    — so a driver named by five stakeholders in its own motivation document
    would look unreferenced. An honest silence beats a confident list of
    non-findings.
    """
    if not projects:
        print("No model found — nothing to report.")
        return 0

    for entry in sorted(projects, key=lambda p: p["project"]):
        project, rows = entry["project"], entry["elements"]
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



WORK_DIR = ".archreator/work"

MKDOCS = """\
# Generated by scripts/model.py portal. Not committed, not edited: everything
# under .archreator/ is regenerated on demand and gitignored.
site_name: {name}
docs_dir: {docs}
site_dir: {site}
use_directory_urls: false
theme:
  name: material
  features: [navigation.indexes, navigation.top, search.highlight, toc.follow]
markdown_extensions:
  - admonition
  - attr_list
  - md_in_html
  - tables
  - toc: {{permalink: true}}
  - pymdownx.details
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
plugins:
  search: {{}}
"""


def portal(project: Path) -> int:
    """The model as a website, for a reader who will not open a repository.

    **Stock MkDocs Material, and nothing of ours.** The config below is the
    whole of it: a theme, Mermaid, and search. There was a custom theme
    directory once — an overridden template, a comment box, a hand-written
    pan-and-zoom viewer, a PDF cover — five hundred lines of front-end that had
    to keep working across two upstream projects, to render documents that
    render fine without them.

    It writes into `.archreator/work/portal/`, which is gitignored, because a
    published copy that lives in the repository is the second model everyone
    edits instead.
    """
    if not (project / MODEL_DIR).is_dir():
        print(f"No {MODEL_DIR}/ under {project} — nothing to render.")
        return 1
    work = project / WORK_DIR / "portal"
    work.mkdir(parents=True, exist_ok=True)
    config = work / "mkdocs.yml"
    config.write_text(
        MKDOCS.format(
            name=f"{project.name} — architecture",
            docs=(project / "architecture").resolve().as_posix(),
            site=(work / "site").resolve().as_posix(),
        ),
        encoding="utf-8",
    )
    # Relative to where the caller is standing, not to the project: the
    # printed command has to work when pasted from a multi-tree repository
    # root that named a tree with --project.
    shown = os.path.relpath(config)
    print(f"Wrote {shown}. Build it with:")
    print(f"  uvx --with mkdocs-material mkdocs build -f {shown}")
    print(f"  uvx --with mkdocs-material mkdocs serve -f {shown}")
    print()
    print("The site is a rendering. The Markdown stays the model, and")
    print(f"{WORK_DIR}/ is gitignored so no copy of it can be committed.")
    return 0


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):  # pragma: no cover
            pass

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    # Read before argparse runs, by the bootstrap at the top of this file: it
    # decides which project's parse to import, which has to happen at import
    # time. Declared here so it appears in --help and is not rejected.
    parser.add_argument(
        "--project", default=".",
        help="the project to read (default: the working directory)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    t = sub.add_parser("trace", help="what a change to one element would touch")
    t.add_argument("element", help="an element ID, qualified or bare")
    t.add_argument("--depth", type=int, default=2, help="how many hops (default: 2)")
    t.add_argument("--scope", default="",
                   help="narrow to one model, where the repository holds several")

    sub.add_parser("coverage", help="what is grounded, and what is not yet approved")
    sub.add_parser("inventory", help="one line per element; writes nothing")
    sub.add_parser("portal", help="write a stock MkDocs config into .archreator/work/portal/")

    e = sub.add_parser("export", help="write model.json for a non-Markdown consumer")
    e.add_argument("--out", type=Path, default=REPO_ROOT / ".model",
                   help="directory to write model.json into (default: .model/)")

    args = parser.parse_args()

    if args.command == "portal":
        # The project the caller named, not the repository root: in a
        # repository of several trees, a portal renders one tree's model.
        return portal(_ROOT)

    if args.command == "trace":
        parsed_all = [
            parse_project(project, detail=True) for project in find_projects()
        ]
        parsed_all = [p for p in parsed_all if p.elements]
        if not parsed_all:
            print("No model found — nothing to trace.")
            return 0
        return trace(parsed_all, args.element, args.depth, args.scope)

    projects = collect()
    if not projects:
        print("No model found — nothing to report.")
        return 0

    if args.command == "coverage":
        return coverage(projects)
    if args.command == "inventory":
        print_inventory(projects)
        return 0

    args.out.mkdir(parents=True, exist_ok=True)
    write_json(projects, args.out / "model.json")
    out = args.out.relative_to(REPO_ROOT) if args.out.is_relative_to(REPO_ROOT) else args.out
    for project in projects:
        print(
            f"  {project['model']}: {len(project['elements'])} element(s), "
            f"{len(project['edges'])} edge(s), {len(project['mentions'])} mention(s)"
        )
    print(f"Written to {out}/model.json. Nothing in the method reads it back.")

    for line in label_census(projects):
        print(line)

    notes = suspect_names(projects)
    if notes:
        # Not an error: this is a faithful reading of what the documents say.
        # The documents are what would need changing.
        print("Names that look like they came from the wrong column:")
        for note in notes:
            print(f"  {note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
