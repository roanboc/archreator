# ArChreator method reset — request and iteration record

- **Date:** 2026-08-31
- **Kind:** method and product reset
- **Scope:** the ArChreator repository only; `architecture-archreator` was
  deliberately left unchanged
- **Status:** implementation and repository validation complete

This temporary note records why ArChreator was reset, what changed, where the
work initially went too far, and which questions should be tested in real use.
It is intentionally stored at the repository root for later analysis and may
be deleted after that review.

## The request

Assess ArChreator as a customer who understands their initiative or business
but does not need to understand enterprise architecture first. Reset the method
to current needs and produce a simpler, more adoptable product without losing
the rigor that makes it useful.

The governing principles were:

- complexity creates failure; well-understood simplicity wins;
- people are the primary customer, while agents consume the same context;
- plain language and focused visuals make understanding, validation and
  communication easier; and
- agents must still traverse the organizational brain across repositories and
  Enterprise, Domain and Solution contexts.

The requested reset included removing low-value machinery, reducing skill and
token volume, simplifying documents, reconsidering assumptions made before
modern agent workflows, and restating the method from current truth.

## Final design decisions

| Concern | Decision |
| --- | --- |
| Customers | Independent builders are the primary guided customer. Enterprise architects remain first-class expert customers with direct standard navigation and less required guidance. |
| Authority | Canonical facts remain readable Markdown under `architecture/`. Agents, briefs, PDFs and the portal are reading or working surfaces, not authorities. |
| Initial project volume | A new project receives only host instructions, `.gitignore` and `architecture/README.md`. No empty area tree is created. |
| Standard structure | The complete Enterprise, Domain and Solution structure remains available lazily in the architecture rulebook and assets. An area folder appears only when it owns useful content. |
| Method kernel | Keep ten narrowly activated AIP-derived skills: five procedures, two document templates and three rulebooks. Preserve Needs, Produces, Judgement, conditional Gate, handoff, anti-pattern and completion contracts. |
| Process grounding | Keep the supplier-input-process-output-customer process model and bind executable skills to its outcomes. |
| Identifiers | Definition catalogues remain `ID | Name | …` for ordering. Every reference outside the defining row uses `Name [ID]`. |
| Hierarchies | Every populated hierarchy level has a file. Every child definition names its parent, and every canonical page states its location without relying on the folder tree or dotted ID. |
| Visual language | Keep ArchiMate-on-Mermaid notation with explicit stereotypes, glyphs, shapes, layer colours, labeled edges and human-first names. |
| Process presentation | Use stable semantic profiles rather than rigid pages: Level 1 landscape, Level 2 process contract and SIPOC, Level 3 operational flow, and Level 4 operating instructions outside architecture. |
| Working documents | Decision, impact, understanding and scope briefs are temporary under `.archreator/work/<run>/` and created only when useful or requested. |
| PDF | Export only an individual requested brief or scope. Remove whole-model PDF publishing. |
| Portal | Keep an on-demand searchable portal for direct browsing and business explanation outside the repository interface. Do not make agent interaction the only way to consume architecture. |
| Traversal | Read Markdown fresh into memory for validation and trace queries. Do not persist a SQLite graph or secondary model. |
| Federation | Retain authority, identity and cross-model contract semantics. Defer registry, synchronization, caching, transport and aggregation details until a real multi-repository use case proves them. |
| Migration | Rewrite ArChreator cleanly without a compatibility layer. Validate it first, then use it to simplify `architecture-archreator` later. |

## How the design changed during review

### 1. The customer definition was corrected

The first assessment treated the builder focus as replacing the earlier
architecture audience. The correction was that enterprise architects remain a
valid and important segment. They need less guided discovery, can navigate a
standard model directly, and can give agents better feedback throughout the
work.

The final design therefore has two routes over one source: guided use for a
builder and direct expert navigation for an enterprise architect.

### 2. Empty structure was separated from standard structure

The initial simplification removed the scaffold's empty folders and pages,
which was correct, but it also made the expected model shape difficult to
discover. The final distinction is:

- the consuming repository creates only the files it currently needs; and
- the plugin retains the complete standard structure, area asset and hierarchy
  guidance as lazy references.

An architecture status table in `architecture/README.md` records Local,
External, Out of scope or a specific Gap instead of materializing placeholders.

### 3. Agent-generated views were bounded

Focused decision, impact and understanding briefs were confirmed as useful,
including optional PDF for business readers. The whole-model PDF was removed.
The portal was retained because enterprise architects and business readers must
be able to browse and explain the architecture without going through an agent.

### 4. The first rewrite over-simplified the product

