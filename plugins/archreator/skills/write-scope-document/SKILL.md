---
name: write-scope-document
description: Document — write one when creating or updating a project scope document in architecture/scope/ — one per initiative, drafted before the pre-implementation gate as step 3 of the align-change-through-layers process, and the durable record of gate approvals.
metadata:
  archreator:
    kind: document-template
    realizes_process: BPROC2.1
    gates: none
---

# ▤ Write a scope document

One document per initiative, and the place its gate approvals are recorded.
An **architecture definition** narrowed to a single change: what it alters,
which layers it touches, who approved it, and what it deliberately left out.

## ⊕ When to use this

| The situation | What it looks like |
| ------------- | ------------------ |
| An initiative starts | Step 3 of `align-change-through-layers`, before the gate that approves it |
| Discovery starts | `discover-business-model` or `discover-strategy` needs somewhere to record Direction |
| An initiative moves | The work diverged from the plan, and the document has to stay true to what shipped |

## ⊖ When not to

| The situation | Use instead |
| ------------- | ----------- |
| One consequential call, no elements changed | `record-decision` |
| A pure bug fix with no documented behavior change | Nothing — say "no scope document" in the pull request, with the root cause |
| The document is merged and a claim in it is now wrong | A new numbered document. A merged record is history |

## ⌖ Where this sits

Realizes `BPROC2.1`. It carries no gate of its own: it is the artifact the
gates are recorded *in*, and so it is created **before** the gate.

```mermaid
flowchart LR
  init(["An initiative, or a discovery"])
  doc[/"architecture/scope/n_name.md"/]
  idx[/"scope/README.md — the index"/]
  g{{"❖ The gate it records"}}
  pr(["The pull request that cites it"])

  init --> doc --> idx
  doc --> g -->|approved| doc
  doc --> pr

  classDef business fill:#fffbb5,stroke:#c8c04a,color:#333
  classDef implementation fill:#ffd6d6,stroke:#d99b9b,color:#333
  classDef artifact fill:#eef2f7,stroke:#9fb0c4,color:#333
  class init,pr business
  class g implementation
  class doc,idx artifact
```

## ▤ Template

Named `<n>_<kebab-case-name>.md`, where `<n>` is the next number in the
chronological sequence — check the index in `architecture/scope/README.md`
(the first initiative creates the folder from the plugin's
`assets/layers/scope/`, which carries the index), and add the new document to
it in the same change.

```markdown
# Project Scope — <Initiative Name>

_[← Scope index](./README.md) · [Model home](../README.md)_

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

| Gate | Approved by | Date | What was approved |
| ---- | ----------- | ---- | ----------------- |
| Understanding | <Requester> | <YYYY-MM-DD> | <the documents and sections presented> |

<!--
  One row per gate this initiative was granted, plus one row for any
  unscheduled stop, with the reason in place of a gate name: `Authorization`
  or `Material uncertainty`. A gate that was not granted gets no row.

  Direction, where the subject is an organization, is two rows: the canvases,
  then the strategy derived from them.
-->

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
```

## ※ Rules

- **Every layer gets a verdict**, including an explicit "no change". Silence
  is not a decision.
- **Every granted gate gets a row, and nothing else does.** An Approvals table
  records what happened, never a census of what did not. Which gate applies is
  defined in exactly one place — `align-change-through-layers` § The gates.
  **An approval that isn't recorded didn't happen.**
- **A granted gate promotes the documents it covered**
  (`architecture-document-style` § Document status). Recording the approval is
  half of it; a row without the status lines leaves the model claiming nothing
  was approved.
- **An interpretation the agent adopted is recorded where it applies**, never
  in a register of pending questions: the affected row's `Source` cell reads
  `adopted — <the call>`, and the document stays `◐` —
  `align-change-through-layers` § Ask only what blocks the work now.
- **"What was approved" names the documents put in front of the Requester**,
  not the topic in the abstract. The gate presentation links them in full
  (`align-change-through-layers` § Show the Requester what they are approving);
  the row is what says which ones they were.
- **Deliverables are concrete artifacts** — file paths, page or screen names —
  never "improved UX".
- **The consolidation record lives here, not in the layer documents.** How
  many elements each catalogue ended up with, what was merged into what, and
  why, is a modeling decision the Requester approves (`document-style` § What
  the document contains).
- **Out of scope is as important as in scope** — it is where the next
  initiative's backlog lives. Pair each meaningful exclusion with a gap note.
- **Where the project keeps a roadmap, gap notes have somewhere to go.** A gap
  note expires with the document it was written in; a row in
  `architecture/6_transition/` does not. Where the initiative closes gaps the
  roadmap already carries, name them here and mark them there in the same
  change — `plan-the-transition` § 6 — Bind the roadmap to the spine holds
  both halves. A project with no roadmap keeps its gap notes and loses nothing.
- **A merged scope document is a historical record.** Follow-up work gets a
  new numbered document.
- **The record is what it says, not where its links point.** When a later
  change moves a file, update the *link targets* in merged documents so they
  still resolve, and leave every word alone — including link text, which was
  accurate when written.
- A small Mermaid plateau diagram is optional, using the `implementation`
  classDef from the notation conventions.

## ✎ Worked example

> A docs-only discovery initiative records Direction as granted, with links to
> the three strategy documents that were shown. Understanding never applied, so
> there is no second row. One row, one approval, and the alignment table above
> it carries the "no change" verdicts for the layers discovery never touched.

## ⚠ Anti-patterns

- Writing a row for a gate that was not granted.
- "What was approved" naming a topic rather than the documents shown.
- Leaving a layer out of the alignment table because nothing changed there.
- Parking an adopted interpretation in a list of questions instead of writing
  it into the row it changed.
- Rewriting a merged document instead of writing the next one.
- Putting the consolidation counts in the layer documents.

## ☑ Done when

- The document is numbered, named and added to the index in the same change.
- Every layer has a verdict, and every granted gate has a row.
- Every document a granted gate covered says `●`, with that gate and that date.
- Anything the Requester provided is filed in `architecture/reference/` and
  indexed there, and the elements derived from it name it.
- Deliverables name artifacts, not intentions.
- Every meaningful exclusion has a gap note.
- Every interpretation the agent adopted reads `adopted — <the call>` in the
  row it changed, in a document still marked `◐`.
