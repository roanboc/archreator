---
name: align-change-through-layers
description: Procedure — run this when requirements change or a new feature or behavior change is requested. Assesses whether the change needs strategy discovery first, aligns it through the architecture layers (strategy → business → information → application → technology) with Requester approval before implementation, records it in a scope document, and only then implements. Not needed for pure bug fixes that change no documented behavior.
metadata:
  archreator:
    kind: gated-procedure
    realizes_process: BPROC2.1, BPROC2.2, BPROC2.3
    gates: Understanding
---

# ⚙ Align a change through the layers

**The spine.** Strategy and business architecture are validated before any
other layer is touched, and validated means the Requester approves before
development proceeds.

A requirement change is never implemented directly. It is aligned through the
documents in `architecture/`, approved at the gate below, captured in a scope
document, and only then coded. The folder numbers give the assessment order.

## ⊕ When to use this

| The situation | What it looks like |
| ------------- | ------------------ |
| A requirement changes | Someone asks for a feature, a behavior change, or reports a problem |
| A change to documented behavior | Anything that will produce code, or alter what a document claims |
| Work resumes after discovery | Discovery finished at Direction, and the original request is still unbuilt |

## ⊖ When not to

| The situation | Use instead |
| ------------- | ----------- |
| A pure bug fix changing no documented behavior | The bug-fix path — no gates, no scope document, but still update whatever the fix falsifies |
| The project was never bootstrapped | `establish-project` first. `AGENTS.md` declaring no depth is the signal |
| The model has drifted rather than the requirement | `restate-current-state` — its own initiative, with its own diff |
| The question is where to go rather than what to build | `plan-the-transition` — a target state, a gap register and a sequence, approved as direction and not as work |
| The subject already runs and the lower layers are empty | `discover-current-landscape` — there is nothing for a change to be aligned against yet |

## ⌖ Where this sits

Realizes `BPROC2.1`, `BPROC2.2` and `BPROC2.3` — the whole of the Operational
band's delivery. It owns **Understanding**; the **Direction** gate belongs to
the discovery it hands off to.

```mermaid
flowchart TD
  req(["A requirement, or a problem"])
  s1["⚙ 1 — Locate the change, assess strategy"]
  v{"Which verdict?"}
  disc(["⇄ discover-business-model · discover-strategy"])
  stop(["Stop — surface the conflict to the Requester"])
  bug{"Pure bug fix?"}
  s2["⚙ 2 — Align business and information"]
  s3["⚙ 3 — Draft the scope document"]
  g2{{"❖ Understanding — strategy, business, information"}}
  s4["⚙ 4 — Align application and technology"]
  s5["⚙ 5 — Implement"]
  s6["⚙ 6 — Verify alignment"]
  s7["⚙ 7 — Open the pull request"]
  merged(["Merged"])

  req --> s1 --> v
  v -->|discovery needed| disc
  v -->|conflicts with a Principle| stop
  v -->|aligned| bug
  bug -->|yes| s5
  bug -->|no| s2 --> s3 --> g2
  g2 -->|changes requested| s2
  g2 -->|approved| s4 --> s5
  s5 --> s6 --> s7 --> merged

  classDef business fill:#fffbb5,stroke:#c8c04a,color:#333
  classDef implementation fill:#ffd6d6,stroke:#d99b9b,color:#333
  class s1,s2,s3,s4,s5,s6,s7,req,merged,stop business
  class g2 implementation
```

Every edge leaving a rhombus is a verdict the agent **records** — a "no change"
on a layer, a "pure bug fix, no scope document". None of them is a silent skip.

## ⚓ Invariants

### Well-done less is more

Every step produces elements — goals, capabilities, services, rules, canvas
blocks. **At every one of them, consolidate before you enumerate.** Two
elements differing only in degree are one element with a severity column. A
list past one screen is asking which of its entries are the same thing seen
from two angles. The rules are in `document-style` § Consolidate
before you enumerate and are not restated here.

This applies to what is **proposed** as much as to what is written: a Requester
handed six overlapping options at a gate has been handed the analysis the
process exists to do for them. And to what is **presented**: a gate summary is
a consolidation, not a table of contents.

### Every verdict is recorded

A layer with no impact still gets a "no change" verdict, written into the
scope document's alignment table. A reader cannot tell an unconsidered layer
from an unaffected one.

### Ask only what blocks the work now

**Decide what you can decide.** A question reaches the Requester only when
both are true: the answer changes what gets built now, and nothing in the
model or the request settles it. Everything else is the agent's call — taken,
applied, and written into the document it affects with its `Source` cell
reading `adopted — <the call>`. That document stays `◐`, so a later word from
the Requester overrides it where an approved fact would not.

