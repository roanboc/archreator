# Contributing

Contributions to **archreator itself** — changes to the skills, the
scaffold, the documentation, or the plugin manifests in this repository.
For an explanation of the method that these files publish, see
[`docs/method.md`](./docs/method.md); for using it in your own project, see
[`docs/adopting.md`](./docs/adopting.md).

## What kind of change is this?

| Kind | Where the record lives |
| ---- | ---------------------- |
| **A change to the method** — new skill, new rule, changed convention, a scaffold refactor | A numbered scope document in [`architecture-archreator`](https://github.com/roanboc/architecture-archreator) under `product-archreator/architecture/scope/`, plus the corresponding change here |
| **A bug fix** with no documented behavior change — a broken link, a typo, a validator false positive | Straight to a PR here; say what broke, the root cause, and the fix |
| **A docs improvement** to the guidance under `docs/` or `site/` | A PR here; short scope note in the PR body if the doc changes what the method claims |
| **A packaging or CI change** — plugin manifest, workflows, `.github/` | A PR here |

The split reflects federation. This repository holds *the method as it
ships*; the sibling repository holds *the models that describe why the
method is what it is*. A method change without a scope document is a
change without a rationale — the rationale lives where the model does.

## The method governs itself

Method changes run through the same gates the method makes downstream
projects run through. In practice:

- **Gate 2 — Business** applies to every change that alters documented
  behavior — every one that touches a skill body, a rule, or the scaffold.
  It is granted in the sibling repository's scope document, then
  implemented here.
- **Gate 1 — Strategy** applies when the change adds or shifts a
  Stakeholder, Driver, Goal, or Principle of the method itself.
- **Gate 3 — Solution design** is the Requester's option at Gate 2.

Pure bug fixes skip the gates, per the method's own rule.

## Working locally

All three validators must be green before pushing; CI runs the same:

```bash
python3 plugins/archreator/templates/scripts/check_links.py    # relative links and HTML anchors resolve
python3 plugins/archreator/templates/scripts/check_model.py    # element-ID references resolve
python3 plugins/archreator/scripts/check_skills.py             # the skill corpus against the process model
```

The first two live under `plugins/archreator/templates/` because they ship with
the scaffold — the same scripts land in every project the method emits. Running
them from the root of this repository is a smoke test: since there is no
`architecture/` folder here, `check_model.py` reports the scaffold as having no
elements and passes trivially, while `check_links.py` checks the docs, the
scaffold, and the site.

`check_skills.py` sits outside `templates/` because a downstream project has no
skills to check. It reads the process model in [`docs/process/`](./docs/process/README.md)
and the skill bodies, and needs PyYAML only once those bodies are YAML — use
`uv run` in place of `python3` where it is not installed.

Skills and schemas are also validated against the pinned
[AIP](https://github.com/zach-blumenfeld/aip) release, which CI checks out into
`.aip/`. To run those locally, clone the same release and point the validators
at your working copy:

```bash
git clone --depth 1 --branch v0.3a3 https://github.com/zach-blumenfeld/aip .aip
uv run .aip/scripts/validate_schema.py plugins/archreator/schemas/gated-procedure.schema.json
uv run .aip/scripts/validate.py plugins/archreator/skills/<a-converted-skill>
```

Clone the release whole rather than copying `scripts/` out of it: the
validators read their sibling `SKILL.md` to derive the expected spec version,
and without it that check passes without doing anything.

## Pull requests

One template for every change:
**[`.github/pull_request_template.md`](./.github/pull_request_template.md)**.
The body links the scope document in the sibling repository (if the change
needed one), gives every affected surface a verdict, and describes the whole
branch (`git diff main...HEAD`), not just the latest commit. For a pure bug
fix, say what broke, the root cause, the fix, and any regression coverage.

The [`write-pr-description`](./plugins/archreator/skills/write-pr-description/SKILL.md)
skill keeps the body current.

## Conventions

- **Conventional Commits** (`feat:`, `fix:`, `docs:`, `chore:`, …).
- **Documentation language:** English.
- **Skill folder names** are a verb and an object for a skill you run, a noun
  phrase for one you consult — see [`plugins/archreator/skills/README.md`](./plugins/archreator/skills/README.md).
- **A merged scope document is a historical record** — link targets get
  repaired when files move; the words never change (`RULE6`).
