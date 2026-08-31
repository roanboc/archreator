# Canvas notation

_Reference for [`architecture-document-style`](../SKILL.md) § What is here, and
what is one file away._

Read this only when the model has a `0_business-design/` layer — Depth 2 and
Depth 3 subjects. An application project never needs it.

The canvases in `0_business-design/` are Strategyzer artifacts, not
ArchiMate. Keep a **table as the detailed, diffable source for each canvas**,
and open each canvas document with the same "How to read this document"
legend every element document gets: the canvas blocks as legend nodes —
`<glyph> «Key Partner» who is depended on [KP#]` — connected by the
relationships the canvas itself defines (a partner and a resource enable an
activity, an activity delivers through a channel, a channel establishes a
relationship, a relationship produces revenue, an activity incurs cost).
That one generic diagram teaches the whole notation; the block catalogues
below it carry the content.

**The products lead the Business Model Canvas.** Before any block catalogue,
a products-at-a-glance section — one column per product: its segments,
channels, relationship, revenue, dominant cost, and whether it scales —
because every later row says "for `PROD#`", and the reader needs the
products before the blocks that serve them. Each canvas gets its own `###`
heading naming the segment or product it belongs to.

**No nine-block overview diagram.** Packing every row into a handful of
nodes restates the tables in a form that is harder to read, and a diagram
earns its place by saying what the table cannot
([`archimate-on-mermaid.md`](./archimate-on-mermaid.md) § Diagrams come
first, one per section).

Where a canvas *is* drawn — a layer view showing fit — the canvas block name
is the element type: it goes in the legend (`«Pain»`, `«Gain Creator»`,
`«Customer Segment»`) and not on the nodes, with the Motivation fill for the
customer profile and the Strategy fill for the value map, as in
`architecture/0_business-design/README.md` § Layer view.
The canvas-block-to-ArchiMate-element mapping lives in that same README and
is not restated anywhere else.
