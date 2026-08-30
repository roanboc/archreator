# ArChreator

**Architecture people can understand and AI can build from.**

ArChreator helps a builder describe an initiative, solution, domain or
enterprise in plain language. It keeps the result as navigable Markdown in the
same repository, with ArchiMate concepts and relationships available as
secondary metadata for enterprise architects and agents.

The method is designed for two equally valid routes:

- a builder explains the subject and receives only the guidance needed to make
  it clear and buildable;
- an enterprise architect navigates the standard structure, relationships and
  portal directly to find gaps or explain the architecture.

An agent is a consumer of this context, not the customer and not the only way
to read it.

## What is different

- A new model starts with one `architecture/README.md`, not empty layer trees.
- A layer folder is created only when the repository owns useful content in it.
- Clear evidence becomes current context without blanket approval ceremonies.
- A person decides only when a gap, inconsistency, material authorization or
  required acceptance needs judgement.
- Decision, impact and understanding briefs are temporary outputs under
  `.archreator/work/<run>/`.
- Requested briefs and scopes can be exported individually to PDF. The complete
  architecture is read in the repository or the on-demand portal, never as one
  large PDF.
- Relationships are parsed from current Markdown on every question. There is
  no SQLite database, cached graph or projection publication.

## The model

`architecture/README.md` is the human front door. It states the model boundary,
owner, level and the status of the standard areas.

| Area | What it explains |
| --- | --- |
| Business design | Customers, value and operating model, only when the business itself is in scope |
| Strategy | Direction, outcomes, drivers and constraints |
| Business | People, capabilities, services and processes |
| Information | Meaning, ownership, use and movement of information |
| Application | Applications, components, interfaces and behavior |
| Technology | Runtimes, platforms, infrastructure and deployment |
| Roadmap and transition | Accepted targets, material gaps and change sequence |

The full document structure and ArchiMate metadata contract live in the
[`architecture-document-style` reference](./plugins/archreator/skills/architecture-document-style/references/model-structure.md).
Its [ArchiMate-on-Mermaid notation](./plugins/archreator/skills/architecture-document-style/references/archimate-on-mermaid.md)
keeps human names dominant while glyphs, stereotypes, shapes, layer colours,
labeled edges and secondary stable IDs make each view precise.

The [hierarchical-element rules](./plugins/archreator/skills/architecture-document-style/references/hierarchical-elements.md)
give every populated level a file, require each child to name its parent and
make every page state where it sits without relying on the folder tree.

Process models use [level-specific presentation profiles](./plugins/archreator/skills/process-and-capability-levels/references/process-presentation-patterns.md):
level 1 shows the landscape, level 2 carries the process contract and SIPOC,
and level 3 adds the operational flow, actors, artifacts, decisions, controls
and handoffs. The required meaning is stable; the page layout remains flexible.

## Quick start

Install the plugin using the instructions for your agent in
[Adopting ArChreator](./docs/adopting.md), then describe what you need:

> Help me model this initiative clearly.

> What would changing the order service affect?

> Explain this architecture to a business reader and create the portal.

ArChreator will establish or refresh only the context needed for that request.

## Method, not a preprompt

ArChreator has ten narrowly activated skills in three types:

- five **Procedures** for modeling context, answering questions, planning,
  delivering change and optional federation;
- two **Document templates** for temporary focused briefs and durable
  decisions; and
- three **Rulebooks** for clear documents, architecture structure and
  proportionate process or capability depth.

The skill contract is adapted from the Agent Instruction Protocol (AIP): every
procedure states when to use it and when not to, its invariants, inputs,
outputs, judgements, conditional human checkpoints, handoffs, anti-patterns and
completion tests. A supplier-input-process-output-customer (SIPOC) model binds
that work to accountable outcomes, so missing method coverage is visible.

See the [skill catalogue](./plugins/archreator/skills/README.md),
[skill format](./docs/skill-format.md), [process model](./docs/process/README.md)
and [method](./docs/method.md).

## License

ArChreator is available under the [MIT License](./LICENSE).
