---
name: core-architecture-doc-style
description: Use when creating or editing any document under architecture/ — numbering, element IDs and the hierarchical numbering of leveled elements (`CAP1`, `CAP1.2`), ArchiMate-on-Mermaid notation, grounding rules, and link conventions for this repo's documentation.
---

# EA documentation style

## Language

Pick one documentation language for the project and use it consistently
across `architecture/`, `architecture/scope/`, commit messages, and code identifiers
(see the project's `CLAUDE.md`). Whatever language is chosen, **folder and
file names stay plain ASCII** (no accents, no non-Latin punctuation) even
if the prose inside is written in a language that uses them — this avoids
cross-platform path and URL-encoding issues. If ArchiMate stereotypes are
translated, keep a correspondence table to the standard English element
names near the top of `architecture/README.md`.

### Write it out

**Language is the interface** — to a human reader, and to an agent that has
nothing but the text. So spell things out:

- **Expand every acronym on its first use in each document**, then use the
  short form freely. Per document, not per project: a reader arriving from a
  deep link shouldn't have to hunt for what a prefix means.
- **Element IDs are acronyms too.** First mention in a document reads
  `CS1` (Customer Segment 1 — business and solution designers), or sits in a
  table whose adjacent column gives the name. Never a bare `CS1` in prose
  the first time.
- **An abbreviation worth using is worth defining.** If the organization has
  its own jargon, it belongs in the glossary in
  `2_business/5_domain-context-and-rules.md`, not only in the head of
  whoever wrote the document.
- **Prefer the full word where it costs nothing.** "Customer segment" reads
  better than "CS" in a sentence; the short form earns its place in tables,
  diagrams, and cross-references where space is genuinely tight.

This costs a few characters and buys the thing the whole method is for: a
document that means the same to the person who wrote it, the person reading
it a year later, and the agent acting on it.

### Consolidate before you enumerate

**Fewer, better-defined elements beat many narrow ones.** Every element in a
catalogue is a row someone has to read and an edge someone has to trace in a
diagram. Ten well-named elements with clear relationships are more useful
than thirty precise ones nobody can hold in their head.

Three rules follow:

- **If two elements differ only in degree, they are one element.** The same
  pain felt by two customer segments at different severity is one pain with
  a severity column — not two pains. The same goes for a capability used
  more heavily by one domain, or a rule enforced more strictly in one place.
- **Merge before you split.** When a list grows past what fits on one screen,
  the first question is which entries are the same thing seen from two
  angles, not how to organise the list.
- **This applies to what an agent proposes, not only to what it writes.**
  Offer a consolidated recommendation, not an exhaustive menu. A Requester
  reading five overlapping options has been handed the analysis work the
  agent was supposed to do.

The reason is the diagrams. The catalogues connect to each other, and the
value of the model is in seeing how — which is exactly what a long list
destroys.

## Numbering

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

## Element IDs

Every element carries a short **ID**: a type prefix followed by a number,
no separator — `G1`, `CAP3`, `PROD2`. IDs are how one document refers to an
element in another without restating it. An element inside a leveled
catalogue extends its parent's ID instead of starting a new number —
`CAP3.2` — see § Levels number hierarchically.

An element is **defined** in one of exactly two shapes, and `check_model.py`
recognizes both:

| Shape | Used for | Example |
| ----- | -------- | ------- |
| The **first column of an inventory table** | Most elements | `` \| `BSVC3` \| Supervised build \| … `` |
| A **bolded lead-in**, ID then an em dash | Goals and Principles, which read better as prose than as rows | `- **G1 — Legible guidance.** A prospective adopter…` |

A **qualified** ID in a first column (`` \| `SALES.BSVC3` \| ``) is a
*reference*, not a definition — that is what a domain charter's "Consumed
services" table holds. Anywhere else, a backticked ID is a reference.

| Where | Prefixes |
| ----- | -------- |
| Motivation | `STK` Stakeholder · `DRV` Driver · `ASM` Assessment · `G` Goal · `OUT` Outcome · `P` Principle |
| Strategy | `CAP` Capability · `RES` Resource · `COA` Course of Action · `VS` Value Stream |
| Business | `ACT` Actor · `ROLE` Role · `BCOL` Business Collaboration · `PROD` Product · `BSVC` Business Service · `BPROC` Business Process · `BOBJ` Business Object · `BIF` Business Interface · `CTR` Contract · `RULE` Business Rule · `VAL` Value |
| Information | `DOBJ` Data Object |
| Application | `ASVC` Application Service · `ACMP` Application Component |
| Technology | `TSVC` Technology Service · `NODE` Node · `ART` Artifact |
| Canvas (VPC) | `JOB` Job · `PAIN` Pain · `GAIN` Gain · `PREL` Pain Reliever · `GCRE` Gain Creator |
| Canvas (BMC) | `KP` Key Partner · `KA` Key Activity · `KR` Key Resource · `VP` Value Proposition · `CR` Customer Relationship · `CH` Channel · `CS` Customer Segment · `RS` Revenue Stream · `COST` Cost |

Every document's "How to read this document" table repeats the prefixes it
uses, expanded — `STK1` = Stakeholder 1 — which is § Write it out applied to
identifiers.

Rules: an ID is assigned once and **never reused** after the element is
removed (a dangling reference should fail loudly, not silently point at
something else); numbering is per prefix, not global — and per parent inside
a leveled catalogue; and an element's ID never changes when it is renamed.
Referencing an element in prose or a table cell means writing its ID —
`relieves GAIN2` — not repeating its description.

### Levels number hierarchically

**An element that decomposes carries its parent's ID plus its own number,
joined by a dot.** Capabilities, processes and products are the usual cases;
any catalogue with levels behaves the same way.

| Level | Capability | Process | Product |
| ----- | ---------- | ------- | ------- |
| **1** | `CAP1` | `BPROC1` | `PROD1` |
| **2** | `CAP1.2` | `BPROC1.3` | `PROD1.2` |
| **3** | `CAP1.2.1` | `BPROC1.3.4` | — |

The last segment is numbered **per parent, not across the level**: the second
child of `CAP1` is `CAP1.2` and the second child of `CAP2` is `CAP2.2`. So
the identifier states where the element sits in the tree, and a reader meeting
`BPROC1.3.4` in a technology document knows which macro process it belongs to
without opening the catalogue.

Two consequences, and they are most of the point:

- **The ID carries the parent, so the table drops its parent column.** A
  `Parent` column beside `CAP1.2` restates what the identifier already says,
  which is DRY — each fact in one place — broken inside a single row. A column naming what a parent is
  *composed of* survives, because it carries the children's **names**, which
  no identifier holds.
- **A level is not a type.** `CAP1.2` is a Capability exactly as `CAP1` is.
  The dot says where it sits, not what it is, and every rule about prefixes,
  glyphs and colours applies to it unchanged.

**Only decomposition is written this way** — a whole-part hierarchy whose
child is a finer-grained element of the same type. Every other relationship
stays a column or an edge: a process realizing a service, a capability using
a resource, a product tier refining its enterprise parent. An identifier can
encode one tree, so it encodes the one the catalogue is organised by.

**Moving an element under a different parent changes its ID.** That is what a
meaningful identifier costs, and it is paid like any other removal: before the
gate that approves the element, renumber it; afterwards, retire the old ID and
define the element under its new parent, with the Retired row naming the ID
that replaced it (§ Never-reused starts at the gate). Re-parenting an approved
process is a modeling change a Requester should be shown — a leveled ID puts
it in front of them instead of letting it pass as an edited column.

### Never-reused starts at the gate

**An identifier is draft until the gate that approves its element, and
permanent afterwards.**

| The element was | Removing it means |
| --------------- | ----------------- |
| **Never approved** — added while drafting, before the gate covering its layer | Renumber so the sequence stays continuous. No Retired row, no note explaining the gap. It never existed as far as the model is concerned |
| **Approved at a gate** | The identifier is retired permanently and never reused, and the retirement is recorded (see `doc-restate-current-state` § The Retired section) |

Which gate covers which element is `core-architecture-first-change` § The gates:
canvases freeze at Gate 0, the strategy layer at Gate 1, business and
information at Gate 2. An element added to an already-approved layer by a
later initiative is draft until *that* initiative's gate.

The reason is what a gap in a sequence should mean. If identifiers freeze the
moment they are typed, a reader finding `CS1`, `CS3`, `CS4` has to wonder what
happened to a customer segment that in fact existed for one afternoon of
drafting and was never shown to anyone. If they freeze at the gate, a gap means
something real was retired — which is exactly what never reusing an identifier
is protecting, and nothing is protected by preserving the history of a draft
nobody approved.

**A gate presentation on a renumbered draft says so in one line.** The
validators only check that references resolve, so renumbering passes silently;
a Requester who reviewed the previous draft will otherwise see identifiers
shift under them without explanation.

**`scripts/check_model.py` enforces this**, and CI runs it: every reference
resolves, no ID is defined twice, no retired ID reappears as live, and every
leveled ID has its parent defined. It checks `architecture/` only. Scope
documents, decision records, and reviews are narrative *about* the model —
they cite retired elements, illustrate the convention, and are frozen once
merged (`core-scope-doc`), so a reference check there could never be made to
pass. Keep IDs accurate in them anyway; nothing but review will catch a
mistake.

### Namespacing across domains

A project modeling multiple domains (see the `discover-domain-modeling` skill and
`architecture/domains/README.md`) qualifies
IDs by domain, the way a module path qualifies a symbol:

| Where the reference is written | How the ID is written | Example |
| ------------------------------- | ---------------------- | -------- |
| Inside the domain that owns the element | bare | `BSVC3` |
| From another domain, or from the enterprise level | `<DOMAIN>.` prefix, domain in upper case | `SALES.BSVC3` |
| An element owned at the enterprise level | always bare | `G1` |

The domain segment is the folder name under `architecture/domains/`, upper-cased
(`domains/sales/` → `SALES.`). A subdomain chains it — `SALES.EMEA.BSVC2` —
which is also why the tree is capped at three levels; beyond that the IDs
stop being readable, and the thing being modeled is a team, not a domain.

**Both qualifiers use a dot, and the prefix tells them apart**: upper-case
segments *before* the prefix are the domain path, numeric segments *after* it
are the catalogue's levels. `SALES.BPROC1.3` is the third process under macro
process `BPROC1`, owned by the sales domain. Read outwards from the prefix and
neither half is ambiguous.

Numbering stays per prefix **per domain**: two domains may both own a
`BSVC3`, and the qualifier is what tells them apart. This is deliberate —
domains are meant to be modeled independently, and forcing globally unique
numbers would make every new domain a merge conflict against every other.

Only a domain's **exposed** services (the ones in its charter) may be
referenced from outside it. Referencing another domain's internal process or
resource by ID reaches through the contract and is a modeling error — take
it up with that domain's charter instead.

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

## Canvas notation

The canvases in `0_business-design/` are Strategyzer artifacts, not
ArchiMate, so they are written as **tables, one per canvas**, not as
diagrams — a nine-block grid is unreadable in Mermaid and a table diffs
cleanly. Each canvas gets its own `###` heading naming the segment or
product it belongs to.

Where a canvas *is* drawn — a layer view showing fit — the canvas block name
is the element type: it goes in the legend (`«Pain»`, `«Gain Creator»`,
`«Customer Segment»`) and not on the nodes, with the Motivation fill for the
customer profile and the Strategy fill for the value map, as in
`architecture/0_business-design/README.md` § Layer view.
The canvas-block-to-ArchiMate-element mapping lives in that same README and
is not restated anywhere else.

## Grounding rule (the most important one)

Every EA element must name the code artifact that realizes it — a page, a
module path, a pipeline file. If you cannot point at the realizing
artifact, either the element doesn't belong in the docs, or the code is
missing and the element should be marked explicitly **"Pending — future
initiative"** (ideally linked to the initiative that will deliver it). This
keeps the whole set verifiable against the code at any time — an outsider
should be able to open any EA document and check it against the repo.

## ArchiMate on Mermaid

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

### Diagrams come first, one per section

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

### Every element document opens with "How to read this document"

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

## Actors: human, AI, and hybrid

`«Business Actor»` and `«Business Role»` nodes name **who** — and in a
system where an AI can hold a role, "who" is no longer implicitly human.
State the actor's kind as `(Human)`, `(AI)`, or `(Hybrid)` (a human and an AI
sharing one role, e.g. a co-pilot pattern). It rides on the node itself —
`⚇ Requester (Human) [ACT1]` — which is the one exception to § ArchiMate on
Mermaid's rule that a content node carries no type word; the legend writes it
against the stereotype, `⚇ «Business Actor (Human)»`. Default to `(Human)`
only when the actor is provably never an AI system acting with delegated
authority — don't omit the qualifier to save space.

