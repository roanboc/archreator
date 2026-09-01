#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml>=6.0",
# ]
# ///
"""Check the skill corpus against the process model and against itself.

The two validators under `scaffold/scripts/` ship to every project the method
emits, and they check what a project has: links, and element-ID references
inside `architecture/`. Neither looks at a skill. That gap is where four
defects have already lived - a skill citing an element ID from a model that
does not ship with it, a section reference to a heading that had been renamed,
and stale paths inside document templates.

This script covers the skills, and lives outside `scaffold/` because a
downstream project has no skills to check.

What is checked (the success line derives the live list from the checks
that actually ran):

- **Section markers** - every reference of the form skill-name, section sign,
  heading - backticked or written as a link - names a skill that exists and a
  heading it actually has, in its SKILL.md or its references.
- **Process binding** - every skill named in the process model exists, every
  level-2 process is realized by at least one skill, and a skill's own
  `realizes_process` agrees with the model.
- **Required sections** - a skill declaring `metadata.archreator.kind` carries
  the headings its kind requires. A skill declaring no kind is skipped, which
  is what lets the corpus be converted in waves.
- **Prefix registry** - the prefix table in the style rulebook matches
  `element-prefixes.json`, the machine-readable copy the scaffold ships.
- **Reference files** - every file under a skill's `references/` is linked
  from its SKILL.md, so nothing citable is unreachable.
- **Scaffold specimens** - no plausible element identifier ships in the
  scaffold as an example a generated project would inherit.
- **Catalogue** - the table in `skills/README.md` names exactly the skills
  that exist, with the kind each declares. The scaffold's `AGENTS.md`
  deliberately does not restate it.
- **Assets** - every file under `assets/` is named by a skill that emits it,
  and every asset a skill names exists.
- **Manifest agreement** - the plugin manifest exists in both places hosts
  look for it, with the same fields, and the marketplace entry agrees.
- **Context files** - the `CLAUDE.md` and `GEMINI.md` the scaffold plants
  hold nothing but the import of `AGENTS.md`.

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
SCAFFOLD_DIR = REPO_ROOT / "plugins" / "archreator" / "scaffold"
SCAFFOLD_AGENTS = SCAFFOLD_DIR / "AGENTS.md"
ASSETS_DIR = REPO_ROOT / "plugins" / "archreator" / "assets"
# The plugin manifest, in the two places the hosts look for it. Claude Code
# reads `.claude-plugin/plugin.json`; Copilot and Codex read the plugin root.
# Neither is derived from the other at runtime, so CI holds them together the
# way it holds the prefix registry together.
PLUGIN_MANIFESTS = (
    REPO_ROOT / "plugins" / "archreator" / "plugin.json",
    REPO_ROOT / "plugins" / "archreator" / ".claude-plugin" / "plugin.json",
)
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"
# A host that reads only its own filename still has to find the entry point,
# and Claude Code has no AGENTS.md fallback. These carry the import and
# nothing else, because content in one of them is content the other hosts
# never see.
CONTEXT_POINTERS = ("CLAUDE.md", "GEMINI.md")
CONTEXT_IMPORT = "@AGENTS.md"
# A backticked element identifier, as check_model.py reads one. Used here only
# to find specimens in the scaffold, so it deliberately matches any prefix
# rather than loading the registry: an invented prefix is just as wrong.
SCAFFOLD_ID_RE = re.compile(r"`([A-Z][A-Z0-9]*\.)*[A-Z]+\d+(\.\d+)*`")
# The headings each kind of skill must carry. This replaces the JSON Schemas:
# the structural promise a schema made is a list of required sections, and a
# list of required sections is legible to the people who write them.
# Defined once, in docs/skill-format.md; this is the machine-readable copy.
# The kind is declared where the agent can actually act on it. A description
# is the only thing loaded before a skill is chosen, so it opens by saying
# whether this is run or consulted; the H1 repeats it as a glyph for whoever
# opens the file. Both are checked against metadata.archreator.kind rather
# than left to authoring discipline.
KIND_MARKERS = {
    "gated-procedure": ("Procedure —", "⚙"),
    "document-template": ("Document —", "▤"),
    "rulebook": ("Rulebook —", "※"),
}

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
# a window, not the name. The name may also be the text of a Markdown link -
# `[`skill`](../SKILL.md) § Heading` is how a reference file cites the page it
# belongs to - so an optional `](...)` is allowed between the name and the
# sign; without it, every citation written as a link went unchecked.
MARKER_RE = re.compile(
    r"`([a-z0-9][a-z0-9-]*)`(?:\]\([^)\n]*\))?\s*§\s*([^\n]*(?:\n[^\n]*)?)"
)
# Terminators that cannot appear inside a heading being cited mid-sentence.
# An em-dash is not one: step headings use it, and the longest-prefix search
# below already copes with a window that runs past the heading it names.
WINDOW_END_RE = re.compile(r"[.,;:)]|\s+§\s+")
# A catalogue row: the skill in the first cell, linked or bare. Later cells are
# split off rather than swept up, so the two tables may carry different
# columns and still be compared on the ones they share.
ASSET_PATH_RE = re.compile(r"\]\(\./([A-Za-z0-9_./-]+?)/?\)")
CATALOGUE_ROW_RE = re.compile(r"^\|\s*(?:\[)?`([a-z0-9-]+)`(?:\]\([^)]*\))?\s*\|(.*)\|\s*$", re.M)
# The level-2 rows of the process model: a dotted ID, the process name, and the
# realizing skills in the last cell.
LEVEL2_ROW_RE = re.compile(r"^\|\s*`(BPROC\d+\.\d+)`\s*\|(.+)\|\s*$", re.M)
SKILL_NAME_RE = re.compile(r"`([a-z0-9][a-z0-9-]*)`")

GATE_GLYPH = "❖"
MIDDLE_DOT = "·"
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


def _headings(path: Path) -> list[str]:
    if not path.is_file():
        return []
    return [normalize(h) for h in HEADING_RE.findall(strip_code(path.read_text(encoding="utf-8")))]


def headings_of(skill: str) -> list[str]:
    """The skill's own headings - what a required section has to be found in."""
    return _headings(SKILLS_DIR / skill / "SKILL.md")


