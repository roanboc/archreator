# ArchiMate on Mermaid

_Reference for [`architecture-document-style`](../SKILL.md) § What is here, and what is one file away._

Read this before drawing anything. ArchiMate has no native Mermaid profile —
no element icons, no standard shapes — so these documents encode its semantics
onto Mermaid flowcharts with four devices, and **this file is the single
source** for all of them. Copy its values; never re-tabulate them in a
document. The rules for where a diagram goes are below them.

## 1. Node labels: one line, identifier last

```
<glyph> <description> [<ID>]
```

`✦ <Capability name> [CAP#]`. The `#` marks an example, not an element.

**One line, always.** A label spanning two lines needs the viewer to render
`<br>`, and whether it does depends on that viewer's HTML-label setting. The
identifier sits last in brackets, in the same place on every node, and the
tables below the diagram carry the full context.

**The stereotype does not appear on the node.** `«Business Service»` is written
in exactly one kind of diagram: one whose **subject is the notation** — the
legend under "How to read this document", and the examples in this section.
Everywhere else glyph, shape and colour carry the type already, with the legend
one screen above. A legend node reads
`<glyph> «Stereotype» <what the type is> [<PREFIX>#]`.

**One carve-out: an actor's kind rides on the node.** `(Human)`, `(AI)` or
`(Hybrid)` stays in the label — `⚇ Requester (Human) [ACT1]` — because nothing
else carries it: colour distinguishes an `(AI)` actor and nothing distinguishes
a `(Hybrid)` one
([`archimate-elements-and-ids.md`](./archimate-elements-and-ids.md) § What
each element represents).

## 2. Element glyphs

A glyph identifies the element type at a glance, which matters most in a
**single-layer view** where the layer colour distinguishes nothing. Some
depict the ArchiMate icon; the rest only distinguish, and a document's
legend says which is which.

| Layer | Glyphs |
| ----- | ------ |
| Motivation | `◍` Stakeholder · `✳` Driver · `⌕` Assessment · `◎` Goal · `◉` Outcome · `⚑` Principle |
| Strategy | `✦` Capability · `▤` Resource · `◈` Value · `➤` Course of Action · `⇉` Value Stream |
| Business | `⚇` Actor · `⚉` Role · `▣` Product · `⬭` Business Service · `⊸` Business Interface · `❒` Contract · `⧉` Collaboration · `⚙` Business Process · `▧` Business Object |
| Information | `▦` Data Object |
| Application | `⊞` Application Component · `⬮` Application Service · `⊸` Application Interface |
| Technology | `⬒` Node · `⬯` Technology Service · `⎔` Artifact |
| Implementation & Migration | `≡` Plateau · `⊘` Gap |
| Canvas (VPC) | `◍` Customer Segment · `⚙` Job · `✖` Pain · `✔` Gain · `▣` Product · `⊖` Pain Reliever · `⊕` Gain Creator |
| Canvas (BMC) | `⧉` Key Partner · `⚙` Key Activity · `▤` Key Resource · `⊸` Channel · `⇄` Customer Relationship · `▲` Revenue Stream · `▼` Cost |

**Unicode only** — no SVG icons, no emoji, no image tags. Repeats across
groups are deliberate: a Key Resource *is* a Resource, a Channel *is* a
Business Interface, and an element that appears in two documents looks the
same in both.

## 3. Element shapes

Within one document each element type takes a distinct Mermaid shape. Shapes
are scoped **per document**, not globally — Mermaid has about a dozen usable
ones and ArchiMate has fifty elements — so each document's legend declares its
own. The assignments below are the defaults.

