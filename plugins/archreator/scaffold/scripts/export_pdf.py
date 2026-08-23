#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     # MkDocs 2.0 replaces the plugin system and the theming this portal is
#     # built on, so the version is held until that has somewhere to go.
#     "mkdocs<2",
#     "mkdocs-material>=9.5",
#     "mkdocs-print-site-plugin>=2.5",
# ]
# ///
"""Export the whole model as one PDF, for a reader who wants a document.

A portal serves the reader who will follow a link. This one serves the reader
who will not: the executive who wants the architecture in a mail attachment,
the auditor who needs a dated copy, the workshop that happens away from a
screen. It is the same rendering as the portal — `mkdocs.yml` already builds
`print_page/`, one page carrying every document — printed rather than served.

**No new renderer.** The PDF is produced by a headless Chromium-family browser
printing that page, so it looks like the portal because it *is* the portal. A
second renderer (LaTeX, WeasyPrint, a Markdown-to-PDF converter) would be a
second set of rules about how the model looks, drifting from the first.

    python3 scripts/export_pdf.py                     # .docs/architecture.pdf
    python3 scripts/export_pdf.py --output plan.pdf   # somewhere else
    python3 scripts/export_pdf.py --no-build          # print what is already built
    python3 scripts/export_pdf.py --print-page        # print nothing, say where the page is

**Leaving documents out.** What the PDF carries is `print-site`'s `exclude`
list in `mkdocs.yml` — globs, relative to the project root, of documents that
stay in the portal but do not belong in a document handed to someone. A second
audience is a second config file inheriting the first and changing only that
list:

    # mkdocs-board.yml
    INHERIT: mkdocs.yml
    plugins:
      print-site:
        exclude:
          - architecture/scope/*

    python3 scripts/export_pdf.py --config mkdocs-board.yml

which builds into `.docs/site-board/`, writes `.docs/architecture-board.pdf`,
and leaves the portal and the default PDF where they were.

**Two things it needs.** A Chromium-family browser — Chromium, Chrome or Edge,
found on `PATH`, at the usual install location, named by `--browser`, or in
`CHROME_PATH` — and, while it renders, network access to the Mermaid library
the theme loads for diagrams. Without a browser it still builds the page and
tells you where it is: any browser's own Print → Save as PDF produces the same
document by hand.

**The diagrams are checked, because their failure is silent.** A browser that
cannot reach Mermaid prints every diagram as the source text that would have
drawn it — a document that looks finished and is not. So the page is loaded a
second time and the drawn diagrams are counted against the ones the model
wrote. Fewer means something stopped them, and the export says so instead of
handing over a PDF nobody looked at.

Like everything else under `.docs/`, the PDF is derived. It is a copy of the
model on the day it was exported, and the Markdown in git stays the model.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_docs import (  # noqa: E402
    CONFIG,
    DERIVED,
    SITE,
    STAGING,
    missing_dependencies,
    resolve_project,
    run_mkdocs,
    stage,
)

# The page `mkdocs.yml` has the print-site plugin build: every document, in
# navigation order, as one HTML page. Which of the two names it takes depends
# on `use_directory_urls`, so both are looked for.
PRINT_PAGES = ("print_page.html", "print_page/index.html")
# Chromium-family executables, by the names they take on each platform. Edge
# is included because it is the browser most likely to already be installed on
# a corporate Windows machine.
ON_PATH = (
    "chromium", "chromium-browser", "google-chrome", "google-chrome-stable",
    "chrome", "microsoft-edge", "microsoft-edge-stable", "msedge",
)
INSTALLED_AT = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
)
# A diagram, before and after the browser draws it. The theme replaces every
# `<pre class="mermaid">` it renders with a host element holding the drawing,
# so counting one against the other says whether the diagrams made it.
DIAGRAM_SOURCE = '<pre class="mermaid"'
DIAGRAM_DRAWN = '<div class="mermaid"'
# How long the browser is given before the render is called failed. Generous:
# it is loading the diagram library over the network on a page that may carry
# a hundred diagrams.
TIMEOUT_SECONDS = 300


def print_page_in(site: Path) -> Path | None:
    """The single page holding every document, whichever name it took."""
    for name in PRINT_PAGES:
        if (site / name).is_file():
            return site / name
    return None


def audience_of(config: str) -> str:
    """The name a config file gives its PDF: `mkdocs-board.yml` -> `board`.

    The default config has no audience — it is the whole model, for whoever
    asks. Anything else is a variant, and gets its own build and its own file
    so that exporting one never overwrites another.
    """
    if config == CONFIG:
        return ""
    stem = Path(config).stem
    return stem[len("mkdocs-"):] if stem.startswith("mkdocs-") else stem


def find_browser(named: str | None) -> str | None:
    for candidate in [named, os.environ.get("CHROME_PATH")]:
        if candidate:
            found = shutil.which(candidate) or (candidate if Path(candidate).is_file() else None)
            if found:
                return found
            print(f"{candidate}: not an executable this machine has.", file=sys.stderr)
            return None
    for name in ON_PATH:
        found = shutil.which(name)
        if found:
            return found
    for path in INSTALLED_AT:
        if Path(path).is_file():
            return path
    return None


def browser_run(browser: str, page: Path, extra: list[str]) -> subprocess.CompletedProcess | None:
    """Load `page` in a headless browser once, with the flags a render needs."""
    with tempfile.TemporaryDirectory(prefix="archreator-pdf-") as profile:
        command = [
            browser,
            "--headless",
            "--disable-gpu",
            "--hide-scrollbars",
            # Its own throwaway profile, so the export never collides with a
            # window the reader already has open.
            f"--user-data-dir={profile}",
            # Diagrams are drawn by a script after the page loads. This lets
            # the clock run on until they are done rather than capturing the
            # first frame.
            "--virtual-time-budget=30000",
            "--run-all-compositor-stages-before-draw",
            *extra,
            page.as_uri(),
        ]
        if os.name == "posix" and getattr(os, "geteuid", lambda: 1)() == 0:
            # Chromium refuses to run as root with its sandbox on, which is
            # the normal case in a container and in CI.
            command.insert(1, "--no-sandbox")
        try:
            return subprocess.run(command, capture_output=True, timeout=TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            print(f"{browser}: still rendering after {TIMEOUT_SECONDS}s — gave up.", file=sys.stderr)
            return None


def check_diagrams(browser: str, page: Path) -> str | None:
    """The complaint to make about this render, or None when it is sound."""
    expected = page.read_text(encoding="utf-8", errors="replace").count(DIAGRAM_SOURCE)
    if not expected:
        return None
    finished = browser_run(browser, page, ["--dump-dom"])
    if finished is None or finished.returncode != 0:
        return "The diagrams could not be checked — the browser did not load the page a second time."
    drawn = finished.stdout.decode("utf-8", "replace").count(DIAGRAM_DRAWN)
    if drawn >= expected:
        return None
    return (
        f"{expected - drawn} of {expected} diagram(s) printed as their source text "
        f"instead of being drawn. The theme fetches Mermaid from a CDN while the "
        f"page renders, so this is what a machine with no route to it produces. "
        f"The PDF is written either way — check it before sending it on."
    )


def render(browser: str, page: Path, output: Path) -> int:
    """Print `page` to `output`. Returns a process exit code."""
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    finished = browser_run(
        browser, page, ["--no-pdf-header-footer", f"--print-to-pdf={output}"]
    )
    if finished is None:
        return 1
    if finished.returncode != 0 or not output.is_file() or output.stat().st_size == 0:
        print(f"{browser}: printed nothing.", file=sys.stderr)
        for line in finished.stderr.decode("utf-8", "replace").splitlines()[-10:]:
            print(f"  {line}", file=sys.stderr)
        return finished.returncode or 1
    return 0


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):  # pragma: no cover - older or wrapped streams
            pass

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--project", type=Path, help="the project to export (default: the only one)")
    parser.add_argument("--config", default=CONFIG, help=f"the portal config to build from (default: {CONFIG})")
    parser.add_argument("--output", type=Path, help=f"where to write it (default: {DERIVED}/architecture.pdf)")
    parser.add_argument("--browser", help="the Chromium-family browser to print with")
    parser.add_argument("--no-build", action="store_true", help="print the portal as it was last built")
    parser.add_argument("--print-page", action="store_true", help="build the page to print, and stop")
    parser.add_argument("--no-check", action="store_true", help="skip the second pass that counts the drawn diagrams")
    args = parser.parse_args()

    project = resolve_project(args.project)
    if project is None:
        return 1
    if not (project / args.config).is_file():
        print(f"{project}: no {args.config} — nothing says how to publish this project.", file=sys.stderr)
        return 1

    # A config other than the default builds its own site and writes its own
    # file, so exporting for one audience never overwrites another's.
    audience = audience_of(args.config)
    site = project / (f"{SITE}-{audience}" if audience else SITE)

    if not args.no_build:
        missing = missing_dependencies()
        if missing:
            print(
                "The export needs " + ", ".join(missing) + ", which this interpreter does not have.\n"
                "  uv run scripts/export_pdf.py        # fetches them, installs nothing\n"
                "  pip install " + " ".join(missing) + "   # or install them once",
                file=sys.stderr,
            )
            return 1
        published, _, _ = stage(project, project / STAGING)
        print(f"{published} document(s) staged into {STAGING}/.")
        code = run_mkdocs(project, ["build", "--site-dir", str(site)], config=args.config)
        if code != 0:
            return code

    page = print_page_in(site)
    if page is None:
        where = site.relative_to(project) if site.is_relative_to(project) else site
        print(
            f"{where}/ holds no print page. It is built by the print-site plugin, "
            f"which {args.config} enables — check that it is still listed there"
            + (", and build the portal rather than passing --no-build." if args.no_build else "."),
            file=sys.stderr,
        )
        return 1

    if args.print_page:
        print(f"The whole model as one page: {page}")
        return 0

    browser = find_browser(args.browser)
    if browser is None:
        print(
            "No Chromium-family browser found, so nothing was printed. The page "
            "the PDF is made from is built and ready:\n"
            f"  {page}\n"
            "Open it in any browser and print it to PDF, or name a browser with "
            "--browser or CHROME_PATH.",
            file=sys.stderr,
        )
        return 1

    default_name = f"architecture-{audience}.pdf" if audience else "architecture.pdf"
    output = (args.output or project / DERIVED / default_name).resolve()
    code = render(browser, page, output)
    if code != 0:
        return code

    size = output.stat().st_size / 1024
    where = output.relative_to(project) if output.is_relative_to(project) else output
    print(f"Exported {where} ({size:.0f} KB), printed from {page.name} by {Path(browser).name}.")

    complaint = None if args.no_check else check_diagrams(browser, page)
    if complaint:
        print(complaint, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
