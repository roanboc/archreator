---
name: process-and-capability-levels
description: Rulebook — consult when shaping an organization's process or capability model so it is complete across its boundary, detailed only where useful and readable as both a hierarchy and a chain of value.
metadata:
  archreator:
    kind: rulebook
    gates: none
---

# ※ Process and capability levels

Processes and capabilities can be decomposed without a natural stopping point.
This rulebook keeps the broad model trustworthy while preventing detail that
nobody needs or can hold in their head.

## ⊕ When to use this

- Modeling or refreshing an enterprise or domain process map.
- Creating a capability map or deciding whether an existing catalogue needs
  another level.
- A discovery or change identifies a process branch whose pain, risk or
  decision needs more detail.
- A catalogue has become an org chart, task list or unreadable flat inventory.

When presenting or reorganizing a process model, read
[the process presentation patterns](./references/process-presentation-patterns.md).
They define the minimum semantic contract at each level while leaving the
document shape flexible for its reader and purpose.

Also apply [the hierarchical-elements reference](../architecture-document-style/references/hierarchical-elements.md)
to level files, page location and parent references. These are general
architecture rules, not process-only conventions.

## ⊖ When not to

- A single solution needs only the business processes or capabilities it
  consumes or locally supports. Link to the owning model instead of creating
  an enterprise map for one application.
- A list of implementation steps belongs in a work plan or operating
  instruction rather than the architecture model.
- No current question or decision needs a process or capability catalogue.
  Standard structure is available; it is not an obligation to create content.

## ⌖ Where this sits

This rulebook realizes no process. Business-model, strategy, landscape,
roadmap and change procedures consult it when organizational processes or
capabilities enter scope. `architecture-document-style` governs how the
resulting elements, relationships and documents are written.

## ※ Rules

### Work breadth first and deepen on pain

Within the declared organizational boundary, establish the macro view before
decomposing one branch. Complete the useful level-1 map and its relevant
level-2 processes or capabilities across that boundary. Add level 3 only when
a named pain, risk, inconsistency or decision requires it.

Horizontal coverage lets a reader distinguish the whole boundary from a
convenient fragment. Vertical completeness has no natural end, so it must earn
its cost. A partial boundary is valid when coverage and exclusions are
explicit; arbitrary partial depth is not.

### Classify level-1 processes in four bands

Use the bands the organization already recognizes when it has an established
quality or process system. Otherwise use these four to test coverage:

| Band | Holds | If it stopped tomorrow |
| --- | --- | --- |
| **Strategic** | Direction, governance, planning, portfolio, risk and oversight | Operations continue but begin to drift |
| **Operational** | The end-to-end value chain customers or beneficiaries rely on | The customer notices now |
| **Support** | People, finance, procurement, technology, facilities and legal support | Other work degrades over time |
| **Evaluation** | Measurement, audit, feedback, corrective action and improvement | Nothing improves and faults repeat |

The bands classify macro processes; they are not architecture elements and get
no identifiers. An empty band is a finding to explain, not a blank to fill with
invented work.

### Use levels consistently

For processes:

| Level | Example reference | Meaning |
| --- | --- | --- |
| **1 — Macro process** | Fulfil customer demand [BPROC7] | A major end-to-end grouping within one band |
| **2 — Process** | Validate an order [BPROC7.2] | Work with a trigger, definable output and one accountable role |
| **3 — Sub-process** | Check payment [BPROC7.2.1] | Ordered steps inside one level-2 process; the first level where a flow usually adds value |
| **4 — Task** | No architecture ID | What one person or system does in one sitting; keep it in an operating instruction |

For capabilities:

| Level | Example reference | Meaning |
| --- | --- | --- |
| **1 — Capability area** | Commerce [CAP3] | A coherent ability against which a strategic choice can be judged |
| **2 — Capability** | Order fulfilment [CAP3.2] | A distinct ability realized by people, information and systems |
| **3 — Sub-capability** | Payment assurance [CAP3.2.1] | Detail justified by a named pain, risk or decision |

A level is not a type. Commerce [CAP3] and Order fulfilment [CAP3.2] are both
Capabilities; the numeric segments only express decomposition.

### Name processes as work and capabilities as abilities

- A process is a verb plus object: **Fulfil an order**. It has sequence and a
  trigger.
- A capability is a noun phrase: **Order fulfilment**. It expresses an ability
  without sequence.

A capability map written entirely as verbs is usually a process list wearing
the wrong label. A process map organized by departments is usually an org
chart wearing the wrong label.

