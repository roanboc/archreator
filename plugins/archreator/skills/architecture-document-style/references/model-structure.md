# Model structure

Use this reference when creating or reorganizing canonical architecture. It
defines the common navigation shape without requiring every model to contain
every area.

## Levels and ownership

| Level | Owns | Defers to |
| --- | --- | --- |
| Enterprise | Business design, enterprise direction, shared capabilities, constraints and cross-domain concerns | Domains and solutions for their internal detail |
| Domain | Domain outcomes, services, information ownership and contracts exposed to other models | Enterprise direction and solution internals |
| Solution | Users, local behavior, information representations, components, interfaces, runtime and consumed contracts | Enterprise and domain facts already owned elsewhere |

A lower model refines an exposed contract; it does not restate its parent. A
fact has one owning model.

## Front door

`architecture/README.md` is always present. It names the model, purpose, level,
accountable owner, parent, documentation language and related models. It links
every local canonical document and carries one status for every standard area:

- **Local**: this repository owns useful content and links its `README.md`;
- **External**: a named model owns the context;
- **Out of scope**: the area is not needed here; or
- **Gap**: the area is needed but evidence is missing or inconsistent.

The status row replaces an empty folder. Create a folder only when it becomes
Local and has supported content.

## Standard areas

| Path | Local content |
| --- | --- |
| `0_business-design/` | Customers, jobs, pains, gains, value propositions, offers, channels and economics when the business or operating model is in scope |
| `1_strategy/` | Stakeholders, drivers, assessments, outcomes, goals, principles, capabilities, resources and constraints |
| `2_business/` | Actors, roles, capabilities, products, services, processes, business objects, contracts and rules |
| `3_information/` | Information concepts, meanings, ownership, quality, lifecycle, exchange and data representations |
| `4_application/` | Applications, components, services, interfaces, behavior and integrations |
| `5_technology/` | Technology services, nodes, platforms, runtimes, artifacts, deployment and operations |
| `6_transition/` | Accepted target outcomes, plateaus, material gaps, initiatives, dependencies and sequence |
| `decisions/` | Durable rationale only when a future reader is likely to ask why a material choice was made |

Each local area starts at `<area>/README.md`. Keep content there while it is
easy to navigate. Split a subject into a numbered file only when it is
independently useful, independently owned or the README has become difficult
to scan. The README then links the files in reading order.

## Document shape

Start from [the area template](../assets/area-readme.md), then remove every
unused section and instruction. A useful area normally has:

1. a title, direct navigation and a one-line `Location` cue;
2. one plain paragraph stating what is true and why it matters;
3. a focused Mermaid view only when relationships, flow, hierarchy or sequence
   are easier to understand visually, following
   [ArchiMate on Mermaid](./archimate-on-mermaid.md);
4. an element table when the document defines elements;
5. a relationship table when it connects them; and
6. gaps, external ownership or sources only when there is something real to
   say.

Do not add a generic status preamble, repeated legend, “How to read” section,
empty heading, retired section or document changelog. Put uncertainty beside
the affected fact.

When an element is decomposed, use
[the hierarchical-elements reference](./hierarchical-elements.md) and start a
level file from [the hierarchy-level asset](../assets/hierarchy-level.md). Each
populated level has a file, each nested row names its parent, and every file is
self-locating without requiring its path to be decoded.

## Element identifiers

Use these common prefixes; introduce a more precise one only when the canonical
ArchiMate type has no suitable prefix here.

