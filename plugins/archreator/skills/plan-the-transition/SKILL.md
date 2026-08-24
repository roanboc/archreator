---
name: plan-the-transition
description: Procedure — run this when the Requester wants to know where the architecture should go and in what order, rather than how to deliver one change. Turns an approved baseline into named target plateaus, a derived gap register and a sequence of initiatives, recorded in architecture/roadmap/ and approved at Gate 1. Use it for target state, to-be architecture, gap analysis, transition planning, a roadmap, or when changes keep arriving with nothing to judge their priority against.
metadata:
  archreator:
    kind: gated-procedure
    realizes_process: BPROC5.1
    gates: Gate 1
---

# ⚙ Plan the transition

Every other skill in the method describes a present. This one describes an
intent: where the architecture should be, what stands between here and there,
and in what order the distance is closed.

**A roadmap is a direction, not a permission.** What is approved here is that
this is the right destination and the right order. Each initiative on it still
enters the spine, still aligns through the layers, and still stops at its own
gates before anything is built. A roadmap that is treated as pre-approval for
the changes on it has quietly deleted every gate the method has.

## ⊕ When to use this

| The situation | What it looks like |
| ------------- | ------------------ |
| The Requester asks where this is going | A target state, a to-be architecture, a two-year plan, an answer to "what should we do first?" |
| Changes arrive with nothing to rank them | Each request is defensible on its own and nobody can say which matters more, because there is nothing they are all being measured against |
| The baseline is freshly described | `discover-current-landscape` just closed, and a described estate with no ambition beside it is half an answer |
| A gap keeps being rediscovered | The same missing capability is named in three scope documents' gap notes and nothing has ever been sequenced to close it |
| The roadmap has been overtaken | A plateau was reached, abandoned or invalidated, and the sequence no longer describes the intent |

## ⊖ When not to

| The situation | Use instead |
| ------------- | ----------- |
| There is no baseline to measure from | `discover-current-landscape` first. A target with nothing to subtract from it produces a wish list, not a gap |
| The strategy layer is unfilled | `discover-strategy` — a target that serves no goal cannot be argued with, only agreed with |
| One change needs delivering | `align-change-through-layers`. A roadmap is not how a requirement gets built |
| The current-state documents have drifted | `restate-current-state` first — planning from a model that describes last year produces gaps that were closed months ago |
| One consequential call, no sequence | `record-decision` |

## ⌖ Where this sits

Realizes `BPROC5.1`, and it is the only process in the method whose output
describes a future rather than a present.

It owns **Gate 1**, which `discover-strategy` also owns. That is deliberate
rather than a collision: Gate 1 is the gate at which a Requester approves
**direction**, and a sequenced target is direction in the same sense a
strategy layer is. Giving the roadmap a gate of its own would add a row to
every Approvals table in every model — including the merged scope documents no
rule permits rewriting — to record a decision an existing gate already names.

```mermaid
flowchart TD
  trig(["A baseline, and a question about where it should go"])
  s1["⚙ 1 — Confirm the baseline is worth planning from"]
  s2["⚙ 2 — Name the target plateaus"]
  s3["⚙ 3 — Derive the gap register"]
  s4["⚙ 4 — Sequence the initiatives"]
  s5["⚙ 5 — Write the scope document, present Gate 1"]
  g1{{"❖ Gate 1 — the target and the sequence"}}
  s6["⚙ 6 — Bind the roadmap to the spine"]
  dcl(["⇄ discover-current-landscape"])
  acl(["⇄ align-change-through-layers"])
  out(["A direction each later change is judged against"])

  trig --> s1
  s1 -->|the baseline is missing| dcl
  s1 -->|the baseline holds| s2 --> s3 --> s4 --> s5 --> g1
  g1 -->|changes requested| s2
  g1 -->|approved| s6 --> out
  s6 -.->|one initiative at a time| acl

  classDef business fill:#fffbb5,stroke:#c8c04a,color:#333
  classDef implementation fill:#ffd6d6,stroke:#d99b9b,color:#333
  class s1,s2,s3,s4,s5,s6,trig,out business
  class g1 implementation
```

## ⚓ Invariants

- **The roadmap is the only place the model describes a future.** The numbered
  layers describe today and are kept that way by `restate-current-state`;
  `architecture/roadmap/` describes intent, and is the reason the two never
  have to be mixed. A target element written into a numbered layer breaks the
  one property that makes the current-state documents trustworthy.
