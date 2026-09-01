# ArchiMate elements and identifiers

_Reference for [`architecture-document-style`](../SKILL.md) § Element IDs._

Read this when allocating an identifier, numbering a level, retiring an
element, or writing a reference that crosses a domain or a model.

## The prefix registry

A prefix says what kind of thing an element is, and this table is the whole
list. A model that needs a prefix not named here is proposing a method change,
not picking a convenience — `scripts/element-prefixes.json` in the project is
the machine-readable copy, and `check_skills.py` holds the two in step.

| Where | Prefixes |
| ----- | -------- |
| Motivation | `STK` Stakeholder · `DRV` Driver · `ASM` Assessment · `G` Goal · `OUT` Outcome · `P` Principle |
| Strategy | `CAP` Capability · `RES` Resource · `COA` Course of Action · `VS` Value Stream |
| Business | `ACT` Actor · `ROLE` Role · `BCOL` Business Collaboration · `PROD` Product · `BSVC` Business Service · `BPROC` Business Process · `BOBJ` Business Object · `BIF` Business Interface · `CTR` Contract · `RULE` Business Rule · `VAL` Value |
| Information | `DOBJ` Data Object |
| Application | `ASVC` Application Service · `ACMP` Application Component |
| Technology | `TSVC` Technology Service · `NODE` Node · `ART` Artifact |
| Implementation & Migration | `PLAT` Plateau · `GAP` Gap |
| Canvas (VPC) | `JOB` Job · `PAIN` Pain · `GAIN` Gain · `PREL` Pain Reliever · `GCRE` Gain Creator |
| Canvas (BMC) | `KP` Key Partner · `KA` Key Activity · `KR` Key Resource · `VP` Value Proposition · `CR` Customer Relationship · `CH` Channel · `CS` Customer Segment · `RS` Revenue Stream · `COST` Cost |

Every document's "How to read this document" legend carries the prefixes it
uses on its nodes, expanded — `«Stakeholder» … [STK#]` —
`architecture-document-style` § Element IDs carries that rule; this page
holds the registry and, below it, what each element means.

## What each element represents

