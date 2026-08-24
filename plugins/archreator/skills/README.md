# Skills

_[← Repository README](../../../README.md)_

The seventeen skills that are the archreator method. Your coding agent picks
them up automatically from their `description:` frontmatter — you don't
invoke them by name in normal use, they surface when their situation
applies.

**A skill is named for what it does.** A verb and an object —
`establish-project`, `write-scope-document` — is a skill you run; a noun
phrase — `architecture-document-style` — is one you consult. That is the rule
[`process-and-capability-levels`](./process-and-capability-levels/SKILL.md)
gives for naming a level-2 process, applied to the skills that realize them,
so a reader can tell from the name alone whether a skill is run or consulted.

**Three kinds, marked in the tables and in each skill's own title.** `⚙` a
procedure you run, `▤` a document you write, `※` a rulebook you consult. The
grouping below is by *process*, and two of the bands hold both procedures and
documents, so the kind is its own column rather than something the grouping
implies. [`docs/skill-format.md`](../../../docs/skill-format.md) specifies all
three.

**The order below is the order they are used in**, which is not the order the
processes of [`docs/process/`](../../../docs/process/README.md) are numbered in:
`BPROC5` joined the model last and runs second, and an assigned identifier is
never reallocated. The four rulebooks that realize no process come last.

This folder sits inside the **`archreator` plugin**, whose root is
`plugins/archreator/` — its manifest is written twice, as
[`plugin.json`](../plugin.json) for the hosts that read the plugin root and
[`.claude-plugin/plugin.json`](../.claude-plugin/plugin.json) for the one
that doesn't, and the marketplace that publishes it is
[`.claude-plugin/marketplace.json`](../../../.claude-plugin/marketplace.json)
at the repository root.

**A skill only links to files inside this folder.** Installing the plugin
copies its directory to a cache, so a relative link out of it resolves to
nothing for anyone who installed rather than cloned. Skills refer to a
consuming project's documents by naming the path in a code span —
`` `architecture/README.md` `` — which reads correctly on both paths.

**This page is the catalogue.** It is the only one — the rest of the
repository links here rather than restating it. The one deliberate copy is
the table in [`scaffold/AGENTS.md`](../scaffold/AGENTS.md), which
lands in a project that cannot link back to this repository at all; change
a row here and change it there in the same commit.
[`check_skills.py`](../scripts/check_skills.py) compares them.

## Establishing the model — `BPROC1`

Turning a subject nobody has modeled into one a change can be judged against.

| Skill | Kind | Reach for it when |
| ----- | ---- | ----------------- |
| [`establish-project`](./establish-project/SKILL.md) | ⚙ Procedure | A project from the template hasn't been set up yet — start here |
| [`discover-business-model`](./discover-business-model/SKILL.md) | ⚙ Procedure | The subject is an organization: canvases first (Gate 0), strategy derived from them |
| [`discover-strategy`](./discover-strategy/SKILL.md) | ⚙ Procedure | The strategy is unfilled or the change shifts it (Gate 1) |
| [`model-domains`](./model-domains/SKILL.md) | ⚙ Procedure | The organization is large enough to split into business lines, or a change crosses a domain boundary |
| [`discover-current-landscape`](./discover-current-landscape/SKILL.md) | ⚙ Procedure | The subject already exists and layers 2–5 are empty — sweep the estate into a described baseline |

## Planning the transition — `BPROC5`

Turning a described present into a destination and an order for reaching it.

| Skill | Kind | Reach for it when |
| ----- | ---- | ----------------- |
| [`plan-the-transition`](./plan-the-transition/SKILL.md) | ⚙ Procedure | The question is where the architecture should go and in what order — target plateaus, a gap register and a sequence |

The only skill whose output describes a future. Everything else in the corpus is
held to describing what is true now, which is a rule worth keeping precisely
because exactly one folder is exempt from it.

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
| [`restate-current-state`](./restate-current-state/SKILL.md) | ⚙ Procedure | The model has accumulated history — shipped "Pending"s, superseded elements, resolved questions — and no longer reads as a description of today |
| [`record-decision`](./record-decision/SKILL.md) | ▤ Document | One consequential call smaller than an initiative — most often an AI actor's autonomy level |

## Learning from the engagement — `BPROC4`

| Skill | Kind | Reach for it when |
| ----- | ---- | ----------------- |
| [`run-retrospective`](./run-retrospective/SKILL.md) | ▤ Document | An initiative or engagement just finished — capture what the method didn't cover before it evaporates |

## The rulebooks

Consulted rather than run, and realizing no process. `document-style` governs
every document in the repository; `architecture-document-style` adds what a
model needs and obeys it; `process-and-capability-levels` shapes a catalogue;
and `stack-selection` is a decision aid reached for inside `BPROC2.2`.

| Skill | Kind | Reach for it when |
| ----- | ---- | ----------------- |
| [`document-style`](./document-style/SKILL.md) | ※ Rulebook | Writing or editing any document at all — the language, what it may contain, and how it links |
| [`architecture-document-style`](./architecture-document-style/SKILL.md) | ※ Rulebook | Editing anything under `architecture/` — numbering, element IDs, tiers, ArchiMate-on-Mermaid, actors, the grounding rule |
| [`process-and-capability-levels`](./process-and-capability-levels/SKILL.md) | ※ Rulebook | An organization's processes or capabilities need shaping — the four macro categories, the levels, and how far down to go |
| [`stack-selection`](./stack-selection/SKILL.md) | ※ Rulebook | No technology stack chosen yet on a small application |
