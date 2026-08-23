#!/usr/bin/env python3
"""Parse the layered model into a graph, once, for whoever needs it.

`check_model.py` built this graph in memory, checked it and threw it away.
That was the right shape while validation was the only consumer. A published
view of the model is a second consumer, and it needs the same parse — so the
parse moved here rather than being written twice, because two parsers of the
same convention drift and the drift is silent.

Nothing here validates and nothing here persists. `check_model.py` imports it
and applies its four checks; `build_model.py` imports it and writes the
projection. This module only reads Markdown and returns what it found.

**Two levels of detail.** `parse_project()` returns what validation needs —
definitions, references, retirements, domains. `parse_project(detail=True)`
additionally reads element names, the remaining table columns, and the typed
edges drawn in Mermaid, none of which a validator has any use for.

**Structure is read from the identifier, never from a heading.** An element's
type comes from its ID prefix, its group from the registry beside this file,
its layer from the numbered folder, its parent from the dot. All four survive
translation, which matters because a model may be written in any language:
`architecture-document-style` fixes the ID grammar and the notation, and fixes
nothing about the words around them. A parser keyed on `Realized by` finds
nothing in a Spanish model. Column headers are therefore carried through as
opaque text and never interpreted.

Deliberately not done here:

- **No inference of relationship semantics.** A Mermaid edge label is carried
  verbatim — `habilita`, `precede a`, `serves`. Mapping those onto ArchiMate's
  relationship vocabulary would be a guess, and a wrong guess in a projection
  is worse than an honest string.
- **No parse of the narrative folders.** Same reasoning as `check_model.py`:
  a merged scope document is immutable and will outlive the elements it names.
- **No caching and no incremental parse.** A whole model is a few hundred
  files, and a projection that is regenerated from scratch cannot go stale.
"""
import json
import re
from dataclasses import dataclass, field
from pathlib import Path


