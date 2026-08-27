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
"""Publish the model as a documentation portal, for readers who never clone the repo.

The Markdown under `architecture/` is the source of truth and this changes
nothing about that. The portal is a *rendering* of those files: rebuilt from
them on every run, gitignored, and carrying no sentence they do not carry.
Same discipline as `build_model.py`, for the same reason — `stack-selection`
§ A persisted projection needs one of four triggers names a non-agent consumer
as a trigger, and a stakeholder who will never open a repository is one. The
projection answers questions about the model; the portal lets someone read it.

**Why there is a staging step.** MkDocs publishes one directory. This project
keeps its documents where they belong instead — `architecture/`, the root
`README.md`, `CONTRIBUTING.md` — so the build copies them into `.docs/src/`,
keeping every path exactly as it is in the repository. Keeping the paths is
what makes the portal's "edit this page" pencil land on the real file in git
rather than on a copy nobody should edit.

Staging **syncs** rather than wipes: a file whose source has not changed is
left alone. That is what lets `mkdocs.yml` run this same file as a build hook,
so a rebuild under `--serve` re-stages without the write it just made looking
like an edit and starting another rebuild.

    python3 scripts/build_docs.py             # build into .docs/site/
    python3 scripts/build_docs.py --serve     # ... and rebuild as you edit
    python3 scripts/build_docs.py --strict    # a broken link fails the build
    python3 scripts/build_docs.py --stage     # stage only, build nothing

Everything under `.docs/` is derived: delete it and nothing is lost.

**The dependencies are declared inline**, so `uv run scripts/build_docs.py`
fetches them into a throwaway environment and installs nothing globally. With
plain `python3`, install them once instead:

    pip install mkdocs-material mkdocs-print-site-plugin
"""
import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

# This file is also loaded by MkDocs as a build hook, by path rather than as
# an import, so the directory it lives in is not on the path when that happens.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from model_graph import EXCLUDED_DIRS, MODEL_DIR, REPO_ROOT, find_projects  # noqa: E402


def federation(project: Path) -> list[dict]:
    """The federation index, read from the document that owns it.

    Read **by position**: cell 1 names the model, cell 2 what it models, cell 3
    the directory its projection is published in. No header word is
    interpreted, which is the same rule the catalogues and the relationship
    tables follow and for the same reason — a model may be written in any
    language.

    A row counts only when its third cell looks like somewhere a projection
    could be: an absolute URL for a model in another repository, or a relative
    path for one published beside this one. That test is what tells the index
    apart from the prose tables around it without reading a heading.
    """
    doc = project / MODEL_DIR / FEDERATION_DOC
    if not doc.is_file():
        return []
    found = []
    for line in doc.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3 or not cells[0] or not cells[2]:
            continue
        location = cells[2]
        if not (location.startswith(("http://", "https://", "./", "../"))):
            continue
        found.append({"name": cells[0], "subject": cells[1], "projection": location})
    return found


