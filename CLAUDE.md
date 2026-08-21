# CLAUDE.md

This repository is **archreator** — an enterprise architecture method that
ships as a Claude Code plugin. It is method and scaffold, nothing more:
worked examples of the method applied to real organizations live in
[`architecture-archreator`](https://github.com/roanboc/architecture-archreator).

## Layout

| Path | What it holds |
| ---- | ------------- |
| [`plugins/archreator/skills/`](./plugins/archreator/skills/README.md) | The fifteen skills that are the method, ordered by the process each realizes, with the four rulebooks last. A verb-and-object name is a skill you run; a noun phrase is one you consult |
| [`plugins/archreator/.claude-plugin/plugin.json`](./plugins/archreator/.claude-plugin/plugin.json) · [`.claude-plugin/marketplace.json`](./.claude-plugin/marketplace.json) | The plugin and marketplace manifests |
| [`plugins/archreator/scripts/`](./plugins/archreator/scripts/check_skills.py) | `check_skills.py`, which checks the corpus against [the skill format](./docs/skill-format.md) and the process model. It stays out of `scaffold/` because a downstream project has no skills |
| `plugins/archreator/scaffold/` | The empty project scaffold, copied whole into a new project by `establish-project` — [the layered model](./plugins/archreator/scaffold/architecture/README.md), [the validators and the projection](./plugins/archreator/scaffold/scripts/README.md), a `.gitignore`, and placeholder `CLAUDE.md`, `README.md` and `CONTRIBUTING.md`. Everything here ships, so it cannot document itself; this row is its description |
| [`docs/`](./docs/method.md) | The method explained in plain English — how the process works, how to adopt it, and [the format every skill follows](./docs/skill-format.md). The skill catalogue is not here; it lives beside the skills |
| [`site/`](./site/index.html) | The one-page public site, deployed to <https://roanboc.github.io/archreator/> |
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

archreator ships as a Claude Code plugin today, and is not tied to it.
**Method content and skill frontmatter are portable; packaging is
provider-specific and disposable.** The test for any file is _would this
need editing if Claude Code vanished tomorrow, or just moving?_ Further
platforms are additive — each adds a manifest, none forks the method.

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
edges, for consumers that cannot read Markdown tables. It is a tool rather
than a gate, and it finds nothing here — the scaffold has no elements.

`check_skills.py` needs PyYAML only once skills carry YAML bodies. Run it with
`uv run` instead of `python3` where that is not installed.

## Conventions

- Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, …).
- Documentation language: **English**.
- The skill catalogue and its groups live in
  [`plugins/archreator/skills/README.md`](./plugins/archreator/skills/README.md); the deeper
  explanation of the method lives under [`docs/`](./docs/method.md).
