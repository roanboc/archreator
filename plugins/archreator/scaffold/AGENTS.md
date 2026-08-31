# AGENTS.md

**This project has not been bootstrapped yet.** It is a fresh copy of the
[archreator](./README.md) template: the method works, the model is empty.
Run the `establish-project` skill before anything else — it names the
project, declares the modeling depth, fills in this file, and hands off to
discovery. Nothing arrives that the project does not use, so there is
nothing to prune. Everything in this file below the rule is a
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

## Who decides

Every change moves through three roles. Nothing here assumes a human fills the
middle one — an AI agent and a person follow the same steps, in the same order,
against the same documents.

| Role | Who | Does |
| ---- | --- | ---- |
| **Requester** | \<who owns the product> | Says what should change — a requirement or a problem, not a diff. **Grants the gate approvals** before any code is written |
| **Agent** | An AI agent (or a person) | Works the change through the layers, stops at each gate for the Requester's approval, writes the scope document, implements, and opens a pull request |
| **Reviewer** | \<who reviews and merges> | Reviews and merges. Nothing ships without a human approving it |

An approval that isn't recorded didn't happen: every gate is written into the
scope document's Approvals table, with who approved, when, and what was shown.

## Modeling depth

**Declared depth: _not yet declared_** — `establish-project` sets this.

The six layers describe a weekend app and a twenty-business-line company
alike; the depth says how much of them gets filled in and which gates apply
(see [`architecture/README.md`](./architecture/README.md)).
Depth 1 is one application with a light strategy layer; Depth 2 is one
organization; Depth 3 splits the model into domains, one per business line.
It is a starting posture, never a ceiling — deepening or descoping is a
normal initiative, decided by the Requester.

## The skills

Your coding agent surfaces the archreator skills from their `description:`
frontmatter; you don't invoke them by name in normal use. Three kinds: `⚙` a
procedure it runs, `▤` a document it writes, `※` a rulebook it consults.

The catalogue lives with the skills, in the plugin — it is not restated here,
because a copy in every generated project is a copy that goes stale in every
generated project.

## Layout

<!-- Replace with the real source layout once the project has code, e.g.:
- `src/` — ...
- `tests/` — ...
-->

- `architecture/` — what this project knows about itself. Its `README.md` is
  the front door and says, per layer, whether this model owns it, another
  model does, it is out of scope, or it is a named gap. **A folder exists only
  once it holds something**; the skills emit the one they need when they need
  it, so an empty directory is never a substitute for saying what is missing.
- **Every document that defines an element says how far it has been
  validated**, with `○` not started, `◐` a draft catalogue of things somebody
  said exist, or `●` validated at a named gate on a named date. A draft
  catalogue is not an architecture draft and must never be read as one;
  `scripts/check_model.py` fails a defining document that declares nothing.
- [`scripts/`](./scripts/README.md) — the two validators, run before every
  push. Everything else the method can do runs from the plugin rather than
  from a copy in here.

## Commands

<!-- Replace with the project's real commands once they exist, e.g.:
```bash
npm run lint
npm run typecheck
npm test
```
All of them must be green before pushing; CI runs the same.
-->

```bash
python3 scripts/check_links.py    # relative links and HTML anchors resolve
python3 scripts/check_model.py    # element-ID references resolve
```

Both must be green before pushing. They need nothing but Python — no network,
no plugin installed — which is the point: this project can check itself.

Everything else the method can do runs from the plugin against this project,
so there is one copy of each tool rather than one per project:

```bash
model.py --project . trace BSVC1     # what a change here would touch
model.py --project . coverage        # what names no realizing artifact
model.py --project . portal          # the model as a website, for a reader outside the repo
build_brief.py --project . --element BSVC1 --focus impact
```

Everything they generate lands under `.archreator/`, which is gitignored.
Delete it and nothing is lost.

## Conventions

<!-- Project-specific conventions go here as they're established —
     glossary location, code language, naming rules, single point of
     enforcement for business rules, etc. Keep this section short; link to
     the EA docs for anything that has a canonical home there instead of
     restating it. -->

- Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, …).
- Documentation language: **English** (change during bootstrap; see
  `document-style`).
