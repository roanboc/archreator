# Schemas

_[← Skills](../skills/README.md)_

The three [AIP](https://github.com/zach-blumenfeld/aip) schemas the skills
validate against. A skill's YAML body must conform to one of them, and a schema
must itself conform to the AIP base — so a skill that drops a gate, invents a
field or misnames one fails before any agent reads it.

A schema covers a **category** of skill, never a single skill. Fourteen skills
share three schemas, which is what makes the corpus queryable: "every procedure
whose steps write to disk without a gate" is one question over typed fields
rather than fourteen readings.

| Schema | For skills that | Required beyond the AIP floor |
| ------ | --------------- | ----------------------------- |
| [`gated-procedure`](./gated-procedure.schema.json) | Run a sequence of steps under human approval | `steps` |
| [`document-template`](./document-template.schema.json) | Specify a document rather than a procedure | `output`, `sections` |
| [`rulebook`](./rulebook.schema.json) | Are consulted rather than run — conventions and decision aids | `rules` |

Every schema carries the AIP floor: `purpose`, and a `trigger_when` with at
least one entry.

## What each adds

**`gated-procedure`** types the approval gate, which upstream AIP leaves as
freeform prose. A `gate` on a step names who approves, what they are shown,
where the approval is recorded, and the condition under which the gate does not
apply. Its presence is what makes a step stop and wait for a person; a step
without one is the agent proceeding on its own judgement. Alongside it,
`realizes_process` binds the skill to the [process model](../../../docs/process/README.md),
`invariants` holds rules that apply across every step rather than at one, and
`hands_off_to` records a switch to another skill that is not an exit.

**`document-template`** types where a document lands, the sections it carries,
and whether it is a historical record whose words may not later change.

**`rulebook`** gives every rule an `id`, a `rationale`, and an optional
`enforced_by`. That last field is the useful one: its absence says the rule
holds by good intentions alone, and the corpus can be asked how many do.

## Checking them

```bash
uv run .aip/scripts/validate_schema.py plugins/archreator/schemas/gated-procedure.schema.json
```

`.aip/` is a checkout of the pinned AIP release. The validators derive the
expected spec version from their own sibling `SKILL.md`, so the whole release
is checked out rather than the scripts alone — cherry-picking makes the
version check pass without doing anything.

The bundled copy of a schema inside a skill's `source/` is what that skill
validates against, and it is the same file as the one here.
