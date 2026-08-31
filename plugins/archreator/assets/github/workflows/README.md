# Workflows, available and switched off

_[← The scaffold](../../README.md)_

Two workflow files that **do not run where they are**. The automation host
reads `.github/workflows/` and nothing else, so a file here is text until
somebody moves it one directory up.

That is deliberate. A pipeline that turns red on a project's first push
teaches a team that the checks are noise, and one that publishes a model
nobody agreed to publish cannot be un-published. So the scaffold ships both
switched off, and `establish-project` moves what the answer to *where does
this project live?* selects.

| File | Activate it when | What it needs first |
| ---- | ---------------- | ------------------- |
| [`checks.yml`](./checks.yml) | The project is on GitHub, public or private | Nothing. Both validators are Python standard library |
| [`publish-docs.yml`](./publish-docs.yml) | The project is on a **public** GitHub repository | Pages switched on: Settings → Pages → Source: GitHub Actions |

## Switching one on by hand

Bootstrap normally does this. To do it later — the project moved to GitHub,
or Pages was enabled after the fact:

```bash
mkdir -p .github/workflows
git mv .github/workflows-available/checks.yml .github/workflows/
```

Then delete this directory once nothing in it is still wanted. Nothing reads
it, and a directory of files that look like they run is worse than no
directory.

## Not on GitHub

Delete `.github/` whole. It holds this directory, the pull-request template
and the question form, and all three are GitHub-shaped. The model, the
validators and the portal are not: `scripts/check_links.py`,
`scripts/check_model.py` and `scripts/build_docs.py` run anywhere Python
does, which is what a pipeline on any other host would call.
