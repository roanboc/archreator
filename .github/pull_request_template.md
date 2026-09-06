<!--
  PR TEMPLATE LAYOUT — GitHub auto-fills a PR body from ONE default
  template, which must live at .github/pull_request_template.md (this file).
  This repository uses that single default for every kind of change; a pure
  bug fix fills the same body with what broke, the root cause, and the fix.
  How to fill this in: CONTRIBUTING.md and the write-pr-description skill.
-->
<!--
  Describe the WHOLE branch, not just the latest commit:
    git log --oneline main..HEAD
    git diff main...HEAD --stat
  Keep this body updated as the branch gains commits.
-->

## Summary

<!-- 2–4 sentences: what this PR delivers and why. -->

## Scope document

<!-- Link the initiative's scope document in the sibling repository,
     https://github.com/roanboc/architecture-archreator — usually under
     product-archreator/architecture/scope/. Its Approvals table records the
     gates the change was granted (Understanding at minimum for any change in
     documented behavior), and nothing for a gate it was not. A change with no
     documented behavior change — a bug fix, a packaging or CI change —
     states "no scope document" here with the reason. -->

## What changed here

<!-- Group by surface. Every commit's work must be represented. -->

- **Skills** — which SKILL.md files, what changed in each
- **Scaffold** — anything under scaffold/
- **Docs / site** — under docs/ or site/
- **Plugin package / CI** — the plugin and marketplace manifests, workflows

## Complexity

<!-- The method's first principle, asked of every change: what was removed?
     What new recurring cost does this add — a file in the scaffold, a check
     to keep green, a copy to hold together — and why is it justified?
     "Nothing removed, nothing recurring added" is a complete answer. -->

## Verification

<!-- What was run and what happened: -->

```
python3 plugins/archreator/scaffold/scripts/check_links.py
python3 plugins/archreator/scaffold/scripts/check_model.py
uv run plugins/archreator/scripts/check_skills.py
```

## Out of scope / follow-ups

<!-- Deliberate exclusions and the gaps they leave — mirror the scope
     document's gap notes. -->
