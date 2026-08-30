#!/usr/bin/env python3
"""Build a disposable, human-facing portal from an ArChreator project.

The builder reads only canonical Markdown from ``README.md``, ``docs/`` and
``architecture/``. It writes the derived site to
``.archreator/work/portal/`` when this command is run; no portal files need to
be committed to the project.

Usage:
    python build_portal.py [PROJECT]
"""

from __future__ import annotations

import argparse
import html
import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Callable, Sequence
from urllib.parse import quote, unquote, urlsplit, urlunsplit


PORTAL_MARKER = ".archreator-portal"
PORTAL_VERSION = "1"


@dataclass(frozen=True)
class Layer:
    key: str
    name: str
    question: str


LAYERS: tuple[Layer, ...] = (
    Layer("0_business-design", "Business design", "Who is served, what do they need, and what is offered?"),
    Layer("1_strategy", "Strategy", "Why does this exist, and what direction guides it?"),
    Layer("2_business", "Business", "Who does what, and which services and processes deliver value?"),
    Layer("3_information", "Information", "What information exists, and how is it used and shared?"),
    Layer("4_application", "Application", "Which software services and components support the business?"),
    Layer("5_technology", "Technology", "What platforms, runtimes, and infrastructure run the solution?"),
    Layer("6_transition", "Roadmap and transition", "What should change, and in what order?"),
)


@dataclass(frozen=True)
class Document:
    source: Path
    relative: PurePosixPath
    output: PurePosixPath
    title: str
    summary: str
    search_text: str
    markdown: str
    layer_key: str | None


@dataclass(frozen=True)
class LayerState:
    layer: Layer
    label: str
    kind: str
    detail: str
    href: PurePosixPath | None
    document_count: int


@dataclass(frozen=True)
class SourceLocation:
    repository_root: Path
    web_base: str | None
    revision: str | None


class PortalError(RuntimeError):
    """Raised when a portal cannot be built safely."""


def _run_git(project: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(project), *args],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    value = result.stdout.strip()
    return value or None


def _normalise_remote(remote: str, revision: str) -> str | None:
    value = remote.strip()
    ssh_match = re.fullmatch(r"git@([^:]+):(.+)", value)
    if ssh_match:
        value = f"https://{ssh_match.group(1)}/{ssh_match.group(2)}"
    elif value.startswith("ssh://git@"):
        value = "https://" + value[len("ssh://git@") :].replace(":", "/", 1)
    value = re.sub(r"\.git$", "", value).rstrip("/")
    if not value.startswith(("https://", "http://")):
        return None
    host = urlsplit(value).hostname or ""
    if host.endswith("gitlab.com"):
        return f"{value}/-/blob/{quote(revision, safe='')}"
    if host.endswith("bitbucket.org"):
        return f"{value}/src/{quote(revision, safe='')}"
    return f"{value}/blob/{quote(revision, safe='')}"


def source_location(project: Path, explicit_base: str | None = None) -> SourceLocation:
    root_value = _run_git(project, "rev-parse", "--show-toplevel")
    repository_root = Path(root_value).resolve() if root_value else project
    revision = _run_git(project, "rev-parse", "HEAD")
    short_revision = _run_git(project, "rev-parse", "--short", "HEAD")
    if explicit_base:
        web_base = explicit_base.rstrip("/")
    else:
        remote = _run_git(project, "remote", "get-url", "origin")
        web_base = _normalise_remote(remote, revision) if remote and revision else None
    return SourceLocation(repository_root, web_base, short_revision)


def _output_path(relative: PurePosixPath) -> PurePosixPath:
    if relative == PurePosixPath("README.md"):
        return PurePosixPath("repository.html")
    if relative.name.casefold() == "readme.md":
        return relative.parent / "index.html"
    return relative.with_suffix(".html")


def _first_heading(markdown: str) -> str | None:
    match = re.search(r"(?m)^#\s+(.+?)\s*$", markdown)
    if not match:
        return None
    return _plain_inline(match.group(1))


