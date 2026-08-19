---
name: process-and-capability-levels
description: Use when modeling an organization's business processes or capabilities — building a process map, deciding how far to decompose, drafting a capability model, or numbering leveled elements. Covers the four macro process categories (strategic, operational, support, evaluation), what each level means and how its elements are described, the hierarchical identifiers that carry the level (`BPROC7`, `BPROC7.2`, `BPROC7.2.1`), seeding a capability map from an industry reference model, and the breadth-first depth-on-pain rule that says which branches to detail and which to leave alone. Not needed for a single application, which has no process map of its own.
---

# Levels, and how far down to go

_Reached from `align-change-through-layers` Step 2 when the project is Depth 2
or above, from `discover-strategy` theme 4, and from
`discover-business-model` at the hand-off. `architecture-document-style` governs
how the documents are written; this governs how they are shaped._

An organization's processes and capabilities are the two catalogues that grow
without limit. Every other layer is bounded by something real — the products
that exist, the systems that run, the people employed — but "decompose the
processes" has no natural floor, and an agent that finds none will keep going.
The result is a model that is correct, complete, and read by nobody.

## The rule everything else serves

**Breadth first, depth on pain. Levels 1 and 2 are complete across the whole
organization; level 3 and below exist only where a named pain justifies them.**

The name is not a figure of speech — it is an element ID. A level-3
decomposition cites the `PAIN` on the value proposition canvas it serves, or
the `ASM` or `DRV` that pain became. A branch with no such citation is not
detailed, and **says so in the focus table** rather than trailing off.

Horizontal completeness is what makes a model trustworthy: a reader who can
see the whole map knows nothing is hidden. Vertical completeness is what makes
it unreadable. Only the second one is optional, so only the second one gets
cut. This is `architecture-document-style` § Consolidate before you enumerate
applied to depth instead of to count, and it is the same instinct as the
modeling-depth ladder — spend the method where the subject is worth it.

## When this applies

- The subject is an **organization** (Depth 2 or above) and its processes or
  capabilities are being modeled or revised.
- A catalogue already exists and has grown past what one reader can hold.

A single application has no process map of its own. It has the processes its
enterprise tier owns, cited and not restated (`RULE11`), plus whatever its own
delivery requires. Do not build a four-category map for one application.

## Processes

### Level 1 is the macro process map, in four categories

Classify every macro process into one of four bands. This is the process map
quality management has used for decades, which matters for a reason beyond
convention: **an organization with a quality system already thinks in these
bands**, and arriving with a different decomposition of work it has already
decomposed spends credibility on nothing. Ask what exists before drawing one.

| Category | Holds | Test — if it stopped tomorrow |
| -------- | ----- | ----------------------------- |
| **Strategic** | Direction and governance: strategy, planning, portfolio, risk, compliance oversight | The organization keeps operating, and starts drifting |
| **Operational** | The value chain the customer pays for, end to end | The customer notices today |
| **Support** | What the rest needs to run: people, finance, procurement, IT, facilities, legal | Everything else degrades within weeks |
| **Evaluation** | Measurement, audit, customer feedback, corrective action, improvement | Nothing breaks, and nothing improves |

**The categories are a classification, not elements.** They get no IDs and no
rows: nothing realizes a band, so the grounding rule would have nothing to
point at. Draw them as subgraphs and carry the band as a column on each
level-1 process.

**The value stream fills exactly one band.** Deriving processes from the value
stream — which is the right way to get the operational band, and the way
`discover-strategy` theme 5 already works — produces nothing for the other
three. That is the categories' main use: they make it possible to notice that
an organization has documented how it delivers and not how it decides, staffs,
or improves. Report an empty band as a finding, not as a blank.

### What each level means

