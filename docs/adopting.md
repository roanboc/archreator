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

### When the plugin does not load

A host that cannot reach the marketplace — a sandboxed or offline session, a
cloud runner that never fetches one — starts with **no archreator skills at
all**. Nothing announces this: the agent simply never mentions the method,
because fourteen of the seventeen skills are invisible to it by design and
the other three were never loaded either. Two symptoms give it away: the agent
plans a change without running `align-change-through-layers`, or it quotes a
skill it reconstructed from somewhere rather than read.

Check it before blaming the method:

```shell
/plugin
```

An empty list means the plugin is not installed in that session, whatever
`.claude/settings.json` declares — a project that enables a plugin through
`extraKnownMarketplaces` still needs the host to fetch it. Take **Option B**
for those sessions: `.agents/skills/` is checked into nothing, read by every
host, and needs no marketplace.

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

Copy [`plugins/archreator/scaffold/`](../plugins/archreator/scaffold/architecture/README.md) into a new repository. It is thirteen files:

- `AGENTS.md` and `README.md` — placeholders you'll fill in when the
  bootstrap skill runs
- `CLAUDE.md` and `GEMINI.md` — one line each, importing `AGENTS.md`, so
  the host that reads only its own filename still finds the entry point
- `architecture/README.md` — the front door: a status row per layer saying
  `Local`, `External`, `Out of scope` or a named `Gap`. Layer folders appear
  when a skill first has something to put in them, from the plugin's
  `assets/`
- `scripts/` — the three validators, run before every push, the parse two
  of them share, its prefix data, the word list of the third and their own
  README. The reading tools stay in the
  plugin and reach a project with `--project` — see
  [§ Reaching a reader who will not open the repository](#reaching-a-reader-who-will-not-open-the-repository)
- `.gitignore` — keeps bytecode, machine-local settings and everything
  regenerated out of the history

Then follow the bootstrap checklist by hand, or install the skills and let
`establish-project` do it.

## Pairing it with a delivery framework

archreator models why the subject exists, who does what and which information
it holds, and registers which software realizes it. It does not design or
build the software: that is the job of the delivery framework the project
already uses — a spec-driven tool such as GitHub Spec Kit, Kiro or OpenSpec,
or a team's own design documents.

`AGENTS.md` § Delivery names the framework and its **standing file** — Spec
Kit's constitution, Kiro's steering files, or whichever file that framework
reads on every task. When a change touches a principle or a business rule,
the agent carries it into that file in its own words with a link back to the
model, so the framework builds against the intent the Requester confirmed.
The realization register in `4_application/` links each component to its
specification there. With no framework named, the scope documents are the
specification.

## Keeping a project in sync with the method

A project on an earlier method has a crossing to make first — a confirmation
now validates a document rather than the merge alone, layers 4 and 5 are a
register handed over to the delivery framework, the gates and the
open-questions log are gone, and fourteen skills are invoked by name. That is [`docs/migrating.md`](./migrating.md), separate from the
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
  confirmed.
- **The scaffold's own scripts** in `plugins/archreator/scaffold/scripts/` land in your
  project's `scripts/`. They are the same on both sides; if the method's
  validators change, copy the complete tool bundle across:
  `check_links.py`, `check_model.py`, `check_prose.py`, `model_graph.py`,
  `element-prefixes.json`, and `prose-denylist.json`. `check_model.py` and
  `check_prose.py` depend on the parser and their data files, so copying only
  the visible validator can leave an older project without the new check.

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

**One question is still a conversion, not an export.** A reader who asks for
a PDF of a single brief or scope gets one converted by the agent, landing
under gitignored `.archreator/work/` beside its Markdown source — never the
whole model, and no dedicated exporter for this case.

**An audience gets a PDF, built from an explicit allow-list.** A reader
outside the repository who needs more than one question answered — a board
pack, a customer-facing summary — gets one `.pdf` built from a named
audience: an explicit, ordered list of paths a human wrote down, globs
allowed, nothing included by default:

    # architecture/export/board.yml
    title: BigView — Board pack
    files:
      - architecture/README.md
      - architecture/1_estrategia/README.md
      - architecture/1_estrategia/*.md
      - architecture/2_negocio/README.md
      - architecture/2_negocio/*.md

    export_pdf.py --project . --config architecture/export/board.yml

Rendered with a real Markdown library and a real browser, not a hand-written
converter — the first version of this tool wrote its own, and it silently
mishandled links, which is exactly the kind of gap a real renderer does not
have. Every diagram is resolved to a picture or a labeled source block, never
a gap: `mermaid.js` is fetched once via `npm` and rendered per-diagram, so
one diagram's syntax error becomes its own labeled fallback instead of
sinking the rest of the document; no `npm` on `PATH` falls back to labeled
source throughout. The footer names the project, the audience, when it was
built and the revision it came from. This is an explicit allow-list one
audience needs, not the whole model minus some excludes — the shape a prior
version of this method tried for PDF and reversed, because it produced the
artifact most likely to be mailed around and quoted long after it stopped
being true. A PDF carries no track-changes equivalent — a reader comments
with whatever their viewer already offers, and what comes back is read by
the agent like any other input; nothing here writes it back into the model
automatically.

Everything generated lands under `.archreator/`, which is gitignored. Delete it
and nothing is lost.
