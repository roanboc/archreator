#!/usr/bin/env python3
"""Small, source-fresh helpers for an ArChreator Markdown model.

Nothing is cached or persisted. Every command reads the current Markdown files.
The module is also a deliberately small Python API for agents that need to walk
the model without scraping command output.
"""

from __future__ import annotations

import argparse
import html
import importlib.util
import re
import secrets
import sys
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence
from urllib.parse import unquote


WORK_RELATIVE = Path(".archreator") / "work"
IGNORE_ENTRY = "/.archreator/work/"
ID_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_.:-]*\d[A-Za-z0-9_.:-]*")
HIERARCHICAL_ID = re.compile(r"^(.+)\.(\d+)$")
ELEMENT_HEADERS = ("id", "name", "archimate type", "description")
TABLE_SEPARATOR = re.compile(r":?-{3,}:?")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
SELF_LOCATION = re.compile(r"^\*\*Location:\*\*\s+\S", re.MULTILINE)
SAFE_RUN_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}")


class ArChreatorError(RuntimeError):
    """An expected user-facing error."""


@dataclass(frozen=True)
class Element:
    """One element declared in a Markdown table containing an ``ID`` column."""

    id: str
    name: str
    kind: str
    path: Path
    line: int
    attributes: dict[str, str] = field(compare=False, hash=False)


@dataclass(frozen=True)
class Relationship:
    """A directed relationship declared by a From/To/Relationship table."""

    source: str
    target: str
    kind: str
    meaning: str
    path: Path
    line: int
    source_name: str | None = None
    target_name: str | None = None


@dataclass(frozen=True)
class Issue:
    """A model or link validation problem."""

    code: str
    message: str
    path: Path
    line: int = 0


@dataclass(frozen=True)
class TraceStep:
    """One shortest-path step returned by :func:`trace`."""

    depth: int
    direction: str
    relationship: Relationship
    element: Element


@dataclass(frozen=True)
class Model:
    """An in-memory view built from the current repository source."""

    root: Path
    elements: dict[str, Element]
    relationships: tuple[Relationship, ...]
    issues: tuple[Issue, ...]


@dataclass(frozen=True)
class _Table:
    headers: tuple[str, ...]
    rows: tuple[tuple[int, tuple[str, ...]], ...]
    line: int


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _split_table_row(line: str) -> tuple[str, ...]:
    """Split a Markdown table row while retaining escaped pipes."""

    text = line.strip()
    if text.startswith("|"):
        text = text[1:]
    if text.endswith("|") and not text.endswith(r"\|"):
        text = text[:-1]

    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for char in text:
        if escaped:
            current.append(char)
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == "|":
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    if escaped:
        current.append("\\")
    cells.append("".join(current).strip())
    return tuple(cells)


def _plain_text(value: str) -> str:
    value = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"<br\s*/?>", " ", value, flags=re.IGNORECASE)
    value = value.replace("__", "")
    value = re.sub(r"[`*~]", "", value)
    return html.unescape(value).strip()


def _normalise_header(value: str) -> str:
    return re.sub(r"\s+", " ", _plain_text(value)).casefold()


def _identifier(value: str) -> str | None:
    text = _plain_text(value)
    if not text or text in {"-", "--", "---", "—"} or text.startswith("<"):
        return None
    return text if ID_PATTERN.fullmatch(text) else None


def _relationship_endpoint(value: str) -> tuple[str | None, str | None]:
    """Return the ID and visible name from a required ``Name [ID]`` reference."""

    text = _plain_text(value)
    decorated = re.fullmatch(r"(.+?)\s+\[([^\[\]]+)\]", text)
    if not decorated:
        return None, None
    name = re.sub(r"\s+", " ", decorated.group(1)).strip()
    candidate = decorated.group(2).strip()
    if not name or not ID_PATTERN.fullmatch(candidate):
        return None, None
    return candidate, name


