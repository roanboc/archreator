# Standards alignment

_[← Repository README](../README.md) · [The method](./method.md)_

Most of what archreator asks for has an established name. This page holds the
mapping: for every term the method coins, the standard it corresponds to, and
whether the coined name or the standard one is the one to use.

A private name is a tax on every reader who already knows the standard one, and
it hides that a rule has decades of practice behind it rather than being one
repository's opinion. The mapping exists so that neither cost is paid silently.

## How to read this page

Each row carries one of three verdicts.

| Verdict | Means |
| ------- | ----- |
| **Cite** | The archreator name is the one to use — it carries emphasis the standard name does not. The standard is named beside it so a reader can place it |
| **Adopted** | The standard's name is the one to use. The method says it directly |
| **Ours** | No established equivalent. The method is on its own here, and says so rather than implying borrowed rigour |

Mappings that hold only loosely are marked **approximate** in the Note column.
A correspondence claimed where none holds would be a worse error than coining
the name.

**A skill names its standard only where the name helps the reader of that
skill.** `record-decision` says ADR, because a reader who knows the pattern
recognises it instantly and one who does not can go and read about it.
`stack-selection` does not say "TOGAF architecture partitioning by level of
detail", because that would cost a line and buy nothing at the point of use.

So most of the correspondences below live **here and only here**. This page is
where the mapping is kept; the skills carry a standard's name where it earns
its space, and the table says which those are.

## Partitioning and scope

| archreator | Established | Verdict | Named in the skill | Note |
| ---------- | ----------- | ------- | ----------------- | ---- |
| **Depth 1 / 2 / 3** — Application, Organization, Enterprise | TOGAF architecture partitioning by *subject matter* | Cite | — | Approximate. TOGAF's Enterprise / Segment / Capability levels partition the same way but cut at different places; Depth is a declared posture for one model, not a portfolio structure |
| **Tier** — Enterprise, Product, Implementation | TOGAF architecture partitioning by *level of detail* | Cite | — | Good match. "A tier may refine what the tier above exposed; it may never restate it" is that partitioning stated as an obligation |
| **The six layers** | ArchiMate layers, plus the Motivation extension | Cite | — | `3_information` is the divergence: ArchiMate has no Information layer, and data objects sit in Application. It corresponds to the data half of TOGAF Phase C, and stands alone here because information ownership is a business question before it is a software one |
| **Levels 1–4** for processes and capabilities | APQC Process Classification Framework; the ISO 9001 process approach | Cite | — | |
| **The four bands** — Strategic, Operational, Support, Evaluation | ISO 9001:2015 clause structure — Leadership and Planning, Operation, Support, Performance evaluation | Cite | — | |
| **SIPOC** | Six Sigma | Adopted | yes | |

## Baseline, target and transition

| archreator | Established | Verdict | Named in the skill | Note |
| ---------- | ----------- | ------- | ----------------- | ---- |
| **Landscape sweep** — filling layers 2–5 from the estate rather than from a requirement | TOGAF Phases B, C and D, **Baseline Architecture** half | Cite | — | Good match on subject. TOGAF interleaves baseline and target in the same phase; archreator separates them into two processes, because only one of them can be validated against something that exists |
| **Coverage declaration** — what the sweep deliberately did not reach | TOGAF's *scope* and *level of detail* decisions in the Statement of Architecture Work | Cite | — | Approximate. The archreator form is an obligation on the model rather than a project artifact — it lives in the layer README, where a reader meets it, not in a document about the engagement |
| **Plateau** | ArchiMate **Plateau** (Implementation & Migration) | Adopted | yes | The standard name and the standard meaning: a relatively stable state the architecture passes through |
| **Gap** | ArchiMate **Gap**; TOGAF **gap analysis** | Adopted | yes | Also standard. What archreator adds is that a gap must name the baseline element it is measured from, which makes a gap register checkable rather than a wish list |
| **The sequence** — initiatives ordered by dependency, without dates | TOGAF Phase E and F — Opportunities and Solutions, Migration Planning; the **Architecture Roadmap** | Cite | — | Approximate. TOGAF's roadmap carries work packages and timing; this one carries order and preconditions, and refuses dates on the grounds that a stale date stops a document being read |
| **`architecture/6_transition/` as the only folder describing a future** | Adjacent only: TOGAF's Transition Architectures | **Ours** | — | The partition is archreator's. Confining intent to one folder so that every other document can be read as present tense without qualification has no standard equivalent, and it exists to serve the agent that reads the model, not the architect who writes it |
| **A roadmap approves direction, not work** | Adjacent only: the distinction between an approved roadmap and an approved project in most stage-gate governance | **Ours** | yes | Stated as a rule rather than left to practice, because an agent handed a roadmap will otherwise treat it as a backlog it has been told to build |

## Provenance and standing

