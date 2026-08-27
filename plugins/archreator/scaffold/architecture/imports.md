# Imports

_[← EA home](./README.md)_

**Used only by a model that references an element in another repository.** A
model that stands alone, or one whose federation lives in the same repository,
leaves this file as it is and nothing reads it.

**Status:** ○ Not started.

A reference that names another model — `other-model::` and then an identifier —
resolves in one of two ways, and which one depends on where that model is.

| The model is | How the reference resolves |
| ------------ | -------------------------- |
| **In this repository** | Against that model's own definitions, which the validator already has. Nothing is declared and nothing can go stale |
| **In another repository** | Against a row in the table below |

## Why a declaration rather than a lookup

Nothing here fetches anything. A validator that read a sibling repository on
every pull request would be slow, would fail whenever somebody else's site was
down, and would let another team's push break this build.

So what is checked is that the dependency was **written down**: an identifier
somebody typed becomes a dependency this model states. That is the same shape
[`domains/`](./domains/README.md) already gives a domain contract — what you
consume is declared, and changing it is a conversation rather than a surprise.

The cost is honest and worth saying out loud: **a row here can be internally
consistent and out of date.** Whether it still matches the upstream is asked by
somebody running the refresh, not by CI.

## What this model consumes

| Element | Name | Read at |
| ------- | ---- | ------- |
|         |      |         |

Read by position: cell 1 the foreign identifier, backticked; cell 2 the name
that model gives it; cell 3 the revision it was read at — a commit, a tag, a
release. Cell 2 is a copy of somebody else's fact and is treated like every
other copy the method allows: written once, and checked.

## What this cannot do

**It cannot reach a private repository**, and neither can the navigator. A
model you cannot publish is a model nobody can federate with.

**It cannot tell you the upstream changed.** It can only tell you this model
disagrees with itself. The two are different failures and only one of them is
mechanical.
