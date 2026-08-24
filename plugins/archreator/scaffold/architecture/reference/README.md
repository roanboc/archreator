# Reference documents

_[← EA home](../README.md) · [Scope documents](../scope/README.md)_

The material this model was built from, kept exactly as it was provided:
meeting transcripts, presentations, specifications, spreadsheets, whatever
somebody sent.

**This is not the model.** Nothing here defines an element or carries an
identifier, and the validators do not read it — a transcript in which somebody
says an element identifier out loud is a person talking, not a definition.
Neither is it published: the portal and the PDF hand a reader the model, and a
raw transcript carries everything else that was in the room that day, to an
audience that was not.

Agent guidance: the `architecture-document-style` skill § Reference documents.

## What it is for

One question, asked late and hard to answer without it: **where did this come
from?**

A figure a Requester queries eighteen months on is answerable from the deck it
was read off. A sentence in a layer document that has stopped making sense can
be checked against the conversation it was written from. And an element
identified in a draft catalogue names its source here, which is what lets the
gate that validates it be a review rather than an act of faith.

## Naming

`YYYY-MM-DD-<short-description>.<ext>`, plain ASCII with hyphens.

The date is, in order of preference:

1. **When the meeting happened** — for a transcript, minutes, or a recording.
2. **When the document was shared** — for anything sent, presented or handed
   over.
3. **When it was added here** — the fallback, when neither of the first two
   can be established.

Take the first that can be established, and where it is not the first, the
index row says which one the date is.

**The original filename lives in the index, not on disk.** A file arriving as
`Strategy Review FINAL v3.pptx` keeps that name in the table below, where it
is searchable and still matches the sender's copy; on disk it becomes a dated
slug, because spaces and capitals in a path break links, tooling, and half the
shells anyone will use on it.

## Index

Every file gets a row, including one nothing has been derived from yet —
this is a record of what was received, not only of what was used.

<!-- TEMPLATE — add one row per document as it arrives. -->

| Date | Fixed by | File | Original name | Provided by | Derived into |
| ---- | -------- | ---- | ------------- | ----------- | ------------ |
|      |          |      |               |             |              |

- **Fixed by** — which of the three rules gave the date: *meeting*, *shared*
  or *added*.
- **Derived into** — the documents or elements that came out of it, or
  *nothing yet*. This is the column that makes the folder worth keeping.

## What does not belong here

| Not this | Where it goes |
| -------- | ------------- |
| Your reading of what a document means | The layer document it informs, cited back here |
| A decision taken in the meeting | `architecture/decisions/`, or a scope document |
| Anything with an element identifier | The model. If it has identifiers, it is not a reference document |
| Credentials, personal data, or anything shared in confidence that the model does not need | Nowhere in the repository |

The last row is the one worth checking before committing. A transcript is a
recording of people talking, and people say things in meetings that they did
not intend to put under version control.