def _plain_inline(value: str) -> str:
    value = re.sub(r"!\[([^]]*)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"[`*_~]", "", value)
    return html.unescape(value).strip()


def _plain_markdown(markdown: str) -> str:
    value = re.sub(r"<!--.*?-->", " ", markdown, flags=re.DOTALL)
    value = re.sub(r"```[^\n]*\n(.*?)```", r" \1 ", value, flags=re.DOTALL)
    value = re.sub(r"!\[([^]]*)\]\([^)]*\)", r" \1 ", value)
    value = re.sub(r"\[([^]]+)\]\([^)]*\)", r" \1 ", value)
    value = re.sub(r"(?m)^#{1,6}\s*", "", value)
    value = re.sub(r"(?m)^\s*[>|*+-]\s*", "", value)
    value = re.sub(r"[`*_~|]", " ", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def _summary(markdown: str, title: str) -> str:
    without_comments = re.sub(r"<!--.*?-->", "", markdown, flags=re.DOTALL)
    blocks = re.split(r"\n\s*\n", without_comments)
    for block in blocks:
        candidate = _plain_markdown(block)
        if not candidate or candidate == title or block.lstrip().startswith(("#", "|", "```")):
            continue
        return candidate if len(candidate) <= 220 else candidate[:217].rstrip() + "…"
    return "Canonical architecture documentation."


def _layer_for(relative: PurePosixPath) -> str | None:
    if len(relative.parts) >= 2 and relative.parts[0] == "architecture":
        key = relative.parts[1]
        if any(layer.key == key for layer in LAYERS):
            return key
    return None


def discover_documents(project: Path) -> list[Document]:
    candidates: list[Path] = []
    root_readme = project / "README.md"
    if root_readme.is_file():
        candidates.append(root_readme)
    for folder_name in ("architecture", "docs"):
        folder = project / folder_name
        if folder.is_dir():
            candidates.extend(path for path in folder.rglob("*.md") if path.is_file())

    def sort_key(path: Path) -> tuple[int, str]:
        relative = path.relative_to(project).as_posix()
        group = 0 if relative == "README.md" else 1 if relative.startswith("architecture/") else 2
        return group, relative.casefold()

    documents: list[Document] = []
    for path in sorted(set(candidates), key=sort_key):
        try:
            markdown = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise PortalError(f"Markdown is not UTF-8: {path}") from exc
        relative = PurePosixPath(path.relative_to(project).as_posix())
        title = _first_heading(markdown) or relative.stem.replace("-", " ").replace("_", " ").title()
        plain = _plain_markdown(markdown)
        documents.append(
            Document(
                source=path,
                relative=relative,
                output=_output_path(relative),
                title=title,
                summary=_summary(markdown, title),
                search_text=plain,
                markdown=markdown,
                layer_key=_layer_for(relative),
            )
        )
    return documents


def _strip_table_markup(value: str) -> str:
    value = _plain_inline(value)
    value = re.sub(r"\s+", " ", value)
    return value.strip(" .—–-")


def _explicit_layer_status(layer: Layer, documents: Sequence[Document]) -> str | None:
    sources: list[str] = []
    architecture_index = next(
        (doc.markdown for doc in documents if doc.relative == PurePosixPath("architecture/README.md")),
        None,
    )
    layer_readme = next(
        (
            doc.markdown
            for doc in documents
            if doc.relative == PurePosixPath("architecture") / layer.key / "README.md"
        ),
        None,
    )
    if layer_readme:
        status_match = re.search(
            r"(?im)^\s*(?:[-*]\s*)?(?:\*\*)?status(?:\*\*)?\s*:\s*(.+?)\s*$",
            layer_readme,
        )
        if status_match:
            return _strip_table_markup(status_match.group(1))
    if architecture_index:
        sources.append(architecture_index)
    if layer_readme:
        sources.append(layer_readme)

    status_words = re.compile(
        r"out(?:side| of) scope|not in scope|not applicable|extern(?:al|ally)|owned (?:by|elsewhere)|"
        r"parent (?:model|repository)|another repo|unavailable|not documented|not started|missing|gap|blocked|"
        r"in progress|draft|documented|available|complete|current|validated|in scope",
        re.IGNORECASE,
    )
    for source in sources:
        for line in source.splitlines():
            if "|" not in line:
                continue
            cells = [_strip_table_markup(cell) for cell in line.strip().strip("|").split("|")]
            identity = layer.name.casefold()
            identity_cells = {
                identity,
                f"{identity} layer",
                layer.key.casefold(),
                f"{layer.key.casefold()}/",
            }
            if not any(cell.casefold() in identity_cells for cell in cells):
                continue
            for cell_index, cell in enumerate(cells):
                if status_words.search(cell):
                    details = [value for value in cells[cell_index:] if value]
                    return " · ".join(details)
    return None


def _status_kind(value: str) -> tuple[str, str]:
    folded = value.casefold()
    if "unavailable" in folded:
        return "Unavailable", "external"
    if re.search(r"extern(?:al|ally)|owned (?:by|elsewhere)|parent (?:model|repository)|another repo", folded):
        return "Externally owned", "external"
    if re.search(r"out(?:side| of) scope|not in scope|not applicable|\bn/a\b", folded):
        return "Out of scope", "out-of-scope"
    if "blocked" in folded:
        return "Blocked", "missing"
    if re.search(r"not documented|not started|missing|\bgap\b", folded):
        return "Not documented", "missing"
    if re.search(r"in progress|\bdraft\b|pending", folded):
        return "In progress", "in-progress"
    return "Documented", "documented"


def layer_states(documents: Sequence[Document]) -> list[LayerState]:
    states: list[LayerState] = []
    for layer in LAYERS:
        layer_documents = [doc for doc in documents if doc.layer_key == layer.key]
        explicit = _explicit_layer_status(layer, documents)
        if explicit:
            label, kind = _status_kind(explicit)
            detail = explicit
        elif layer_documents:
            label, kind = "Documented", "documented"
            detail = f"{len(layer_documents)} document{'s' if len(layer_documents) != 1 else ''}"
        else:
            label, kind = "Not documented", "missing"
            detail = "No status or content is recorded in this model."
        readme = next(
            (
                doc
                for doc in layer_documents
                if doc.relative.name.casefold() == "readme.md"
            ),
            None,
        )
        href = (readme or (layer_documents[0] if layer_documents else None))
        states.append(
            LayerState(
                layer=layer,
                label=label,
                kind=kind,
                detail=detail,
                href=href.output if href else None,
                document_count=len(layer_documents),
            )
        )
    return states


def _slug(value: str) -> str:
    value = _plain_inline(value).casefold()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "section"


def _split_link_target(value: str) -> tuple[str, str]:
    value = value.strip()
    if value.startswith("<") and ">" in value:
        return value[1 : value.index(">")], ""
    match = re.match(r"(\S+)(?:\s+[\"'](.*)[\"'])?$", value)
    if not match:
        return value, ""
    return match.group(1), match.group(2) or ""


class MarkdownRenderer:
    """Small, safe renderer for the Markdown constructs used by the model."""

    def __init__(self, rewrite_link: Callable[[str], str]):
        self.rewrite_link = rewrite_link
        self._heading_counts: dict[str, int] = {}

    def inline(self, value: str) -> str:
        tokens: list[str] = []

        def token(content: str) -> str:
            tokens.append(content)
            return f"\x00{len(tokens) - 1}\x00"

        def code_replace(match: re.Match[str]) -> str:
            return token(f"<code>{html.escape(match.group(1))}</code>")

        value = re.sub(r"`([^`]+)`", code_replace, value)

        def image_replace(match: re.Match[str]) -> str:
            target, title = _split_link_target(match.group(2))
            href = html.escape(self.rewrite_link(target), quote=True)
            title_attr = f' title="{html.escape(title, quote=True)}"' if title else ""
            return token(
                f'<img src="{href}" alt="{html.escape(match.group(1), quote=True)}" loading="lazy"{title_attr}>'
            )

        value = re.sub(r"!\[([^]]*)\]\(([^)]+)\)", image_replace, value)

        def link_replace(match: re.Match[str]) -> str:
            target, title = _split_link_target(match.group(2))
            href = html.escape(self.rewrite_link(target), quote=True)
            title_attr = f' title="{html.escape(title, quote=True)}"' if title else ""
            return token(f'<a href="{href}"{title_attr}>{html.escape(match.group(1))}</a>')

        value = re.sub(r"\[([^]]+)\]\(([^)]+)\)", link_replace, value)

        def autolink_replace(match: re.Match[str]) -> str:
            href = html.escape(match.group(1), quote=True)
            return token(f'<a href="{href}">{html.escape(match.group(1))}</a>')

        value = re.sub(r"<(https?://[^>]+)>", autolink_replace, value)
        value = html.escape(value)
        value = re.sub(r"\*\*(.+?)\*\*|__(.+?)__", lambda m: f"<strong>{m.group(1) or m.group(2)}</strong>", value)
        value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)|(?<!_)_([^_]+)_(?!_)", lambda m: f"<em>{m.group(1) or m.group(2)}</em>", value)
        value = re.sub(r"~~(.+?)~~", r"<del>\1</del>", value)
        for index, content in enumerate(tokens):
            value = value.replace(f"\x00{index}\x00", content)
        return value

    @staticmethod
    def _is_table_separator(line: str) -> bool:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)

    @staticmethod
    def _is_block_start(lines: Sequence[str], index: int) -> bool:
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            return True
        if re.match(r"^#{1,6}\s+", line) or re.match(r"^\s*```", line):
            return True
        if re.match(r"^\s*(?:[-+*]|\d+[.)])\s+", line) or re.match(r"^\s*>\s?", line):
            return True
        if re.fullmatch(r"\s*(?:-{3,}|\*{3,}|_{3,})\s*", line):
            return True
        return index + 1 < len(lines) and "|" in line and MarkdownRenderer._is_table_separator(lines[index + 1])

    def render(self, markdown: str) -> str:
        markdown = re.sub(r"<!--.*?-->", "", markdown, flags=re.DOTALL)
        lines = markdown.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        if lines and lines[0].strip() == "---":
            try:
                end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
                lines = lines[end + 1 :]
            except StopIteration:
                pass
        output: list[str] = []
        index = 0
        while index < len(lines):
            line = lines[index]
            if not line.strip():
                index += 1
                continue

            fence = re.match(r"^\s*```\s*([^\s`]*)?.*$", line)
            if fence:
                language = (fence.group(1) or "").casefold()
                index += 1
                code_lines: list[str] = []
                while index < len(lines) and not re.match(r"^\s*```", lines[index]):
                    code_lines.append(lines[index])
                    index += 1
                index += 1 if index < len(lines) else 0
                code = "\n".join(code_lines)
                if language == "mermaid":
                    output.append(
                        '<figure class="diagram"><pre class="mermaid">'
                        + html.escape(code)
                        + '</pre><figcaption>Diagram</figcaption></figure>'
                    )
                else:
                    class_attr = f' class="language-{html.escape(language, quote=True)}"' if language else ""
                    output.append(f"<pre><code{class_attr}>{html.escape(code)}</code></pre>")
                continue

            heading = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
            if heading:
                level = len(heading.group(1))
                base = _slug(heading.group(2))
                count = self._heading_counts.get(base, 0)
                self._heading_counts[base] = count + 1
                anchor = base if count == 0 else f"{base}-{count + 1}"
                output.append(f'<h{level} id="{anchor}">{self.inline(heading.group(2))}</h{level}>')
                index += 1
                continue

            if index + 1 < len(lines) and "|" in line and self._is_table_separator(lines[index + 1]):
                headers = [cell.strip() for cell in line.strip().strip("|").split("|")]
                index += 2
                rows: list[list[str]] = []
                while index < len(lines) and "|" in lines[index] and lines[index].strip():
                    rows.append([cell.strip() for cell in lines[index].strip().strip("|").split("|")])
                    index += 1
                output.append('<div class="table-wrap"><table><thead><tr>')
                output.extend(f"<th>{self.inline(cell)}</th>" for cell in headers)
                output.append("</tr></thead><tbody>")
                for row in rows:
                    output.append("<tr>")
                    output.extend(
                        f"<td>{self.inline(row[column]) if column < len(row) else ''}</td>"
                        for column in range(len(headers))
                    )
                    output.append("</tr>")
                output.append("</tbody></table></div>")
                continue

            list_match = re.match(r"^\s*([-+*]|\d+[.)])\s+(.+)$", line)
            if list_match:
                ordered = list_match.group(1)[0].isdigit()
                tag = "ol" if ordered else "ul"
                items: list[str] = []
                while index < len(lines):
                    item_match = re.match(r"^\s*([-+*]|\d+[.)])\s+(.+)$", lines[index])
                    if not item_match or item_match.group(1)[0].isdigit() != ordered:
                        break
                    item = item_match.group(2)
                    checkbox = re.match(r"^\[([ xX])\]\s*(.*)$", item)
                    if checkbox:
                        checked = " checked" if checkbox.group(1).casefold() == "x" else ""
                        item = f'<input type="checkbox" disabled{checked}> {self.inline(checkbox.group(2))}'
                    else:
                        item = self.inline(item)
                    items.append(f"<li>{item}</li>")
                    index += 1
                output.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
                continue

            if re.match(r"^\s*>\s?", line):
                quote_lines: list[str] = []
                while index < len(lines) and re.match(r"^\s*>\s?", lines[index]):
                    quote_lines.append(re.sub(r"^\s*>\s?", "", lines[index]))
                    index += 1
                output.append(f"<blockquote><p>{self.inline(' '.join(quote_lines))}</p></blockquote>")
                continue

            if re.fullmatch(r"\s*(?:-{3,}|\*{3,}|_{3,})\s*", line):
                output.append("<hr>")
                index += 1
                continue

            paragraph = [line.strip()]
            index += 1
            while index < len(lines) and not self._is_block_start(lines, index):
                paragraph.append(lines[index].strip())
                index += 1
            output.append(f"<p>{self.inline(' '.join(paragraph))}</p>")
        return "\n".join(output)


