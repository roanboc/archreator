# Finding the processes, and where they live

_Reference for [`process-and-capability-levels`](../SKILL.md) § How far down to
go._

Read this when starting a catalogue from nothing, or when deciding which file
a level belongs in.

## Start from the industry, then ask

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

## A reference proposes; it never fills

Both discovery skills forbid assuming, and a plausible industry catalogue is
exactly the filler that rule exists to stop — it reads as agreed when nobody
agreed it. The reference changes the *question*, not the *authority*: every
element still comes from a Requester answer, and anything unconfirmed is marked
**"Pending — future initiative"** or logged as an open question, never left
sitting in the table looking approved.

Name the reference in the document, so a reader can tell which rows started as
a proposal and check them against the source.

## The focus table turns a partial model into a deliberate one

It lives in the catalogue's index and carries **every** level-2 element.

| ID | Element | Detailed to | Justified by | Note |
| -- | ------- | ----------- | ------------ | ---- |
| `BPROC7.2` | Deliver the service | Level 3 | `PAIN2` | Where the engagement's pain sits |
| `BPROC7.3` | Bill and collect | Level 2 | — | No pain raised. Revisit when one is |

A branch stopping at level 2 with a dash in the justification column is a
decision a reader can disagree with. The same branch with nothing written is a
gap they cannot tell from an oversight — and they will assume the oversight.

**Present this table at the gate.** It is usually the most contested thing in
the model, and it should be: it is where the engagement's scope actually lives.

## Where the documents live

**Below roughly fifteen elements in a level, the whole catalogue is one
document** — rows grouped by level and ordered by ID, which sorts them into the
tree without a `Level` column or a parent column to maintain. That is the
fifteen-element threshold in `architecture-document-style` § Diagrams come
first, applied to the file rather than to the diagram.

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
not renumber, and a second focused branch renumbers nothing outside the folder.

Each level document is a full element document — legend, diagram per section,
inventory table. The index README carries the focus table and links the levels;
it defines no elements of its own, so it needs no legend.

## The identifier carries the level

A level-2 process under macro process `BPROC7` is `BPROC7.2`, and a level-3
sub-process under that is `BPROC7.2.1` — `architecture-document-style` § Levels
number hierarchically holds the rule, including what re-parenting an approved
element costs. Splitting the catalogue into a folder changes none of it: the
files exist for readability, and the identifiers say the same thing they would
say in one table.

This is what makes a partial model navigable. The focus table says which
branches were detailed; the IDs say the same thing element by element, so a
`BPROC7.2.1` cited from the application layer announces both its parent and the
fact that this branch was one of the few taken to level 3.

