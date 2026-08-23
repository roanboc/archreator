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
import shutil
import subprocess
import sys
from pathlib import Path

# This file is also loaded by MkDocs as a build hook, by path rather than as
# an import, so the directory it lives in is not on the path when that happens.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from model_graph import EXCLUDED_DIRS, MODEL_DIR, find_projects  # noqa: E402

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
# The derived tree, and the two things in it. `src/` is the staged copy MkDocs
# publishes, `site/` is the portal it builds.
DERIVED = ".docs"
STAGING = f"{DERIVED}/src"
SITE = f"{DERIVED}/site"
CONFIG = "mkdocs.yml"
# The packages `mkdocs.yml` names. Reported by import name, installed under
# another, so both are carried.
REQUIRED = {"mkdocs": "mkdocs", "material": "mkdocs-material",
            "mkdocs_print_site_plugin": "mkdocs-print-site-plugin"}


def _excluded(path: Path) -> bool:
    return bool((EXCLUDED_DIRS | {DERIVED}) & set(path.parts))


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


def run_mkdocs(project: Path, arguments: list[str]) -> int:
    command = [sys.executable, "-m", "mkdocs", *arguments, "--config-file", str(project / CONFIG)]
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
    print(f"{published} document(s) staged into {STAGING}/ ({changed}).")
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
        print(
            f"Portal built into {SITE}/. It uses directory URLs, so read it with\n"
            f"  python3 scripts/build_docs.py --serve\n"
            f"rather than by opening the files directly."
        )
    return code


if __name__ == "__main__":
    sys.exit(main())