def _markdown_tables(text: str) -> tuple[_Table, ...]:
    lines = text.splitlines()
    fenced = [False] * len(lines)
    marker: str | None = None
    for index, line in enumerate(lines):
        match = FENCE.match(line)
        if match:
            token = match.group(1)
            if marker is None:
                marker = token[0]
                fenced[index] = True
                continue
            if token[0] == marker:
                fenced[index] = True
                marker = None
                continue
        fenced[index] = marker is not None

    tables: list[_Table] = []
    index = 0
    while index + 1 < len(lines):
        if fenced[index] or fenced[index + 1] or "|" not in lines[index]:
            index += 1
            continue
        headers = _split_table_row(lines[index])
        separator = _split_table_row(lines[index + 1])
        if (
            len(headers) < 2
            or len(headers) != len(separator)
            or not all(TABLE_SEPARATOR.fullmatch(cell.strip()) for cell in separator)
        ):
            index += 1
            continue

        rows: list[tuple[int, tuple[str, ...]]] = []
        cursor = index + 2
        while cursor < len(lines) and not fenced[cursor] and "|" in lines[cursor]:
            cells = _split_table_row(lines[cursor])
            if len(cells) != len(headers):
                break
            rows.append((cursor + 1, cells))
            cursor += 1
        tables.append(_Table(headers, tuple(rows), index + 1))
        index = cursor
    return tuple(tables)


def _relationship_columns(headers: Sequence[str]) -> tuple[int, int, int] | None:
    normalised = [_normalise_header(header) for header in headers]
    source = next((normalised.index(name) for name in ("from", "source") if name in normalised), None)
    target = next((normalised.index(name) for name in ("to", "target") if name in normalised), None)
    kind = next(
        (normalised.index(name) for name in ("relationship", "relation") if name in normalised),
        None,
    )
    if source is None or target is None or kind is None:
        return None
    return source, target, kind


def _read_markdown(path: Path) -> tuple[str | None, Issue | None]:
    try:
        return path.read_text(encoding="utf-8"), None
    except (OSError, UnicodeError) as exc:
        return None, Issue("UNREADABLE_MARKDOWN", str(exc), path)