When populating `2_business/1_business-actors-and-roles.md`, explicitly
ask, for every role: **does an AI system perform or assist this role, and
at what autonomy?** — don't let "actor" default to human by omission. For
every `(AI)` or `(Hybrid)` actor, the actors table carries three extra
columns beyond the usual name/description:

| Column | Answers |
| ------ | ------- |
| Autonomy level | One of: **advisory** (suggests, a human decides and acts), **co-pilot** (acts, a human reviews before it takes effect), **autonomous with checkpoint** (acts independently, a human is notified and can intervene after the fact), **fully autonomous** (acts independently, no routine human checkpoint) |
| Decision rights | What this actor is actually authorized to decide or change, in concrete terms — not "helps with X" |
| Escalation path | Who/what it hands off to when it's outside its authority or confidence — a Business Role, not a vague "a human" |

If an initiative changes an AI actor's autonomy level or decision rights,
that's exactly the kind of call the `doc-decision-record` skill is for.

## What the document contains: the subject, not its own construction

**Every sentence in an architecture document is either about the subject or
about the act of modeling it. The first belongs here; the second belongs in
the scope document.**

| Stays — it is about the subject | Goes — it is about making the document |
| ------------------------------- | -------------------------------------- |
| "This diagram is the risk, drawn" | "The source material lists seven industries and eight customer types" |
| "`BPROC1` uses no capability — Reach is the only stage the organization does nothing skilful in" | "Writing them as separate elements would have produced an unreadable catalogue" |
| "`VAL1` is the only value every stakeholder receives" | "Twelve pains were consolidated into five" |
| "The areas have no realizing artifact, and that is correct rather than a gap" | "Identifiers were renumbered once, here, before the gate" |

