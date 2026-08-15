# Adopting archreator

_[← Repository README](../README.md) · [The method](./method.md)_

Two ways in, both landing at the same place — the skills drive the process
either way.

## Option A — install the plugin (recommended)

Works on any Claude Code project, existing or new:

```shell
/plugin marketplace add roanboc/archreator
/plugin install archreator@archreator
```

Then just say what you want to model. The `core-project-bootstrap` skill
takes it from there: it asks what the project is, picks a modeling depth,
tells you which one it picked, and writes the scaffold into your
repository.

**The plugin ships two things.** The skills — which do not touch your files
until you ask them to — and the scaffold under
[`.claude/templates/`](../.claude/templates/README.md), which `core-project-bootstrap`
copies into your project. Nothing else lands.

## Option B — clone the scaffold directly

Copy [`.claude/templates/`](../.claude/templates/README.md) into a new repository. It holds:

- `CLAUDE.md` and `README.md` — placeholders you'll fill in when the
  bootstrap skill runs
- `architecture/` — layer READMEs for the six layers, plus `scope/` and
  `decisions/`
- `scripts/` — the two validators, run before every push

Then follow the bootstrap checklist by hand, or install the plugin and let
the skill do it.

## Keeping a project in sync with the method

Three things ship in this repo with different lifecycles, and only one of
them stays in sync automatically:

- **The skills**, at `.claude/skills/*/`, come with the plugin and update
  when you run `/plugin update archreator@archreator`.
- **The scaffold**, at `.claude/templates/`, is copied *once* into your project by
  `core-project-bootstrap`. It does not update afterwards, because a
  scaffold that changed under a project would rewrite documents the
  Requester already approved.
- **The scaffold's own scripts** in `.claude/templates/scripts/` land in your
  project's `scripts/`. They are the same on both sides; if the method's
  validators change, copy the updated files across.

If a scaffold change matters enough to backport (a rule that would
retroactively affect an existing model), it becomes an initiative in your
project like any other: assessed, approved at Gate 2, and applied by hand.

## Reading order

- Understand what changes: [`docs/method.md`](./method.md)
- See what each skill is for: [`docs/skills.md`](./skills.md)
- See it applied to a real organization:
  [`architecture-archreator`](https://github.com/roanboc/architecture-archreator)

## Contributing back

Improvements to the method (a new skill, a change to an existing one, a
rule refinement) are welcome. See [`CONTRIBUTING.md`](../CONTRIBUTING.md)
in the root — the method itself governs how it evolves, so a proposal runs
through the same gates it makes you run through.
