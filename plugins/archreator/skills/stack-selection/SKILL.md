---
name: stack-selection
description: Rulebook — consult when a new project has no technology stack yet, when assessing 5_technology/ for a small application, or when deciding whether the model needs a persisted projection. The decision framework and the criteria, never a list of named products.
disable-model-invocation: true
metadata:
  archreator:
    kind: rulebook
    gates: none
---

# ※ Stack selection

Guidance for **deciding**, not a substitute for the technology layer itself.
Once a choice is made it is documented, with its reasoning, in
`architecture/5_technology/1_technology-services.md`.

**This rulebook names no products**, and neither does a project that follows
it without checking. It carries the shape of the decision and the criteria a
candidate is judged against; the current answer is found each time.

## ⊕ When to use this

| The situation | What it looks like |
| ------------- | ------------------ |
| No stack chosen | `establish-project` reached Step 3 and `5_technology/` is empty |
| Assessing the technology layer | A change touches `5_technology/` on a small application |
| Considering a derived store | Someone is asking whether the model should be projected into a database |

## ⊖ When not to

| The situation | Use instead |
| ------------- | ----------- |
| The stack is chosen and documented | `align-change-through-layers` — a change to it is an ordinary change |
| A concrete requirement rules the framework out | Compliance, unusual compute or real scale beats anything here. Record the call with `record-decision` |
| The project is not a small application | These criteria are calibrated for small and solo projects |

## ⌖ Where this sits

**Realizes no process.** A decision aid reached for inside `BPROC2.2`, and by
`establish-project` when a project has no stack yet. The output is a choice,
recorded where choices are recorded.

## ※ Rules

### Start with the decision tree

1. **Does the app need to store or mutate shared state at all** — multi-user
   data, anything outliving a single browser session?
   - **No** → it is a static site or tool. Skip everything about databases and
     auth, and do not add a backend "just in case".
   - **Yes** → continue.
2. **Does it need user accounts or access control?**
   - Where one product covers both the data and its access control, and
     enforces the rules in the store rather than in application code, prefer
     it: one less place for the permission model to drift from the data model.
   - Otherwise pick a standalone auth provider.
3. **How much infrastructure control does the project actually need?** Small
   apps essentially never need any. Default to managed and serverless, and
   revisit only when a specific concrete requirement demands otherwise.

### Find the current answer, and date it

The tree says what the project needs. What meets that need is a question about
this year, so answer it now rather than from memory:

- **Read what the ecosystem publishes about itself** — a framework's own
  deployment documentation names the paths it is tested on.
- **Take a repository's build configuration as evidence, and an article as
  none.** What comparable projects run beats what is written about them.
- **Check maintenance before capability.** An archived project keeps its
  documentation, its benchmarks and its search ranking. Read release dates and
  open-issue response, not the README.
- **Read the pricing page on the day you decide.**

**Record the date, the alternatives and the sources** alongside the choice: a
technology decision with no date is one nobody can re-evaluate.

### The criteria a candidate is judged against

| Criterion | The question |
| --------- | ------------ |
| **Coverage** | Does one product cover data and access control together, enforced in the store? Every boundary between products is a place two models can disagree |
| **Operation** | Is it managed? Run a server, a database or a cluster yourself only when a concrete requirement demands it |
| **Cost at this size** | Does its free or lowest tier cover the project's foreseeable life? |
| **Moving parts** | How many services must agree for a request to succeed? Fewer beats more control on a small project |
| **Maintenance** | Is it actively released and answered? A young successor to an abandoned project is a real risk, not a neutral one |
| **Exit** | Is the data in a portable format, and is the access-control model reproducible elsewhere? |

### The model is Markdown, and the default is to derive nothing

The Markdown under `architecture/` is the **source of truth**: it is what the
Requester approves at the gates and what review acts on.

**The default is to derive nothing from it.** The graph is already implicit in
the documents, `grep` traverses it, and an agent reads Markdown natively. A
derived store is a second representation that can fall behind the first.

What *is* needed is **validation**, and validation needs a parse rather than a
store. `check_model.py` builds the graph in memory, checks that every
reference resolves and no identifier is reused, and exits. Nothing persists,
so nothing goes stale.

### A persisted projection needs one of four triggers

Reach for one only when one of these is actually true — and record the call
with `record-decision`.

| Trigger | Why it changes the answer |
| ------- | ------------------------- |
| The model no longer fits in one context read | An agent that must query rather than read needs something to query |
| Domains live in separate repositories | Federation needs an interchange format; an agent cannot `grep` a repository it has not cloned |
| A genuinely **transitive** question recurs | "Blast radius of retiring `CAP3`" is a traversal, not a lookup — but see below |
| A non-agent consumer appears | A dashboard, a report or a rendered model cannot read Markdown tables |

**The third trigger has a cheaper answer than it looks.** archreator answers
its own transitive question — what a change to one element would touch — by
parsing the Markdown fresh on every run, which on the largest model built on it
takes well under a second. **A store you have to remember to rebuild is a store
that will be wrong.**

So reach for a projection when the parse is genuinely too slow, or when the
fourth trigger fires and something outside the repository has to read it:

```bash
model.py --project . export     # .model/model.json, which nothing here reads back
```

**An unfamiliar reader is not that consumer.** The fourth trigger is about
something that has to *query* the model — a dashboard computing coverage, a
report counting what a change touches. Someone who only has to read it wants
the documents rendered, which needs no projection at all: `model.py portal`
writes a stock MkDocs config and the documents publish as a website, straight
from the Markdown.

Whatever a projection is written into, three things keep it from becoming the
second source of truth this section warns about: it is **regenerated** from
scratch on every run, it is **gitignored**, and **nothing reads it that could
have read the Markdown instead**.

`model.py inventory` is worth knowing about before a trigger fires: diffing the
inventory of two commits says which elements a large edit added, dropped or
renamed.

## ✎ Worked example

> A two-person team wants a booking tool with logins. Step 1 says shared
> state, step 2 says accounts — so a product covering both data and access
> control, over a database and a separate auth provider, because the
> permission model then lives where the data does. Step 3 finds no
> infrastructure requirement, so managed and serverless. The agent checks what
> currently meets that in this framework's ecosystem, against the criteria
> above, and records the choice in `1_technology-services.md` with the date,
> what else was considered, and the role-by-operation matrix the access rules
> will be traceable to.

## ⚠ Anti-patterns

- Adding a backend to something whose state is fully client-side, "just in case".
- Wiring a separate auth provider to a database that already bundles one.
- Committing to paid infrastructure before there is a concrete reason.
- Naming a product from memory rather than checking what it is today.
- Recording a technology choice with no date, so nobody can tell what it was
  true of.
- Projecting the model into a database because it would be tidy, rather than
  because one of the four triggers fired.
- Hand-editing a projection instead of regenerating it, or committing one.
- Reading the projection for something the Markdown would have answered.
- Choosing a stack and leaving the reasoning in a chat rather than in the
  technology layer.
