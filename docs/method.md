# The method

_[← Repository README](../README.md)_

The one-paragraph version: **a requirement never becomes code directly.** It
is aligned through numbered architecture layers, stopped at explicit
approval gates the Requester grants, captured in a scope document, and only
then implemented. Humans keep strategy and business judgement; AI agents do
the modeling and the building in between, and every actor's kind and
autonomy is written down.

## The loop: Requester → Agent → Reviewer

Every change moves through three roles. Nothing here assumes a human fills
the middle one — an AI agent and a person follow the same steps, in the
same order, against the same documents.

| Role | Who | Does |
| ---- | --- | ---- |
| **Requester** | You | Says what should change — a requirement or a problem, not a diff. **Grants the gate approvals** before any code is written |
| **Agent** | An AI agent (or a person) | Walks the architecture ladder, stops at each gate for the Requester's approval, writes a short scope document, implements, and opens a PR |
| **Reviewer** | You | Reviews and merges. Nothing ships without a human approving it |

## The six layers

The architecture folder is numbered in the order layers are assessed.
Deriving one before the one above it is validated is what the whole method
exists to prevent.

| # | Layer | Answers |
| - | ----- | ------- |
| 0 | Business design | Who are the customers, what do they need, and how does each offering pay? |
| 1 | Strategy | Why does this exist? Who cares? What capabilities and value stream? |
| 2 | Business | Who does what? Which services are offered, through which processes? |
| 3 | Information | What information exists, where does it live, how does it flow? |
| 4 | Application | Which software services and components realize the business services? |
| 5 | Technology | What runs it all — runtimes, tooling, build, hosting, deployment? |

Layer 0 is the odd one out — it holds no ArchiMate elements, only the
Value Proposition and Business Model canvases the architecture is derived
from. It is filled only when the initiative is modeling an organization.

## One method, three depths

The same six layers describe a weekend app and a twenty-business-line
company alike. What changes is **how much of them gets filled in and which
gates apply.** Every project declares one depth in `AGENTS.md`, and **the
agent tells you which depth it picked and why**.

| Depth | The subject is | You get | Gates |
| ----- | -------------- | ------- | ----- |
| **1 — Application** | one app or tool | a light strategy layer: goals and principles, enough to judge a change against | one, before code |
| **2 — Organization** | a company, department, or service line | value proposition and business model canvases, and the operating model derived from them | four |
| **3 — Enterprise** | several business lines | the above, plus each line modeled as a domain with its own charter and service contracts | four, plus every affected domain's owner |

Depth is a starting posture, never a ceiling — deepening is a normal
change, not a restart.

## The gates

Approval is granted by the Requester and recorded in the scope document's
**Approvals** table — which gate, who approved, when, and what was shown. A
gate that didn't apply gets an `N/A — <why>` row rather than being deleted.
An approval that isn't recorded didn't happen.

There are four: **Gate 0 — Business model**, **Gate 1 — Strategy**,
**Gate 2 — Business**, and **Gate 3 — Solution design**. Which of them applies
to a given change, and what the Requester is shown at each, is defined in
exactly one place — the
[`align-change-through-layers` skill](../plugins/archreator/skills/align-change-through-layers/SKILL.md)
§ The gates. This page names the gates; it does not restate the rule, because a
second copy is a second thing to drift.

Pure bug fixes that change no documented behavior pass no gates.

## Process flow

How a requirement gets from "someone wants a change" to "merged", and where
each actor's responsibility starts and ends.

```mermaid
flowchart LR
  req(["⚇ Requester presents a requirement"])
  align["⚙ Agent aligns it through the layers"]
  gates{{"❖ Gates 0–3 — the Requester approves"}}
  build["⚙ Agent implements, keeping the documents true"]
  rev(["⚇ Reviewer reads the whole branch"])
  merged(["Merged"])

  req --> align --> gates
  gates -->|changes requested| align
  gates -->|approved| build --> rev
  rev -->|changes requested| build
  rev -->|approved| merged

  classDef business fill:#fffbb5,stroke:#c8c04a,color:#333
  classDef implementation fill:#ffd6d6,stroke:#d99b9b,color:#333
  class req,align,build,rev,merged business
  class gates implementation
```

Two loops, and neither can be skipped: the Requester's, which runs before any
code exists, and the Reviewer's, which runs before any code merges.

Inside the Agent boxes there is branching — a "no change" verdict on a layer,
a "pure bug fix, no scope document" statement, a conflict with an approved
Principle that stops the work, an open question logged for the Requester.
**Every one of those is stated and recorded, never a silent skip.** Drawn out,
that branching is the levelled process model in
[`docs/process/`](./process/README.md); written out step by step it is the
[`align-change-through-layers` skill](../plugins/archreator/skills/align-change-through-layers/SKILL.md).

## Where the model lives

Layer folders and files are numbered by assessment order. Each element
carries a short ID — a type prefix and a number, like `G1`, `CAP3`,
`BSVC2` — which extends its parent's where a catalogue has levels, so the
second capability under `CAP3` is `CAP3.2` and its first sub-capability is
`CAP3.2.1`. The whole set is grounded: every element names the code
artifact, page, or written procedure that realizes it, or is explicitly
marked "Pending — future initiative". Two validators in
[`plugins/archreator/scaffold/scripts/`](../plugins/archreator/scaffold/scripts/) enforce that references
resolve, that every leveled ID has a parent, and that no identifier is reused.

The scaffold at [`plugins/archreator/scaffold/`](../plugins/archreator/scaffold/architecture/README.md) has every layer
README ready to fill in. The full conventions — numbering, ArchiMate on
Mermaid, colour ramps, actor kinds — are in
[`plugins/archreator/scaffold/architecture/README.md`](../plugins/archreator/scaffold/architecture/README.md)
and in the [`architecture-document-style` skill](../plugins/archreator/skills/architecture-document-style/SKILL.md).