| Shape | Mermaid | Default element |
| ----- | ------- | --------------- |
| Stadium | `id([" "])` | Stakeholder, Business Actor, Business Service, Customer Segment |
| Hexagon | `id{{" "}}` | Driver, Course of Action, Job, Key Activity, Collaboration |
| Flag | `id>" "]` | Assessment, Pain |
| Rounded rectangle | `id(" ")` | Goal |
| Rectangle, double bars | `id[[" "]]` | Outcome, Value Stream stage, Gain |
| Parallelogram | `id[/" "/]` | Principle, Contract |
| Rectangle | `id[" "]` | Capability, Business Role, Product, Business Interface, Channel |
| Cylinder | `id[(" ")]` | Resource, Key Resource |
| Rectangle (cont.) | `id[" "]` | Data Object, Application Component, Node |
| Stadium (cont.) | `id([" "])` | Application Service, Technology Service |
| Parallelogram (cont.) | `id[/" "/]` | Artifact |
| Trapezoid | `id[/" "\]` | Value, Pain Reliever, Gain Creator, Revenue Stream |
| Subroutine | `id[[" "]]` (cont.) | Plateau |
| Circle | `id((" "))` | Gap |
| Inverted trapezoid | `id[\" "/]` | Cost |

## 4. Layer colour, and the tone ramp inside it

**Layer color** via a `classDef` per layer, approximating the standard
ArchiMate palette:

| Layer                      | class            | Fill             |
| --------------------------- | ---------------- | ---------------- |
| Motivation                  | `motivation`     | violet `#e6d6f5` |
| Strategy                    | `strategy`       | sand `#f5deaa`   |
| Business                    | `business`       | yellow `#fffbb5` |
| Application                 | `application`    | cyan `#c2f0ff`   |
| Technology                  | `technology`     | green `#c9e7b7`  |
| Implementation & Migration  | `implementation` | rose `#ffd6d6`   |

This table is the **single source** for the layer palette. Mermaid `classDef`
blocks necessarily inline these hexes per diagram, but no other prose table
restates them.

**In a single-layer view, ramp the layer's hue by element type** — light at
the start of the chain, dark at the end — so type is readable without
hunting for the stereotype. In a **cross-layer** view the flat layer palette
wins instead: there, colour's job is separating motivation from business from
technology, not one motivation element from another.

| Layer | Ramp, light to dark |
| ----- | ------------------- |
| Motivation | Stakeholder `#f4ecfc` → Driver `#e6d6f5` → Assessment `#d8c3f0` → Goal `#c6aae9` → Outcome `#b493e0` → Principle `#a37cd8` |
| Strategy | Resource `#faf0d5` → Capability `#f5deaa` → Value stream stage `#eed4a0` → Value `#e9c987` → Course of Action `#d9ad5c` |
| Business | Actor `#fffbb5` → Role `#f7f099` → Service `#efe57d` → Interface `#e5d95f` → Contract/Collaboration `#d9cc4a` |
| Application | Service `#c2f0ff` → Data Object `#c2f0ff` → Component `#9adcf0` |
| Technology | Service `#c9e7b7` → Artifact `#dcefd0` → Node `#a9d68f` |
| Implementation & Migration | Plateau `#ffe8e8` → Gap `#ffd6d6` |

Strokes darken with the fill. Text stays `#333` throughout.

**Two colours override the layer's own.** An `(AI)` actor is drawn in the
Application cyan even inside a business diagram, so a reader never mistakes it
for a person. An element borrowed from another layer for context keeps its home
layer's colour, shape and glyph, so it reads as a visitor.

## 5. Relationships are declared in tables; a diagram renders them

**A diagram is a rendering.** Nothing reads one — the projection builds the
graph from catalogue columns and relationship tables, so a relationship drawn
in Mermaid and written nowhere else is invisible to every tool. Two places
declare one: a **catalogue column** whose cell is a list of identifiers and
nothing else, and a **`## Relationships` table** beside the diagram it
explains, whose columns are fixed by position — 1 and 3 the identifiers, 2 and
4 `<glyph> «Archetype» <name>`, 5 the relationship, anything after notes. No
header word is read, so the table works in a model written in any language,
and `scripts/check_model.py` holds each end's name against the catalogue that
owns it. The worked example and the full rule are in
[`archimate-relationships.md`](./archimate-relationships.md).

## Drawing rules

