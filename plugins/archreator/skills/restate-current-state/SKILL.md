---
name: restate-current-state
description: Use when the model has accumulated history that obscures what is true now — shipped work still marked "Pending", superseded elements still listed as live, resolved open questions still in the pending table, decision records that no longer bind, or a Requester asking "what does this actually look like today?". Compacts the current-state documents so only live elements remain, without rewriting the immutable record of how they got there.
---

# Restating the current state

`architecture/` describes the **current** state. `architecture/scope/` and
`architecture/decisions/` describe **how it got there**. Over a dozen initiatives
those two drift into each other: elements marked "Pending" that shipped
three initiatives ago, services that were replaced but never removed,
open questions answered in a conversation nobody wrote down, decision
records superseded in practice but not in status.

The result is a model that is still *accurate* line by line and no longer
*true* as a whole — a reader can't tell which parts describe today. This
skill fixes that.

## The one rule that governs this skill

**Restating changes the current-state documents. It never rewrites
history.**

| Rewritable — it describes now | Immutable — it describes then |
| ----------------------------- | ----------------------------- |
| Everything under `architecture/` | Merged scope documents in `architecture/scope/` |
| `architecture/scope/README.md`'s index and `open-questions.md` | The Approvals tables inside them |
| A decision record's **Status** line | A decision record's Context, Options, Decision, Consequences |
| Layer README state tables | Anything a Requester approved at a gate |

A merged scope document is the record of what was approved on a date. If it
becomes wrong, it doesn't get corrected — it gets superseded by a later one,
which is the whole reason the index is chronological. Editing it would erase
the evidence that a gate was passed against different information.

**One carve-out: link targets, not words.** When a later change renames or
moves a file, a merged document's links stop resolving. Repair the path and
leave every word alone, link text included. A dangling link makes the record
less usable without making it more truthful — fixing the path preserves the
history, and changing a claim would rewrite it. See `write-scope-document` § Rules.

**An approved element's ID is never reused.** A retired element's ID stays
retired. If you find yourself wanting to reassign `BSVC3` because the old one
is gone, stop: a stale reference must fail loudly, not silently resolve to
something else.

The rule starts at the gate, not at first writing — an element removed before
it was ever approved is renumbered out of the sequence and leaves nothing
behind (`architecture-document-style` § Never-reused starts at the gate). By the
time this skill runs, everything in the model has been through a gate, so in
practice restatement only ever meets permanent identifiers.

## When to run it

- Before a Requester reviews the model as a whole, or onboards someone to it.
- After a run of initiatives that each left a "Pending" behind.
- When `open-questions.md`'s Pending table has rows nobody remembers.
- On a fixed cadence if the project has one — quarterly is plenty.
- **Not** as part of an ordinary initiative. Restating is its own change,
  with its own scope document, precisely so the diff is reviewable as
  "what changed about our picture of today" and nothing else.

## Step 1 — Find what has gone stale

Work through the model and collect, without changing anything yet:

1. **Pendings that shipped.** Every element marked "Pending — future
   initiative": does the thing now exist? Check the repository, or ask
   whether the team, role, or procedure is now real. This is the most common
   staleness and the most damaging, because a shipped Pending makes the
   model look further behind than it is.
2. **Elements with nothing realizing them.** The inverse: an element that
   claims a realizing artifact which no longer exists. The grounding rule
   says it must name something real — if the module was deleted, either the
   element is retired or it becomes Pending again.
3. **Superseded elements.** Two elements describing the same thing at
   different times, where only one is live. Usually a service replaced by a
   better one, or a role that was split.
4. **Resolved open questions.** Rows in `open-questions.md`'s Pending table
   that were answered — in a gate conversation, a PR thread, or by the
   passage of events.
5. **Decision records that no longer bind.** A decision whose Consequences
   no longer describe the project, or that a later decision quietly
   replaced.
6. **Layer state tables that lie.** A layer README saying "not started" for
   a layer that now has three documents, or vice versa.
7. **The document narrating its own construction.** Sentences about what the
   source material held, what was consolidated into what, why identifiers
   moved, which initiative the document is new as of, or an empty Retired
   section. `architecture-document-style` § What the document contains has the test
   and the worked examples; a restatement is the natural pass to apply it,
   because this is a document reading as its own history rather than as a
   description of today.