def _find_repo_root(start: Path) -> Path:
    """The project this script is reading.

    The scripts ship inside the scaffold, so the same file runs from
    `<project>/scripts/` in a generated project and from the method's own
    `scaffold/scripts/`. Walking up to the enclosing repository gets the
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
# rather than part of it, and are deliberately not read.
NARRATIVE = {"scope", "decisions", "reviews", "engagements"}
# Directories that are tooling rather than repository content. `.git` is
# obvious; `.claude`, `.agents`, `.gemini`, `.codex` and `.copilot` hold
# agent-local material — installed and vendored third-party skills, worktrees,
# local settings — one per host the method runs on, and `.aip` is a checkout
# of the pinned AIP release the validators are run from. None is this
# repository's to validate, and none is a downstream project's once these
# scripts ship there.
# `.docs` is the documentation portal's staged copy and built site — every
# document a second time, which would otherwise read as every element being
# defined twice.
EXCLUDED_DIRS = {".git", ".claude", ".agents", ".gemini", ".codex", ".copilot",
                 ".aip", ".docs"}
# See the note in check_links.py: anchored to line starts and matched on fence
# length, so a fence containing a fence does not close early and leak its body
# back into the scanned prose.
FENCE_RE = re.compile(
    r"^(?P<ticks>`{3,})[^\n]*\n.*?^(?P=ticks)`*[ \t]*$",
    re.DOTALL | re.MULTILINE,
)

# Element-ID prefixes, loaded from the file that ships beside this script.
# The human-readable source is the table in the architecture-document-style
# skill; check_skills.py keeps the two in step, so this is not a second place
# to maintain the list.
PREFIX_FILE = Path(__file__).resolve().parent / "element-prefixes.json"
with PREFIX_FILE.open(encoding="utf-8") as handle:
    _GROUPS = json.load(handle)["prefixes"]
# Code -> the element type it names, and code -> the group it belongs to.
# Both are language-independent, which is the whole reason to key on them.
PREFIX_TYPES = {code: name for group in _GROUPS.values() for code, name in group.items()}
PREFIX_GROUPS = {code: label for label, group in _GROUPS.items() for code in group}
# Longest first, so alternation matches `BSVC` before `B`-prefixed neighbours.
PREFIXES = sorted(PREFIX_TYPES, key=len, reverse=True)

# The element itself: a type prefix, its number, then one dotted number per
# level below the top (`CAP1`, `CAP1.2`, `CAP1.2.3`).
_LOCAL = r"(?:" + "|".join(PREFIXES) + r")\d+(?:\.\d+)*"
# A full ID prepends the domain path, when there is one (`SALES.CAP1.2`).
_ID = r"(?:[A-Z][A-Z0-9]*\.)*" + _LOCAL

# A backticked ID anywhere in the prose or a table cell is a reference.
REFERENCE_RE = re.compile(r"`(" + _ID + r")`")
# A table row whose first cell is a bare backticked ID defines that element.
# A *domain-qualified* first cell is a reference instead — that is what a
# domain charter's "Consumed services" table holds. A *leveled* first cell
# (`BPROC7.2`) is a definition like any other: the dot is this element's own
# place in the catalogue, not somebody else's ownership of it.
TABLE_DEF_RE = re.compile(r"^\|\s*`([A-Z][A-Z0-9]*\d+(?:\.\d+)*)`\s*\|", re.M)
# Splits an ID into its domain path and the rest, so the two meanings of the
# dot never get confused for each other.
ID_PARTS_RE = re.compile(r"^((?:[A-Z][A-Z0-9]*\.)*)(" + _LOCAL + r")$")
# Goals and principles are written as bolded lead-ins rather than table rows.
BULLET_DEF_RE = re.compile(r"\*\*(" + _ID + r")\s+—", re.M)
RETIRED_HEADING_RE = re.compile(r"^##+\s+Retired\s*$", re.M)
TABLE_ROW_RE = re.compile(r"^\|.*\|\s*$", re.M)
ID_HEADER_RE = re.compile(r"^\|\s*(?:Qualified\s+)?ID\s*\|", re.I)
# Splits the prefix off a local ID, so `CAP1.2` yields `CAP`.
LOCAL_PREFIX_RE = re.compile(r"^([A-Z][A-Z0-9]*?)\d")
# A numbered layer folder — `1_strategy`, `1_estrategia`. The digit is the
# layer and survives translation; the slug does not.
LAYER_DIR_RE = re.compile(r"^(\d)_(.+)$")
# The name in a bolded lead-in definition: `**G1 — Legible guidance.**`
BULLET_NAME_RE = re.compile(r"\*\*(" + _ID + r")\s+—\s+(.+?)\*\*", re.S)
# A table's separator row, which is what marks the line above it as headers.
TABLE_SEP_RE = re.compile(r"^\|[\s:|-]+\|\s*$")
# A catalogue cell that leads with the element's name in bold, before any gloss.
NAME_LEAD_RE = re.compile(r"^\*\*(.+?)\*\*")

# A fenced Mermaid block. Matched on the raw text, before fences are stripped.
MERMAID_RE = re.compile(
    r"^(?P<ticks>`{3,})mermaid[^\n]*\n(?P<body>.*?)^(?P=ticks)`*[ \t]*$",
    re.DOTALL | re.MULTILINE,
)
# A Mermaid node declaration. The shape brackets vary by element type — see
# `architecture/README.md` § Shapes — so this matches the variable name and
# the first quoted label, whatever brackets sit between them.
MERMAID_NODE_RE = re.compile(r'^\s*(\w+)\s*[\[({>/\\]+\s*"([^"]*)"', re.M)
# A Mermaid edge, with the optional `|label|` the notation puts relationships
# in. Covers the arrow forms the notation actually uses: solid, dotted and
# thick, which is every form in the corpus.
MERMAID_EDGE_RE = re.compile(
    r"^\s*(\w+)\s*(?:-{2,3}>|-\.-+>|={2,3}>)\s*(?:\|([^|]*)\|)?\s*(\w+)", re.M
)
# The identifier a node label ends with: `✦ Fundación de datos [CAP2.3]`.
NODE_ID_RE = re.compile(r"\[(" + _ID + r")\]\s*$")


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


def qualifier_of(element: str) -> str:
    """The domain path of an ID, or "" when it is unqualified.

    `SALES.BPROC1.3` is qualified and `BPROC1.3` is not, even though both
    contain a dot: the levels sit after the prefix, the domain before it.
    """
    match = ID_PARTS_RE.match(element)
    return match.group(1).rstrip(".") if match else ""


def local_of(element: str) -> str:
    """The ID with any domain path removed — `SALES.CAP1.2` yields `CAP1.2`."""
    match = ID_PARTS_RE.match(element)
    return match.group(2) if match else element


def prefix_of(element: str) -> str:
    """The type prefix of an ID — `SALES.CAP1.2` yields `CAP`."""
    match = LOCAL_PREFIX_RE.match(local_of(element))
    return match.group(1) if match else ""


def parent_of(element: str) -> str:
    """The ID one level up, or "" for an element that is already top-level.

    A trailing numeric segment is a level, so `SALES.CAP1.2` is a child of
    `SALES.CAP1`, while `SALES.CAP1` is a top-level capability whose leading
    segment names its domain rather than a parent element.
    """
    head, _, tail = element.rpartition(".")
    return head if tail.isdigit() else ""


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


def _excluded(path: Path) -> bool:
    return bool(EXCLUDED_DIRS & set(path.parts))


def find_projects() -> list[Path]:
    """A project is the directory containing an `architecture/` folder."""
    projects = []
    for model_dir in sorted(REPO_ROOT.rglob(MODEL_DIR)):
        if _excluded(model_dir) or not model_dir.is_dir():
            continue
        projects.append(model_dir.parent)
    return projects


def domain_of(md_file: Path, project: Path) -> str:
    """Upper-cased domain path for a file inside `architecture/domains/<name>/`."""
    parts = md_file.relative_to(project).parts
    segments = [parts[i + 1] for i, part in enumerate(parts[:-1]) if part == "domains"]
    return ".".join(s.upper() for s in segments)


def layer_of(md_file: Path, model_root: Path) -> tuple[str, str]:
    """(number, folder) of the numbered layer a file sits in, or ("", "").

    The first numbered folder on the path wins, which is also the right answer
    inside a domain: `domains/sales/1_strategy/x.md` is the strategy layer.
    """
    for part in md_file.relative_to(model_root).parts[:-1]:
        match = LAYER_DIR_RE.match(part)
        if match:
            return match.group(1), part
    return "", ""


def model_files(project: Path) -> list[Path]:
    """Every Markdown file of the model proper, narrative folders excluded."""
    model_root = project / MODEL_DIR
    return [
        path
        for path in sorted(model_root.rglob("*.md"))
        if not _excluded(path)
        and "scaffold" not in path.parts
        and not (NARRATIVE & set(path.relative_to(model_root).parts))
    ]


def _cells(row: str) -> list[str]:
    """The cells of a Markdown table row, outer pipes dropped."""
    return [cell.strip() for cell in row.strip().strip("|").split("|")]


def _plain(cell: str) -> str:
    """A table cell reduced to its text: links, bold and code spans removed."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", cell)
    text = text.replace("**", "").replace("`", "")
    return text.strip()