**The semantics are ArchiMate's, not this method's.** Where archreator says
nothing about what an element means, the
[ArchiMate® specification](https://pubs.opengroup.org/architecture/archimate32-doc/)
decides — and where the two ever disagree, the specification prevails over
any transcription here. The one-liners below are quoted from the ArchiMate
3.2 Specification (© The Open Group; ArchiMate is a registered trademark of
The Open Group) so a model can be built where the specification is not
reachable, which an agent's environment often is not.

Two columns are the method's own. **Aspect** carries the standard's
classification — active structure, behavior, passive structure, with
motivation and composite beside them — because the aspect is what decides
how a catalogue draws best
([`archimate-on-mermaid.md`](./archimate-on-mermaid.md) § The relationship
decides the shape of a view). **This method adds** holds archreator's considerations
for working the element, where there are any — practice beside the
definition, never a redefinition.

**New element guidance lands in that column first.** An instruction about
one element — how it levels, when it earns a row, how it draws — goes into
its cell as it is learned, and earns a reference file of its own only when
it outgrows the row. Fewer documents saying more is what keeps the
structure consistent.

### Motivation

| Prefix | Element | Aspect | The standard says it represents | This method adds |
| ------ | ------- | ------ | ------------------------------- | ---------------- |
| `STK` | Stakeholder | Motivation | The role of an individual, team, or organization (or classes thereof) that represents their interests in the effects of the architecture | A child model's stakeholders refine the parent's ([`model-structure.md`](./model-structure.md)) |
| `DRV` | Driver | Motivation | An external or internal condition that motivates an organization to define its goals and implement the changes necessary to achieve them | — |
| `ASM` | Assessment | Motivation | The result of an analysis of the state of affairs of the enterprise with respect to some driver | — |
| `G` | Goal | Motivation | A high-level statement of intent, direction, or desired end state for an organization and its stakeholders | A child model's goals serve the parent's, cited by federation ID |
| `OUT` | Outcome | Motivation | An end result, effect, or consequence of a certain state of affairs | Each row says how it is checked — and honestly when there is no method yet |
| `P` | Principle | Motivation | A statement of intent defining a general property that applies to any system in a certain context in the architecture | — |

### Strategy

| Prefix | Element | Aspect | The standard says it represents | This method adds |
| ------ | ------- | ------ | ------------------------------- | ---------------- |
| `CAP` | Capability | Behavior | An ability that an active structure element, such as an organization, person, or system, possesses | Areas at level 1, capabilities at level 2 — the subject's own, one per key activity where canvases exist (`discover-strategy`) |
| `RES` | Resource | Structure | An asset owned or controlled by an individual or organization | — |
| `COA` | Course of Action | Behavior | An approach or plan for configuring some capabilities and resources of the enterprise, undertaken to achieve a goal | — |
| `VS` | Value Stream | Behavior | A sequence of activities that create an overall result for a customer, stakeholder, or end user | — |

### Business

| Prefix | Element | Aspect | The standard says it represents | This method adds |
| ------ | ------- | ------ | ------------------------------- | ---------------- |
| `ACT` | Business Actor | Active structure | A business entity that is capable of performing behavior | An actor earns its row by filling or assisting a role of *this* model — a mere dependency is a partner, a contract and a node. State the kind, `(Human)`, `(AI)` or `(Hybrid)`, on the node and in the row, defaulting to human only when the actor provably never is an AI acting with delegated authority. An `(AI)` or `(Hybrid)` actor's row also carries its autonomy level — advisory, co-pilot, autonomous with checkpoint, fully autonomous — its concrete decision rights, and the role it escalates to; changing any of those is a `record-decision` call |
| `ROLE` | Business Role | Active structure | The responsibility for performing specific behavior, to which an actor can be assigned, or the part an actor plays in a particular action or event | For every role, ask whether an AI system performs or assists it, and at what autonomy — never let "actor" default to human by omission |
| `BCOL` | Business Collaboration | Active structure | An aggregate of two or more business internal active structure elements that work together to perform collective behavior | — |
| `BIF` | Business Interface | Active structure | A point of access where a business service is made available to the environment | — |
| `BPROC` | Business Process | Behavior | A sequence of business behaviors that achieves a specific result such as a defined set of products or business services | Levels follow the standard process hierarchy — the four categories band the map, macro processes at level 1, processes at level 2, activities below only on pain (`process-and-capability-levels`) |
| `BSVC` | Business Service | Behavior | Explicitly defined behavior that a business role, business actor, or business collaboration exposes to its environment | — |
| `PROD` | Product | Composite | A coherent collection of services and/or passive structure elements, accompanied by a contract or set of agreements, offered as a whole to internal or external customers | — |
| `BOBJ` | Business Object | Passive structure | A concept used within a particular business domain | — |
| `CTR` | Contract | Passive structure | A formal or informal specification of an agreement between a provider and a consumer that specifies the rights and obligations associated with a product and establishes functional and non-functional parameters for interaction | — |
| `VAL` | Value | Motivation | The relative worth, utility, or importance of a concept | — |
| `RULE` | Business Rule | Motivation | **archreator's own, no ArchiMate counterpart** — a declared constraint on how the business operates, which systems must honor | — |

### Information

| Prefix | Element | Aspect | The standard says it represents | This method adds |
| ------ | ------- | ------ | ------------------------------- | ---------------- |
| `DOBJ` | Data Object | Passive structure | Data structured for automated processing | Breaks down as data domains at level 1, then data objects extending the ID — drawn as a composite, objects nested in their domains (`process-and-capability-levels`) |

### Application

| Prefix | Element | Aspect | The standard says it represents | This method adds |
| ------ | ------- | ------ | ------------------------------- | ---------------- |
| `ASVC` | Application Service | Behavior | An explicitly defined exposed application behavior | — |
| `ACMP` | Application Component | Active structure | An encapsulation of application functionality aligned to implementation structure, which is modular and replaceable | Every component names the path that realizes it — the grounding rule applied literally |

### Technology

| Prefix | Element | Aspect | The standard says it represents | This method adds |
| ------ | ------- | ------ | ------------------------------- | ---------------- |
| `TSVC` | Technology Service | Behavior | An explicitly defined exposed technology behavior | — |
| `NODE` | Node | Active structure | A computational or physical resource that hosts, manipulates, or interacts with other computational or physical resources | — |
| `ART` | Artifact | Passive structure | A piece of data that is used or produced in a software development process, or by deployment and operation of an IT system | — |

### Implementation & Migration

| Prefix | Element | Aspect | The standard says it represents | This method adds |
| ------ | ------- | ------ | ------------------------------- | ---------------- |
| `PLAT` | Plateau | Composite | A relatively stable state of the architecture that exists during a limited period of time | — |
| `GAP` | Gap | Passive structure | A statement of difference between two plateaus | — |

The canvas prefixes are not here because they are not ArchiMate: they are
Strategyzer's blocks — the Value Proposition Canvas pairs and the Business
Model Canvas nine — and the how-to-read legend of each canvas document
carries how they read
([`canvases.md`](./canvases.md)).

## Levels number hierarchically

**An element that decomposes carries its parent's ID plus its own number,
joined by a dot.** Capabilities, processes and products are the usual cases;
any catalogue with levels behaves the same way.

| Level | Capability | Process | Product |
| ----- | ---------- | ------- | ------- |
| **1** | `CAP#` | `BPROC#` | `PROD#` |
| **2** | `CAP#.#` | `BPROC#.#` | `PROD#.#` |
| **3** | `CAP#.#.#` | `BPROC#.#.#` | — |

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

## Never-reused starts at the gate

**An identifier is draft until the gate that approves its element, and
permanent afterwards.** Which of the two a reader is looking at is declared at
the top of the document — § Document status — so this rule is visible rather
than remembered.

| The element was | Removing it means |
| --------------- | ----------------- |
| **Never approved** — added while drafting, before the gate covering its layer | Renumber so the sequence stays continuous. No Retired row, no note explaining the gap. It never existed as far as the model is concerned |
| **Approved at a gate** | The identifier is retired permanently and never reused, and the retirement is recorded (see `restate-current-state` § The Retired section) |

Which gate covers which element is `align-change-through-layers` § The gates:
canvases and the strategy layer freeze at Direction, business and
information at Understanding. An element added to an already-approved layer by a
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
merged (`write-scope-document`), so a reference check there could never be made to
pass. Keep IDs accurate in them anyway; nothing but review will catch a
mistake.

## Namespacing across domains

A project modeling multiple domains (see the `model-domains` skill and
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

## Crossing a model boundary

An identifier is scoped to its model. Two models may each own a `G1`, which is
deliberate — globally unique numbering would make every new model a merge
conflict against every other — and it is why a bare identifier can only ever
mean something inside the model that wrote it.

**A reference to another model leads with that model's federation ID**:
`ORG.STK#`, `PRD_MTD.BSVC#`, `DMN_SALES.EMEA.BSVC#`. The federation ID is a
short uppercase code built from the tier — `ORG` for the organization,
`DMN_<NAME>` for a domain, `PRD_<NAME>` for a product — and the hierarchy
runs Organization, then Domain, then Product; the component below a product
keeps no model tree of its own and therefore no federation ID. The tier code
stands alone only where the tier cannot have siblings, which is the
organization alone: a domain or product carries its short name from birth,
because a second one arriving must never rename the first. **A federation ID
is stable once granted, exactly like an element's.**

The underscore belongs inside the ID, so the dot keeps exactly two meanings:
ownership before the type prefix — a federation ID, a domain path, or both —
and catalogue levels after it. Read outwards: model, then domain path, then
prefix, then levels; each kind of segment appears at most once, and always
in that order. One grammar carries domains and federation alike; which one a
qualifier is depends on what the model declared, never on how it is spelled.

**A model declares its own federation ID once, on its front door** — a
`**Federation ID:** \`ORG\`` line in its `architecture/README.md` — and the
citing model maps the IDs it uses in `architecture/federation.md` (cell 1
the ID, cell 2 the model's key). That mapping is the point rather than a
convenience: a model you may reference is a model you have declared you
federate with, and `check_model.py` holds the mapping against the ID the
target's own front door declares. There is no way to reach into something
you never said you depend on.

**How it resolves depends on where the other model is**, and the two cases are
genuinely different:

| The model is | Resolution | What can go wrong |
| ------------ | ---------- | ----------------- |
| **In this repository** | Against that model's own definitions, exactly and immediately | A stale identifier fails the build, like any other |
| **In another repository** | Against a row in `architecture/imports.md` declaring it | The row can be internally consistent and out of date |

Nothing fetches anything. A validator that read a sibling repository on every
pull request would be slow, would fail when somebody else's site was down, and
would let another team's push break this build. What is checked is that the
dependency was **stated** — and the name the import row restates is held
against the upstream only when the upstream is here to be read.