Interpretation of the subject is not only allowed, it is most of what makes a
model worth reading — the left column is the payoff of § Diagrams come first.
What goes is the document narrating its own drafting.

**The removed material is not lost; it moves to where it was already
required.** A consolidation — what was merged into what, and how many elements
each catalogue ended up with — is a modeling decision the Requester approves at
a gate, so it belongs in the scope document and the gate presentation
(`discover-operating-model` § Gate 0 already asks for it there). Writing it in
the layer document as well is a second copy of a fact, which is DRY broken.

### Two carve-outs

- **Anything awaiting validation stays inline.** A "Pending — future
  initiative" marker, an adopted interpretation, a figure nobody has confirmed
  — these sit in the body, where the reviewer who can correct them will see
  them. Moving them to the end is how they stop being corrected.
- **Provenance attaches to elements; history attaches to documents.** A table
  cell naming the initiative that delivered an element is a trace worth
  keeping. A sentence saying the *document* is new as of that initiative is the
  document talking about itself. The first is a reference, the second is a
  narrative.

### No version commentary

No "as of initiative N", no note about what an unapproved proposal would
change, no record of a draft's revisions, no "Retired — None". The document
states what is true now; git holds how it got there and the scope documents
hold why. A model carrying its own changelog gives a reader two accounts to
reconcile and no way to tell which is current.

