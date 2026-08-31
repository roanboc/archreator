# AGENTS.md

This repository is **archreator** — an enterprise architecture method that
ships as a plugin for coding agents. It is method and scaffold, nothing
more: worked examples of the method applied to real organizations live in
[`architecture-archreator`](https://github.com/roanboc/architecture-archreator).

## Layout

| Path | What it holds |
| ---- | ------------- |
| [`plugins/archreator/skills/`](./plugins/archreator/skills/README.md) | The eighteen skills that are the method, ordered by the process each realizes, with the four rulebooks last. A verb-and-object name is a skill you run; a noun phrase is one you consult |
| [`plugins/archreator/plugin.json`](./plugins/archreator/plugin.json) · [`plugins/archreator/.claude-plugin/plugin.json`](./plugins/archreator/.claude-plugin/plugin.json) · [`.claude-plugin/marketplace.json`](./.claude-plugin/marketplace.json) | The plugin and marketplace manifests. The two plugin manifests are the same fact in the two places hosts look for it, and `check_skills.py` holds them together |
| [`plugins/archreator/scripts/`](./plugins/archreator/scripts/check_skills.py) | `check_skills.py`, which checks the corpus against [the skill format](./docs/skill-format.md) and the process model, and [`install_skills.py`](./plugins/archreator/scripts/install_skills.py), which copies the skills into `.agents/skills/` for a host that installs no plugin. Both stay out of `scaffold/` because a downstream project has no skills |
| [`plugins/archreator/scaffold/`](./plugins/archreator/scaffold/architecture/README.md) | What lands in a new project on its first commit, and nothing more — `AGENTS.md` with the roles and the declared depth, `README.md`, the two host pointers, `.gitignore`, `architecture/README.md` (the status table that replaced an empty layer tree), and `scripts/` with the two validators and the parse they share |
| [`plugins/archreator/assets/`](./plugins/archreator/assets/README.md) | The templates a skill emits **when the project has something to put in them** — the layer READMEs, the non-layer folders, the GitHub-shaped files, `CONTRIBUTING.md`. Their relative links resolve where they land, so `check_links.py` skips the tree and `check_skills.py` proves instead that every asset is reachable from a skill |
| [`docs/`](./docs/method.md) | The method explained in plain English — how the process works, [how to adopt it and how a model is published](./docs/adopting.md), and [the format every skill follows](./docs/skill-format.md). The skill catalogue is not here; it lives beside the skills |
| [`site/`](./site/index.html) | The public site, deployed to <https://roanboc.github.io/archreator/> — a landing page, [a get-started page](./site/start.html) with the install recipe per host, and the stylesheet both share |
| [`CONTRIBUTING.md`](./CONTRIBUTING.md) | How to contribute changes to this repository |

## The rule that governs everything else

**Strategy and business architecture are validated before any other layer,
and the Requester approves at explicit gates before development.** A change
to a project *using* archreator runs through `align-change-through-layers`;
a change to *the method itself* is recorded in the sibling repository
[`architecture-archreator`](https://github.com/roanboc/architecture-archreator),
whose `product-archreator/architecture/scope/` is where the method's own
initiatives live.

Pure bug fixes to the method that change no documented behavior skip the
gates but still update whatever the fix falsifies.

## Portability

archreator runs on Claude Code, GitHub Copilot (CLI, VS Code and the Copilot
app), OpenAI Codex CLI and Gemini CLI. **Method content and skill frontmatter
are portable; packaging is provider-specific and disposable.** The test for
any file is _would this need editing if one host vanished tomorrow, or just
moving?_ Further platforms are additive — each adds a manifest, none forks
the method.

Three rules keep that true. A skill names no host: no tool names, no
`allowed-tools`, no path into a host's own configuration. The project entry
point is `AGENTS.md`, and the `CLAUDE.md` and `GEMINI.md` beside it hold
nothing but an `@AGENTS.md` import, because Claude Code reads `CLAUDE.md`
only and has no `AGENTS.md` fallback. And a fact that has to exist in two
places for two hosts is written twice and held together by
[`check_skills.py`](./plugins/archreator/scripts/check_skills.py), never
generated at runtime.

[`docs/adopting.md`](./docs/adopting.md) carries the install recipe for each
host.

## Commands

```bash
python3 plugins/archreator/scaffold/scripts/check_links.py    # relative links and HTML anchors resolve
python3 plugins/archreator/scaffold/scripts/check_model.py    # element-ID references resolve, per project
uv run    plugins/archreator/scripts/check_skills.py           # the skill corpus against the process model
uv run    pytest plugins/archreator/scripts/tests/
```

All must be green before pushing. The first two run on the scaffold here
exactly as a downstream project runs them on its own model; the third has no
downstream counterpart.

**The scaffold ships two validators and the parse they share, and nothing
else.** A project has to be able to check itself with no plugin installed and
no network, so `check_links.py`, `check_model.py`, `model_graph.py` and
`element-prefixes.json` are copied into it. The reading tools are not:
`plugins/archreator/scripts/model.py` and `build_brief.py` run from here and
take `--project <path>`, importing that project's `model_graph.py` so there is
one parse of the document convention rather than one per project.

```bash
model.py --project . trace CAP1     # what a change to one element would touch
model.py --project . coverage       # what names no realizing artifact
model.py --project . portal         # a stock MkDocs config in .archreator/work/portal/
model.py --project . export         # .model/model.json, which nothing here reads back
build_brief.py --project . --element CAP1 --focus impact
```

`build_brief.py` names a scope and writes one Markdown brief into
`.archreator/work/briefs/` — the elements that matter, generated ArchiMate
views of how they depend on each other across the layers, and the paragraphs
the documents already write. Disposable, never committed, stamped with the
revision it came from.

**Nothing is cached.** Every tool parses the Markdown fresh, which takes well
under a second on the largest model built on this method. There was a
persisted SQLite graph; in that model it had gone stale and was answering from
a revision that no longer described the architecture, with nothing to tell the
reader. A cache that is silently wrong is worse than no cache.

A reference can name an element in another model — `other-model::CAP1` — and
`check_model.py` resolves it against that model when it is in the same
repository, or against `architecture/imports.md` when it is not. Nothing
fetches: a validator reading a sibling repository on every pull request would
be slow, would fail when somebody else's site was down, and would let another
team's push break this build.

`check_skills.py` needs PyYAML, which `uv run` supplies from the script's own
inline metadata.

## Conventions

- Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, …).
- Documentation language: **English**.
- The skill catalogue and its groups live in
  [`plugins/archreator/skills/README.md`](./plugins/archreator/skills/README.md); the deeper
  explanation of the method lives under [`docs/`](./docs/method.md).
