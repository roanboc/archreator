# Standards alignment

_[← Repository README](../README.md) · [The method](./method.md)_

archreator coins names for a number of things that already have them. Sometimes
that is right — a coined name carrying the method's own emphasis is worth its
keep. Usually it is not: a private name is a tax on every reader who already
knows the standard one, and it hides the fact that a rule has decades of practice
behind it rather than being one repository's opinion.

This page is the inventory. Every coined term in the method, the established name
it corresponds to, and a verdict.

## The three verdicts

| Verdict | Means |
| ------- | ----- |
| **Cite** | The archreator name stays, because it carries emphasis the standard name does not. The standard is named alongside it, so a reader can place it |
| **Rename** | The archreator name misleads, or is unresolvable to a reader outside this repository. It goes |
| **Ours** | No established equivalent found. Kept without apology, and without pretending otherwise |

**Where a mapping is approximate, this page says so.** Claiming a correspondence
that does not hold would be a worse error than coining the name in the first place.

## Partitioning and scope

| archreator | Established | Verdict | Note |
| ---------- | ----------- | ------- | ---- |
| **Depth 1 / 2 / 3** — Application, Organization, Enterprise | TOGAF architecture partitioning by *subject matter* | Cite | Approximate. TOGAF's Enterprise / Segment / Capability levels partition the same way but cut at different places; Depth is a declared posture for one model, not a portfolio structure |
| **Tier** — Enterprise, Product, Implementation | TOGAF architecture partitioning by *level of detail* | Cite | Good match. "A tier may refine what the tier above exposed; it may never restate it" is that partitioning stated as an obligation |
| **The six layers** | ArchiMate layers, plus the Motivation extension | Cite | Already used by name. `3_information` is the divergence: ArchiMate has no Information layer, and data objects sit in Application. It corresponds to the data half of TOGAF Phase C, and is separated here because information ownership is a business question before it is a software one |
| **Levels 1–4** for processes and capabilities | APQC Process Classification Framework; the ISO 9001 process approach | Cite | Already half-cited in `process-and-capability-levels` |
| **The four bands** — Strategic, Operational, Support, Evaluation | ISO 9001:2015 clause structure — Leadership and Planning, Operation, Support, Performance evaluation | Cite | Close enough to name. The skill already says "the process map quality management has used for decades" without saying which |
| **SIPOC** | Six Sigma | — | Already standard, already named |

## Governance

| archreator | Established | Verdict | Note |
| ---------- | ----------- | ------- | ---- |
| **Gates 0–3** | Architecture board review; Stage-Gate (Cooper) | Cite | The named-gate-before-proceeding shape is Stage-Gate's; the subject matter is TOGAF's architecture governance |
| **The Approvals table** | TOGAF Architecture Contract | Cite | Approximate. A Contract is a fuller artifact; this is the record of who approved what, when, and against which document |
| **Scope document** | TOGAF Architecture Definition Document, narrowed to one initiative | Cite | Approximate |
| **Requester / Agent / Reviewer** | RACI, narrowed to three fixed roles | Cite | Approximate. What archreator adds is that the middle role is not assumed human |

## Documentation practice

| archreator | Established | Verdict | Note |
| ---------- | ----------- | ------- | ---- |
| **Grounding rule** — every element names the artifact realizing it, or is marked Pending | ISO/IEC/IEEE 42010 *correspondences* and *correspondence rules* | Cite | Strong match. A correspondence relates architecture-description elements to other things; a correspondence rule is what makes it checkable, and `check_model.py` enforces one |
| **`P3`** — "each fact in one place" | **DRY** (Hunt and Thomas); single source of truth | **Rename** | A bare `P3` is unresolvable outside the sibling repository, and in a downstream project it resolves to *that* project's third principle. Fixed in this change |
| **`P5`** — what a gap in the identifiers means | The never-reuse rule the same skill already states | **Rename** | Same defect, same fix |
| **"Consolidate before you enumerate" / "well-done less is more"** | KISS; YAGNI; parsimony in modeling | Cite | The archreator phrasing is an instruction where the standards are slogans, so it earns its keep |
| **"The document describes the subject, not its own construction"** | Living documentation (Martraire); present-tense technical writing | Cite | Approximate. The specific ban on version commentary inside a model document looks like archreator's own sharpening |
| **`doc-restate-current-state`** | No clean equivalent. Adjacent: documentation debt, model refactoring | **Ours** | Making "the model has drifted" its own gated initiative, with its own skill, is not a practice found under a standard name |

## AI actors

| archreator | Established | Verdict | Note |
| ---------- | ----------- | ------- | ---- |
| **Autonomy levels** — advisory, co-pilot, autonomous with checkpoint, fully autonomous | Human **in** / **on** / **out of** the loop; Sheridan and Verplank's levels of automation | Cite | Four levels refine three: advisory and co-pilot are both human-in-the-loop, differing on whether the AI acts before or after the human decides. Worth keeping, because that pair is the distinction practitioners most often collapse |
| **Decision rights, escalation path** | Human oversight, as framed by NIST AI RMF's human-AI configuration and the EU AI Act's Article 14 | Cite | Approximate — those are compliance frames, not modeling notation. These columns are the modeling form of the same question |
| **Modeling an AI as a Business Actor holding a role** | — | **Ours** | The README calls this the project's distinguishing bet, and no established EA practice found does it |

## Delivery practice

| archreator | Established | Verdict | Note |
| ---------- | ----------- | ------- | ---- |
| **`doc-decision-record`** | **ADR** — Architecture Decision Record (Nygard, 2011); MADR | Cite | The skill never says "ADR", which costs it every reader who already knows the pattern. Its sections already parallel MADR's |
| **`flow-story-sharding`** | Vertical slicing; INVEST (Wake) | Cite | Already cites BMAD-METHOD for the context-engineering half; INVEST names the sizing half |
| **`flow-engagement-retrospective`** | Retrospective; blameless post-mortem | Cite | |
| **`flow-stack-selection`** rationale capture | SPADE — Setting, People, Alternatives, Decide, Explain (Rajaram) | Cite | Considered and not adopted wholesale: this skill is a decision *aid* carrying defaults, not a decision *record*. SPADE belongs with `doc-decision-record` if anywhere |
| **The canvases** | Osterwalder — Business Model Canvas, Value Proposition Canvas | — | Already cited by name |

## What this change applied

Only the two **Rename** verdicts, because those are correctness rather than
vocabulary. `P3` and `P5` are element IDs from a model that does not ship with the
skills, so every downstream project inherited references it cannot resolve — and
worse, ones that resolve to the wrong thing wherever the project happens to have a
third principle of its own.

The **Cite** verdicts are deliberately not applied yet. Every skill body is being
rewritten as a schema-validated AIP Instruction, and editing prose now that is
about to be restructured is work done twice. Each citation lands with its skill's
conversion, checked against this page.
