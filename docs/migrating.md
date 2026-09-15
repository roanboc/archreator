# Crossing versions — for a project on 0.2 or 0.3

_[← Repository README](../README.md) · [Adopting archreator](./adopting.md)_

A new project needs none of this: `establish-project` emits the current
scaffold. This page is for a repository already running on an earlier method,
and says what its own files have to change. Each section names the version
that introduced it.

The plugin itself updates the ordinary way — see
[keeping a project in sync](./adopting.md#keeping-a-project-in-sync-with-the-method).

## Relationships live in one catalogue (0.5)

A model declares every relationship a catalogue column does not carry in one
file, `architecture/relationships.md`, as rows of
`From | To | Relationship | Notes`, grouped by the document that defines the
source element. The `## Relationships` table beside each diagram, and any
section addressed to agents, leave the human pages: a page draws its
relationships and names them in prose, and a machine reads the catalogue. A
project that wants its human tables free of bare identifiers moves the
column-shaped relationships there too and says so in its `AGENTS.md`.

A reference changes shape with it. Inside the page that defines an element,
the bare identifier; from any other page, the type, the identifier and the
name — ``the process [`BPROC3.1`] Market and generate demand`` — with the
identifier in backticks inside the brackets. `Name [ID]` stays only on diagram
nodes.

The "How to read this document" section goes too. A diagram explains itself:
node labels carry glyph, name and identifier, the section heading names the
type, and one sentence under a diagram says what a colour or a dashed border
means where it matters. `check_model.py` still asks a defining document for a
diagram before its first table and one per section; it no longer asks for a
legend, and a stereotype on a node still fails outside a diagram marked
`%% legend`.

Four things move in an existing project: each `## Relationships` table
becomes rows of the catalogue under its document's heading, with the pending
marker moved from the relationship cell to the notes; each legend section is
deleted, with any sentence about a colour or a dashed border moved under the
diagram it explains; references outside the defining page take the new shape;
and `scripts/model_graph.py` and `scripts/check_model.py` are copied again
from the scaffold, because the parser now reads a relationship row by shape,
keeps catalogue cells out of `trace`'s mentions and no longer asks for a
legend. Nothing in the elements, their identifiers or their
status glyphs moves.

## Fifteen skills are invoked by name (0.4)

Three skills surface on their own — `align-change-through-layers`,
`architecture-document-style` and `document-style`. Every other skill is
`/archreator:<skill>`, out of context until called, and a skill that hands
off to one reads it from disk. On a host that ignores the key, nothing
changes.

A project changes two things in its `AGENTS.md`: the skills section, which
said the agent surfaces every skill from its description, and the rule
paragraph, which now says a change inside an element the model already names
is coded directly and documents nothing. The validators, the model and the
scope documents are untouched.

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
discipline, the two validators and all eighteen skills are unchanged; the
relationship tables move once, into the catalogue the 0.5 section describes,
and nothing else in a model's content needs to move.