def reference_files(skill: str) -> list[Path]:
    """The skill's progressive-disclosure references, if it has any."""
    return sorted((SKILLS_DIR / skill / "references").glob("*.md"))


def citable_headings(skill: str) -> list[str]:
    """Every heading a `skill` section reference may name.

    A rulebook keeps the rules that apply everywhere in SKILL.md and the lookup
    tables needed only sometimes in references/. A citation names a heading, not
    a file, so moving a section into a reference has to leave every citation of
    it resolving - otherwise the split would cost an edit in each citing skill,
    which is the churn progressive disclosure is supposed to avoid.
    """
    headings = headings_of(skill)
    for path in reference_files(skill):
        headings += _headings(path)
    return headings


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
# The same tooling-and-derived set the two scaffold validators skip: a brief
# generated into .archreator/, or a stale pre-reset .docs/ staging copy, is
# not the corpus's to validate.
EXCLUDED_PARTS = {".git", ".claude", ".agents", ".gemini", ".codex",
                  ".copilot", ".aip", ".docs", ".archreator", ".model"}


def scanned_files() -> list[Path]:
    files = []
    for path in REPO_ROOT.rglob("*"):
        if EXCLUDED_PARTS & set(path.parts) or not path.is_file():
            continue
        if path.resolve() == SELF:
            continue
        if path.suffix in {".md", ".py"}:
            files.append(path)
    return sorted(files)


def _continues(heading: str, prefix: str, rest: list[str]) -> bool:
    """Does `prefix` name the start of `heading`, without the citation then
    contradicting it?

    A short prefix of a citation can open a heading it does not mean - `what`
    opens both `what the document contains` and `what belongs at which tier`.
    So where the heading carries on with a word and the citation carries on
    with a different word, this is a different section wearing the same first
    word.
    """
    if not heading.startswith(prefix):
        return False
    tail = heading[len(prefix):].strip().split(" ")
    if not tail or not tail[0] or not rest or not rest[0]:
        return True
    # Only an alphabetic pair can contradict; punctuation carries no meaning here.
    if tail[0][:1].isalpha() and rest[0][:1].isalpha():
        return tail[0] == rest[0]
    return True


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
                cache[skill] = citable_headings(skill)
            words = candidate.split(" ")
            matched = False
            for count in range(len(words), 0, -1):
                prefix = " ".join(words[:count])
                if len(prefix) < MIN_PREFIX_CHARS:
                    break
                if any(_continues(h, prefix, words[count:]) for h in cache[skill]):
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


