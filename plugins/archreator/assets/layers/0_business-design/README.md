# Business Design Layer

_[← EA home](../README.md)_

The business model in the language the business uses: who the customers are,
what they are trying to get done, what hurts today, and which product or
service relieves it. For each product, how it is delivered and paid for.

**ArchiMate viewpoint:** none. Two Strategyzer canvases: a
[Value Proposition Canvas](https://www.strategyzer.com/library/the-value-proposition-canvas)
per customer segment and a
[Business Model Canvas](https://www.strategyzer.com/library/the-business-model-canvas)
per product or service. Layers 1 to 5 are derived from their blocks.

<!--
  TEMPLATE — emitted by `discover-business-model` on an organization only; an
  application project never has this folder. The block-by-block mapping to
  ArchiMate and the fit rule are the method's (`architecture-document-style`,
  the canvases reference); the fit verdict is written in the value proposition
  canvas. Keep this page in the layer README shape and nothing else.
-->

## Documents

| #   | Document                                                             | Elements                                                                          | Question it answers                                     |
| --- | -------------------------------------------------------------------- | --------------------------------------------------------------------------------- | -------------------------------------------------------- |
| 1   | [1_value-proposition-canvas.md](./1_value-proposition-canvas.md)     | Customer Segments, Jobs, Pains, Gains, Products & Services, Pain Relievers, Gain Creators | Who do we serve, what do they need, and what do we offer? |
| 2   | [2_business-model-canvas.md](./2_business-model-canvas.md)           | The nine BMC blocks, one canvas per product or service                            | How is each offering delivered, and how does it pay?     |

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
  subgraph VPC["Value Proposition Canvas"]
    cs(["◍ «Customer Segment» who we serve [CS#]"]):::motivation
    job{{"⚙ «Job» what they are trying to do [JOB#]"}}:::motivation
    pain>"✖ «Pain» what hurts today [PAIN#]"]:::motivation
    gain[["✔ «Gain» what they would call a win [GAIN#]"]]:::motivation
    prod["▣ «Product» what they get [PROD#]"]:::strategy
    prel[/"⊖ «Pain Reliever» how the pain is removed [PREL#]"\]:::strategy
    gcre[/"⊕ «Gain Creator» how the gain is produced [GCRE#]"\]:::strategy
  end
  subgraph BMC["Business Model Canvas"]
    kp{{"⧉ «Key Partner» who we depend on [KP#]"}}:::business
    kr[("▤ «Key Resource» what we have [KR#]")]:::strategy
    ka{{"⚙ «Key Activity» what we do with it [KA#]"}}:::strategy
    vp["◈ «Value Proposition» what the product promises [VP#]"]:::strategy
    ch["⊸ «Channel» how it reaches them [CH#]"]:::business
    cr["⇄ «Customer Relationship» how we treat them [CR#]"]:::business
    rs[/"▲ «Revenue Stream» what comes in [RS#]"\]:::technology
    cost[\"▼ «Cost» what it costs [COST#]"/]:::implementation
  end

  cs -->|performs| job
  job -->|frustrated by| pain
  job -->|rewarded by| gain
  prod -->|aggregates| prel
  prod -->|aggregates| gcre
  prel -->|addresses| pain
  gcre -->|produces| gain
  kp -->|enables| ka
  kr -->|enables| ka
  ka -->|produces| prod
  prod -->|promises| vp
  prod -->|reaches through| ch
  ch -->|reaches| cs
  cr -->|keeps| cs
  cs -->|pays| rs
  ka -->|incurs| cost

  classDef motivation fill:#e6d6f5,stroke:#7e57c2,color:#333
  classDef strategy fill:#f5deaa,stroke:#c8a24a,color:#333
  classDef business fill:#fffbb5,stroke:#b8a200,color:#333
  classDef technology fill:#c9e7b7,stroke:#558b2f,color:#333
  classDef implementation fill:#ffd6d6,stroke:#b06060,color:#333
```

The customer profile takes the Motivation fill and the value map the Strategy
fill, because that is where each block lands once derived; the segment and the
product are the same elements on both canvases. Revenue borrows the Technology
green and cost the Implementation rose, because no ArchiMate element lends
them a colour.

## Layer view

<!--
  TEMPLATE — replace with the project's real segment, job, pain, gain,
  product, and the capability that relieves the pain, once known. Keep the
  shape: the customer profile on the left, the value map on the right, and
  the "addresses"/"produces" edges between them — those edges are the fit.
-->

```mermaid
flowchart LR
  subgraph PROFILE["Customer profile"]
    seg(["◍ <Who we serve> [CS#]"]):::motivation
    job{{"⚙ <What they're trying to do> [JOB#]"}}:::motivation
    pain>"✖ <What hurts today> [PAIN#]"]:::motivation
    gain[["✔ <What they'd call a win> [GAIN#]"]]:::motivation
  end

  subgraph VALUEMAP["Value map"]
    prod["▣ <What we offer> [PROD#]"]:::strategy
    prel[/"⊖ <How it removes the pain> [PREL#]"\]:::strategy
    gcre[/"⊕ <How it produces the gain> [GCRE#]"\]:::strategy
  end

  seg -->|performs| job
  job -->|frustrated by| pain
  job -->|rewarded by| gain
  prod -->|aggregates| prel
  prod -->|aggregates| gcre
  prel -->|addresses| pain
  gcre -->|produces| gain

  classDef motivation fill:#e6d6f5,stroke:#7e57c2,color:#333
  classDef strategy fill:#f5deaa,stroke:#c8a24a,color:#333
```

The canvas blocks take the Motivation and Strategy fills because that is
where they land once derived. The palette's single source is the
`architecture-document-style` rulebook § ArchiMate on Mermaid.
