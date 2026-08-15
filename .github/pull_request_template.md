<!--
  PR TEMPLATE LAYOUT — why there are two template files in two places:
  GitHub auto-fills a PR body from ONE default template, which must live at
  .github/pull_request_template.md (this file). Named alternates for the
  "choose a template" flow must live in the .github/PULL_REQUEST_TEMPLATE/
  directory — hence the bug-fix template at
  .github/PULL_REQUEST_TEMPLATE/bugfix.md, selected via ?template=bugfix.md.
  The split is required by GitHub, not an oversight. Which one to use:
  CONTRIBUTING.md and the core-pr-description skill.
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
     product-archreator/architecture/scope/. Its Approvals table records
     the gates the change passed (Gate 2 at minimum for any change in
     documented behavior). If this is a bug fix with no documented
     behavior change, use the bug-fix template instead. -->

## What changed here

<!-- Group by surface. Every commit's work must be represented. -->

- **Skills** — which SKILL.md files, what changed in each
- **Scaffold** — anything under templates/
- **Docs / site** — under docs/ or site/
- **Plugin package / CI** — manifests under .claude-plugin/, workflows

## Verification

<!-- What was run and what happened: -->

```
python3 .claude/templates/scripts/check_links.py
python3 .claude/templates/scripts/check_model.py
```

## Out of scope / follow-ups

<!-- Deliberate exclusions and the gaps they leave — mirror the scope
     document's gap notes. -->
