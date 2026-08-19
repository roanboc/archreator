---
name: stack-selection
description: Rulebook — consult when bootstrapping a new project and no technology stack has been chosen yet, when assessing architecture/5_technology/ for a small application, or when deciding whether the model needs a persisted projection. Gives a decision framework and concrete defaults rather than re-deriving the choice from scratch each time.
metadata:
  archreator:
    kind: rulebook
    gates: none
---

# ※ Stack selection

Guidance for **deciding**, not a substitute for the technology layer itself.
Once a choice is made it is documented, with its reasoning, in
`architecture/5_technology/1_technology-services.md` as usual.

It exists because for a small or solo project the honest answer to "what
should we build this on" is almost always one of a handful of well-worn
combinations, not a bespoke evaluation.

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
| A concrete requirement rules the defaults out | Compliance, unusual compute or real scale beats any default here. Record the call with `record-decision` |
| The project is not a small application | These defaults are calibrated for small and solo projects, and stop being defaults above that |

## ⌖ Where this sits

**Realizes no process.** It is a decision aid reached for inside `BPROC2.2`,
and by `establish-project` when a project has no stack yet. Nothing here is a
step; the output is a choice, recorded where choices are recorded.

## ※ Rules

### Start with the decision tree

1. **Does the app need to store or mutate shared state at all** — multi-user
   data, anything outliving a single browser session?
   - **No** → it is a static site or tool. Skip everything about databases and
     auth. This is the cheapest, simplest and most secure option there is;
     do not add a backend "just in case".
   - **Yes** → continue.
2. **Does it need user accounts or access control?**
   - Where the database choice already bundles auth with row-level policies,
     default to that rather than a separate provider — one less moving part,
     and one less place for the permission model to drift from the data model.
   - Otherwise pick a standalone auth provider.
3. **How much infrastructure control does the project actually need?** Small
   apps essentially never need any. Default to managed and serverless, and
   revisit only when a specific concrete requirement demands otherwise.

### No backend — static only

Build to static files, ship on a free static host. Zero servers to secure,
zero ongoing cost, zero uptime to babysit.

| Need | Default | Alternatives |
| ---- | ------- | ------------ |
| Hosting | **GitHub Pages** — versioned with the code, free, trivial Actions deploy | Cloudflare Pages (faster edge, still free), Netlify |

Right for tools, demos, docs sites, and anything whose state is fully
client-side. No server means nothing to secure, patch, or pay to keep running.

### Needs a backend — data, users, or both

| Need | Default | When to reach for the alternative |
| ---- | ------- | --------------------------------- |
| **Database, auth and row-level access control** | **Supabase** — managed Postgres, built-in Auth, Row-Level Security enforced by the database rather than application code, generous free tier | **Firebase** where the data is naturally document-shaped and prototyping speed beats relational integrity; **PlanetScale** or **Neon** where you want only the database because auth already exists |
| **Auth only** | **Auth.js** where self-hosting is fine and the framework is Next.js | **Clerk** for the fastest setup and best out-of-box components, at the cost of a third-party dependency and its own free-tier limits |
| **App hosting and deploy** | **Vercel** for Next.js — zero-config, preview deployments per pull request | **Netlify** as a framework-agnostic equivalent; **Cloudflare Pages** for the cheapest and fastest option at real scale |
| **CI** | **GitHub Actions**, already assumed by `write-pr-description` and the deployment conventions | — |

**The reference combination** for a typical small app with users and real
data is **Next.js + Vercel + Supabase**. Vercel handles hosting and CI/CD
through its GitHub integration; Supabase provides Postgres with Row-Level
Security as the single point of access-control enforcement. Document the
role-by-operation mapping in the business layer once the roles are known, so
the policies stay traceable to that matrix.

### The model is Markdown, and the default is to derive nothing

The Markdown under `architecture/` is the **source of truth**: it is what the
Requester approves at the gates and what review acts on.

**The default is to derive nothing from it.** The graph is already implicit in
the documents, `grep` traverses it, and an agent reads Markdown natively —
there is no parsing gap to close for the reader the model is written for. A
derived store is a second representation that can fall behind the first, which
is exactly the drift the one-fact-one-place rule exists to prevent.