def _frontmatter(skill: str) -> dict:
    """The whole frontmatter mapping, or {} when it will not parse."""
    path = SKILLS_DIR / skill / "SKILL.md"
    match = FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
    if not match or yaml is None:
        return {}
    try:
        loaded = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _first_heading(skill: str) -> str:
    """The skill's H1, unnormalized, so its glyph survives."""
    text = strip_code((SKILLS_DIR / skill / "SKILL.md").read_text(encoding="utf-8"))
    found = HEADING_RE.findall(text)
    return found[0].strip() if found else ""


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
        prefix, glyph = KIND_MARKERS[kind]
        description = str(_frontmatter(skill).get("description", ""))
        if not description.startswith(prefix):
            errors.append(
                f"{skill}: a {kind} description must open `{prefix}` - it is "
                "the only signal an agent has before the skill is chosen"
            )
        first = _first_heading(skill)
        if first and not first.startswith(glyph):
            errors.append(f"{skill}: a {kind} title opens with the glyph `{glyph}`")
        headings = headings_of(skill)
        for required in REQUIRED_SECTIONS[kind]:
            want = normalize(required)
            if not any(h.startswith(want) for h in headings):
                errors.append(f"{skill}: a {kind} needs a `{required}` section")

        # A declared gate has to appear in the body. The reverse is not an
        # error: a skill may draw a gate belonging to the skill it hands to,
        # which is how establish-project shows where bootstrap ends.
        body = (SKILLS_DIR / skill / "SKILL.md").read_text(encoding="utf-8")
        for gate in listed(meta, "gates"):
            # Matched on the gate glyph, not a bare mention: a skill routinely
            # names gates it does not own, saying they are N/A.
            if gate.lower() != "none" and (GATE_GLYPH + " " + gate) not in body:
                errors.append(
                    f"{skill}: declares `{gate}` but its body never names it"
                )

        # Every skill named in a Hands off to table has to exist.
        text = strip_code((SKILLS_DIR / skill / "SKILL.md").read_text(encoding="utf-8"))
        section = handoff_re.search(text)
        if section:
            for target in SKILL_NAME_RE.findall(section.group(1)):
                if target not in known and "-" in target:
                    errors.append(f"{skill}: hands off to `{target}`, which does not exist")
    return errors


def check_scaffold_specimens() -> list[str]:
    """No scaffold document under architecture/ may show an element identifier.

    The scaffold is copied whole into a new project, so anything it contains
    arrives in that project's `architecture/` folder. A specimen identifier —
    `BPROC7.2` in a sentence teaching how levels are numbered — is a reference
    to an element nobody defined, and `check_model.py` correctly rejects it the
    moment the project defines its first real element.

    It cannot be caught downstream by the validator that would care: the
    scaffold here is excluded from `check_model.py` (its layer READMEs would
    fail against themselves), and once copied it is no longer recognisable as
    scaffold. So it is caught here, at the only point where the file is still
    known to be a template.

    The convention those specimens were teaching belongs to the rulebooks,
    which are not copied anywhere and may show whatever they need to.
    """
    errors: list[str] = []
    model_dir = SCAFFOLD_DIR / "architecture"
    for path in sorted(model_dir.rglob("*.md")):
        text = strip_code(path.read_text(encoding="utf-8"))
        for match in SCAFFOLD_ID_RE.finditer(text):
            errors.append(
                f"{path.relative_to(REPO_ROOT)}: shows the element identifier "
                f"{match.group(0)}, which ships into every generated project as "
                f"a dangling reference. Name the rule and cite the rulebook instead"
            )
    return errors


