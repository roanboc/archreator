#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "markdown>=3.6",
#     "pyyaml>=6.0",
#     "playwright>=1.42",  # page.pdf(outline=...) needs 1.42+
# ]
# ///
"""Write one .pdf from an explicit, ordered list of model documents.

A reader who will read prose in a tool everyone already has gets one document
built from a named audience config:

    export_pdf.py --project . --config architecture/export/board.yml

An audience config is a small YAML file naming exactly what feeds the
document, in the order it should read:

    title: BigView — Board pack
    files:
      - architecture/README.md
      - architecture/1_estrategia/README.md
      - architecture/1_estrategia/*.md
      - architecture/2_negocio/*.md
    exclude:
      - architecture/2_negocio/actividades/*

**Nothing is included by default.** `files` is an explicit allow-list a human
wrote down, not a whole-model export with excludes — a glob expands in place,
sorted, but entries never reorder across each other, which is what lets a
project put a section out of its folder's own order without renaming files.
A path or glob that matches nothing is an error: an audience config that used
to work and now points at a renamed file fails loudly rather than shipping a
quiet hole.

**Markdown goes through a real renderer, not a hand-written one.** A first
version of this tool wrote its own Markdown subset converter for `.docx`, and
it never learned `[text](url)` link syntax — a gap invisible until a document
full of un-rendered bracket-paren text made the whole thing look nothing like
its source. This version converts with the `markdown` library and prints the
result with a real browser layout engine, so link handling, tables and
nesting are exactly as reliable as they are anywhere else Markdown is read.

**Every diagram is resolved to a picture or a labeled source block, never a
gap.** `mermaid.js` is fetched once via `npm pack` (registry.npmjs.org, not a
CDN — see § Why npm and not a CDN below) and inlined into the page; each
diagram is rendered individually in the browser, and one that fails to parse
is replaced with its own labeled fallback rather than left blank or sinking
the rest of the document. No `npm` on `PATH`, or the fetch fails — every
diagram becomes a labeled source block instead, and the export still
completes.

**The document is disposable**, same as every other generated artifact: it
lands under gitignored `.archreator/work/exports/`, stamped in its footer
with the project, the audience, when it was built and the model revision it
came from — see `docs/adopting.md` § An audience gets a PDF, built from an
explicit allow-list.

## Why npm and not a CDN

A generated page that loads `mermaid.js` from a CDN `<script src>` is the
simplest version of this, and was tried first. It depends on that CDN being
reachable from wherever this runs, which is not guaranteed — some
environments allow the npm registry but block generic CDN hosts by policy.
Fetching the package via `npm pack` and inlining its script instead removes
that dependency at render time: once vendored, the page is self-contained.
"""
import argparse
import html
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

# --------------------------------------------------------------------------
# This tool runs from the plugin and reads a project. The parse it needs -
# `model_graph.py` - lives in that project's `scripts/`, beside the two
# validators, because a project has to be able to check itself with no plugin
# installed and no network. Copied from `build_brief.py` rather than shared,
# exactly as `model.py` and `build_brief.py` already each carry their own copy.
# --------------------------------------------------------------------------
def _project_root(argv: list[str]) -> Path:
    for index, argument in enumerate(argv):
        if argument == "--project" and index + 1 < len(argv):
            return Path(argv[index + 1]).resolve()
        if argument.startswith("--project="):
            return Path(argument.split("=", 1)[1]).resolve()
    return Path.cwd().resolve()


def _find_parse(root: Path) -> Path | None:
    if not root.is_dir():
        return None
    for candidate in (root, *root.parents):
        parse = candidate / "scripts" / "model_graph.py"
        if parse.is_file():
            if candidate != root and not (root / "architecture").is_dir():
                return None
            return parse
        if (candidate / ".git").exists():
            return None
    return None


_ROOT = _project_root(sys.argv[1:])
_PARSE = _find_parse(_ROOT)
if _PARSE is None:
    if {"-h", "--help"} & set(sys.argv[1:]):
        print(__doc__)
        sys.exit(0)
    sys.exit(
        f"No archreator project at {_ROOT}: expected a directory holding "
        f"architecture/, with scripts/model_graph.py beside it or at the "
        f"enclosing repository root.\n"
        f"Run this from a project's root, or pass --project <path>."
    )
sys.path.insert(0, str(_PARSE.parent))

import model  # noqa: E402  (path is set up just above)