What *is* needed is **validation**, and validation needs a parse rather than a
store. `check_model.py` builds the graph in memory, checks that every
reference resolves and no identifier is reused, and exits. Nothing persists,
so nothing goes stale. This is the failure agents are worst at unaided: an
agent reading `relieves GAIN2` cannot cheaply tell that `GAIN2` was deleted
three initiatives ago, and will reason confidently from the stale reference.

### A persisted projection needs one of four triggers

Reach for one only when one of these is actually true — and record the call
with `record-decision`.

| Trigger | Why it changes the answer |
| ------- | ------------------------- |
| The model no longer fits in one context read | An agent that must query rather than read needs something to query |
| Domains live in separate repositories | Federation needs an interchange format; an agent cannot `grep` a repository it has not cloned |
| A genuinely **transitive** question recurs | "Blast radius of retiring `CAP3`" is a traversal, not a lookup. A one-off is a script, not infrastructure |
| A non-agent consumer appears | A dashboard, a report or a rendered model cannot read Markdown tables |

When that day comes the default is **SQLite**, as a `nodes`/`edges` pair
traversed with recursive CTEs. At the scale a model reaches — hundreds of
elements, edges in the low thousands, traversals a few hops deep — SQLite *is*
the graph database, and `sqlite3` ships with Python.

```sql
CREATE TABLE nodes(id TEXT PRIMARY KEY, type TEXT, layer TEXT,
                   name TEXT, doc TEXT, realized_by TEXT);
CREATE TABLE edges(src TEXT, dst TEXT, rel TEXT);  -- realizes, serves, …
```

The projection is regenerated, never hand-edited, and `check_model.py` already
extracts what it would need. Consistent element IDs are what make it
mechanical rather than a parsing exercise, which is the reason to use them
from the first document.

Dedicated **embedded** graph databases are worth knowing about only once
SQLite has actually stopped being enough: [LadybugDB](https://ladybugdb.com/),
the maintained successor to Kuzu — embedded, columnar, Cypher, interoperating
with DuckDB, Arrow and Parquet; [GraphLite](https://github.com/GraphLite-AI/GraphLite),
Rust, embedded, implementing the ISO **GQL** standard; and
[ArcadeDB](https://arcadedb.com/embedded.html), embeddable on the JVM.
**Kuzu itself was archived in October 2025** after its team was acquired —
existing releases still run, but do not adopt it for new work. Both active
successors are young enough that betting an organization's shared model on one
is a real risk.

### The principles behind the defaults

- **Managed over self-hosted.** A small app's traffic and data volume
  essentially never justifies operating a server, a database or a cluster
  yourself. Reach for that only when a concrete, articulated requirement
  demands it — never as a default posture.
- **Free tier first.** Vercel, Supabase, Netlify, Cloudflare Pages and GitHub
  Actions all have free tiers generous enough for a small app's entire
  lifetime pre-scale.
- **Fewer moving parts beats more control.** A bundled database-and-auth
  product that removes an entire class of drift — auth logic disagreeing with
  data-access logic — is usually worth more than the flexibility of wiring the
  two together yourself.
- **Whatever is chosen, record it and the reasoning.** This skill helps you
  decide quickly; the technology layer document is what stays true and
  verifiable over the life of the project.

## ✎ Worked example

> A two-person team wants a booking tool with logins. Step 1 says shared
> state, step 2 says accounts — so Supabase rather than a separate auth
> provider, because Row-Level Security keeps the permission model in the same
> place as the data. Step 3 finds no infrastructure requirement, so Vercel.
> Next.js + Vercel + Supabase, recorded in `1_technology-services.md` with the
> role-by-operation matrix that the policies will be traceable to.

## ⚠ Anti-patterns

- Adding a backend to something whose state is fully client-side, "just in case".
- Wiring a separate auth provider to a database that already bundles one.
- Committing to paid infrastructure before there is a concrete reason.
- Projecting the model into a database because it would be tidy, rather than
  because one of the four triggers fired.
- Hand-editing a projection instead of regenerating it.
- Choosing a stack and leaving the reasoning in a chat rather than in the
  technology layer.
