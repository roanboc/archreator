# AGENTS.md

**This project has not been bootstrapped yet.** It is a fresh copy of the
[archreator](./README.md) template: the method works, the model is empty.
Run the `establish-project` skill before anything else — it names the
project, declares the modeling depth, prunes what wasn't inherited, and
hands off to discovery. Everything in this file below the rule is a
placeholder it will replace.

<!--
  TEMPLATE — establish-project replaces this comment block, the line above,
  and the placeholders below. Keep "The rule that governs everything else"
  and "Modeling depth"; they are the whole point of this template.
-->

## The rule that governs everything else

**Strategy and business architecture are validated before any other layer,
and the Requester approves at explicit gates before development.** A change
in requirements is never coded directly: align it through the numbered EA
layers (`architecture/1_strategy` → … → `5_technology`), stop at the gates for
the Requester's approval, record it in a scope document (`architecture/scope/`),
then implement. Pure bug fixes that change no documented behavior skip the
alignment and the gates, but still keep the docs true.

## Modeling depth

**Declared depth: _not yet declared_** — `establish-project` sets this.

The six layers describe a weekend app and a twenty-business-line company
alike; the depth says how much of them gets filled in and which gates apply
(see [`architecture/README.md` § Modeling depth](./architecture/README.md#modeling-depth)).
Depth 1 is one application with a light strategy layer; Depth 2 is one
organization; Depth 3 splits the model into [domains](./architecture/domains/README.md).
It is a starting posture, never a ceiling — deepening or descoping is a
normal initiative, decided by the Requester.

## The skills

Your coding agent surfaces these from their `description:` frontmatter; you
don't invoke them by name in normal use. They are listed in the order they are
used in, with the four rulebooks — consulted rather than run — at the end.

| Skill | Reach for it when |
| ----- | ----------------- |
| `establish-project` | A project from the template hasn't been set up yet — start here |
| `discover-business-model` | The subject is an organization: canvases first (Gate 0), strategy derived from them |
| `discover-strategy` | The strategy is unfilled or the change shifts it (Gate 1) |
| `model-domains` | The organization is large enough to split into business lines, or a change crosses a domain boundary |
| `align-change-through-layers` | Any requirement change. **The spine** — defines the gates and the order |
| `write-scope-document` | Writing the initiative's scope document; its Approvals table is the durable record of the gates |
| `shard-stories` | A work package is too large to finish in one sitting |
| `write-pr-description` | Opening or updating a pull request — the body covers the whole branch, not the latest commit |
| `restate-current-state` | The model has accumulated history — shipped "Pending"s, superseded elements, resolved questions — and no longer reads as a description of today |
| `record-decision` | One consequential call smaller than an initiative — most often an AI actor's autonomy level |
| `run-retrospective` | An initiative or engagement just finished — capture what the method didn't cover before it evaporates |
| `document-style` | Writing or editing any document at all — the language, what it may contain, and how it links |
| `architecture-document-style` | Editing anything under `architecture/` — numbering, element IDs, tiers, ArchiMate-on-Mermaid, actors, the grounding rule |
| `process-and-capability-levels` | An organization's processes or capabilities need shaping — the four macro categories, the levels, and how far down to go |
| `stack-selection` | No technology stack chosen yet on a small application |

## Layout

<!-- Replace with the real source layout once the project has code, e.g.:
- `src/` — ...
- `tests/` — ...
-->

- `architecture/` — everything architectural: the numbered ArchiMate layers
  describing the current state, `architecture/domains/` (Depth 3 only),
  `architecture/scope/` — one document per initiative — and
  `architecture/decisions/` for calls smaller than an initiative.
- `CONTRIBUTING.md` — who the Requester, Agent and Reviewer are, and the
  development workflow.
- [`scripts/`](./scripts/README.md) — the two validators, run before every
  push, and the three tools: the projection, the documentation portal and the
  PDF export.
- `mkdocs.yml` and `overrides/` — how the model is published as a website.
  Everything they produce lands in `.docs/`, which is derived and gitignored.

## Commands

<!-- Replace with the project's real commands once they exist, e.g.:
```bash
npm run lint
npm run typecheck
npm test
npm run build
```
All of them must be green before pushing; CI runs the same.
-->

```bash
python3 scripts/check_links.py    # relative links and HTML anchors resolve
python3 scripts/check_model.py    # element-ID references resolve
```

Both must be green before pushing. Three tools sit beside them, none of them a
gate:

```bash
python3 scripts/build_model.py    # the model as nodes and edges, in .model/
python3 scripts/build_docs.py     # the model as a website, in .docs/site/
python3 scripts/export_pdf.py     # the model as one PDF, in .docs/
```

`build_model.py` is for a consumer that queries the model; the other two are
for a reader who is not in this repository. All three are regenerated from the
Markdown under `architecture/`, which stays the source of truth.

## Conventions

<!-- Project-specific conventions go here as they're established —
     glossary location, code language, naming rules, single point of
     enforcement for business rules, etc. Keep this section short; link to
     the EA docs for anything that has a canonical home there instead of
     restating it. -->

- Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, …).
- Documentation language: **English** (change during bootstrap; see
  `document-style`).
