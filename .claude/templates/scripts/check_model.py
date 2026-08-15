#!/usr/bin/env python3
"""Check that element-ID references in this repo resolve to real elements.

`core-architecture-doc-style` gives every element an ID (`G1`, `CAP3`, `SALES.BSVC3`) and
says an ID is assigned once and never reused, so that a stale reference
fails loudly rather than silently pointing at something else. Nothing
enforced that until this script: `check_links.py` verifies that a *link*
resolves, and an agent reading `relieves PAIN2` has no cheap way to notice
that `PAIN2` was deleted three initiatives ago.

Three things are checked, per project:

- **Dangling references** — every referenced ID resolves to a definition.
  A qualified reference (`SALES.BSVC3`) resolves inside that domain's
  folder under `domains/`; an unknown domain is an error.
- **Duplicate definitions** — no ID is defined twice.
- **Retired then live** — no ID appears in both a live table and a
  `## Retired` section. Retired IDs stay retired.

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
- `.claude/skills/` — skill files carry illustrative IDs inside templates
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
import re
import sys
from collections import defaultdict
from pathlib import Path

def _find_repo_root(start: Path) -> Path:
    """The project this script is validating.

    The scripts ship inside the scaffold, so the same file runs from
    `<project>/scripts/` in a generated project and from the method's own
    `templates/scripts/`. Walking up to the enclosing repository gets the
    right answer in both places.
    """
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists():
            return candidate
    return start.parent


REPO_ROOT = _find_repo_root(Path(__file__).resolve().parent)
# The layered model's directory name, in every project tree and in the
# scaffold the skills emit.
MODEL_DIR = "architecture"
# Narrative folders inside the model directory. They are *about* the model
# rather than part of it, and are deliberately not reference-checked.
NARRATIVE = {"scope", "decisions", "reviews", "engagements"}
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)

# Element-ID prefixes, from `core-architecture-doc-style` § Element IDs. Longest first so
# that alternation matches `BSVC` before `B`-prefixed neighbours.
PREFIXES = sorted(
    [
        "STK", "DRV", "ASM", "G", "OUT", "P",           # motivation
        "CAP", "RES", "COA", "VS",                       # strategy
        "ACT", "ROLE", "BCOL", "PROD", "BSVC", "BPROC",  # business
        "BOBJ", "BIF", "CTR", "RULE", "VAL",
        "DOBJ",                                          # information
        "ASVC", "ACMP",                                  # application
        "TSVC", "NODE", "ART",                           # technology
        "JOB", "PAIN", "GAIN", "PREL", "GCRE",           # canvas (VPC)
        "KP", "KA", "KR", "VP", "CR", "CH", "CS", "RS", "COST",  # canvas (BMC)
    ],
    key=len,
    reverse=True,
)
_ID = r"(?:[A-Z][A-Z0-9]*\.)*(?:" + "|".join(PREFIXES) + r")\d+"

# A backticked ID anywhere in the prose or a table cell is a reference.
REFERENCE_RE = re.compile(r"`(" + _ID + r")`")
# A table row whose first cell is a bare backticked ID defines that element.
# A *qualified* first cell is a reference instead — that is what a domain
# charter's "Consumed services" table holds.
TABLE_DEF_RE = re.compile(r"^\|\s*`([A-Z][A-Z0-9]*\d+)`\s*\|", re.M)
# Goals and principles are written as bolded lead-ins rather than table rows.
BULLET_DEF_RE = re.compile(r"\*\*(" + _ID + r")\s+—", re.M)
RETIRED_HEADING_RE = re.compile(r"^##+\s+Retired\s*$", re.M)
TABLE_ROW_RE = re.compile(r"^\|.*\|\s*$", re.M)
ID_HEADER_RE = re.compile(r"^\|\s*(?:Qualified\s+)?ID\s*\|", re.I)


def strip_code(text: str) -> str:
    return FENCE_RE.sub("", text)


def split_retired(text: str) -> tuple[str, str]:
    """Return (live, retired) halves, split at a `## Retired` heading."""
    match = RETIRED_HEADING_RE.search(text)
    if not match:
        return text, ""
    return text[: match.start()], text[match.start() :]


def definitions_in(text: str) -> set[str]:
    return set(TABLE_DEF_RE.findall(text)) | set(BULLET_DEF_RE.findall(text))


def unvalidated_tables(text: str) -> int:
    """Count tables whose header row has no ID column."""
    count = 0
    in_table = False
    for line in text.splitlines():
        is_row = TABLE_ROW_RE.match(line) is not None
        if is_row and not in_table:
            in_table = True
            if not ID_HEADER_RE.match(line):
                count += 1
        elif not is_row:
            in_table = False
    return count


def find_projects() -> list[Path]:
    """A project is the directory containing an `architecture/` folder."""
    projects = []
    for model_dir in sorted(REPO_ROOT.rglob(MODEL_DIR)):
        if ".git" in model_dir.parts or not model_dir.is_dir():
            continue
        projects.append(model_dir.parent)
    return projects


def domain_of(md_file: Path, project: Path) -> str:
    """Upper-cased domain path for a file inside `architecture/domains/<name>/`."""
    parts = md_file.relative_to(project).parts
    segments = [parts[i + 1] for i, part in enumerate(parts[:-1]) if part == "domains"]
    return ".".join(s.upper() for s in segments)


def check_project(project: Path) -> tuple[list[str], int, int]:
    """Return (errors, definition count, unvalidated-table count)."""
    errors: list[str] = []
    skipped = 0
    # Qualified name -> the file that defined it. "" is the enterprise scope.
    defined: dict[str, Path] = {}
    duplicates: list[str] = []
    retired: dict[str, Path] = {}
    references: list[tuple[str, Path]] = []
    domains: set[str] = set()

    model_root = project / MODEL_DIR
    files = [
        path
        for path in sorted(model_root.rglob("*.md"))
        if ".git" not in path.parts
        and ".claude" not in path.parts
        and not (NARRATIVE & set(path.relative_to(model_root).parts))
    ]

    for md_file in files:
        text = strip_code(md_file.read_text(encoding="utf-8"))
        scope = domain_of(md_file, project)
        if scope:
            domains.add(scope)
        skipped += unvalidated_tables(text)
        live_text, retired_text = split_retired(text)

        for element in definitions_in(live_text):
            key = f"{scope}.{element}" if scope else element
            if key in defined:
                duplicates.append(
                    f"{md_file.relative_to(REPO_ROOT)}: duplicate definition of "
                    f"`{key}` (first defined in "
                    f"{defined[key].relative_to(REPO_ROOT)})"
                )
            else:
                defined[key] = md_file
        for element in definitions_in(retired_text):
            retired[f"{scope}.{element}" if scope else element] = md_file

        defined_here = definitions_in(text)
        for reference in REFERENCE_RE.findall(text):
            if "." not in reference and reference in defined_here:
                continue
            references.append((reference, md_file))

    errors.extend(sorted(duplicates))

    for element, md_file in sorted(retired.items()):
        if element in defined:
            errors.append(
                f"{md_file.relative_to(REPO_ROOT)}: `{element}` is retired but "
                f"still defined live in {defined[element].relative_to(REPO_ROOT)}"
            )

    seen: set[tuple[str, Path]] = set()
    for reference, md_file in references:
        if (reference, md_file) in seen:
            continue
        seen.add((reference, md_file))
        scope = domain_of(md_file, project)
        candidates = [reference]
        if "." not in reference and scope:
            candidates.insert(0, f"{scope}.{reference}")
        if any(candidate in defined or candidate in retired for candidate in candidates):
            continue
        rel = md_file.relative_to(REPO_ROOT)
        qualifier = reference.rsplit(".", 1)[0] if "." in reference else ""
        if qualifier and qualifier not in domains:
            errors.append(f"{rel}: `{reference}` names unknown domain `{qualifier}`")
        else:
            errors.append(f"{rel}: `{reference}` is not defined in this project")

    return errors, len(defined), skipped


def main() -> int:
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
