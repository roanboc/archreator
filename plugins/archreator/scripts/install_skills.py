#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Copy the skills into the directory every host reads.

Claude Code, Copilot and Codex install archreator as a plugin, and that is
the route `docs/adopting.md` recommends: the plugin carries the scaffold as
well as the skills. Gemini CLI installs an extension from a repository root
rather than a subdirectory, so it cannot take this repository's plugin, and
a developer on any host may simply prefer not to install one.

`.agents/skills/` is the path all four hosts read, and this script fills it.
It copies skills only. The scaffold arrives separately - `establish-project`
still emits it, or Option C in `docs/adopting.md` copies it by hand.

Existing skill directories are replaced, so re-running after a `git pull` is
how an installation is updated.

Exit code is 0 when every skill lands, 1 otherwise.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def _find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / ".git").exists():
            return candidate
    return start


REPO_ROOT = _find_repo_root(Path(__file__).resolve().parent)
SKILLS_DIR = REPO_ROOT / "plugins" / "archreator" / "skills"


def skill_dirs() -> list[Path]:
    """The skill folders, which are the ones holding a SKILL.md.

    `skills/README.md` is the catalogue, not a skill, and a host that
    scanned it as one would surface a table of contents as an instruction.
    """
    if not SKILLS_DIR.is_dir():
        return []
    return sorted(p for p in SKILLS_DIR.iterdir() if (p / "SKILL.md").is_file())


def resolve_destination(args: argparse.Namespace) -> Path:
    if args.dest:
        return Path(args.dest).expanduser().resolve()
    if args.repo:
        return Path.cwd() / ".agents" / "skills"
    return Path.home() / ".agents" / "skills"


def main() -> int:
    # The skill names are ASCII, but the findings below are not, and a
    # console that cannot encode them should show a replacement character
    # rather than take the run down with it.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):  # pragma: no cover
            pass

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--repo",
        action="store_true",
        help="install into ./.agents/skills/ in the current project instead of the home directory",
    )
    parser.add_argument(
        "--dest",
        help="install into this directory instead of either default",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="list what would be copied and change nothing",
    )
    args = parser.parse_args()

    skills = skill_dirs()
    if not skills:
        print(f"No skills found under {SKILLS_DIR} - nothing to install.")
        return 1

    destination = resolve_destination(args)
    print(f"{len(skills)} skills → {destination}")

    if args.dry_run:
        for skill in skills:
            state = "replace" if (destination / skill.name).exists() else "install"
            print(f"  {state:<8} {skill.name}")
        print("Dry run - nothing was written.")
        return 0

    errors: list[str] = []
    destination.mkdir(parents=True, exist_ok=True)
    for skill in skills:
        target = destination / skill.name
        try:
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(skill, target)
        except OSError as exc:
            errors.append(f"{skill.name}: {exc}")

    if errors:
        print("Could not install:")
        for line in errors:
            print(f"  {line}")
        return 1

    print("Installed. Restart your agent so it rescans the directory.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
