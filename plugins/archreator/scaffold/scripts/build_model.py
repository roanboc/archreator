#!/usr/bin/env python3
"""Project the model into JSON and SQLite, for consumers that cannot read Markdown.

The Markdown under `architecture/` is the source of truth. This writes a
second representation of it, which is a thing `stack-selection` spends a whole
section warning against — so the reason matters more than the mechanism.

**Why this exists.** `stack-selection` § A persisted projection needs one of
four triggers lists a non-agent consumer as one of them: *a dashboard, a
report or a rendered model cannot read Markdown tables*. A published view of
the model for stakeholders who will never open a repository is exactly that
consumer, and it is what fired the trigger. The projection is the difference
between a site that renders documents and a site that can answer "what is
`CAP2.3`, and what would break if it went away".

**The discipline that keeps it honest.** The projection is regenerated and
never hand-edited, it is not committed, and nothing reads it that could have
read the Markdown instead. Delete the output and nothing is lost. That is the
whole answer to the drift a derived store usually invites: a file that is
rebuilt from scratch on every run cannot fall behind the thing it is built
from.

Usage:

    python3 scripts/build_model.py               # write .model/model.{json,db}
    python3 scripts/build_model.py --out DIR     # somewhere else
    python3 scripts/build_model.py --inventory   # print, write nothing

`--inventory` prints one line per element and is the point of this script for
anyone doing a large edit: diffing the inventory of two commits says exactly
which elements were added, dropped or renamed, which reading 111 files does
not.

**Two deviations from the schema `stack-selection` specifies**, both recorded
here because the rulebook is the authority and this is the code disagreeing
with it:

- **A `project` column, and a compound primary key.** One repository can hold
  several models — `find_projects()` has always allowed it — and two of them
  may each own a `G1`. A bare `id` primary key would collide.
- **`realized_by` is best-effort, and it is the one place language leaks in.**
  Every other field is read from the identifier, the folder or the notation,
  all of which survive translation. Which *column* holds a realization is
  fixed by no rule, so it is matched against a short list of headings and left
  empty when none matches. `attrs` always carries every column verbatim, so
  nothing is lost when the guess fails — consult it rather than teaching this
  list a new language.
"""
import argparse
import json
import sqlite3
import sys
from pathlib import Path

from model_graph import MODEL_DIR, REPO_ROOT, find_projects, parse_project

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

SCHEMA = """
CREATE TABLE nodes(
    project     TEXT NOT NULL,
    id          TEXT NOT NULL,
    type        TEXT,
    layer       TEXT,
    name        TEXT,
    status      TEXT,
    doc         TEXT,
    realized_by TEXT,
    local       TEXT,
    prefix      TEXT,
    layer_group TEXT,
    layer_no    TEXT,
    domain      TEXT,
    parent      TEXT,
    retired     INTEGER NOT NULL DEFAULT 0,
    attrs       TEXT,
    PRIMARY KEY (project, id)
);
CREATE TABLE edges(
    project     TEXT NOT NULL,
    src         TEXT NOT NULL,
    dst         TEXT NOT NULL,
    rel         TEXT,
    doc         TEXT,
    origin      TEXT NOT NULL DEFAULT 'catalogue',
    pending     INTEGER NOT NULL DEFAULT 0,
    -- The model the far end belongs to. Empty for all but a reference that
    -- crosses a federation boundary, and read as `project` when it is.
    dst_project TEXT NOT NULL DEFAULT ''
);
CREATE TABLE excerpts(
    project TEXT NOT NULL,
    element TEXT NOT NULL,
    doc     TEXT NOT NULL,
    heading TEXT,
    body    TEXT NOT NULL
);
CREATE TABLE mentions(
    project TEXT NOT NULL,
    doc     TEXT NOT NULL,
    element TEXT NOT NULL
);
CREATE INDEX edges_src ON edges(project, src);
CREATE INDEX edges_dst ON edges(project, dst);
CREATE INDEX mentions_element ON mentions(project, element);
CREATE INDEX excerpts_element ON excerpts(project, element);
"""


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
            "Generated by scripts/build_model.py from the Markdown under "
            "architecture/. Regenerated, never hand-edited; the Markdown is "
            "the source of truth."
        ),
        "schema": SCHEMA_VERSION,
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "revision": revision(),
        "projects": projects,
    }
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def write_sqlite(projects: list[dict], path: Path) -> None:
    if path.exists():
        path.unlink()
    connection = sqlite3.connect(path)
    try:
        connection.executescript(SCHEMA)
        for project in projects:
            name = project["project"]
            connection.executemany(
                "INSERT INTO nodes(project, id, type, layer, name, status, doc,"
                " realized_by, local, prefix, layer_group, layer_no, domain, parent,"
                " retired, attrs)"
                " VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                [
                    (
                        name,
                        element["id"],
                        element["type"],
                        element["layer"],
                        element["name"],
                        element["status"],
                        element["doc"],
                        element["realized_by"],
                        element["local"],
                        element["prefix"],
                        element["group"],
                        element["layer_no"],
                        element["domain"],
                        element["parent"],
                        int(element["retired"]),
                        json.dumps(element["attrs"], ensure_ascii=False),
                    )
                    for element in project["elements"]
                ],
            )
            connection.executemany(
                "INSERT INTO edges(project, src, dst, rel, doc, origin, pending,"
                " dst_project) VALUES(?,?,?,?,?,?,?,?)",
                [
                    (
                        name,
                        edge["src"],
                        edge["dst"],
                        edge["rel"],
                        edge["doc"],
                        edge["origin"],
                        int(edge["pending"]),
                        edge["dst_project"],
                    )
                    for edge in project["edges"]
                ],
            )
            connection.executemany(
                "INSERT INTO mentions(project, doc, element) VALUES(?,?,?)",
                [(name, doc, element) for doc, element in project["mentions"]],
            )
            connection.executemany(
                "INSERT INTO excerpts(project, element, doc, heading, body)"
                " VALUES(?,?,?,?,?)",
                [
                    (name, e["element"], e["doc"], e["heading"], e["body"])
                    for e in project["excerpts"]
                ],
            )
        connection.commit()
    finally:
        connection.close()


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
        default=REPO_ROOT / ".model",
        help="directory to write model.json and model.db into (default: .model/)",
    )
    parser.add_argument(
        "--inventory",
        action="store_true",
        help="print one line per element and write nothing",
    )
    args = parser.parse_args()

    projects = collect()
    if not projects:
        print("No model found — nothing to project.")
        return 0

    if args.inventory:
        print_inventory(projects)
        return 0

    args.out.mkdir(parents=True, exist_ok=True)
    write_json(projects, args.out / "model.json")
    write_sqlite(projects, args.out / "model.db")

    out = args.out.relative_to(REPO_ROOT) if args.out.is_relative_to(REPO_ROOT) else args.out
    for project in projects:
        print(
            f"  {project['model']}: {len(project['elements'])} element(s), "
            f"{len(project['edges'])} edge(s), {len(project['mentions'])} mention(s)"
        )
    print(f"Projection written to {out}/model.json and {out}/model.db.")

    for line in label_census(projects):
        print(line)

    notes = suspect_names(projects)
    if notes:
        # Not an error: the projection is a faithful reading of what the
        # documents say. The documents are what would need changing.
        print("Names that look like they came from the wrong column:")
        for note in notes:
            print(f"  {note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
