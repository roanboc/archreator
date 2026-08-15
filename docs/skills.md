# The skills

_[← Repository README](../README.md) · [The method](./method.md)_

The method is fourteen skills. Claude Code picks each one up automatically
from its `description:` frontmatter — you don't invoke them by name in
normal use, they surface when their situation applies.

Skill folders carry a **role prefix** so the grouping is visible on a plain
folder listing. Nested folders would hide skills from the plugin loader, so
the grouping lives in the file name instead.

## Core — the process spine

Always in play. Together they define the method.

| Skill | Used for |
| ----- | -------- |
| [`core-project-bootstrap`](../.claude/skills/core-project-bootstrap/SKILL.md) | **First contact.** Turns a fresh copy into *this* project: names it, declares the modeling depth out loud, prunes what wasn't inherited, and hands off to discovery |
| [`core-architecture-first-change`](../.claude/skills/core-architecture-first-change/SKILL.md) | **The process itself.** Confirm the depth, locate the domain, assess the strategy (handing off to discovery when the strategy is new or shifting), walk the layers top-down, stop at the Requester's approval gates, write a scope document, implement, verify alignment, write the PR |
| [`core-architecture-doc-style`](../.claude/skills/core-architecture-doc-style/SKILL.md) | Numbering, element identifiers, ArchiMate-on-Mermaid notation, the human/AI/hybrid actor convention, the grounding rule, and the rule that a document describes its subject rather than its own construction |
| [`core-scope-doc`](../.claude/skills/core-scope-doc/SKILL.md) | The scope-document template and its rules — every layer gets a verdict, deliverables are concrete, out-of-scope matters as much as in-scope, the Approvals table records every gate |
| [`core-pr-description`](../.claude/skills/core-pr-description/SKILL.md) | Pull-request bodies that describe the whole branch, not just the latest commit, and follow the right template (default or bug fix) |

## Discover — question-driven

Reach for these when the model is unfilled or the change shifts what a
project *is*. They talk to the Requester.

| Skill | Used for |
| ----- | -------- |
| [`discover-operating-model`](../.claude/skills/discover-operating-model/SKILL.md) | **The company track.** When the subject is an organization rather than an app, question-driven discovery of a value proposition canvas per customer segment and a business model canvas per product, ending at the business-model gate (Gate 0) — then handing off to `discover-strategy`, which derives the architecture from the approved canvases instead of re-asking |
| [`discover-strategy`](../.claude/skills/discover-strategy/SKILL.md) | Question-driven discovery of the strategy layer and key business elements with the Requester — triggered when the strategy is still template placeholders or the change shifts it; a docs-only initiative ending at the strategy approval gate (Gate 1) |
| [`discover-process-and-capability-levels`](../.claude/skills/discover-process-and-capability-levels/SKILL.md) | The shape of an organization's two unbounded catalogues: the macro process map in four categories (strategic, operational, support, evaluation), what each level means and how its elements are described, and the rule that decides how far down to go — **breadth first, depth on pain**: levels 1 and 2 complete, level 3 only where a named pain justifies it |
| [`discover-domain-modeling`](../.claude/skills/discover-domain-modeling/SKILL.md) | **Depth 3.** Whether a business line deserves to be a domain at all (a five-part test), how to write its charter, how element IDs are namespaced across domains, and the federation rule — changing an exposed service needs the consuming domains' Requesters too |

## Doc — keeping the state honest

Reach for these when the record of *what is true today* or *why we chose
this* needs work.

| Skill | Used for |
| ----- | -------- |
| [`doc-restate-current-state`](../.claude/skills/doc-restate-current-state/SKILL.md) | Compacts the model so it describes today: shipped "Pending"s get their realizing artifact, superseded elements move to a Retired table, resolved open questions are archived. Merged scope documents are never rewritten — they are the record of what was approved when |
| [`doc-decision-record`](../.claude/skills/doc-decision-record/SKILL.md) | A short, durable rationale for a single consequential call that's smaller than an initiative — most often why an AI actor's autonomy level or decision rights were set the way they were |

## Flow — situational

Reach for these only when the situation calls for them.

| Skill | Used for |
| ----- | -------- |
| [`flow-story-sharding`](../.claude/skills/flow-story-sharding/SKILL.md) | When a scope document's work package is too large for one sitting, shard it into small, self-contained story files so an agent or person resuming later never has to re-derive the whole plan from the architecture tree |
| [`flow-stack-selection`](../.claude/skills/flow-stack-selection/SKILL.md) | A decision framework plus concrete defaults for choosing a stack on a small/solo app: static-only versus needs data/auth, with the reasoning for picking one over the other |
| [`flow-engagement-retrospective`](../.claude/skills/flow-engagement-retrospective/SKILL.md) | Run after an initiative or a client engagement closes: captures where the method failed to say what to do and what was done instead, as a pattern note with client facts left behind. It proposes method changes; it never makes them |