- **A gap is derived, never asserted.** Every gap names the baseline it starts
  from — an element that exists and is wrong, or an element that is absent —
  and the plateau that closes it. A gap that names neither is an opinion
  wearing an identifier.
- **A plateau is a state, not a project.** It is named for what is true when
  you arrive, and it is reached or it is not. "Single customer record across
  all channels" is a plateau; "the data migration programme" is the work.
- **Sequence by dependency and appetite, not by ambition.** What must be true
  before something else can start is the method's business; how much change
  the organization can absorb at once is the Requester's, and asking is
  cheaper than discovering.
- **The roadmap declares its own standing.** Its documents define elements, so
  they carry a status line like any others: `◐ Draft catalogue` while the
  target is being drafted, `● Validated at Gate 1` once the Requester has
  settled it (`architecture-document-style` § Document status). A roadmap
  nobody has approved and one that was agreed last quarter are read very
  differently, and only the marker says which is on the screen.
- **Nothing here is approved to build.** Gate 1 approves the destination and
  the order. Every initiative on the roadmap runs the spine, and no gate is
  skipped because the roadmap already named it.
- **A roadmap that is not revisited is worse than none**, because it is
  trusted. Every plateau reached, abandoned or invalidated is written back.

## ⚙ Steps

### 1 — Confirm the baseline is worth planning from

Read what the model actually says about today before proposing a tomorrow. A
gap computed against an empty or stale layer is fiction that will survive
several meetings before anyone notices.

Check three things and say the verdict out loud: the strategy layer is filled
and approved; the layers relevant to the question hold elements rather than
placeholders; and the current-state documents have not obviously drifted from
what shipped.

**⚖ Judgement.** Empty lower layers mean stopping and handing to
`discover-current-landscape` — the target is worth nothing until the estate is
described. Drifted layers mean handing to `restate-current-state` first.
Partial coverage is different from either: a baseline with a declared boundary
is plannable *within that boundary*, and the roadmap simply says so.

**→ Produces** the verdict on the baseline, and a handoff if it does not hold.

### 2 — Name the target plateaus

Work backwards from the strategy layer's goals. For each goal, ask what would
have to be true of the architecture for the goal to be met, and name that
state. That is a plateau, and it belongs in `architecture/roadmap/`.

Keep them few. Two or three plateaus for a two-year horizon is a plan a
Requester can hold in their head and argue with; eleven is a backlog with
dates on it, and nobody checks anything against eleven.

Each plateau names the goals it serves, so that a plateau serving no goal is
visible as the unjustified ambition it is.

**⚖ Judgement.** A plateau that cannot be described without naming the project
that delivers it is a project. Rename it for the state, and if that cannot be
done, it does not belong here.

**← Needs** the strategy layer, and the baseline from Step 1.

**→ Produces** the plateaus in `architecture/roadmap/`.

### 3 — Derive the gap register

For each plateau, walk the layers and subtract. What exists today that the
target does not want; what the target wants that does not exist; what exists
and is in the wrong place, owned by the wrong actor, or duplicated across
three systems.

Each gap gets an identifier, the baseline it is measured from, the plateau it
is closed by, and — where the baseline says so — the element it concerns. A
Pending row from a landscape sweep is the most productive source there is: an
application nobody could locate an owner for is already a gap, written down by
somebody else, waiting to be named as one.

Say what is *not* a gap, too. A duplicated system the organization has decided
to live with is a deliberate state, and recording it as a gap invites somebody
to close it in three years without knowing it was a decision.

**← Needs** the plateaus, and the current-state layers.

**→ Produces** the gap register in `architecture/roadmap/`.

### 4 — Sequence the initiatives

Group the gaps into initiatives, and order them. An initiative here is a
placeholder — a name, the gaps it closes, the plateau it moves toward, and
what must be true before it can start. It is not a scope document, and it does
not become one until it is actually started.

Order by dependency first, and where dependencies leave a choice, ask the
Requester. Two orderings that are equally sound to an architect are rarely
equally sound to the person paying for them.

Mark each initiative with what it depends on rather than with a date. A
sequence survives a slipped quarter; a date does not, and a roadmap full of
stale dates stops being read.

**← Needs** the gap register.

**→ Produces** the sequence in `architecture/roadmap/`.

### 5 — Write the scope document, present Gate 1