MERMAID_OPEN = re.compile(r"^```mermaid\s*$", re.MULTILINE)
MERMAID_FENCE = re.compile(r"^```mermaid[ \t]*\n(.*?)\n^```[ \t]*$", re.MULTILINE | re.DOTALL)
MERMAID_VERSION = "10.9.8"

PAGE_CSS = """
body { font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
       color: #1a1a1a; line-height: 1.5; font-size: 11pt; }
h1, h2, h3, h4, h5, h6 { margin-top: 1.4em; margin-bottom: 0.4em; }
h1 { font-size: 22pt; border-bottom: 2px solid #ddd; padding-bottom: 4px; }
h2 { font-size: 16pt; }
h3 { font-size: 13pt; }
table { border-collapse: collapse; width: 100%; margin: 0.8em 0; font-size: 10pt; }
th, td { border: 1px solid #ccc; padding: 4px 8px; text-align: left; vertical-align: top; }
th { background: #f2f2f2; }
code { background: #f2f2f2; padding: 1px 4px; border-radius: 3px;
       font-family: Consolas, monospace; font-size: 0.9em; }
pre { background: #f7f7f7; padding: 8px; border-radius: 4px; overflow-x: auto;
      font-family: Consolas, monospace; font-size: 9pt; white-space: pre-wrap; }
pre.mermaid, .mermaid-fallback, .mermaid-rendered { text-align: center; margin: 1em 0; }
.mermaid-fallback pre { text-align: left; }
.mermaid-rendered svg, img { max-width: 100%; height: auto; }
.source-caption { color: #888; font-style: italic; font-size: 9pt; margin-top: 2em;
                   border-top: 1px dashed #ccc; padding-top: 8px; }
.source-file:first-child .source-caption { border-top: none; margin-top: 0; }
blockquote { border-left: 3px solid #ccc; margin: 0.8em 0; padding-left: 1em; color: #555; }
a { color: #1155cc; }
"""


def _is_glob(pattern: str) -> bool:
    return any(ch in pattern for ch in "*?[")


def load_config(path: Path) -> dict:
    import yaml

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not data.get("files"):
        sys.exit(f"{path}: needs a non-empty 'files' list — the audience's "
                  f"explicit, ordered allow-list")
    data.setdefault("title", path.stem)
    data.setdefault("exclude", [])
    return data


def resolve_files(project: Path, config: dict, config_path: Path) -> list[Path]:
    """The ordered, deduplicated, excluded file list an audience declares.

    Order is `files`, top to bottom; a glob expands sorted in place but never
    reorders across entries — a project decides its own reading order rather
    than inheriting the filesystem's.
    """
    seen: set[Path] = set()
    ordered: list[Path] = []
    for entry in config["files"]:
        if _is_glob(entry):
            matches = sorted(p for p in project.glob(entry) if p.is_file())
            if not matches:
                sys.exit(f"{config_path}: '{entry}' matched no files under {project}")
        else:
            candidate = project / entry
            if not candidate.is_file():
                sys.exit(f"{config_path}: '{entry}' does not exist under {project}")
            matches = [candidate]
        for match in matches:
            if match not in seen:
                seen.add(match)
                ordered.append(match)

    excluded: set[Path] = set()
    for pattern in config["exclude"]:
        excluded.update(project.glob(pattern) if _is_glob(pattern) else [project / pattern])
    ordered = [f for f in ordered if f not in excluded]
    if not ordered:
        sys.exit(f"{config_path}: every matched file was excluded — nothing to export")
    return ordered


def count_mermaid(files: list[Path]) -> int:
    return sum(len(MERMAID_OPEN.findall(f.read_text(encoding="utf-8"))) for f in files)


