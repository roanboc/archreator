# Workflows

_[← Assets](../../README.md)_

One workflow, emitted into `.github/workflows/` when the project is on GitHub
and wants CI.

| File | Emit it when | It runs |
| ---- | ------------ | ------- |
| [`checks.yml`](./checks.yml) | The project is on GitHub | `scripts/check_links.py` and `scripts/check_model.py` on every pull request |

**It needs nothing installed.** Both validators are plain Python with no
dependencies, no network and no plugin — which is why they are the two things
the scaffold copies into a project rather than leaving in the method.

There is no publishing workflow. The portal is generated on request, into a
gitignored directory, by whoever wants to read it — see
[`docs/adopting.md`](https://github.com/roanboc/archreator/blob/main/docs/adopting.md).
A pipeline that publishes a model on every merge is a decision about
disclosure, and it should be made deliberately rather than inherited from a
template.
