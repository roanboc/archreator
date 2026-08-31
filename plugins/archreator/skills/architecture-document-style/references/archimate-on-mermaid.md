# ArchiMate on Mermaid

_Reference for [`architecture-document-style`](../SKILL.md) § Drawing._

Read this before drawing anything. It carries the four devices that encode
ArchiMate semantics onto Mermaid, and the rules for where a diagram goes.

ArchiMate has no native Mermaid profile — no icons, no standard shapes — so
these documents encode its semantics with **four devices: label format,
glyph, shape, and colour.** All four are specified in exactly one place,
`architecture/README.md` § Notation conventions, including the glyph set, the
default shape per element, the layer palette and the per-element tone ramps.
Read that section before drawing anything, and copy its values rather than
re-tabulating them here — a second copy is a second thing to drift.

The parts worth restating, because they are decisions rather than values:

- **Node labels are one line, identifier last**:
  `<glyph> <description> [<ID>]`. One line because a label
  spanning two depends on the viewer rendering `<br>`, and whether it does
  depends on that viewer's HTML-label setting — the same diagram reads
  correctly in one place and runs together in another. A single line cannot
  break. The identifier goes last, in brackets, where it is still in the same
  place on every node; the tables carry the full context.
- **The stereotype appears only where the notation is the subject** — the
  legend under "How to read this document", and the notation section of
  `architecture/README.md`. A legend node reads
  `<glyph> «Stereotype» <what the type is>`; a content node drops the word,
  because glyph, shape and colour already carry the type and the legend is one
  screen above. The word is the widest thing on a node and the only one of the
  four devices that costs label width.
- **An actor's kind is not a stereotype and stays on the node.**
  `⚇ Requester (Human) [ACT1]`, `⚇ The drafting agent (AI) [ACT2]` — see
  § Actors. Nothing else in the notation distinguishes a `(Hybrid)` actor, and
  a reader who defaults to "person" has been misled rather than merely
  under-informed.
- **Colour separates layers across a diagram and element types within one.**
  A single-layer view ramps the layer's hue by element type; a cross-layer
  view keeps the flat palette. An element borrowed from another layer keeps
  its home colour, shape and glyph.
- **Dashed edges mean Pending.** Solid is true today. This one rule turns a
  diagram into a statement about the present rather than an aspiration.

Relationships are labeled with their ArchiMate name (**serves**,
**realizes**, **assigned to**, **accesses**, **triggers**, **flow**,
**aggregates**, **influences**); where Mermaid arrowheads can't distinguish
relation types, the label is authoritative.

## Diagrams come first, one per section

**A section that has a diagram opens with it**, and the tables and prose
below describe it. Not the reverse: a reader who meets three tables before a
picture has to build the picture themselves, and most will not.

**One diagram per section, not one per document.** Past roughly fifteen
elements a single view of a layer can only be a selection, and a selection
that looks complete is worse than several honest parts — it teaches the
reader something false about the size of the model. Draw one link of the
chain per section, letting consecutive diagrams overlap by one rank so they
can be read as a sequence.

**A diagram earns its place by saying something the table cannot.** Which
element has the most edges, which has none, where every path converges,
which side of a boundary is thin. If a diagram only restates the rows
beneath it, cut it — that is DRY applied to pictures.

## Every element document opens with "How to read this document"

A legend diagram showing this document's element types and how they connect,
then a table of **glyph / shape / element / ID prefix** — including any
element borrowed from another layer for context. **This is the one diagram
that names the stereotypes**, which is what lets every diagram below it drop
them.

**A layer README that only indexes other documents is exempt**: it has no
elements to legend, and giving it one would be ceremony rather than help.

The cost is a few lines per document. What it buys is that **each layer is
self-documenting**: a reader arriving from a deep link, or an agent loading
one file, has the notation in front of them and needs no second file open.
That matters more here than in most documentation, because these documents
are read one at a time and out of order.

