---
name: architecture-document-style
description: Rulebook — consult when creating or editing any document under architecture/ — the numbering of layer folders, element IDs, how far a document has been validated, the grounding rule, how a relationship is declared, and the skeleton every element document follows. Its references carry the lookup tables — the ArchiMate-on-Mermaid notation, the element and relationship references with the standard's definitions and the method's considerations, the prefix registry and hierarchical numbering, canvases, and where a model sits between enterprise and implementation. Adds to document-style, which governs every document in the repository and which architecture documents obey too.
metadata:
  archreator:
    kind: rulebook
    gates: none
---

# ※ Architecture document style

How a model is written: its identifiers, how far it has been validated, and
the skeleton of an element document.

This is the architecture half. The rules that govern **every** document — the
language, what a document may contain, and how it links — are in
`document-style`, and a model document obeys those too.

## ⊕ When to use this

| The situation | What it looks like |
| ------------- | ------------------ |
| Editing the model | Any document under `architecture/` is being created or changed |
| Allocating an identifier | A new element needs an ID, or a leveled one needs numbering |
| Drawing anything | A diagram is going into a document |
| Writing any other document | A README, a `docs/` page, a contributing guide — for § What the document contains and § Links |

## ⊖ When not to

| The situation | Use instead |
| ------------- | ----------- |
| The question is how far to decompose | `process-and-capability-levels` — that governs shape, this governs form |
| The question is what the document is for | The skill that produces it — `write-scope-document`, `record-decision` |

## ⌖ Where this sits

**Realizes no process.** It is the rulebook every process complies with, and
the most-cited skill in the corpus — every skill that writes or edits a model
document reaches for it. Nothing here is a step.

## ※ Rules

### What is here, and what is one file away

**This page holds the rules that apply to every architecture document.** The
lookup tables — the ones needed only when you are drawing, numbering or
crossing a boundary — are in `references/`, and a citation naming a heading
there resolves exactly as one naming a heading here.

| Read | When |
| ---- | ---- |
| [`references/archimate-on-mermaid.md`](./references/archimate-on-mermaid.md) | Before drawing anything — the four notation devices, and where a diagram goes |
| [`references/archimate-elements-and-ids.md`](./references/archimate-elements-and-ids.md) | Allocating an identifier — the prefix registry, what each element represents in the standard's words, hierarchical numbering, retirement, domain and federation qualifiers |
| [`references/archimate-relationships.md`](./references/archimate-relationships.md) | Declaring a relationship, and what each one represents in the standard's words with both role names |
| [`references/model-structure.md`](./references/model-structure.md) | Deciding what this model owns and what it defers to its parent |
| [`references/canvases.md`](./references/canvases.md) | The model has a `0_business-design/` layer — Depth 2 and 3 only |
| [`references/reference-documents.md`](./references/reference-documents.md) | Filing source material, or writing anything down from a meeting |

### Numbering

- Layer folders are numbered in assessment order and never reordered:
  `1_strategy`, `2_business`, `3_information`, `4_application`,
  `5_technology` (translate the words if the project's doc language isn't
  English, but keep the numbers and the order). Projects that model an
  organization also have `0_business-design`, holding the canvases the rest
  is derived from — it is not an ArchiMate layer, and application-only
  projects leave it empty.
- Files inside a layer carry a numeric prefix giving the **logical analysis
  order**, which each layer README explains in an "Analysis order" table.
  A new file gets the next number, plus a row in that table; only renumber
  when the analysis order genuinely changes.
- Scope documents (`architecture/scope/`) are numbered **chronologically** per
  initiative.
- `architecture/6_transition/` is not a layer and carries no layer number. Its
  documents are numbered in analysis order like a layer's are, because a gap
  cannot be derived before the plateau it is measured against exists. It is
  **the only folder in the model that describes a future**; every numbered
  layer describes the current state, and that division is what lets a reader
  trust a layer document without checking its date.

### One document per layer, until it is not

A layer opens as **one document**, and a small subject stays that way — a
whole business layer can be one honest file. A larger subject splits **by
element family, in analysis order**, the shape the canonical file names
already anticipate: `1_business-actors-and-roles.md`,
`2_business-services.md`, `3_business-processes.md`.

Split when any of these becomes true, and not before:

- **A reader scrolls through one family to reach another** — past roughly
  twenty-five elements in the document, counting every level, the page has
  stopped being scannable.
- **One family carries a leveled catalogue of its own** — a process map
  with its level-2 contracts, a capability decomposition — big enough to be
  the document a reader opens on purpose.
- **Two families are validated at different sittings of a gate.** What is
  approved together can live together; what is approved separately should
  be separable.

Each split document keeps the full skeleton — its own "How to read" legend,
its own status line — and the layer README's analysis-order table is the
index. Split along family lines only: levels 1 and 2 of one catalogue stay
in one document, with only a level-3 flow earning a file of its own
(`process-and-capability-levels` § What is here, and what is one file away).
And merge back when a change leaves stubs: two half-empty documents are
worse than one honest one.

