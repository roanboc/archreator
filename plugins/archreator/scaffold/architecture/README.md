# Enterprise Architecture — <Project Name>

_[← Repository README](../README.md) · [Scope documents](./scope/README.md)_

This folder is the **primary documentation of the system**, organized as an
ArchiMate-layered enterprise architecture. Every element is grounded in the
implemented solution: entries name the page, module, or pipeline file that
realizes them (or are marked explicitly **"Pending — future initiative"**),
so the architecture can be verified against the code at any time.

Folders and files carry a numeric prefix giving the order in which they are
assessed. **Any change in requirements is aligned through these layers in
this order — strategy first, technology last — and captured in a
[scope document](./scope/README.md) before implementation starts** (see
[CONTRIBUTING.md](https://github.com/roanboc/archreator/blob/main/CONTRIBUTING.md) and the
`align-change-through-layers` skill).

## Layers, in assessment order

| #   | Layer                                       | ArchiMate viewpoint      | Answers                                                                       |
| --- | -------------------------------------------- | ------------------------ | ------------------------------------------------------------------------------ |
| 0   | [0_business-design/](./0_business-design/README.md) | _none — business design input_ | Who are the customers, what do they need, and how does each offering pay? |
| 1   | [1_strategy/](./1_strategy/README.md)       | Motivation + Strategy    | Why does this exist? Who cares? What capabilities and value stream?           |
| 2   | [2_business/](./2_business/README.md)       | Business layer           | Who does what? Which services are offered, through which processes?          |
| 3   | [3_information/](./3_information/README.md) | Passive structure (data) | What information exists, where does it live, how does it flow?               |
| 4   | [4_application/](./4_application/README.md) | Application layer        | Which software services and components realize the business services?       |
| 5   | [5_technology/](./5_technology/README.md)   | Technology layer         | What runs it all — runtimes, tooling, build, hosting, deployment?            |
| 6   | [6_transition/](./6_transition/README.md) | Implementation & Migration | Where should this go, what stands in the way, and in what order?              |
| —   | [domains/](./domains/README.md)             | _the same layers, nested_ | Which business lines own their own model, and what they expose to each other |
| —   | [reference/](./reference/README.md)         | _none — source material_ | What was this built from — which transcript, deck or document said so?         |

Layer `0` is the odd one out: it holds no ArchiMate elements at all, only
the Value Proposition and Business Model canvases the architecture is
**derived** from. It is filled in only when the initiative is modeling an
organization rather than building a single application — see
[0_business-design/](./0_business-design/README.md), which carries the
block-by-block mapping into layers 1 and 2. An application project leaves
the folder empty and starts at layer 1.

## Modeling depth

The same six layers describe a weekend application and a company with twenty
business lines. What changes is **how much of them gets filled in, and which
gates apply** — not which folders exist. Every project declares one of three
depths in `AGENTS.md`:

| Depth | The subject is | `0_business-design/` | `1_strategy/` | `domains/` | Gates |
| ----- | -------------- | -------------------- | ------------- | ---------- | ----- |
| **1 — Application** | one application; no organization is modeled | not used | light — goals and principles, enough to judge a change against | not used | 2, and 3 if requested |
| **2 — Organization** | one organization, sharing one model | canvases per segment and product | full | not used | 0–3 |
| **3 — Enterprise** | several business lines, each owning its own model | per domain that needs one | full, at the enterprise level and per domain | [the domain tree](./domains/README.md) | 0–3, plus the consuming domains' Requesters on any cross-domain contract change |

Rules that make the ladder work:

- **The agent declares the depth out loud** and says why, at
  `align-change-through-layers` Step 1a. A Requester told "I'm treating this as Depth 1 —
  one application, light strategy layer; say the word if you want the
  organization modeled properly" can correct it in a sentence.
- **Depth is a starting posture, never a ceiling.** Deepening is its own
  initiative — Depth 1 → 2 makes the organization the subject and fills the
  canvases; Depth 2 → 3 splits the model into domains. Descoping collapses
  the tree. Both are the Requester's call, recorded like any other change.
- **Every depth still gets all seven layer folders.** A layer with nothing to
  say yet is marked "not started" in its README's table, not deleted — an
  unfilled layer is a known gap, a missing folder is an unknown one.
- **Depth is about the subject, not the effort.** A large application is
  still Depth 1. A two-person consultancy modeling how it works is Depth 2.

Files inside each layer folder are numbered the same way; each layer README
explains its own analysis order. Delivered initiatives (ArchiMate
Implementation & Migration viewpoint) are documented per initiative in
[../scope/](./scope/README.md), not here — the numbered layers describe the
**current** state; scope documents describe the **changes** that produce it.

Where the architecture is *going* is neither of those, and it has a folder of
its own: [6_transition/](./6_transition/README.md) holds the target plateaus, the gaps
between them and today, and the order the gaps are closed in. **It is the only
place in the model permitted to describe a future**, which is what lets every
numbered layer be read as a description of now without qualification.

And what all of it was *built from* is in [reference/](./reference/README.md):
the transcripts, decks and documents somebody provided, kept as they arrived.
Not the model, not published, and not read by the validators — it is what a
claim in the model can be taken back to when somebody asks where it came from.

## Document status

Every document that defines an element declares, in its preamble, how far it
has been validated:

| Glyph | Status | A reader may |
| ----- | ------ | ------------ |
| `○` | **Not started** | Take nothing from it. The document exists so the gap is visible |
| `◐` | **Draft catalogue** | Read it as a list of things somebody said exist, with notes. Not approved, identifiers still draft, nothing here to be built on |
| `●` | **Validated** | Rely on it. Confirmed on a named date by its gate — or, where no gate covers the layer, by the recorded decision that routed it elsewhere. Identifiers permanent |

**A draft catalogue is not an architecture draft.** An architecture draft
proposes how something should be structured; a draft catalogue records what
somebody said is there, so that it can be checked. A catalogue and an approved
layer are the same shape on the page, and this marker is the only thing
separating them — which is why a document defining elements without one fails
`scripts/check_model.py`.

Draft catalogues carry `Source` and `Notes` columns; at the gate `Source`
stays and `Notes` is emptied. The full rule, and what each glyph obliges, is
in the `architecture-document-style` skill § Document status.

## Notation conventions

ArchiMate has no native Mermaid profile — no element icons, no standard
shapes. These documents encode ArchiMate semantics onto Mermaid flowcharts
with four devices, and this section is the **single source** for all of them.

### 1. Node labels: one line, identifier last

```
<glyph> <description> [<ID>]
```

`✦ Business understanding [CAP1]`, then `✦ Model stewardship [CAP2]`.

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

### 2. Element glyphs

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

### 3. Element shapes

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

### 4. Layer colour, and the tone ramp inside it

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

### 5. Relationships are declared in tables; a diagram renders them

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
written in any language. The worked example is in
`architecture-document-style` § The relationship table, and not here — a
specimen identifier in the scaffold ships into every generated project as a
reference to an element nobody defined. **Each end names its archetype and its name because a table cell
has no glyph, shape or colour to carry the type** — and because the name is a
copy of what the catalogue owns, `scripts/check_model.py` holds the two in step.
The `architecture-document-style` skill is the single source for the full rule.

**Dashed edges mean Pending in a diagram; a table says it in words**, with the
same `Pending — future initiative` marker the grounding rule uses.

### Drawing rules

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

<!--
  If this project documents in a language other than English, keep a
  stereotype-correspondence table here (translated label → standard
  ArchiMate element name) so the vocabulary stays traceable. See the
  architecture-document-style skill.
-->

## Layered overview

<!--
  TEMPLATE — replace with the project's real stakeholders, goal, value
  stream, business service(s), application component(s), and technology
  node(s) once they're known. Keep the shape (one subgraph per layer, a
  classDef per layer, ArchiMate relationship labels on the edges), and the
  label form from § 1: glyph, description, identifier — no stereotype.
