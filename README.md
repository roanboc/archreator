# archreator

**Model how your organization works, so AI can help run it.** archreator
turns a company — or a single application — into a living architecture that
lives in git as markdown: who you serve, what you offer, who does what, and
which system realizes each piece. Humans own the strategy and approve at
explicit gates; AI agents do the modeling and the building in between.

Its distinguishing bet: **an AI is modeled as a member of the organization,
not a tool used by it.** Every actor carries a kind (human, AI, or hybrid),
and every AI actor carries an autonomy level, concrete decision rights, and
a named escalation path.

> 📖 **See it in use.** The worked models — an organization, the method
> itself, the guidance site — live in
> [`architecture-archreator`](https://github.com/roanboc/architecture-archreator).
> This repository holds the method; that one holds real examples of it
> applied.

## What this repository is

- **Fourteen Claude Code skills** — the method itself, grouped by role
  under [`.claude/skills/`](./.claude/skills/README.md).
- **A scaffold** — the empty project a new adopter starts from, at
  [`.claude/templates/`](./.claude/templates/README.md), copied by the
  `core-project-bootstrap` skill.
- **A plugin package** — the manifests at
  [`.claude/.claude-plugin/plugin.json`](./.claude/.claude-plugin/plugin.json)
  and [`.claude-plugin/marketplace.json`](./.claude-plugin/marketplace.json)
  that publish it to the Claude Code plugin marketplace.
- **The docs and the site** — plain-English explanation under
  [`docs/`](./docs/method.md), one-page public site under
  [`site/`](./site/index.html).

No application code. No worked models — those live in the sibling repo.

## Quick start

```shell
/plugin marketplace add roanboc/archreator
/plugin install archreator@archreator
```

Then just say what you want to model. The `core-project-bootstrap` skill
takes it from there: it asks what the project is, picks a modeling depth,
tells you which one it picked, and writes the scaffold into your
repository.

Prefer a fresh repo? Clone the scaffold from
[`.claude/templates/`](./.claude/templates/README.md) into a new project.

## Where to go from here

| To understand | Read |
| ------------- | ---- |
| **What the method does and how** | [`docs/method.md`](./docs/method.md) — the process, the layers, the loop |
| **What each skill is for** | [`docs/skills.md`](./docs/skills.md) · [`.claude/skills/README.md`](./.claude/skills/README.md) |
| **How to adopt it in your own project** | [`docs/adopting.md`](./docs/adopting.md) |
| **What a filled-in model looks like** | [`architecture-archreator`](https://github.com/roanboc/architecture-archreator) |
| **How to contribute to this repository** | [`CONTRIBUTING.md`](./CONTRIBUTING.md) |