### A row must survive a page

Model documents are read on screens and exported to portrait pages — a
brief or a scope converted to PDF — and a table that overflows sideways is
unreadable in the export and barely readable before it. So a catalogue
keeps **at most six columns, and at most one whose cells are sentences**.

Slim before widening, in this order:

- **A fact that is a relationship is not a column of its own** — it is a
  relationship column of bare identifiers, or a row of the `## Relationships`
  table beside the diagram that renders it
  ([`references/archimate-relationships.md`](./references/archimate-relationships.md)).
- **A fact the description already carries is not a second column.** A
  purpose formula shaped "turns X into Y" names the trigger and the output;
  columns restating them are width without information.
- **What is shared by every row is said once above the table**, never
  repeated per row.

When a row still cannot fit — an element whose contract is genuinely prose —
**flip the catalogue to the record form**: each element defined as a bolded
lead-in (`**BPROC1.2 — Build and validate.**` — the same definition shape
goals and principles use), its attributes as prose or a narrow two-column
field table beneath, its relationships in the `## Relationships` table. The
validators read both shapes already.

Never fix width in the export: a landscape page, a shrunken font or a
truncated column is a rendering hiding a content bug, and the next export
meets it again.

### Document status

**Every document that defines an element says in its preamble how far it has
been validated.** One line, under the viewpoint line, opening with one of
three glyphs:

| Glyph | Status | What it means |
| ----- | ------ | ------------- |
| `○` | **Not started** | The document exists so the gap is visible. It defines nothing yet, and a claim about this part of the subject is not in the model |
| `◐` | **Draft catalogue** | Elements have been *identified* — from a conversation, a reference document, a sweep of a running estate — and written down with notes. Nobody has approved them. Identifiers are still draft, figures are unconfirmed, and nothing here may be built on |
| `●` | **Validated** | Confirmed by whoever is accountable for it, on a named date. Identifiers are permanent and a change to any of them is an initiative |

The line names the gate too, so a reader knows what would move it — or what
already did:

```markdown
**Status:** ◐ Draft catalogue — identified from the sources named below, not
yet validated. **Understanding** covers this layer.

**Status:** ● Validated at **Understanding**, 2026-08-24.
```

**A `●` earned outside a gate names the decision that put it there.** Not
every layer is covered by one: a Requester may decline Design and route the
solution design to ordinary pull-request review, and that is a real decision by
the person with the standing to make it. Such a document is validated, and its
line says by what:

```markdown
**Status:** ● Validated — **Design** declined at Understanding (scope document 1,
2026-08-22), which routed this layer to pull-request review.
```

This is the one place `●` can be claimed without a gate, and the escape is
narrow on purpose: it needs a recorded decision to point at. "I checked it" is
not one, because an approval that is not recorded did not happen.

`○` is the only one that is optional, and necessarily so: a document that
defines nothing has nothing a reader could mistake, so the validator does not
ask for a status there. Use it anyway where an empty document exists to keep a
gap visible.

**The glyph carries the meaning; the sentence beside it is prose in whatever
language the model is written in.** That is the same arrangement the element
notation uses, and it is why `scripts/check_model.py` can enforce this in a
model written in any language: it checks that a document defining elements
carries exactly one status glyph before its first `##`, and never reads the
words.

**A draft catalogue is not an architecture draft, and the distinction is the
point of the marker.** An architecture draft is a proposal about how something
should be structured. A draft catalogue is a list of things somebody said
exist, written down so they can be checked. Presenting the second as the first
is the failure this exists to prevent: a Requester who is shown a catalogue
and hears "architecture" approves a description nobody has verified, and an
agent that reads one will build on a system that was mentioned once in a
meeting.

**So a draft catalogue's tables carry two extra columns**, and they earn their
width:

| Column | Holds |
| ------ | ----- |
| `Source` | Which reference document or conversation the element came from — [`references/reference-documents.md`](./references/reference-documents.md). An element with no source in a draft catalogue is an invention |
| `Notes` | What is uncertain, contested or awaiting confirmation. Two names for what may be one thing; a figure nobody could stand behind; a system whose owner is unknown |

At the gate, `Source` stays — provenance does not expire. **`Notes` is
emptied**, because a note that survives its own gate is one of three things: a
fact, which belongs in the model; a question, which belongs in the
open-questions log; or something nobody cared about, which belongs nowhere.

**Mixed documents are normal, and the status is the weakest part.** A
validated layer that a new initiative adds elements to is `◐` until that
initiative's gate — not `●` with an asterisk. A reader who trusts a `●`
document must be able to trust all of it.

### Element IDs

Every element carries a short **ID**: a type prefix followed by a number,
no separator — `G1`, `CAP3`, `PROD2`. IDs are how one document refers to an
element in another without restating it. An element inside a leveled
catalogue extends its parent's ID instead of starting a new number —
`CAP3.2`.

