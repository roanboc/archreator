# Actors: human, AI, and hybrid

_Reference for [`architecture-document-style`](../SKILL.md) § What is here, and what is one file away._

Read this when populating `2_business/1_business-actors-and-roles.md`, or
whenever a role might be performed by an AI system.

`«Business Actor»` and `«Business Role»` nodes name **who** — and in a
system where an AI can hold a role, "who" is no longer implicitly human.
State the actor's kind as `(Human)`, `(AI)`, or `(Hybrid)` (a human and an AI
sharing one role, e.g. a co-pilot pattern). It rides on the node itself —
`⚇ Requester (Human) [ACT1]` — which is the one exception to § ArchiMate on
Mermaid's rule that a content node carries no type word; the legend writes it
against the stereotype, `⚇ «Business Actor (Human)»`. Default to `(Human)`
only when the actor is provably never an AI system acting with delegated
authority — don't omit the qualifier to save space.

When populating `2_business/1_business-actors-and-roles.md`, explicitly
ask, for every role: **does an AI system perform or assist this role, and
at what autonomy?** — don't let "actor" default to human by omission. For
every `(AI)` or `(Hybrid)` actor, the actors table carries three extra
columns beyond the usual name/description:

| Column | Answers |
| ------ | ------- |
| Autonomy level | One of: **advisory** (suggests, a human decides and acts), **co-pilot** (acts, a human reviews before it takes effect), **autonomous with checkpoint** (acts independently, a human is notified and can intervene after the fact), **fully autonomous** (acts independently, no routine human checkpoint) |
| Decision rights | What this actor is actually authorized to decide or change, in concrete terms — not "helps with X" |
| Escalation path | Who/what it hands off to when it's outside its authority or confidence — a Business Role, not a vague "a human" |

If an initiative changes an AI actor's autonomy level or decision rights,
that's exactly the kind of call the `record-decision` skill is for.

## An actor earns its row by acting

**A supplier the organization only depends on is not an actor.** A platform,
a hosting service, a model provider — it fills no role in this model and
decides nothing in it, so it gets no `ACT` row: it is a key partner where a
canvas exists, a contract on the business layer, and a node on the
technology layer, and those three carry everything true about it. The test
is the role column: an actor whose row cannot name a role it fills or
assists in is a dependency wearing the wrong stereotype.