-->

```mermaid
flowchart TB
  subgraph MOT["Motivation & Strategy"]
    goal("◎ <Why this exists> [G1]"):::motivation
    vs[["⇉ <Stage 1 → Stage 2 → …> [VS1]"]]:::strategy
  end

  subgraph BUS["Business layer"]
    svc(["⬭ <What's offered> [BSVC1]"]):::business
    actor(["⚇ <Who uses it> (Human) [ACT1]"]):::business
  end

  subgraph APP["Application layer"]
    app["⊞ <What realizes the service> [ACMP1]"]:::application
  end

  subgraph TEC["Technology layer"]
    tech["⬒ <What it runs on> [NODE1]"]:::technology
  end

  goal -->|realized by| vs
  vs -->|realized by| svc
  actor -->|served by| svc
  svc -->|realized by| app
  app -->|runs on| tech

  classDef motivation fill:#e6d6f5,stroke:#7e57c2,color:#333
  classDef strategy fill:#f5deaa,stroke:#c8a24a,color:#333
  classDef business fill:#fffbb5,stroke:#b8a200,color:#333
  classDef application fill:#c2f0ff,stroke:#0288d1,color:#333
  classDef technology fill:#c9e7b7,stroke:#558b2f,color:#333
```

## Reading order

Top-down (recommended for newcomers — the same order as the folder numbers).
If the project modeled an organization, start one step earlier, at
[0_business-design/1_value-proposition-canvas.md](./0_business-design/1_value-proposition-canvas.md)
→ [0_business-design/2_business-model-canvas.md](./0_business-design/2_business-model-canvas.md),
and read the strategy layer as their consequence:
[1_strategy/1_motivation.md](./1_strategy/1_motivation.md)
→ [1_strategy/3_value-stream.md](./1_strategy/3_value-stream.md)
→ [2_business/2_business-services.md](./2_business/2_business-services.md)
→ [3_information/1_data-objects.md](./3_information/1_data-objects.md)
→ [4_application/2_application-components.md](./4_application/2_application-components.md)
→ [5_technology/2_deployment.md](./5_technology/2_deployment.md).

Bottom-up (for developers verifying alignment): start from
[4_application/2_application-components.md](./4_application/2_application-components.md),
which links each component to its source file, then trace upward via the
"realizes" relationships.
