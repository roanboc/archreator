# Source — `establish-project`

What this skill was compiled from, and the calls made while compiling it.

| File | What it is |
| ---- | ---------- |
| [`original-SKILL.md`](./original-SKILL.md) | The freeform markdown skill this replaced, kept verbatim |
| [`gated-procedure.schema.json`](./gated-procedure.schema.json) | The bundled copy of [the canonical schema](../../../schemas/gated-procedure.schema.json), which `check_skills.py` keeps byte-identical |

## Why `gated-procedure`

The skill is a sequence with an accountable actor and a handoff, which is the
shape that schema types. It carries **no gate of its own** — bootstrapping
writes into a project where nothing was ever approved, so there is nothing to
approve against. The first approval belongs to the discovery it hands off to.

That makes it the right first conversion: it exercises the graph, the actors,
the handoffs and `applies_at_depth` without depending on the gate field, which
`discover-business-model` proves separately.

## Script or prose

**No step is script-backed, and that is deliberate.** AIP's test is whether a
step's logic is a fixed rule over structured input or a judgement over a
loosely-specified one.

- **The depth decision** is the clearest case for prose. It maps a Requester's
  sentence onto one of three depths, which is exactly the "interpreting or
  judging the input" case AIP says not to script. It is a prose step with
  `one_of` and the criteria in `analysis`.
- **Emitting the scaffold** is a file copy whose destination and pruning vary
  per project, and whose optional-file decisions are judgement.
- **Clearing placeholders** could be checked mechanically, but the check
  already exists downstream: `done_when` names `check_links.py` and
  `check_model.py`, which ship with the scaffold and run in the project.

Adding a script here would restate a check the project already owns.

## The four-bucket completeness check

Walked line by line against `original-SKILL.md`.

**Mapped** — the two opening questions, the depth table, the say-it-out-loud
rule, "when in doubt go shallower", the scaffold contents, the five-item
first-commit checklist, the depth-by-depth layer states, the discovery handoff
table, the closing-the-loop reminder, and the whole `Done when` list.

**Schema gap** — none. The one addition made while compiling was `scenarios`,
which already existed in the schema.

**Body drop, then recovered** — the original's quoted announcement of a depth
decision was compressed into an invariant on the first pass, losing the
wording an agent should actually use. It is restored as the first entry under
`scenarios`, where a worked example belongs.

**Deliberate drop** — the opening navigational note (`README.md` is the
human-facing version of this checklist; `CONTRIBUTING.md` is the method it
leads into). It describes the document's surroundings rather than the work,
and `architecture-document-style` § What the document contains rules that out.
The relationship it described is not lost: the scaffold's own `README.md` and
`CONTRIBUTING.md` are `produces` entries on the steps that write them.