| Level | ID | It is | Named | Usual count |
| ----- | -- | ----- | ----- | ----------- |
| **1 — Macro process** | `BPROC7` | A band's major grouping of work, end to end | Verb + object, or a noun phrase where the organization already has one | 8–15 for a whole organization |
| **2 — Process** | `BPROC7.2` | An end-to-end process with a trigger, a definable output, and one accountable role | Verb + object | 3–8 per macro process |
| **3 — Sub-process** | `BPROC7.2.1` | The ordered steps inside a level-2 process — the first level where a flow diagram says something a list cannot | Verb + object | Only where a pain justifies it |
| **4 — Task** | — | What one person or system does in one sitting | Verb + object | Belongs in a work instruction, not in the model |

Level 4 is named here so it can be refused. When a Requester asks for it, the
answer is that the model stops at 3 and the procedure continues in whatever
the organization uses for work instructions — the EA is not the operating
manual, and the two have different lifecycles.

### The minimum description

A process named without a trigger and an output is a heading. Each level
carries at least:

| Level | Columns beyond ID and name |
| ----- | -------------------------- |
| **1** | Category · purpose (one sentence) · owner · composed of |
| **2** | Purpose · trigger · supplier · input · output · customer · owner role · realized by |
| **3** | The level-2 set, plus the sequence — which is what the diagram carries |

No level carries a parent column: `BPROC7.2` names its parent already, and a
column repeating it is DRY broken inside a row. `composed of` stays, because
it carries the children's **names**, which the identifiers do not.

**Purpose is one sentence saying what this turns into what, and for whom.**
"Manages orders" is a restatement of the name. "Turns a confirmed order into a
delivered shipment for the customer who placed it" is a definition.

**Supplier and customer are named, not implied.** With them the level-2 row is a
SIPOC — supplier, input, process, output, customer — and a SIPOC belongs to *each*
process, never one to the whole map. They cost two columns and they are what turns
a catalogue into a chain: a process whose supplier is nobody is either triggered
from outside the organization or missing a predecessor, and a process whose customer
is nobody produces an output no one consumes. Neither is visible from trigger and
output alone.

Name the neighbouring process by ID where there is one (`BPROC7.2`), and the
external party where there is not (`Requester`, `Regulator`). A chain the reader can
follow by ID is the payoff — and the identifiers already carry the tree, so the
chain and the hierarchy are readable from the same table.

`realized by` is the grounding rule (`architecture-document-style` § Grounding
rule) on the organization track: a process is realized by a team, a role, or a
written procedure — not by a source file. Name that, or mark it Pending.

## Capabilities

### What separates them from processes

**Processes are verbs; capabilities are nouns.** A process is work the
organization *does*, in sequence, with a trigger. A capability is what it *is
able to do*, with no sequence and no trigger — "Claims adjudication", not
"Adjudicate a claim". A capability map whose entries all start with a verb is
a process list wearing the wrong label, and it is the most common failure of
this document.

| Level | ID | It is | Usual count |
| ----- | -- | ----- | ----------- |
| **1 — Capability area** | `CAP1` | What a decision gets taken at — "does this initiative strengthen X?" is answerable | 6–12 for a whole organization |
| **2 — Capability** | `CAP1.2` | A distinct ability, realized by people, systems and information | 3–8 per area |
| **3 — Sub-capability** | `CAP1.2.3` | Only where a pain justifies it | — |

Only the leaves name a realizing artifact. An area is realized by its parts,
and asking it to point at something real is the grounding rule applied one
level too high.

### Start from the industry, then ask

"What must this organization be able to do?" is a question businesses answer
badly — they describe their org chart, or the projects currently running. Turn
recall into recognition:

1. **Name the industry** as precisely as the business actually operates in it,
   and confirm that naming with the Requester before using it.
2. **Name a reference model** for that industry, and write which one into the
   document. Cross-industry and per-industry process classification
   frameworks, banking, telecom, insurance and supply-chain reference models,
   and the IT service-management and governance frameworks all serve; where
   nothing industry-specific exists, a value-chain frame plus the four
   categories is enough to start from.