An element is **defined** in one of exactly two shapes, and `check_model.py`
recognizes both:

| Shape | Used for | Example |
| ----- | -------- | ------- |
| The **first column of an inventory table** | Most elements | `` \| `BSVC3` \| Supervised build \| … `` |
| A **bolded lead-in**, ID then an em dash | Goals and Principles, which read better as prose than as rows — and any catalogue flipped to the record form because its rows outgrew a page (§ A row must survive a page) | `- **G1 — Legible guidance.** A prospective adopter…` |

A **qualified** ID in a first column (`` \| `SALES.BSVC3` \| ``) is a
*reference*, not a definition — that is what a domain charter's "Consumed
services" table holds. Anywhere else, a backticked ID is a reference.

Rules: an ID is assigned once and **never reused** after the element is
removed (a dangling reference should fail loudly, not silently point at
something else); numbering is per prefix, not global — and per parent inside
a leveled catalogue; and an element's ID never changes when it is renamed.
Referencing an element in prose or an ordinary table cell means writing its
name with the stable ID riding along — `relieves Faster approval [GAIN2]` —
without repeating its full description; the name leads, per `document-style`
§ The name leads, and the identifier rides along. Cross-document references
link that visible pair to the element definition; multiple references are one
per line.

Each document's "How to read this document" legend carries, on its nodes,
every prefix the document uses, expanded — `«Stakeholder» … [STK#]` — which
is § Write it out applied to identifiers. Examples use `#` (and `#.#` for
levels), never a plausible real identifier that pollutes searches for actual
elements.

**The prefix registry, hierarchical numbering, what happens to an identifier
when the element is retired, and how a reference crosses a domain or a model
boundary are all in
[`references/archimate-elements-and-ids.md`](./references/archimate-elements-and-ids.md).**

### Grounding rule (the most important one)

Every EA element must name the code artifact that realizes it — a page, a
module path, a pipeline file. If you cannot point at the realizing
artifact, either the element doesn't belong in the docs, or the code is
missing and the element should be marked explicitly **"Pending — future
initiative"** (ideally linked to the initiative that will deliver it). This
keeps the whole set verifiable against the code at any time — an outsider
should be able to open any EA document and check it against the repo.

### Relationships are declared, never only drawn

An element's relationships are **declared**, in one of two places, and a
diagram renders what was declared. A relationship whose only home is a Mermaid
block is a fact living inside a rendering, which `P1` does not allow — and it
is invisible to everything except a person reading that one document.

- **A catalogue column**, when its cell is a list of identifiers and nothing
  else. The header is the relationship's name, carried verbatim into the
  projection. **This is the one place a reference is a bare identifier**, and
  a name written into such a cell silently deletes the relationship.
- **A `## Relationships` table**, beside the diagram it explains, for anything
  a single row cannot carry — above all a relationship between two peers in
  one layer, which a catalogue has no column shape for. Its columns are fixed
  **by position, never by header word**: 1 and 3 hold the identifiers, 2 and 4
  describe them as `<glyph> «Archetype» <name>`, 5 is the relationship.

**A relationship that is not true yet says so in words** — the same
`Pending — future initiative` marker the grounding rule uses — never with a
dashed arrow, because a diagram is not read.

The full rules, including where the marker may and may not go and what
`check_model.py` holds against the catalogue, are in
[`references/archimate-relationships.md`](./references/archimate-relationships.md).

### Document skeleton

- Title (`# …`), then a nav line:
  `_[← <Layer> layer](./README.md) · [EA home](../README.md)_`
  (scope docs link to the scope index instead).
- State the **ArchiMate elements/viewpoint** covered near the top.
- Then the **status line**, where the document defines elements — § Document
  status. It sits in the preamble, before the first `##`, because that is
  where a validator looks for it and where a reader meets it before anything
  it might be believed for.
- A **"How to read this document"** section next: the legend diagram, whose
  nodes name the stereotypes and ID prefixes — and no table restating it
  (`references/archimate-on-mermaid.md` § Every element document opens with
  "How to read this document").
- Then **one section per element family, headed by that family's name** — a
  catalogue table never rides under another family's heading, because the
  heading is what tells a reader what the identifiers in front of them
  describe. A leveled catalogue names the level in the heading
  (`### Level 1 — the areas`, `### Level 2 — the capabilities`).
- Each section **opens with its diagram** where one earns its place
  (`references/archimate-on-mermaid.md` § Diagrams come first, one per
  section), followed by the inventory table, followed by prose.
- A **Retired** section, only if something approved has been retired
  (`restate-current-state`).
- **Additional notes**, last, and only if there is one — see § What the
  document contains.
- Prefer tables for element inventories, Mermaid for relationships, and
  prose only for rationale (the "why", not the "what" — the diagrams and
  tables already say what), and only where the "why" is about the subject.
