# The method

_[← Repository README](../README.md)_

**What you get out of this is your own requirement, sharper than the one you
arrived with** — who it serves, what it has to do, and which of your
assumptions turned out to disagree with each other.

The one-paragraph version of how: **a change to what the model claims is
worked through numbered architecture layers, captured in a scope document,
and built directly from your request.** Your approval is the pull request
merging — nothing earlier claims to be one, and the agent stops before that
only when something contradicts what you have already decided or reads two
ways. A change inside something the model already names — a screen, a
filter, a file format — is just built, and the model stays true by
construction. You keep the strategy and business judgement; AI agents do the
modeling and the building in between, and every actor's kind and autonomy is
written down.

You are never asked to learn a notation to answer a question about your own
business. If you already know one, the model is a standard layered structure in
plain files you can navigate directly.

## The loop: Requester → Agent → Reviewer

Every change moves through three roles, and nothing assumes a human fills the
middle one: an AI agent and a person follow the same steps, in the same order,
against the same documents.

| Role | Who | Does |
| ---- | --- | ---- |
| **Requester** | You | Says what should change — a requirement or a problem, not a diff, in plain words |
| **Agent** | An AI agent (or a person) | Walks the architecture ladder, writes a short scope document, builds directly from the request, and opens a PR — stopping only when something contradicts what you have decided, reads two ways, or needs authorization |
| **Reviewer** | You | Reviews and merges. The merge is the approval; nothing ships without it |

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

**All six describe today**, which leaves two questions they cannot answer.

*Where did the estate come from, if no requirement ever asked for it?* An
organization modeled after the fact has processes, applications and
infrastructure no change request will ever produce. Layers 2–5 are filled for
it once, from evidence rather than from a requirement, by the
[`discover-current-landscape` skill](../plugins/archreator/skills/discover-current-landscape/SKILL.md)
— which stops where a declared boundary says, so a reader can tell what was left
out from what was missed.

*Where is it going?* That lives in `architecture/6_transition/`, the one folder
permitted to describe a future: target plateaus, the gaps between them and
today, and the order the gaps are closed in. The
[`plan-the-transition` skill](../plugins/archreator/skills/plan-the-transition/SKILL.md)
writes it, built directly and merged like any initiative — merging it
approves the direction, not permission to build any of it. Intent lives in
one folder so every numbered layer reads as a description of now.

## One method, three depths

The same six layers describe a weekend app and a twenty-business-line
company alike. What changes is **how much of them gets filled in.** Every
project declares one depth in `AGENTS.md`, and **the agent tells you which
depth it picked and why**.

| Depth | The subject is | You get | Approval |
| ----- | -------------- | ------- | -------- |
| **1 — Application** | one app or tool | a light strategy layer: goals and principles, enough to judge a change against | Your merge of the pull request |
| **2 — Organization** | a company, department, or service line | value proposition and business model canvases, and the operating model derived from them | Your merge of the pull request |
| **3 — Enterprise** | several business lines | the above, plus each line modeled as a domain with its own charter and service contracts | Your merge, and every affected domain's Requester told at the same pull request |

Depth is a starting posture, never a ceiling — deepening is a normal
change, not a restart.

## When it stops and asks you

**Nothing stops for approval before it is built.** The agent works from your
request directly, through the layers, and opens the result as a pull
request. **Your merge of that pull request is the approval** — nothing
earlier claims to be one.

Three things stop the work before that point, and the agent says which:

| Stop | It fires when |
| ---- | ------------- |
| **Contradiction** | The change conflicts with a principle, a decision already recorded, or a rule the model states |
| **Ambiguity** | Two readings of the request build different things, and nothing in the model settles which |
| **Authorization** | The work would commit you to spend, exposure, or publication you have not agreed to |

Naming the stop is what makes it answerable — "I need authorization before I
publish this" tells you what kind of answer is wanted; "is this okay?" does
not.

What a stop is checked against, and how it is presented, is defined in
exactly one place — the
[`align-change-through-layers` skill](../plugins/archreator/skills/align-change-through-layers/SKILL.md)
§ Where this stops. This page names the reasons; it does not restate the rule.

A bug fix, or a change inside an element the model already names, stops for
nothing and documents nothing; a change that only keeps a row true edits the
row in the same commit.

## Process flow

How a requirement gets from "someone wants a change" to "merged".

```mermaid
flowchart LR
  req(["⚇ Requester presents a requirement"])
  align["⚙ Agent aligns it through the layers"]
  build["⚙ Agent implements, keeping the documents true"]
  rev(["⚇ Reviewer reads the whole branch"])
  merged(["Merged — the approval"])

  req --> align --> build --> rev
  rev -->|changes requested| build
  rev -->|approved| merged

  classDef business fill:#fffbb5,stroke:#c8c04a,color:#333
  class req,align,build,rev,merged business
```

One loop, and it cannot be skipped: the Reviewer's, which runs before any
code merges. Where the Requester and the Reviewer are the same person — the
common case — that one review is the one approval there is.

Inside the Agent boxes there is branching — a "no change" verdict on a layer,
a "pure bug fix, no scope document" statement, a conflict with a Principle
already written down that stops the work, a call the agent took and recorded
as draft.
**Every one of those is stated and recorded, never a silent skip.** Drawn out,
that branching is the levelled process model in
[`docs/process/`](./process/README.md); written out step by step it is the
[`align-change-through-layers` skill](../plugins/archreator/skills/align-change-through-layers/SKILL.md).

## Where the model lives

Layer folders and files are numbered by assessment order. Each element
carries a short ID — a type prefix and a number, like `G1`, `CAP3`,
`BSVC2` — which extends its parent's where a catalogue has levels, so the
second capability under `CAP3` is `CAP3.2`. Every element names the code
artifact, page, or written procedure that realizes it, or is explicitly
marked "Pending — future initiative". Three validators in
[`plugins/archreator/scaffold/scripts/`](../plugins/archreator/scaffold/scripts/) enforce that references
resolve, that every leveled ID has a parent, that no identifier is reused, and
that a model page speaks about its subject rather than about its governance or
the method.

Beside the numbered layers sit the folders that are not layers:
`architecture/scope/` (one document per initiative), `architecture/decisions/`
(calls smaller than an initiative), `architecture/domains/` (Depth 3 only),
`architecture/6_transition/` (where it is going), `architecture/reference/`
(the source material the model was built from, dated, indexed, never published)
and `architecture/relationships.md`, the one catalogue of every relationship a
catalogue column does not carry — a human page draws and names its
relationships, and a machine reads them there.

**Every document that defines an element says how far it has been validated**,
with one of three glyphs in its preamble: `○` not started, `◐` a draft
catalogue, `●` validated, since a named date. A draft catalogue is
a list of things somebody said exist, written down with notes so they can be
checked — it is *not* an architecture draft, and on the page the two are
identical. The marker is what separates them, and `check_model.py` fails a
document that defines elements without declaring one.

The Markdown is the model, and a reader who never opens a repository is served
by rendering it rather than by a second copy: one command writes a
searchable-website configuration, a focused brief answers one question, and
everything generated is gitignored — see
[`docs/adopting.md`](./adopting.md#reaching-a-reader-who-will-not-open-the-repository).

The scaffold at [`plugins/archreator/scaffold/`](../plugins/archreator/scaffold/architecture/README.md) opens with a
status row per layer rather than empty folders; a layer's README arrives when
a skill first fills it. The full conventions — numbering, ArchiMate on
Mermaid, colour ramps, actor kinds — are in the
[`architecture-document-style` skill](../plugins/archreator/skills/architecture-document-style/SKILL.md)
and its references.