def _relative_url(from_page: PurePosixPath, to_page: PurePosixPath) -> str:
    return posixpath.relpath(to_page.as_posix(), start=from_page.parent.as_posix() or ".")


def _root_prefix(page: PurePosixPath) -> str:
    return posixpath.relpath(".", start=page.parent.as_posix() or ".").rstrip("/") + "/"


def _source_href(
    document: Document,
    current_page: PurePosixPath,
    output_root: Path,
    location: SourceLocation,
) -> str:
    try:
        repository_relative = document.source.relative_to(location.repository_root).as_posix()
    except ValueError:
        repository_relative = document.relative.as_posix()
    if location.web_base:
        return f"{location.web_base}/{quote(repository_relative, safe='/')}"
    current_folder = output_root / Path(current_page.parent.as_posix())
    return Path(os.path.relpath(document.source, start=current_folder)).as_posix()


def _link_rewriter(
    document: Document,
    mapping: dict[PurePosixPath, Document],
    project: Path,
    output_root: Path,
) -> Callable[[str], str]:
    def rewrite(target: str) -> str:
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or target.startswith(("mailto:", "tel:", "#")):
            return target
        source_target = unquote(parsed.path)
        if not source_target:
            return target
        if source_target.startswith("/"):
            return target
        resolved = (document.source.parent / source_target).resolve()
        try:
            relative = PurePosixPath(resolved.relative_to(project).as_posix())
        except ValueError:
            return target
        mapped = mapping.get(relative)
        if mapped:
            path = _relative_url(document.output, mapped.output)
        else:
            current_folder = output_root / Path(document.output.parent.as_posix())
            path = Path(os.path.relpath(resolved, start=current_folder)).as_posix()
        return urlunsplit(("", "", quote(path, safe="/.:@+"), parsed.query, parsed.fragment))

    return rewrite


