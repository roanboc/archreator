# Model structure — Enterprise, Domain and Solution

_Reference for [`architecture-document-style`](../SKILL.md) § What is here, and
what is one file away._

Read this when deciding what a model owns, what it defers to its parent, and
which folders it should actually have.

## What belongs at which tier

A model that federates — an organization with applications built under it —
has the same six layers at every level, and **the layers do not mean the same
thing at each**. Without a rule for that, the same fact gets written twice at
different granularity, which is DRY broken across a boundary rather than
inside a document.

**Tier is not depth.** Depth says how much of the six layers a model fills in
at all. Tier says how much *detail* each layer carries and who it defers to.
Two models at the same depth can sit at different tiers:

| Model | Depth | Tier |
| ----- | ----- | ---- |
| The organization | 2 — Organization | **Enterprise** |
| A product it offers | 1 — Application | **Product** |
| A thing that implements part of that product | 1 — Application | **Implementation** |

### The rule

**A tier may refine what the tier above exposed; it may never restate it. Every
refining element names its parent.**

The same rule holds between federated models in one repository: a product's
tree cites the organization's strategy by federation ID —
`ORG.G#` in a `Serves` column on its goals, a `Sharpens` column on its
drivers — and defines only what the product adds. A motivation layer that
reads correctly with the parent's copied in has restated it.

**And a child's own elements trace to the parent.** What a child defines it
derives from or aligns to something the parent already knows — a stakeholder
column naming the parent element each one refines, a driver sharpening a
parent driver. A child cannot discover a stakeholder the parent has never
heard of: an element that matters to the product but appears nowhere in the
organization's model is a finding **about the organization's model** — raise
it there first, and refine it below once the parent owns it.

| Layer | Enterprise | Product | Implementation |
| --- | --- | --- | --- |
| 0 business-design | Owned | — | — |
| 1 strategy | Owned | Only goals and principles specific to this product and absent above | Cites its parent; adds nothing |
| 2 business | Owned | Product-specific services and rules | Cites its parent, and details only what the implementation requires |
| 3 information | Owned | Product-specific objects | Cites its parent; representations and implementation-specific objects only |
| 4 application | Key components and dependencies | Decomposes its enterprise component | Full component, port and interface design |
| 5 technology | Key nodes and dependencies | Product-specific services | Full runtime, deployment and CI design |

The enterprise layer 4 names **that** an application exists, what it offers,
and who runs it. The tier below says **how** it is built. Neither restates the
other, and the link between them is a column in the enterprise table naming
which model carries the detail.

**An implementation does own business and information elements** — it is not
a bare application and technology model. An AI actor with an autonomy level
and decision rights belongs where the delivery happens, not one tier up in the
abstract. What an implementation may not do is *restate* a service, an actor
or an object the tier above already owns: it cites that one and adds only what
its own delivery requires.

### Telling which tier you are in

Ask what the model is *for*. If it describes a business, it is enterprise. If
it describes something the business offers, it is product. If it describes one
built thing that realizes part of an offer, it is implementation. A model that
would have to restate its parent's elements to make sense is not a tier of its
own — it is a section of its parent.

### Where an implementation's model lives

Either in the product's own tree, or in a tree of its own. **That is the
Requester's call, made per implementation**, and both are legitimate: keep it
local when the implementation needs little design of its own, split it when it
needs a lot. The tier rule is unaffected either way — it governs what the
model contains, not which directory holds it.

