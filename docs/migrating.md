# Crossing to 0.2 — for a project on the 0.1 method

_[← Repository README](../README.md) · [Adopting archreator](./adopting.md)_

A new project needs none of this: `establish-project` emits the current
scaffold and nothing here applies. This page is for a repository that adopted
the method before 0.2 — it holds the old scripts, the empty layer folders and
the four numbered gates — and says what changes, what stays, and why the
stays are deliberate.

The plugin itself updates the ordinary way — see
[keeping a project in sync](./adopting.md#keeping-a-project-in-sync-with-the-method).
Everything below is about the project's own files.

## The gates: four numbers become three names

| It was | It is now | What changed |
| ------ | --------- | ------------ |
| Gate 0 — Business model | **Direction**, first sitting | Same approval, same order: the canvases before anything is derived |
| Gate 1 — Strategy | **Direction**, second sitting | One gate granted in two sittings, two rows in the Approvals table |
| Gate 2 — Business | **Understanding** | Unchanged in substance: strategy, business and information before any code |
| Gate 3 — Solution design | **Design** | Still the opt-in offered at Understanding |

Two vocabularies will coexist in an old project, and that is correct:

- **Merged scope documents are never rewritten**, so every Approvals table
  that says `Gate 2 — Negocio` keeps saying it. A frozen document quoting a
  retired vocabulary is history, not drift.
- **Living documents sweep once** — `AGENTS.md`, the architecture front door,
  the layer READMEs' gate mentions — in one ordinary change.
- **The front door carries the correspondence**, one line near the top of
  `architecture/README.md` — beside the stereotype table, where a translated
  model keeps one — so a reader meeting both vocabularies can map them:
  Direction = Gates 0 and 1, Understanding = Gate 2, Design = Gate 3.

**Gate names translate like stereotypes do.** A Spanish model that wrote
`Compuerta 0` writes «Dirección», «Entendimiento» and «Diseño», with the
English names in the same correspondence line — `document-style` § Language.
The validators never read the words beside a status glyph, so a translated
`● Validado en Dirección` passes exactly as the English form does.

## The scripts: readers move to the plugin, validators stay

Delete from the project's `scripts/`: `build_model.py`, `query_model.py`,
`neighbourhood.sql`, `build_brief.py`, `build_docs.py`, `export_pdf.py`.
Their replacements — `model.py` (trace, coverage, inventory, export, portal)
and `build_brief.py` — live in the plugin and read the project through
`--project .`, importing the project's own parse.

Take the 0.2 copies of what stays: `check_links.py`, `check_model.py`,
`model_graph.py`, `element-prefixes.json`, and the scripts `README.md`. The
validators still run offline with no plugin installed; only the reading
tools require the plugin to be present.

**Why the projection went.** The old `query_model.py` and `build_brief.py`
rebuilt the SQLite projection only when `.model/model.db` was absent; an
existing file was trusted with no freshness check. Verified on the largest
real model on this method: rename an element and `trace` serves the old name
with no warning, add one and it answers "no such element", and the brief
stamps a revision hash implying a currency the content does not have. The fix
is not a smarter cache but none: a full parse of that model takes well under
a second.

Housekeeping that follows: keep `.model/` in `.gitignore` only if `model.py
export` is used, add `.archreator/`, and delete any lingering
`.model/model.db` — nothing reads it any more, and while the old scripts
remain it is exactly the stale answer the paragraph above describes. A
workflow that ran `build_docs.py` (a Pages publish, for instance) must be
retired or rewritten around `model.py portal`; the checks workflow is
untouched.

## What an existing project deliberately keeps

- **Materialized layer folders stay.** The status table that replaces the
  empty tree is how a *new* project starts. In an old one the layer READMEs
  are live link targets — from frozen scope documents above all, which are
  never rewritten — so deleting the folders breaks documents the method
  forbids editing. Keep them; the front door's status column already says
  what each layer holds.
- **A portal or PDF pipeline the project built stays a project-local tool.**
  The method no longer ships one: the stock portal is `model.py --project .
  portal`, and there is no PDF export any more. A project that delivers a
  scoped PDF to its business readers — a real and reasonable deliverable —
  keeps its own copy of the old tooling, owned by the project, with the
  costs owned too: it depends on the deleted staging scripts, so the fork
  keeps both, and the method will not maintain them.
- **Every element, identifier, status glyph and skill name survives.** All
  eighteen skills keep their names; the ○ / ◐ / ● discipline, the prefix
  registry and the relationship tables are unchanged. Nothing in a model's
  content needs to move.