def _nav_html(
    page: PurePosixPath,
    title: str,
    documents: Sequence[Document],
    states: Sequence[LayerState],
) -> str:
    overview_href = _relative_url(page, PurePosixPath("index.html"))
    layer_items: list[str] = []
    for state in states:
        target = state.href or PurePosixPath(f"index.html#layer-{state.layer.key}")
        href = _relative_url(page, target) if state.href else overview_href + f"#layer-{state.layer.key}"
        layer_items.append(
            f'<li><a href="{html.escape(href, quote=True)}">'
            f'<span>{html.escape(state.layer.name)}</span>'
            f'<span class="nav-status status-{state.kind}" title="{html.escape(state.label, quote=True)}"></span>'
            "</a></li>"
        )
    other_architecture = [
        doc
        for doc in documents
        if doc.relative.parts[0] == "architecture" and doc.layer_key is None
    ]
    general = [doc for doc in documents if doc.relative.parts[0] != "architecture"]

    def document_list(items: Sequence[Document]) -> str:
        return "".join(
            f'<li><a href="{html.escape(_relative_url(page, doc.output), quote=True)}">{html.escape(doc.title)}</a></li>'
            for doc in items
        )

    sections = ""
    if other_architecture:
        sections += (
            '<details class="nav-group"><summary>Other architecture</summary><ul>'
            + document_list(other_architecture)
            + "</ul></details>"
        )
    if general:
        sections += (
            '<details class="nav-group"><summary>Project documents</summary><ul>'
            + document_list(general)
            + "</ul></details>"
        )
    return f"""
<aside class="sidebar" id="portal-navigation">
  <div class="brand"><a href="{html.escape(overview_href, quote=True)}">{html.escape(title)}</a><small>Architecture portal</small></div>
  <nav aria-label="Architecture">
    <a class="overview-link" href="{html.escape(overview_href, quote=True)}">Overview</a>
    <h2>Layers</h2>
    <ol class="layer-nav">{''.join(layer_items)}</ol>
    {sections}
  </nav>
</aside>"""


