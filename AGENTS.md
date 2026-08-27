# AGENTS.md

This repository is **archreator** — an enterprise architecture method that
ships as a plugin for coding agents. It is method and scaffold, nothing
more: worked examples of the method applied to real organizations live in
[`architecture-archreator`](https://github.com/roanboc/architecture-archreator).

## Layout

| Path | What it holds |
| ---- | ------------- |
| [`plugins/archreator/skills/`](./plugins/archreator/skills/README.md) | The seventeen skills that are the method, ordered by the process each realizes, with the four rulebooks last. A verb-and-object name is a skill you run; a noun phrase is one you consult |
| [`plugins/archreator/plugin.json`](./plugins/archreator/plugin.json) · [`plugins/archreator/.claude-plugin/plugin.json`](./plugins/archreator/.claude-plugin/plugin.json) · [`.claude-plugin/marketplace.json`](./.claude-plugin/marketplace.json) | The plugin and marketplace manifests. The two plugin manifests are the same fact in the two places hosts look for it, and `check_skills.py` holds them together |
| [`plugins/archreator/scripts/`](./plugins/archreator/scripts/check_skills.py) | `check_skills.py`, which checks the corpus against [the skill format](./docs/skill-format.md) and the process model, and [`install_skills.py`](./plugins/archreator/scripts/install_skills.py), which copies the skills into `.agents/skills/` for a host that installs no plugin. Both stay out of `scaffold/` because a downstream project has no skills |
| `plugins/archreator/scaffold/` | The empty project scaffold, copied whole into a new project by `establish-project` — [the layered model](./plugins/archreator/scaffold/architecture/README.md), the reference folder its sources are kept in, [the validators, the projection and the two readers of it, the portal and the PDF export](./plugins/archreator/scaffold/scripts/README.md), [the graph navigator](./plugins/archreator/scaffold/navigator/index.html), the `mkdocs.yml` and `overrides/` those last two read, a `.github/` holding the pull-request template, the question form and the two workflows it ships switched off, a `.gitignore`, and placeholder `AGENTS.md`, `README.md` and `CONTRIBUTING.md`. Everything here ships, so it cannot document itself; this row is its description |
| [`docs/`](./docs/method.md) | The method explained in plain English — how the process works, how to adopt it, [how a model is published](./docs/publishing.md), and [the format every skill follows](./docs/skill-format.md). The skill catalogue is not here; it lives beside the skills |
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
python3 plugins/archreator/scripts/check_skills.py             # the skill corpus against the process model
```

All three must be green before pushing. The first two run on the scaffold here
exactly as a downstream project runs them on its own model; the third has no
downstream counterpart.

`scaffold/scripts/build_model.py` projects a model into `.model/` as nodes and
edges, for consumers that cannot read Markdown tables, and
`scaffold/scripts/query_model.py` is that consumer — `trace` for what a change
to one element would touch, `coverage` for what names no realizing artifact.
Both are tools rather than gates, and both find nothing here: the scaffold has
no elements.

A reference can name an element in another model — `other-model::CAP1` — and
`check_model.py` resolves it against that model when it is in the same
repository, or against `architecture/imports.md` when it is not. Nothing
fetches: a validator reading a sibling repository on every pull request would
be slow, would fail when somebody else's site was down, and would let another
team's push break this build.

`scaffold/navigator/` is the projection with a picture — one static page that
draws the model, filters it by layer and walks outward from any element.
`build_docs.py` publishes it with the portal. It executes
`scaffold/scripts/neighbourhood.sql`, the same traversal `query_model.py` runs,
because a walk implemented once per reader drifts.

`scaffold/scripts/build_docs.py` and `export_pdf.py` are the last two tools:
the model as a website and as one PDF, for readers who are not in the
repository — see [`docs/publishing.md`](./docs/publishing.md). Run against the
scaffold they publish the empty template, which is exactly what CI does to
prove the shipped configuration still builds.

`check_skills.py` needs PyYAML only once skills carry YAML bodies. Run it with
`uv run` instead of `python3` where that is not installed.

## Conventions

- Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, …).
- Documentation language: **English**.
- The skill catalogue and its groups live in
  [`plugins/archreator/skills/README.md`](./plugins/archreator/skills/README.md); the deeper
  explanation of the method lives under [`docs/`](./docs/method.md).
