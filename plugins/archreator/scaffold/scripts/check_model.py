#!/usr/bin/env python3
"""Check that element-ID references in this repo resolve to real elements.

`architecture-document-style` gives every element an ID (`G1`, `CAP3`, `SALES.BSVC3`) and
says an ID is assigned once and never reused, so that a stale reference
fails loudly rather than silently pointing at something else. Nothing
enforced that until this script: `check_links.py` verifies that a *link*
resolves, and an agent reading `relieves PAIN2` has no cheap way to notice
that `PAIN2` was deleted three initiatives ago.

**The parse lives in `model_graph.py`**, which this script imports. It moved
there when the published view of the model became a second consumer of the
same reading of the same convention; a second parser would have drifted from
this one silently. What stayed here is the judgement — the four checks below
and the exit code. Nothing is persisted: validation needs a parse, not a
store, so this script still builds the graph, checks it and exits.

Four things are checked, per project:

- **Dangling references** — every referenced ID resolves to a definition.
  A qualified reference (`SALES.BSVC3`) resolves inside that domain's
  folder under `domains/`; an unknown domain is an error.
- **Duplicate definitions** — no ID is defined twice.
- **Retired then live** — no ID appears in both a live table and a
  `## Retired` section. Retired IDs stay retired.
- **Orphan levels** — a leveled ID (`CAP1.2`, `BPROC7.2.1`) has the element
  one level up defined too. A hierarchical identifier that names a parent
  nobody wrote is the same defect as a dangling reference.
- **Undeclared status** — a document that defines an element says in its
  preamble how far it has been validated, with one of the three glyphs in
  `architecture-document-style` § Document status. A catalogue of elements
  somebody mentioned in a meeting and a layer a Requester approved look
  identical on the page, and an agent that cannot tell them apart will build
  on the wrong one. This is checked on the glyph, never on the word beside
  it, so it holds in a model written in any language.

An ID can carry two dot-separated qualifiers and they mean different things,
so the parser reads outwards from the type prefix: upper-case segments
*before* it are the domain path (`SALES.BSVC3`), numeric segments *after* it
are the catalogue's levels (`BSVC3.1`). Only the first makes a reference
qualified — `architecture-document-style` § Levels number hierarchically.

A **project** is the directory containing an `architecture/` folder, so IDs are
scoped per project and two projects may each own a `G1`.

**Only the numbered layers are checked.** They describe the current state.
`architecture/scope/`, `architecture/decisions/`, `architecture/reviews/` and `architecture/engagements/` live inside
`architecture/` too, but they are narrative *about* the model, and narrative
legitimately contains illustrations ("no component verifies that `PAIN2`
resolves"), hypotheticals, and references to elements that have since been
retired. They also cite elements in the same bolded
form a motivation document uses to define one, so a definition and a mention
are indistinguishable there.

The decisive argument is `RULE6`: a merged scope document is immutable. The
model moves on and the document does not, so it will eventually reference
something that no longer exists — and no edit is permitted to fix it.
Reference-checking a frozen document is incoherent, not merely awkward.

Deliberately not checked:

- `architecture/scope/`, `architecture/decisions/`, `architecture/reviews/` and `architecture/engagements/` inside
  `architecture/`, and anything outside `architecture/` entirely, per above.
- The scaffold under `scaffold/` — its layer READMEs and the skill files
  beside them carry illustrative IDs inside templates
  (`BSVC1`, `SALES.BSVC3`, `RULE7`); validating the documentation of the
  convention would fail on itself.
- A project whose `architecture/` defines no elements — an unfilled scaffold,
  whose layer READMEs are full of illustrative placeholders by design.
- Tables with no ID column — they predate the convention or hold prose.
  They are counted and reported as unvalidated coverage, not as errors.
- Fenced code blocks, for the same reason `check_links.py` skips them.
- Whether a "Realized by" cell points at a file that exists. That is the
  grounding rule, and it is still enforced only for links.
"""
import sys
from pathlib import Path

