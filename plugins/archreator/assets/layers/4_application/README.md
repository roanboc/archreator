# Application Layer

_[← EA home](../README.md)_

The software that realizes the business services: application services, the
components providing them, how the components collaborate, and the solution
design and the contract of every interface.

**ArchiMate viewpoint:** Application layer: Application Service, Application
Component, Application Collaboration, Application Interface.

<!--
  TEMPLATE — the author's notes: a small project populates 1 and 2 and adds
  3–5 when the component count or the number of interchangeable adapters earns
  the grain. Every component row names the module or file that implements it
  (the grounding rule in `architecture-document-style`). "How to add a new X"
  recipes go in 4_solution-design.md once the shape repeats.
-->

## Documents

| #   | Document                                                             | Elements                                                     | Question it answers                              |
| --- | -----------------------------------------------------------------------| --------------------------------------------------------------- | --------------------------------------------------- |
| 1   | [1_application-services.md](./1_application-services.md)             | Application Services and the business services they realize | What does the software offer the business layer? |
| 2   | [2_application-components.md](./2_application-components.md)         | Application Components, mapped to source files               | Which components provide those services?          |
| 3   | [3_application-collaborations.md](./3_application-collaborations.md) | Collaborations and interaction sequences                     | How do the components interact?                   |
| 4   | [4_solution-design.md](./4_solution-design.md)                       | Overall design, diagrams, patterns, tooling                  | How is the code structured, and why?               |
| 5   | [5_interface-contracts.md](./5_interface-contracts.md)               | Per-interface pre/postconditions, invariants, error behavior | What exactly does each interface promise?          |

## Metamodel

<!--
  The notation of this layer, written once: every element type the layer's
  documents draw, with its glyph, shape, colour, stereotype and prefix, and
  how the types typically connect. Keep it in step with the documents below;
  they carry no legend of their own.
-->

```mermaid
flowchart LR
  %% legend
  svc(["⬮ «Application Service» what the software offers [ASVC#]"]):::appservice
  cmp["⊞ «Application Component» what provides it [ACMP#]"]:::application
  aif["⊸ «Application Interface» where it is reached [AIF#]"]:::application
  bsvc(["⬭ «Business Service» what it realizes, from the business layer [BSVC#]"]):::business

  cmp -->|realizes| svc
  svc -->|exposed at| aif
  svc -->|realizes| bsvc
  cmp -->|serves| cmp

  classDef appservice fill:#c2f0ff,stroke:#0288d1,color:#333
  classDef application fill:#9adcf0,stroke:#0288d1,color:#333
  classDef business fill:#fffbb5,stroke:#b8a200,color:#333
```

A single-layer view, so the cyan ramps from service to component; the
business service is a visitor and keeps its yellow.

## Layer view

<!--
  TEMPLATE — replace with the project's real service, components and how they
  depend on each other. Keep the label shape: glyph, name, identifier. This is
  a single-layer view, so the cyan ramps from service to component.
-->

```mermaid
flowchart TB
  svc(["⬮ <What the software offers> [ASVC#]"]):::appservice
  entry["⊞ <Entry point> [ACMP#]"]:::application
  core["⊞ <Core logic> [ACMP#]"]:::application
  adapter["⊞ <Adapter/implementation> [ACMP#]"]:::application

  entry -->|realizes| svc
  core -->|serves| entry
  adapter -->|serves| core

  classDef appservice fill:#c2f0ff,stroke:#0288d1,color:#333
  classDef application fill:#9adcf0,stroke:#0288d1,color:#333
```