def _shell(
    *,
    page: PurePosixPath,
    portal_title: str,
    page_title: str,
    body: str,
    nav: str,
    generated: str,
    revision: str | None,
    source_href: str | None = None,
) -> str:
    prefix = _root_prefix(page)
    source = (
        f'<a class="source-link" href="{html.escape(source_href, quote=True)}">View canonical source</a>'
        if source_href
        else ""
    )
    revision_text = f" · revision {html.escape(revision)}" if revision else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <title>{html.escape(page_title)} · {html.escape(portal_title)}</title>
  <link rel="stylesheet" href="{html.escape(prefix, quote=True)}assets/portal.css">
</head>
<body data-portal-root="{html.escape(prefix, quote=True)}">
  <a class="skip-link" href="#main-content">Skip to content</a>
  {nav}
  <div class="page">
    <header class="topbar">
      <button class="nav-toggle" type="button" aria-controls="portal-navigation" aria-expanded="false">Menu</button>
      <div class="search"><label for="portal-search">Search the architecture</label><input id="portal-search" type="search" autocomplete="off" placeholder="Search names, decisions, services…"><div id="search-results" class="search-results" hidden></div></div>
      {source}
    </header>
    <main id="main-content" class="content">{body}</main>
    <footer>Generated {html.escape(generated)}{revision_text}. Canonical facts remain in the linked Markdown sources.</footer>
  </div>
  <script src="{html.escape(prefix, quote=True)}assets/portal.js"></script>
  <script type="module">
    const diagrams = document.querySelectorAll('.mermaid');
    if (diagrams.length) {{
      try {{
        const {{ default: mermaid }} = await import('https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs');
        mermaid.initialize({{ startOnLoad: false, securityLevel: 'strict', theme: 'neutral' }});
        await mermaid.run({{ nodes: [...diagrams] }});
      }} catch (error) {{
        document.documentElement.classList.add('mermaid-unavailable');
        console.info('Mermaid diagrams remain available as source because rendering is unavailable.', error);
      }}
    }}
  </script>
</body>
</html>
"""


def _index_body(portal_title: str, states: Sequence[LayerState], documents: Sequence[Document]) -> str:
    cards: list[str] = []
    for state in states:
        href = state.href.as_posix() if state.href else f"#layer-{state.layer.key}"
        cards.append(
            f'<article class="layer-card status-border-{state.kind}" id="layer-{state.layer.key}">'
            f'<div class="card-heading"><span class="layer-number">{html.escape(state.layer.key.split("_", 1)[0])}</span>'
            f'<h2><a href="{html.escape(href, quote=True)}">{html.escape(state.layer.name)}</a></h2></div>'
            f'<span class="status-pill status-{state.kind}">{html.escape(state.label)}</span>'
            f'<p>{html.escape(state.layer.question)}</p>'
            f'<p class="status-detail">{html.escape(state.detail)}</p>'
            "</article>"
        )
    other_docs = [doc for doc in documents if doc.layer_key is None]
    links = "".join(
        f'<li><a href="{html.escape(doc.output.as_posix(), quote=True)}"><strong>{html.escape(doc.title)}</strong><span>{html.escape(doc.summary)}</span></a></li>'
        for doc in other_docs
    )
    other_section = (
        f'<section><h2>Other project documents</h2><ul class="document-list">{links}</ul></section>'
        if links
        else ""
    )
    architecture_index = next(
        (doc for doc in documents if doc.relative == PurePosixPath("architecture/README.md")),
        None,
    )
    introduction = (
        architecture_index.summary
        if architecture_index
        else "Browse the current model directly from its canonical project documentation."
    )
    model_overview = (
        f'<a class="hero-link" href="{html.escape(architecture_index.output.as_posix(), quote=True)}">Read the model overview</a>'
        if architecture_index
        else ""
    )
    return f"""
<section class="hero">
  <p class="eyebrow">Architecture portal</p>
  <h1>{html.escape(portal_title)}</h1>
  <p>{html.escape(introduction)}</p>
  <p>Layer status distinguishes documented content, known gaps, work outside this model, and architecture owned elsewhere.</p>
  {model_overview}
</section>
<section aria-labelledby="layers-heading">
  <h2 id="layers-heading">Architecture layers</h2>
  <div class="layer-grid">{''.join(cards)}</div>
</section>
{other_section}
"""


PORTAL_CSS = r"""
:root {
  --bg: #f6f7f9;
  --surface: #ffffff;
  --surface-2: #eef1f5;
  --text: #17202a;
  --muted: #586474;
  --line: #d8dee7;
  --accent: #2859a6;
  --accent-soft: #e8f0ff;
  --documented: #1f7a4d;
  --progress: #9a6700;
  --missing: #a33a3a;
  --external: #6453a6;
  --out: #687386;
  --sidebar: 18rem;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color-scheme: light;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; background: var(--bg); color: var(--text); line-height: 1.62; }
