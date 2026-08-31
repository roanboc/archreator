---
name: process-and-capability-levels
description: Rulebook — consult when modeling an organization's business processes or capabilities — building a process map, deciding how far to decompose, drafting a capability model, or numbering leveled elements. Covers the four macro process categories (strategic, operational, support, evaluation), what each level means and how its elements are described, the hierarchical identifiers that carry the level (`BPROC7`, `BPROC7.2`, `BPROC7.2.1`), seeding a capability map from an industry reference model, and the breadth-first depth-on-pain rule that says which branches to detail and which to leave alone. Not needed for a single application, which has no process map of its own.
metadata:
  archreator:
    kind: rulebook
    gates: none
---

# ※ Process and capability levels

An organization's processes and capabilities are the two catalogues that grow
without limit. Every other layer is bounded by something real — the products
that exist, the systems that run, the people employed — but "decompose the
processes" has no natural floor, and an agent that finds none will keep going.
The result is a model that is correct, complete, and read by nobody.

`architecture-document-style` governs how these documents are written. This
governs how they are **shaped**.

## ⊕ When to use this

| The situation | What it looks like |
| ------------- | ------------------ |
| Modeling an organization | The subject is Depth 2 or above and its processes or capabilities are being drafted or revised |
| A catalogue has outgrown a reader | It exists, and nobody can hold it |
| Reached from a procedure | `align-change-through-layers` Step 2 at Depth 2+, `discover-strategy` theme 4, or `discover-business-model` at the handoff |

## ⊖ When not to

| The situation | Use instead |
| ------------- | ----------- |
| The subject is a single application | Nothing. It has the processes its enterprise tier owns, cited and not restated, plus whatever its own delivery requires. Do not build a four-category map for one application |
| The question is how to write the document | `architecture-document-style` — that governs form, this governs shape |

## ⌖ Where this sits

**Realizes no process.** It is a rule the discovery and alignment procedures
comply with, reached for while they run rather than run on its own.

## ※ Rules

### Breadth first, depth on pain

**Levels 1 and 2 are complete across the whole organization; level 3 and below
exist only where a named pain justifies them.**

The name is not a figure of speech — it is an element ID. A level-3
decomposition cites the `PAIN` on the value proposition canvas it serves, or
the `ASM` or `DRV` that pain became. A branch with no such citation is not
detailed, and **says so in the focus table** rather than trailing off.

Horizontal completeness is what makes a model trustworthy: a reader who sees
the whole map knows nothing is hidden. Vertical completeness is what makes it
unreadable. Only the second is optional, so only the second gets cut. This is
`document-style` § Consolidate before you enumerate applied to
depth instead of to count.
### What is here, and what is one file away

**This page holds the judgement — how far to decompose, and what a process is
as against a capability.** The lookup content is one file away, read when you
have already decided a level is needed.

| Read | When |
| ---- | ---- |
| [`references/levels-and-descriptions.md`](./references/levels-and-descriptions.md) | The four macro categories, what each level means, and the minimum a description carries |
| [`references/starting-and-filing.md`](./references/starting-and-filing.md) | Starting a catalogue from nothing, the focus table, and which file a level belongs in |

### Processes are verbs; capabilities are nouns

A process is work the organization *does*, in sequence, with a trigger. A
capability is what it *is able to do*, with no sequence and no trigger —
"Claims adjudication", not "Adjudicate a claim". A capability map whose entries
all start with a verb is a process list wearing the wrong label, and it is the
most common failure of this document.

| Level | ID | It is | Usual count |
| ----- | -- | ----- | ----------- |
| **1 — Capability area** | `CAP1` | What a decision gets taken at — "does this initiative strengthen X?" is answerable | 6–12 for a whole organization |
| **2 — Capability** | `CAP1.2` | A distinct ability, realized by people, systems and information | 3–8 per area |
| **3 — Sub-capability** | `CAP1.2.3` | Only where a pain justifies it | — |

Only the leaves name a realizing artifact. An area is realized by its parts,
and asking it to point at something real is the grounding rule applied one
level too high.

## ✎ Worked example

> A consultancy's operational band derives cleanly from the value stream, and
> the Evaluation band comes back empty. That is reported as a finding — the
> organization has documented how it delivers and not how it improves — rather
> than left blank. Capabilities are seeded from a named cross-industry
> framework, taken back one area at a time, and the two areas the Requester
> adds are the ones the reference could not have known. One branch reaches
> level 3, citing `PAIN2`; the focus table gives the other seven a dash.

## ⚠ Anti-patterns

- Decomposing every branch to level 3 because the model looks incomplete.
- A capability map whose entries start with verbs.
- Filling a catalogue from a reference model and presenting it as the
  organization's own.
- Reporting an empty band as a blank rather than a finding.
- Giving a band an ID, when nothing realizes it.
- A focus table missing the branches that were *not* detailed — a reader
  cannot tell a decision from an oversight.
- Building a four-category process map for a single application.

## ☑ Done when

The catalogue these rules shaped is finished when:

- Every band of the level-1 map is either populated or reported empty.
- Levels 1 and 2 are complete across the whole subject.
- Every level-3 document cites the pain that justifies it.
- The focus table covers every level-2 element, including the undetailed ones.
- Every identifier extends its parent's, and no table carries a parent column
  beside it.
- Each level-2 process names a supplier and a customer, not just an input and
  an output.
- Each process carries a purpose, a trigger, an output and an owner; each
  capability is a noun, and its leaves name what realizes them.
- The reference model used to seed the capability map is named in the
  document, and nothing it proposed sits unconfirmed without being marked.
