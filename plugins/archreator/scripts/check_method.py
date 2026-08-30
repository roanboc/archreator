#!/usr/bin/env python3
"""Validate the ArChreator method package without third-party dependencies."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile
from typing import Mapping, Sequence


EXPECTED_SKILLS = frozenset(
    {
        "model-context",
        "deliver-change",
        "plan-roadmap",
        "answer-context-question",
        "federate-context",
        "write-brief",
        "record-decision",
        "document-style",
        "architecture-document-style",
        "process-and-capability-levels",
    }
)

KIND_MARKERS = {
    "gated-procedure": ("Procedure —", "⚙"),
    "document-template": ("Document —", "▤"),
    "rulebook": ("Rulebook —", "※"),
}

DEFAULT_SECTION_CONTRACT = {
    "gated-procedure": frozenset(
        {
            "⊕ When to use this",
            "⊖ When not to",
            "⌖ Where this sits",
            "⚓ Invariants",
            "⚙ Steps",
            "⇄ Hands off to",
            "⚠ Anti-patterns",
            "☑ Done when",
        }
    ),
    "document-template": frozenset(
        {
            "⊕ When to use this",
            "⊖ When not to",
            "⌖ Where this sits",
            "▤ Template",
            "※ Rules",
            "⚠ Anti-patterns",
            "☑ Done when",
        }
    ),
    "rulebook": frozenset(
        {
            "⊕ When to use this",
            "⊖ When not to",
            "⌖ Where this sits",
            "※ Rules",
            "⚠ Anti-patterns",
        }
    ),
}

EXPECTED_SCAFFOLD_FILES = frozenset(
    {
        ".gitignore",
        "AGENTS.md",
        "CLAUDE.md",
        "GEMINI.md",
        "architecture/README.md",
    }
)
EXPECTED_SCAFFOLD_DIRECTORIES = frozenset({"architecture"})

OLD_SCRIPT_NAMES = frozenset(
    {
        "build_brief.py",
        "build_docs.py",
        "build_model.py",
        "check_links.py",
        "check_model.py",
        "element-prefixes.json",
        "export_pdf.py",
        "model_graph.py",
        "neighbourhood.sql",
        "query_model.py",
    }
)

SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PROCESS_ID = re.compile(r"^BPROC\d+\.\d+$")
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
STEP_HEADING = re.compile(r"^###\s+\d+(?:\.|\s+—)\s+.+$", re.MULTILINE)
GATE_MARKER = re.compile(r"^\*\*❖\s+(?:Gate\s+—\s+)?(.+?)\*\*", re.MULTILINE)
NEEDS_MARKER = re.compile(r"\*\*←\s+Needs\.?\*\*")
PRODUCES_MARKER = re.compile(r"\*\*→\s+Produces\.?\*\*")
CROSS_REFERENCE = re.compile(r"`([a-z0-9]+(?:-[a-z0-9]+)*)`\s+§\s+")


@dataclass(frozen=True)
class Issue:
    path: Path
    code: str
    message: str
    line: int | None = None

    def display(self, root: Path) -> str:
        try:
            location = self.path.resolve().relative_to(root.resolve()).as_posix()
        except (OSError, ValueError):
            location = str(self.path)
        if self.line is not None:
            location += f":{self.line}"
        return f"{location}: {self.code}: {self.message}"


@dataclass(frozen=True)
class SkillRecord:
    path: Path
    folder_name: str
    declared_name: str
    kind: str
    description: str
    process_ids: tuple[str, ...]
    gates: tuple[str, ...]
    body: str
    body_start_line: int
    headings: frozenset[str]


class FrontmatterError(ValueError):
    """The constrained skill frontmatter is malformed."""


def _scalar(value: str, line_number: int) -> str:
    value = value.strip()
    if not value:
        raise FrontmatterError(f"line {line_number}: scalar value is empty")
    if value[0] in "[{|>&*!" or value.startswith("-"):
        raise FrontmatterError(
            f"line {line_number}: only inline string values and nested mappings are supported"
        )
    if value.startswith('"'):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise FrontmatterError(f"line {line_number}: invalid quoted string") from exc
        if not isinstance(parsed, str):
            raise FrontmatterError(f"line {line_number}: value must be a string")
        return parsed
    if value.startswith("'"):
        if len(value) < 2 or not value.endswith("'"):
            raise FrontmatterError(f"line {line_number}: invalid quoted string")
        return value[1:-1].replace("''", "'")
    return value


def parse_frontmatter(text: str) -> tuple[dict[str, object], str, int]:
    """Parse the small mapping-only YAML subset used by ArChreator skills."""

    lines = text.splitlines()
    if not lines or lines[0].lstrip("\ufeff") != "---":
        raise FrontmatterError("line 1: expected opening ---")
    try:
        closing = next(index for index in range(1, len(lines)) if lines[index] == "---")
    except StopIteration as exc:
        raise FrontmatterError("frontmatter has no closing ---") from exc

    root: dict[str, object] = {}
    stack: list[tuple[int, dict[str, object]]] = [(-1, root)]
    key_pattern = re.compile(r"^([A-Za-z0-9_.-]+):(?:\s*(.*))?$")

    for index, raw in enumerate(lines[1:closing], start=2):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if "\t" in raw:
            raise FrontmatterError(f"line {index}: tabs are not allowed")
        indent = len(raw) - len(raw.lstrip(" "))
        match = key_pattern.fullmatch(raw[indent:])
        if not match:
            raise FrontmatterError(f"line {index}: expected key: value")

        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            raise FrontmatterError(f"line {index}: invalid indentation")
        parent_indent, parent = stack[-1]
        expected_indent = 0 if parent_indent == -1 else parent_indent + 2
        if indent != expected_indent:
            raise FrontmatterError(
                f"line {index}: expected {expected_indent} spaces, found {indent}"
            )

        key, raw_value = match.groups()
        if key in parent:
            raise FrontmatterError(f"line {index}: duplicate key {key}")
        if raw_value is None or raw_value == "":
            child: dict[str, object] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = _scalar(raw_value, index)

    return root, "\n".join(lines[closing + 1 :]), closing + 2


def _markdown_cells(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    return [cell.strip() for cell in stripped[1:-1].split("|")]


def section_contract_from_text(text: str) -> dict[str, frozenset[str]]:
    required: dict[str, set[str]] = {kind: set() for kind in KIND_MARKERS}
    column_kind = {
        3: "gated-procedure",
        4: "document-template",
        5: "rulebook",
    }
    for line in text.splitlines():
        cells = _markdown_cells(line)
        if len(cells) < 6:
            continue
        glyph = cells[0].strip("`")
        if glyph not in {"⊕", "⊖", "⌖", "⚓", "⚙", "▤", "※", "⇄", "✎", "⚠", "☑"}:
            continue
        heading = f"{glyph} {cells[1]}"
        for column, kind in column_kind.items():
            if cells[column].casefold().startswith("required"):
                required[kind].add(heading)
    return {kind: frozenset(headings) for kind, headings in required.items()}


def _mapping(value: object, field: str) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise FrontmatterError(f"{field} must be a mapping")
    return value


def _field(mapping: Mapping[str, object], field: str) -> str:
    value = mapping.get(field)
    if not isinstance(value, str) or not value.strip():
        raise FrontmatterError(f"{field} must be a non-empty string")
    return value.strip()


def _split_csv(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(",") if part.strip())


def _plain_heading(raw: str) -> str:
    raw = re.sub(r"^[⊕⊖⌖⚓⚙▤※⇄✎⚠☑]\s+", "", raw.strip())
    return re.sub(r"\s+", " ", raw).strip().casefold()


def validate_skill(
    skill_file: Path,
    section_contract: Mapping[str, frozenset[str]],
) -> tuple[SkillRecord | None, list[Issue]]:
    issues: list[Issue] = []
    try:
        text = skill_file.read_text(encoding="utf-8")
        frontmatter, body, body_start = parse_frontmatter(text)
        name = _field(frontmatter, "name")
        description = _field(frontmatter, "description")
        metadata = _mapping(frontmatter.get("metadata"), "metadata")
        archreator = _mapping(metadata.get("archreator"), "metadata.archreator")
        kind = _field(archreator, "kind")
        raw_gates = _field(archreator, "gates")
        raw_processes = archreator.get("realizes_process", "")
        if not isinstance(raw_processes, str):
            raise FrontmatterError("metadata.archreator.realizes_process must be a string")
    except (OSError, UnicodeError, FrontmatterError) as exc:
        issues.append(Issue(skill_file, "FRONTMATTER", str(exc)))
        return None, issues

    folder_name = skill_file.parent.name
    if not SKILL_NAME.fullmatch(folder_name):
        issues.append(Issue(skill_file, "SKILL_FOLDER", f"invalid skill folder name {folder_name!r}"))
    if name != folder_name:
        issues.append(
            Issue(skill_file, "SKILL_NAME", f"frontmatter name {name!r} must match folder {folder_name!r}")
        )
    if kind not in KIND_MARKERS:
        issues.append(Issue(skill_file, "SKILL_KIND", f"unsupported kind {kind!r}"))

    headings = [(len(mark.group(1)), mark.group(2)) for mark in HEADING.finditer(body)]
    plain_headings = frozenset(_plain_heading(raw) for _, raw in headings)
    h1 = next((raw for level, raw in headings if level == 1), "")

    if kind in KIND_MARKERS:
        description_marker, h1_marker = KIND_MARKERS[kind]
        if not description.startswith(description_marker):
            issues.append(
                Issue(
                    skill_file,
                    "DESCRIPTION_KIND",
                    f"description for {kind} must start with {description_marker!r}",
                )
            )
        if not h1.startswith(h1_marker + " "):
            issues.append(
                Issue(skill_file, "H1_KIND", f"H1 for {kind} must start with {h1_marker!r}")
            )
        for required in section_contract.get(kind, frozenset()):
            if not re.search(rf"^##\s+{re.escape(required)}\s*$", body, re.MULTILINE):
                issues.append(
                    Issue(skill_file, "MISSING_SECTION", f"required section '## {required}' is missing")
                )

    process_ids = _split_csv(raw_processes)
    for process_id in process_ids:
        if not PROCESS_ID.fullmatch(process_id):
            issues.append(Issue(skill_file, "PROCESS_ID", f"invalid process ID {process_id!r}"))

    if raw_gates.casefold() == "none":
        gates: tuple[str, ...] = ()
    else:
        gates = _split_csv(raw_gates)
        if not gates or any(gate.casefold() == "none" for gate in gates):
            issues.append(Issue(skill_file, "GATES", "gates must be comma-separated names or 'none'"))

    found_gates: list[str] = []
    for match in GATE_MARKER.finditer(body):
        label = match.group(1).strip()
        if label.endswith("."):
            label = label[:-1].rstrip()
        found_gates.append(label)
    declared_by_key = {gate.casefold(): gate for gate in gates}
    found_by_key = {gate.casefold(): gate for gate in found_gates}
    for key, gate in declared_by_key.items():
        if key not in found_by_key:
            issues.append(Issue(skill_file, "MISSING_GATE", f"declared gate {gate!r} has no ❖ marker"))
    for key, gate in found_by_key.items():
        if key not in declared_by_key:
            issues.append(Issue(skill_file, "UNDECLARED_GATE", f"❖ marker {gate!r} is not declared"))
    if kind != "gated-procedure" and gates:
        issues.append(Issue(skill_file, "GATE_KIND", "only a gated-procedure may declare gates"))

    if kind == "gated-procedure":
        steps_heading = re.search(r"^##\s+⚙\s+Steps\s*$", body, re.MULTILINE)
        if steps_heading:
            next_h2 = re.search(r"^##\s+", body[steps_heading.end() :], re.MULTILINE)
            end = steps_heading.end() + next_h2.start() if next_h2 else len(body)
            steps_text = body[steps_heading.end() : end]
            step_matches = list(STEP_HEADING.finditer(steps_text))
            if not step_matches:
                issues.append(Issue(skill_file, "NO_STEPS", "procedure has no numbered steps"))
            for index, step in enumerate(step_matches):
                step_end = step_matches[index + 1].start() if index + 1 < len(step_matches) else len(steps_text)
                step_text = steps_text[step.end() : step_end]
                title = step.group(0).removeprefix("### ")
                if not NEEDS_MARKER.search(step_text):
                    issues.append(Issue(skill_file, "STEP_NEEDS", f"step {title!r} has no Needs marker"))
                if not PRODUCES_MARKER.search(step_text):
                    issues.append(
                        Issue(skill_file, "STEP_PRODUCES", f"step {title!r} has no Produces marker")
                    )

    record = SkillRecord(
        path=skill_file,
        folder_name=folder_name,
        declared_name=name,
        kind=kind,
        description=description,
        process_ids=process_ids,
        gates=gates,
        body=body,
        body_start_line=body_start,
        headings=plain_headings,
    )
    return record, issues


def process_rows_from_text(text: str) -> tuple[dict[str, frozenset[str]], list[str]]:
    rows: dict[str, frozenset[str]] = {}
    duplicates: list[str] = []
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        header = _markdown_cells(lines[index])
        if "ID" not in header or "Realized by" not in header:
            index += 1
            continue
        id_column = header.index("ID")
        skill_column = header.index("Realized by")
        index += 2
        while index < len(lines):
            cells = _markdown_cells(lines[index])
            if len(cells) != len(header):
                break
            process_id = cells[id_column].strip("`")
            if PROCESS_ID.fullmatch(process_id):
                skills = frozenset(re.findall(r"`([a-z0-9]+(?:-[a-z0-9]+)*)`", cells[skill_column]))
                if process_id in rows:
                    duplicates.append(process_id)
                rows[process_id] = skills
            index += 1
    return rows, duplicates


def validate_process_bindings(
    records: Mapping[str, SkillRecord],
    rows: Mapping[str, frozenset[str]],
    process_path: Path,
) -> list[Issue]:
    issues: list[Issue] = []
    for name, record in records.items():
        for process_id in record.process_ids:
            if process_id not in rows:
                issues.append(
                    Issue(record.path, "UNKNOWN_PROCESS", f"{process_id} is absent from the SIPOC model")
                )
            elif name not in rows[process_id]:
                issues.append(
                    Issue(
                        record.path,
                        "PROCESS_NOT_LISTED",
                        f"{process_id} does not name {name!r} in its Realized by cell",
                    )
                )
    for process_id, names in rows.items():
        for name in names:
            record = records.get(name)
            if record is None:
                issues.append(
                    Issue(
                        process_path,
                        "PROCESS_SKILL_MISSING",
                        f"{process_id} names missing skill {name!r}",
                    )
                )
            elif process_id not in record.process_ids:
                issues.append(
                    Issue(
                        process_path,
                        "SKILL_PROCESS_MISSING",
                        f"{process_id} names {name!r}, but that skill does not declare the process",
                    )
                )
    return issues


def validate_cross_references(records: Mapping[str, SkillRecord]) -> list[Issue]:
    issues: list[Issue] = []
    for source in records.values():
        flattened = re.sub(r"\s+", " ", source.body)
        for match in CROSS_REFERENCE.finditer(flattened):
            target_name = match.group(1)
            target = records.get(target_name)
            if target is None:
                issues.append(
                    Issue(source.path, "CROSS_SKILL", f"reference names missing skill {target_name!r}")
                )
                continue
            remainder = flattened[match.end() :].casefold()
            if not any(remainder.startswith(heading) for heading in target.headings if heading):
                sample = remainder.split(".", 1)[0][:80].strip()
                issues.append(
                    Issue(
                        source.path,
                        "CROSS_HEADING",
                        f"{target_name!r} has no heading matching {sample!r}",
                    )
                )
    return issues


def validate_catalogue(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    skills_root = root / "plugins" / "archreator" / "skills"
    catalogue = skills_root / "README.md"
    try:
        directories = {path.name for path in skills_root.iterdir() if path.is_dir()}
    except OSError as exc:
        return [Issue(skills_root, "SKILL_DIRECTORIES", str(exc))]
    missing = sorted(EXPECTED_SKILLS - directories)
    extra = sorted(directories - EXPECTED_SKILLS)
    if missing:
        issues.append(Issue(skills_root, "SKILL_DIRECTORIES", f"missing skill directories: {', '.join(missing)}"))
    if extra:
        issues.append(Issue(skills_root, "SKILL_DIRECTORIES", f"unexpected skill directories: {', '.join(extra)}"))
    try:
        catalogue_text = catalogue.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        issues.append(Issue(catalogue, "CATALOGUE", str(exc)))
        return issues
    links = re.findall(r"\]\(\./([a-z0-9]+(?:-[a-z0-9]+)*)/SKILL\.md(?:#[^)]+)?\)", catalogue_text)
    counts = Counter(links)
    listed = set(counts)
    if listed != EXPECTED_SKILLS:
        issues.append(
            Issue(
                catalogue,
                "CATALOGUE",
                f"catalogue skills differ: missing={sorted(EXPECTED_SKILLS - listed)}, extra={sorted(listed - EXPECTED_SKILLS)}",
            )
        )
    duplicates = sorted(name for name, count in counts.items() if count != 1)
    if duplicates:
        issues.append(Issue(catalogue, "CATALOGUE", f"skills must be linked once: {', '.join(duplicates)}"))
    return issues


def _load_json(path: Path) -> tuple[object | None, Issue | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, Issue(path, "JSON", str(exc))


def validate_manifests(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    plugin_root = root / "plugins" / "archreator"
    manifest_paths = [
        plugin_root / "plugin.json",
        plugin_root / ".claude-plugin" / "plugin.json",
        plugin_root / ".codex-plugin" / "plugin.json",
    ]
    manifests: list[tuple[Path, object]] = []
    for path in manifest_paths:
        value, issue = _load_json(path)
        if issue:
            issues.append(issue)
        else:
            manifests.append((path, value))
    if len(manifests) == len(manifest_paths):
        canonical = manifests[0][1]
        for path, value in manifests[1:]:
            if value != canonical:
                issues.append(Issue(path, "MANIFEST_MISMATCH", "plugin manifest differs from plugin.json"))

    marketplace_path = root / ".claude-plugin" / "marketplace.json"
    marketplace, issue = _load_json(marketplace_path)
    if issue:
        issues.append(issue)
    if manifests and isinstance(manifests[0][1], dict) and isinstance(marketplace, dict):
        version = manifests[0][1].get("version")
        entries = marketplace.get("plugins")
        entry = next(
            (item for item in entries if isinstance(item, dict) and item.get("name") == "archreator"),
            None,
        ) if isinstance(entries, list) else None
        if entry is None:
            issues.append(Issue(marketplace_path, "MARKETPLACE", "archreator entry is missing"))
        elif entry.get("version") != version:
            issues.append(
                Issue(
                    marketplace_path,
                    "MARKETPLACE_VERSION",
                    f"marketplace version {entry.get('version')!r} does not match {version!r}",
                )
            )
    return issues


def validate_scaffold(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    scaffold = root / "plugins" / "archreator" / "scaffold"
    if not scaffold.is_dir():
        return [Issue(scaffold, "SCAFFOLD", "scaffold directory is missing")]
    files = {path.relative_to(scaffold).as_posix() for path in scaffold.rglob("*") if path.is_file()}
    directories = {
        path.relative_to(scaffold).as_posix() for path in scaffold.rglob("*") if path.is_dir()
    }
    missing = sorted(EXPECTED_SCAFFOLD_FILES - files)
    extra = sorted(files - EXPECTED_SCAFFOLD_FILES)
    if missing:
        issues.append(Issue(scaffold, "SCAFFOLD_FILES", f"missing files: {', '.join(missing)}"))
    if extra:
        issues.append(Issue(scaffold, "SCAFFOLD_FILES", f"unexpected files: {', '.join(extra)}"))
    unexpected_directories = sorted(directories - EXPECTED_SCAFFOLD_DIRECTORIES)
    if unexpected_directories:
        issues.append(
            Issue(scaffold, "SCAFFOLD_DIRECTORIES", f"unexpected directories: {', '.join(unexpected_directories)}")
        )
    for directory in sorted(path for path in scaffold.rglob("*") if path.is_dir()):
        if not any(child.is_file() for child in directory.rglob("*")):
            issues.append(
                Issue(directory, "EMPTY_SCAFFOLD_AREA", "empty scaffold directories are not allowed")
            )

    for pointer_name in ("CLAUDE.md", "GEMINI.md"):
        pointer = scaffold / pointer_name
        try:
            content = pointer.read_text(encoding="utf-8").strip()
        except (OSError, UnicodeError) as exc:
            issues.append(Issue(pointer, "POINTER", str(exc)))
            continue
        if content != "@AGENTS.md":
            issues.append(Issue(pointer, "POINTER", "file must contain only @AGENTS.md"))
    ignore = scaffold / ".gitignore"
    try:
        entries = {line.strip() for line in ignore.read_text(encoding="utf-8").splitlines() if line.strip()}
        if "/.archreator/work/" not in entries:
            issues.append(Issue(ignore, "WORK_IGNORE", "missing /.archreator/work/"))
    except (OSError, UnicodeError) as exc:
        issues.append(Issue(ignore, "WORK_IGNORE", str(exc)))
    return issues


def validate_forbidden_implementation(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    plugin_root = root / "plugins" / "archreator"
    if not plugin_root.is_dir():
        return [Issue(plugin_root, "PLUGIN", "plugin directory is missing")]
    for path in plugin_root.rglob("*"):
        if not path.is_file():
            continue
        lowered = path.name.casefold()
        if lowered in OLD_SCRIPT_NAMES:
            issues.append(Issue(path, "OLD_SCRIPT", "obsolete scaffold/runtime script remains"))
        if path.suffix.casefold() in {".db", ".sqlite", ".sqlite3", ".sql"}:
            issues.append(Issue(path, "PERSISTED_GRAPH", "database artifacts are not part of the method"))
        if path.suffix.casefold() == ".py":
            try:
                source = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                issues.append(Issue(path, "PYTHON_READ", str(exc)))
                continue
            if re.search(r"(?m)^\s*(?:import\s+sqlite3\b|from\s+sqlite3\b)", source):
                issues.append(Issue(path, "SQLITE", "SQLite implementation is not allowed"))
    return issues


def _load_runtime(path: Path):
    spec = importlib.util.spec_from_file_location("_archreator_method_runtime_check", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("runtime module cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
        sys.modules.pop(spec.name, None)
    return module


def validate_runtime_boundaries(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    runtime_path = root / "plugins" / "archreator" / "scripts" / "archreator.py"
    try:
        runtime = _load_runtime(runtime_path)
        error_type = runtime.ArChreatorError
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            architecture = project / "architecture"
            architecture.mkdir()
            model = architecture / "README.md"
            model.write_text("# Temporary architecture\n", encoding="utf-8")

            work = runtime.ensure_work_directory(project, "method-check")
            expected_work = project / ".archreator" / "work" / "method-check"
            if work.resolve() != expected_work.resolve():
                issues.append(Issue(runtime_path, "WORK_BOUNDARY", f"work output was {work}"))
            ignore = (project / ".gitignore").read_text(encoding="utf-8")
            if "/.archreator/work/" not in ignore.splitlines():
                issues.append(Issue(runtime_path, "WORK_BOUNDARY", "work output is not ignored"))

            expected_portal = project / ".archreator" / "work" / "portal" / "index.html"
            if expected_portal.exists():
                issues.append(Issue(runtime_path, "PORTAL_BOUNDARY", "portal exists before request"))
            portal = runtime.build_portal_output(project)
            if portal.resolve() != expected_portal.resolve() or not portal.is_file():
                issues.append(Issue(runtime_path, "PORTAL_BOUNDARY", f"portal output was {portal}"))

            brief = work / "brief.md"
            brief.write_text("# Temporary brief\n", encoding="utf-8")

            def must_reject(label: str, operation) -> None:
                try:
                    operation()
                except error_type:
                    return
                issues.append(Issue(runtime_path, "PDF_BOUNDARY", f"PDF API accepted {label}"))

            must_reject("architecture source", lambda: runtime.export_pdf(project, model, kind="brief"))
            must_reject("whole-model kind", lambda: runtime.export_pdf(project, brief, kind="model"))
            must_reject(
                "output outside work",
                lambda: runtime.export_pdf(project, brief, kind="scope", output=project / "scope.pdf"),
            )
    except Exception as exc:  # A validator should report a broken runtime, not crash.
        issues.append(Issue(runtime_path, "RUNTIME_BOUNDARY", f"boundary check failed: {exc}"))
    return issues


def validate_output_contracts(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    checks = {
        root / "plugins" / "archreator" / "skills" / "write-brief" / "SKILL.md": (
            ".archreator/work/<run>/",
            "individual brief or scope to PDF",
        ),
        root / "plugins" / "archreator" / "skills" / "answer-context-question" / "SKILL.md": (
            ".archreator/work/portal/",
            "only on request",
        ),
        root
        / "plugins"
        / "archreator"
        / "skills"
        / "architecture-document-style"
        / "references"
        / "archimate-on-mermaid.md": (
            "<glyph> «ArchiMate type» Human name [ID]",
            "## Conditional human decisions",
        ),
        root
        / "plugins"
        / "archreator"
        / "skills"
        / "architecture-document-style"
        / "references"
        / "hierarchical-elements.md": (
            "## Give every populated level a file",
            "`**Location:**`",
            "## Name the parent on every child",
            "`Name [ID]`",
        ),
        root
        / "plugins"
        / "archreator"
        / "skills"
        / "process-and-capability-levels"
        / "references"
        / "process-presentation-patterns.md": (
            "`ID | Name | ArchiMate type | Description`",
            "`Name [ID]`",
            "## Level 1 — process landscape",
            "## Level 2 — process contract",
            "## Level 3 — operational flow",
            "## Level 4 — operating tasks",
        ),
    }
    for path, phrases in checks.items():
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            issues.append(Issue(path, "OUTPUT_CONTRACT", str(exc)))
            continue
        for phrase in phrases:
            if phrase.casefold() not in text.casefold():
                issues.append(Issue(path, "OUTPUT_CONTRACT", f"missing boundary statement {phrase!r}"))
    return issues


def validate_repository(root: Path) -> list[Issue]:
    root = root.resolve()
    issues: list[Issue] = []
    skills_root = root / "plugins" / "archreator" / "skills"
    contract_path = root / "docs" / "skill-format.md"
    process_path = root / "docs" / "process" / "README.md"

    try:
        contract_text = contract_path.read_text(encoding="utf-8")
        section_contract = section_contract_from_text(contract_text)
        incomplete = [kind for kind, headings in section_contract.items() if not headings]
        if incomplete:
            issues.append(
                Issue(contract_path, "SECTION_CONTRACT", f"no required sections parsed for: {', '.join(incomplete)}")
            )
            section_contract = DEFAULT_SECTION_CONTRACT
        elif section_contract != DEFAULT_SECTION_CONTRACT:
            issues.append(
                Issue(
                    contract_path,
                    "SECTION_CONTRACT",
                    "required glyph sections differ from the restored AIP contract",
                )
            )
    except (OSError, UnicodeError) as exc:
        issues.append(Issue(contract_path, "SECTION_CONTRACT", str(exc)))
        section_contract = DEFAULT_SECTION_CONTRACT

    records: dict[str, SkillRecord] = {}
    if skills_root.is_dir():
        for directory in sorted((path for path in skills_root.iterdir() if path.is_dir()), key=lambda path: path.name):
            skill_file = directory / "SKILL.md"
            if not skill_file.is_file():
                issues.append(Issue(skill_file, "SKILL_FILE", "SKILL.md is missing"))
                continue
            record, skill_issues = validate_skill(skill_file, section_contract)
            issues.extend(skill_issues)
            if record is not None:
                records[directory.name] = record
    else:
        issues.append(Issue(skills_root, "SKILLS", "skills directory is missing"))

    try:
        process_files = sorted(process_path.parent.glob("*.md"))
        if not process_files:
            raise OSError("process model has no Markdown files")
        process_text = "\n\n".join(
            path.read_text(encoding="utf-8") for path in process_files
        )
        rows, duplicates = process_rows_from_text(process_text)
        for process_id in duplicates:
            issues.append(Issue(process_path, "DUPLICATE_PROCESS", f"duplicate SIPOC row {process_id}"))
        if not rows:
            issues.append(Issue(process_path, "PROCESS_MODEL", "no level-2 SIPOC rows found"))
        issues.extend(validate_process_bindings(records, rows, process_path))
    except (OSError, UnicodeError) as exc:
        issues.append(Issue(process_path, "PROCESS_MODEL", str(exc)))

    issues.extend(validate_cross_references(records))
    issues.extend(validate_catalogue(root))
    issues.extend(validate_manifests(root))
    issues.extend(validate_scaffold(root))
    issues.extend(validate_forbidden_implementation(root))
    issues.extend(validate_runtime_boundaries(root))
    issues.extend(validate_output_contracts(root))
    return sorted(issues, key=lambda issue: (str(issue.path), issue.line or 0, issue.code, issue.message))


def _parser() -> argparse.ArgumentParser:
    default_root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description="Validate the ArChreator method package")
    parser.add_argument("--repo", type=Path, default=default_root, help="repository root")
    return parser


def _safe_print(value: str) -> None:
    """Print Unicode diagnostics even when a Windows console uses cp1252."""

    try:
        print(value)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or "ascii"
        escaped = value.encode(encoding, errors="backslashreplace").decode(encoding)
        print(escaped)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    root = args.repo.resolve()
    issues = validate_repository(root)
    if issues:
        for issue in issues:
            _safe_print(issue.display(root))
        _safe_print(f"FAILED: {len(issues)} method contract error(s)")
        return 1
    _safe_print(f"OK: {len(EXPECTED_SKILLS)} skills and the ArChreator method contract are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
