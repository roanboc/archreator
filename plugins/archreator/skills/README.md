# Skills

ArChreator uses ten narrowly activated skills. Their typed structure makes the
method reviewable: procedures define workflow and judgement, document templates
define useful artifacts, and rulebooks preserve consistency without becoming
extra phases.

## Procedures

| Skill | Use it for |
| --- | --- |
| [`model-context`](./model-context/SKILL.md) | Establish, complete or refresh the smallest reliable current model |
| [`answer-context-question`](./answer-context-question/SKILL.md) | Ground an explanation, impact or decision question and choose the smallest useful response |
| [`plan-roadmap`](./plan-roadmap/SKILL.md) | Derive target outcomes, material gaps and a practical sequence from a reliable baseline |
| [`deliver-change`](./deliver-change/SKILL.md) | Trace, implement and verify a change while keeping canonical context true |
| [`federate-context`](./federate-context/SKILL.md) | Optionally connect independently owned models for a real cross-model need |

## Document templates

| Skill | Use it for |
| --- | --- |
| [`write-brief`](./write-brief/SKILL.md) | Create one temporary decision, impact, understanding or scope brief, with an optional requested PDF |
| [`record-decision`](./record-decision/SKILL.md) | Preserve the durable rationale for one accepted material choice |

## Rulebooks

| Skill | Use it for |
| --- | --- |
| [`document-style`](./document-style/SKILL.md) | Keep documentation plain, compact, current and linked without repeated guidance |
| [`architecture-document-style`](./architecture-document-style/SKILL.md) | Preserve model ownership, lazy standard structure, self-locating hierarchies, identifiers, ArchiMate metadata, relationships, grounding and visuals |
| [`process-and-capability-levels`](./process-and-capability-levels/SKILL.md) | Keep organizational process and capability models broad enough, deep only where justified, SIPOC-grounded and recognizable at each level |

The repository's Markdown is the architecture. `architecture/README.md` is its
front door; other canonical files exist only when they carry relevant facts.
Scopes, briefs and their PDFs belong under `.archreator/work/<run>/`; the
on-demand portal belongs under `.archreator/work/portal/`. Derived output is
disposable and never authoritative.

See [the skill format](../../../docs/skill-format.md) for the Agent Instruction
Protocol (AIP)-derived contract and [the process model](../../../docs/process/README.md)
for the supplier-input-process-output-customer (SIPOC) bindings.