**Never ask about a state that does not exist yet.** A question about what
will be true after work nobody has scheduled is not a question; it is the
work, unstarted.

**Speak the subject's language, never the method's.** The Requester is shown
what changes about their business and asked whether it is right. They are not
asked to choose between the method's options, and never have to know what a
gate is to answer.

## ❖ The gates

**Two gates, named for what the Requester approves** — you approve the
direction, and you approve before any code exists.

| Gate | When | The Requester approves |
| ---- | ---- | ----------------------- |
| **❖ Direction** | Only when the change moves *why* or *for whom* — Step 1 finds the initiative is modeling an organization, triggers strategy discovery, or the initiative is planning rather than building | Where the subject is an organization, the Value Proposition Canvas per customer segment and the Business Model Canvas per product, before anything is derived from them — see `discover-business-model`. Then the strategy layer itself (motivation, capabilities, value stream) and the key business elements discovered with it — see `discover-strategy`; or the target plateaus, the gap register and the sequence — see `plan-the-transition` |
| **❖ Understanding** | Every initiative that changes documented behavior, which is every initiative that will produce code. A docs-only initiative passes Direction instead | The changes, or explicit "no change" verdicts, to `1_strategy`, `2_business` and `3_information` |

**On an ordinary change, a Depth 1 project meets one gate.** Understanding is
mandatory. Direction belongs to discovery and planning, so an application
project meets it only when one of those runs — its first strategy discovery,
or a roadmap.

**Direction may be granted in two sittings, and it is still one gate.** Where
the subject is an organization the canvases are approved first and the strategy
derived from them second: deriving strategy from unapproved canvases is the
error the ordering prevents. Two rows in the Approvals table, each naming what
was shown; one gate.

**Direction approving a roadmap approves no work.** Every initiative on a
sequence still arrives here, still walks the layers, and still stops at its own
Understanding gate.

**A granted gate moves a status line.** An element added or changed by this
initiative sits in a document marked `◐ Draft catalogue` until the gate
covering its layer is granted; the moment it is, the document says
`● Validated at <gate>, <date>` and its `Notes` column is emptied —
`architecture-document-style` § Document status.

**This table is the single source for which gate applies when.** `AGENTS.md`,
`architecture/scope/README.md` and `write-scope-document` point here rather than
restating it.

Approval is granted by the **Requester** (see `AGENTS.md` § Who decides) and
recorded in the scope document's Approvals table — which gate, who approved,
when, and what was shown. **An approval that isn't recorded didn't happen**, and
**a gate that was not granted gets no row**: an Approvals table holds what
happened, never a census of what did not.

### Unscheduled stops

The gates are the stops you can see coming. Two things stop the work between
them, and the agent **names which one** rather than just asking a question:

| Stop | It fires when |
| ---- | ------------- |
| **Material uncertainty** | Two readings of the request lead to materially different work, and nothing in the model settles which. Not "I would like confirmation" — a coin-flip whose two sides build different things |
| **Authorization** | The work would commit the Requester to something they have not agreed: spend, public exposure, publishing the model, a direction |

Naming the stop is what makes it answerable: "I need authorization before I
publish this" tells a Requester what kind of answer is wanted; "is this okay?"
does not. A stop is recorded in the Approvals table like a gate, with the
reason in place of a gate name.

### Where a gate happens

| Surface | Use it when |
| ------- | ----------- |
| **The conversation** | The Requester is in the session with you |
| **A pull-request comment** | The Requester is not in the session, or the approval should be reviewable by others. The reply *is* the record |
| **A published view of the model** | Stakeholders read the model but never open GitHub. Only once the project publishes a site |

Whichever surface is used, the approval is transcribed into the Approvals table
with its date and what was shown.

### Show the Requester what they are approving

**Every gate presentation carries full clickable links to the exact content
under review** — one per document, resolving to the branch the work is on, not
to the default branch:

```
https://github.com/<owner>/<repo>/blob/<branch>/<path>
```

Not a repository-relative path, not a file name, not "see the canvases": an
approval granted against a summary is an approval of the summary. Link the
branch, never the default branch, and give one link per document rather than a
link to a folder. In a pull-request comment write the full URLs — GitHub
renders relative links there inconsistently.

## ⚙ Steps

### 1 — Locate the change, then assess strategy

**1a — Confirm the modeling depth, and say it out loud.** `AGENTS.md` records
the declared depth. Read it and check the request against it.

| Finding | What to do |
| ------- | ---------- |
| The request fits the declared depth | Say which depth you are working at, in one line, and continue |
| The request outgrows it | Say so, and what deepening would cost. A depth change is its own initiative, decided by the Requester, never absorbed quietly mid-change |
| `AGENTS.md` declares no depth | The project was never bootstrapped — run `establish-project` first |