3. **Draft levels 1 and 2 from it, as a proposal.**
4. **Take it back one area at a time**: confirm, rename, reject, and — the
   question that earns the exercise — *what is missing that a business like
   yours would have?*
5. **Re-word every survivor in the organization's own language.** A reference
   model's vocabulary is a scaffold for the conversation, not the deliverable.

**Cite, never copy.** Name the reference as the source of a proposal; do not
reproduce its content into the model.

### The safeguard

**A reference proposes; it never fills.** Both discovery skills forbid
assuming, and a plausible industry catalogue is exactly the kind of filler
that rule exists to stop — it reads as agreed when nobody agreed it. The
reference changes the *question*, not the *authority*: every element still
comes from a Requester answer, and anything unconfirmed is marked
**"Pending — future initiative"** or logged as an open question, never left
sitting in the table looking approved.

Name the reference in the document, so a reader can tell which rows started as
a proposal and check them against the source.

## The focus table

The table that turns a partial model into a deliberate one. It lives in the
catalogue's index and carries **every** level-2 element:

| ID | Element | Detailed to | Justified by | Note |
| -- | ------- | ----------- | ------------ | ---- |
| `BPROC7.2` | Deliver the service | Level 3 | `PAIN2` | Where the engagement's pain sits |
| `BPROC7.3` | Bill and collect | Level 2 | — | No pain raised. Revisit when one is |

A branch stopping at level 2 with a dash in the justification column is a
decision a reader can disagree with. The same branch with nothing written is a
gap they cannot tell from an oversight — and they will assume the oversight.

Present this table at the gate. It is usually the most contested thing in the
model, and it should be: it is where the engagement's scope actually lives.

## Where the documents live

**Below roughly fifteen elements in a level, the whole catalogue is one
document** — its rows grouped by level and ordered by ID, which sorts them
into the tree without a `Level` column or a parent column to maintain. That
is the fifteen-element threshold in `architecture-document-style` § Diagrams
come first, applied to the file rather than to the diagram.

**Above it, the catalogue becomes a folder** named for the file it replaces,
with one document per level:

```
2_business/3_business-processes/README.md                     the map, and the focus table
2_business/3_business-processes/1_level-1-macro-processes.md
2_business/3_business-processes/2_level-2-processes.md
2_business/3_business-processes/3_level-3-<macro-process>.md  one per focused branch
```

Capabilities take the same shape under `1_strategy/`. The folder keeps the
layer's own numbering intact: the slot number does not move, its neighbours do
not renumber, and a second focused branch renumbers nothing outside the
folder.

Each level document is a full element document — legend, diagram per section,
inventory table — per `architecture-document-style`. The index README carries the
focus table and links the levels; it defines no elements of its own, so it
needs no legend.

**The identifier carries the level.** A level-2 process under macro process
`BPROC7` is `BPROC7.2`, and a level-3 sub-process under that is `BPROC7.2.1`
— `architecture-document-style` § Levels number hierarchically holds the rule,
including what re-parenting an approved element costs. Splitting the catalogue
into a folder changes none of it: the files exist for readability, and the
identifiers say the same thing they would say in one table.

This is what makes a partial model navigable. The focus table says which
branches were detailed; the IDs say the same thing element by element, so a
`BPROC7.2.1` cited from the application layer announces both its parent and
the fact that this branch was one of the few taken to level 3.

## Done when

- Every band of the level-1 map is either populated or reported empty.
- Levels 1 and 2 are complete across the whole subject.
- Every level-3 document cites the pain that justifies it.
- The focus table covers every level-2 element, including the undetailed ones.
- Every identifier extends its parent's — a level-2 process under `BPROC7` is
  `BPROC7.<n>` — and no table carries a parent column beside it.
- Each level-2 process names a supplier and a customer, not just an input and
  an output.
- Each process carries a purpose, a trigger, an output and an owner; each
  capability is a noun and its leaves name what realizes them.
- The reference model used to seed the capability map is named in the
  document, and nothing it proposed sits unconfirmed without being marked.
