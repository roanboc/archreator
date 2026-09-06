# Skills

_[← Repository README](../../../README.md)_

The eighteen skills that are the archreator method, and the only catalogue of
them. Your coding agent picks them up from their `description:` frontmatter —
they surface when their situation applies rather than being invoked by name.

**A skill is named for what it does.** A verb and an object —
`establish-project`, `write-scope-document` — is a skill you run; a noun
phrase — `architecture-document-style` — is one you consult.

**Three kinds, marked in the tables and in each skill's own title.** `⚙` a
procedure you run, `▤` a document you write, `※` a rulebook you consult.
[`docs/skill-format.md`](../../../docs/skill-format.md) specifies all three.

**The order below is the order they are used in**, not the order the processes
of [`docs/process/`](../../../docs/process/README.md) are numbered in. The four
rulebooks that realize no process come last.

This folder sits inside the **`archreator` plugin**, whose root is
`plugins/archreator/` — its manifest is written twice, as
[`plugin.json`](../plugin.json) and
[`.claude-plugin/plugin.json`](../.claude-plugin/plugin.json), and the
marketplace that publishes it is
[`.claude-plugin/marketplace.json`](../../../.claude-plugin/marketplace.json)
at the repository root.

**A skill only links to files inside this folder**, and names a consuming
project's documents in a code span — `` `architecture/README.md` `` — because
installing the plugin copies this directory to a cache.
[`check_skills.py`](../scripts/check_skills.py) holds the catalogue below
against the skill directories that exist.

## Establishing the model — `BPROC1`

Turning a subject nobody has modeled into one a change can be judged against.

| Skill | Kind | Reach for it when |
| ----- | ---- | ----------------- |
| [`establish-project`](./establish-project/SKILL.md) | ⚙ Procedure | A project from the template hasn't been set up yet — start here |
| [`discover-business-model`](./discover-business-model/SKILL.md) | ⚙ Procedure | The subject is an organization: canvases first (Direction), strategy derived from them |
| [`discover-strategy`](./discover-strategy/SKILL.md) | ⚙ Procedure | The strategy is unfilled or the change shifts it (Direction) |
| [`model-domains`](./model-domains/SKILL.md) | ⚙ Procedure | The organization is large enough to split into business lines, or a change crosses a domain boundary |
| [`discover-current-landscape`](./discover-current-landscape/SKILL.md) | ⚙ Procedure | The subject already exists and layers 2–5 are empty — sweep the estate into a described baseline |

## Planning the transition — `BPROC5`

Turning a described present into a destination and an order for reaching it.

| Skill | Kind | Reach for it when |
| ----- | ---- | ----------------- |
| [`plan-the-transition`](./plan-the-transition/SKILL.md) | ⚙ Procedure | The question is where the architecture should go and in what order — target plateaus, a gap register and a sequence |

The only skill whose output describes a future; everything else in the corpus
describes what is true now.

## Delivering a change — `BPROC2`

Turning a requirement into merged code whose architecture documents are still true.

| Skill | Kind | Reach for it when |
| ----- | ---- | ----------------- |
| [`align-change-through-layers`](./align-change-through-layers/SKILL.md) | ⚙ Procedure | Any requirement change. **The spine** — defines the gates and the order |
| [`write-scope-document`](./write-scope-document/SKILL.md) | ▤ Document | Writing the initiative's scope document; its Approvals table is the durable record of the gates |
| [`shard-stories`](./shard-stories/SKILL.md) | ▤ Document | A work package is too large to finish in one sitting |
| [`write-pr-description`](./write-pr-description/SKILL.md) | ⚙ Procedure | Opening or updating a pull request — the body covers the whole branch, not the latest commit |

## Keeping the model true — `BPROC3`

Turning a model that has drifted back into a description of today.

| Skill | Kind | Reach for it when |
| ----- | ---- | ----------------- |
| [`restate-current-state`](./restate-current-state/SKILL.md) | ⚙ Procedure | The model has accumulated history — shipped "Pending"s, superseded elements — and no longer reads as a description of today |
| [`record-decision`](./record-decision/SKILL.md) | ▤ Document | One consequential call smaller than an initiative — most often an AI actor's autonomy level |
| [`answer-architecture-question`](./answer-architecture-question/SKILL.md) | ⚙ Procedure | A reader wants a focused, disposable brief about one element, domain, concern, impact or decision |

## Learning from the engagement — `BPROC4`

| Skill | Kind | Reach for it when |
| ----- | ---- | ----------------- |
| [`run-retrospective`](./run-retrospective/SKILL.md) | ▤ Document | An initiative or engagement just finished — capture what the method didn't cover before it evaporates |

## The rulebooks

Consulted rather than run, and realizing no process.

| Skill | Kind | Reach for it when |
| ----- | ---- | ----------------- |
| [`document-style`](./document-style/SKILL.md) | ※ Rulebook | Writing or editing any document at all — the language, what it may contain, and how it links |
| [`architecture-document-style`](./architecture-document-style/SKILL.md) | ※ Rulebook | Editing anything under `architecture/` — numbering, element IDs, tiers, ArchiMate-on-Mermaid, actors, the grounding rule |
| [`process-and-capability-levels`](./process-and-capability-levels/SKILL.md) | ※ Rulebook | An organization's processes or capabilities need shaping — the four macro categories, the levels, and how far down to go |
| [`stack-selection`](./stack-selection/SKILL.md) | ※ Rulebook | No technology stack chosen yet on a small application |
