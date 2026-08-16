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
gates apply.** Every project declares one depth in `CLAUDE.md`, and **the
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

| Gate | When | The Requester approves |
| ---- | ---- | ----------------------- |
| **Gate 0 — Business model** | Only when the initiative is modeling an organization | The canvases: Value Proposition per segment, Business Model per product |
| **Gate 1 — Strategy** | Only when strategy discovery is triggered | The strategy layer and the key business elements discovered with it |
| **Gate 2 — Business** | Every initiative that changes documented behavior | The changes (or explicit "no change" verdicts) to `1_strategy`, `2_business`, `3_information` |
| **Gate 3 — Solution design** | Only when the Requester opts in at Gate 2 | The solution architecture and logical application components |

Pure bug fixes that change no documented behavior pass no gates.

## Process flow

How a requirement gets from "someone wants a change" to "merged", and where
each actor's responsibility starts and ends.

```mermaid
flowchart TD
  subgraph REQ["Requester"]
    req(["Presents a requirement or reports a problem"])
    gate0{"Gate 0 — approve the business model?"}
    gate1{"Gate 1 — approve the strategy?"}
    gate2{"Gate 2 — approve strategy, business, information?"}
    gate3{"Gate 3 — approve the solution design?"}
  end

  subgraph AGENT["Agent (person or AI)"]
    depth["Confirm modeling depth; at Depth 3, locate the domain"]
    assess["Assess 1_strategy against the change"]
    canvases["Operating-model discovery — canvases, docs-only"]
    discovery["Strategy discovery — question-driven, docs-only"]
    dscope["Draft scope document"]
    conflict{"Contradicts an existing Principle?"}
    bugfix{"Pure bug fix — no documented behavior changes?"}
    walk23["Align 2_business and 3_information"]
    scopedoc["Draft scope document"]
    walk45["Align 4_application and 5_technology"]
    implement["Implement, keeping EA + scope docs true to the code"]
    verify["Verify alignment"]
    openpr["Open PR"]
    address["Address review feedback"]
  end

  subgraph REV["Reviewer"]
    review{"Approve?"}
  end

  stop[["Stop — surface the conflict to the Requester"]]
  merged(["Merged"])

  req --> depth --> assess
  assess -->|the subject is an organization| canvases
  canvases --> dscope --> gate0
  gate0 -- changes requested --> canvases
  gate0 -- approved --> discovery
  assess -->|strategy is placeholders, or the change shifts it| discovery
  discovery --> dscope
  dscope --> gate1
  gate1 -- changes requested --> discovery
  gate1 -- approved --> verify
  assess --> conflict
  conflict -- yes --> stop
  stop -.->|Requester resolves| req
  conflict -- no --> bugfix
  bugfix -- yes --> implement
  bugfix -- no --> walk23 --> scopedoc --> gate2
  gate2 -- changes requested --> walk23
  gate2 -- approved --> walk45
  walk45 -->|Gate 3 requested| gate3
  gate3 -- changes requested --> walk45
  gate3 -- approved --> implement
  walk45 -->|Gate 3 not requested| implement
  implement --> verify --> openpr --> review
  review -- changes requested --> address --> openpr
  review -- approved --> merged
```

Every arrow into the Agent subgraph is a decision the agent makes
explicitly and records — a "no change" verdict on an EA layer, a "pure bug
fix, no scope document" statement, a gate approval written into the
Approvals table, an open question logged for the Requester — never a silent
skip.

The step-by-step version of this same flow lives in the
[`core-architecture-first-change` skill](../plugins/archreator/skills/core-architecture-first-change/SKILL.md).

## Where the model lives

Layer folders and files are numbered by assessment order. Each element
carries a short ID — a type prefix and a number, like `G1`, `CAP3`,
`BSVC2` — which extends its parent's where a catalogue has levels, so the
second capability under `CAP3` is `CAP3.2` and its first sub-capability is
`CAP3.2.1`. The whole set is grounded: every element names the code
artifact, page, or written procedure that realizes it, or is explicitly
marked "Pending — future initiative". Two validators in
[`plugins/archreator/templates/scripts/`](../plugins/archreator/templates/scripts/) enforce that references
resolve, that every leveled ID has a parent, and that no identifier is reused.

The scaffold at [`plugins/archreator/templates/`](../plugins/archreator/templates/README.md) has every layer
README ready to fill in. The full conventions — numbering, ArchiMate on
Mermaid, colour ramps, actor kinds — are in
[`plugins/archreator/templates/architecture/README.md`](../plugins/archreator/templates/architecture/README.md)
and in the [`core-architecture-doc-style` skill](../plugins/archreator/skills/core-architecture-doc-style/SKILL.md).
