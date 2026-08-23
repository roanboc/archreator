# \<project-name\>

<!--
  TEMPLATE — `establish-project` replaces this whole file with the project's
  own front door. Keep it short: what this is, who it's for, and where the
  model lives. The completion check looks for the `<placeholder>` marker
  below, so remove it once the real content is written.
-->

**\<placeholder> — one sentence saying what this project is and who it serves.**

## The model

This project's architecture lives in [`architecture/`](./architecture/README.md),
as numbered ArchiMate layers. Start there to understand what the project
does and how its pieces relate.

- [`architecture/`](./architecture/README.md) — the layered model, current state
- [`architecture/scope/`](./architecture/scope/README.md) — one document per initiative, with its approval gates
- [`architecture/decisions/`](./architecture/decisions/README.md) — consequential calls smaller than an initiative

Not a repository person? `python3 scripts/build_docs.py` renders the same
documents as a searchable website and `python3 scripts/export_pdf.py` as a
single PDF — both built from the Markdown, which stays the model.

## How changes are made

Requirements are aligned through the model and approved at explicit gates
before anything is built. [`AGENTS.md`](./AGENTS.md) states the rule and the
declared modeling depth, [`CONTRIBUTING.md`](./CONTRIBUTING.md) names who
grants those gates, and the `align-change-through-layers` skill runs the process.

## Built with

[archreator](https://github.com/roanboc/archreator) — an enterprise
architecture method that lives in git as markdown, with humans owning the
strategy and approving at gates, and AI agents doing the modeling and the
building in between.
