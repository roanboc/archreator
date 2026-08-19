#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml>=6.0",
# ]
# ///
"""Check the skill corpus against the process model and against itself.

The two validators under `templates/scripts/` ship to every project the method
emits, and they check what a project has: links, and element-ID references
inside `architecture/`. Neither looks at a skill. That gap is where four
defects have already lived - a skill citing an element ID from a model that
does not ship with it, a section reference to a heading that had been renamed,
and stale paths inside document templates.

This script covers the skills, and lives outside `templates/` because a
downstream project has no skills to check.

Four things are checked:

- **Section markers** - every reference of the form skill-name, section sign,
  heading names a skill that exists and a heading it actually has.
- **Process binding** - every skill named in the process model exists, every
  level-2 process is realized by at least one skill, and a skill's own
  `realizes_process` agrees with the model.
- **Required sections** - a skill declaring `metadata.archreator.kind` carries
  the headings its kind requires. A skill declaring no kind is skipped, which
  is what lets the corpus be converted in waves.
- **Catalogue agreement** - the skill table in `skills/README.md` and its
  deliberate copy in `templates/CLAUDE.md` carry the same rows.

Headings may open with a glyph, which is stripped before matching: the glyph
is notation, the words are the identity.

A section reference is matched as a prefix of the heading, because a citation
in running prose is routinely cut short by the sentence around it - a
reference to `Grounding` for a heading of `Grounding rule (the most important
one)`. One rename therefore escapes: extending a heading while keeping its
opening words, where `Rules` becomes `Rules and constraints`. Renaming to
anything else is caught.

Exit code is 0 when everything resolves, 1 otherwise.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:  # Only needed once skills carry YAML bodies; absent is not fatal.
    import yaml
except ImportError:  # pragma: no cover - exercised by environment, not tests
    yaml = None


def _find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / ".git").exists():
            return candidate
    return start


REPO_ROOT = _find_repo_root(Path(__file__).resolve().parent)
SKILLS_DIR = REPO_ROOT / "plugins" / "archreator" / "skills"
PROCESS_DIR = REPO_ROOT / "docs" / "process"
CATALOGUE = SKILLS_DIR / "README.md"
CATALOGUE_COPY = REPO_ROOT / "plugins" / "archreator" / "templates" / "CLAUDE.md"
# The headings each kind of skill must carry. This replaces the JSON Schemas:
# the structural promise a schema made is a list of required sections, and a
# list of required sections is legible to the people who write them.
# Defined once, in docs/skill-format.md; this is the machine-readable copy.
REQUIRED_SECTIONS = {
    "gated-procedure": [
        "When to use this", "When not to", "Where this sits",
        "Invariants", "Steps", "Hands off to", "Anti-patterns", "Done when",
    ],
    "document-template": [
        "When to use this", "When not to", "Where this sits",
        "Template", "Rules", "Done when",
    ],
    "rulebook": ["When to use this", "When not to", "Rules"],
}

# A fenced block, anchored and matched on fence length so a fence containing a
# fence does not close early. Same rule as the two shipped validators.
FENCE_RE = re.compile(
    r"^(?P<ticks>`{3,})[^\n]*\n.*?^(?P=ticks)`*[ \t]*$",
    re.DOTALL | re.MULTILINE,
)
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.M)
# A skill name in backticks, a section sign, then the heading - which may wrap
# onto the next line and runs into the prose after it. What follows the sign is
# a window, not the name.
MARKER_RE = re.compile(r"`([a-z0-9][a-z0-9-]*)`\s*§\s*([^\n]*(?:\n[^\n]*)?)")
# Terminators that cannot appear inside a heading being cited mid-sentence.
WINDOW_END_RE = re.compile(r"[.,;:)—]|\s+§\s+")
CATALOGUE_ROW_RE = re.compile(r"^\|\s*(?:\[)?`([a-z0-9-]+)`(?:\]\([^)]*\))?\s*\|\s*(.+?)\s*\|\s*$", re.M)
# The level-2 rows of the process model: a dotted ID, the process name, and the
# realizing skills in the last cell.
LEVEL2_ROW_RE = re.compile(r"^\|\s*`(BPROC\d+\.\d+)`\s*\|(.+)\|\s*$", re.M)
SKILL_NAME_RE = re.compile(r"`([a-z0-9][a-z0-9-]*)`")

MIN_PREFIX_CHARS = 4


def normalize(text: str) -> str:
    """Whitespace-collapsed, lower-cased, and stripped of any leading glyph.

    A section heading may open with a notation glyph. The glyph says what kind
    of section it is; the words are what a reference names.
    """
    collapsed = re.sub(r"\s+", " ", text).strip().lower()
    return re.sub(r"^[^0-9a-z]+", "", collapsed)


def strip_code(text: str) -> str:
    return FENCE_RE.sub("", text)


def skill_names() -> set[str]:
    if not SKILLS_DIR.is_dir():
        return set()
    return {p.name for p in SKILLS_DIR.iterdir() if (p / "SKILL.md").is_file()}


def headings_of(skill: str) -> list[str]:
    path = SKILLS_DIR / skill / "SKILL.md"
    if not path.is_file():
        return []
    return [normalize(h) for h in HEADING_RE.findall(strip_code(path.read_text(encoding="utf-8")))]


def skill_meta(skill: str) -> dict:
    """The `metadata.archreator` block of a skill, or {} when it has none."""
    path = SKILLS_DIR / skill / "SKILL.md"
    match = FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
    if not match:
        return {}
    if yaml is None:
        return {"__unparsed__": True}
    try:
        loaded = yaml.safe_load(match.group(1))
    except yaml.YAMLError as error:
        # An unquoted colon in a description is the usual cause, and it makes
        # the frontmatter unreadable to anything that parses it strictly.
        return {"__invalid__": str(error).splitlines()[0]}
    if not isinstance(loaded, dict):
        return {}
    meta = (loaded.get("metadata") or {}).get("archreator") or {}
    return meta if isinstance(meta, dict) else {}


def listed(meta: dict, key: str) -> list[str]:
    """A comma-separated metadata value as a list.

    Agent Skills types `metadata.*` as string to string, so a list is written
    as one comma-separated string rather than a YAML sequence.
    """
    return [v.strip() for v in str(meta.get(key, "")).split(",") if v.strip()]


# This file defines the marker pattern, so it necessarily contains examples of
# it. Scanning itself would report its own documentation as broken references.
SELF = Path(__file__).resolve()


def scanned_files() -> list[Path]:
    files = []
    for path in REPO_ROOT.rglob("*"):
        if {".git", ".claude", ".aip"} & set(path.parts) or not path.is_file():
            continue
        if path.resolve() == SELF:
            continue
        if path.suffix in {".md", ".py"}:
            files.append(path)
    return sorted(files)


def check_section_markers(known: set[str]) -> list[str]:
    """Every section reference names a skill that exists and a heading it has."""
    errors: list[str] = []
    cache: dict[str, list[str]] = {}
    seen: set[tuple[str, str, Path]] = set()

    for path in scanned_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for skill, window in MARKER_RE.findall(text):
            if skill not in known:
                # Not every backticked token before a section sign is a skill;
                # only flag one that looks like a skill and is not one.
                if "-" in skill:
                    errors.append(
                        f"{path.relative_to(REPO_ROOT)}: `{skill}` § ... names no such skill"
                    )
                continue
            cut = WINDOW_END_RE.search(window)
            candidate = normalize(window[: cut.start()] if cut else window)
            if not candidate:
                continue
            key = (skill, candidate, path)
            if key in seen:
                continue
            seen.add(key)
            if skill not in cache:
                cache[skill] = headings_of(skill)
            words = candidate.split(" ")
            matched = False
            for count in range(len(words), 0, -1):
                prefix = " ".join(words[:count])
                if len(prefix) < MIN_PREFIX_CHARS:
                    break
                if any(h.startswith(prefix) for h in cache[skill]):
                    matched = True
                    break
            if not matched:
                errors.append(
                    f"{path.relative_to(REPO_ROOT)}: `{skill}` § {candidate!r} "
                    f"matches no heading in that skill"
                )
    return errors


def level2_processes() -> dict[str, set[str]]:
    """Level-2 process ID -> the skills the model says realize it."""
    processes: dict[str, set[str]] = {}
    if not PROCESS_DIR.is_dir():
        return processes
    for path in sorted(PROCESS_DIR.rglob("*.md")):
        text = strip_code(path.read_text(encoding="utf-8"))
        for pid, rest in LEVEL2_ROW_RE.findall(text):
            realized = rest.rsplit("|", 1)[-1]
            processes.setdefault(pid, set()).update(SKILL_NAME_RE.findall(realized))
    return processes


def check_process_binding(known: set[str]) -> list[str]:
    errors: list[str] = []
    processes = level2_processes()
    if not processes:
        errors.append("docs/process/: no level-2 processes found - the model is unreadable")
        return errors

    for pid, skills in sorted(processes.items()):
        if not skills:
            errors.append(f"docs/process/: `{pid}` names no skill that realizes it")
        for skill in sorted(skills):
            if skill not in known:
                errors.append(f"docs/process/: `{pid}` is realized by `{skill}`, which does not exist")

    for skill in sorted(known):
        meta = skill_meta(skill)
        if meta.get("__unparsed__") or meta.get("__invalid__"):
            continue
        for pid in listed(meta, "realizes_process"):
            if pid not in processes:
                errors.append(f"{skill}: realizes_process `{pid}` is not a level-2 process")
            elif skill not in processes[pid]:
                errors.append(
                    f"{skill}: declares `{pid}`, but the process model does not name it there"
                )
    return errors


def check_required_sections(known: set[str]) -> list[str]:
    """A skill declaring a kind carries the headings that kind requires.

    A skill declaring no kind has not been converted yet and is skipped, which
    is what lets the corpus move over in waves.
    """
    errors: list[str] = []
    handoff_re = re.compile(r"^#+[^\n]*hands off to[^\n]*$(.*?)(?=^#|\Z)", re.M | re.I | re.S)
    for skill in sorted(known):
        meta = skill_meta(skill)
        if meta.get("__invalid__"):
            errors.append(f"{skill}: frontmatter is not valid YAML - {meta['__invalid__']}")
            continue
        if meta.get("__unparsed__"):
            errors.append(f"{skill}: PyYAML is not installed, so its frontmatter was not read")
            continue
        kind = meta.get("kind")
        if not kind:
            continue
        if kind not in REQUIRED_SECTIONS:
            errors.append(
                f"{skill}: kind `{kind}` is not one of " + ", ".join(sorted(REQUIRED_SECTIONS))
            )
            continue
        headings = headings_of(skill)
        for required in REQUIRED_SECTIONS[kind]:
            want = normalize(required)
            if not any(h.startswith(want) for h in headings):
                errors.append(f"{skill}: a {kind} needs a `{required}` section")

        # Every skill named in a Hands off to table has to exist.
        text = strip_code((SKILLS_DIR / skill / "SKILL.md").read_text(encoding="utf-8"))
        section = handoff_re.search(text)
        if section:
            for target in SKILL_NAME_RE.findall(section.group(1)):
                if target not in known and "-" in target:
                    errors.append(f"{skill}: hands off to `{target}`, which does not exist")
    return errors


def catalogue_rows(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    text = strip_code(path.read_text(encoding="utf-8"))
    return {name: normalize(desc) for name, desc in CATALOGUE_ROW_RE.findall(text)}


def check_catalogue(known: set[str]) -> list[str]:
    errors: list[str] = []
    primary = catalogue_rows(CATALOGUE)
    copy = catalogue_rows(CATALOGUE_COPY)
    if not primary:
        return ["plugins/archreator/skills/README.md: no skill rows found"]

    missing = sorted(known - set(primary))
    for skill in missing:
        errors.append(f"skills/README.md: `{skill}` exists but is not in the catalogue")
    for skill in sorted(set(primary) - known):
        errors.append(f"skills/README.md: `{skill}` is catalogued but no such skill exists")
    for skill in sorted(set(primary) - set(copy)):
        errors.append(f"templates/CLAUDE.md: `{skill}` is missing from the copied table")
    for skill in sorted(set(copy) - set(primary)):
        errors.append(f"templates/CLAUDE.md: `{skill}` is in the copied table but not the catalogue")
    for skill in sorted(set(primary) & set(copy)):
        if primary[skill] != copy[skill]:
            errors.append(
                f"templates/CLAUDE.md: the row for `{skill}` has drifted from skills/README.md"
            )
    return errors


def main() -> int:
    known = skill_names()
    if not known:
        print(f"No skills found under {SKILLS_DIR.relative_to(REPO_ROOT)} - nothing to check.")
        return 0

    all_errors: list[str] = []
    for label, errors in [
        ("section markers", check_section_markers(known)),
        ("process binding", check_process_binding(known)),
        ("required sections", check_required_sections(known)),
        ("catalogue", check_catalogue(known)),
    ]:
        if errors:
            all_errors.append(f"{label}:")
            all_errors.extend(f"  {e}" for e in errors)

    if all_errors:
        print("Skill corpus errors:")
        for line in all_errors:
            print(f"  {line}")
        return 1

    converted = sum(1 for s in known if skill_meta(s).get("kind"))
    print(f"{len(known)} skills ({converted} converted): section markers, process "
          f"binding, required sections and catalogue all resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