Present the list to the Requester before touching anything. Restating is
mechanical only where the answer is obvious; "is this element still live?"
frequently isn't, and guessing wrong deletes something real.

## Step 2 — Restate

For each finding, apply the matching move. **Every move is additive or
corrective in the current-state documents, and leaves history alone.**

| Finding | Move |
| ------- | ---- |
| Pending that shipped | Replace "Pending — future initiative" with the artifact that now realizes it. Link the scope document that delivered it |
| Realizing artifact gone | Retire the element, or mark it Pending again with a note saying what was removed and when |
| Superseded element | Keep the live one. Move the retired one to the layer document's **Retired** section (below), never delete the row outright |
| Resolved open question | Move the row from Pending to Resolved in `open-questions.md`, with the answer and where it was given. The originating scope document's Open Questions section is *not* edited — it recorded what was open at the time |
| Decision no longer binding | Set the decision record's Status to `Superseded by <n>_<slug>.md`, or `Retired — <one line why>`. Leave every other section untouched |
| Layer state table wrong | Correct it to what the folder actually contains |
| Document narrating its own construction | Delete it, or move it to the scope document that should have carried it. Keep anything awaiting validation where it is, and move a surviving subject note to an **Additional notes** section at the end |

### The Retired section

**It holds gate-approved elements only, and a document that has retired
nothing does not have one.** Not an empty table, not a "None" line — an
absent section says "nothing retired here" more clearly than a sentence
saying so, and a sentence saying so is the version commentary
`architecture-document-style` § No version commentary forbids.

Each layer document that retires anything gains a short section at the end:

```markdown
## Retired

Elements that were live and no longer are. Their IDs stay retired; nothing
reuses them.

| ID | Element | Retired in | Why |
| -- | ------- | ---------- | --- |
| `BSVC3` | Supervised build (manual) | [`4_...md`](../../scope/4_....md) | Replaced by `BSVC7` when the process was automated |
```

This is the compromise that makes compaction safe. The reader of the main
tables sees only what is live, which is the point of the exercise; the
reader who finds a dangling `BSVC3` in an old document can still discover
what happened to it. A model that simply deletes retired elements produces
references that resolve to nothing with no explanation — which is worse than
the clutter it was trying to remove.

Keep it short. If a Retired table grows past roughly a dozen rows, the
elements at the bottom are old enough that the scope documents are a better
record; move them out and say so in one line.

## Step 3 — Record it as an initiative

Restating is a change to the model, so it gets a scope document like
anything else (`write-scope-document` skill), with:

- an EA-alignment table naming every layer touched, and "no change" for the
  rest;
- **Gate 2**, because the current-state documents changed. This is not a
  formality: retiring an element the Requester still considers live is
  exactly the mistake this gate catches;
- Gates 0, 1, and 3 marked `N/A — restatement changes no strategy and
  delivers no code`;
- an in-architecture/scope/out-of-scope table. Restating is famously easy to let sprawl
  into "and while I was there I improved…". It shouldn't. A change to what
  the model *says about the world* is a different initiative from a change
  to *how accurately the model reports itself*.

## Step 4 — Verify

- Every element in every live table names a realizing artifact or is
  explicitly Pending — the grounding rule, re-checked across the whole
  model rather than one layer.
- No ID appears in both a live table and a Retired table.
- No ID has been reused.
- No document narrates its own construction, and none carries an empty
  Retired section.
- Every merged scope document is byte-identical to before, except where it
  was only linked to. Check this deliberately: `git diff` should show no
  changes to `architecture/scope/<n>_*.md` for any already-merged `<n>`.
- `open-questions.md`'s Pending table contains only questions genuinely
  still open.
- Cross-links resolve.

## What this skill does not do

- **It does not compact the git history**, and shouldn't. The commit log and
  the merged scope documents are the audit trail; restating makes the *model*
  readable, not the past shorter.
- **It does not resolve open questions.** Moving a row to Resolved requires
  an answer that already exists. If the answer isn't there, the question is
  still open, and a restatement that quietly closes it is a restatement that
  lied.
- **It does not change what the model asserts about the world** — only
  whether the model still describes today. If restating reveals the
  architecture should be different, that is the *next* initiative, through
  `align-change-through-layers`, with its own gates.
