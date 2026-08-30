---
name: architecture-document-style
description: Rulebook — consult when creating or editing canonical architecture Markdown so enterprise, domain and solution models remain human-readable, standard, traversable and explicit about ownership.
metadata:
  archreator:
    kind: rulebook
    gates: none
---

# ※ Architecture document style

Canonical architecture is plain-language Markdown with precise secondary
metadata. Builders should understand the subject without learning ArchiMate;
enterprise architects and agents should still be able to navigate the same
facts in a standard way.

## ⊕ When to use this

- Creating, editing, splitting or reviewing anything under `architecture/`.
- Choosing model ownership, standard areas, element identifiers, ArchiMate
  types, relationships, provenance or a diagram.
- Referencing another domain, repository or enterprise/domain/solution model.

Read [the model-structure reference](./references/model-structure.md)
when creating or reorganizing a model or area. Read
[the hierarchical-elements reference](./references/hierarchical-elements.md)
when an element is decomposed into levels or a child-level file is created.
Read
[the domain-boundaries reference](../federate-context/references/domain-boundaries.md)
when deciding a domain boundary or declaring a cross-model contract. Read
[ArchiMate on Mermaid](./references/archimate-on-mermaid.md) before drawing or
changing an architecture view; it is the single source for labels, glyphs,
shapes and the layer palette.

## ⊖ When not to

- General repository documentation with no modeled elements; use
  `document-style` alone.
- A disposable scope or brief under `.archreator/work/`; it cites canonical
  sources but does not become part of them.
- Portal or PDF output. Those are regenerated reading surfaces, never the
  authority for a model fact.

## ⌖ Where this sits

This rulebook realizes no process. It adds the modeling contract to
`document-style` and is consulted by modeling, change, roadmap, question and
federation procedures.

## ※ Rules

### Declare the model and its authority

Every model has one level: **Enterprise**, **Domain** or **Solution**.
`architecture/README.md` is its front door and names the model, purpose,
level, accountable owner, documentation language, parent when one exists and
the boundary of facts it owns.

- Enterprise models own shared business design, direction, capabilities,
  constraints and cross-domain concerns.
- Domain models own domain outcomes, services, information responsibility and
  contracts exposed to enterprise, peers or solutions.
- Solution models own local behavior, representations, components,
  interfaces, runtime and the contracts they consume.

A lower model refines what its parent exposes; it does not restate the parent.
One model owns each fact. Other models link to the definition and add only
their own detail.

### Create areas lazily and navigate them directly

The standard areas are:

| Path | Holds when locally relevant |
| --- | --- |
| `0_business-design/` | Customers, jobs, pains, gains, value propositions, products and business economics |
| `1_strategy/` | Stakeholders, drivers, outcomes, goals, principles, capabilities, resources and constraints |
| `2_business/` | Actors, roles, products, services, processes, business objects, contracts and rules |
| `3_information/` | Meaning, ownership, quality, lifecycle, exchange and data representations |
| `4_application/` | Applications, components, services, interfaces, behavior and integrations |
| `5_technology/` | Platforms, runtimes, nodes, artifacts, deployment and operations |
| `6_transition/` | Accepted targets, plateaus, material gaps, initiatives, dependencies and sequence |
| `decisions/` | Durable rationale for consequential choices a future reader will question |

The front door marks each area **Local**, **External**, **Out of scope** or a
specific **Gap**. That row replaces an empty folder. Create an area's
`README.md` only when supported local content exists; keep content there until
splitting makes navigation or ownership materially clearer.

Areas 0–5 describe current truth. Area 6 describes intended future states and
their sequence. Do not mix planned elements into current catalogues or use a
roadmap as authorization to deliver its initiatives.

### Give every element a stable identity

An identifier is a stable machine anchor for a modeled element. It begins with
a type prefix and number. Use the prefixes and detailed area contract in the
model-structure reference.

- An ID is unique inside its owning model and stays with a surviving element
  when its name or description changes.
- Once an ID has entered the canonical model or is referenced elsewhere, do
  not reuse it for a different element.
- Decomposition extends the parent ID. For example, Order management
  [CAP3.2] is a child of Commerce [CAP3]. The number states hierarchy only
  when the child is a finer element of the same type.
- A domain qualifier precedes the prefix, such as Order handling
  [SALES.BSVC2]. From another model, qualify the anchor as Order handling
  [customer-platform::SALES.BSVC2].
- Number locally rather than inventing globally unique sequences. The model
  and domain qualifiers carry the boundary.
- Assign IDs only to modeled elements. A heading, layer band, explanatory
  node or conditional human decision is not given an element ID merely so a
  diagram can point at it.

Do not use descriptive slug IDs such as `ORDER-FULFILMENT`. Names change as a
business learns, and renaming a slug breaks durable and cross-model
references. A numeric type ID stays anchored to the element while its human
name improves.

Definitions and references deliberately use different forms. A catalogue
definition starts with its ID so it sorts and scans by stable identity. Every
reference outside that definition row is human-first as Order handling
[BSVC2]. A bare ID is valid only in the `ID` cell of the row that defines it;
it is never a prose, relationship, diagram or brief reference.

When an element is decomposed, apply the hierarchical-elements reference. Each
populated level has its own file, every child definition names its parent as
`Name [ID]`, and each file states its full location in the hierarchy. The
dotted ID remains the machine hierarchy; it never substitutes for human
orientation.

### Put plain meaning before precise metadata

Define modeled elements in an ID-first catalogue:

```markdown
| ID | Name | ArchiMate type | Description |
| --- | --- | --- | --- |
| ACMP1 | Order service | Application Component | Accepts and tracks orders. |
```

