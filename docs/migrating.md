# Crossing versions — for a project on 0.2 through 0.5

_[← Repository README](../README.md) · [Adopting archreator](./adopting.md)_

A new project needs none of this: `establish-project` emits the current
scaffold. This page is for a repository already running on an earlier method,
and says what its own files have to change. Each section names the version
that introduced it.

The plugin itself updates the ordinary way — see
[keeping a project in sync](./adopting.md#keeping-a-project-in-sync-with-the-method).

## The gates are gone (0.6)

Direction and Understanding are retired. The agent builds directly from the
Requester's request, through the layers, and opens the result as a pull
request. **The Requester's merge is the approval** — nothing before that
claims to be one. The agent still stops, but only for three named reasons,
in place of the two gates and the two unscheduled stops that preceded them:
**Contradiction** (the change conflicts with a Principle, a decision already
recorded, or a rule the model states), **Ambiguity** (two readings of the
request build different things), and **Authorization** (the work would
commit the Requester to spend, exposure or publication they have not
agreed). See `align-change-through-layers` § Where this stops.

- **No scope document carries an Approvals table any more.** What changed
  and why is the document; the pull request whose merge approved it is the
  record. A merged document that still shows one keeps it — history, not
  drift.
- **A document moves from `◐` to `●` when the pull request that changed it
  merges**, not when a gate is granted. The glyph and the discipline are
  unchanged; what moves it is.
- **`metadata.archreator.gates` is gone from every skill's frontmatter**, and
  `gated-procedure` is renamed `procedure` — a purely internal kind value,
  invisible in what a skill's description or title show. Neither rename
  needs anything in an existing project.
- **Living documents sweep once** — `AGENTS.md`, `CONTRIBUTING.md`, the
  architecture front door, the layer READMEs, `architecture/scope/README.md`
  — in one ordinary change. The rule paragraph now says the owner's merge is
  the approval, and cites the three stops in place of the two gates.
- **Merged scope documents are never rewritten.** An Approvals table
  recording a granted Direction or Understanding keeps recording it. A
  frozen document quoting a retired gate is history, not drift.

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
means where it matters. The notation moves up one level: each layer README
gains `## Metamodel` before its `## Layer view` — one `%% legend` diagram of
the layer's element types with glyph, shape, colour, stereotype and prefix —
and the layer templates under `assets/layers/` ship it. `check_model.py`
still asks a defining document for some view and, in each section, for its
diagram before that section's tables; it no longer asks for a legend, and a
stereotype on a node still fails outside a diagram marked `%% legend`.

A page speaks about its subject and about nothing else. Who approves it and
at which session, which gate is pending, how a canvas block becomes an
element, how files are numbered: all of it leaves the model pages for
`AGENTS.md`, the method and the status line. A third validator,
`scripts/check_prose.py`, fails a page on the vocabulary that gives such a
sentence away, from a word list in `scripts/prose-denylist.json` that a
project translates with its documentation language. The layer README takes
one shape — title, one sentence, the viewpoint line, `## Documents`,
`## Metamodel`, `## Layer view` — and the sections a 0.4 README carried
("Analysis order", "Fit is a rule", "From canvas to ArchiMate") go: the fit
verdict lives in the value proposition canvas, the mapping in the method's
canvases reference, and the order is the table's.

Six things move in an existing project: each `## Relationships` table
becomes rows of the catalogue under its document's heading, with the pending
marker moved from the relationship cell to the notes; each legend section is
deleted, with any sentence about a colour or a dashed border moved under the
diagram it explains; references outside the defining page take the new shape;
and `scripts/model_graph.py` and `scripts/check_model.py` are copied again
from the scaffold, because the parser now reads a relationship row by shape,
keeps catalogue cells out of `trace`'s mentions and no longer asks for a
legend; `scripts/check_prose.py` and `scripts/prose-denylist.json` are copied
from the scaffold, the list translated where the documentation language is
not English, and the sentences it names are cut or moved to `AGENTS.md`; and
each layer README is cut to its shape, its fit verdict moved into the canvas
that verifies it and its canvas mapping deleted, because the method holds it.
Nothing in the elements, their identifiers or their status glyphs moves.

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
