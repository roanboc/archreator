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

This repository holds *the method as it ships*; the sibling repository
holds *the models that describe why the method is what it is*, which is
where a method change's rationale belongs.

## The method governs itself

Method changes run through the same gates the method makes downstream
projects run through. In practice:

- **Understanding** applies to every change that alters documented
  behavior — every one that touches a skill body, a rule, or the scaffold.
  It is granted in the sibling repository's scope document, then
  implemented here.
- **Direction** applies when the change adds or shifts a
  Stakeholder, Driver, Goal, or Principle of the method itself — and when an
  initiative sets a direction rather than building one.

Pure bug fixes skip the gates, per the method's own rule.

## Working locally

All three validators must be green before pushing; CI runs the same:

```bash
python3 plugins/archreator/scaffold/scripts/check_links.py    # relative links and HTML anchors resolve
python3 plugins/archreator/scaffold/scripts/check_model.py    # element-ID references resolve
python3 plugins/archreator/scripts/check_skills.py             # the skill corpus against the process model
```

The first two live under `plugins/archreator/scaffold/` because the same
scripts land in every project the method emits. Run from this repository's
root they are a smoke test: there is no `architecture/` folder here, so
`check_model.py` passes trivially while `check_links.py` checks the docs, the
scaffold, and the site.

`check_skills.py` sits outside `scaffold/` because a downstream project has no
skills to check. It reads the process model in [`docs/process/`](./docs/process/README.md)
and every skill's frontmatter and headings against
[the skill format](./docs/skill-format.md). It needs PyYAML — use `uv run` in
place of `python3` where that is not installed.

## Pull requests

One template for every change:
**[`.github/pull_request_template.md`](./.github/pull_request_template.md)**.
The body links the scope document in the sibling repository (if the change
needed one), gives every affected surface a verdict, and describes the whole
branch (`git diff main...HEAD`). For a pure bug fix, say what broke, the root
cause, the fix, and any regression coverage.

The [`write-pr-description`](./plugins/archreator/skills/write-pr-description/SKILL.md)
skill keeps the body current.

## Conventions

- **Conventional Commits** (`feat:`, `fix:`, `docs:`, `chore:`, …).
- **Documentation language:** English.
- **Skill folder names** are a verb and an object for a skill you run, a noun
  phrase for one you consult — see [`plugins/archreator/skills/README.md`](./plugins/archreator/skills/README.md).
- **Skills follow a fixed format** — frontmatter, sections and glyphs are
  specified in [`docs/skill-format.md`](./docs/skill-format.md), and
  `check_skills.py` enforces it.
- **A merged scope document is a historical record** — link targets get
  repaired when files move; the words never change (`RULE6`).
