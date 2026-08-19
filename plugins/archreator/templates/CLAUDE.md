# CLAUDE.md

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

Claude Code surfaces these from their `description:` frontmatter; you don't
invoke them by name in normal use. They are listed in the order they are
used in, with the three rulebooks — consulted rather than run — at the end.

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
| `architecture-document-style` | Editing anything under `architecture/` — numbering, element IDs, ArchiMate-on-Mermaid, the grounding rule — and writing any other document in the repository, for what it may contain |
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
- `scripts/` — the two validators, run before every push.

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

Both must be green before pushing.

## Conventions

<!-- Project-specific conventions go here as they're established —
     glossary location, code language, naming rules, single point of
     enforcement for business rules, etc. Keep this section short; link to
     the EA docs for anything that has a canonical home there instead of
     restating it. -->

- Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, …).
- Documentation language: **English** (change during bootstrap; see
  `architecture-document-style`).