def stage_navigator(project: Path, site: Path) -> list[str]:
    """Put the graph navigator, the projection and sql.js into the built site.

    **The page is never published without a way to say what is wrong with it.**
    Three things have to arrive: the page itself, which is in this repository;
    the projection, which is built from the Markdown; and sql.js, which is
    fetched. Only the third can fail, and when it does the portal still builds
    and the navigator explains itself. A model that will not publish because a
    graph viewer could not download a library is a bad trade — the documents
    are what a reader came for.
    """
    import hashlib
    import io
    import urllib.request
    import zipfile

    notes: list[str] = []
    # Beside the scripts, not inside the project. A repository holding several
    # trees keeps one copy of the tooling for all of them — the same
    # arrangement `neighbourhood.sql` is found by.
    source = Path(__file__).resolve().parent.parent / NAVIGATOR
    if not source.is_dir():
        return notes
    target = site / NAVIGATOR
    target.mkdir(parents=True, exist_ok=True)
    for path in sorted(source.iterdir()):
        if path.is_file():
            shutil.copy2(path, target / path.name)

    # The projection, built from the Markdown like everything else here, and
    # the traversal the page shares with `query_model.py`.
    import build_model

    # **This project's projection, not the repository's.** `collect()` finds
    # every model in the repository, and publishing all of them under one
    # project's portal would put another model's elements at this model's
    # address — the restating the federation rule exists to prevent, done by a
    # build step instead of by an author. A repository holding several models
    # publishes several projections, and the federation index is what joins
    # them.
    mine = build_model.project_name(project)
    projects = [p for p in build_model.collect() if p["project"] == mine]
    if projects:
        build_model.write_sqlite(projects, target / "model.db")
        build_model.write_json(projects, target / "model.json")
    else:
        notes.append(
            f"{NAVIGATOR}/: the model defines no elements, so the navigator will "
            f"say so rather than draw an empty graph"
        )
    traversal = Path(__file__).resolve().parent / "neighbourhood.sql"
    if traversal.is_file():
        shutil.copy2(traversal, target / traversal.name)

    # The federation index, derived. Absent when this model is not the topmost
    # of a federation, which is most models — and the navigator then reads its
    # own projection and behaves exactly as it would have.
    members = federation(project)
    if members:
        (target / FEDERATION_JSON).write_text(
            json.dumps({"schema": 1, "models": members}, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        notes.append(
            f"{NAVIGATOR}/: federating {len(members)} model(s) named in "
            f"{MODEL_DIR}/{FEDERATION_DOC}"
        )
    else:
        (target / FEDERATION_JSON).unlink(missing_ok=True)

    if all((target / name).is_file() for name in SQLJS_FILES):
        return notes
    try:
        with urllib.request.urlopen(SQLJS_URL, timeout=60) as response:
            archive = zipfile.ZipFile(io.BytesIO(response.read()))
        for name, digest in SQLJS_FILES.items():
            blob = archive.read(name)
            got = hashlib.sha256(blob).hexdigest()
            if got != digest:
                raise ValueError(f"{name}: expected {digest}, got {got}")
            (target / name).write_bytes(blob)
    except Exception as error:  # noqa: BLE001 - any failure degrades the same way
        for name in SQLJS_FILES:
            (target / name).unlink(missing_ok=True)
        notes.append(
            f"{NAVIGATOR}/: sql.js {SQLJS_VERSION} could not be fetched ({error}). "
            f"The portal is built and the navigator page will explain what is "
            f"missing; re-run with network access to complete it"
        )
    return notes

# What lands in the portal: the model, and the documents that frame it. Every
# Markdown file directly in the project root is published too, which is how
# `README.md` becomes the front page. A project that keeps documentation
# somewhere else adds the directory here — this tuple is the only thing in the
# portal that knows the project's layout.
STAGED_DIRS = (MODEL_DIR, "docs", "scripts")
# Suffixes copied out of those directories: the Markdown is the content, the
# rest is what a document embeds.
STAGED_SUFFIXES = {".md", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
# The per-host context files carry one line importing `AGENTS.md`. Published,
# they put three copies of the same pointer in the navigation and say nothing
# to a reader who is not an agent.
NOT_STAGED = {"CLAUDE.md", "GEMINI.md"}
# `architecture/reference/` holds source documents exactly as they were
# provided - transcripts, decks, whatever somebody sent. They are provenance
# for the repository and not publication material: the portal exists to hand a
# reader the model, and a model that quotes a transcript has already decided
# what in it was worth saying. Publishing the raw file would also publish
# whatever else was in the room that day, to an audience that was not.
NOT_PUBLISHED = {"reference"}
# The derived tree, and the two things in it. `src/` is the staged copy MkDocs
# publishes, `site/` is the portal it builds.
DERIVED = ".docs"
STAGING = f"{DERIVED}/src"
SITE = f"{DERIVED}/site"
CONFIG = "mkdocs.yml"
# The graph navigator, and what it needs beside it. The page is ours; sql.js is
# not, and the difference is why one is copied and the other is fetched.
NAVIGATOR = "navigator"
# Pinned by version *and* by digest. A release tag can be moved; a SHA-256
# cannot, and this is a binary nobody reviewing a pull request will read.
SQLJS_VERSION = "1.13.0"
SQLJS_URL = (
    f"https://github.com/sql-js/sql.js/releases/download/v{SQLJS_VERSION}/sqljs-wasm.zip"
)
# The federation index, authored in the topmost model of a federation and
# derived into the site beside the navigator. Authored, so it is Markdown and
# it is committed; derived, so the JSON is neither.
FEDERATION_DOC = "federation.md"
FEDERATION_JSON = "federation.json"
SQLJS_FILES = {
    "sql-wasm.js": "694ca5b36aa3e6e71f417819d7df390b65343665fcfa5c69015ca33d93d291b3",
    "sql-wasm.wasm": "0734155c83e493983d1f2ff5b09a4fab6e35a32e9449c7e4e545756439f62d73",
}
# The packages `mkdocs.yml` names. Reported by import name, installed under
# another, so both are carried.
REQUIRED = {"mkdocs": "mkdocs", "material": "mkdocs-material",
            "mkdocs_print_site_plugin": "mkdocs-print-site-plugin"}


def shown(path: Path) -> str:
    """A path as a reader of this repository would name it.

    One repository can hold several models, and `.docs/site` names none of
    them. Reported from the repository root, the message says which.
    """
    return str(path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path)


def _excluded(path: Path) -> bool:
    return bool((EXCLUDED_DIRS | NOT_PUBLISHED | {DERIVED}) & set(path.parts))


def sources(project: Path) -> list[Path]:
    """Every file the portal publishes, in repository order."""
    found: list[Path] = [
        path for path in sorted(project.glob("*.md")) if path.name not in NOT_STAGED
    ]
    for name in STAGED_DIRS:
        root = project / name
        if not root.is_dir():
            continue
        found.extend(
            path
            for path in sorted(root.rglob("*"))
            if path.is_file()
            and path.suffix.lower() in STAGED_SUFFIXES
            and not _excluded(path.relative_to(project))
        )
    return found


# A relative Markdown link. Same shape the link checker matches, and used here
# for the opposite question: not "does this resolve in the repository" but
# "will it still resolve once published".
PORTAL_LINK_RE = re.compile(r"\[[^\]]*\]\(\s*(?!https?:|mailto:|#)([^)\s]+)")


def unpublished_links(project: Path, wanted: dict[Path, Path]) -> list[str]:
    """Links from a staged document to a file that exists but is not staged.

    `check_links.py` proves a link resolves in the repository. That is a
    different question from whether it resolves in the portal, and the two part
    company exactly where a folder is deliberately unpublished — a draft
    catalogue citing the transcript it was built from is the case this exists
    for. The repository reader follows the link; the portal reader gets a 404,
    and nothing else in the pipeline would say so.

    Reported, never fatal. Publishing a partial view is a legitimate choice and
    the person making it should simply know which links it costs.
    """
    staged = set(wanted)
    notes: list[str] = []
    for relative, source in sorted(wanted.items()):
        if source.suffix.lower() != ".md":
            continue
        for match in PORTAL_LINK_RE.finditer(source.read_text(encoding="utf-8", errors="replace")):
            target = match.group(1).split("#", 1)[0]
            if not target:
                continue
            resolved = (source.parent / target).resolve()
            if not resolved.is_file() or not resolved.is_relative_to(project):
                continue
            if resolved.relative_to(project) not in staged:
                notes.append(f"{relative} → {resolved.relative_to(project)}")
    return notes


def stage(project: Path, staging: Path) -> tuple[int, int, int]:
    """Mirror the documents into `staging`. Returns (published, copied, dropped).

    A sync, not a rebuild: a file whose source has not changed is not
    rewritten, so running this from inside a MkDocs rebuild does not look like
    an edit to the watcher that triggered it.
    """
    wanted = {path.relative_to(project): path for path in sources(project)}
    staging.mkdir(parents=True, exist_ok=True)

    dropped = 0
    for existing in sorted(staging.rglob("*"), reverse=True):
        relative = existing.relative_to(staging)
        if existing.is_file() and relative not in wanted:
            existing.unlink()
            dropped += 1
        elif existing.is_dir() and not any(existing.iterdir()):
            existing.rmdir()

    copied = 0
    for relative, source in wanted.items():
        target = staging / relative
        if target.is_file():
            here, there = target.stat(), source.stat()
            if (here.st_size, int(here.st_mtime)) == (there.st_size, int(there.st_mtime)):
                continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied += 1
    return len(wanted), copied, dropped


def on_pre_build(config, **_kwargs) -> None:
    """MkDocs build hook, wired up in `mkdocs.yml`.

    It is what makes `mkdocs build` and `mkdocs serve` correct when they are
    called directly — by a CI action, by an editor, by hand — instead of only
    through this script.
    """
    project = Path(config.config_file_path).resolve().parent
    stage(project, Path(config["docs_dir"]))


def resolve_project(explicit: Path | None) -> Path | None:
    """The project to publish: one that has both a model and a portal config."""
    if explicit is not None:
        return explicit.resolve()
    candidates = [path for path in find_projects() if (path / CONFIG).is_file()]
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        print(
            f"No project to publish: a project is a directory holding both "
            f"`{MODEL_DIR}/` and `{CONFIG}`.",
            file=sys.stderr,
        )
        return None
    print("Several projects found. Name one with --project:", file=sys.stderr)
    for candidate in candidates:
        print(f"  {candidate}", file=sys.stderr)
    return None


def missing_dependencies() -> list[str]:
    return sorted(
        package for module, package in REQUIRED.items()
        if importlib.util.find_spec(module) is None
    )


def run_mkdocs(project: Path, arguments: list[str], config: str = CONFIG) -> int:
    command = [sys.executable, "-m", "mkdocs", *arguments, "--config-file", str(project / config)]
    return subprocess.call(command, cwd=project)


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):  # pragma: no cover - older or wrapped streams
            pass

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--project", type=Path, help="the project to publish (default: the only one)")
    parser.add_argument("--serve", action="store_true", help="serve it, rebuilding as the model is edited")
    parser.add_argument("--addr", default="127.0.0.1:8000", help="address for --serve (default: %(default)s)")
    parser.add_argument("--strict", action="store_true", help="treat MkDocs warnings, a broken link among them, as errors")
    parser.add_argument("--stage", action="store_true", help="stage the documents and build nothing")
    args = parser.parse_args()

    project = resolve_project(args.project)
    if project is None:
        return 1
    if not (project / CONFIG).is_file():
        print(f"{project}: no {CONFIG} — nothing says how to publish this project.", file=sys.stderr)
        return 1

    published, copied, dropped = stage(project, project / STAGING)
    changed = f"{copied} written, {dropped} removed" if copied or dropped else "already current"
    print(f"{published} document(s) staged into {shown(project / STAGING)}/ ({changed}).")

    dangling = unpublished_links(project, {p.relative_to(project): p for p in sources(project)})
    if dangling:
        print(f"{len(dangling)} link(s) point at files this portal does not publish. They")
        print("resolve in the repository and will 404 for a reader of the site:")
        for note in dangling:
            print(f"  {note}")
    if args.stage:
        return 0

    missing = missing_dependencies()
    if missing:
        print(
            "The portal needs " + ", ".join(missing) + ", which this interpreter does not have.\n"
            "  uv run scripts/build_docs.py        # fetches them, installs nothing\n"
            "  pip install " + " ".join(missing) + "   # or install them once",
            file=sys.stderr,
        )
        return 1

    arguments = ["serve", "--dev-addr", args.addr] if args.serve else ["build"]
    if args.strict:
        arguments.append("--strict")
    if args.serve:
        # MkDocs watches what it publishes, which is the staged copy. These
        # point it at the documents themselves, so an edit to the model
        # re-stages through the hook and rebuilds.
        watched = [project / name for name in STAGED_DIRS] + [
            path for path in sorted(project.glob("*.md")) if path.name not in NOT_STAGED
        ]
        for path in watched:
            if path.exists():
                arguments += ["--watch", str(path)]

    code = run_mkdocs(project, arguments)
    if code == 0 and not args.serve:
        site = shown(project / SITE)
        for note in stage_navigator(project, project / SITE):
            print(f"  {note}")
        print(
            f"Portal built into {site}/. Open {site}/index.html to read it, "
            f"{site}/{NAVIGATOR}/ for the graph, hand the folder to whoever will "
            f"host it, or run --serve to rebuild as you edit."
        )
    return code


if __name__ == "__main__":
    sys.exit(main())