def check_prefix_registry() -> list[str]:
    """The prefix table in the style rulebook matches the file the scripts read.

    One fact, two representations: a table a person reads, and a JSON file that
    ships beside check_model.py because a project has the scripts and not the
    skills. Neither is derived from the other at runtime, so CI holds them
    together.
    """
    skill = (
        SKILLS_DIR / "architecture-document-style" / "references" / "archimate-elements-and-ids.md"
    )
    registry = (
        REPO_ROOT / "plugins" / "archreator" / "scaffold" / "scripts" / "element-prefixes.json"
    )
    if not skill.is_file() or not registry.is_file():
        return []

    lines = skill.read_text(encoding="utf-8").splitlines()
    header = [
        i for i, line in enumerate(lines)
        if line.strip().startswith("| Where ") and "Prefixes" in line
    ]
    if not header:
        return ["architecture-document-style: references/archimate-elements-and-ids.md has no element-prefix table"]

    documented: dict[str, str] = {}
    for line in lines[header[0] + 2:]:
        if not line.strip().startswith("|"):
            break
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 2:
            continue
        for entry in cells[1].split(MIDDLE_DOT):
            code, _, name = entry.strip().partition(" ")
            documented[code.strip("`")] = name.strip()

    shipped: dict[str, str] = {}
    for group in json.loads(registry.read_text(encoding="utf-8"))["prefixes"].values():
        shipped.update(group)

    errors: list[str] = []
    for code in sorted(set(documented) - set(shipped)):
        errors.append(f"`{code}` is in the style rulebook's table but not element-prefixes.json")
    for code in sorted(set(shipped) - set(documented)):
        errors.append(f"`{code}` is in element-prefixes.json but not the style rulebook's table")
    for code in sorted(set(documented) & set(shipped)):
        if documented[code] != shipped[code]:
            errors.append(
                f"`{code}` is `{documented[code]}` in the rulebook and "
                f"`{shipped[code]}` in element-prefixes.json"
            )

    # Every non-canvas prefix also carries the standard's one-line definition
    # in the same reference — § What each element represents: rows of prefix,
    # element, aspect, definition, and the method's considerations. Canvas
    # prefixes are Strategyzer blocks, not ArchiMate elements, and are exempt.
    defined: set[str] = set()
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("| `"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) == 5 and cells[2] and cells[3]:
            defined.add(cells[0].strip("`"))
    archimate = {
        code
        for label, group in json.loads(registry.read_text(encoding="utf-8"))["prefixes"].items()
        if not label.startswith("Canvas")
        for code in group
    }
    for code in sorted(archimate - defined):
        errors.append(
            f"`{code}` has no row in the rulebook's element-definitions table "
            f"(§ What each element represents)"
        )
    return errors


def check_references_reachable(known: set[str]) -> list[str]:
    """Every references/*.md is linked from the SKILL.md that owns it.

    Progressive disclosure only works if the skill says what is one file away.
    A reference nothing links to is a file the agent never learns exists, which
    is worse than the section having stayed inline.
    """
    errors: list[str] = []
    for skill in sorted(known):
        files = reference_files(skill)
        if not files:
            continue
        body = (SKILLS_DIR / skill / "SKILL.md").read_text(encoding="utf-8")
        for path in files:
            if f"references/{path.name}" not in body:
                errors.append(
                    f"{skill}: references/{path.name} is not linked from SKILL.md, "
                    "so nothing will ever read it"
                )
    return errors


def catalogue_rows(path: Path) -> dict[str, list[str]]:
    """Skill name -> its remaining cells, normalized."""
    if not path.is_file():
        return {}
    text = strip_code(path.read_text(encoding="utf-8"))
    rows = {}
    for name, rest in CATALOGUE_ROW_RE.findall(text):
        rows[name] = [normalize(cell) for cell in rest.split("|")]
    return rows


