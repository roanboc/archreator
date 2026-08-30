---
name: document-style
description: Rulebook — consult when writing or editing repository documentation so it stays plain, current, compact and navigable. Architecture documents obey this rulebook and architecture-document-style adds their modeling contract.
metadata:
  archreator:
    kind: rulebook
    gates: none
---

# ※ Document style

Write one document that means the same thing to the person who knows the
subject, the person who arrives later and the agent acting on it. Brevity is
useful only after ambiguity and duplication have been removed.

## ⊕ When to use this

- Creating or editing a README, guide, process page, decision, architecture
  document or other maintained Markdown.
- Simplifying documentation whose history, repeated guidance or terminology
  obscures its subject.
- Reviewing whether several statements or elements are genuinely distinct.

Apply `architecture-document-style` as well for canonical files under
`architecture/`.

## ⊖ When not to

- Source-code formatting, API syntax or generated output governed by another
  format.
- A temporary brief whose structure is defined by its document-template skill;
  use these language and duplication rules without turning the brief into
  canonical documentation.
- Preserving an original source exactly as received. Link it as evidence
  rather than rewriting it as though it were the model.

## ⌖ Where this sits

This rulebook realizes no process. Procedures and document templates consult
it while producing human-readable artifacts. It sets the common writing rules;
`architecture-document-style` adds identifiers, ownership, relationships and
model structure.

## ※ Rules

### Use language as the interface

- Use the project's documentation language consistently. Keep paths in plain
  ASCII where a portable filename is needed.
- Lead with the words the subject's people use. Introduce architecture or
  technical vocabulary only when it adds precision.
- Expand an unavoidable acronym or specialist term on first use in each
  independently read document. A deep-linked reader should not need another
  page merely to decode a sentence.
- A catalogue row **defines** an element and stays ID-first so definitions sort
  by stable identity: `ID | Name | …`. Every **reference** outside that row is
  human-first with the ID last, such as `Order handling [BSVC1]`. A bare ID is
  valid only in the defining row's `ID` cell; prose, relationship endpoints,
  diagrams, briefs and other content never use it alone.
- Machine-only metadata and explicit query arguments may use a bare ID. When
  that identity is rendered for a reader, restore the human-first `Name [ID]`
  form.
- Use active, concrete sentences. State who owns or does something when the
  identity matters.

### Consolidate before enumerating

Fewer, well-defined ideas are easier to validate and connect than many narrow
ones.

- If two entries differ only in wording or degree, keep one and express the
  variation as an attribute, measure or segment-specific value.
- When a list becomes hard to hold in one view, first test which entries are
  the same thing seen from different positions. Split the document only after
  consolidating the subject.
- Present a reasoned recommendation rather than handing the reader a long menu
  of overlapping choices.
- Keep distinct things distinct when they have different ownership, outcomes,
  contracts or lifecycles. Simplicity is not loss of meaning.

### Describe the subject and current truth

A maintained document says what is true, why it matters and how it connects.
It does not narrate how the document was drafted.

- Keep interpretation that helps the reader understand the subject.
- Remove drafting history, consolidation counts, revision commentary and
  explanations of why a heading or table was chosen. Git and temporary work
  artifacts hold how the document changed.
- Do not add “as of initiative” commentary or an empty section that says there
  is nothing to report.
- Put durable rationale in a decision record only when a future reader will
  reasonably ask why an alternative was rejected.
- State uncertainty beside the affected fact as **Assumption**, **Gap** or
  **Inconsistent evidence**. Do not hide it in a generic notes section or make
  the whole document sound provisional when only one fact is uncertain.
- Replace obsolete current-state statements and remove resolved uncertainty.
  Preserve history only in artifacts whose purpose is historical.

### Give the document only the structure it needs

- Start with the subject and its importance. Use headings that help a reader
  answer a real question.
- Use a table for facts that are meaningfully comparable, a visual for
  relationships, flow or sequence, and prose for explanation and rationale.
- Do not repeat a generic “How to read this document,” notation legend or
  method explanation on every page. Add local guidance only when the document
  would otherwise be ambiguous.
- Remove unused template sections. Absence is clearer than “None.”
- Keep navigation close to the title when a reader can arrive by a deep link.

### Keep one fact in one home

- Define a fact once and link to it elsewhere. A summary may orient the reader
  but must not become a second independently maintained definition.
- Use relative links to a specific file and retain an anchor when pointing to
  a section. Link text should name the subject, not expose a raw path.
- A cross-reference to a modeled element uses `Human name [ID]`, with the
  stable anchor secondary. When several are referenced, make each
  independently readable.
- When moving or renaming a file, search the repository and repair its links
  in the same change.
- A skill links only to resources shipped inside the plugin's `skills/`
  directory. Name consuming-project paths in code spans rather than creating a
  link that will break after plugin installation.

## ⚠ Anti-patterns

- Architecture vocabulary replacing the organization's own words without
  adding precision.
- A bare acronym, identifier or path that forces a second lookup, or an
  ID-first reference outside a catalogue definition that makes a person decode
  the machine anchor before the name.
- Exhaustive catalogues whose entries overlap.
- A document explaining its own construction or carrying its changelog.
- Repeated legends, “How to read” sections or empty headings copied from a
  template.
- Uncertainty separated from the claim it qualifies.
- The same table or definition maintained in several places.

## ☑ Done when

- A reader can identify the subject, current truth and material uncertainty
  without knowing the method.
- Terms and element references are understandable where encountered:
  catalogue definitions are ID-first and references are human-first.
- Repetition has been replaced with links, and every link resolves.
- Every remaining section and visual earns its place.
