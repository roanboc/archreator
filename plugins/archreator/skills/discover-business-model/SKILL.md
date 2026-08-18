---
name: discover-business-model
description: Use when the initiative is modeling an organization rather than building a single application — a company, a department, or a service line whose operating model is itself the deliverable. Runs a question-driven discovery with the Requester over the Value Proposition Canvas and a Business Model Canvas per product, ending at an explicit business-model approval gate (Gate 0), then hands off to discover-strategy to derive the enterprise architecture from it.
---

# Operating model discovery

_Reached from `align-change-through-layers` Step 1c, or from `establish-project` on a
project whose subject is an organization. `README.md`
orients a person; `CONTRIBUTING.md` draws where
this branch sits in the whole flow._

The company track. When this skill applies, **the product is the
architecture**: the deliverable is a documented business model and the
operating model derived from it — no application design, no stack
decisions, no code. Whatever gets built later is a separate initiative that
runs the normal `align-change-through-layers` process and finds the organization
already modeled.

Use this instead of `discover-strategy` when the thing being modeled is an
organization. Use `discover-strategy` directly when it is a single
application. The two are not alternatives to each other for the same
subject — this skill **runs first and then hands off**, because a company's
strategy layer is a consequence of its business model, not an independent
statement.

## When this applies

- The Requester is describing a business, not a feature: customers,
  offerings, revenue, partners, staff.
- Several products or services share one set of capabilities, and the
  question "who does what" has an answer bigger than one team.
- The model is meant to outlive any one application — other projects will
  consume it as the organization's shared source of truth.

If none of that is true, stop and use `discover-strategy`.

## How to run the conversation

The rules are the same as `discover-strategy`'s, and they matter more here
because the subject is a real business the Requester knows far better than
you do:

- **Ask, don't assume.** Every block on every canvas comes from a Requester
  answer, an existing document, or observable fact — never from what a
  business of this kind "usually" looks like. Generic canvas filler is
  worse than a blank: it reads as agreed when nobody agreed it. What the
  Requester can't answer yet is marked **"Pending — future initiative"** or
  logged as an open question with the interpretation you adopted.
- **Small batches, one theme at a time.** Ask 3–5 questions per round, in
  the theme order below. Business language, not canvas jargon — "what do
  they try that doesn't work today?" beats "enumerate the pains".
- **Write as you go, and show it back.** Update the canvas documents after
  each round and reflect a short summary back, so a misread segment
  surfaces in minutes rather than at the gate.
- **Consolidate as you go, not at the end.** Discovery generates elements
  fast — a round of questions about pains easily yields twelve. Before
  writing them down, merge the ones that are the same pain felt at different
  severity, or the same job seen from two segments, and give the survivor a
  per-segment column instead. `architecture-document-style` § Consolidate before you
  enumerate has the rules. Doing this at the end means renumbering
  everything; doing it per round means the canvas is always readable, and the
  Requester is reviewing a model rather than a transcript.
- **One segment and one product at a time.** Finish a customer segment's
  profile before starting the next. Finish a product's nine blocks before
  starting the next. Canvases filled in parallel drift into each other.
- **Revision, not amnesia.** If canvases already exist, start from them:
  confirm what still holds and focus on what the new requirement bends.

## Question themes, in order

Themes 1–6 fill `architecture/0_business-design/1_value-proposition-canvas.md`,
one canvas per customer segment. Theme 7 fills
`2_business-model-canvas.md`, one canvas per product.

1. **Customer segments.** Who pays, who uses, and who decides — often three
   different people? Which of them would notice first if the business
   stopped? Which segment is the business actually built around, if it had
   to pick one?
2. **Jobs.** What is each segment trying to get done — the functional job,
   but also the social one (how it makes them look) and the emotional one
   (what it stops them worrying about)? What are they doing about it today,
   including doing nothing?
3. **Pains.** What goes wrong with that today — cost, delay, risk, effort,
   the outcome simply not arriving? What have they tried that didn't work?
   What would they call unacceptable rather than merely annoying?
4. **Gains.** What would they call a win — required, expected, or a
   delight? How would they measure it? What would make them recommend it to
   someone else?
5. **Products and services.** What is actually sold, as a customer would
   name it? Which segment is each one for? Is it one product with tiers, or
   genuinely separate products with separate economics — this decides how
   many business model canvases theme 7 needs.
