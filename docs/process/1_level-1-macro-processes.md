# Level 1 — the macro processes

_[← The process model](./README.md)_

The five macro processes, each with its level-2 children, ordered on this page by
when they run rather than by identifier — `BPROC5` was added last and runs second.
An identifier is assigned once and never reallocated, so a number says when a
process joined the model; the sequence is carried by this page's order and the
map, never by the number.
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
  p13["⚙ Discover the strategy [BPROC1.3]"]
  deep{"Several business lines?"}
  p14["⚙ Split the model into domains [BPROC1.4]"]
  est{"Does an estate already run?"}
  p15["⚙ Discover the current landscape [BPROC1.5]"]
  done(["A model a change can be judged against"])

  req --> p11 --> org
  org -->|yes, Depth 2 or 3| p12 --> p13
  org -->|no, Depth 1| p13
  p13 --> deep
  deep -->|yes, Depth 3| p14 --> est
  deep -->|no| est
  est -->|yes| p15 --> done
  est -->|no, greenfield| done

  classDef business fill:#fffbb5,stroke:#c8c04a,color:#333
  class p11,p12,p13,p14,p15,req,done business
```

The depth question is asked once, at `BPROC1.1`, and it decides which of these
processes run at all. A Depth 1 application never enters `BPROC1.2`, and only a
Depth 3 enterprise enters `BPROC1.4`.

`BPROC1.5` is decided by a different question, asked later: whether the subject was
already running before anyone modeled it. A greenfield project skips it and fills its
lower layers one initiative at a time through `BPROC2`; an organization that has
existed for years cannot, because the estate is not a consequence of any requirement.

## `BPROC5` — Plan the transition

Turns an approved description of today into a destination, the distance to it, and the
order that distance is closed in.

```mermaid
flowchart TD
  ask(["Where should this go, and what first?"])
  base{"Is there a baseline worth planning from?"}
  back(["⇄ BPROC1.5, or BPROC3.1"])
  p51["⚙ Define the target and sequence the roadmap [BPROC5.1]"]
  road(["A direction each later change is judged against"])

  ask --> base
  base -->|no| back
  base -->|yes| p51 --> road

  classDef business fill:#fffbb5,stroke:#c8c04a,color:#333
  class p51,ask,back,road business
```

The only process whose output describes a future. Everything else in the model is
held to describing what is true now; the exemption is one folder,
`architecture/6_transition/`, and it is the whole of `BPROC5`'s output.

Built directly and merged like any initiative, rather than needing an approval
of its own — see [`2_level-2-processes.md`](./2_level-2-processes.md).

## `BPROC2` — Deliver an architected change

Turns a Requester's requirement into merged code whose architecture documents are
still true.

```mermaid
flowchart TD
  req(["A requirement, or a problem"])
  p21["⚙ Align the change through the layers [BPROC2.1]"]
  p22["⚙ Implement and verify [BPROC2.2]"]
  p23["⚙ Hand over for review [BPROC2.3]"]
  merged(["Merged — the approval"])

  req --> p21 --> p22 --> p23 --> merged

  classDef business fill:#fffbb5,stroke:#c8c04a,color:#333
  class p21,p22,p23,req,merged business
```

`BPROC2.1`'s interior is the one branch detailed to level 3, in
[`3_level-3-align-a-change.md`](./3_level-3-align-a-change.md).

## `BPROC3` — Keep the model true

Keeps a model truthful, records the calls that explain it, and turns one
reader question into a bounded reading without changing the model.

```mermaid
flowchart TD
  drift(["The model no longer reads as a description of today"])
  onecall(["One consequential call, smaller than an initiative"])
  question(["A reader has one architecture question"])
  p31["⚙ Restate the current state [BPROC3.1]"]
  p32["⚙ Record a decision [BPROC3.2]"]
  p33["⚙ Answer an architecture question [BPROC3.3]"]
  back(["A model that describes today"])
  rec(["A rationale a future reader can find"])
  brief(["A focused, disposable brief"])

  drift --> p31 --> back
  onecall --> p32 --> rec
  question --> p33 --> brief

  classDef business fill:#fffbb5,stroke:#c8c04a,color:#333
  class p31,p32,p33,drift,onecall,question,back,rec,brief business
```

The three children share a band and nothing else: different triggers, run
independently, never handing off to one another, so the band has no internal
sequence.

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

One child, and the thinnest band in the model. Its output is the only input
`BPROC1` has for changing the method itself.
