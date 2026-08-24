# Level 1 — the macro processes

_[← The process model](./README.md)_

The five macro processes, each with its level-2 children, ordered on this page by
when they run rather than by identifier — `BPROC5` was added last and runs second.
The map that places them relative to one another is on
[the index page](./README.md#the-macro-process-map); this page opens each one up.
What every child process consumes and produces is in
[`2_level-2-processes.md`](./2_level-2-processes.md).

## `BPROC1` — Establish the architecture model

Turns a subject nobody has modeled into a populated, approved model the next change
can be judged against.

```mermaid
flowchart TD
  req(["A subject nobody has modeled yet"])
  p11["⚙ Establish the project [BPROC1.1]"]
  org{"Is the subject an organization?"}
  p12["⚙ Discover the business model [BPROC1.2]"]
  g0{{"❖ Gate 0 — the canvases"}}
  p13["⚙ Discover the strategy [BPROC1.3]"]
  g1{{"❖ Gate 1 — the strategy layer"}}
  deep{"Several business lines?"}
  p14["⚙ Split the model into domains [BPROC1.4]"]
  est{"Does an estate already run?"}
  p15["⚙ Discover the current landscape [BPROC1.5]"]
  g23{{"❖ Gates 2 and 3 — the landscape"}}
  done(["A model a change can be judged against"])

  req --> p11 --> org
  org -->|yes, Depth 2 or 3| p12 --> g0
  g0 -->|changes requested| p12
  g0 -->|approved| p13
  org -->|no, Depth 1| p13
  p13 --> g1
  g1 -->|changes requested| p13
  g1 -->|approved| deep
  deep -->|yes, Depth 3| p14 --> est
  deep -->|no| est
  est -->|yes| p15 --> g23
  g23 -->|changes requested| p15
  g23 -->|approved| done
  est -->|no, greenfield| done

  classDef business fill:#fffbb5,stroke:#c8c04a,color:#333
  classDef implementation fill:#ffd6d6,stroke:#d99b9b,color:#333
  class p11,p12,p13,p14,p15,req,done business
  class g0,g1,g23 implementation
```

The depth question is asked once, at `BPROC1.1`, and it decides which of these
processes run at all. A Depth 1 application never enters `BPROC1.2`, and only a
Depth 3 enterprise enters `BPROC1.4`.

`BPROC1.5` is decided by a different question, asked later: whether the subject was
already running before anyone modeled it. A greenfield project skips it and fills its
lower layers one initiative at a time through `BPROC2`; an organization that has
existed for years cannot, because the estate is not a consequence of any requirement
and no requirement will ever ask for it to be written down.

## `BPROC5` — Plan the transition

Turns an approved description of today into a destination, the distance to it, and the
order that distance is closed in.

```mermaid
flowchart TD
  ask(["Where should this go, and what first?"])
  base{"Is there a baseline worth planning from?"}
  back(["⇄ BPROC1.5, or BPROC3.1"])
  p51["⚙ Define the target and sequence the roadmap [BPROC5.1]"]
  g1{{"❖ Gate 1 — the target and the sequence"}}
  road(["A direction each later change is judged against"])

  ask --> base
  base -->|no| back
  base -->|yes| p51 --> g1
  g1 -->|changes requested| p51
  g1 -->|approved| road

  classDef business fill:#fffbb5,stroke:#c8c04a,color:#333
  classDef implementation fill:#ffd6d6,stroke:#d99b9b,color:#333
  class p51,ask,back,road business
  class g1 implementation
```

The only process whose output describes a future. Everything else in the model —
every layer document, every validator, every restatement — is held to describing
what is true now, and that rule is worth keeping precisely because one place is
exempt from it. The exemption is a folder, `architecture/roadmap/`, and it is the
whole of `BPROC5`'s output.

It reuses Gate 1 rather than adding a fifth gate. The reasoning is in
[`2_level-2-processes.md`](./2_level-2-processes.md).

## `BPROC2` — Deliver an architected change

Turns a Requester's requirement into merged code whose architecture documents are
still true.

```mermaid
flowchart TD
  req(["A requirement, or a problem"])
  p21["⚙ Align the change through the layers [BPROC2.1]"]
  g2{{"❖ Gate 2 — strategy, business, information"}}
  g3{{"❖ Gate 3 — the solution design"}}
  p22["⚙ Implement and verify [BPROC2.2]"]
  p23["⚙ Hand over for review [BPROC2.3]"]
  merged(["Merged"])

  req --> p21 --> g2
  g2 -->|changes requested| p21
  g2 -->|approved, Gate 3 requested| g3
  g3 -->|changes requested| p21
  g3 -->|approved| p22
  g2 -->|approved, Gate 3 not requested| p22
  p22 --> p23 --> merged

  classDef business fill:#fffbb5,stroke:#c8c04a,color:#333
  classDef implementation fill:#ffd6d6,stroke:#d99b9b,color:#333
  class p21,p22,p23,req,merged business
  class g2,g3 implementation
```

`BPROC2.1` is the only process in the model that can reach two gates, and the second
is the Requester's option rather than the method's requirement. Its interior is the
one branch detailed to level 3, in
[`3_level-3-align-a-change.md`](./3_level-3-align-a-change.md).

## `BPROC3` — Keep the model true

Turns a model that has drifted from what shipped back into a description of today.

```mermaid
flowchart TD
  drift(["The model no longer reads as a description of today"])
  call(["One consequential call, smaller than an initiative"])
  p31["⚙ Restate the current state [BPROC3.1]"]
  g2b{{"❖ Gate 2 — the restatement"}}
  p32["⚙ Record a decision [BPROC3.2]"]
  back(["A model that describes today"])
  rec(["A rationale a future reader can find"])

  drift --> p31 --> g2b -->|approved| back
  g2b -->|changes requested| p31
  call --> p32 --> rec

  classDef business fill:#fffbb5,stroke:#c8c04a,color:#333
  classDef implementation fill:#ffd6d6,stroke:#d99b9b,color:#333
  class p31,p32,drift,call,back,rec business
  class g2b implementation
```

The two children share a band and nothing else. They answer different triggers, run
independently, and never hand off to one another, which is why the band has no
internal sequence.

## `BPROC4` — Learn from the engagement

Turns what the method failed to cover into proposals, before the memory of it
evaporates.

```mermaid
flowchart TD
  fin(["An initiative or engagement just finished"])
  p41["⚙ Run the engagement retrospective [BPROC4.1]"]
  prop(["Proposals for the method"])

  fin --> p41 --> prop

  classDef business fill:#fffbb5,stroke:#c8c04a,color:#333
  class p41,fin,prop business
```

One child, and the thinnest band in the model. It earns its place because its output
is the only input `BPROC1` has for changing the method itself.