def load_model(repository: str | Path) -> Model:
    """Read ``architecture/**/*.md`` into a new in-memory graph.

    Call this again after a source edit. There is intentionally no cache to
    invalidate and no generated graph to rebuild.
    """

    root = Path(repository).resolve()
    architecture = root / "architecture"
    if not architecture.is_dir():
        issue = Issue("MODEL_ROOT_MISSING", "architecture/ does not exist", architecture)
        return Model(root, {}, (), (issue,))

    declarations: dict[str, list[Element]] = {}
    relationships: list[Relationship] = []
    issues: list[Issue] = []

    for path in sorted(architecture.rglob("*.md")):
        if _inside(path.resolve(), (root / WORK_RELATIVE).resolve()):
            continue
        text, read_issue = _read_markdown(path)
        if read_issue:
            issues.append(read_issue)
            continue
        assert text is not None
        if path.relative_to(architecture).as_posix().casefold() != "readme.md":
            title = HEADING.match(text.lstrip("\ufeff"))
            if title is None or len(title.group(1)) != 1:
                issues.append(
                    Issue(
                        "MISSING_TITLE",
                        "canonical files need an H1 that names their subject",
                        path,
                        1,
                    )
                )
            if not SELF_LOCATION.search(text):
                issues.append(
                    Issue(
                        "MISSING_LOCATION",
                        "canonical files need a **Location:** line that states their area and hierarchy",
                        path,
                        1,
                    )
                )
        for table in _markdown_tables(text):
            relationship_columns = _relationship_columns(table.headers)
            if relationship_columns:
                source_column, target_column, kind_column = relationship_columns
                normalised = [_normalise_header(header) for header in table.headers]
                meaning_column = normalised.index("meaning") if "meaning" in normalised else None
                for line, row in table.rows:
                    if not any(cell.strip() for cell in row):
                        continue
                    source, source_name = _relationship_endpoint(row[source_column])
                    target, target_name = _relationship_endpoint(row[target_column])
                    kind = _plain_text(row[kind_column])
                    if not source or not target or not kind:
                        issues.append(
                            Issue(
                                "INVALID_RELATIONSHIP",
                                "relationship rows need valid From, To and Relationship values",
                                path,
                                line,
                            )
                        )
                        continue
                    meaning = _plain_text(row[meaning_column]) if meaning_column is not None else ""
                    relationships.append(
                        Relationship(
                            source,
                            target,
                            kind,
                            meaning,
                            path,
                            line,
                            source_name,
                            target_name,
                        )
                    )
                continue

            normalised = [_normalise_header(header) for header in table.headers]
            if "id" not in normalised:
                continue
            if tuple(normalised[:4]) != ELEMENT_HEADERS:
                issues.append(
                    Issue(
                        "INVALID_ELEMENT_TABLE",
                        "element catalogues must begin with ID, Name, ArchiMate type and Description",
                        path,
                        table.line,
                    )
                )
                continue
            id_column = 0
            name_column = 1
            type_column = 2
            parent_column = normalised.index("parent") if "parent" in normalised else None
            for line, row in table.rows:
                if not any(cell.strip() for cell in row):
                    continue
                identifier = _identifier(row[id_column])
                if not identifier:
                    if row[id_column].strip() not in {"", "-", "--", "---", "—"}:
                        issues.append(
                            Issue("INVALID_ID", f"invalid element ID: {_plain_text(row[id_column])!r}", path, line)
                        )
                    continue
                attributes = {
                    _plain_text(header): _plain_text(value)
                    for header, value in zip(table.headers, row)
                    if _normalise_header(header) != "id"
                }
                name = _plain_text(row[name_column]) or identifier
                kind = (
                    _plain_text(row[type_column])
                    if _plain_text(row[type_column])
                    else _plain_text(table.headers[name_column])
                )
                declarations.setdefault(identifier, []).append(
                    Element(identifier, name, kind, path, line, attributes)
                )
                hierarchy = HIERARCHICAL_ID.fullmatch(identifier)
                if hierarchy:
                    expected_parent = hierarchy.group(1)
                    if parent_column is None:
                        issues.append(
                            Issue(
                                "MISSING_PARENT_REFERENCE",
                                f"nested element {_element_reference(declarations[identifier][-1])} needs a Parent column",
                                path,
                                line,
                            )
                        )
                        continue
                    parent, parent_name = _relationship_endpoint(row[parent_column])
                    if not parent or not parent_name:
                        issues.append(
                            Issue(
                                "INVALID_PARENT_REFERENCE",
                                f"nested element {_element_reference(declarations[identifier][-1])} needs Parent as Name [ID]",
                                path,
                                line,
                            )
                        )
                        continue
                    if parent != expected_parent:
                        issues.append(
                            Issue(
                                "PARENT_ID_MISMATCH",
                                f"{_element_reference(declarations[identifier][-1])} expects parent ID {expected_parent}, not {parent}",
                                path,
                                line,
                            )
                        )
                        continue
                    relationships.append(
                        Relationship(
                            parent,
                            identifier,
                            "Composition",
                            f"{parent_name} composes {name}.",
                            path,
                            line,
                            parent_name,
                            name,
                        )
                    )
                elif parent_column is not None and _plain_text(row[parent_column]) not in {
                    "",
                    "-",
                    "--",
                    "---",
                    "—",
                }:
                    issues.append(
                        Issue(
                            "UNEXPECTED_PARENT_REFERENCE",
                            f"top-level element {_element_reference(declarations[identifier][-1])} cannot declare a hierarchical parent",
                            path,
                            line,
                        )
                    )

    elements: dict[str, Element] = {}
    for identifier, occurrences in declarations.items():
        elements[identifier] = occurrences[0]
        for duplicate in occurrences[1:]:
            first = occurrences[0]
            issues.append(
                Issue(
                    "DUPLICATE_ID",
                    f"{_element_reference(first)} was first declared at "
                    f"{first.path.relative_to(root)}:{first.line}",
                    duplicate.path,
                    duplicate.line,
                )
            )

    for relationship in relationships:
        if relationship.source not in elements:
            source_reference = f"{relationship.source_name} [{relationship.source}]"
            issues.append(
                Issue(
                    "UNRESOLVED_ID",
                    f"relationship source {source_reference} is not declared",
                    relationship.path,
                    relationship.line,
                )
            )
        elif relationship.source_name is not None and relationship.source_name != elements[relationship.source].name:
            issues.append(
                Issue(
                    "STALE_REFERENCE_NAME",
                    f"relationship source {relationship.source_name} [{relationship.source}] "
                    f"does not match {_element_reference(elements[relationship.source])}",
                    relationship.path,
                    relationship.line,
                )
            )
        if relationship.target not in elements:
            target_reference = f"{relationship.target_name} [{relationship.target}]"
            issues.append(
                Issue(
                    "UNRESOLVED_ID",
                    f"relationship target {target_reference} is not declared",
                    relationship.path,
                    relationship.line,
                )
            )
        elif relationship.target_name is not None and relationship.target_name != elements[relationship.target].name:
            issues.append(
                Issue(
                    "STALE_REFERENCE_NAME",
                    f"relationship target {relationship.target_name} [{relationship.target}] "
                    f"does not match {_element_reference(elements[relationship.target])}",
                    relationship.path,
                    relationship.line,
                )
            )

    issues.extend(check_relative_links(root, architecture))
    return Model(root, elements, tuple(relationships), tuple(issues))


