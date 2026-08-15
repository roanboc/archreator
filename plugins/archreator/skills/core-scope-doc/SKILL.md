---
name: core-scope-doc
description: Use when creating or updating a project scope document in architecture/scope/ — one per initiative, drafted before the pre-implementation gate as step 3 of the core-architecture-first-change process, and the durable record of gate approvals.
---

# Writing a scope document

One file per initiative in `architecture/scope/`, named `<n>_<kebab-case-name>.md`
where `<n>` is the next number in the chronological sequence (check the
index table in `architecture/scope/README.md`, and add the new document to it).

## Template

```markdown
# Project Scope — <Initiative Name>

_[← Scope index](./README.md) · [EA home](../ea/README.md)_

**ArchiMate viewpoint:** Implementation & Migration.
**Delivered as:** <branch and/or PR reference>.

<One paragraph: what this initiative changes and why now.>

## EA alignment (assessed top-down before implementing)

| Layer         | Impact                                              |
| ------------- | ---------------------------------------------------- |
| 0_business-design | <canvases added/changed — or "not used" for an application project> |
| 1_strategy    | <new/changed goals, drivers — or "no change" + why> |
| 2_business    | <services, processes, rules, glossary>              |
| 3_information | <data objects, flows, storage, classification>      |
| 4_application | <services, components, ports>                       |
| 5_technology  | <runtimes, build, CI, hosting>                      |

## Approvals

| Gate                     | Approved by | Date         | What was approved                          |
| ------------------------ | ----------- | ------------ | ------------------------------------------- |
| Gate 0 — Business model  | <Requester> | <YYYY-MM-DD> | <the canvases — or "N/A — <why>">          |
| Gate 1 — Strategy        | <Requester> | <YYYY-MM-DD> | <the strategy layer — or "N/A — <why>">    |
| Gate 2 — Business        | <Requester> | <YYYY-MM-DD> | <the docs/sections presented at the gate>  |
| Gate 3 — Solution design | <Requester> | <YYYY-MM-DD> | <the solution design — or "N/A — not requested"> |

## Plateaus

| Plateau                | State                     |
| ----------------------- | ------------------------- |
| **Baseline** (before)  | <state before the change> |
| **Target** (delivered) | <state after the change>  |

## Work packages and deliverables

### WP1 — <name>

- **Deliverables:** <files, modules, docs — concrete artifacts>
- **Outcome:** <the capability gained>

## In scope / out of scope

| In scope | Out of scope (gaps, candidate future work) |
| -------- | ------------------------------------------- |
| …        | …                                           |

## Gap notes

- <Each out-of-scope item that leaves a real gap: what closing it would
  take, and what makes it easy or hard.>

## Open questions

- <Only if there are any: adopted interpretations that the product owner
  or stakeholders still need to confirm, each linked to the document where
  the interpretation was applied.>
```

## Rules

- **Every layer gets a verdict** in the EA-alignment table, including
  explicit "no change" — silence is not a decision.
- **Every gate gets a row, including the ones that didn't apply.** Which
  gate applies to which initiative is defined in exactly one place —
  `core-architecture-first-change` § The gates — and the shortest form of it is:
  **Gate 2 applies to every initiative that changes documented behavior,
  which is every initiative that will produce code; a docs-only initiative
  passes Gate 0 and/or Gate 1 instead.** A gate that didn't apply is written
  `N/A — <why>` rather than deleted, so a reader can tell a skipped gate
  from a forgotten one. An approval that isn't recorded didn't happen; a
  scope document is a historical record, so the table shows who accepted
  what, durably. **"What was approved" names the documents that were put in
  front of the Requester**, not the topic in the abstract — the gate
  presentation links them in full (`core-architecture-first-change` § Show the Requester
  what they are approving), and the row is what says which ones they were.
- **Deliverables are concrete artifacts** (file paths, page/screen names),
  never vague ("improved UX").
- **The consolidation record lives here, not in the layer documents.** How
  many elements each catalogue ended up with, what was merged into what, and
  why — that is a modeling decision the Requester approves, so it belongs in
  this document and in the gate presentation drawn from it. An architecture
  document that also states it is a second copy of the fact, and describes its
  own construction rather than its subject
  (`core-architecture-doc-style` § What the document contains).
- **Out of scope is as important as in scope**: it is where the next
  initiative's backlog lives. Pair each meaningful exclusion with a gap
  note.
- A merged initiative's scope document is a **historical record** — do not
  rewrite it later; follow-up work gets a new numbered document.
- **The record is what it says, not where its links point.** If a later
  change renames or moves a file, update the *link targets* in merged scope
  documents so they still resolve, and leave every word alone — including
  link text, which was accurate when written. A dangling link makes the
  record less usable without making it more truthful, so repairing the path
  preserves the history rather than rewriting it. Anything that changes a
  claim — a deliverable, a verdict, an approval — is still forbidden.
- Optionally include a small Mermaid plateau diagram using the
  `implementation` classDef from the EA notation conventions
  (`architecture/README.md`).

## Optional: the open-questions log

Projects with an external stakeholder or governing body who cannot be
consulted synchronously (a board, a client, a compliance owner) benefit
from a single living index, `architecture/scope/open-questions.md`, listing every
adopted interpretation across all scope documents that still needs
confirmation. If the project keeps one:

- **Every new (or resolved) "Open questions" row is mirrored there** in the
  same change — it is the consolidated index reviewed between initiatives
  so questions don't get lost in old scope documents.
- Step 0 of `core-architecture-first-change` reads it before starting a new change.

Projects without an external stakeholder to reconcile with can skip this
file entirely — the "Open questions" section within each scope document is
enough.