Two of them hold their own sections below — § Diagrams come first, one per
section, and § Every element document opens with "How to read this document".
What remains here is the rest:

**Dashed edges mean Pending; solid is true today.** The fact lives in a table
either way — a dashed arrow renders a Pending row, and is never the
declaration itself.

Relationships are labeled with the standard's role name for the drawn
direction — *serves*, *realized by*, *triggers* — the set and both
directions' names being
[`archimate-relationships.md`](./archimate-relationships.md) § What each
relationship represents. Where Mermaid arrowheads can't distinguish relation
types, the label is authoritative.

**A model documented in a language other than English keeps a
stereotype-correspondence table** — translated label → standard ArchiMate
element name — in its own `architecture/README.md`, so the vocabulary stays
traceable back to the standard.

## The relationship decides the shape of a view

A diagram's shape follows the relationships it renders, more than the
elements' layer or aspect:

- **Composition and aggregation nest.** What is composed draws inside its
  owner — containers, boxes inside boxes, one per level, the composite
  domain map being the worked shape. Never draw an arrow for a composition
  that nesting can say.
- **Triggering and flow chain.** Order is the fact, so the shape is a
  left-to-right sequence with labeled handoffs — the process map and the
  value stream.
- **Assignment, realization and serving connect.** These are the labeled
  arrows of most content diagrams — an actor assigned to its roles, a
  component realizing its services, a service serving whom it serves —
  and an element that only carries them never draws alone.
- **Access points at the passive.** Behavior reading or writing an object
  is an arrow into a container — or better, the `Uses` and `Produces`
  columns of a flow table, where the fact is declared anyway.
- **Influence chains motivation** — stakeholder through driver to goal and
  outcome — and **specialization trees**, drawn rarely and small.

The **aspect** is the corollary, not the rule. Each element's aspect is in
[`archimate-elements-and-ids.md`](./archimate-elements-and-ids.md) § What
each element represents; the relationships and their role names are
[`archimate-relationships.md`](./archimate-relationships.md) § What each
relationship represents.

## Diagrams come first, one per section

**This rule is per section, not per document.** A section that has a diagram
**opens with it**, and *that section's* tables and prose follow immediately
below it. The next section opens with its own diagram, and so on down the
document.

**Never stack a document's diagrams at the top.** A gallery of every view
ahead of all the prose is the failure this rule names: each diagram is then
separated from the tables that explain it, and a reader meeting three pictures
before a single row cannot tell which one describes what.

**One diagram per section, not one per document.** Past roughly fifteen
elements a single view of a layer can only be a selection, and a selection
that looks complete teaches the reader something false about the size of the
model. Draw one link of the chain per section, letting consecutive diagrams
overlap by one rank so they can be read as a sequence.

**A diagram earns its place by saying something the table cannot.** Which
element has the most edges, which has none, where every path converges,
which side of a boundary is thin. If a diagram only restates the rows
beneath it, cut it — that is DRY applied to pictures.

## Every element document opens with "How to read this document"

A legend diagram showing this document's element types and how they typically
connect — including any element borrowed from another layer for context. Each
legend node carries everything a reader needs to decode the diagrams below —
`<glyph> «Stereotype» <what the type is> [<PREFIX>#]` — drawn in the
element's own shape and colour. **This is the one diagram that names the
stereotypes**, which is what lets every diagram below it drop them.

**The legend marks itself with `%% legend` as the first line of its Mermaid
body**, on the line after `flowchart …`:

```
flowchart LR
  %% legend
  stk([" ◍ «Stakeholder» whose interests the model serves [STK#] "])
```

The validator reads that marker, not the heading above it, so a stereotype
label is permitted in this diagram and nowhere else whatever language the
document's headings are written in.

**The legend diagram is the whole section — no table restates it.** Its nodes
already name the glyph, the stereotype and the ID prefix, and the diagram
renders each type's shape and colour.

**A layer README that only indexes other documents is exempt**: it has no
elements to legend.

Each layer is then self-documenting: a reader arriving from a deep link has the
notation in front of them and needs no second file open.