The clean rewrite initially removed too much: the visible scaffold guidance,
the AIP-derived skill format, the SIPOC process model and the ArchiMate visual
notation. That left something close to a plain preprompt and removed much of
ArChreator's differentiated value.

This was the most important correction in the work. Simplicity was redefined as
removing ceremony and unused artifacts while preserving the method kernel that
improves reasoning, consistency, navigation and communication.

### 5. The method kernel was restored in a smaller form

The restored kernel uses three explicit skill kinds:

- procedures for current context, questions, roadmaps, delivery and optional
  federation;
- document templates for focused briefs and durable decisions; and
- rulebooks for document style, architecture structure and proportionate
  process or capability depth.

Business-model, strategy and landscape discovery remain available as lazy
references inside `model-context` rather than standalone skills loaded into
every task.

### 6. ArchiMate visuals were restored as a single convention

The clean, explicit diagram style was retained. A modeled node shows
`<glyph> «ArchiMate type» Name [ID]`, uses the standard layer palette and shape,
and every edge is labeled. Conditional human decisions use rose workflow
notation and are not invented as ArchiMate elements.

The convention lives once in the plugin. Individual architecture pages do not
repeat generic legends or “How to read” sections.

### 7. Identifier guidance went through two refinements

The first correction made every visible identity human-first. The final
distinction is more useful:

- a catalogue definition keeps the ID in the first column because the order
  exposes a stable sequence and hierarchy; and
- prose, relationships, diagrams, briefs, parent references and generated
  traces always show `Name [ID]`.

The runtime now rejects noncanonical element catalogues, bare relationship
endpoints and stale displayed names.

### 8. Consistency became a content contract, not a fixed page

The concern was that different projects could produce unrelated process
formats. The response is a level-specific semantic contract with flexible
presentation:

- Level 1 shows the complete landscape, bands, purpose, owner, children and a
  macro view;
- Level 2 records purpose, trigger, full SIPOC, owner, realization and process
  boundaries;
- Level 3 adds actors, artifacts, ordered sub-processes, decisions, exceptions,
  applications, controls and handoffs; and
- Level 4 remains an operating instruction with ordinary step numbers and no
  architecture IDs.

The agent may combine or reorder tables, prose and visuals and may omit a
redundant artifact. It may not silently omit the meaning required at that
level.

### 9. Hierarchy became explicitly human-readable

A dotted ID is effective for a machine but insufficient orientation for a
person. The final hierarchy rule applies to processes, capabilities, data
objects, application components and other decomposed ArchiMate elements:

- create one file for every populated level;
- put an H1, direct navigation and one compact `Location` line on every
  canonical file below the architecture front door;
- add a `Parent` column to every nested definition and use `Name [ID]` there;
- derive the same-type Composition relationship from that parent reference;
  and
- create no empty file for an anticipated level.

ArChreator's own process model was split into distinct Level 1 and Level 2
files so the method demonstrates the rule it asks customer models to follow.

## What changed in the repository

### Method and documentation

- Rewrote the root explanation, adoption guide, method, skill format, process
  model and standards alignment in simpler current-state language.
- Reduced the active method to ten typed skills while retaining substantive
  AIP and SIPOC contracts.
- Added lazy business-model, strategy, landscape, domain-boundary, model
  structure, ArchiMate notation, hierarchy and process-presentation references.
- Added reusable area and hierarchy-level assets.

### Project scaffold

- Reduced the scaffold to `.gitignore`, `AGENTS.md`, the two host pointers and
  `architecture/README.md`.
- Removed empty area folders, empty catalogues, publication configuration,
  copied runtime scripts and placeholder issue or pull-request machinery.
- Kept one status table as the model boundary and navigation front door.

### Runtime and outputs

- Replaced the persisted graph toolchain with one source-fresh Python runtime.
- Added `check`, `trace`, `work`, scoped `pdf` and on-demand `portal` commands.
- Made ID-first catalogues, `Name [ID]` relationship endpoints, visible-name
  freshness, self-locating pages and parent hierarchy machine-checkable.
- Made `Parent` a traversable same-type Composition relationship.
- Restricted generated artifacts to the ignored `.archreator/work/` boundary.

### Portal and public site

- Added a small standard-library static portal builder with search, source
  links, standard status labels and Mermaid rendering with source fallback.
- Rewrote the public site around the two customer routes, typed method, lazy
  model, focused outputs and retained architecture rigor.
- No portal or public site was externally published during this work.

### Validation

- Added a standard-library method validator for the skill contract, process
  bindings, manifests, scaffold boundary, required method references and
  forbidden legacy machinery.
