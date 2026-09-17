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
  share, its prefix data and their own README. The reading tools stay in the
  plugin and reach a project with `--project` — see
  [§ Reaching a reader who will not open the repository](#reaching-a-reader-who-will-not-open-the-repository)
- `.gitignore` — keeps bytecode, machine-local settings and everything
  regenerated out of the history

Then follow the bootstrap checklist by hand, or install the skills and let
`establish-project` do it.

## Keeping a project in sync with the method

A project on an earlier method has a crossing to make first — the gates are
gone, so is the open-questions log, and fifteen skills are now invoked by
name. That is [`docs/migrating.md`](./migrating.md), separate from the
routine sync below.

Three things ship in this repo with different lifecycles, and only one of
them stays in sync automatically:

- **The skills**, at `plugins/archreator/skills/*/`, come with the plugin and
  update when you run `/plugin update archreator@archreator` in Claude Code,
  `copilot plugin update archreator` in Copilot, or
  `codex plugin update archreator` in Codex. Installed through Option B
  instead, they update by re-running `install_skills.py` after a `git pull`.
- **The scaffold**, at `plugins/archreator/scaffold/`, is copied *once* into your project by
  `establish-project`. It does not update afterwards; a scaffold that
  changed under a project would rewrite documents the Requester already
  approved.
- **The scaffold's own scripts** in `plugins/archreator/scaffold/scripts/` land in your
  project's `scripts/`. They are the same on both sides; if the method's
  validators change, copy the updated files across.

If a scaffold change matters enough to backport (a rule that would
retroactively affect an existing model), it becomes an initiative in your
project like any other: assessed, applied by hand, and merged the same way.

## Reading order

- Understand what changes: [`docs/method.md`](./method.md)
- See what each skill is for:
  [`plugins/archreator/skills/README.md`](../plugins/archreator/skills/README.md)
- See it applied to a real organization:
  [`architecture-archreator`](https://github.com/roanboc/architecture-archreator)

## Contributing back

Improvements to the method (a new skill, a change to an existing one, a
rule refinement) are welcome. See [`CONTRIBUTING.md`](../CONTRIBUTING.md)
in the root — the method itself governs how it evolves, so a proposal is
built and merged the same way it makes you build and merge.

## Reaching a reader who will not open the repository

Three ways, and none of them is a second copy of the model.

**A portal.** One command writes a stock MkDocs Material config into
`.archreator/work/portal/` and tells you how to build or serve it:

```bash
model.py --project . portal
uvx --with mkdocs-material mkdocs build -f .archreator/work/portal/mkdocs.yml
```

That is the whole of it — a theme, Mermaid, and search. No custom template, no
viewer, no cover page: the documents render fine without them.

**A brief.** For one question rather than the whole model, `build_brief.py`
writes a single Markdown document about a named scope — the elements in it,
generated views of how they cross the layers, and what the documents already
say. Hand that to somebody, or convert it to whatever format they asked for.

```bash
build_brief.py --project . --element BSVC1 --focus business
```

**A PDF is a conversion, not an export.** The method ships no PDF exporter. A
business reader who asks for a PDF gets one brief or scope converted by the
agent, landing under gitignored `.archreator/work/` beside its Markdown source
— never the whole model.

**A Word document, for feedback.** A reader who will mark up prose in a tool
everyone already has gets one `.docx` built from a named audience — an
explicit, ordered list of paths a human wrote down, globs allowed, nothing
included by default:

    # architecture/export/board.yml
    title: BigView — Board pack
    files:
      - architecture/README.md
      - architecture/1_estrategia/README.md
      - architecture/1_estrategia/*.md
      - architecture/2_negocio/README.md
      - architecture/2_negocio/*.md

    export_word.py --project . --config architecture/export/board.yml

Every diagram travels — rendered where a Mermaid renderer happens to be on
`PATH`, kept as clearly labeled source otherwise — or the run refuses to
write a document that silently dropped one. Track Changes is on; nothing
else about editing is locked down yet, pending how that actually reads for
whoever gets the document. The footer names the project, the audience, when
it was built and the revision it came from, so a copy that comes back edited
can still be placed. This is an explicit allow-list one audience needs, not
the whole model minus some excludes — the shape a prior version of this
method tried for PDF and reversed, because it produced the artifact most
likely to be mailed around and quoted long after it stopped being true. What
comes back is read by the agent like any other input; nothing here writes it
back into the model automatically.

Everything generated lands under `.archreator/`, which is gitignored. Delete it
and nothing is lost.