def check_assets(known: set[str]) -> list[str]:
    """Every asset is named by a skill, and every asset the index names exists.

    Named, not emitted: this is a reachability check on plain text, and it
    cannot tell an emission instruction from a mention. What it guarantees is
    that no asset is orphaned from the corpus that is supposed to emit it.

    `check_links.py` cannot check this tree - a template's relative links are
    written for the project it lands in - so what it would have caught is
    caught here instead, and more usefully: a link resolving proved a file was
    there, this proves a file is reachable by the process that emits it.

    The assets README is the index; a skill claims an asset by naming its path.
    """
    if not ASSETS_DIR.is_dir():
        return []
    errors: list[str] = []
    named: set[str] = set()
    # The skills only: the assets README is the index, and an index row is a
    # claim about who emits a file, not the emission itself. With the README
    # in the haystack, an asset no skill ever mentions passed on the strength
    # of its own catalogue entry — the exact rot this check exists to catch.
    sources = [SKILLS_DIR / s / "SKILL.md" for s in sorted(known)]
    sources += sorted((SKILLS_DIR).rglob("references/*.md"))
    haystack = "\n".join(
        p.read_text(encoding="utf-8") for p in sources if p.is_file()
    )

    for path in sorted(ASSETS_DIR.rglob("*")):
        if not path.is_file() or path == ASSETS_DIR / "README.md":
            continue
        rel = path.relative_to(ASSETS_DIR).as_posix()
        # A skill claims a file by its qualified path (`assets/github/
        # pull_request_template.md`) or any of its folders with a trailing
        # slash (`assets/github/`). The claim carries the `assets/` prefix so
        # an ordinary word cannot claim by accident, and the bare `layers`
        # folder is not claimable: `assets/layers/` names the whole shelf,
        # which is exactly the generic mention that made this check vacuous.
        parts = rel.split("/")
        claims = {f"assets/{rel}"}
        for depth in range(1, len(parts)):
            ancestor = "/".join(parts[:depth])
            if ancestor != "layers":
                claims.add(f"assets/{ancestor}/")
        if any(claim in haystack for claim in claims):
            named.add(rel)
        else:
            errors.append(
                f"assets/{rel}: no skill names it, so nothing will ever emit it"
            )

    index = (ASSETS_DIR / "README.md")
    if not index.is_file():
        errors.append("assets/README.md is missing - it is the index of what gets emitted when")
    else:
        for match in ASSET_PATH_RE.findall(index.read_text(encoding="utf-8")):
            if not (ASSETS_DIR / match).exists():
                errors.append(f"assets/README.md names assets/{match}, which does not exist")
    return errors


def check_catalogue(known: set[str]) -> list[str]:
    errors: list[str] = []
    primary = catalogue_rows(CATALOGUE)
    if not primary:
        return ["plugins/archreator/skills/README.md: no skill rows found"]

    missing = sorted(known - set(primary))
    for skill in missing:
        errors.append(f"skills/README.md: `{skill}` exists but is not in the catalogue")
    for skill in sorted(set(primary) - known):
        errors.append(f"skills/README.md: `{skill}` is catalogued but no such skill exists")
    for skill, cells in sorted(primary.items()):
        declared = skill_meta(skill).get("kind")
        if not declared or len(cells) < 2:
            continue
        word = KIND_MARKERS[declared][0].split(" ")[0].lower()
        if word not in cells[0]:
            errors.append(
                f"skills/README.md: `{skill}` is catalogued as `{cells[0]}` "
                f"but declares kind `{declared}`"
            )
    return errors