def _name_of(cell: str) -> str:
    """The element's name from its cell.

    A catalogue cell is either the name alone or the name in bold followed by
    an em-dash gloss — `**Operaciones y transformación** — entregar con…`.
    The bold run is the name in both cases; the gloss stays in `attrs` with
    the rest of the row.
    """
    match = NAME_LEAD_RE.match(cell.strip())
    return _plain(match.group(1)) if match else _plain(cell)


def table_definitions(text: str) -> dict[str, tuple[str, dict[str, str]]]:
    """Map each ID defined in a catalogue table to its name and its columns.

    **Only tables whose first header is `ID` are read.** An identifier
    legitimately appears in the first column of other tables — a capability
    area is listed again against the assessments it answers, for instance —
    and those rows say something about the element rather than defining it.
    Taking a name from one produces a confident, wrong answer, which is worse
    than none. `ID_HEADER_RE` is the same test `unvalidated_tables()` uses to
    decide what counts as a catalogue, so there is one rule, not two.

    The name is the second cell, which the notation fixes. Every column from
    the second on is carried under its own header as opaque text — headers are
    prose in whatever language the model is written in, so interpreting them
    here would make this parser monolingual.
    """
    found: dict[str, tuple[str, dict[str, str]]] = {}
    headers: list[str] = []
    is_catalogue = False
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if TABLE_SEP_RE.match(line):
            header_line = lines[index - 1] if index else ""
            if TABLE_ROW_RE.match(header_line or ""):
                headers = [_plain(cell) for cell in _cells(header_line)]
                is_catalogue = ID_HEADER_RE.match(header_line) is not None
            continue
        match = TABLE_DEF_RE.match(line)
        if not match or not headers or not is_catalogue:
            continue
        cells = _cells(line)
        if len(cells) < 2:
            continue
        attrs = {
            headers[i]: _plain(cells[i])
            for i in range(1, min(len(cells), len(headers)))
            if headers[i]
        }
        found[match.group(1)] = (_name_of(cells[1]), attrs)
    return found


def bullet_definitions(text: str) -> dict[str, str]:
    """Map each ID defined as a bolded lead-in to its name."""
    return {
        match.group(1): _plain(match.group(2)).rstrip(".")
        for match in BULLET_NAME_RE.finditer(text)
    }


def mermaid_edges(text: str) -> list[tuple[str, str, str]]:
    """Typed edges (source ID, target ID, label) drawn in Mermaid.

    This is the only place a relationship between two elements is written
    machine-readably: a table column names a relationship in prose, but a
    diagram names both ends. The label is carried verbatim — see the module
    docstring on why it is not mapped onto ArchiMate's vocabulary.

    Runs on the raw text, before `strip_code`, because the diagrams live
    inside the fences everything else deliberately drops.
    """
    edges: list[tuple[str, str, str]] = []
    for block in MERMAID_RE.finditer(text):
        body = block.group("body")
        ids: dict[str, str] = {}
        for node in MERMAID_NODE_RE.finditer(body):
            match = NODE_ID_RE.search(node.group(2))
            if match:
                ids[node.group(1)] = match.group(1)
        for edge in MERMAID_EDGE_RE.finditer(body):
            source, label, target = edge.group(1), edge.group(2), edge.group(3)
            if source in ids and target in ids:
                edges.append((ids[source], ids[target], (label or "").strip()))
    return edges


