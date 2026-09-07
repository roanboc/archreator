# When a document or a table outgrows a page

_Reference for [`architecture-document-style`](../SKILL.md) § What is here, and
what is one file away. Read it when a layer document is being split into files,
or a table has started to scroll._

## One document per layer, until it is not

A layer opens as **one document**, and a small subject stays that way — a
whole business layer can be one honest file. A larger subject splits **by
element family, in analysis order**, the shape the canonical file names
already anticipate: `1_business-actors-and-roles.md`,
`2_business-services.md`, `3_business-processes.md`.

Split when any of these becomes true, and not before:

- **A reader scrolls through one family to reach another** — past roughly
  twenty-five elements in the document, counting every level.
- **One family carries a leveled catalogue of its own** — a process map with
  its level-2 contracts, a capability decomposition — big enough to be the
  document a reader opens on purpose.
- **Two families are validated at different sittings of a gate.** What is
  approved together can live together.

Each split document keeps the full skeleton — its own "How to read" legend,
its own status line — and the layer README's analysis-order table is the
index. Split along family lines only: levels 1 and 2 of one catalogue stay in
one document, with only a level-3 flow earning a file of its own
(`process-and-capability-levels` § What is here, and what is one file away).
Merge back when a change leaves stubs.

## A row must survive a page

**A table is the preferred display, and a table that fits stays a table.**
The rule here fires on one symptom only: **horizontal scroll** — on the
rendered page, or on the portrait PDF a brief or scope is converted to. A
table that fits never flips, whatever its column count.

Past roughly **six columns, or more than one column of sentence-length
cells**, a table usually starts to scroll — a symptom threshold to check at,
never a cap to conform to pre-emptively. When a table does scroll, slim it
first, in this order:

- **A fact that is a relationship is not a column of its own** — it is a
  relationship column of bare identifiers, or a row of the `## Relationships`
  table beside the diagram that renders it
  ([`references/archimate-relationships.md`](./archimate-relationships.md)).
- **A fact the description already carries is not a second column.** A
  purpose formula shaped "turns X into Y" names the trigger and the output;
  columns restating them are width without information.
- **What is shared by every row is said once above the table**, never
  repeated per row.

Only when a slimmed row still scrolls — an element whose contract is
genuinely prose — **flip that catalogue to the record form**: each element
defined as a bolded lead-in (`**BPROC1.2 — Build and validate.**`, the same
shape goals and principles use), its attributes as prose or a narrow
two-column field table beneath, its relationships in the `## Relationships`
table. The record form is an exception with a named cause, never a style, and
never applied to a neighbouring table "for consistency".

Never fix width in the export: a landscape page, a shrunken font or a
truncated column is a rendering hiding a content bug.
