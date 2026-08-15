# CLAUDE.md

This repository is **archreator** — an enterprise architecture method that
ships as a Claude Code plugin. It is method and scaffold, nothing more:
worked examples of the method applied to real organizations live in
[`architecture-archreator`](https://github.com/roanboc/architecture-archreator).

## Layout

| Path | What it holds |
| ---- | ------------- |
| [`.claude/skills/`](./.claude/skills/README.md) | The fourteen skills that are the method, grouped by role — `core-*` (the spine), `discover-*` (question-driven), `doc-*` (state management), `flow-*` (situational) |
| [`.claude/.claude-plugin/plugin.json`](./.claude/.claude-plugin/plugin.json) · [`.claude-plugin/marketplace.json`](./.claude-plugin/marketplace.json) | The plugin and marketplace manifests |
| [`.claude/templates/`](./.claude/templates/README.md) | The empty project scaffold — layer READMEs, the two validators (`scripts/`), the placeholder `CLAUDE.md` and `README.md`. Copied into a new project by `core-project-bootstrap` |
| [`docs/`](./docs/method.md) | The method explained in plain English — how the process works, the skill catalogue, how to adopt it |
| [`site/`](./site/index.html) | The one-page public site, deployed to <https://roanboc.github.io/archreator/> |
| [`CONTRIBUTING.md`](./CONTRIBUTING.md) | How to contribute changes to this repository |

## The rule that governs everything else

**Strategy and business architecture are validated before any other layer,
and the Requester approves at explicit gates before development.** A change
to a project *using* archreator runs through `core-architecture-first-change`;
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
python3 .claude/templates/scripts/check_links.py    # relative links and HTML anchors resolve
python3 .claude/templates/scripts/check_model.py    # element-ID references resolve, per project
```

Both must be green before pushing; CI runs the same on the scaffold as any
downstream project runs on its own model.

## Conventions

- Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, …).
- Documentation language: **English**.
- The skill catalogue and its groups live in
  [`.claude/skills/README.md`](./.claude/skills/README.md); the deeper
  explanation of the method lives under [`docs/`](./docs/method.md).