@dataclass
class Element:
    """One element of the model, as the documents define it."""

    id: str  # qualified within its project: `SALES.CAP1.2`, or `CAP1.2`
    local: str  # `CAP1.2`
    prefix: str  # `CAP`
    type: str  # `Capability`
    group: str  # `Strategy` — the element's own layer, from its prefix
    domain: str  # `SALES`, or "" outside a domain
    parent: str  # `SALES.CAP1`, or "" when top-level
    name: str
    doc: str  # repository-relative path of the defining document
    layer: str  # the numbered folder it was defined in — `1_strategy`
    layer_no: str  # `1`
    retired: bool
    attrs: dict[str, str] = field(default_factory=dict)


@dataclass
class Edge:
    """One relationship between two elements."""

    src: str
    dst: str
    rel: str  # `decomposes` | `references` | a verbatim Mermaid edge label
    doc: str


@dataclass
class ParsedProject:
    """Everything one project's documents say, before anyone judges it."""

    project: Path
    defined: dict[str, Path]
    duplicates: list[str]
    retired: dict[str, Path]
    references: list[tuple[str, Path]]
    domains: set[str]
    skipped: int
    elements: dict[str, Element] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)
    # (document, element) — where each element is spoken about. Kept apart
    # from `edges` because one end is a document rather than an element, and
    # mixing the two would make the element graph untraversable.
    mentions: list[tuple[str, str]] = field(default_factory=list)


def parse_project(project: Path, *, detail: bool = False) -> ParsedProject:
    """Read one project's model.

    Without `detail` this returns exactly what validation needs. With it,
    element names, the remaining table columns and the Mermaid edges are read
    too — work a validator has no use for and a projection cannot do without.
    """
    defined: dict[str, Path] = {}
    duplicates: list[str] = []
    retired: dict[str, Path] = {}
    references: list[tuple[str, Path]] = []
    domains: set[str] = set()
    skipped = 0
    elements: dict[str, Element] = {}
    edges: list[Edge] = []

    model_root = project / MODEL_DIR

    for md_file in model_files(project):
        raw = md_file.read_text(encoding="utf-8")
        text = strip_code(raw)
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
            if not qualifier_of(reference) and reference in defined_here:
                continue
            references.append((reference, md_file))

        if not detail:
            continue

        doc = str(md_file.relative_to(REPO_ROOT)).replace("\\", "/")
        layer_no, layer = layer_of(md_file, model_root)
        named = table_definitions(live_text)
        bullets = bullet_definitions(live_text)
        retired_here = definitions_in(retired_text)

        for element in sorted(definitions_in(live_text) | retired_here):
            key = f"{scope}.{element}" if scope else element
            if key in elements:
                continue
            name, attrs = named.get(element, ("", {}))
            if not name:
                name = bullets.get(element, "")
            prefix = prefix_of(element)
            elements[key] = Element(
                id=key,
                local=element,
                prefix=prefix,
                type=PREFIX_TYPES.get(prefix, ""),
                group=PREFIX_GROUPS.get(prefix, ""),
                domain=scope,
                parent=parent_of(key),
                name=name,
                doc=doc,
                layer=layer,
                layer_no=layer_no,
                retired=element in retired_here,
                attrs=attrs,
            )

        for source, target, label in mermaid_edges(raw):
            src = f"{scope}.{source}" if scope else source
            dst = f"{scope}.{target}" if scope else target
            # An unlabelled edge from a parent to its own child is the
            # decomposition the identifier already carries, drawn so a reader
            # can see it. Emitting both would double every level of every
            # catalogue.
            if not label and parent_of(dst) == src:
                continue
            edges.append(Edge(src=src, dst=dst, rel=label or "relates to", doc=doc))

    mentions: list[tuple[str, str]] = []
    if detail:
        for key, element in elements.items():
            if element.parent:
                edges.append(
                    Edge(src=element.parent, dst=key, rel="decomposes", doc=element.doc)
                )
        seen: set[tuple[str, str]] = set()
        for reference, md_file in references:
            scope = domain_of(md_file, project)
            doc = str(md_file.relative_to(REPO_ROOT)).replace("\\", "/")
            qualified = f"{scope}.{reference}" if scope else reference
            target = qualified if qualified in elements else reference
            if (doc, target) in seen:
                continue
            seen.add((doc, target))
            mentions.append((doc, target))
        mentions.sort()

    return ParsedProject(
        project=project,
        defined=defined,
        duplicates=duplicates,
        retired=retired,
        references=references,
        domains=domains,
        skipped=skipped,
        elements=elements,
        edges=edges,
        mentions=mentions,
    )
