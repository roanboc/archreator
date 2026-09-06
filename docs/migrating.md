# Crossing to 0.3 — for a project on the 0.2 method

_[← Repository README](../README.md) · [Adopting archreator](./adopting.md)_

A new project needs none of this: `establish-project` emits the current
scaffold. This page is for a repository already running on 0.2, and says what
its own files have to change.

The plugin itself updates the ordinary way — see
[keeping a project in sync](./adopting.md#keeping-a-project-in-sync-with-the-method).

## The Design gate is gone

Two gates remain, **Direction** and **Understanding**. Nothing that was
approved at Design is reopened, and no approval is lost: Design covered the
application and technology layers, which are now written after Understanding
without a gate of their own.

- **Living documents sweep once** — `AGENTS.md`, the architecture front door,
  the layer READMEs, `architecture/scope/README.md` — in one ordinary change.
- **Merged scope documents are never rewritten.** An Approvals table that
  records a granted Design keeps recording it. A frozen document quoting a
  retired gate is history, not drift.

## An ungranted gate gets no row

An Approvals table records what happened. A gate that was not granted gets no
row at all, so `N/A — <why>` rows are no longer written.

Existing ones are left alone: in a merged scope document they are part of the
record, and in a living one they cost less to leave than to sweep. Delete them
only in a document the current initiative is editing anyway.

## The open-questions log is retired

`architecture/scope/open-questions.md` is no longer part of the method, and
neither is the "Open questions" section of the scope-document template.

Each row still open moves to the document its answer would change, as a
decision the agent takes and records — the row's `Source` cell reads
`adopted — <the call>`, and the document stays `◐`, so a later word from the
Requester still overrides it. A row nobody can answer that way was a question
about a future nobody had scheduled; drop it. Once the file is empty, delete
it and its index entry — and where a merged scope document links to it, repoint
that link at the initiative retiring the log, which is the one edit a merged
record accepts.

## An identifier freezes at merge, not at a gate

An element ID is assigned once and never reused after the change that
introduced it merges. In 0.2 the freeze was pinned to the gate that approved
the element, which left elements added between Understanding and merge in an
undefined state. Nothing already assigned moves.

## What an existing project keeps

Every element, status glyph, prefix and skill name survives. The ○ / ◐ / ●
discipline, the relationship tables, the two validators and all eighteen
skills are unchanged, and nothing in a model's content needs to move.