- Added runtime tests for source freshness, catalogue order, relationship
  references, stale names, hierarchy, self-location, traversal, scoped PDF and
  work boundaries.
- Added portal tests and CI workflows that run the method, runtime and portal
  suites.

## What was removed

| Removed | Reason |
| --- | --- |
| Empty scaffold layer tree and placeholder files | They create volume before value and make missing, external and out-of-scope context indistinguishable. |
| SQLite database, SQL neighbourhood query and persisted graph publication | Current Markdown can be read and traversed on demand without a second model or rebuild lifecycle. |
| Whole-model PDF and copied publication stack | Repository navigation and the portal are better whole-model reading surfaces; PDF remains useful only for one focused business artifact. |
| Mandatory Gate 0 to Gate 3 ceremony | Human stops now occur only for material uncertainty, authorization or required acceptance. |
| Permanent scope document for every change | Routine work uses the current model and implementation evidence; a temporary scope brief exists only when coordination benefits. |
| Numerous narrow top-level skills | Their useful judgement was consolidated into five procedures, two document templates and three rulebooks; discovery detail remains lazy. |
| Compatibility and migration layer | The requester chose a clean rewrite and later validation against real projects. |

## What the method did not cover well

### Simplicity versus identity

The earlier method did not state which parts formed the irreducible product
kernel. Without that boundary, reducing token and artifact volume could also
remove the elements that made ArChreator more than a prompt.

The correction was to distinguish ceremony from rigor: remove automatic files,
blank gates, duplicate representations and speculative infrastructure; retain
typed workflows, discovery judgement, SIPOC, ArchiMate semantics, human
navigation and validation.

**Generalizes:** yes. Every future simplification should name the capability it
preserves before deleting its current mechanism.

### Scaffold versus discoverable standard

The earlier method coupled “the standard exists” with “all standard files are
created now.” Removing the files then appeared to remove the standard.

The correction was lazy materialization: the project carries only current
content, while the plugin carries the discoverable structure and reusable
assets.

**Generalizes:** yes. A template library and a generated project are different
products and should have different volume.

### Machine hierarchy versus human location

The earlier rule treated the hierarchical ID as enough and discouraged a
Parent column. That optimized storage while forcing a reader to decode IDs or
paths.

The correction was to keep the dotted ID for machines and add a compact page
location plus a human-first parent reference for people.

**Generalizes:** yes. Machine-normalized identity should not replace local
human context.

### Consistency versus rigid templates

The earlier options were too close to either unrestricted generation or large
fixed pages. The useful middle is a semantic profile: define what must be
recoverable, recommend strong presentation patterns and let the agent adapt the
layout.

**Generalizes:** yes. Content contracts should be stable; rendering should be
purpose- and reader-sensitive.

## Deliberately not done

- `architecture-archreator` was not simplified or migrated. It remains a later
  validation case after this method is accepted.
- The `ea_bigview` model was read for usage evidence but not edited.
- Federation transport, registry and synchronization were not designed without
  a proven use case.
- No external plugin installation, cache refresh, release, portal deployment or
  public site deployment was performed.
- No customer or confidential business content was copied into this note.

## Follow-up validation

1. Apply the scaffold and method to one genuinely small application repository.
   Measure created file count, questions asked, token load and whether the
   builder can validate the result unaided.
2. Apply the hierarchy and process profiles to `ea_bigview`. Confirm that a
   reader can move from Level 1 to Level 3 and identify the full parent chain on
   every page without decoding paths.
3. Exercise Enterprise → Domain → Solution federation across real repositories
   before choosing transport or aggregation machinery.
4. Test the portal with an enterprise architect explaining the model to a
   business audience and record what direct browsing still lacks.
5. After ArChreator is accepted, simplify `architecture-archreator` using the
   new method and compare the resulting volume and clarity.
6. Decide from those trials whether visible `Name [ID]` references in arbitrary
   prose and Mermaid need broader automated linting beyond the enforced
   catalogue, relationship and parent contracts.

## Review entry points

- [Method](./docs/method.md)
- [Skill format](./docs/skill-format.md)
- [Process model](./docs/process/README.md)
- [Model structure](./plugins/archreator/skills/architecture-document-style/references/model-structure.md)
- [Hierarchical elements](./plugins/archreator/skills/architecture-document-style/references/hierarchical-elements.md)
- [ArchiMate on Mermaid](./plugins/archreator/skills/architecture-document-style/references/archimate-on-mermaid.md)
- [Process presentation patterns](./plugins/archreator/skills/process-and-capability-levels/references/process-presentation-patterns.md)
- [Runtime guide](./plugins/archreator/scripts/README.md)
- [Portal guide](./docs/portal.md)
