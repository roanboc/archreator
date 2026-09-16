# Canvas notation

_Reference for [`architecture-document-style`](../SKILL.md) § What is here, and
what is one file away._

Read this only when the model has a `0_business-design/` layer — Depth 2 and
Depth 3 subjects. An application project never needs it.

The canvases in `0_business-design/` are Strategyzer artifacts, not
ArchiMate. Keep a **table as the detailed, diffable source for each canvas**, one
section per block, each opening with its own diagram where one earns its
place. The relationships the canvas itself defines (a partner and a resource
enable an activity, an activity delivers through a channel, a channel
establishes a relationship, a relationship produces revenue, an activity
incurs cost) are rows of the relationship catalogue, drawn where a section
needs them. No canvas document opens with a legend.

**The products lead the Business Model Canvas.** Before any block catalogue,
a products-at-a-glance section — one column per product: its segments,
channels, relationship, revenue, dominant cost, and whether it scales —
because every later row says "for `PROD#`", and the reader needs the
products before the blocks that serve them. Each canvas gets its own `###`
heading naming the segment or product it belongs to.

**No nine-block overview diagram.** Packing every row into a handful of
nodes restates the tables in a form that is harder to read; a diagram
earns its place by saying what the table cannot
([`archimate-on-mermaid.md`](./archimate-on-mermaid.md) § Diagrams come
first, one per section).

Where a canvas *is* drawn — a layer view showing fit — the canvas block name
is the element type: the subgraph or section heading names it (`Customer
profile`, `Value map`) and no node carries it, with the Motivation fill for the
customer profile and the Strategy fill for the value map, as in
`architecture/0_business-design/README.md` § Layer view.
The canvas-block-to-ArchiMate-element mapping lives in that same README and
is not restated anywhere else.

## From canvas to ArchiMate

The canvases are worth filling in only if the architecture is derived from
them. Each block has one destination, and the receiving document records where
the element came from in its `Source` column. This table is the single source
of the mapping: a layer README never restates it, and a project document that
needs it names the block in its `Source` column and nothing more.

### Value Proposition Canvas

| Canvas block | ArchiMate element | Derived into |
| ------------ | ----------------- | ------------ |
| Customer Segment | «Stakeholder», and a «Business Actor» / «Business Role» | `1_strategy/1_motivation.md`, `2_business/1_business-actors-and-roles.md` |
| Customer Job | «Goal» of that Stakeholder (a «Business Process» they perform) | `1_strategy/1_motivation.md` |
| Pain | «Assessment», attached to the «Driver» it assesses | `1_strategy/1_motivation.md` |
| Gain | «Outcome» | `1_strategy/1_motivation.md` |
| Products & Services | «Product», aggregating «Business Service»s | `2_business/2_business-services.md` |
| Pain Reliever | «Capability», with a «Course of Action» where a choice was made | `1_strategy/2_capabilities-and-resources.md` |
| Gain Creator | «Capability» delivering a «Value» | `1_strategy/2_capabilities-and-resources.md` |

### Business Model Canvas

| Canvas block | ArchiMate element | Derived into |
| ------------ | ----------------- | ------------ |
| Customer Segments | «Stakeholder» / «Business Actor» | `1_strategy/1_motivation.md`, `2_business/1_business-actors-and-roles.md` |
| Value Propositions | «Value», attached to the «Product» | `2_business/2_business-services.md` |
| Channels | «Business Interface», plus the «Business Service» delivering through it | `2_business/2_business-services.md` |
| Customer Relationships | «Business Service» (onboarding, support, account management) | `2_business/2_business-services.md` |
| Key Activities | «Business Process», realizing a «Capability» | `2_business/3_business-processes.md` |
| Key Resources | «Resource» | `1_strategy/2_capabilities-and-resources.md` |
| Key Partners | external «Business Actor», with a «Contract» or «Business Collaboration» | `2_business/1_business-actors-and-roles.md` |
| Revenue Streams | no native element; «Value» in the monetary sense | a table in `0_business-design/2_business-model-canvas.md`, keyed to the product it belongs to |
| Cost Structure | no native element | a table in the same canvas, keyed to the resource or capability that incurs it |

Revenue and cost have no first-class ArchiMate element, and inventing a
stereotype for them would put the model out of step with the standard. They
stay as tables in the Business Model Canvas, keyed by element identifier to the
product, resource or capability they attach to.

### Fit is a rule

A value proposition canvas only means something if it fits, and
`discover-business-model` § 3 — Verify fit before presenting checks it before
Direction and again whenever either canvas changes: every Pain is addressed by
at least one Pain Reliever, every Gain is produced by at least one Gain
Creator, every Pain Reliever and Gain Creator traces to a Capability, and
every Product has its own Business Model Canvas. An unaddressed Pain is a
missing capability or a customer the business decided not to serve, and the
canvas says which. The verdict is written in the value proposition canvas,
under its own heading; the layer README carries no fit section.