def _without_fenced_lines(text: str) -> Iterable[tuple[int, str]]:
    marker: str | None = None
    for line_number, line in enumerate(text.splitlines(), 1):
        match = FENCE.match(line)
        if match:
            token = match.group(1)[0]
            if marker is None:
                marker = token
            elif marker == token:
                marker = None
            continue
        if marker is None:
            yield line_number, line


def _link_destination(raw: str) -> str:
    value = raw.strip()
    if value.startswith("<") and ">" in value:
        return value[1 : value.index(">")]
    return value.split(maxsplit=1)[0]


def _anchor_slugs(path: Path) -> set[str]:
    text, issue = _read_markdown(path)
    if issue or text is None:
        return set()
    seen: dict[str, int] = {}
    slugs: set[str] = set()
    for _, line in _without_fenced_lines(text):
        match = HEADING.match(line)
        if not match:
            continue
        heading = _plain_text(match.group(2)).casefold()
        slug = re.sub(r"[^\w\- ]", "", heading, flags=re.UNICODE)
        slug = re.sub(r"\s+", "-", slug.strip())
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        slugs.add(slug if count == 0 else f"{slug}-{count}")
    return slugs


def check_relative_links(repository: str | Path, source_root: str | Path | None = None) -> tuple[Issue, ...]:
    """Check local Markdown links and anchors under ``source_root``."""

    root = Path(repository).resolve()
    scan_root = Path(source_root).resolve() if source_root else root / "architecture"
    if not scan_root.is_dir():
        return ()
    issues: list[Issue] = []
    anchors: dict[Path, set[str]] = {}

    for path in sorted(scan_root.rglob("*.md")):
        text, read_issue = _read_markdown(path)
        if read_issue:
            issues.append(read_issue)
            continue
        assert text is not None
        for line, content in _without_fenced_lines(text):
            for match in MARKDOWN_LINK.finditer(content):
                destination = _link_destination(match.group(1))
                if not destination or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", destination) or destination.startswith("//"):
                    continue
                raw_path, separator, raw_anchor = destination.partition("#")
                raw_path = unquote(raw_path.split("?", 1)[0])
                anchor = unquote(raw_anchor).casefold()
                target = path if not raw_path else (path.parent / raw_path).resolve()
                if not _inside(target, root):
                    issues.append(Issue("LINK_OUTSIDE_REPOSITORY", f"link leaves repository: {destination}", path, line))
                    continue
                if not target.exists():
                    issues.append(Issue("BROKEN_LINK", f"target does not exist: {destination}", path, line))
                    continue
                anchor_target = target
                if target.is_dir():
                    anchor_target = target / "README.md"
                if separator and anchor_target.suffix.casefold() == ".md":
                    available = anchors.setdefault(anchor_target, _anchor_slugs(anchor_target))
                    if anchor not in available:
                        issues.append(Issue("BROKEN_ANCHOR", f"anchor does not exist: {destination}", path, line))
    return tuple(issues)


def trace(model: Model, element_id: str, direction: str = "both", depth: int = 1) -> tuple[TraceStep, ...]:
    """Walk outgoing, incoming or both relationship directions breadth-first."""

    if element_id not in model.elements:
        raise ArChreatorError(f"element is not declared: {element_id}")
    if direction not in {"forward", "reverse", "both"}:
        raise ArChreatorError("direction must be forward, reverse or both")
    if depth < 1:
        raise ArChreatorError("depth must be at least 1")

    outgoing: dict[str, list[Relationship]] = {}
    incoming: dict[str, list[Relationship]] = {}
    for relationship in model.relationships:
        outgoing.setdefault(relationship.source, []).append(relationship)
        incoming.setdefault(relationship.target, []).append(relationship)

    queue: deque[tuple[str, int]] = deque([(element_id, 0)])
    visited = {element_id}
    steps: list[TraceStep] = []
    while queue:
        current, current_depth = queue.popleft()
        if current_depth >= depth:
            continue
        candidates: list[tuple[str, Relationship, str]] = []
        if direction in {"forward", "both"}:
            candidates.extend((edge.target, edge, "forward") for edge in outgoing.get(current, ()))
        if direction in {"reverse", "both"}:
            candidates.extend((edge.source, edge, "reverse") for edge in incoming.get(current, ()))
        for neighbour, relationship, walked_direction in candidates:
            if neighbour in visited or neighbour not in model.elements:
                continue
            visited.add(neighbour)
            next_depth = current_depth + 1
            steps.append(
                TraceStep(next_depth, walked_direction, relationship, model.elements[neighbour])
            )
            queue.append((neighbour, next_depth))
    return tuple(steps)


