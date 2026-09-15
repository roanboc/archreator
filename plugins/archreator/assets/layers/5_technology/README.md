# Technology Layer

_[← EA home](../README.md)_

The runtimes, tooling, and infrastructure that the
[application layer](../4_application/README.md) executes on.

## Analysis order

Files are numbered in the order they are analyzed: first _which technology
services exist and what provides them_, then _how the built artifacts reach
their runtime nodes_.

| #   | Document                                               | Elements                                                          | Question it answers                       |
| --- | --------------------------------------------------------| --------------------------------------------------------------------| --------------------------------------------- |
| 1   | [1_technology-services.md](./1_technology-services.md) | Technology Services and the nodes/system software providing them | What infrastructure services are used?    |
| 2   | [2_deployment.md](./2_deployment.md)                   | Nodes, Artifacts, and the CI/CD deployment pipeline               | How does the build get to where it runs?  |

If no stack has been chosen yet, use the `stack-selection` skill for the
decision framework and the criteria to judge current options against, before
writing `1_technology-services.md`.

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
  node["⬒ «Node» where it runs [NODE#]"]:::technology
  tsvc(["⬯ «Technology Service» what the platform offers [TSVC#]"]):::technology
  art[/"⎔ «Artifact» what is deployed or persisted [ART#]"/]:::technology
  cmp["⊞ «Application Component» what it hosts, from the application layer [ACMP#]"]:::application

  node -->|realizes| tsvc
  node -->|hosts| art
  art -->|realizes| cmp
  tsvc -->|serves| cmp

  classDef technology fill:#c9e7b7,stroke:#558b2f,color:#333
  classDef application fill:#9adcf0,stroke:#0288d1,color:#333
```

Green is Technology; the application component is a visitor and keeps its
cyan.

## Layer view

<!--
  TEMPLATE — replace with the project's real runtimes, hosting, and CI/CD
  pipeline once known.
-->

```mermaid
flowchart TB
  runtime["⬒ <Where it runs> [NODE#]"]:::technology
  hosting(["⬯ <Hosting/platform> [TSVC#]"]):::technology
  ci(["⬯ <CI/CD> [TSVC#]"]):::technology

  ci -->|builds and publishes to| hosting
  runtime -->|requests| hosting

  classDef technology fill:#c9e7b7,stroke:#558b2f,color:#333
```
