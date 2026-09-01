# ArchiMate relationships

_Reference for [`architecture-document-style`](../SKILL.md) § Relationships
are declared, never only drawn._

Read this when writing a catalogue column that points at other elements, a
`## Relationships` section beside a diagram, or an edge label — and before
choosing the shape of a view, because **the relationship, more than the
element, is what decides how a diagram reads best**
([`archimate-on-mermaid.md`](./archimate-on-mermaid.md) § The relationship
decides the shape of a view).

## What each relationship represents

The semantics are ArchiMate's, exactly as they are for elements
([`archimate-elements-and-ids.md`](./archimate-elements-and-ids.md) § What
each element represents carries how the deference works; it holds here
identically). The definitions are quoted from the ArchiMate 3.2
Specification (© The Open Group). An edge label or a relationship cell
prefers the role name for its direction — *serves*, *realized by* — and a
domain word is allowed where it says more; nothing machine-maps labels onto
this vocabulary.

| Relationship | Kind | The standard says | Role names |
| ------------ | ---- | ----------------- | ---------- |
| Composition | Structural | An element consists of one or more other concepts | → composed of · ← composed in |
| Aggregation | Structural | An element combines one or more other concepts | → aggregates · ← aggregated in |
| Assignment | Structural | The allocation of responsibility, performance of behavior, storage, or execution | → assigned to · ← has assigned |
| Realization | Structural | An element plays a critical role in the creation, achievement, sustenance, or operation of a more abstract element | → realizes · ← realized by |
| Serving | Dependency | An element provides its functionality to another element | → serves · ← served by |
| Access | Dependency | The ability of behavior and active structure elements to observe or act upon passive structure elements | → accesses · ← accessed by |
| Influence | Dependency | An element affects the implementation or achievement of some motivation element | → influences · ← influenced by |
| Association | Dependency | An unspecified relationship, or one that is not represented by another ArchiMate relationship | associated with · → associated to · ← associated from |
| Triggering | Dynamic | A temporal or causal relationship between elements | → triggers · ← triggered by |
| Flow | Dynamic | Transfer from one element to another | → flows to · ← flows from |
| Specialization | Other | An element is a particular kind of another element | → specializes · ← specialized by |
| Junction | Connector | Connects relationships of the same type | — |

## The relationship table

An element's relationships are **declared**, in one of two places, and a
diagram renders what was declared. A relationship whose only home is a Mermaid
block is a fact living inside a rendering, which `P1` does not allow — and it
is invisible to everything except a person reading that one document.

**A catalogue column declares the relationships a row can carry.** One row per
element, and a column naming what it points at:

| ID | Application service | Realizes | Provided by |
| -- | ------------------- | -------- | ----------- |
| `ASVC1` | **Layer-by-layer alignment** | `BSVC1` | `ACMP1` |

The column header is the relationship, carried verbatim into the projection —
`Realizes`, `Realiza`, `Serves`. Nothing maps it onto ArchiMate's vocabulary,
because a guess there is worse than an honest string.

**A cell declares only when it is a list of identifiers and nothing else.**
`` `ACMP7`, `ACMP8` `` declares two relationships; "A row in `BOBJ3`'s Approvals
table" is prose that mentions one. This is what separates a relationship column
from an attribute column — `Maturity` holds the word "Established" and
`Realizes` holds identifiers, and both are columns of the same catalogue.

**This is the one place a reference is a bare identifier.**
`architecture-document-style` § Element IDs asks a reference in prose or an
ordinary cell to carry the name with the identifier riding along —
`Name [ID]` — so a reader is never sent looking. A relationship column is read by a parser before it is read
by a person, and a name inside it turns the cell into prose the parse stops
seeing — silently, because a column that declares nothing looks exactly like a
column that has nothing to declare. The name belongs in the row's own name
column, and in cells 2 and 4 of the relationship table below, where it is
checked against the catalogue rather than trusted.

**A relationship table declares everything a row cannot.** A catalogue has one
row per element, so it has no shape at all for a relationship between two peers
in the same layer — which is most of them. Give the document a `## Relationships`
section beside the diagram that renders it:

| From | From element | To | To element | Relationship |
| ---- | ------------ | -- | ---------- | ------------ |
| `CAP5` | ✦ «Capability» Learn from an engagement | `CAP1` | ✦ «Capability» Discover a subject from nothing | precedes |

**Read by position, never by header word.** Columns 1 and 3 hold the
identifiers; 2 and 4 describe them; 5 is the relationship; anything after is
notes. A table whose first header is `ID` is a catalogue and is never read as
this, which is what keeps a catalogue with a `Realizes` column from being
mistaken for one. Headers are prose in whatever language the model is written
in, and nothing here reads them — the same arrangement that puts an element's
name in a catalogue's second cell.

**Each end names its archetype and its name, and both are copies.** A node in a
diagram drops its stereotype because glyph, shape and colour carry the type
three times with a legend one screen above; a table cell has none of those, and
`CAP5` alone tells a reader nothing. So the archetype and the name are written
out — and because both are facts owned elsewhere, `check_model.py` holds the
**name** against the catalogue that defines the element and fails on a
mismatch. It is `P1`'s escape clause used exactly as `element-prefixes.json`
uses it: one unavoidable copy, with a check on it.

The **archetype is deliberately not checked**, and the glyph is optional. An
archetype cannot drift away from the prefix sitting in the cell beside it, and
the word for it is language-dependent where the prefix is not — `«Capability»`
in one model is `«Capacidad»` in another, and a registry of English names
cannot judge either.

**A relationship that is not true yet says so in words** — the same
`Pending — future initiative` marker the grounding rule uses — in the notes
column. Never with a dashed arrow: that is a diagram device, and diagrams are
not read.

**A catalogue row says it once, for the whole row, and the marker leads a
cell.** An element that does not exist yet points at nothing that is true yet,
so the marker written for the grounding rule marks every relationship the row
declares — `**Pending — future initiative**` in a `State` or `Note` column, and
the parse reads it. Two rules make that safe and both are load-bearing:

- **It cannot go in the relationship cell.** A cell declares only when it holds
  identifiers and nothing else, so a word written beside one does not qualify
  the relationship — it deletes it.
- **It must start the cell it is in.** A catalogue row is prose as well as
  data, and a sentence *about* pending work is not a pending row. Anchored to
  the start, "**Pending** — no contributor base exists yet" marks the row and
  "stops depending on their availability" does not.

