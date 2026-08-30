# The process model

_[Repository README](../../README.md) · [The method](../method.md) · [Skill format](../skill-format.md)_

**Location:** ArChreator method → Process model.

This is ArChreator applied to itself: a compact view of the work the method
performs and the skills that perform it. The numbered files define each
populated level; this index explains how work moves between them.

## Process flow

```mermaid
flowchart LR
  need(["A subject, question, target or change"])
  current["⚙ «Business Process» Model current context [BPROC1.1]"]:::business
  cross{"Cross-model context needed?"}
  connect["⚙ «Business Process» Connect cross-model context [BPROC1.2]"]:::business
  route{"What is needed?"}
  answer["⚙ «Business Process» Answer a context question [BPROC2.1]"]:::business
  roadmap["⚙ «Business Process» Plan a roadmap [BPROC2.2]"]:::business
  assess["⚙ «Business Process» Frame and assess a change [BPROC3.1]"]:::business
  implement["⚙ «Business Process» Implement and verify [BPROC3.2]"]:::business
  refresh["⚙ «Business Process» Refresh current context [BPROC3.3]"]:::business
  understood(["A grounded answer"])
  planned(["A target and sequence"])

  need --> current --> cross
  cross -->|yes| connect --> route
  cross -->|no| route
  route -->|understand or decide| answer --> understood
  route -->|target and sequence| roadmap --> planned
  planned -.->|an initiative is selected| assess
  route -->|deliver a change| assess --> implement --> refresh --> current

  classDef business fill:#fffbb5,stroke:#b8a200,color:#333
```

## Populated levels

| Document | Defines |
| --- | --- |
| [Macro processes — Level 1](./1_level-1-macro-processes.md) | Three macro processes and the Level 2 processes each contains |
| [Processes — Level 2](./2_level-2-processes.md) | Seven complete supplier-input-process-output-customer contracts and their skill bindings |

The hierarchy is complete to Level 2. Implement and verify [BPROC3.2] is the
second child of Deliver change and keep context true [BPROC3]; order of
execution comes from the flow rather than the number. No current need justifies
a Level 3 method-process file.

## Skill and gate relationship

Procedures perform ordered work. Document templates produce a focused artifact
inside that work. Rulebooks preserve language, architecture and process
consistency without becoming extra processes.

Human gates are conditional exceptions inside the Level 2 processes. They run
only for material gaps or inconsistencies, consequential authorization, or
explicitly required acceptance. Clear evidence and routine verification
continue without a blanket approval sequence.
