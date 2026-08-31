# The skill format

_[← Repository README](../README.md) · [Contributing](../CONTRIBUTING.md)_

Every skill is one markdown file with YAML frontmatter, in a folder named for
it. One artifact serves both readers: an agent executes it, a person reviews
it, and neither reads a translation of the other's copy.

The structure is fixed so a reader knows where to look and
[`check_skills.py`](../plugins/archreator/scripts/check_skills.py) knows what
to enforce. What that script checks is this page, expressed as code.

## Frontmatter

| Field | Required | Holds |
| ----- | -------- | ----- |
| `name` | Yes | Matches the folder. Lowercase, hyphens, no leading or trailing hyphen |
| `description` | Yes | The activation summary — the only signal an agent has before opening the file. Keyword-rich, and **no unquoted colon**, which makes the frontmatter unparseable |
| `metadata.archreator.kind` | Yes | `gated-procedure`, `document-template` or `rulebook` |
| `metadata.archreator.realizes_process` | When one applies | The level-2 process IDs from [`docs/process/`](./process/README.md) |
| `metadata.archreator.gates` | Yes | The gates this skill stops at, or `none` |

**The description declares the kind, in its first two words.** `Procedure — run
this when…`, `Document — write one when…`, `Rulebook — consult when…`. The
description is the only thing loaded before a skill is chosen, so it is the only
place a kind marker can change what the agent reaches for; the folder name, the
metadata and the catalogue all say it too, and all three are invisible at that
moment. The title repeats it as a glyph — `# ⚙`, `# ▤`, `# ※` — for whoever
opens the file. `check_skills.py` checks both against `kind`.

**Values are strings.** Agent Skills types `metadata.*` as string to string, so
a list is one comma-separated string rather than a YAML sequence.

The description carries the keywords that make the skill findable; the body's
**When to use this** carries the checkable conditions. Writing the full
condition list in both is one fact in two places.

## Sections

Headings open with a glyph. The glyph says what kind of section it is, the
words are its identity — a reference names the words, and `check_skills.py`
strips the glyph before matching.

| Glyph | Section | Holds | `gated-procedure` | `document-template` | `rulebook` |
| ----- | ------- | ----- | :---------------: | :-----------------: | :--------: |
| `⊕` | When to use this | The observable conditions | required | required | required |
| `⊖` | When not to | Where a different skill serves | required | required | required |
| `⌖` | Where this sits | The process realized, the gates, the diagram | required | required | optional — to say it realizes none |
| `⚓` | Invariants | Rules holding at every step | required | — | — |
| `⚙` | Steps | The work, numbered | required | — | — |
| `▤` | Template | The document's shape | — | required | — |
| `※` | Rules | The rules themselves | — | required | required |
| `⇄` | Hands off to | Skills reached, and what returns | required | — | — |
| `✎` | Worked example | One concrete case | optional | optional | optional |
| `⚠` | Anti-patterns | Corrections | required | optional | optional |
| `☑` | Done when | Checkable completion | required | required | optional — the checklist for a catalogue its rules shaped |

## Inside a step

| Glyph | Marker | Holds |
| ----- | ------ | ----- |
| `⚖` | Judgement | The criteria to weigh, where the step is a decision rather than a mechanism |
| `←` | Needs | What the step consumes from an earlier one |
| `→` | Produces | What it writes, by path |
| `❖` | Gate | The approval that stops the step until a person acts. Every gate named in `metadata.archreator.gates` appears here, and `check_skills.py` checks it — matched on the glyph, because a skill routinely names gates it does not own to say they are `N/A` |

**Needs and Produces each get their own paragraph.** Consecutive lines are one
paragraph in markdown, and the two arrows render on one line if they share it.

## The diagram

Every **Where this sits** carries one. It summarises the whole document:
numbered steps in sequence, the decisions between them, the gates, and the
skills handed off to — so a reader can see the sub-process end to end before
reading a word of it.

Filled boxes are this skill's steps. Unfilled ones are skills it reaches.
Rose hexagons are gates. Glyph, shape and colour follow
[`architecture/README.md` § Notation conventions](../plugins/archreator/scaffold/architecture/README.md#notation-conventions),
which stays the single source for the palette.

## Cross-references

A skill names another skill's section as `` `skill-name` `` followed by `§`
and the heading. `check_skills.py` resolves both halves, which is what makes a
rename safe and a heading rename loud.

A skill links only to files inside `skills/`. Installing the plugin copies the
directory to a cache, so a relative link out of it resolves to nothing for
anyone who installed rather than cloned. A consuming project's documents are
named in a code span instead — `` `architecture/README.md` `` — which reads
correctly on both paths.

**A skill never cites an element ID from a specific model.** `P3` is that
model's third principle, and in a downstream project it resolves to something
else entirely. Name the principle.

## References

A skill may keep lookup content in `references/*.md` beside its `SKILL.md`.
**SKILL.md holds what is needed to decide; a reference holds what is needed to
look up.** The test is whether the content is read on every activation or only
on some: the rule that a diagram opens its section is read every time, the
table of which Mermaid shape a Plateau takes is read when somebody draws one.

The split exists because a rulebook is loaded by every skill that obeys it, so
its size is paid on almost every activation. `architecture-document-style` was
39,850 characters — roughly ten thousand tokens, on top of whatever the agent
was actually asked to do. Moving its glyph, shape, colour, prefix and canvas
tables into references cut it to 14,221 without deleting a rule.

Three rules keep it honest, and `check_skills.py` enforces the first two:

- **A citation names a heading, not a file.** `` `skill` § Heading `` resolves
  against the skill's SKILL.md *and* its references, so moving a section into a
  reference costs no edit anywhere else. That is what makes the split
  reversible and cheap.
- **Every reference is linked from its own SKILL.md**, in a table saying when
  to read it. A reference nothing links to is a file the agent never learns
  exists, which is worse than the section having stayed inline.
- **A reference is not a required section.** The sections a kind owes —
  § Sections — are found in SKILL.md or not at all. A skill cannot satisfy
  *Rules* by having a reference that happens to contain rules.

## Where this format came from

The section vocabulary is adapted from the
[Agent Instruction Protocol](https://github.com/zach-blumenfeld/aip) (AIP),
which models a skill as a schema-validated execution graph. Its lasting
contribution here is **naming the negative space**: a skill states when *not*
to use it, what it hands off to and gets back, the mistakes it steers away
from, and the rules holding across every step rather than at one of them.
Those four sections are AIP's, and three of them were where real defects had
been hiding.

Two more of its ideas carry through. A skill belongs to a **kind**, and the
kind decides what structure it owes — which is why `REQUIRED_SECTIONS` is
keyed by kind rather than applied uniformly. And its test for what to
mechanize is the right one: script a fixed rule over structured input, leave a
judgement over a loosely-specified one as prose for the agent to reason
through.

**The format is markdown rather than AIP's fenced YAML, and that is a
deliberate divergence.** AIP's value comes from steps backed by scripts and
wired by typed edges; these skills have neither — they are judgement
procedures under human approval, and the one conversion measured carried zero
script-backed steps and zero graph edges while growing 59% in lines. Markdown
also keeps one artifact for both readers, and keeps the diagrams, which a YAML
body cannot hold.

The parts of AIP worth having did not need its file format. What replaced the
JSON Schemas is the section table above, and `check_skills.py` enforcing it.
