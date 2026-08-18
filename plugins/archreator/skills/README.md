# Skills

_[← Repository README](../../../README.md)_

The fourteen skills that are the archreator method. Claude Code picks them
up automatically from their `description:` frontmatter — you don't invoke
them by name in normal use, they surface when their situation applies.

Skill folders carry a **role prefix** so the grouping is visible on a plain
folder listing: nested folders would hide skills from the plugin loader, so
the grouping lives in the file name instead.

This folder sits inside the **`archreator` plugin**, whose root is
`plugins/archreator/` — its manifest is
[`.claude-plugin/plugin.json`](../.claude-plugin/plugin.json),
and the marketplace that publishes it is
[`.claude-plugin/marketplace.json`](../../../.claude-plugin/marketplace.json)
at the repository root.

**A skill only links to files inside this folder.** Installing the plugin
copies its directory to a cache, so a relative link out of it resolves to
nothing for anyone who installed rather than cloned. Skills refer to a
consuming project's documents by naming the path in a code span —
`` `architecture/README.md` `` — which reads correctly on both paths.

**This page is the catalogue.** It is the only one — the rest of the
repository links here rather than restating it. The one deliberate copy is
the table in [`templates/CLAUDE.md`](../templates/CLAUDE.md), which
lands in a project that cannot link back to this repository at all; change
a row here and change it there in the same commit.

## Core — the process spine

Always in play. Together they define the method.

| Skill | Reach for it when |
| ----- | ----------------- |
| [`core-project-bootstrap`](./core-project-bootstrap/SKILL.md) | A project from the template hasn't been set up yet — start here |
| [`core-architecture-first-change`](./core-architecture-first-change/SKILL.md) | Any requirement change. **The spine** — defines the gates and the order |
| [`core-architecture-doc-style`](./core-architecture-doc-style/SKILL.md) | Editing anything under `architecture/` — numbering, element IDs, ArchiMate-on-Mermaid, the grounding rule — and writing any other document in the repository, for what it may contain |
| [`core-scope-doc`](./core-scope-doc/SKILL.md) | Writing the initiative's scope document; its Approvals table is the durable record of the gates |
| [`core-pr-description`](./core-pr-description/SKILL.md) | Opening or updating a pull request — the body covers the whole branch, not the latest commit |

## Discover — question-driven

Reach for these when the model is unfilled or the change shifts what a
project *is*. They talk to the Requester.

| Skill | Reach for it when |
| ----- | ----------------- |
| [`discover-operating-model`](./discover-operating-model/SKILL.md) | The subject is an organization: canvases first (Gate 0), strategy derived from them |
| [`discover-strategy`](./discover-strategy/SKILL.md) | The strategy is unfilled or the change shifts it (Gate 1) |
| [`discover-process-and-capability-levels`](./discover-process-and-capability-levels/SKILL.md) | An organization's processes or capabilities need shaping — the four macro categories, the levels, and how far down to go |
| [`discover-domain-modeling`](./discover-domain-modeling/SKILL.md) | The organization is large enough to split into business lines, or a change crosses a domain boundary |

## Doc — keeping the state honest

Reach for these when the record of *what is true today* or *why we chose
this* needs work.

| Skill | Reach for it when |
| ----- | ----------------- |
| [`doc-restate-current-state`](./doc-restate-current-state/SKILL.md) | The model has accumulated history — shipped "Pending"s, superseded elements, resolved questions — and no longer reads as a description of today |
| [`doc-decision-record`](./doc-decision-record/SKILL.md) | One consequential call smaller than an initiative — most often an AI actor's autonomy level |

## Flow — situational

Reach for these only when the situation calls for them.

| Skill | Reach for it when |
| ----- | ----------------- |
| [`flow-story-sharding`](./flow-story-sharding/SKILL.md) | A work package is too large to finish in one sitting |
| [`flow-stack-selection`](./flow-stack-selection/SKILL.md) | No technology stack chosen yet on a small application |
| [`flow-engagement-retrospective`](./flow-engagement-retrospective/SKILL.md) | An initiative or engagement just finished — capture what the method didn't cover before it evaporates |