Planning is a full initiative. Create the scope document with
`write-scope-document` before presenting, so the Requester approves against a
document.

The alignment table gets a verdict for every numbered layer, and for most of
them that verdict is an explicit "no change": a plan describes a future, and
the numbered layers describe today. The one exception is `1_strategy`, where
naming a target routinely surfaces a course of action the layer did not carry
— record that as a change, because it is one.

**❖ Gate 1 — the target and the sequence.** The Requester approves.

Present the plateaus, the gaps under each, and the order, with full branch
links (`align-change-through-layers` § Show the Requester what they are
approving). Two things have to be said out loud rather than left in the
document: that approving this approves the **destination and the order**, not
the work; and what is deliberately not on it, because a roadmap's exclusions
are the half a Requester is most likely to disagree with.

Record the approval in the Approvals table, naming the roadmap documents shown.

**← Needs** the plateaus, the gaps, the sequence.

**→ Produces** `architecture/scope/<n>_*.md`, its row in the index, and the
Approvals table's Gate 1 row.

### 6 — Bind the roadmap to the spine

A roadmap nothing points at is a document that ages quietly. Two bindings stop
that, and both are small.

**Each initiative, when it starts, cites the gaps it closes** in its own scope
document, and the roadmap's entry is marked as in flight. `write-scope-document`
already requires every meaningful exclusion to carry a gap note; those notes
are now candidate rows in the register rather than observations that expire
with the document they were written in.

**Each plateau, when it is reached, is recorded rather than deleted.** The
plateau stays, marked reached, with the initiative that arrived at it — which
is what makes the roadmap a record of direction over time instead of a
perpetually optimistic present tense. A plateau abandoned is marked abandoned,
with why, for the same reason.

**← Needs** Gate 1.

**→ Produces** the roadmap's status column, kept current by later initiatives.

## ⇄ Hands off to

| Skill | When | What comes back |
| ----- | ---- | --------------- |
| `discover-current-landscape` | Step 1 finds the lower layers empty | A described, approved baseline — after which this skill restarts at Step 2 |
| `restate-current-state` | Step 1 finds the current-state documents drifted | A model that describes today, which is what a gap has to be measured against |
| `write-scope-document` | Step 5 | The initiative's record, and the Approvals table Gate 1 is written in |
| `align-change-through-layers` | Step 6, once per initiative on the sequence, as each is actually started | A delivered change, whose scope document cites the gaps it closed |
| `record-decision` | A call inside the plan is consequential and smaller than the plan — which plateau a contested system lands in, and why | A numbered decision record the roadmap can point at instead of re-arguing |

## ✎ Worked example

> An organization has a described estate and four strategy goals. Step 2 turns
> the goals into two plateaus, one of them "every customer-facing service
> authenticates against one identity provider". Step 3 subtracts and finds
> eleven gaps, four of which are Pending rows left by the landscape sweep.
> Step 4 groups them into five initiatives and finds that three of them cannot
> start until the identity work lands, which settles most of the ordering
> without asking anyone. The Requester, at Gate 1, moves one initiative later
> because a contract renewal makes next year cheaper than this one — an
> ordering fact no architect had. The roadmap records the reason beside the
> sequence, so the next reader does not re-derive it.

## ⚠ Anti-patterns

- A target state with no baseline, so every gap is really a guess.
- Plateaus named after projects — "the ERP programme" is not a state.
- A gap register that restates the target in the negative, adding nothing.
- Dates instead of dependencies, so the whole plan is stale in a quarter.
- Sequencing every gap, until the roadmap is a backlog nobody reads.
- Writing target elements into the numbered layers, which are the model's only
  description of today.
- Treating Gate 1 on the roadmap as approval to build the things on it.
- Deleting a plateau when it is reached, leaving no record that it was ever
  the plan.

## ☑ Done when

- Every plateau names the goals it serves, and is a state rather than a
  project.
- Every gap names the baseline it is measured from and the plateau that closes
  it.
- Deliberate states the organization has chosen to live with are recorded as
  such, not as gaps.
- The sequence orders initiatives by dependency, and the Requester's ordering
  choices are recorded with their reasons.
- Nothing in `architecture/roadmap/` has leaked into the numbered layers.
- The scope document records Gate 1 as granted, naming the roadmap documents
  shown, and the presentation said plainly that the work itself is not
  approved.
- The roadmap says how it is kept current, and who does it.
