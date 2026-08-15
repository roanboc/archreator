---
name: discover-domain-modeling
description: Use when an organization's model is large enough to split into business lines or domains, when adding a new domain to an existing enterprise model, or when a change crosses a domain boundary. Covers the split test, writing a domain charter, namespaced element IDs, and the federation rule that governs cross-domain contracts. Not needed for a project modeling a single application or a single organization.
---

# Modeling an organization as domains

_Reached from `core-architecture-first-change` Step 1b, or when a Requester asks to model a
business line. The structure this skill produces is described in
`architecture/domains/README.md`;
`README.md` orients a person._

A **domain** is a part of the organization modeled as though it were an
organization in its own right — customers, services, capabilities, and a
purpose larger than itself. Some of its customers are external; some are
other domains. The model shape repeats at every level, so a business line
can be understood on its own terms.

This is `architecture/README.md` § Modeling depth. Reaching it is
a decision, not a default: at Depth 2 the whole organization shares one
`architecture/` tree, and that is correct until it isn't.

## Step 1 — Decide whether to split at all

Splitting costs a charter to maintain, a boundary to respect, and a set of
Requesters to consult on every contract change. Apply the test in
`architecture/domains/README.md` § When to split a domain out:
carve one out only when **two or more** hold — its own customers, its own
economics, its own decision rights, its own capabilities, a named interface.

Two questions settle most cases:

1. **What would this domain expose?** If you can't name the services other
   parts of the organization would consume, it isn't a domain yet. A team
   that everyone reaches into ad hoc is a team.
2. **Who says yes inside it?** If every meaningful decision escalates out,
   the boundary is organizational fiction and modeling it will produce a
   charter nobody honors.

Say the verdict out loud with its reason. "Three of the five tests hold —
own customers, own economics, own decision rights — so I'd model Advisory
as a domain" is a sentence the Requester can disagree with. Silently
restructuring the tree is not.

**Splitting is a business-layer change.** It goes through `core-architecture-first-change`
like anything else: a scope document, and Gate 2 before the folders move.

## Step 2 — Write the charter

The domain's `README.md` **is** its charter — the contract between it and
the rest of the organization, and the only part other domains may depend on.
Write it before filling in any of the domain's layers: the charter is what
the split is *for*, and writing it first is what catches a domain that
turns out to have nothing to expose.

```markdown
# Domain — <Name>

_[← Domains](../README.md) · [EA home](../../README.md)_

**Purpose.** <What this domain is for, and the larger purpose it serves.>

## Customers

| Customer | Kind | What they need from this domain |
| -------- | ---- | -------------------------------- |
| <segment or domain> | external / internal | <…> |

## Exposed services

The interface. Other domains may reference these IDs and nothing else.

| ID | Service | Serves | Realized by |
| -- | ------- | ------ | ----------- |
| `BSVC1` | <name> | <customer or domain> | <team, procedure, or component — or "Pending"> |

## Consumed services

| Qualified ID | From | What this domain relies on it for |
| ------------- | ---- | ---------------------------------- |
| `OTHER.BSVC2` | <domain> | <…> |

## Decision rights and escalation

- **Decides alone:** <concrete decisions this domain makes without asking>
- **Escalates to:** <a named role, not "a human">

## Operated by

<Human / AI / Hybrid>, at <autonomy level>. <Decision rights and escalation
path, per `core-architecture-doc-style` § Actors — applied to the domain as a whole.>
```

Two rules that decide whether the charter is worth anything:

- **Exposed means exposed.** A service in this table is a promise. If you
  wouldn't want another domain building on it, don't list it.
- **The grounding rule still applies.** Every exposed service names the
  team, written procedure, or component that realizes it — or is marked
  "Pending — future initiative". A charter full of aspirations is how a
  federated model rots.

## Step 3 — Fill in the domain's layers

Same numbered layers as the enterprise, same skills (`core-architecture-doc-style` for
notation, `discover-strategy` if the domain needs its own strategy). Fill
in only the layers the domain has something to say about and mark the rest
"not started".

A domain gets its own `1_strategy/` when it has goals distinct from the
enterprise's — not merely a share of them. Most domains do; a purely
internal shared-services domain often doesn't, and inherits the enterprise
strategy instead. Say which.

A domain gets its own `0_business-design/` canvases only when it sells to a
customer segment the enterprise canvases don't already cover.

## Step 4 — Namespace the IDs

Bare inside the owning domain (`BSVC3`), qualified from outside
(`SALES.BSVC3`), bare at the enterprise level (`G1`). Numbering is per
prefix **per domain** — two domains may each own a `BSVC3`. Full rules in
`core-architecture-doc-style` § Element IDs.

The qualifier is the folder name upper-cased, so renaming a domain folder
rewrites every inbound reference. Pick the name once, and prefer the
business's own word for the domain over an invented one.

## Cross-domain changes

**A domain's exposed services are its contract; everything else is
internal.** That yields four rules:

| Situation | What it requires |
| --------- | ---------------- |
| Change inside a domain, touching nothing exposed | The owning domain's Requester only. Most changes |
| Adding a new exposed service | The owning domain's Requester. Nobody depends on it yet |
| Changing or removing an exposed service | **The consuming domains' Requesters at Gate 2 too** — a contract has two sides. Name every consumer in the scope document |
| Referencing another domain's internal element | A modeling error. Either it belongs in that domain's charter, or the dependency shouldn't exist. Take it up with the charter |

When a change spans domains, it is still **one** initiative with one scope
document — but its EA-alignment table names each domain touched, and its
Approvals table carries a Gate 2 row per Requester. Splitting it into one
initiative per domain loses the thing that made it a contract change.

## What this does not do yet

Domain boundaries are what make parallel work by multiple agents safe — one
agent per domain, coordinating only on charters. That isn't set up here.
Doing it well needs a queryable projection of the model so agents can see
each other's work, which the backlog sequences after the graph exporter
(`flow-stack-selection` § The model as data). Until then, work domains one at a
time.
