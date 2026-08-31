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

**All six describe today.** That is what makes them worth reading, and it
leaves two questions they cannot answer.

*Where did the estate come from, if no requirement ever asked for it?* An
organization that existed before it was modeled has processes, applications and
infrastructure that no change request will ever produce. Layers 2–5 are filled
for it once, from evidence rather than from a requirement, by the
[`discover-current-landscape` skill](../plugins/archreator/skills/discover-current-landscape/SKILL.md)
— which stops where a declared boundary says, so a reader can tell what was left
out from what was missed.

*Where is it going?* That lives in `architecture/6_transition/`, the one folder
permitted to describe a future: target plateaus, the gaps between them and
today, and the order the gaps are closed in. The
[`plan-the-transition` skill](../plugins/archreator/skills/plan-the-transition/SKILL.md)
writes it, and the Requester approves it as **direction** — not as permission
to build any of it. Keeping intent in one folder is what lets every numbered
layer be read as a description of now without checking its date.

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

## When it stops and asks you

**Three gates, named for what you approve**, and the names are the ones the
[repository README](../README.md#how-it-works) already uses on its two
pictures:

| Gate | You approve | It applies when |
| ---- | ----------- | --------------- |
| **Direction** | Where this is going — the canvases where the subject is an organization, then the strategy derived from them, or a roadmap | The change moves *why* or *for whom* |
| **Understanding** | Who does what, and with which information — before any code exists | Every change that will produce code |
| **Design** | What builds it, before it is built | Only if you ask, when you are offered it at Understanding |

**A single application meets one gate and one offer.** Understanding is
mandatory; Design is offered at it. Direction belongs to modeling an
organization or settling a direction, so a Depth 1 project never sees it — and
gets no row saying so, because a gate that could not have applied is not a gate
that was skipped.

Direction may be granted in two sittings where the subject is an organization —
the canvases first, the strategy derived from them second — and it is still one
gate, because both are the same act: settling where this is going.

Approval is granted by the Requester and recorded in the scope document's
**Approvals** table — which gate, who approved, when, and what was shown. An
approval that isn't recorded didn't happen. Only a gate that *could* have
applied and did not gets an `N/A — <why>` row.

Between the gates, two things stop the work, and the agent says which:
**material uncertainty** (two readings of the request build different things,
and nothing in the model settles it) and **authorization** (the work would
commit you to spend, exposure, or publication you have not agreed).

Which gate applies to a given change, and what you are shown at each, is
defined in exactly one place — the
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
  gates{{"❖ the three gates — the Requester approves"}}
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

Beside the numbered layers sit the folders that are not layers:
`architecture/scope/` (one document per initiative), `architecture/decisions/`
(calls smaller than an initiative), `architecture/domains/` (Depth 3 only),
`architecture/6_transition/` (where it is going) and `architecture/reference/` (the
transcripts, decks and documents the model was built from, kept as they
arrived, dated, indexed, and never published).

**Every document that defines an element says how far it has been validated**,
with one of three glyphs in its preamble: `○` not started, `◐` a draft
catalogue, `●` validated at a named gate on a named date. The middle one is
the one that matters. A draft catalogue is a list of things somebody said
exist, written down with notes so they can be checked — it is *not* an
architecture draft, and on the page the two are identical. A Requester shown a
catalogue and told "architecture" approves a description nobody verified; an
agent that reads one builds on a system mentioned once in a meeting. The
marker is what separates them, and `check_model.py` fails a document that
defines elements without declaring one.

The Markdown is the model, and the readers who never open a repository are
served by rendering it rather than by keeping a second copy: one command
publishes the same documents as a searchable website, another prints them as a
single PDF, and both are regenerated and gitignored — see
[`docs/adopting.md`](./adopting.md#reaching-a-reader-who-will-not-open-the-repository).

The scaffold at [`plugins/archreator/scaffold/`](../plugins/archreator/scaffold/architecture/README.md) has every layer
README ready to fill in. The full conventions — numbering, ArchiMate on
Mermaid, colour ramps, actor kinds — are in
[`plugins/archreator/scaffold/architecture/README.md`](../plugins/archreator/scaffold/architecture/README.md)
and in the [`architecture-document-style` skill](../plugins/archreator/skills/architecture-document-style/SKILL.md).