def vendor_mermaid(version: str = MERMAID_VERSION) -> str | None:
    """`mermaid.min.js`'s source, fetched via npm, or None if that's not possible.

    Best-effort, never a hard requirement — see the module docstring's § Why
    npm and not a CDN. `None` means every diagram falls back to a labeled
    source block instead of live rendering.
    """
    if shutil.which("npm") is None:
        return None
    tmp = Path(tempfile.mkdtemp(prefix="archreator-mermaid-"))
    try:
        result = subprocess.run(
            ["npm", "pack", f"mermaid@{version}", "--silent"],
            cwd=tmp, capture_output=True, text=True, timeout=60, check=False,
        )
        if result.returncode != 0:
            return None
        tarballs = list(tmp.glob("mermaid-*.tgz"))
        if not tarballs:
            return None
        with tarfile.open(tarballs[0]) as tar:
            member = tar.extractfile("package/dist/mermaid.min.js")
            return member.read().decode("utf-8") if member else None
    except (OSError, subprocess.SubprocessError, KeyError, tarfile.TarError):
        return None
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def find_chromium() -> str | None:
    """A Chromium binary actually on disk under `PLAYWRIGHT_BROWSERS_PATH`.

    Generic, not hardcoded to one sandbox's exact revision: the installed
    `playwright` pip package can resolve to a browser revision that differs
    from what a pre-provisioned environment actually shipped, which makes
    `p.chromium.launch()` with no arguments fail outright. `None` lets
    Playwright's own default resolution try instead.

    Prefers `chromium_headless_shell-*` over the full `chromium-*` build: the
    full build ships a `chrome_sandbox` setuid helper that Chromium always
    tries to launch through when present, regardless of `--no-sandbox` — and
    in a container where that helper isn't actually setuid-root (common; the
    bit is often stripped by image builds), that is a hard launch failure
    with no flag that works around it. The headless-shell build carries no
    such helper at all, so there is nothing to fail to invoke.
    """
    browsers_path = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    if not browsers_path:
        return None
    for pattern in (
        "chromium_headless_shell-*/chrome-linux*/headless_shell",
        "chromium-*/chrome-linux*/chrome",
    ):
        matches = [
            p for p in Path(browsers_path).glob(pattern)
            if p.is_file() and os.access(p, os.X_OK)
        ]
        if matches:
            return str(sorted(matches)[-1])
    return None


def extract_diagrams(text: str) -> tuple[str, list[str]]:
    """Pull fenced ```mermaid``` blocks out before Markdown conversion.

    Left in place, the `markdown` library would treat them as ordinary fenced
    code and HTML-escape them for display rather than leaving them for the
    diagram pass. Each is replaced with a plain-text marker that survives
    paragraph-wrapping either way, and substituted back in `render_source`.
    """
    diagrams: list[str] = []

    def replace(match: re.Match) -> str:
        diagrams.append(match.group(1))
        return f"\x00MERMAID_{len(diagrams) - 1}\x00"

    return MERMAID_FENCE.sub(replace, text), diagrams


def heading_shift(project: Path, source: Path) -> int:
    """How many levels to push this file's headings down.

    A source file's own `# Title` always comes out `<h1>`, which is correct
    for exactly one file per document — every other file's `<h1>` landing at
    the same level is why the PDF's bookmark panel came out flat instead of
    matching the repository's own folder hierarchy (front door, then a layer,
    then that layer's documents). Depth is read from the path itself: a
    `README.md` sits at its folder's own depth (a layer's front door), and
    any other file in that folder is one level deeper (that layer's own
    documents) — so `2_negocio/actividades/*.md`, one folder deeper still,
    naturally nests under whichever `2_negocio/*.md` document precedes it in
    the audience config's declared order.
    """
    rel = source.relative_to(project)
    depth = len(rel.parent.parts) + (0 if source.name.lower() == "readme.md" else 1)
    return max(depth - 1, 0)


def shift_headings(html_fragment: str, shift: int) -> str:
    if shift <= 0:
        return html_fragment
    return re.sub(
        r"(</?h)([1-6])(?=[ >])",
        lambda m: f"{m.group(1)}{min(int(m.group(2)) + shift, 6)}",
        html_fragment,
    )


def render_source(project: Path, source: Path, live_diagrams: bool) -> tuple[str, int]:
    import markdown

    text = source.read_text(encoding="utf-8")
    stripped, diagrams = extract_diagrams(text)
    body = markdown.markdown(stripped, extensions=["tables", "fenced_code"])
    body = shift_headings(body, heading_shift(project, source))
    for index, diagram in enumerate(diagrams):
        marker = f"\x00MERMAID_{index}\x00"
        if live_diagrams:
            block = f'<pre class="mermaid">{html.escape(diagram)}</pre>'
        else:
            block = (
                '<div class="mermaid-fallback"><p><em>Diagram source (Mermaid) — '
                "render at https://mermaid.live or in a Markdown viewer:</em></p>"
                f"<pre>{html.escape(diagram)}</pre></div>"
            )
        body = body.replace(marker, block)
    rel = html.escape(str(source.relative_to(project)))
    return f'<div class="source-file"><p class="source-caption">{rel}</p>{body}</div>', len(diagrams)


