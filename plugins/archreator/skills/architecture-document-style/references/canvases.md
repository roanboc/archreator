# Canvas notation

_Reference for [`architecture-document-style`](../SKILL.md) § Where a model
sits._

Read this only when the model has a `0_business-design/` layer — Depth 2 and
Depth 3 subjects. An application project never needs it.

The canvases in `0_business-design/` are Strategyzer artifacts, not
ArchiMate. Keep a **table as the detailed, diffable source for each canvas**.
Each Business Model Canvas also carries a Mermaid overview in the traditional
nine-block arrangement: Key Partners; Key Activities above Key Resources;
Value Propositions; Customer Relationships above Channels; Customer Segments;
and Cost Structure and Revenue Streams across the bottom. Populate it from
the same rows and show `Name [ID]`; do not invent arrows between blocks or add
facts that exist only in the diagram. Each canvas gets its own `###` heading
naming the segment or product it belongs to.

Where a canvas *is* drawn — a layer view showing fit — the canvas block name
is the element type: it goes in the legend (`«Pain»`, `«Gain Creator»`,
`«Customer Segment»`) and not on the nodes, with the Motivation fill for the
customer profile and the Strategy fill for the value map, as in
`architecture/0_business-design/README.md` § Layer view.
The canvas-block-to-ArchiMate-element mapping lives in that same README and
is not restated anywhere else.