def check_manifests() -> list[str]:
    """The plugin manifest agrees with its copy, and the marketplace with both.

    Claude Code reads `.claude-plugin/plugin.json`, Copilot and Codex read
    `plugin.json` at the plugin root, and all three want the same fields. The
    same fact in two files is the arrangement the prefix registry already
    lives with: written twice so each host finds it where it looks, never
    generated at runtime, and held together here.
    """
    errors: list[str] = []
    loaded: dict[Path, dict] = {}
    for path in PLUGIN_MANIFESTS:
        if not path.is_file():
            errors.append(f"{path.relative_to(REPO_ROOT)}: the plugin manifest is missing")
            continue
        try:
            loaded[path] = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path.relative_to(REPO_ROOT)}: not valid JSON - {exc}")
    if len(loaded) != len(PLUGIN_MANIFESTS):
        return errors

    canonical, copy = PLUGIN_MANIFESTS
    left, right = loaded[canonical], loaded[copy]
    for key in sorted(set(left) | set(right)):
        if key not in left:
            errors.append(f"`{key}` is in {copy.relative_to(REPO_ROOT)} but not {canonical.name}")
        elif key not in right:
            errors.append(f"`{key}` is in {canonical.name} but not {copy.relative_to(REPO_ROOT)}")
        elif left[key] != right[key]:
            errors.append(f"`{key}` differs between the two plugin manifests")

    if not MARKETPLACE.is_file():
        errors.append(".claude-plugin/marketplace.json is missing")
        return errors
    try:
        market = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f".claude-plugin/marketplace.json: not valid JSON - {exc}")
        return errors

    entries = [e for e in market.get("plugins", []) if e.get("name") == left.get("name")]
    if not entries:
        errors.append(
            f".claude-plugin/marketplace.json lists no plugin named `{left.get('name')}`"
        )
        return errors
    entry = entries[0]
    for key in ("version", "description"):
        if entry.get(key) != left.get(key):
            errors.append(f"the marketplace entry's `{key}` has drifted from the plugin manifest")
    source = REPO_ROOT / entry.get("source", "").lstrip("./")
    if source.resolve() != canonical.parent.resolve():
        errors.append(
            f"the marketplace entry's `source` is {entry.get('source')!r}, "
            f"which is not where the plugin manifest lives"
        )
    return errors


def check_context_files() -> list[str]:
    """The scaffold's per-host context files import AGENTS.md and say nothing else.

    `AGENTS.md` is the entry point, and Copilot and Codex read it directly.
    Claude Code reads `CLAUDE.md` only, with no fallback, and Gemini CLI
    reads `GEMINI.md` unless configured otherwise - so each gets a file
    carrying the import. Anything else written into one of them is guidance
    the other hosts never see, which is the drift this catches.
    """
    errors: list[str] = []
    if not SCAFFOLD_AGENTS.is_file():
        errors.append("scaffold/AGENTS.md is missing - it is the entry point the others import")
    for name in CONTEXT_POINTERS:
        path = SCAFFOLD_DIR / name
        if not path.is_file():
            errors.append(f"scaffold/{name} is missing - {CONTEXT_IMPORT} is all it needs to hold")
            continue
        lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
        body = [line for line in lines if line and not line.startswith("#")]
        if body != [CONTEXT_IMPORT]:
            errors.append(
                f"scaffold/{name} holds more than `{CONTEXT_IMPORT}`; "
                f"content here is content the other hosts never see"
            )
    return errors


def main() -> int:
    # Findings carry em-dashes, notation glyphs and whatever a heading is
    # named in. A console that cannot encode them should show a replacement
    # character, not raise and take the whole run down with it.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):  # pragma: no cover - older or wrapped streams
            pass
    known = skill_names()
    if not known:
        print(f"No skills found under {SKILLS_DIR.relative_to(REPO_ROOT)} - nothing to check.")
        return 0

    # The labels are also what the success line reports, so a check added here
    # is announced without a second list to keep in step.
    checks = [
        ("section markers", check_section_markers(known)),
        ("process binding", check_process_binding(known)),
        ("required sections", check_required_sections(known)),
        ("prefix registry", check_prefix_registry()),
        ("reference files", check_references_reachable(known)),
        ("scaffold specimens", check_scaffold_specimens()),
        ("catalogue", check_catalogue(known)),
        ("assets", check_assets(known)),
        ("manifests", check_manifests()),
        ("context files", check_context_files()),
    ]

    all_errors: list[str] = []
    for label, errors in checks:
        if errors:
            all_errors.append(f"{label}:")
            all_errors.extend(f"  {e}" for e in errors)

    if all_errors:
        print("Skill corpus errors:")
        for line in all_errors:
            print(f"  {line}")
        return 1

    converted = sum(1 for s in known if skill_meta(s).get("kind"))
    labels = [label for label, _ in checks]
    named = ", ".join(labels[:-1]) + f" and {labels[-1]}"
    print(f"{len(known)} skills ({converted} converted): {named} all resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