### Notes that survive go to the end

A note worth keeping that belongs to no single section goes in a final
**Additional notes** section, after the last element group — not woven between
a diagram and the table it explains, where it displaces what the reader came
for.

## Document skeleton

- Title (`# …`), then a nav line:
  `_[← <Layer> layer](./README.md) · [EA home](../README.md)_`
  (scope docs link to the scope index instead).
- State the **ArchiMate elements/viewpoint** covered near the top.
- A **"How to read this document"** section next: the legend diagram and the
  glyph / shape / element / ID-prefix table.
- Then one section per element group, each **opening with its diagram**,
  followed by the inventory table, followed by prose.
- A **Retired** section, only if something approved has been retired
  (`doc-restate-current-state`).
- **Additional notes**, last, and only if there is one — see § What the
  document contains.
- Prefer tables for element inventories, Mermaid for relationships, and
  prose only for rationale (the "why", not the "what" — the diagrams and
  tables already say what), and only where the "why" is about the subject.

## Links

- Always relative, always to a specific file (`../2_business/README.md`,
  not `../2_business/`), keeping `#anchors` when pointing at a section.
- Human-readable link text (`[solution design](./…)`), not raw paths.
- Each fact lives in exactly one document; everything else links to it. If
  you are about to restate a table or diagram, link instead.
- When renaming or moving a doc, grep the whole repo for the old path and
  fix every reference in the same change.
- **Skill files are the exception: they link only within the plugin's own
  `skills/` directory.**
  A skill points at a consuming project's documents by naming the path in a
  code span — `` `architecture/README.md` § Modeling depth `` — never as a
  relative link. Skills ship as a plugin, and installing one copies its
  directory to a cache, so a link reaching outside that directory resolves
  to nothing for anyone who installed rather than cloned.
