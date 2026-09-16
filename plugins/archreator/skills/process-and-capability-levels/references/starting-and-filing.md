# Finding the processes, and where they live

_Reference for [`process-and-capability-levels`](../SKILL.md) § What is here, and
what is one file away._

Read this when starting a catalogue from nothing, or when deciding which file
a level belongs in.

## Start from the industry, then ask

"What must this organization be able to do?" is answered badly — businesses
describe their org chart, or the projects currently running. Turn recall into
recognition:

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

A plausible industry catalogue reads as agreed when nobody agreed it. The
reference changes the *question*, not the *authority*: every element comes from
a Requester answer or an adopted call recorded in its `Source` cell
(`align-change-through-layers` § Ask only what blocks the work now), and
anything unconfirmed is marked **"Pending — future initiative"**.

Name the reference in the document, so a reader can tell which rows started as
a proposal and check them against the source.

## The focus table turns a partial model into a deliberate one

It lives in the catalogue's index and carries **every** level-2 element.

| ID | Element | Detailed to | Justified by | Note |
| -- | ------- | ----------- | ------------ | ---- |
| `BPROC7.2` | Deliver the service | Level 3 | `PAIN2` | Where the engagement's pain sits |
| `BPROC7.3` | Bill and collect | Level 2 | — | No pain raised. Revisit when one is |

A branch stopping at level 2 with a dash in the justification column is a
decision a reader can disagree with; the same branch with nothing written is a
gap they cannot tell from an oversight.

**Present this table in the pull request.** It is where the engagement's scope lives.

## Where the documents live

**Below roughly fifteen elements in a level, the whole catalogue is one
document** — rows grouped by level and ordered by ID, which sorts them into the
tree without a `Level` column or a parent column to maintain. That is the
fifteen-element threshold in `architecture-document-style` § Diagrams come
first, applied to the file rather than to the diagram.

**Processes keep levels 1 and 2 in that one document whatever their size**:
the map, the catalogue of macro processes with purpose and owner, and under
each macro process a table of its processes with purpose, owner and state. A
document per macro process restated the map and the table and said nothing
of its own, so it is not written.

**Level 3 is the activities of one process, one file per detailed process**,
in a flat folder beside the document, named by the process identifier and its
name:

```
2_business/3_business-processes.md                            levels 1 and 2, the focus table
2_business/activities/bproc4.2-develop-agents-and-applications.md   one per focused branch
```

No folder per category or per macro process: the identifier already carries
the tree. The document opens with the process's inputs-and-outputs diagram,
then the flow of its activities, then each activity with its tasks
([`presentation-patterns.md`](./presentation-patterns.md) § Level 3 — the
flow).

**Capabilities split by level when they pass the threshold**, into a folder
named for the file it replaces — `1_strategy/2_capabilities/` with one
document per level and an index README that carries the focus table and links
the levels. The folder keeps the layer's own numbering intact: the slot number
does not move and its neighbours do not renumber. Each level document is a
full element document — status line, diagram per section, inventory table;
the index defines no elements and needs no diagram.

## The identifier carries the level

A level-2 process under macro process `BPROC7` is `BPROC7.2`, and a level-3
activity under that is `BPROC7.2.1` — `architecture-document-style` § Levels
number hierarchically holds the rule, including what re-parenting an approved
element costs. Splitting the catalogue into a folder changes none of it.

The focus table says which branches were detailed; the IDs say the same thing
element by element, so a `BPROC7.2.1` cited from the application layer
announces both its parent and that this branch was taken to level 3.

