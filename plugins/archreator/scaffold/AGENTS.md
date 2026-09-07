# AGENTS.md

**This project has not been bootstrapped yet.** It is a fresh copy of the
[archreator](./README.md) template: the method works, the model is empty.
Run `/archreator:establish-project` before anything else — it names the
project, declares the modeling depth, fills in this file, and hands off to
discovery. Everything in this file below the rule is a placeholder it will
replace.

<!--
  TEMPLATE — establish-project replaces this comment block, the line above,
  and the placeholders below. Keep "The rule that governs everything else"
  and "Modeling depth"; they are the whole point of this template.
-->

## The rule that governs everything else

**Strategy and business architecture are validated before any other layer,
and the Requester approves at explicit gates before development.** A change
to what the model claims — an element added, removed or re-related, a rule it
states contradicted — is never coded directly: align it through the numbered
EA layers (`architecture/1_strategy` → … → `5_technology`), stop at the gates
for the Requester's approval, record it in a scope document
(`architecture/scope/`), then implement. A change inside an element the model
already names — a screen, a filter, a format, a defect — is coded directly and
documents nothing; one that only keeps a row true edits the row in the same
commit.

## Who decides

Every change moves through three roles. Nothing here assumes a human fills the
middle one — an AI agent and a person follow the same steps against the same
documents.

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
alike; the depth says how much of them gets filled in and which gates apply —
the ladder is in [`architecture/README.md`](./architecture/README.md) and is
not restated here. It is a starting posture, never a ceiling: deepening or
descoping is a normal initiative, decided by the Requester.

## The skills

Three archreator skills surface on their own — `align-change-through-layers`
when a requirement arrives, `architecture-document-style` and `document-style`
when a document is edited. Every other skill is invoked by name,
`/archreator:<skill>`, and typing `/archreator:` lists them. Three kinds: `⚙`
a procedure it runs, `▤` a document it writes, `※` a rulebook it consults.

The catalogue lives with the skills, in the plugin, and is not restated here.

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
  `scripts/check_model.py` fails a defining document that declares nothing,
  and one that carries no view or whose first view comes after its first
  table. **Each section opens with its own diagram and its own tables follow
  it** — never every diagram stacked at the top with the prose underneath.
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
no plugin installed — so this project can check itself.

Everything else the method can do runs from the plugin against this project,
so there is one copy of each tool rather than one per project:

```bash
model.py --project . trace BSVC1     # what a change here would touch
model.py --project . coverage        # what names no realizing artifact
model.py --project . names src/x.py  # which elements name this path — is a change here inside the model?
model.py --project . health          # how much is validated, and whether a granted gate moved a status line
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
