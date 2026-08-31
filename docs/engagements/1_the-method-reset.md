# 1 — The method reset, run twice and compared

**Date:** 2026-08-31
**Kind:** initiative
**Delivered:** [PR #48](https://github.com/roanboc/archreator/pull/48) (the kept
reset), with [PR #47](https://github.com/roanboc/archreator/pull/47) as the
rejected alternative whose corrections this note preserves

The same request — assess archreator as a customer who understands their
business but not enterprise architecture, and reset the method to something
simpler without losing the rigor — was answered twice, independently, and the
answers were compared. One run rebuilt the method around ten skills and a new
runtime; the other kept the eighteen-skill kernel and cut what lands in a
customer's repository and what an agent must load before the first useful
thing. The second was kept. The first run's real value was the Requester's
corrections along the way, which its own retrospective recorded and which
would otherwise die with its branch. This note is where they survive.

## What the method did not cover

### Which parts of it were the product

Nothing said which mechanisms were the
kernel — the thing that makes the method more than a prompt — and which were
ceremony around it. The first reset removed the skill format, the process
grounding and the notation along with the empty folders, and what remained was
close to a plain preprompt. The correction, the most important one of the
whole engagement: simplicity means removing ceremony and unused artifacts,
never the kernel that improves reasoning, navigation and communication.

### The difference between the standard existing and the standard being materialized

The method equated "the model has a shape" with "every file of
that shape is created now", so a new project opened on forty-four files about
nothing. The correction: the customer repository carries only current
content, the plugin carries the discoverable standard, and a front-door status
row per layer replaces every empty folder.

### Who the reader of an identifier is

The rules optimized identifiers for
the parser and let the reader decode them. The correction, refined twice: a
defining row keeps the identifier first because the sequence and hierarchy
must be scannable; a machine-read relationship column keeps bare identifiers
because a name written there deletes the relationship; everywhere else the
name leads and the identifier rides along.

### What a cache costs when it lies

The reading tools trusted a persisted
projection that was rebuilt only when its file was missing. On the largest
real model on this method, verified during this comparison: rename an element
and the trace serves the old name with no warning; add one and the answer is
a confident "no such element"; the brief stamps a revision hash implying a
currency the content does not have. A full fresh parse of that model takes
well under a second.

### Whether an approval may become invisible

The first reset made every gate
conditional and every scope record disposable, which reads as simplification
and deletes the audit trail — against the one rule every repository on the
method states first. The correction: three gates, named for what the
Requester approves, predictable in advance, with unscheduled stops for
material uncertainty in between; a gate that could not have applied gets no
row, and a delegation is recorded once and cited, never implied.

## What was done instead, and why

The kept reset attacked the two measured costs — context residency (one
rulebook cost ~10,000 tokens on nearly every activation; split so the
always-loaded page carries the rules and the lookup tables sit one file away)
and repository residency (44 files to 11, everything else emitted by the
skill that first has content for it). It deleted rather than rebuilt: the
projection, the custom portal and the whole-model PDF went, and what replaced
them is a fresh parse, a generated stock configuration, and nothing,
respectively. The rejected reset was mined afterwards for what the kept one
lacked, and the comparison itself became a follow-up change: the reference
conventions reconciled to name-first, the emission choreography bound to the
skills that own it, the migration crossing written down.

## Does it generalize?

- **Name the capability preserved before deleting its mechanism** — yes.
  Every future simplification should state what survives it, or it is the
  first reset's over-deletion again.
- **A template library and a generated project deserve different volume** —
  yes. Lazy materialization is now the scaffold's design, and the binding
  that makes it real is that every asset names the skill that emits it.
- **Machine-normalized identity must not replace local human context** —
  yes. The name-leads rule is now stated once, with its two earned
  exceptions.
- **Content contracts stable, rendering reader-sensitive** — yes for
  processes (each level says what must be recoverable; presentation is
  free). Not yet encoded beyond them.
- **Two independent attempts at one consequential change, then a
  comparison** — specific to this. It cost roughly double and was worth it
  exactly because the change was a reset; a routine initiative does not earn
  a control group.

## What surprised us

The strongest argument for the winning design came from the losing run's
paper trail — the corrections, not the code. And the one place the kept reset
contradicted the Requester's recorded principles was a deletion that looked
like the others: the scoped PDF for business readers went out with the
whole-model PDF, though the principle distinguished them and the method's
largest real deployment delivers one to its approver.

## Deliberately not recorded

Nothing here names the organizations modeled with the method, their figures,
segments or systems. Where an example was needed, the corpus's own phrase
"the largest real model on this method" stands in for it.

## Proposed

| # | Skill or document | The sentence it would add | Raised as |
| - | ----------------- | ------------------------- | --------- |
| 1 | `docs/adopting.md` | A business reader can ask for one brief or scope as a PDF, and the method owns the recipe — restoring the scoped export the principle kept when the whole-model one went | not yet — the Requester decides whether the method owns it or a project does |
| 2 | `architecture-archreator` | The reset recorded as the initiative it is, through Understanding, once the method it delivers is validated | not yet — deliberately deferred by the Requester |
| 3 | the scaffold | The acceptance test is a person who has never heard of ArchiMate modeling something real with it, measured on files produced, questions asked, and whether a draft catalogue reads as one | not yet — nothing further should be built until it passes |
| 4 | `process-and-capability-levels` | A presentation pattern per level — the vertical contract table, the ordered-flow table — as a reference beside the content contract | not yet |
