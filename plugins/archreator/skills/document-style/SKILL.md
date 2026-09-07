---
name: document-style
description: Rulebook — consult before writing or editing any Markdown document in this repository.
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
(see the project's `AGENTS.md`). Whatever language is chosen, **folder and
file names stay plain ASCII** (no accents, no non-Latin punctuation) even
if the prose inside is written in a language that uses them — this avoids
cross-platform path and URL-encoding issues. If ArchiMate stereotypes are
translated, keep a correspondence table to the standard English element
names near the top of `architecture/README.md`.

The method's own vocabulary translates the same way. The two gate names may
be written in the project's language — «Dirección», «Entendimiento» — with the
English originals in the same correspondence table. The validators read the
status glyph, never the words beside it.

#### Write it out

Spell things out:

- **Expand every acronym on its first use in each document**, then use the
  short form freely. Per document, not per project: a deep link is an
  arrival.
- **Element IDs are acronyms too.** First mention in a document names the
  element the ordinary way — **business and solution designers [CS1]** — and
  expands the prefix beside it (`CS` = Customer Segment), or sits in a table
  whose adjacent column gives the name. Never a bare `CS1` in prose the first
  time.
- **A cross-reference shows identity and meaning.** Write the element's name
  with the ID riding along — `[Business and solution designers [CS1]](...)` —
  rather than linking a bare ID. When one field references several elements,
  put one linked `Name [ID]` on each line. A portal tooltip may repeat the
  name as a convenience, but never carries information absent from the
  Markdown.
- **An abbreviation worth using is worth defining.** If the organization has
  its own jargon, it belongs in the glossary in
  `2_business/5_domain-context-and-rules.md`, not only in the head of
  whoever wrote the document.
- **Prefer the full word where it costs nothing.** "Customer segment" reads
  better than "CS" in a sentence; the short form earns its place in tables,
  diagrams, and cross-references where space is genuinely tight.

#### The name leads, and the identifier rides along

`CAP3` is a key, not a name. In a sentence, a heading, a diagram label or a
brief, write the name and let the identifier ride along — `Name [ID]`:

> …which is why **the Supervised build service [BSVC3]** was split from…

Not "which is why `BSVC3` was split from".

**Two places keep the identifier first.** A catalogue's own definition row
opens with the ID — and the bolded lead-in `**G1 — Legible guidance.**` is the
same defining shape in prose — because the leading identifier exposes the
sequence and the hierarchy at a glance. And a **relationship column** holds
bare identifiers and nothing else, because a parser reads it before a person
does and a name written there silently deletes the relationship —
`architecture-document-style` § Relationships are declared, never only drawn.

Everywhere else the name leads.

#### Consolidate before you enumerate

**Fewer, better-defined elements beat many narrow ones.** Ten well-named
elements with clear relationships are more useful than thirty precise ones
nobody can hold in their head. Three rules follow:

- **If two elements differ only in degree, they are one element.** The same
  pain felt by two customer segments at different severity is one pain with
  a severity column — not two pains. The same goes for a capability used
  more heavily by one domain, or a rule enforced more strictly in one place.
- **Merge before you split.** When a list grows past what fits on one screen,
  the first question is which entries are the same thing seen from two
  angles, not how to organise the list.
- **This applies to what an agent proposes, not only to what it writes.**
  Offer a consolidated recommendation, not an exhaustive menu. A Requester
  reading five overlapping options has been handed the analysis the agent was
  supposed to do.

### What the document contains: the subject, not its own construction

**Every sentence in a document is either about its subject or about the act of
writing it. The first belongs in the document; the second belongs in the scope
document.**

**This governs every document in the repository, not only those under
`architecture/`** — a README, a page under `docs/`, a process model, a
contributing guide. A layer document is the common case the examples below are
drawn from; a reference page narrating which of its entries were added last
breaks the same rule.

| Stays — it is about the subject | Goes — it is about making the document |
| ------------------------------- | -------------------------------------- |
| "This diagram is the risk, drawn" | "The source material lists seven industries and eight customer types" |
| "`BPROC1` uses no capability — Reach is the only stage the organization does nothing skilful in" | "Writing them as separate elements would have produced an unreadable catalogue" |
| "`VAL1` is the only value every stakeholder receives" | "Twelve pains were consolidated into five" |
| "The areas have no realizing artifact, and that is correct rather than a gap" | "Identifiers were renumbered once, here, before the gate" |

Interpretation of the subject stays; what goes is the document narrating its
own drafting.

**The removed material moves to where it was already required.** A
consolidation — what was merged into what, and how many elements each
catalogue ended up with — is a modeling decision the Requester approves at a
gate, so it belongs in the scope document and the gate presentation
(`discover-business-model` § 5 — Present for approval already asks for it
there).

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
hold why.

**A rebuilt document carries none of the rebuild.** When a model is rebuilt
or crosses a method version, the new documents never mention the corpus they
replaced, the version they crossed, or the ref where the old text is
preserved — the initiative's scope document says all of that once. A status
line names the mark and the gate that covers the document, nothing else.

#### Notes that survive go to the end

A note worth keeping that belongs to no single section goes in a final
**Additional notes** section, after the last element group — never woven
between a diagram and the table it explains.

### Links

- Always relative, always to a specific file (`../2_business/README.md`,
  not `../2_business/`), keeping `#anchors` when pointing at a section.
- Human-readable link text (`[solution design](./…)`), not raw paths.
- Each fact lives in exactly one document; everything else links to it. If
  you are about to restate a table or diagram, link instead.
- When renaming or moving a doc, grep the whole repo for the old path and
  fix every reference in the same change.
- **Skill files are the exception: they link only within the plugin's own
  `skills/` directory.** A skill points at a consuming project's documents by
  naming the path in a code span — `` `architecture/README.md` § Modeling
  depth `` — never as a relative link. Installing a plugin copies its
  directory to a cache, so a link reaching outside it resolves to nothing.

## ⚠ Anti-patterns

- A document narrating its own construction — what the source material held,
  what was consolidated into what, why identifiers moved.
- "As of initiative N", or any other version commentary. Git holds how a
  document got here; the scope documents hold why.
- A rebuilt document narrating the rebuild — what the old corpus held, where
  it is preserved, which method version was crossed.
- An empty section written to say a section is empty.
- Restating a table or diagram that another document owns, rather than
  linking it.
- A skill linking outside the plugin's own `skills/` directory.
- A bare identifier in prose — `CAP3` where **the name [CAP3]** should lead
  (§ The name leads, and the identifier rides along).

