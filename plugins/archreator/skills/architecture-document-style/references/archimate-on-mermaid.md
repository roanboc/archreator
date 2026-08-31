# ArchiMate on Mermaid

_Reference for [`architecture-document-style`](../SKILL.md) § What is here, and what is one file away._

Read this before drawing anything. It carries the four devices that encode
ArchiMate semantics onto Mermaid, and the rules for where a diagram goes.

ArchiMate has no native Mermaid profile — no element icons, no standard
shapes. These documents encode ArchiMate semantics onto Mermaid flowcharts
with four devices, and **this file is the single source** for all of them. Copy its values;
never re-tabulate them in a document.

## 1. Node labels: one line, identifier last

```
<glyph> <description> [<ID>]
```

`✦ <Capability name> [CAP#]`. The `#` marks an example, not an element.

**One line, always.** A label spanning two lines needs the viewer to render
`<br>`, and whether it does depends on that viewer's HTML-label setting — so
the same diagram reads correctly in one place and runs together into a single
string in another. A single-line label cannot break anywhere. The identifier
sits last in brackets, still in the same place on every node, and the tables
below the diagram carry the full context.

**The stereotype does not appear on the node.** `«Business Service»` is written
in exactly one kind of diagram: one whose **subject is the notation** — the
legend under "How to read this document", and the examples in this section.
Everywhere else the type is already carried three times, by glyph, shape and
colour, with the legend one screen above; a fourth carrier is the widest thing
on the node and the least informative. A legend node reads
`<glyph> «Stereotype» <what the type is>`, and it is the only place the word
earns its width.

**One carve-out: an actor's kind rides on the node.** `(Human)`, `(AI)` or
`(Hybrid)` stays in the label — `⚇ Requester (Human) [ACT1]` — because it is
information nothing else carries. Colour distinguishes an `(AI)` actor and
nothing distinguishes a `(Hybrid)` one, and defaulting a reader to "person" is
the mistake § Actors exists to prevent.

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

`⌕` is ArchiMate's Assessment magnifier, `◎` its Goal, `◉` its Outcome, `⊸`
its interface lollipop; `✳` echoes the Driver's steering wheel; `▧` is a
deliberate near-neighbour of `▦`, because a Business Object and the Data
Object holding it are usually one thing seen from two layers; `⊖`/`⊕` and
`▲`/`▼` make canvas arithmetic visible. **Unicode only** — glyphs render
everywhere Markdown does, which was found not to be true of the alternatives
tried before (SVG icons, emoji, image tags).

Repeats across groups are deliberate: a Key Resource *is* a Resource, a
Channel *is* a Business Interface, and an element that appears in two
documents should look the same in both.

## 3. Element shapes

Within one document each element type takes a distinct Mermaid shape. Shapes
are scoped **per document**, not globally — Mermaid has about a dozen usable
ones and ArchiMate has fifty elements — so each document's legend declares
its own. The assignments below are the defaults; follow them where the
element appears.

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

This table is the **single source** for the layer palette; the `architecture-document-style`
skill and every other document point here for the exact fills. Mermaid
`classDef` blocks necessarily inline these hexes per diagram (Mermaid has no
cross-file classDef), but no other prose table restates them.

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

Strokes darken with the fill. Text stays `#333` throughout — every fill above
is light enough to carry it in both GitHub themes.

**Two colours override the layer's own.** An `(AI)` actor is drawn in the
Application cyan even inside a business diagram, because a reader should
never mistake it for a person. And an element borrowed from another layer for
context keeps its home layer's colour, shape and glyph, so it is recognisable
as a visitor.

## 5. Relationships are declared in tables; a diagram renders them

**A diagram is a rendering.** Nothing reads one — the projection builds the
graph from catalogue columns and relationship tables, and a relationship drawn
in Mermaid and written nowhere else is invisible to every tool and to every
reader who is not looking at that document.

Two places declare one:

- **A catalogue column**, when its cell is a list of identifiers and nothing
  else. The header is the relationship's name.
- **A `## Relationships` table**, beside the diagram it explains, for anything
  a single row cannot carry — above all a relationship between two peers in one
  layer, which a catalogue has no column shape for.

Its columns are fixed by position: 1 and 3 hold the two identifiers, 2 and 4
describe them as `<glyph> «Archetype» <name>`, 5 is the relationship, and
anything after is notes. No header word is read, so the table works in a model
written in any language. The worked example and the full rule — where the
`Pending` marker may go, and what is held against the catalogue — are in
[`relationship-tables.md`](./relationship-tables.md), and not here. **Each end
names its archetype and its name because a table cell has no glyph, shape or
colour to carry the type** — and because the name is a copy of what the
catalogue owns, `scripts/check_model.py` holds the two in step.

**Dashed edges mean Pending in a diagram; a table says it in words**, with the
same `Pending — future initiative` marker the grounding rule uses.

## Drawing rules

- **Diagram first, then the tables and prose that describe it.** Every
  section that has a diagram opens with it.
- **One diagram per section, not one per document.** A single view of a whole
  layer can only be a selection once the layer passes about fifteen elements,
  and a selection that looks complete is worse than several honest parts.
  Sectional diagrams overlap by one rank so a reader can chain them.
- **Each document opens with a "How to read this document" section**: a
  legend diagram showing the element types and how they connect, then the
  glyph / shape / element / ID-prefix table. Layers are self-documenting;
  nobody should need another file open to read one. **This legend is what
  makes § 1 affordable** — it is the one diagram that names the stereotypes,
  so the diagrams below it don't have to.
- **Dashed edges mean Pending.** Solid is true today.

Relationships are labeled with their ArchiMate name: **serves**,
**realizes**, **assigned to**, **accesses**, **triggers**, **flow**,
**aggregates**, **influences**. Where Mermaid arrowheads can't distinguish
relation types, the label is authoritative.

**A model documented in a language other than English keeps a
stereotype-correspondence table** — translated label → standard ArchiMate
element name — in its own `architecture/README.md`, so the vocabulary stays
traceable back to the standard.

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

