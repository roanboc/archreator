---
name: discover-strategy
description: Use when the align-change-through-layers process finds that a change needs a new or significantly revised strategy — the strategy layer still contains template placeholders (first real initiative of a project created from the template), or the change adds/modifies a Stakeholder, Driver, Goal, or Principle, or reshapes the value stream. Runs a question-driven discovery with the Requester to document the strategy and the key business elements, ending at an explicit strategy approval gate (Gate 1) before anything else is built.
---

# Strategy discovery

_Reached from `align-change-through-layers` Step 1c. `README.md`
orients a person; `CONTRIBUTING.md` draws where
this branch sits in the whole flow._

When this skill applies, **the entire initiative is discovery**: no code,
no application design, no stack decisions. The deliverables are the
strategy layer, the key business elements it implies, and a scope document
recording the Requester's **Gate 1 — Strategy** approval. Implementation —
whatever request originally triggered the discovery — follows as a
separate initiative through the normal `align-change-through-layers` process, which
will then find the strategy filled in and current.

## How to run the conversation

- **Ask, don't assume.** Every element in the strategy docs comes from a
  Requester answer, an existing document, or observable fact — never from
  what a project like this "usually" wants. What the Requester can't
  answer yet is marked **"Pending — future initiative"** or logged as an
  open question with the interpretation you adopted (see `write-scope-document`).
- **Small batches, one theme at a time.** Ask 3–5 questions per round,
  following the theme order below. Phrase them in the Requester's business
  language, not in ArchiMate vocabulary — "who would be upset if this
  didn't exist?" beats "enumerate your stakeholders".
- **Write as you go, and show it back.** After each round, update the
  affected documents (per `architecture-document-style`) and reflect a short summary back
  to the Requester so misunderstandings surface immediately — the docs are
  the record of the conversation, not a transcript kept elsewhere.
- **Consolidate as you go.** Goals that differ only in wording are one goal;
  a capability named twice at different granularity is one capability. Merge
  per round rather than at the end, per `architecture-document-style` § Consolidate before
  you enumerate. A strategy layer with six load-bearing goals is worth more
  than one with twenty, because every later initiative gets checked against
  it and nobody checks against twenty.
- **Revision, not amnesia.** If the strategy layer already has real
  content (trigger was a strategy *shift*, not a blank template), start
  from what's documented: confirm what still holds, and focus the
  questions on what the new requirement bends or breaks.
- **Derive, don't re-ask.** If
  `architecture/0_business-design/README.md`
  is filled in, the Requester has already answered most of theme 1, 2, 4
  and 5 in business language and approved the answers at Gate 0. Start each
  theme from the canvas blocks it derives from — per the mapping in that
  folder's README — draft the elements, and ask only what the canvases
  leave genuinely open. Re-asking questions the Requester already answered
  on a canvas is how a gated process loses their trust. Note the source
  block on each derived element so the trace back to the canvas survives.

## Question themes, in order

The order matches the strategy layer's own analysis order (see
`architecture/1_strategy/README.md`): who wants what and why, then what we must
be able to do, then how value flows — and only then the key business
elements underneath.

1. **Stakeholders and drivers** (`1_motivation.md`): Who cares whether
   this exists — users, owners, payers, regulators? What pressures them
   (cost, time, risk, obligation, opportunity)? Who can veto or must
   sign off?
2. **Goals and outcomes** (`1_motivation.md`): What must become true for
   this to be worth building? How would the Requester recognize success —
   what observable outcome, by when? What is explicitly *not* a goal?
3. **Principles** (`1_motivation.md`): What must always — or never — be
   true, regardless of feature? Keep them few, load-bearing, and testable
   ("role determines access", not "be secure"); these are what every
   future change gets checked against. **No canvas block feeds this
   theme** — principles are discovered directly with the Requester on both
   tracks, so ask these questions even when the canvases are filled.
4. **Capabilities and resources** (`2_capabilities-and-resources.md`):
   What must the project be able to do to reach those goals? With what —
   people, systems, data, budget — and what is missing today? **On an
   organization, this theme runs through `process-and-capability-levels`**:
   capabilities are leveled, seeded from a named industry reference as a
   proposal the Requester confirms, and detailed below level 2 only where a
   pain justifies it. Asking an organization to recall its capabilities from
   a blank page is the version of this theme that produces an org chart.
5. **Value stream** (`3_value-stream.md`): From the first stakeholder
   need to value delivered, what are the stages? Which capability serves
   each stage?
6. **Key business elements** (`architecture/2_business/`): Who are the actors
   and roles — and is any role performed or assisted by an AI, at what
   autonomy level and decision rights (`architecture-document-style`'s actor notation)?
   What core services are offered, what main business objects are handled,
   and which terms and rules came up repeatedly (they seed the glossary
   and rules table)? On an organization, ask what process map already exists —
   a quality management system often holds a correct level 1 — and shape what
   you find with `process-and-capability-levels`.

Theme 6 discovers the **key** business elements — enough for the strategy
to be judged coherent and for Gate 1 to mean something. The full business
and information alignment still happens per initiative in `align-change-through-layers`
steps 2–4.

## Deliverables

A docs-only initiative:

- `architecture/1_strategy/` filled in (or revised), and the key business
  elements captured in `architecture/2_business/`;
- a scope document (`write-scope-document` skill) whose EA-alignment table records
  the impact on layers 1–2 and an explicit "not started" / "no change"
  verdict for the rest, and whose Approvals table records Gate 1;
- open questions logged for everything adopted-but-unconfirmed.

## Before the gate — create the scope document

Discovery is a full initiative, not a detour, so it gets its own scope
document like any other. **Create it before presenting Gate 1**, not after:
the Requester should approve against a concrete document, and the approval
needs somewhere to be recorded the moment it is granted.

Using the `write-scope-document` skill, add the next-numbered file to `architecture/scope/`
and its row to `architecture/scope/README.md`'s index. On this track the EA
alignment table records the impact on layers 1–2 with an explicit "not
started" verdict for the rest, and the Approvals table carries a Gate 1 row
plus `N/A` rows for the gates that don't apply (Gate 2 and Gate 3 always;
Gate 0 unless `discover-business-model` handed off to you, in which case
it is already recorded).

## Gate 1 — Strategy approval

When the themes are exhausted (or the Requester's answers are), present
one compact summary — stakeholders, drivers, goals, principles, value
stream, key business elements — with **full branch links to each document
behind it** (`align-change-through-layers` § Show the Requester what they are approving),
and ask explicitly for approval of the strategy. Record the approval in the
scope document's Approvals table (who, when, what was shown). Only after
Gate 1 is granted may an implementation initiative build on this strategy;
if changes are requested, revise and present again.