Never let the depth go unstated. A Requester told "I'm treating this as Depth 1
— one application, light strategy layer; say the word if you want the
organization modeled properly" can correct you in one sentence. A Requester told
nothing finds out three initiatives later.

**1b — Locate the domain (Depth 3 only).** Name which domain owns this change,
and check whether it touches another domain's **exposed** services. If it does,
the consuming domains' Requesters approve at Understanding too, and `model-domains`
governs how the contract changes. At Depth 1 and 2, skip.

**1c — Assess strategy, and decide whether this is discovery.**

**⚖ Judgement.** Read `architecture/1_strategy/` against the change and reach
one of four verdicts, explicitly:

| Verdict | Triggered when | What happens |
| ------- | -------------- | ------------ |
| **Operating-model discovery** | The subject being modeled is an **organization** rather than a single application, and `0_business-design/` is empty or no longer matches | Switch to `discover-business-model`. The initiative becomes the canvases, ending at **Direction** |
| **Strategy discovery** | `1_strategy/` still holds placeholders, or the change adds or modifies a Stakeholder, Driver, Goal or Principle, or reshapes the value stream | Switch to `discover-strategy`. The initiative becomes a docs-only discovery ending at **Direction** |
| **Conflict** | The change contradicts an existing Principle | Stop and surface it to the Requester. Resolving it may amount to changing the Principle, which is the trigger above |
| **Aligned** | The change serves an existing goal and value-stream stage | Record which ones, and continue |

Tell the first two apart by the subject, not the size of the request: "several
products share one capability base and I need to model the business" is
operating-model discovery; "this app needs a new feature" is not.

**→ Produces** a stated depth, the owning domain at Depth 3, and one of four
recorded verdicts.

#### Handing off is not an exit

Both discovery verdicts switch skills, but neither leaves this process. A
discovery initiative is still an initiative: it gets the next numbered scope
document, indexed, created **before** its gate so the Requester approves
against a concrete document. Then it finishes at Step 7 and Step 8 like any
other.

What a discovery initiative skips is Steps 2, 4, 5 and 6 — no business or
information alignment beyond what discovery produces, no Understanding, no
application layer, no code. Its Approvals table records Direction and nothing
else.

### 2 — Align business and information

For each layer, read the layer README and answer its question for the requested
change. Update the affected documents as you go — they are part of the same
change set, not an afterthought.

| Layer | The question |
| ----- | ------------ |
| `architecture/2_business/` | Which business services, processes or objects are added or changed? New business rules get a row in the rules table, with the *why*, before they get code. New terms go into the glossary, and code reuses glossary terms |
| `architecture/3_information/` | New or changed data objects, flows, representations, storage, classification, retention? |

At Depth 2 and above, processes are levelled and level 1 is classified into
four macro categories — use `process-and-capability-levels` rather than deciding
the shape per initiative. If the change adds an actor, or changes an existing
AI actor's autonomy level or decision rights, consider a `record-decision`
alongside the scope document explaining why.

A layer folder that does not exist yet is emitted from the plugin's assets
at the moment the change first fills it — `assets/layers/2_business/`,
`assets/layers/3_information/` — never created empty in advance.

**← Needs** the verdicts from Step 1.

**→ Produces** changed `2_business/` and `3_information/`, or explicit "no
change" verdicts.

### 3 — Draft the scope document

Create the next-numbered file in `architecture/scope/` with
`write-scope-document`. Do this **before Understanding**, so the Requester approves
against a concrete document; refine it as implementation proceeds.

**→ Produces** `architecture/scope/<n>_*.md`, and its row in the index.

### 4 — Understanding, before any code

**❖ Understanding — strategy, business, information.** The Requester approves.

Present, in one message: the changed or added strategy, business and
information documents — or their explicit "no change" verdicts — and the draft
scope document. Ask one question, in the subject's own words: **does this
describe the business correctly, so implementation can start?**

Do not write application or technology documents, or code, until it is answered
with an approval. Record it in the Approvals table; if changes are requested,
rework Steps 1–3 and present again.

**← Needs** the aligned layers and the scope document.

**→ Produces** the Understanding row.

### 5 — Align application and technology

| Layer | The question |
| ----- | ------------ |
| `architecture/4_application/` | Which application services or components change? New ports and interfaces follow `5_interface-contracts.md`; new platforms and adapters follow `4_solution-design.md` |
| `architecture/5_technology/` | Any impact on runtimes, build, CI or hosting? Where no stack has been chosen, use `stack-selection` rather than re-deriving one |

As in Step 2, a layer filled for the first time gets its README from the
plugin's assets — `assets/layers/4_application/`, `assets/layers/5_technology/`.

