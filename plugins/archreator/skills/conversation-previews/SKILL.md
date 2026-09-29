---
name: conversation-previews
description: Rulebook — consult before showing the Requester what a change or a discovery claims, asking them anything, or recording their confirmation. What a preview holds, when one is due, how a question is put, and how a confirmation given in conversation or at a session validates a document.
disable-model-invocation: true
metadata:
  archreator:
    kind: rulebook
---

# ※ Conversation previews

**The Requester understands and confirms in the conversation they are already
having, not by opening the repository.** A preview is what the agent shows
there: what changes about the subject, the calls the agent took on their
behalf, and one question when something needs their answer. The repository
stays the record. The conversation is where the claims are understood, and a
confirmation given there is what validates them.

## ⊕ When to use this

| The situation | What it looks like |
| ------------- | ------------------ |
| A discovery finishes a group of layers | The canvases, or the strategy, or the business and information layers, have been drafted and nothing below them is built yet |
| A stop fires | A contradiction, an ambiguity or an authorization — `align-change-through-layers` § Where this stops |
| A change is ready for its pull request | The layers are aligned and the agent is about to hand the branch over |
| An AI actor's autonomy or decision rights change | Any change to what an AI actor may decide alone, whatever else the change holds |
| A decision-maker is never in the conversation | The Requester is reached at a meeting, not in the chat the agent works in |

## ⊖ When not to

| The situation | Use instead |
| ------------- | ----------- |
| A change inside an element the model already names, or one that only keeps a row true | Nothing to preview. It is built directly, and its pull request says so |
| A reader wants to understand the model, not confirm a change to it | `answer-architecture-question` — a brief is for reading, a preview is for deciding |
| The question is about the method, not the subject | Nothing. A Requester is never asked to choose between the method's options |

## ⌖ Where this sits

**Realizes no process.** It is the rule for the moments a process meets its
Requester: the stops of `align-change-through-layers`, the end of each
discovery, and the confirmation that moves a document to `●`
(`architecture-document-style` § Document status).

## ※ Rules

### A preview shows what changes, not the model

A preview answers one question for the Requester: *what is now true about my
subject that was not before, and what did you decide for me?* It holds:

1. **One sentence of why** — the goal or driver the change serves, in the
   subject's words.
2. **What changes**, as before and after, or as the new rows only — never the
   whole catalogue. Where a picture says it faster, one small diagram of who
   hands what to whom.
3. **The calls the agent took**, one line each: every row sourced
   `adopted — <the call>` on the branch. These are what the Requester is
   least likely to have noticed and most likely to disagree with, so they
   are never folded into the rest.
4. **One question, or "nothing is needed from you"** — never "does this look
   right?"

It carries no element identifiers, no glyphs, no layer numbers and no word
of the method's vocabulary. The Requester is shown their business, not the
model of it. A reader who wants the rows follows the link to the branch.

**A preview fits on one screen.** Past that, it is showing the model rather
than the change; split it by the question each part needs answered, and show
the part that blocks the work first.

### A preview is generated from the branch

Every fact in a preview comes from a file on the branch the work is on, and
the preview names that branch and its revision. A preview written from memory
becomes a second model that drifts from the first. When the Requester changes
something in answer, the file changes first and the preview is shown again
from it.

### When a preview is due

| Moment | Why it is due |
| ------ | ------------- |
| **At the end of each discovery group** — the canvases; then the strategy; then business and information | Each group is what the next is derived from. The next group is not drafted until this one is confirmed, because building on an unconfirmed layer builds on an assumption |
| **When a stop fires** | A contradiction is shown as the two statements side by side; an ambiguity as the two readings and what each would build; an authorization as what exactly would be committed |
| **Before the pull request of a change** | The one moment everything the change claims is in one place |
| **Whenever an AI actor's autonomy or decision rights change** | Delegating a decision to an agent is the claim a Requester most needs to have understood |

Nothing else interrupts. A change with no stop, no adopted call and no AI
actor touched shows its preview once, before the pull request, and asks for
nothing if nothing is needed.

### A question is tied to one row, and offers the choices the model allows

- **Few at a time.** Two or three, never a questionnaire. Ask the one that
  blocks the most work first.
- **Top-down.** Why the change is made and which part of the business it
  touches are settled before any question about information or realization.
- **Each question names the one statement it is about**, in the subject's
  words, and offers the answers the model already allows — the goals that
  exist, the actors that exist, *new*, *something else* — with the agent's
  own call marked as the default.
- **Offered as choices where the conversation can show them, numbered
  otherwise.** A free-text answer is always accepted.

A question the model or the request already settles is not asked; neither is
one about a state that does not exist yet.

### Where the preview goes

**The preview goes to wherever the decision-maker is.**

| The decision-maker | Carrier | How the answer comes back |
| ------------------ | ------- | ------------------------- |
| In the conversation with the agent | The conversation itself, in the richest form it renders | Their reply |
| Reached at a meeting, never in the conversation | A one-page session pack of the same content, exported from the branch | The session's notes, filed under `architecture/reference/` (`architecture-document-style` § Reference documents) |

In the conversation, a table always works. Show a diagram rendered where the
conversation can display one, and as its source or a link where it cannot.
Where a preview would leave the conversation — published as a page, sent as a
file outside the repository's own readers — that is publishing, and the
Authorization stop applies before it is sent.

### A confirmation validates, and the merge records it

A confirmation is a person with standing over the subject saying, in the
conversation or at a session, that what the preview showed is true. It is
written down at once, on the branch, in the document it confirms:

- Every row it covers has its `Source` cell extended with
  `confirmed — <who>, <in conversation | at the session of <date>>`, and an
  adopted call it accepted becomes a plain fact.
- When every row of a document is confirmed, its status line reads
  `● Validated, <date> — confirmed by <who>`, with the date of the
  confirmation.
- The scope document's alignment table says, per layer, which preview was
  confirmed and by whom.

**The merge lands what was confirmed; it does not validate on its own.** A
document whose preview nobody confirmed stays `◐` after its pull request
merges, and says so. A correction to a confirmed row is a change like any
other, and is previewed again.

Only the Requester, or at Depth 3 the Requester of the domain the rows belong
to, confirms. A Reviewer's approval of the pull request is a review of the
work, not a confirmation of the claims.

## ✎ Worked example

> Strategy discovery drafts three goals, two principles and five capabilities
> from a one-paragraph request, and took four calls the request did not
> settle. The preview opens with the one-sentence why, lists the goals and
> principles as plain sentences, and puts the four calls on their own lines.
> It asks one question — whether the second principle forbids or only
> discourages sharing data outside the organization, with *forbids* marked as
> the agent's call. The Requester answers *discourages, except to
> regulators*. The principle is rewritten on the branch, every confirmed row
> gains its `confirmed —` source, the strategy documents move to `●`, and only
> then is the business layer drafted.

## ⚠ Anti-patterns

- Previewing the whole catalogue instead of what changed.
- Burying the agent's own calls among the rest of the change.
- Asking "does this look right?" rather than a question tied to one row.
- A preview with an identifier, a glyph or a layer number in it.
- A preview written from memory rather than generated from the branch.
- Drafting the next discovery group before this one is confirmed.
- Moving a document to `●` because its pull request merged, with no
  confirmation behind it.
- Sending a preview outside the repository's readers without the
  Authorization stop.

## ☑ Done when

- Every preview due was shown, to the person who decides, where they are.
- Every answer is written into the document it concerns before anything is
  built on it.
- Every `●` in the change names who confirmed it and when.
- Every adopted call was either confirmed, changed, or left `◐` and said so.
