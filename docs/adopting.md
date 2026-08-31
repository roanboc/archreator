# Adopting archreator

_[← Repository README](../README.md) · [The method](./method.md)_

Three ways in, all landing at the same place — the skills drive the process
whichever you take.

## Option A — install the plugin (recommended)

Works on any project, existing or new. Pick your agent:

**Claude Code**

```shell
/plugin marketplace add roanboc/archreator
/plugin install archreator@archreator
```

**GitHub Copilot** — the CLI, VS Code, or the Copilot app

```shell
copilot plugin marketplace add roanboc/archreator
copilot plugin install archreator@archreator
```

**Codex CLI**

```shell
codex plugin marketplace add roanboc/archreator
codex plugin install archreator@archreator
```

Then just say what you want to model. The `establish-project` skill
takes it from there: it asks what the project is, picks a modeling depth,
tells you which one it picked, and writes the scaffold into your
repository.

**The plugin ships two things.** The skills — which do not touch your files
until you ask them to — and the scaffold under
[`plugins/archreator/scaffold/`](../plugins/archreator/scaffold/architecture/README.md), which `establish-project`
copies into your project. Nothing else lands.

## Option B — install the skills on their own

Gemini CLI installs an extension from a repository root rather than a
subdirectory, so it cannot take this repository's plugin. `.agents/skills/`
is the directory every host reads, and
[`install_skills.py`](../plugins/archreator/scripts/install_skills.py) fills
it — from a clone of this repository:

```shell
python3 plugins/archreator/scripts/install_skills.py
```

`--repo` puts them in the current project's `.agents/skills/` instead of your
home directory, and `--dry-run` shows what would land. Restart the agent
afterwards so it rescans.

This route ships the skills and not the scaffold, so `establish-project`
emits the scaffold on first run exactly as it does under a plugin — or take
Option C and copy it yourself.

## Option C — clone the scaffold directly

Copy [`plugins/archreator/scaffold/`](../plugins/archreator/scaffold/architecture/README.md) into a new repository. It is eleven files:

- `AGENTS.md` and `README.md` — placeholders you'll fill in when the
  bootstrap skill runs
- `CLAUDE.md` and `GEMINI.md` — one line each, importing `AGENTS.md`, so
  the host that reads only its own filename still finds the entry point
- `architecture/README.md` — the front door: a status row per layer saying
  `Local`, `External`, `Out of scope` or a named `Gap`. Layer folders appear
  when a skill first has something to put in them, from the plugin's
  `assets/`
- `scripts/` — the two validators, run before every push, the parse they
  share, and its prefix data. The reading tools stay in the plugin and reach
  a project with `--project` — see
  [§ Reaching a reader who will not open the repository](#reaching-a-reader-who-will-not-open-the-repository)
- `.gitignore` — keeps bytecode, machine-local settings and everything
  regenerated out of the history

Then follow the bootstrap checklist by hand, or install the skills and let
`establish-project` do it.

## Keeping a project in sync with the method

Three things ship in this repo with different lifecycles, and only one of
them stays in sync automatically:

- **The skills**, at `plugins/archreator/skills/*/`, come with the plugin and
  update when you run `/plugin update archreator@archreator` in Claude Code,
  `copilot plugin update archreator` in Copilot, or
  `codex plugin update archreator` in Codex. Installed through Option B
  instead, they update by re-running `install_skills.py` after a `git pull`.
- **The scaffold**, at `plugins/archreator/scaffold/`, is copied *once* into your project by
  `establish-project`. It does not update afterwards, because a
  scaffold that changed under a project would rewrite documents the
  Requester already approved.
- **The scaffold's own scripts** in `plugins/archreator/scaffold/scripts/` land in your
  project's `scripts/`. They are the same on both sides; if the method's
  validators change, copy the updated files across.

If a scaffold change matters enough to backport (a rule that would
retroactively affect an existing model), it becomes an initiative in your
project like any other: assessed, approved at Understanding, and applied by hand.

## Reading order

- Understand what changes: [`docs/method.md`](./method.md)
- See what each skill is for:
  [`plugins/archreator/skills/README.md`](../plugins/archreator/skills/README.md)
- See it applied to a real organization:
  [`architecture-archreator`](https://github.com/roanboc/architecture-archreator)

## Contributing back

Improvements to the method (a new skill, a change to an existing one, a
rule refinement) are welcome. See [`CONTRIBUTING.md`](../CONTRIBUTING.md)
in the root — the method itself governs how it evolves, so a proposal runs
through the same gates it makes you run through.

## Reaching a reader who will not open the repository

Two ways, and neither of them is a second copy of the model.

**A portal.** One command writes a stock MkDocs Material config into
`.archreator/work/portal/` and tells you how to build or serve it:

```bash
model.py --project . portal
uvx --with mkdocs-material mkdocs build -f .archreator/work/portal/mkdocs.yml
```

That is the whole of it — a theme, Mermaid, and search. There was a custom
theme directory once: an overridden template, a comment box, a hand-written
pan-and-zoom viewer, a PDF cover page. Five hundred lines of front-end that had
to keep working across two upstream projects, to render documents that render
fine without them.

**A brief.** For one question rather than the whole model, `build_brief.py`
writes a single Markdown document about a named scope — the elements in it,
generated views of how they cross the layers, and what the documents already
say. Hand that to somebody, or convert it to whatever format they asked for.

```bash
build_brief.py --project . --element BSVC1 --focus business
```

**There is no PDF export any more.** There was one — a headless browser
printing the whole model through a print-site plugin — and it produced the
artifact most likely to be mailed around and quoted eight months after it
stopped being true. A brief is a better thing to hand somebody, and turning
one page of Markdown into a PDF is not something the method needs to own.

Everything generated lands under `.archreator/`, which is gitignored. Delete it
and nothing is lost; a published copy that lives in the repository is the
second model everyone edits instead.
