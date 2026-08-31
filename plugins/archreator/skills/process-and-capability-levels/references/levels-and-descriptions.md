# Levels, and what each one must say

_Reference for [`process-and-capability-levels`](../SKILL.md) § How far down to
go._

Read this when you have decided *that* a catalogue needs another level and now
need to know what that level owes — the four macro categories, what each level
means, and the minimum a description carries.

## Level 1 is the macro process map, in four categories

This is the process map quality management has used for decades, which matters
beyond convention: **an organization with a quality system already thinks in
these bands**, and arriving with a different decomposition of work it has
already decomposed spends credibility on nothing. Ask what exists before
drawing one.

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
stream — the right way to get the operational band, and how `discover-strategy`
theme 5 already works — produces nothing for the other three. That is the
categories' main use: they make it possible to notice that an organization has
documented how it delivers and not how it decides, staffs, or improves. Report
an empty band as a finding, not as a blank.

## What each level means

| Level | ID | It is | Named | Usual count |
| ----- | -- | ----- | ----- | ----------- |
| **1 — Macro process** | `BPROC7` | A band's major grouping of work, end to end | Verb + object, or a noun phrase where the organization already has one | 8–15 for a whole organization |
| **2 — Process** | `BPROC7.2` | An end-to-end process with a trigger, a definable output, and one accountable role | Verb + object | 3–8 per macro process |
| **3 — Sub-process** | `BPROC7.2.1` | The ordered steps inside a level-2 process — the first level where a flow diagram says something a list cannot | Verb + object | Only where a pain justifies it |
| **4 — Task** | — | What one person or system does in one sitting | Verb + object | Belongs in a work instruction, not in the model |

Level 4 is named here so it can be refused. When a Requester asks for it, the
answer is that the model stops at 3 and the procedure continues in whatever the
organization uses for work instructions — the model is not the operating
manual, and the two have different lifecycles.

## The minimum description

A process named without a trigger and an output is a heading. Each level
carries at least:

| Level | Columns beyond ID and name |
| ----- | -------------------------- |
| **1** | Category · purpose (one sentence) · owner · composed of |
| **2** | Purpose · trigger · supplier · input · output · customer · owner role · realized by |
| **3** | The level-2 set, plus the sequence — which is what the diagram carries |

No level carries a parent column: `BPROC7.2` names its parent already, and a
column repeating it is DRY broken inside a row. `composed of` stays, because it
carries the children's **names**, which the identifiers do not.

**Purpose is one sentence saying what this turns into what, and for whom.**
"Manages orders" is a restatement of the name. "Turns a confirmed order into a
delivered shipment for the customer who placed it" is a definition.

**Supplier and customer are named, not implied.** With them the level-2 row is
a SIPOC — supplier, input, process, output, customer — and a SIPOC belongs to
*each* process, never one to the whole map. They cost two columns and they are
what turns a catalogue into a chain: a process whose supplier is nobody is
either triggered from outside the organization or missing a predecessor, and a
process whose customer is nobody produces an output no one consumes. Neither is
visible from trigger and output alone.

Name the neighbouring process by ID where there is one (`BPROC7.2`), and the
external party where there is not (`Requester`, `Regulator`). A chain the
reader can follow by ID is the payoff — and the identifiers already carry the
tree, so the chain and the hierarchy are readable from the same table.

`realized by` is the grounding rule (`architecture-document-style` § Grounding
rule) on the organization track: a process is realized by a team, a role, or a
written procedure — not by a source file. Name that, or mark it Pending.