from model_graph import (
    MODEL_DIR,
    REPO_ROOT,
    domain_of,
    find_projects,
    parent_of,
    parse_project,
    qualifier_of,
)


def check_project(project: Path) -> tuple[list[str], int, int]:
    """Return (errors, definition count, unvalidated-table count)."""
    parsed = parse_project(project)
    errors: list[str] = sorted(parsed.duplicates)

    for element, md_file in sorted(parsed.retired.items()):
        if element in parsed.defined:
            errors.append(
                f"{md_file.relative_to(REPO_ROOT)}: `{element}` is retired but "
                f"still defined live in {parsed.defined[element].relative_to(REPO_ROOT)}"
            )

    for element, md_file in sorted(parsed.defined.items()):
        parent = parent_of(element)
        if parent and parent not in parsed.defined and parent not in parsed.retired:
            errors.append(
                f"{md_file.relative_to(REPO_ROOT)}: `{element}` is one level "
                f"below `{parent}`, which is not defined in this project"
            )

    # Keyed the same way `parsed.statuses` is, so the two line up without
    # either side having to reconstruct the other's paths.
    defining = {
        str(path.relative_to(REPO_ROOT)).replace("\\", "/")
        for path in set(parsed.defined.values()) | set(parsed.retired.values())
    }
    for doc, (status, count) in sorted(parsed.statuses.items()):
        if doc not in defining:
            # A document defining nothing - an index, a layer README of a
            # layer nobody has filled - owes no status. It has nothing whose
            # standing a reader could mistake.
            continue
        if count == 0:
            errors.append(
                f"{doc}: defines elements and declares no status. Open the "
                f"preamble with one of ○ (not started), ◐ (draft catalogue) "
                f"or ● (validated)"
            )
        elif count > 1:
            errors.append(
                f"{doc}: the preamble carries {count} status glyphs, so a "
                f"reader cannot tell which one it means"
            )
        elif not status:  # pragma: no cover - unreachable while count == 1
            errors.append(f"{doc}: unrecognised status glyph")

    seen: set[tuple[str, Path]] = set()
    for reference, md_file in parsed.references:
        if (reference, md_file) in seen:
            continue
        seen.add((reference, md_file))
        scope = domain_of(md_file, project)
        qualifier = qualifier_of(reference)
        candidates = [reference]
        if not qualifier and scope:
            candidates.insert(0, f"{scope}.{reference}")
        if any(
            candidate in parsed.defined or candidate in parsed.retired
            for candidate in candidates
        ):
            continue
        rel = md_file.relative_to(REPO_ROOT)
        if qualifier and qualifier not in parsed.domains:
            errors.append(f"{rel}: `{reference}` names unknown domain `{qualifier}`")
        else:
            errors.append(f"{rel}: `{reference}` is not defined in this project")

    return errors, len(parsed.defined), parsed.skipped


def main() -> int:
    # Findings carry em-dashes, notation glyphs and whatever a heading is
    # named in. A console that cannot encode them should show a replacement
    # character, not raise and take the whole run down with it.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):  # pragma: no cover - older or wrapped streams
            pass
    all_errors: list[str] = []
    summary: list[str] = []
    for project in find_projects():
        errors, defined, skipped = check_project(project)
        rel = project.relative_to(REPO_ROOT) if project != REPO_ROOT else Path(".")
        if not defined:
            # An unfilled template scaffold: its layer READMEs are full of
            # illustrative placeholders by design, so there is nothing to check.
            summary.append(f"  {rel}/{MODEL_DIR}: no elements defined — scaffold, not checked")
            continue
        all_errors.extend(errors)
        note = f", {skipped} table(s) without an ID column not validated" if skipped else ""
        summary.append(f"  {rel}/{MODEL_DIR}: {defined} element(s){note}")

    for line in summary:
        print(line)
    if all_errors:
        print("Element-ID problems found:")
        for error in all_errors:
            print(f"  {error}")
        return 1
    print("All element-ID references resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