| Concern | Prefixes |
| --- | --- |
| Business design | `CS` Customer Segment, `JOB`, `PAIN`, `GAIN`, `VP` Value Proposition, `PROD` Product |
| Strategy | `STK` Stakeholder, `DRV` Driver, `ASM` Assessment, `G` Goal, `OUT` Outcome, `P` Principle, `CAP` Capability, `RES` Resource |
| Business | `ACT` Actor, `ROLE`, `BSVC` Business Service, `BPROC` Business Process, `BOBJ` Business Object, `CTR` Contract, `RULE`, `VAL` Value |
| Information | `INFO` Information Concept, `DOBJ` Data Object |
| Application | `APP` Application, `ACMP` Application Component, `ASVC` Application Service, `AIF` Application Interface |
| Technology | `NODE`, `TSVC` Technology Service, `ART` Artifact |
| Transition | `PLAT` Plateau, `GAP` Gap, `INIT` Initiative |

An ID is a stable machine anchor for a modeled element, not its human name.
Hierarchical decomposition appends numeric segments: Order management
[CAP2.1] is a child of Commerce [CAP2]. A reference from another model is
qualified inside the brackets, such as Order handling
[customer-platform::BSVC1]. A domain namespace inside one model precedes the
type prefix, such as Order handling [SALES.BSVC1]. Do not invent globally
unique numbering.

Prefer numeric type IDs to descriptive slug IDs. A business may rename “Order
fulfilment” to “Customer delivery” while it remains the same capability. A
slug derived from the old name must then change and break inbound and
cross-model references; Commerce [CAP2] stays stable while the human name
improves.

Assign an ID only to a modeled element. Do not create one for a heading, layer
band, explanatory diagram node or conditional human decision. The bare ID
appears only in the first cell of the catalogue row that defines the element.
Every reference elsewhere uses `Human name [ID]`; never use a bare ID or an
ID-first form in prose, relationships, diagrams or briefs.

The ID is not sufficient human navigation. A dotted-ID definition includes a
`Parent` column containing `Name [ID]`, and its file's `Location` line names
the hierarchy. Removing the final numeric segment from the child ID must yield
the parent ID.

The base definition columns are stable and keep the machine anchor beside the
human name:

```markdown
| ID | Name | ArchiMate type | Description |
| --- | --- | --- | --- |
| ACMP1 | Order service | Application Component | Accepts and tracks orders. |
```

Add Owner, Source, Realized by or another attribute only when it carries useful
content for that catalogue, after `Description`. A domain-specific catalogue
may add useful columns, but `ID` remains first for stable ordering and `Name`
remains second so the machine anchor and human identity stay adjacent. A
nested catalogue adds `Parent` immediately after `Description`.

## Relationships

Declare traversable relationships once:

- same-type decomposition uses the child catalogue's `Parent` column as its
  canonical Composition relationship; and
- every other relationship uses the relationship table below.

```markdown
| From | Relationship | To | Meaning |
| --- | --- | --- | --- |
| Order service [ACMP1] | Realization | Order handling [BSVC1] | The application component realizes the business service. |
```

Use an ArchiMate relationship when it fits: **Composition**, **Aggregation**,
**Assignment**, **Realization**, **Serving**, **Access**, **Influence**,
**Association**, **Triggering**, **Flow** or **Specialization**. If none fits,
use a precise plain relationship rather than a false mapping. `From` and `To`
use human-first `Name [ID]` endpoints; the IDs preserve direction and
traversal while the names make the row understandable. `Meaning` explains the
fact to a person.

A Mermaid view may render these facts but never owns them. Label every modeled
node `<glyph> «ArchiMate type» Human name [ID]`, label every edge and keep each
view readable without zooming. The notation, shapes and palette are defined
once in [ArchiMate on Mermaid](./archimate-on-mermaid.md). Planned
relationships belong in `6_transition/`; current-area views show current facts.

## Sources and navigation

Keep source material only when it is useful and appropriate for checking a
claim. Link evidence from the affected fact or a short source table. Do not
publish private raw material through the portal by default.

Every canonical file is reachable from its area README and every local area
from `architecture/README.md`. Direct links, stable IDs and declared
relationships are the navigation contract for builders, enterprise architects
and agents. Where an ID is visible, its link text remains human-first as
`Human name [ID]`. Briefs and the portal derive from this contract and
introduce no new facts.
