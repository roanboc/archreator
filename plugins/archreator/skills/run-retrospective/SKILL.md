---
name: run-retrospective
description: Use at the end of a completed initiative or client engagement, once the work has merged or been delivered — captures what the method failed to tell you to do and what you did instead, as a pattern note that can become a method improvement. Not a project retrospective about what went well; specifically about the gap between the method and the judgement the work actually needed.
---

# Engagement retrospective

_Run after the work, not during it. The scope document records what was
built; this records **what the method did not know how to build it**._

Every method improvement starts as somebody improvising. An experienced
person hits a moment the instructions do not cover, does something sensible,
and moves on — and the knowledge stays in their head. This skill is the
mechanism that stops that happening, by asking the question while the
improvising is still fresh.

## When this applies

- An initiative merged, or a client engagement finished.
- Someone ran the method end to end and had to make judgement calls.

**Not** after every commit, and not as a general project retrospective. The
subject is narrow on purpose: the gap between what the method says and what
the work needed.

## What it is not

- **Not a diary.** "Discovery went well" teaches nobody anything.
- **Not a place for client facts.** See § The confidentiality boundary.
- **Not a way to change skills.** It *proposes*; changes go through the
  gates like any other change.

## The six questions

Ask them in order, in one pass, of whoever did the work. Three to five
minutes of real thinking beats an hour of thorough recollection.

1. **Where did the method not tell you what to do?** The moments you
   improvised — where you had to decide something the skills were silent on.
2. **What did you do instead, and why that?** The reasoning matters more than
   the action; the action rarely transfers, the reasoning sometimes does.
3. **Would you do the same next time, or was it specific to this?** The
   generalization test. Most answers are "specific to this", and that is a
   perfectly good answer.
4. **What did the Requester or client say that surprised you?** The wrongness
   signal — a customer segment named wrong, a symptom presented as a cause,
   a constraint that turned out not to be one. This is where consultant
   judgement actually lives.
5. **What did you decide not to write down, and why?** Makes the
   confidentiality boundary explicit instead of assumed, and often surfaces
   something that *could* be written down in general terms.
6. **If this became a skill edit, which skill, and what sentence would it
   add?** Forces the output to be actionable. A pattern that cannot be
   written as a sentence is not ready.

## The three rules

**No client facts.** Names, figures, industries specific enough to identify,
anything a client told you in confidence — none of it goes in the note. The
note records the **pattern**, not the case. "An owner presented a symptom as
the problem, and the frame only broke when the fifth question contradicted
the first" is a pattern. The same sentence with the company in it is a leak.

**A note that proposes nothing is still a note.** Not every engagement
teaches something. Recording "nothing generalizable this time" is evidence —
it is how you find out whether the method is converging or whether the
mechanism is manufacturing lessons to justify itself. **Never invent a
finding to make a note look worthwhile.**

**Proposals become initiatives, not edits.** This skill never edits a skill,
a layer document, or a rule. It writes a note whose last section proposes,
and each proposal is picked up as its own change through `align-change-through-layers`
with the gates that implies. That is what keeps a human between the learning
and the method.

## The note

One file per retrospective, numbered chronologically, in the organization's
own `docs/engagements/` (or wherever the consuming project keeps them —
name the location in that project's `CLAUDE.md`).

```markdown
# N — <what the work was, in the most general terms that stay true>

**Date:** YYYY-MM-DD
**Kind:** initiative | client engagement
**Delivered:** <link to the scope document, or "not public">

## What the method did not cover

<The improvised moments. One heading each where there were several.>

## What was done instead, and why

<The reasoning. Not the steps.>

## Does it generalize?

<Per moment: yes / specific to this / not yet known. Say which and why.>

## What surprised us

<The wrongness signals — where the stated frame turned out to be wrong.>

## Deliberately not recorded

<That client-confidential material was excluded, and roughly what kind.
Never the material itself.>

## Proposed

| # | Skill or document | The sentence it would add | Raised as |
| - | ----------------- | ------------------------- | --------- |
| 1 | `<skill>`         | <one sentence>            | <initiative, or "not yet"> |

<Or: "Nothing generalizable this time." — a complete and acceptable answer.>
```

## The confidentiality boundary

On a client engagement the raw material is confidential by default. The note
is public by default. **That crossing is the risky part of this skill**, and
it is one-directional: a pattern may be lifted out of a case, but nothing
identifying may travel with it.

Two tests before writing a sentence:

- **Would the client recognise themselves in it?** If yes, generalize until
  they would not, or drop it.
- **Does the pattern still teach something once the specifics are gone?** If
  not, it was a fact about that client, not a pattern.

When in doubt, question 5 exists to record that something was left out. An
excluded item that is noted as excluded is not a loss — it is a marker that
the boundary was considered.

## Following through

A note nobody acts on is a diary with extra steps. When a pattern appears in
**two** notes, it has stopped being a coincidence and should be raised as an
initiative that week. When it appears in one, wait — the generalization test
in question 3 is unreliable on a single case, and encoding a one-off makes
the method worse rather than better.

Follow `architecture-document-style` for numbering and links, and `write-scope-document` for any
initiative a proposal becomes.