| archreator | Established | Verdict | Named in the skill | Note |
| ---------- | ----------- | ------- | ----------------- | ---- |
| **Document status** — `○` not started, `◐` draft catalogue, `●` validated at a gate | Adjacent only: document control and revision status in records management; ISO/IEC/IEEE 42010's *architecture description* has no equivalent | **Ours** | yes | The distinction being marked is not maturity but *authority*: whether a person with the standing to say so has agreed the document is true. No architecture standard marks that on the document itself, and every one of them assumes a reader who knows which is which |
| **Draft catalogue** — elements identified with notes, not an architecture draft | Adjacent only: an inventory, a discovery log, TOGAF's Baseline Architecture *before* it is validated | **Ours** | yes | The naming is the whole contribution. "Draft architecture" invites a reader to critique the structure; "draft catalogue" tells them the structure is not the claim — the existence of the items is, and it has not been checked |
| **`Source` and `Notes` columns, and emptying `Notes` at the gate** | Adjacent only: issue logs, RAID logs | **Ours** | yes | The rule that a note cannot survive its gate is the part worth having: it forces every open thread to become a fact, a logged question, or an admission that nobody cared |
| **`architecture/reference/`** — provided source material, dated and indexed | TOGAF **Architecture Repository**, loosely; ISO/IEC/IEEE 42010 *architecture rationale* | Cite | yes | Approximate. TOGAF's repository is a governed store of reference models and standards; this is narrower and more mundane — the actual documents a client handed over, kept so a claim can be taken back to them |
| **Date precedence** — the meeting, else the sharing, else the filing | Adjacent only: archival description practice, which distinguishes creation from accession date | Cite | yes | The archival distinction is the same one, and the ordering here is the practical form of it: prefer the date the content is *about* over the date it arrived |

## Governance

| archreator | Established | Verdict | Named in the skill | Note |
| ---------- | ----------- | ------- | ----------------- | ---- |
| **Gates 0–3** | Architecture board review; Stage-Gate (Cooper) | Cite | — | The named-gate-before-proceeding shape is Stage-Gate's; the subject matter is TOGAF's architecture governance |
| **The Approvals table** | TOGAF Architecture Contract | Cite | — | Approximate. A Contract is a fuller artifact; this is the record of who approved what, when, and against which document |
| **Scope document** | TOGAF Architecture Definition Document, narrowed to one initiative | Cite | — | Approximate |
| **Requester / Agent / Reviewer** | RACI, narrowed to three fixed roles | Cite | — | Approximate. What archreator adds is that the middle role is not assumed human |

## Documentation practice

| archreator | Established | Verdict | Named in the skill | Note |
| ---------- | ----------- | ------- | ----------------- | ---- |
| **Grounding rule** — every element names the artifact realizing it, or is marked Pending | ISO/IEC/IEEE 42010 *correspondences* and *correspondence rules* | Cite | — | Strong match. A correspondence relates architecture-description elements to other things; a correspondence rule is what makes it checkable, and `check_model.py` enforces one |
| **Each fact in one place** | **DRY** (Hunt and Thomas); single source of truth | Adopted | yes | The skills name the principle rather than an element ID. An ID from archreator's own motivation layer does not resolve for a reader of the skills, and in a downstream project resolves to *that* project's principle instead |
| **What a gap in the identifiers means** | The never-reuse rule, stated in `architecture-document-style` § Element IDs | Adopted | — | Same reason |
| **"Consolidate before you enumerate" / "well-done less is more"** | KISS; YAGNI; parsimony in modeling | Cite | — | The archreator phrasing is an instruction where the standards are slogans, so it earns its keep |
| **"The document describes the subject, not its own construction"** | Living documentation (Martraire); present-tense technical writing | Cite | — | Approximate. The specific ban on version commentary inside a document is archreator's own sharpening |
| **`restate-current-state`** | Adjacent only: documentation debt, model refactoring | **Ours** | — | Making "the model has drifted" its own gated initiative, with its own skill, has no standard name |

## AI actors

| archreator | Established | Verdict | Named in the skill | Note |
| ---------- | ----------- | ------- | ----------------- | ---- |
| **Autonomy levels** — advisory, co-pilot, autonomous with checkpoint, fully autonomous | Human **in** / **on** / **out of** the loop; Sheridan and Verplank's levels of automation | Cite | — | Four levels refine three: advisory and co-pilot are both human-in-the-loop, differing on whether the AI acts before or after the human decides. That pair is the distinction practitioners most often collapse, which is why four are kept |
| **Decision rights, escalation path** | Human oversight, as framed by NIST AI RMF's human-AI configuration and the EU AI Act's Article 14 | Cite | — | Approximate — those are compliance frames, not modeling notation. These columns are the modeling form of the same question |
| **Modeling an AI as a Business Actor holding a role** | — | **Ours** | — | The README calls this the project's distinguishing bet, and no established EA practice does it |

## Delivery practice

| archreator | Established | Verdict | Named in the skill | Note |
| ---------- | ----------- | ------- | ----------------- | ---- |
| **`record-decision`** | **ADR** — Architecture Decision Record (Nygard); MADR | Cite | yes | Its sections parallel MADR's. Not naming the pattern costs it every reader who already knows it |
| **`shard-stories`** | Vertical slicing; INVEST (Wake) | Cite | partly | The skill names vertical slicing and cites BMAD-METHOD for the context-engineering half. INVEST names the sizing criteria and is not in the skill |
| **`run-retrospective`** | Retrospective; blameless post-mortem | Cite | yes | |
| **`stack-selection`** | SPADE — Setting, People, Alternatives, Decide, Explain (Rajaram) | Cite | — | SPADE belongs with `record-decision` rather than here: this skill is a decision *aid* carrying defaults, not a decision *record* |
| **The canvases** | Osterwalder — Business Model Canvas, Value Proposition Canvas | Adopted | yes | |
| **The skill format** | [AIP](https://github.com/zach-blumenfeld/aip) — the Agent Instruction Protocol | Cite | — | The section vocabulary and the kind-decides-structure idea are AIP's. The fenced-YAML body is not adopted: these skills have no script-backed steps and no graph edges, which is what that format exists to carry. [`docs/skill-format.md`](./skill-format.md) says what was taken and what was left |
| **`shard-stories`' context packing** | [BMAD-METHOD](https://github.com/bmadcode/BMAD-METHOD) — context-engineered development | Cite | yes | Already cited in the skill itself |
