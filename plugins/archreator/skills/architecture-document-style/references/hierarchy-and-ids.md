# Element identifiers, levels and namespaces

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

Every document's "How to read this document" table repeats the prefixes it
uses, expanded — `STK#` = Stakeholder — `architecture-document-style`
§ Element IDs carries that rule; this page only holds the registry.

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

**A reference to another model names that model first, separated by two
colons**: `product-archreator::ACMP1`, `sales-platform::EMEA.BSVC3`.

Two colons rather than a third meaning for the dot. The dot already separates
the domain path (before the prefix) from the catalogue's levels (after it), and
one character meaning three things stops being readable. Read outwards: model,
then domain path, then prefix, then levels — each separator appears at most
once, and always in that order.

**The model's name is the one the federation index gives it.** That is the
point rather than a convenience: a model you may reference is a model you have
declared you federate with, in `architecture/federation.md`. There is no way to
reach into something you never said you depend on.

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