# Renders every `.mermaid` block individually so one bad diagram's syntax
# error becomes its own labeled fallback instead of leaving a blank gap or
# aborting the whole document — see the module docstring's diagram guarantee.
MERMAID_RUNNER = """
(async () => {
  mermaid.initialize({startOnLoad: false});
  const nodes = document.querySelectorAll('pre.mermaid');
  for (const el of nodes) {
    const source = el.textContent;
    try {
      const id = 'm' + Math.random().toString(36).slice(2);
      const { svg } = await mermaid.render(id, source);
      el.outerHTML = '<div class="mermaid-rendered">' + svg + '</div>';
    } catch (err) {
      const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      el.outerHTML = '<div class="mermaid-fallback"><p><em>Diagram failed to render (' +
        esc(String(err && err.message || err)) + '):</em></p><pre>' + esc(source) + '</pre></div>';
    }
  }
  window.__archreatorMermaidDone = true;
})();
"""


def build_html(project: Path, config: dict, files: list[Path], mermaid_js: str | None) -> tuple[str, int]:
    sections = []
    diagrams_seen = 0
    for source in files:
        section, count = render_source(project, source, live_diagrams=mermaid_js is not None)
        sections.append(section)
        diagrams_seen += count

    scripts = ""
    if mermaid_js is not None:
        scripts = f"<script>{mermaid_js}</script><script>{MERMAID_RUNNER}</script>"

    html_doc = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>{html.escape(config["title"])}</title>
<style>{PAGE_CSS}</style>
</head><body>
<h1>{html.escape(config["title"])}</h1>
{"".join(sections)}
{scripts}
</body></html>"""
    return html_doc, diagrams_seen


def render_pdf(html_doc: str, out_path: Path, footer_text: str, wait_for_mermaid: bool) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        chromium_path = find_chromium()
        launch_kwargs = {"executable_path": chromium_path} if chromium_path else {}
        # A container's chrome_sandbox helper binary is frequently present but
        # not properly setuid-root, which makes Chromium's sandbox subsystem
        # fail outright even with --no-sandbox alone. --disable-setuid-sandbox
        # is the standard second flag for headless Chromium under Docker.
        browser = p.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"], **launch_kwargs)
        try:
            page = browser.new_page()
            page.set_content(html_doc, wait_until="load")
            if wait_for_mermaid:
                page.wait_for_function("window.__archreatorMermaidDone === true", timeout=60000)
            page.pdf(
                path=str(out_path),
                print_background=True,
                # Verified directly: `outline` alone writes no outline tree at
                # all on this Chromium build — it only takes effect together
                # with `tagged`. `tagged` also marks the PDF as accessible
                # (adds a structure tree for screen readers), a reasonable
                # bonus rather than a cost.
                outline=True,
                tagged=True,
                display_header_footer=True,
                header_template="<span></span>",
                footer_template=(
                    '<div style="font-size:8px; width:100%; text-align:center; color:#666;">'
                    f"{html.escape(footer_text)} · page "
                    '<span class="pageNumber"></span></div>'
                ),
                margin={"top": "1cm", "bottom": "1cm", "left": "1cm", "right": "1cm"},
            )
        finally:
            browser.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--project", default=".",
                        help="the project to read (default: the working directory)")
    parser.add_argument("--config", required=True, type=Path,
                        help="the audience config naming what feeds the document")
    parser.add_argument("--to", type=Path,
                        help="where to write the .pdf (default: .archreator/work/exports/)")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    config_path = args.config.resolve()
    if not config_path.is_file():
        sys.exit(f"No config at {config_path}")

    config = load_config(config_path)
    files = resolve_files(project, config, config_path)
    diagram_total = count_mermaid(files)

    mermaid_js = vendor_mermaid()
    html_doc, diagrams_seen = build_html(project, config, files, mermaid_js)
    assert diagrams_seen == diagram_total, (
        f"internal error: counted {diagram_total} diagram(s) but extracted "
        f"{diagrams_seen} — count_mermaid and extract_diagrams disagree"
    )

    when = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    rev = model.revision()
    footer_text = (
        f"{project.name} · {config['title']} · generated {when}"
        + (f" · revision {rev[:12]}" if rev else "")
    )

    out_dir = args.to or (project / ".archreator" / "work" / "exports")
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_path = out_dir / f"{config_path.stem}-{stamp}.pdf"

    render_pdf(html_doc, out_path, footer_text, wait_for_mermaid=mermaid_js is not None)

    print(
        f"PDF export written to {out_path} — {len(files)} file(s), "
        f"{diagram_total} diagram(s) "
        f"({'rendered live' if mermaid_js else 'kept as source, npm unavailable'})."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