The name and description are the human interface. `ArchiMate type` uses the
canonical element name as secondary metadata for expert navigation and agent
reasoning. Add `Owner`, `Source`, `Realized by` or another useful attribute
after `Description` when it carries real content. A domain-specific catalogue
may add other columns, but `ID` and `Name` remain first so stable ordering and
human identity stay adjacent. A nested catalogue adds `Parent` immediately
after the base columns and uses `Name [ID]` in that cell.

Outside its definition row, always reference the same element as Order service
[ACMP1]. Relationship tables, prose, diagrams, briefs and other content never
use a bare ID or put it before the name.

An element belongs at the level that owns its meaning, not necessarily in the
repository containing its implementation. Link to parent and external facts
rather than recreating them locally.

### Declare every traversable relationship once

Same-type decomposition is the one specialized form: a nested definition's
`Parent` column declares its Composition relationship and lets a reader move
up without decoding the ID. Do not repeat that relationship below.

Use a relationship table for facts an agent or architect must follow:

```markdown
| From | Relationship | To | Meaning |
| --- | --- | --- | --- |
| Order service [ACMP1] | Realization | Order handling [BSVC1] | The application component realizes the business service. |
```

- `From` and `To` use `Human name [ID]`; the stable IDs define direction and
  the names let a person understand the row without another lookup.
- Use the canonical ArchiMate relationship where it fits: Composition,
  Aggregation, Assignment, Realization, Serving, Access, Influence,
  Association, Triggering, Flow or Specialization.
- `Meaning` says in ordinary language what is true in this context. If no
  ArchiMate relationship fits honestly, use a precise plain relationship
  rather than a false mapping.
- A diagram may render declared relationships; it never owns one. Do not make
  prose or an arrow the only place a traversable fact exists.
- Cross-model relationships retain source model, target model, direction and
  authority boundary. Missing external context is reported, not treated as an
  absent relationship.

### Ground claims and preserve useful provenance

Every important element should be checkable against something real: a team,
role, written procedure, repository path, running service, contract, source
document or accountable person's confirmation. When the realization, owner or
meaning cannot be established, write a specific **Gap** beside that fact.

During discovery, retain a concise source and any material inconsistency.
Never convert plausibility into a model fact. Raw reference material is
evidence rather than architecture and is not published through a portal by
default. Record observable facts, decisions and constraints from a meeting,
not personal judgements about participants.

### Draw focused views

Use Mermaid when relationships, flow, hierarchy or sequence become materially
easier to understand. Follow
[ArchiMate on Mermaid](./references/archimate-on-mermaid.md); do not restate its
notation locally.

- Keep a view focused enough to read without searching a wall of nodes. Split
  by question or section when necessary.
- Label every modeled node
  `<glyph> «ArchiMate type» Human name [ID]`, with the ID last, and label every
  relationship edge.
- Keep an element's layer and type visually consistent within the model.
- Add a local legend only when the notation would otherwise be ambiguous; do
  not repeat a generic legend or “How to read” section on every page.
- The tables remain the source. A visual must not introduce a fact absent from
  them.

### Make delegated authority explicit

An actor is **Human**, **AI** or **Hybrid** when that distinction affects
responsibility. For an AI or hybrid actor with delegated work, record:

| Attribute | Holds |
| --- | --- |
| Autonomy | Advisory, co-pilot, autonomous with checkpoint, or fully autonomous |
| Decision rights | What the actor may decide or change in concrete terms |
| Escalation | The named role receiving work outside its authority or confidence |

Do not add these columns to catalogues with no AI or hybrid actor. A material
change to authority may need a durable decision record explaining why. A view
may give an AI or hybrid actor the notation reference's cyan delegated-authority
accent; its explicit `«Business Actor»` stereotype continues to state the
element's type and layer.

### Keep each document proportionate

A useful canonical document has a title, direct navigation and one compact
`Location` line that identifies its area, hierarchy and parent context without
relying on its path. It then carries a short statement of what is true and why
it matters, followed only by the visuals, element tables, relationship tables,
gaps and sources the subject needs. Remove unused sections. Do not require a
repeated status preamble, notation legend, document changelog, empty retired
table or method explanation.

Trust is expressed where it matters: area status at the front door, sources
and uncertainty beside affected facts, and durable decisions linked to the
elements they explain.

## ⚠ Anti-patterns

- Creating every standard folder before any of it carries content.
- Restating enterprise or domain facts in a lower model.
- A nested file whose level or parent can be discovered only from its filename,
  path or dotted ID.
- Using a bare ID or an ID-first label outside the catalogue row that defines
  it, or using a descriptive slug ID as a supposedly stable anchor.
- Inventing an ArchiMate type or relationship to make a table look complete.
- A relationship that exists only in prose or Mermaid.
- A current-state catalogue containing target elements.
- An ungrounded element presented as fact instead of a specific gap.
- Repeated legends and status boilerplate that displace the subject.
- An AI actor with no stated authority or escalation.
- Federation machinery introduced before a real cross-model need defines it.

## ☑ Done when

- The front door makes boundary, ownership, status and navigation clear.
- Every other canonical file states its location, and every nested definition
  names its parent.
- Every local fact has one owning definition and every external fact is linked.
- Catalogue definitions are ID-first, every reference outside them is
  human-first, relationships are declared and links resolve.
- Plain descriptions are understandable without ArchiMate knowledge while the
  canonical metadata remains available.
- Material claims are grounded or marked with a specific gap.
- Current and future states remain separate.