### Give each process a minimum SIPOC

A process name is not a definition. At minimum record:

| Level | Required meaning beyond ID and name |
| --- | --- |
| **1** | Band, purpose, accountable owner and composed-of children |
| **2** | Purpose, trigger, Supplier, Input, Output, Customer, accountable owner and realization |
| **3** | The level-2 meaning plus the ordered flow and material decisions |

Supplier, Input, Process, Output and Customer form the SIPOC. Apply it to each
level-2 process, not once to the whole map. Reference a neighbouring process
as `Name [ID]` where one supplies or consumes the output; name the external
actor where the chain crosses the boundary.

Purpose states what the process turns into what and for whom. “Manages
orders” repeats a name; “turns a confirmed order into a delivered shipment for
the customer” defines the result.

Realization names the role, team, written procedure or system that makes the
process real, or a specific gap. Capability areas are realized by their parts;
only the leaves need direct realization.

### Let identifiers carry the hierarchy

A child extends its parent: Validate an order [BPROC7.2] belongs to Fulfil
customer demand [BPROC7], and Check payment [BPROC7.2.1] belongs to Validate
an order [BPROC7.2]. Number children within their parent. Every nested
definition also names that parent in a `Parent` column as `Name [ID]`; people
must not have to decode the dotted ID to know where they are. Keep a
composed-of field at Level 1 only when it helps the landscape show the
children's names.

Definition catalogues remain ID-first so their hierarchy sorts naturally:
`ID | Name | ArchiMate type | Description`. Every reference outside a
definition row is human-first as `Name [ID]`.

Encode only true same-type decomposition in the identifier. Service
realization, capability use and cross-model refinement remain declared
relationships.

### Let industry references propose, never fill

When a blank-page question produces an org chart or current project list:

1. Confirm the industry or operating context in the organization's words.
2. Choose and name a relevant reference model.
3. Use it to propose level-1 and level-2 candidates.
4. Review one area at a time: confirm, rename, reject and ask what this
   organization has that the reference could not know.
5. Rewrite every survivor in the organization's language.

Cite the reference; do not reproduce it as if it were evidence about this
organization. Unsupported candidates remain proposals outside the canonical
catalogue or become explicit gaps when their absence matters.

### Make selective depth explicit

When any branch reaches level 3, keep a focus table covering every level-2
branch:

```markdown
| Process | Detailed to | Justified by | Note |
| --- | --- | --- | --- |
| Deliver the service [BPROC7.2] | Level 3 | Late handoff [PAIN2] | This is where the delay occurs. |
| Bill and collect [BPROC7.3] | Level 2 | — | No current question requires more detail. |
```

The table lets a reader distinguish deliberate stopping from forgotten work.
The justification names the pain, driver, assessment, risk or decision that
earned the detail. Do not create a focus table for a small catalogue with no
selective decomposition or ambiguity about coverage.

### Give populated levels clear homes

Once the hierarchy has more than one populated level, give each populated
level its own file and link those files from the process or capability index.
One file may hold all elements at a level. Split a Level 3 file by its Level 2
parent when several branches become difficult to navigate or have different
owners. Every file states its level and full location; every child row names
its parent.

A level-3 flow is useful when order, branching or handoff matters; do not draw
one that merely repeats a list.

Create no empty level file, catalogue or expected branch. The front door and
coverage statement carry what is outside scope or not yet known.

## ⚠ Anti-patterns

- Decomposing every branch to the same depth for visual symmetry.
- Building a four-band process map for one application.
- Treating a department list as processes or a verb list as capabilities.
- A level-2 process with no supplier, customer, trigger or definable output.
- Filling the canonical catalogue from an industry reference without
  organizational evidence.
- A focus table that omits branches left at level 2.
- A nested catalogue with no human-readable parent reference.
- A level file whose location can be understood only from its filename or ID.
- Level-4 work instructions inside the architecture model.
- Empty catalogue files created because a standard path exists.

## ☑ Done when

- Every level-1 process is classified, or an empty band is explained.
- Coverage is clear across the declared boundary before any selective depth.
- Each level-2 process carries a usable SIPOC, purpose, owner and realization.
- Processes are verbs, capabilities are nouns and hierarchical IDs reflect
  real decomposition.
- Every populated level has a linked file, every child names its parent and
  every file states where it sits.
- Every level-3 branch has a named reason, and the focus table shows where
  decomposition stopped.
- Reference-model proposals are distinguishable from supported facts.
- The selected presentation preserves the level's semantic contract without
  adding empty headings, files or repeated notation guidance.
