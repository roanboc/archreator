# Hierarchical elements

Use this reference when a modeled element is decomposed into levels. It
applies to Business Processes, Capabilities, Data Objects and any other
ArchiMate element whose children refine a parent of the same type.

The identifier carries hierarchy for machines. The document must state that
hierarchy in words for people.

## Give every populated level a file

Once a hierarchy is decomposed, create one file for each level that actually
contains elements. One file may catalogue every element at that level. Split a
large level by parent branch only when navigation, ownership or readability
improves.

- Level 1 establishes the whole useful boundary.
- Level 2 refines the Level 1 elements.
- Level 3 exists only where a named need justifies more detail.
- Do not create a file for an empty or anticipated level.
- The owning area README links the level files in reading order.
- A parent level links to every populated child-level file beneath it.

Filenames may carry an order and a useful subject, but a reader must never have
to decode a path or filename to discover the current level or parent.

## Make every page self-locating

Every canonical file except `architecture/README.md` begins with three small
orientation cues:

1. an H1 that names the subject and, for a hierarchy file, its level;
2. direct navigation back to the architecture front door and owning area; and
3. one `**Location:**` line naming the hierarchy from broadest context to the
   subject of the file.

For a file that expands one parent branch:

```markdown
# Validate an order [BPROC2.2] — Level 3 sub-processes

_[Architecture](../../README.md) · [Business](../README.md) · [Process index](./README.md)_

**Location:** Business → Business processes → Fulfil customer demand [BPROC2]
→ Validate an order [BPROC2.2] → Level 3.
```

For a level file containing children of several parents:

```markdown
# Business processes — Level 2

_[Architecture](../../README.md) · [Business](../README.md) · [Process index](./README.md)_

**Location:** Business → Business processes → Level 2. Each element's parent
is named in the catalogue.
```

Keep this line factual. It replaces a repeated “How to read” section and is
not a place for method explanation, status history or a notation legend.

## Name the parent on every child

A nested element's definition row always has a `Parent` column after the base
definition columns. The cell uses the human-first `Name [ID]` form and links
the parent when it is local:

```markdown
| ID | Name | ArchiMate type | Description | Parent |
| --- | --- | --- | --- | --- |
| BPROC2.2.1 | Check completeness | Business Process | Confirms that the submitted order contains the required information. | [Validate an order](./2_level-2-processes.md#validate-an-order-bproc22) [BPROC2.2] |
| BPROC2.2.2 | Check payment | Business Process | Establishes whether payment can proceed. | [Validate an order](./2_level-2-processes.md#validate-an-order-bproc22) [BPROC2.2] |
```

- `Parent` is required when the ID has a hierarchical numeric suffix.
- The parent reference must match the ID obtained by removing the child's last
  numeric segment: Check payment [BPROC2.2.2] has parent Validate an order
  [BPROC2.2].
- The `Parent` cell is the canonical same-type Composition relationship. Do
  not repeat it in a generic relationship table.
- A Level 1 element has no parent and therefore needs no empty `Parent` cell.
- A file defining one child still names the parent in both its `Location` line
  and its definition.

The parent file may summarize or visually show its children, but it links to
their definitions rather than copying them.

## Keep other containment explicit

Only same-type refinement extends the parent's numeric ID. When one element
contains a different ArchiMate type, give each its normal independent ID and
declare the appropriate Composition, Aggregation or other relationship. The
child page's `Location` line may still name the containing context so the
reader knows where they are.

Examples include:

- Capability → Capability → Sub-capability;
- Business Process → Process → Sub-process;
- Data Object → Data Object part; and
- Application Component → nested Application Component.

The rule is the same in every case: a level file is explicit, a child names its
parent, and a page states its location without relying on the repository tree.