def ensure_work_directory(repository: str | Path, name: str | None = None) -> Path:
    """Create one ignored, project-local output directory and return it."""

    root = Path(repository).resolve()
    if not root.is_dir():
        raise ArChreatorError(f"repository does not exist: {root}")
    if name is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        name = f"{stamp}-{secrets.token_hex(3)}"
    if not SAFE_RUN_NAME.fullmatch(name) or name in {".", ".."}:
        raise ArChreatorError("run name may contain only letters, numbers, dots, dashes and underscores")

    _ensure_work_ignored(root)

    destination = root / WORK_RELATIVE / name
    try:
        destination.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise ArChreatorError(f"work run already exists: {name}") from exc
    return destination


def _ensure_work_ignored(root: Path) -> None:
    ignore_file = root / ".gitignore"
    existing = ignore_file.read_text(encoding="utf-8") if ignore_file.exists() else ""
    if IGNORE_ENTRY not in {line.strip() for line in existing.splitlines()}:
        separator = "" if not existing or existing.endswith(("\n", "\r")) else "\n"
        ignore_file.write_text(f"{existing}{separator}{IGNORE_ENTRY}\n", encoding="utf-8")


def build_portal_output(repository: str | Path, source_base_url: str | None = None) -> Path:
    """Build the optional portal through its sibling module, only on request."""

    root = Path(repository).resolve()
    if not root.is_dir():
        raise ArChreatorError(f"repository does not exist: {root}")
    _ensure_work_ignored(root)
    module_path = Path(__file__).resolve().parents[1] / "portal" / "build_portal.py"
    if not module_path.is_file():
        raise ArChreatorError(f"portal builder is missing: {module_path}")
    spec = importlib.util.spec_from_file_location("_archreator_portal", module_path)
    if spec is None or spec.loader is None:
        raise ArChreatorError(f"portal builder cannot be loaded: {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        return module.build_portal(root, source_base_url)
    except Exception as exc:
        portal_error = getattr(module, "PortalError", ())
        if portal_error and isinstance(exc, portal_error):
            raise ArChreatorError(str(exc)) from exc
        raise


def _require_work_path(root: Path, value: str | Path, label: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = candidate.resolve()
    work_root = (root / WORK_RELATIVE).resolve()
    if not _inside(candidate, work_root):
        raise ArChreatorError(f"{label} must be inside {WORK_RELATIVE.as_posix()}/")
    return candidate


def export_pdf(
    repository: str | Path,
    source: str | Path,
    *,
    kind: str,
    output: str | Path | None = None,
) -> Path:
    """Export one requested scope or brief from the work area to PDF.

    Both input and output are restricted to ``.archreator/work``. This API
    cannot point at the architecture directory and is not a model publisher.
    """

    root = Path(repository).resolve()
    if kind not in {"brief", "scope"}:
        raise ArChreatorError("PDF kind must be brief or scope")
    source_path = _require_work_path(root, source, "PDF source")
    if source_path.suffix.casefold() != ".md" or not source_path.is_file():
        raise ArChreatorError("PDF source must be an existing Markdown file")
    output_path = _require_work_path(root, output or source_path.with_suffix(".pdf"), "PDF output")
    if output_path.suffix.casefold() != ".pdf":
        raise ArChreatorError("PDF output must end in .pdf")

    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            ListFlowable,
            ListItem,
            PageBreak,
            Paragraph,
            Preformatted,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
    except ModuleNotFoundError as exc:
        raise ArChreatorError(
            "PDF export needs reportlab. Install it with: python -m pip install reportlab"
        ) from exc

    source_text = source_path.read_text(encoding="utf-8")
    lines = source_text.splitlines()
    if len(lines) >= 2 and lines[0].strip() == "---":
        try:
            close = lines[1:].index("---") + 1
            lines = lines[close + 1 :]
        except ValueError:
            pass

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            "DocumentTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=27,
            textColor=colors.HexColor("#17324D"),
            spaceAfter=8 * mm,
        )
    )
    for level, size, colour in (
        (1, 16, "#17324D"),
        (2, 13, "#24577A"),
        (3, 11, "#24577A"),
    ):
        styles.add(
            ParagraphStyle(
                f"Heading{level}Clean",
                parent=styles[f"Heading{level}"],
                fontName="Helvetica-Bold",
                fontSize=size,
                leading=size + 4,
                textColor=colors.HexColor(colour),
                spaceBefore=5 * mm,
                spaceAfter=2.5 * mm,
                keepWithNext=True,
            )
        )
    styles.add(
        ParagraphStyle(
            "BodyClean",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor("#24303A"),
            spaceAfter=2.5 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            "Meta",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#637381"),
            alignment=TA_CENTER,
        )
    )
    styles.add(
        ParagraphStyle(
            "TableHeader",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=colors.white,
        )
    )

    def paragraph(value: str, style: str = "BodyClean"):
        return Paragraph(html.escape(_plain_text(value)), styles[style])

    story: list[object] = []
    title = source_path.stem.replace("-", " ").replace("_", " ").title()
    first_heading = next((HEADING.match(line) for line in lines if HEADING.match(line)), None)
    if first_heading:
        title = _plain_text(first_heading.group(2))
    story.append(paragraph(title, "DocumentTitle"))
    story.append(paragraph(f"{kind.title()} exported from {source_path.name}", "Meta"))
    story.append(Spacer(1, 5 * mm))

    index = 0
    first_title_skipped = False
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        heading = HEADING.match(line)
        if heading:
            level = len(heading.group(1))
            if level == 1 and not first_title_skipped:
                first_title_skipped = True
                index += 1
                continue
            story.append(paragraph(heading.group(2), f"Heading{min(level, 3)}Clean"))
            index += 1
            continue
        if line.strip() in {"---", "***"}:
            story.append(Spacer(1, 3 * mm))
            index += 1
            continue
        if line.startswith("```") or line.startswith("~~~"):
            fence = line[:3]
            code: list[str] = []
            index += 1
            while index < len(lines) and not lines[index].startswith(fence):
                code.append(lines[index])
                index += 1
            index += 1
            story.append(Preformatted("\n".join(code), styles["Code"]))
            story.append(Spacer(1, 2 * mm))
            continue
        if index + 1 < len(lines) and "|" in line:
            headers = _split_table_row(line)
            separator = _split_table_row(lines[index + 1])
            if len(headers) >= 2 and len(headers) == len(separator) and all(
                TABLE_SEPARATOR.fullmatch(cell.strip()) for cell in separator
            ):
                data = [[paragraph(cell, "TableHeader") for cell in headers]]
                index += 2
                while index < len(lines) and "|" in lines[index]:
                    cells = _split_table_row(lines[index])
                    if len(cells) != len(headers):
                        break
                    data.append([paragraph(cell) for cell in cells])
                    index += 1
                page_width = A4[0] - 36 * mm
                table = Table(data, colWidths=[page_width / len(headers)] * len(headers), repeatRows=1)
                table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17324D")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C9D3DC")),
                            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F7F9")]),
                            ("LEFTPADDING", (0, 0), (-1, -1), 5),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                            ("TOPPADDING", (0, 0), (-1, -1), 5),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                        ]
                    )
                )
                story.extend([table, Spacer(1, 3 * mm)])
                continue
        if re.match(r"^\s*[-*+]\s+", line):
            items: list[object] = []
            while index < len(lines) and re.match(r"^\s*[-*+]\s+", lines[index]):
                value = re.sub(r"^\s*[-*+]\s+", "", lines[index])
                items.append(ListItem(paragraph(value), leftIndent=10))
                index += 1
            story.append(ListFlowable(items, bulletType="bullet", leftIndent=14, bulletFontName="Helvetica"))
            story.append(Spacer(1, 2 * mm))
            continue
        if line.strip() == "<!-- pagebreak -->":
            story.append(PageBreak())
            index += 1
            continue

        paragraph_lines = [line.strip()]
        index += 1
        while index < len(lines) and lines[index].strip():
            if HEADING.match(lines[index]) or re.match(r"^\s*[-*+]\s+", lines[index]):
                break
            if index + 1 < len(lines) and "|" in lines[index] and all(
                TABLE_SEPARATOR.fullmatch(cell.strip()) for cell in _split_table_row(lines[index + 1])
            ):
                break
            paragraph_lines.append(lines[index].strip())
            index += 1
        story.append(paragraph(" ".join(paragraph_lines)))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
        title=title,
        author="ArChreator",
    )

    def footer(canvas, document_state):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#D5DDE4"))
        canvas.line(18 * mm, 13 * mm, A4[0] - 18 * mm, 13 * mm)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(colors.HexColor("#637381"))
        canvas.drawString(18 * mm, 8.5 * mm, f"ArChreator {kind}")
        canvas.drawRightString(A4[0] - 18 * mm, 8.5 * mm, f"Page {document_state.page}")
        canvas.restoreState()

    document.build(story, onFirstPage=footer, onLaterPages=footer)
    return output_path


