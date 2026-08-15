---
name: core-project-bootstrap
description: Use when a project has the archreator method available but no model yet — there is no architecture/ folder, CLAUDE.md or README.md still contain placeholder markers, architecture/ holds only layer READMEs, or the user says they just installed the plugin, cloned or generated the repository and wants to start. Emits the scaffold, walks the first-commit checklist, assesses and announces the modeling depth, and hands off to the right discovery track. Not needed once CLAUDE.md declares a depth.
---

# Bootstrapping a project from the template

_`README.md` is the human-facing version of this
checklist; `CONTRIBUTING.md` is the method it
leads into._

This skill is the bridge between an installed method and a modeled project:
it **emits the scaffold**, turns it into *this* project, declares how deeply
the project intends to model itself, and hands off to discovery. Everything
after that is the normal `core-architecture-first-change` process — there is no separate
"template mode" to graduate out of.

The scaffold ships beside the skills, at `templates/` inside the plugin. Nothing is inherited by cloning, so nothing has to be pruned
afterwards: the project gets exactly the empty model, and the method stays
where it was installed.

**Run this before anything else on a fresh project.** An agent that skips
straight to `core-architecture-first-change` will find placeholder strategy, trigger
discovery, and produce a strategy layer for a project that still has no
name, no declared language, and no declared depth.

## Step 1 — Find out what is being built, and how deep to model it

Ask, don't infer. Two questions carry the whole step:

1. **What is this project?** One or two sentences in the Requester's own
   words.
2. **What is the subject — an application, or an organization?** Something
   being built, or the way a business works?

From the answers, pick a depth from
`architecture/README.md` § Modeling depth:

| The Requester describes | Depth |
| ----------------------- | ----- |
| An app, a tool, a site, a service they're building | **1 — Application** |
| A company, a department, or a service line whose way of working is the deliverable | **2 — Organization** |
| Several business lines that need to be understood separately | **3 — Enterprise** |

**Then say it out loud, with the reason and the exit.** This is the whole
point of the step:

> "You're building one application, so I'll treat this as **Depth 1** — a
> light strategy layer (goals and principles, enough to judge changes
> against), no business-model canvases, and one approval gate before code.
> If this turns into modeling how the business works, say so and we'll
> deepen it — that's a normal change, not a restart."

Never pick silently. A Requester who is told can correct you in one
sentence; a Requester who is told nothing finds out three initiatives later.

**When in doubt, go shallower.** Deepening is a normal initiative;
unwinding an over-modeled project means throwing away documents the
Requester already approved.

## Step 2 — Emit the scaffold, then make it this project

**First, copy the scaffold** from `templates/` in the plugin into
the project root. It holds `CLAUDE.md`, `README.md`, `architecture/` — with
`architecture/scope/` and `architecture/decisions/` inside it — and
`scripts/`, the two validators that keep the model honest. An empty model
with every layer README in place, and the checks that enforce it. Copy it
whole; the checklist below replaces the placeholders, and Step 3 sets the
layers to the declared depth.

The scaffold is the only thing that lands. The method itself stays where the
plugin installed it, which is why there is nothing of archreator's to delete
afterwards.

Then, in one pass, so the first commit is coherent:

1. **`CLAUDE.md`** — the real project name and description, the layout, the
   commands, and the **declared modeling depth** (`core-architecture-first-change` Step 1a
   reads it on every subsequent change). This file is the agent entry point;
   leaving placeholders in it is what makes later sessions guess.
2. **`README.md`** — the project's own front door. What it is, who it's for,
   how to run it. Not archreator's README with names swapped.
3. **Documentation language** — decide once, note it in `CLAUDE.md`. English
   is the template's default. If it's another language, `core-architecture-doc-style`
   requires a stereotype-correspondence table in `architecture/README.md` so the
   ArchiMate vocabulary stays traceable.
4. **`CONTRIBUTING.md` § Development workflow** — fill in once a stack
   exists; leave the TEMPLATE comment until then rather than inventing
   commands.
5. **Optional files** — keep `architecture/scope/open-questions.md` only if there's
   a stakeholder who can't be consulted synchronously; keep
   `architecture/decisions/` only if the project will make enough
   architecture-significant calls to justify a log. Delete either otherwise;
   both can come back later.

## Step 3 — Set the scaffold to the declared depth

All six layer folders stay, at every depth. What changes is their **declared
state**: a layer the project isn't filling in yet gets "not started" in its
README table, not a deletion. An unfilled layer is a known gap; a missing
folder is an unknown one.

- **Depth 1** — leave `0_business-design/` and `domains/` empty and say so.
- **Depth 2** — `0_business-design/` gets filled by discovery; `domains/`
  stays empty.
- **Depth 3** — read `architecture/domains/README.md` and use the
  `discover-domain-modeling` skill; the enterprise level is modeled first, domains
  after.

If no stack is chosen yet and this is a small application, use
`flow-stack-selection` rather than re-deriving one, and record the choice in
`architecture/5_technology/1_technology-services.md`.

## Step 4 — Hand off to discovery

Bootstrap does not write the strategy — discovery does, with the Requester,
against gates. Hand off by depth:

| Depth | Next |
| ----- | ---- |
| 1 | `discover-strategy` — a light pass. Stakeholders, drivers, goals, and the Principles that will gate every later change. Ends at **Gate 1** |
| 2 | `discover-operating-model` — the canvases first, **Gate 0**, then `discover-strategy` derives the strategy from them, **Gate 1** |
| 3 | `discover-operating-model` for the enterprise, then `discover-domain-modeling` per business line |

Discovery is a full initiative: it gets scope document `1_...md` in
`architecture/scope/`, indexed in `architecture/scope/README.md`, created before its gate.
That is the project's first initiative and the reason the index isn't empty
on day one.

When discovery finishes, the request that started all this — "build me X" —
is still unbuilt. Say so, and offer to open it as the next initiative.

## Done when

- `CLAUDE.md` and `README.md` contain no `<placeholder>` markers, and
  `CLAUDE.md` declares the modeling depth.
- The documentation language is decided and recorded.
- The scaffold has been copied out of the plugin's `templates/` and the optional files
  are kept or deleted deliberately.
- Every layer README's table says either what exists or "not started".
- Scope document `1_...md` exists and is indexed.
- `python3 scripts/check_links.py` and `python3 scripts/check_model.py`
  both pass. They came with the scaffold, so every project has them from
  its first commit.
