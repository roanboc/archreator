# Level 2 — the processes

_[← The process model](./README.md) · [Level 1](./1_level-1-macro-processes.md)_

Every level-2 process, with the full supplier-input-output-customer set. `Realized
by` is the [grounding rule](../../plugins/archreator/skills/architecture-document-style/SKILL.md)
on the method's own track — a process here is realized by a written procedure, and a
skill is a written procedure.

## `BPROC1` — Establish the architecture model

| ID | Process | Purpose | Trigger | Suppliers | Inputs | Outputs | Customers | Owner role | Realized by |
| -- | ------- | ------- | ------- | --------- | ------ | ------- | --------- | ---------- | ----------- |
| `BPROC1.1` | Establish the project | Turns a fresh copy of the scaffold into a named project with a declared depth every later process relies on | A repository exists from the scaffold and has not been set up | Requester | What is being built; how deep to model it | A named project; a declared modeling depth; the first scope document | `BPROC1.2` or `BPROC1.3` | Agent | `establish-project` |
| `BPROC1.2` | Discover the business model | Turns what the Requester knows about customers and offerings into approved canvases the strategy is derived from | The subject is an organization, not a single application | Requester | Customers, offerings, revenue, partners | A Value Proposition canvas per segment; a Business Model canvas per product; **Gate 0** recorded | `BPROC1.3` | Requester approves, Agent drafts | `discover-business-model` |
| `BPROC1.3` | Discover the strategy | Turns approved canvases, or an empty template, into a strategy layer a change can be judged against | The strategy layer is unfilled, or a change shifts it | `BPROC1.2`; Requester | Approved canvases, or a placeholder strategy layer | A filled `1_strategy/`; the key business elements found with it; **Gate 1** recorded | `BPROC2.1` | Requester approves, Agent drafts | `discover-strategy`, shaped by `process-and-capability-levels` |
| `BPROC1.4` | Split the model into domains | Turns one enterprise tree that has outgrown itself into domains with contracts between them | The organization has several business lines, or a change crosses a boundary | Requester; `BPROC1.3` | An enterprise-level model that has outgrown one tree | One charter per domain, with its exposed and consumed services | `BPROC2.1`; each domain's Requester | Agent | `model-domains` |

## `BPROC2` — Deliver an architected change

| ID | Process | Purpose | Trigger | Suppliers | Inputs | Outputs | Customers | Owner role | Realized by |
| -- | ------- | ------- | ------- | --------- | ------ | ------- | --------- | ---------- | ----------- |
| `BPROC2.1` | Align the change through the layers | Turns a requirement into approved changes to the upper layers, or explicit verdicts that none were needed | A Requester presents a requirement or reports a problem | Requester; `BPROC1.3` | The requirement; the current `architecture/` | Changed layer documents, or explicit "no change" verdicts; a scope document; **Gate 2** and, if requested, **Gate 3** | `BPROC2.2` | Agent | `align-change-through-layers` Steps 0–5, `write-scope-document` |
| `BPROC2.2` | Implement and verify | Turns an approved scope document into code the architecture documents are still true of | A scope document has passed its gates | `BPROC2.1` | The approved scope document; the aligned layer documents | Code; architecture and scope documents still true to it; a green validator run | `BPROC2.3` | Agent | `align-change-through-layers` Steps 6–7, `shard-stories`, `stack-selection` |
| `BPROC2.3` | Hand over for review | Turns a finished branch into a pull request a Reviewer can judge without reading every commit | The work is implemented and verified | `BPROC2.2` | The whole branch, `main...HEAD` | A pull request describing every change on the branch | Reviewer | Agent | `align-change-through-layers` Step 8, `write-pr-description` |

## `BPROC3` — Keep the model true

| ID | Process | Purpose | Trigger | Suppliers | Inputs | Outputs | Customers | Owner role | Realized by |
| -- | ------- | ------- | ------- | --------- | ------ | ------- | --------- | ---------- | ----------- |
| `BPROC3.1` | Restate the current state | Turns a model carrying its own history into one that reads as a description of today | The model has accumulated shipped "Pending"s, superseded elements and resolved questions | `BPROC2.2`; elapsed time | A model carrying its own history | Layer documents that read as a description of today; a Retired section; **Gate 2** recorded | Requester; the next `BPROC2.1` | Agent | `restate-current-state` |
| `BPROC3.2` | Record a decision | Turns a call too small for an initiative into a rationale the next reader can find | A call too small for an initiative but too consequential to leave unrecorded | Requester; Agent | The constraint, risk or requirement that made the call non-obvious | A numbered decision record, indexed | The next reader who asks "why this and not the alternative?" | Agent | `record-decision` |

## `BPROC4` — Learn from the engagement

| ID | Process | Purpose | Trigger | Suppliers | Inputs | Outputs | Customers | Owner role | Realized by |
| -- | ------- | ------- | ------- | --------- | ------ | ------- | --------- | ---------- | ----------- |
| `BPROC4.1` | Run the engagement retrospective | Turns what the method failed to cover into written proposals, before the memory of it evaporates | An initiative or engagement just finished | `BPROC2.3` | What the method did and did not cover, while it is still remembered | A retrospective note carrying proposals | Whoever maintains the method | Whoever did the work | `run-retrospective` |

## The four skills that realize no process

They should not be made to. A rule is not a step.

| Skill | What it is |
| ----- | ---------- |
| [`document-style`](../../plugins/archreator/skills/document-style/SKILL.md) | The rules every document in the repository obeys, whatever it is about |
| [`architecture-document-style`](../../plugins/archreator/skills/architecture-document-style/SKILL.md) | What a model adds on top of those — identifiers, notation, tiers, actors |
| [`process-and-capability-levels`](../../plugins/archreator/skills/process-and-capability-levels/SKILL.md) | How far a catalogue decomposes, and how its levels are shaped |
| [`stack-selection`](../../plugins/archreator/skills/stack-selection/SKILL.md) | A decision aid, reached for inside `BPROC2.2` |

**Processes and skills bind many-to-many, and neither side is the other's index.**
A process boundary is drawn by accountability — one trigger, one definable output,
one owner role. A skill boundary is drawn by activation — when an agent reaches for
it, and what must be in context when it does. `align-change-through-layers` spans
all three of `BPROC2`'s children because that is the coherent unit an agent
activates on; splitting it to match the process model would serve the diagram at the
reader's expense.