a { color: var(--accent); text-underline-offset: .18em; }
a:hover { text-decoration-thickness: .14em; }
.skip-link { position: fixed; left: 1rem; top: -5rem; z-index: 20; padding: .65rem 1rem; background: var(--surface); border: 2px solid var(--accent); }
.skip-link:focus { top: 1rem; }
.sidebar { position: fixed; inset: 0 auto 0 0; width: var(--sidebar); overflow-y: auto; padding: 1.4rem 1rem; background: #17243a; color: #fff; z-index: 10; }
.brand { padding: 0 .5rem 1.2rem; border-bottom: 1px solid #ffffff2b; }
.brand a { display: block; color: #fff; font-size: 1.12rem; font-weight: 750; text-decoration: none; }
.brand small { color: #c8d2e2; }
.sidebar nav { padding-top: 1rem; }
.sidebar h2 { margin: 1.1rem .5rem .4rem; color: #9eabc0; font-size: .75rem; letter-spacing: .09em; text-transform: uppercase; }
.overview-link, .layer-nav a, .nav-group a { color: #eaf0f8; text-decoration: none; }
.overview-link { display: block; padding: .55rem .5rem; font-weight: 650; }
.layer-nav, .nav-group ul { margin: 0; padding: 0; list-style: none; }
.layer-nav a, .nav-group a { display: flex; justify-content: space-between; gap: .5rem; padding: .45rem .5rem; border-radius: .35rem; }
.layer-nav a:hover, .nav-group a:hover, .overview-link:hover { background: #ffffff18; }
.nav-status { flex: 0 0 auto; width: .62rem; height: .62rem; margin-top: .42rem; border-radius: 50%; background: currentColor; }
.nav-group { margin-top: .75rem; }
.nav-group summary { cursor: pointer; padding: .45rem .5rem; color: #c8d2e2; font-size: .86rem; font-weight: 650; }
.nav-group a { font-size: .88rem; }
.page { min-height: 100vh; margin-left: var(--sidebar); }
.topbar { position: sticky; top: 0; z-index: 8; display: flex; align-items: end; gap: 1rem; padding: .85rem clamp(1rem, 3vw, 3rem); background: color-mix(in srgb, var(--surface) 94%, transparent); border-bottom: 1px solid var(--line); backdrop-filter: blur(8px); }
.search { position: relative; flex: 1 1 28rem; max-width: 44rem; }
.search label { display: block; margin-bottom: .2rem; color: var(--muted); font-size: .75rem; font-weight: 650; }
.search input { width: 100%; padding: .66rem .8rem; border: 1px solid #aeb8c6; border-radius: .45rem; background: var(--surface); color: var(--text); font: inherit; }
.search input:focus { outline: 3px solid #8eb4ee80; border-color: var(--accent); }
.search-results { position: absolute; top: calc(100% + .3rem); width: 100%; max-height: min(30rem, 70vh); overflow-y: auto; padding: .4rem; background: var(--surface); border: 1px solid var(--line); border-radius: .45rem; box-shadow: 0 .8rem 2rem #1622382b; }
.search-results a { display: block; padding: .55rem .65rem; color: var(--text); text-decoration: none; border-radius: .3rem; }
.search-results a:hover, .search-results a:focus { background: var(--accent-soft); }
.search-results strong, .search-results span { display: block; }
.search-results span { color: var(--muted); font-size: .82rem; }
.source-link { flex: 0 0 auto; padding: .55rem .75rem; font-size: .86rem; font-weight: 650; }
.nav-toggle { display: none; }
.content { width: min(100%, 78rem); min-height: 70vh; padding: clamp(2rem, 5vw, 4.5rem) clamp(1rem, 5vw, 5rem); }
.content > :first-child { margin-top: 0; }
.content h1 { max-width: 26ch; font-size: clamp(2.1rem, 5vw, 3.8rem); line-height: 1.08; letter-spacing: -.035em; }
.content h2 { margin-top: 2.4rem; line-height: 1.2; }
.content h3 { margin-top: 1.8rem; }
.content p, .content li { max-width: 78ch; }
.content pre { max-width: 100%; overflow-x: auto; padding: 1rem; background: #17243a; color: #f2f5f9; border-radius: .5rem; }
.content code { padding: .08em .28em; background: var(--surface-2); border-radius: .22em; font-size: .9em; }
.content pre code { padding: 0; background: transparent; }
.content blockquote { margin-left: 0; padding: .3rem 1rem; color: var(--muted); border-left: .25rem solid var(--accent); }
.content img { max-width: 100%; height: auto; }
.table-wrap { max-width: 100%; overflow-x: auto; margin: 1.2rem 0; border: 1px solid var(--line); border-radius: .45rem; }
table { width: 100%; border-collapse: collapse; background: var(--surface); font-size: .92rem; }
th, td { padding: .66rem .75rem; text-align: left; vertical-align: top; border-bottom: 1px solid var(--line); }
th { background: var(--surface-2); }
tr:last-child td { border-bottom: 0; }
.hero { margin-bottom: 3rem; padding: clamp(1.5rem, 4vw, 3rem); background: linear-gradient(135deg, #e7efff, #f6f8ff 55%, #ede9ff); border: 1px solid #ccdaf4; border-radius: .8rem; }
.hero h1 { margin: .25rem 0 1rem; }
.hero p:last-child { margin-bottom: 0; max-width: 64ch; font-size: 1.08rem; }
.hero-link { display: inline-block; margin-top: .25rem; font-weight: 700; }
.eyebrow { margin: 0; color: var(--accent); font-size: .78rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
.layer-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 19rem), 1fr)); gap: 1rem; }
.layer-card { padding: 1.2rem; background: var(--surface); border: 1px solid var(--line); border-top: .3rem solid var(--out); border-radius: .55rem; }
.layer-card h2 { margin: 0; font-size: 1.12rem; }
.layer-card p { margin: .7rem 0 0; font-size: .92rem; }
.card-heading { display: flex; align-items: center; gap: .65rem; }
.layer-number { display: grid; place-items: center; width: 1.8rem; height: 1.8rem; background: var(--surface-2); border-radius: 50%; font-size: .78rem; font-weight: 800; }
.status-pill { display: inline-block; margin-top: .75rem; padding: .2rem .55rem; border-radius: 999px; background: color-mix(in srgb, currentColor 12%, transparent); font-size: .74rem; font-weight: 750; }
.status-detail { color: var(--muted); }
.status-documented { color: var(--documented); }
.status-in-progress { color: var(--progress); }
.status-missing { color: var(--missing); }
.status-external { color: var(--external); }
.status-out-of-scope { color: var(--out); }
.status-border-documented { border-top-color: var(--documented); }
.status-border-in-progress { border-top-color: var(--progress); }
.status-border-missing { border-top-color: var(--missing); }
.status-border-external { border-top-color: var(--external); }
.status-border-out-of-scope { border-top-color: var(--out); }
.document-list { padding: 0; list-style: none; }
.document-list a { display: grid; gap: .15rem; margin-bottom: .6rem; padding: .85rem 1rem; background: var(--surface); border: 1px solid var(--line); border-radius: .45rem; text-decoration: none; }
.document-list span { color: var(--muted); font-size: .9rem; }
.diagram { margin: 1.5rem 0; padding: 1rem; overflow-x: auto; background: var(--surface); border: 1px solid var(--line); border-radius: .55rem; }
.diagram figcaption { margin-top: .5rem; color: var(--muted); font-size: .78rem; }
.mermaid-unavailable .diagram::after { content: "Diagram rendering is unavailable; the Mermaid source is shown instead."; display: block; color: var(--muted); font-size: .82rem; }
footer { padding: 1.4rem clamp(1rem, 5vw, 5rem) 2.5rem; color: var(--muted); border-top: 1px solid var(--line); font-size: .8rem; }
@media (prefers-color-scheme: dark) {
  :root { --bg: #101722; --surface: #172130; --surface-2: #202c3d; --text: #edf2f8; --muted: #aeb9c7; --line: #334155; --accent: #8eb7ff; --accent-soft: #243c64; color-scheme: dark; }
  .hero { background: linear-gradient(135deg, #182c4d, #1b2637 55%, #282342); border-color: #334b70; }
  .content pre { background: #0b111b; }
  .search input { border-color: #5d6b7d; }
}
@media (max-width: 820px) {
  .sidebar { transform: translateX(-100%); transition: transform .2s ease; box-shadow: .8rem 0 2rem #0005; }
  body.nav-open .sidebar { transform: translateX(0); }
  .page { margin-left: 0; }
  .nav-toggle { display: inline-flex; padding: .55rem .7rem; background: var(--surface); color: var(--text); border: 1px solid var(--line); border-radius: .4rem; }
  .source-link { display: none; }
}
"""


PORTAL_JS_TEMPLATE = r"""
(() => {
  const INDEX = __SEARCH_INDEX__;
  const body = document.body;
  const root = body.dataset.portalRoot || './';
  const input = document.getElementById('portal-search');
  const results = document.getElementById('search-results');
  const toggle = document.querySelector('.nav-toggle');

  const escapeHtml = (value) => value.replace(/[&<>\"']/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '\"': '&quot;', "'": '&#39;'
  })[character]);

  const hideResults = () => {
    results.hidden = true;
    results.innerHTML = '';
  };

  input?.addEventListener('input', () => {
    const terms = input.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    if (!terms.length) {
      hideResults();
      return;
    }
    const matches = INDEX.map((entry) => {
      const title = entry.title.toLocaleLowerCase();
      const path = entry.path.toLocaleLowerCase();
      const text = entry.text.toLocaleLowerCase();
      if (!terms.every((term) => title.includes(term) || path.includes(term) || text.includes(term))) return null;
      const score = terms.reduce((total, term) => total + (title.includes(term) ? 8 : 0) + (path.includes(term) ? 3 : 0) + (text.includes(term) ? 1 : 0), 0);
      return { entry, score };
    }).filter(Boolean).sort((left, right) => right.score - left.score || left.entry.title.localeCompare(right.entry.title)).slice(0, 20);
    results.innerHTML = matches.length
      ? matches.map(({ entry }) => `<a href="${root}${entry.url}"><strong>${escapeHtml(entry.title)}</strong><span>${escapeHtml(entry.summary)}</span></a>`).join('')
      : '<span class="no-results">No matching architecture documents.</span>';
    results.hidden = false;
  });

  input?.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      input.value = '';
      hideResults();
    }
  });

  document.addEventListener('click', (event) => {
    if (!event.target.closest('.search')) hideResults();
  });

  toggle?.addEventListener('click', () => {
    const open = body.classList.toggle('nav-open');
    toggle.setAttribute('aria-expanded', String(open));
  });
})();
"""


def _portal_title(documents: Sequence[Document], project: Path) -> str:
    architecture_index = next(
        (doc for doc in documents if doc.relative == PurePosixPath("architecture/README.md")),
        None,
    )
    root_readme = next((doc for doc in documents if doc.relative == PurePosixPath("README.md")), None)
    return (architecture_index or root_readme).title if (architecture_index or root_readme) else project.name


def _write_site(
    build_root: Path,
    final_root: Path,
    project: Path,
    documents: Sequence[Document],
    location: SourceLocation,
) -> None:
    build_root.mkdir(parents=True, exist_ok=True)
    assets = build_root / "assets"
    assets.mkdir()
    generated = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    title = _portal_title(documents, project)
    states = layer_states(documents)
    mapping = {doc.relative: doc for doc in documents}

    search_index = [
        {
            "title": doc.title,
            "path": doc.relative.as_posix(),
            "summary": doc.summary,
            "text": doc.search_text,
            "url": doc.output.as_posix(),
        }
        for doc in documents
    ]
    serialised_index = json.dumps(search_index, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    (assets / "portal.css").write_text(PORTAL_CSS.strip() + "\n", encoding="utf-8")
    (assets / "portal.js").write_text(
        PORTAL_JS_TEMPLATE.replace("__SEARCH_INDEX__", serialised_index).strip() + "\n",
        encoding="utf-8",
    )

    index_page = PurePosixPath("index.html")
    index_nav = _nav_html(index_page, title, documents, states)
    (build_root / "index.html").write_text(
        _shell(
            page=index_page,
            portal_title=title,
            page_title="Overview",
            body=_index_body(title, states, documents),
            nav=index_nav,
            generated=generated,
            revision=location.revision,
        ),
        encoding="utf-8",
    )

    for document in documents:
        target = build_root / Path(document.output.as_posix())
        target.parent.mkdir(parents=True, exist_ok=True)
        renderer = MarkdownRenderer(_link_rewriter(document, mapping, project, final_root))
        body = renderer.render(document.markdown)
        nav = _nav_html(document.output, title, documents, states)
        source_href = _source_href(document, document.output, final_root, location)
        target.write_text(
            _shell(
                page=document.output,
                portal_title=title,
                page_title=document.title,
                body=body,
                nav=nav,
                generated=generated,
                revision=location.revision,
                source_href=source_href,
            ),
            encoding="utf-8",
        )

    (build_root / PORTAL_MARKER).write_text(
        f"ArChreator generated portal\nformat={PORTAL_VERSION}\n",
        encoding="utf-8",
    )


def _install_build(build_root: Path, target: Path) -> None:
    if target.exists() and not (target / PORTAL_MARKER).is_file():
        raise PortalError(
            f"Refusing to replace {target}: it does not contain the ArChreator portal marker."
        )
    backup = target.with_name(f".{target.name}-previous")
    if backup.exists():
        if not (backup / PORTAL_MARKER).is_file():
            raise PortalError(f"Refusing to remove unrecognised backup directory: {backup}")
        shutil.rmtree(backup)
    try:
        if target.exists():
            target.rename(backup)
        build_root.rename(target)
    except Exception:
        if not target.exists() and backup.exists():
            backup.rename(target)
        raise
    if backup.exists():
        shutil.rmtree(backup)


def build_portal(project: Path, source_base_url: str | None = None) -> Path:
    """Build and return ``<project>/.archreator/work/portal/index.html``."""
    project = project.expanduser().resolve()
    if not project.is_dir():
        raise PortalError(f"Project directory does not exist: {project}")
    documents = discover_documents(project)
    if not documents:
        raise PortalError(
            "No canonical Markdown found. Add README.md or Markdown under architecture/ or docs/."
        )
    work_root = project / ".archreator" / "work"
    work_root.mkdir(parents=True, exist_ok=True)
    ignore_file = work_root / ".gitignore"
    if not ignore_file.exists():
        ignore_file.write_text("*\n!.gitignore\n", encoding="utf-8")
    target = work_root / "portal"
    build_root = Path(tempfile.mkdtemp(prefix=".portal-build-", dir=work_root))
    try:
        _write_site(
            build_root,
            target,
            project,
            documents,
            source_location(project, source_base_url),
        )
        _install_build(build_root, target)
    finally:
        if build_root.exists():
            shutil.rmtree(build_root)
    return target / "index.html"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a searchable static portal from canonical ArChreator Markdown.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
            Output is always written to <project>/.archreator/work/portal/.
            The directory is disposable and should not be committed.
            """
        ),
    )
    parser.add_argument("project", nargs="?", type=Path, default=Path.cwd(), help="project root (default: current directory)")
    parser.add_argument(
        "--source-base-url",
        help="web URL containing the project sources; Git remotes are detected when omitted",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        index = build_portal(args.project, args.source_base_url)
    except PortalError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"Portal built: {index}")
    print(f"Open: {index.as_uri()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