6. **Pain relievers and gain creators.** For each pain, what specifically
   removes it — and for each gain, what produces it? This is where fit gets
   tested: an unaddressed pain means either a missing capability or a
   customer the business has decided not to serve, and the Requester should
   say which out loud.
7. **Business model, per product.** For each product from theme 5, the nine
   blocks in Osterwalder's order — value propositions, customer segments,
   channels, customer relationships, revenue streams, key resources, key
   activities, key partners, cost structure. Useful probes: how does a
   customer first hear about this, and how do they buy it? What is billed —
   time, seats, usage, outcome? What would stop the business tomorrow if
   the supplier vanished? Which single cost line dominates?

Ask, at theme 7 and again while deriving, whether any activity or role is
performed or assisted by an **AI system** — and if so at what autonomy
level, with what decision rights, and escalating to which role. An
organization that has AI in its delivery or in its products should say so
in the model rather than leave it implicit (see `architecture-document-style`'s actor
notation).

## Before the gate — create the scope document

Discovery is a full initiative, not a detour, so it gets its own scope
document like any other. **Create it before presenting Gate 0**, not after:
the Requester should approve against a concrete document, and the approval
needs somewhere to be recorded the moment it is granted.

Using the `write-scope-document` skill, add the next-numbered file to `architecture/scope/` and
its row to `architecture/scope/README.md`'s index. One document covers this whole
track — the same file gains its Gate 1 row when `discover-strategy` takes
over, so don't open a second one at the handoff.

## Gate 0 — Business model approval

When the themes are exhausted (or the Requester's answers are), verify fit
before presenting anything: every Pain has a Pain Reliever, every Gain has
a Gain Creator, every Product has its own business model canvas. Fix or
flag the gaps — do not quietly present an unfit canvas.

Then present one compact summary — segments, their jobs, the sharpest
pains and gains, the products, and for each product the blocks that
distinguish it (revenue, channels, dominant cost) — with **full branch links
to each canvas document** (`align-change-through-layers` § Show the Requester what they
are approving), and ask explicitly for approval of the business model.

Name the consolidation in the summary: how many elements each catalogue
holds, and what was merged to get there. A Requester who can see that twelve
pains became five is being shown a modeling decision they can overturn — and
that decision is usually more consequential than any single element in the
list.

**In the summary and the scope document — not in the canvas.** The canvas
describes the business; how many elements it took to describe it is a fact
about the modeling, and belongs where the decision is recorded
(`architecture-document-style` § What the document contains).

Record the approval in the scope document's Approvals table (who, when,
what was shown). If changes are requested, revise and present again.

**Nothing is derived until Gate 0 is granted.** The whole point of the
ordering is that the strategy layer is a consequence of an approved
business model; deriving from an unapproved canvas means redoing layers 1
and 2 when the canvas moves.

## Handing off to strategy discovery

Once Gate 0 is granted, run `discover-strategy` — which will find the
canvases filled and **derive rather than re-ask**. Its themes map onto the
canvas blocks per the mapping in
`architecture/0_business-design/README.md`;
the only theme with no canvas source is **Principles**, which is still
discovered directly with the Requester. That handoff ends at **Gate 1 —
Strategy**, as usual.

The capabilities and processes derived there are **leveled**, and how far down
they go is decided rather than assumed — `process-and-capability-levels` holds
that, including the rule that pays for this whole track's breadth: levels 1
and 2 complete, level 3 only where one of the Pains on the canvas you just had
approved justifies it. The Pains are what make that rule usable, which is why
it lands on this track and not on the application one.

## Deliverables

A docs-only initiative:

- `architecture/0_business-design/1_value-proposition-canvas.md` — one canvas
  per customer segment, plus the fit check;
- `architecture/0_business-design/2_business-model-canvas.md` — one canvas per
  product, plus the revenue and cost tables keyed to element IDs;
- the strategy and key business layers derived from them via
  `discover-strategy`;
- a scope document (`write-scope-document` skill) whose EA-alignment table records the
  impact on layers 0–2 and an explicit "not started" verdict for the rest,
  and whose Approvals table records **both Gate 0 and Gate 1**;
- open questions logged for everything adopted-but-unconfirmed.

Follow `architecture-document-style` for numbering, element IDs, ArchiMate-on-Mermaid
notation, and the grounding rule. The grounding rule reads differently on
this track: an organization's business processes are realized by people and
procedures, not source files, so name the team, role, or written procedure
that realizes each element — or mark it "Pending — future initiative".
