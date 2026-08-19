---
name: document-style
description: Rulebook — consult when writing or editing any document in this repository, whatever it is about — a README, a page under docs/, a contributing guide, a layer document. Covers the documentation language and how acronyms and identifiers are written out, what a document may contain (its subject rather than its own construction, and no version commentary), where a surviving note goes, and the link conventions. Architecture documents obey these too, and architecture-document-style adds the rest.
metadata:
  archreator:
    kind: rulebook
    gates: none
---

# ※ Document style

What every document in this repository obeys, whatever it is about. Three
rules: the language it is written in, what it may contain, and how it links.

`architecture-document-style` adds everything specific to a model — element
identifiers, notation, tiers, actors — and obeys these three as well.

## ⊕ When to use this

| The situation | What it looks like |
| ------------- | ------------------ |
| Writing any document | A README, a page under `docs/`, a contributing guide, a skill |
| Editing a model document | These rules apply there too; `architecture-document-style` adds the rest |
| Deciding what a document may hold | A sentence is about the subject, or about the act of writing it |

## ⊖ When not to

| The situation | Use instead |
| ------------- | ----------- |
| The question is about identifiers, notation, tiers or actors | `architecture-document-style` |
| The question is how far to decompose a catalogue | `process-and-capability-levels` |

## ⌖ Where this sits

**Realizes no process.** It is the rule every document in the repository
complies with, and the one rulebook that is not about architecture at all.

## ※ Rules

### Language

Pick one documentation language for the project and use it consistently
across `architecture/`, `architecture/scope/`, commit messages, and code identifiers
(see the project's `CLAUDE.md`). Whatever language is chosen, **folder and
file names stay plain ASCII** (no accents, no non-Latin punctuation) even
if the prose inside is written in a language that uses them — this avoids
cross-platform path and URL-encoding issues. If ArchiMate stereotypes are
translated, keep a correspondence table to the standard English element
names near the top of `architecture/README.md`.

#### Write it out

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

#### Consolidate before you enumerate

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

### What the document contains: the subject, not its own construction

**Every sentence in a document is either about its subject or about the act of
writing it. The first belongs in the document; the second belongs in the scope
document.**

**This governs every document in the repository, not only those under
`architecture/`** — a README, a page under `docs/`, a process model, a
contributing guide. A layer document is the common case and the examples below
are drawn from one, but nothing in the rule is specific to architecture. A
reference page that narrates which of its entries were added last is doing the
same thing as a layer document narrating its own drafting.

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
(`discover-business-model` § 5 — Present for approval already asks for it
there). Writing it in
the layer document as well is a second copy of a fact, which is DRY broken.

#### Two carve-outs

- **Anything awaiting validation stays inline.** A "Pending — future
  initiative" marker, an adopted interpretation, a figure nobody has confirmed
  — these sit in the body, where the reviewer who can correct them will see
  them. Moving them to the end is how they stop being corrected.
- **Provenance attaches to elements; history attaches to documents.** A table
  cell naming the initiative that delivered an element is a trace worth
  keeping. A sentence saying the *document* is new as of that initiative is the
  document talking about itself. The first is a reference, the second is a
  narrative.

#### No version commentary

No "as of initiative N", no note about what an unapproved proposal would
change, no record of a draft's revisions, no "Retired — None". The document
states what is true now; git holds how it got there and the scope documents
hold why. A model carrying its own changelog gives a reader two accounts to
reconcile and no way to tell which is current.

#### Notes that survive go to the end

A note worth keeping that belongs to no single section goes in a final
**Additional notes** section, after the last element group — not woven between
a diagram and the table it explains, where it displaces what the reader came
for.

### Links

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

## ⚠ Anti-patterns

- A document narrating its own construction — what the source material held,
  what was consolidated into what, why identifiers moved.
- "As of initiative N", or any other version commentary. Git holds how a
  document got here; the scope documents hold why.
- An empty section written to say a section is empty.
- Restating a table or diagram that another document owns, rather than
  linking it.
- A skill linking outside the plugin's own `skills/` directory.
