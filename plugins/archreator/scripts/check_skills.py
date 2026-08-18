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

It widens as skills become AIP Instructions, because an AIP body is one fenced
YAML block and `check_links.py` exempts fenced blocks by design. Every path a
converted skill names would stop being checked by anything.

This script covers the skills, and lives outside `templates/` because a
downstream project has no skills to check.

Five things are checked:

- **Section markers** - every `<skill>` § `<Section>` reference names a skill
  that exists and a heading it actually has.
- **Process binding** - every skill named in the process model exists, every
  level-2 process is realized by at least one skill, and a converted skill's
  own `realizes_process` agrees with the model.
- **Body paths** - `script`, `template_asset`, `references` and `tables`
  entries in a converted skill resolve to files in that skill's folder.
- **Graph integrity** - inside a converted body, step names are unique,
  `depends_on` names a step that exists, and `hands_off_to` names a real skill.
- **Schema binding** - the schema bundled in a skill's `source/` is the same
  file as the canonical one under `schemas/`, and the frontmatter `schemaId`
  matches its `$id`. AIP requires the bundle so a skill is self-contained;
  nothing in AIP notices when the copy drifts from the original.
- **Catalogue agreement** - the skill table in `skills/README.md` and its
  deliberate copy in `templates/CLAUDE.md` carry the same rows.

A section reference is matched as a prefix of the heading, because a citation
in running prose is routinely cut short by the sentence around it - `§ Grounding`
for a heading of `Grounding rule (the most important one)`. One rename therefore
escapes: extending a heading while keeping its opening words, where `Rules`
becomes `Rules and constraints`. Renaming to anything else is caught.

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
SCHEMAS_DIR = REPO_ROOT / "plugins" / "archreator" / "schemas"

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
    """Whitespace-collapsed, lower-cased, punctuation-trimmed for comparison."""
    return re.sub(r"\s+", " ", text).strip().lower()


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


def body_yaml(skill_md: Path) -> dict | None:
    """The parsed YAML body of an AIP skill, or None if it is not one."""
    match = FRONTMATTER_RE.match(skill_md.read_text(encoding="utf-8"))
    if not match:
        return None
    body = match.group(2).strip()
    fence = re.match(r"^```(?:yaml|yml)\s*\n(.*?)\n```\s*$", body, re.DOTALL)
    if not fence:
        return None
    if yaml is None:
        return {"__unparsed__": True}
    loaded = yaml.safe_load(fence.group(1))
    return loaded if isinstance(loaded, dict) else {}


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
        parsed = body_yaml(SKILLS_DIR / skill / "SKILL.md")
        if not parsed or parsed.get("__unparsed__"):
            continue
        declared = parsed.get("realizes_process") or []
        if isinstance(declared, str):
            declared = [declared]
        for pid in declared:
            if pid not in processes:
                errors.append(f"{skill}: realizes_process `{pid}` is not a level-2 process")
            elif skill not in processes[pid]:
                errors.append(
                    f"{skill}: declares `{pid}`, but the process model does not name it there"
                )
    return errors


def check_body_paths(known: set[str]) -> list[str]:
    """Paths a converted skill names resolve inside its own folder.

    `produces` is deliberately not checked: those are paths in a consuming
    project's repository, which does not exist here.
    """
    errors: list[str] = []
    unparsed = []
    for skill in sorted(known):
        skill_dir = SKILLS_DIR / skill
        parsed = body_yaml(skill_dir / "SKILL.md")
        if not parsed:
            continue
        if parsed.get("__unparsed__"):
            unparsed.append(skill)
            continue
        targets: list[str] = []
        for step in parsed.get("steps") or []:
            if isinstance(step, dict):
                for field in ("script", "uses_template"):
                    value = step.get(field)
                    if isinstance(value, str) and "/" in value:
                        targets.append(value)
        if isinstance(parsed.get("template_asset"), str):
            targets.append(parsed["template_asset"])
        for ref in parsed.get("references") or []:
            if isinstance(ref, dict) and isinstance(ref.get("path"), str):
                targets.append(ref["path"])
        for table in parsed.get("tables") or []:
            if isinstance(table, dict) and isinstance(table.get("asset"), str):
                targets.append(table["asset"])
        for target in targets:
            if not (skill_dir / target).exists():
                errors.append(f"{skill}: `{target}` does not resolve inside the skill folder")
    if unparsed:
        errors.append(
            "PyYAML is not installed, so the YAML bodies of "
            + ", ".join(unparsed)
            + " were not checked. Install it, or run this script with `uv run`."
        )
    return errors


def check_graph(known: set[str]) -> list[str]:
    """Inside a converted body, the references between steps actually resolve."""
    errors: list[str] = []
    for skill in sorted(known):
        parsed = body_yaml(SKILLS_DIR / skill / "SKILL.md")
        if not parsed or parsed.get("__unparsed__"):
            continue
        steps = [s for s in (parsed.get("steps") or []) if isinstance(s, dict)]
        names = [s.get("name") for s in steps if isinstance(s.get("name"), str)]
        for name in sorted({n for n in names if names.count(n) > 1}):
            errors.append(f"{skill}: two steps are both named `{name}`")
        known_steps = set(names)
        for step in steps:
            for dependency in step.get("depends_on") or []:
                if dependency not in known_steps:
                    errors.append(
                        f"{skill}: step `{step.get('name')}` depends on `{dependency}`, "
                        f"which is not a step in this procedure"
                    )
        for handoff in parsed.get("hands_off_to") or []:
            if isinstance(handoff, dict):
                target = handoff.get("skill")
                if isinstance(target, str) and target not in known:
                    errors.append(f"{skill}: hands off to `{target}`, which does not exist")
    return errors


def check_schema_binding(known: set[str]) -> list[str]:
    """A skill's bundled schema is the canonical one, and its id matches."""
    errors: list[str] = []
    canonical = {}
    if SCHEMAS_DIR.is_dir():
        for path in SCHEMAS_DIR.glob("*.schema.json"):
            try:
                canonical[json.loads(path.read_text(encoding="utf-8"))["$id"]] = path
            except (ValueError, KeyError):
                errors.append(f"schemas/{path.name}: not readable as a schema with an $id")

    for skill in sorted(known):
        skill_md = SKILLS_DIR / skill / "SKILL.md"
        match = FRONTMATTER_RE.match(skill_md.read_text(encoding="utf-8"))
        if not match:
            continue
        declared = re.search(r"^\s*schemaId:\s*(\S+)\s*$", match.group(1), re.M)
        source = SKILLS_DIR / skill / "source"
        if not declared:
            if source.is_dir():
                errors.append(f"{skill}: has a source/ directory but declares no metadata.aip.schemaId")
            continue
        schema_id = declared.group(1).strip("\"'")
        if schema_id not in canonical:
            errors.append(f"{skill}: schemaId `{schema_id}` matches no schema under schemas/")
            continue
        bundled = list(source.glob("*.schema.json")) if source.is_dir() else []
        if not bundled:
            errors.append(f"{skill}: declares a schemaId but bundles no schema in source/")
            continue
        original = canonical[schema_id].read_text(encoding="utf-8")
        for copy in bundled:
            if copy.read_text(encoding="utf-8") != original:
                errors.append(
                    f"{skill}: source/{copy.name} has drifted from schemas/{canonical[schema_id].name}"
                )
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
        ("body paths", check_body_paths(known)),
        ("graph integrity", check_graph(known)),
        ("schema binding", check_schema_binding(known)),
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

    print(f"{len(known)} skills: section markers, process binding, paths, graph, "
          f"schema binding and catalogue all resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