def _display_issue(issue: Issue, root: Path) -> str:
    try:
        location = issue.path.relative_to(root).as_posix()
    except ValueError:
        location = str(issue.path)
    if issue.line:
        location = f"{location}:{issue.line}"
    return f"{location}: {issue.code}: {issue.message}"


def _markdown_cell(value: object) -> str:
    return str(value).replace("|", r"\|").replace("\r", " ").replace("\n", " ")


def _element_reference(element: Element) -> str:
    return f"{element.name} [{element.id}]"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read and check an ArChreator Markdown model")
    parser.add_argument("--repo", default=".", help="repository root (default: current directory)")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("check", help="check model IDs, relationships and local Markdown links")

    trace_parser = commands.add_parser("trace", help="walk relationships from one element")
    trace_parser.add_argument("element_id")
    trace_parser.add_argument("--direction", choices=("forward", "reverse", "both"), default="both")
    trace_parser.add_argument("--depth", type=int, default=1)

    work_parser = commands.add_parser("work", help="create an ignored output directory")
    work_parser.add_argument("--name", help="stable run name; omitted names use UTC time plus a random suffix")

    pdf_parser = commands.add_parser("pdf", help="export one work-area scope or brief to PDF")
    pdf_parser.add_argument("source", help="Markdown source inside .archreator/work/")
    pdf_parser.add_argument("--kind", choices=("scope", "brief"), required=True)
    pdf_parser.add_argument("--output", help="PDF path inside .archreator/work/")

    portal_parser = commands.add_parser("portal", help="build the optional human-facing portal")
    portal_parser.add_argument("--source-base-url", help="web URL containing the project sources")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    root = Path(args.repo).resolve()
    try:
        if args.command == "check":
            model = load_model(root)
            if model.issues:
                for issue in model.issues:
                    print(_display_issue(issue, root))
                return 1
            print(f"OK: {len(model.elements)} elements, {len(model.relationships)} relationships")
            return 0
        if args.command == "trace":
            model = load_model(root)
            steps = trace(model, args.element_id, args.direction, args.depth)
            start = model.elements[args.element_id]
            print(f"# {args.direction.title()} trace from {_element_reference(start)} (depth {args.depth})")
            print("| Depth | Direction | Relationship | Meaning | Element | Source |")
            print("| ---: | --- | --- | --- | --- | --- |")
            for step in steps:
                source = f"{step.element.path.relative_to(root).as_posix()}:{step.element.line}"
                print(
                    f"| {step.depth} | {_markdown_cell(step.direction)} | "
                    f"{_markdown_cell(step.relationship.kind)} | {_markdown_cell(step.relationship.meaning)} | "
                    f"{_markdown_cell(_element_reference(step.element))} | {source} |"
                )
            return 0
        if args.command == "work":
            print(ensure_work_directory(root, args.name))
            return 0
        if args.command == "pdf":
            print(export_pdf(root, args.source, kind=args.kind, output=args.output))
            return 0
        if args.command == "portal":
            print(build_portal_output(root, args.source_base_url))
            return 0
    except (ArChreatorError, OSError, UnicodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
