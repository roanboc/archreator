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

- **Fourteen Claude Code skills** — the method itself, under
  [`plugins/archreator/skills/`](./plugins/archreator/skills/README.md), each
  named for the process it realizes.
- **A scaffold** — the empty project a new adopter starts from, at
  [`plugins/archreator/templates/`](./plugins/archreator/templates/README.md), copied by the
  `establish-project` skill.
- **A plugin package** — the manifests at
  [`plugins/archreator/.claude-plugin/plugin.json`](./plugins/archreator/.claude-plugin/plugin.json)
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

Then just say what you want to model — the `establish-project` skill
takes it from there.

Prefer to clone the scaffold instead of installing? Both routes, and what
each one lands in your project, are in
[`docs/adopting.md`](./docs/adopting.md).

## Where to go from here

| To understand | Read |
| ------------- | ---- |
| **What the method does and how** | [`docs/method.md`](./docs/method.md) — the process, the layers, the loop |
| **The method as a levelled process model** | [`docs/process/`](./docs/process/README.md) — the macro map, a SIPOC per process, and which skill realizes each |
| **The format every skill follows** | [`docs/skill-format.md`](./docs/skill-format.md) — frontmatter, the fixed sections, and the glyphs that mark them |
| **Which standards it rests on** | [`docs/standards-alignment.md`](./docs/standards-alignment.md) — every coined term, the established name behind it, and where the method is genuinely its own |
| **What each skill is for** | [`plugins/archreator/skills/README.md`](./plugins/archreator/skills/README.md) — the catalogue, in the order they are used |
| **How to adopt it in your own project** | [`docs/adopting.md`](./docs/adopting.md) |
| **What a filled-in model looks like** | [`architecture-archreator`](https://github.com/roanboc/architecture-archreator) |
| **How to contribute to this repository** | [`CONTRIBUTING.md`](./CONTRIBUTING.md) |