**← Needs** the granted Understanding.

**→ Produces** changed `4_application/` and `5_technology/`.

### 6 — Implement

**First, size the work.** If any work package is too large or long-running to
finish in one sitting — more than a handful of files, or spanning a break, a
session boundary, or a handoff — shard it with `shard-stories` before writing
code. A small work package needs no stories; an inline task list in the scope
document is the default.

Only now write code. Keep the architecture and scope documents true to what is
actually delivered. If implementation diverges from the plan, update them in
the same commit series; if the divergence touches what a gate approved, take
the delta back to the Requester instead of silently absorbing it.

**← Needs** the approved scope document.

**→ Produces** code, and documents still true of it.

### 7 — Verify alignment before finishing

- Every new or changed code artifact is named by some architecture document.
- Every element added names the code artifact that realizes it, or is marked
  "Pending — future initiative" with a link to the initiative that will deliver
  it.
- **Name every other model in the repository whose current state this change
  falsifies, and correct it in the same change** (`RULE12`). Grep for the paths,
  directory names and artifact names the change moved or renamed; every hit in
  another model's layer documents is a statement that was true before and may
  not be now.
- The scope document's in-scope/out-of-scope table matches the diff.
- Its Approvals table has a row for every gate this initiative was granted,
  and no row for one it was not.
- At Depth 3: every cross-domain ID reference points at a service the owning
  domain's charter actually exposes.
- Cross-links resolve, paths and anchors both.

**Neither validator can find these.** `check_model` verifies that an element
*reference* resolves and `check_links` that a *link* resolves; neither reads
what a "Realized by" cell claims about a path.

**If this was a discovery initiative, say what comes next.** Discovery ends at
Direction having delivered documents and no code — which is correct, but
a Requester who asked for a feature and received a merged docs-only PR will
reasonably think the process failed to build anything. Name the request that
triggered discovery and offer to open it as the next initiative.

### 8 — Open the pull request

Use `write-pr-description`: it fills the one template and covers the whole
branch (`main...HEAD`), not just the latest commit.

**→ Produces** a pull request a Reviewer can judge.

## ⇄ Hands off to

| Skill | When | What comes back |
| ----- | ---- | --------------- |
| `discover-business-model` | Step 1c returns operating-model discovery | Approved canvases at Direction, then the strategy derived from them |
| `discover-strategy` | Step 1c returns strategy discovery | A filled strategy layer at Direction. Implementation re-enters here as its own initiative |
| `model-domains` | Depth 3, and the change crosses a domain boundary | The contract change, with every consuming Requester at Understanding |
| `write-scope-document` | Step 3 | The document the gates are recorded in |
| `process-and-capability-levels` | Step 2 at Depth 2 or above | Levelled processes, shaped rather than decided per initiative |
| `stack-selection` | Step 5, and no stack chosen | A recorded choice in `5_technology/` |
| `shard-stories` | Step 6, and a work package is too large | Self-contained stories in build order |
| `write-pr-description` | Step 8 | The pull-request body |
| `run-retrospective` | The pull request merged and judgement was exercised — the method was silent somewhere and someone improvised | A pattern note in the organization's own records; each proposal becomes its own initiative |

## ✎ Worked example

> A Requester asks for an export feature. Step 1a states Depth 1. Step 1c finds
> the strategy filled and the change serving an existing goal — **aligned** —
> and records which goal. Step 2 adds one business service and one data object,
> and gives `1_strategy` an explicit "no change". Understanding is presented
> with branch links to three documents and the draft scope document, and one
> question: does this describe the business correctly? Steps 5–8 implement,
> verify and open the PR, and Step 7 catches that a renamed directory falsified
> two rows in a second model — which is the check nothing automated would have
> found.

## ⚠ Anti-patterns

- Writing code before Understanding is granted.
- Leaving a layer without a verdict because nothing changed there.
- Presenting a gate with a summary and no links, or links to the default branch.
- Treating a discovery verdict as an exit from this process rather than a
  handoff that returns.
- Absorbing a divergence from what a gate approved instead of taking it back.
- Deciding process decomposition depth per initiative rather than through
  `process-and-capability-levels`.
- Skipping the cross-model check because both validators are green.
- Asking the Requester something the model already settles, or something about
  a state that does not exist yet.
- Writing a row for a gate that was never granted.

## ☑ Done when

- The depth is stated, and at Depth 3 the owning domain is named.
- Step 1c's verdict is recorded, whichever of the four it was.
- Every layer has a verdict in the scope document's alignment table.
- Every gate granted has a row, and no gate that was not granted has one.
- Every element added names what realizes it, or is marked Pending.
- Every other model this change falsifies has been corrected in the same change.
- The pull request covers the whole branch.
