# Adopting ArChreator

_[Repository README](../README.md) · [The method](./method.md)_

## Install the plugin

### Claude Code

```console
/plugin marketplace add roanboc/archreator
/plugin install archreator@archreator
```

### GitHub Copilot

```console
copilot plugin marketplace add roanboc/archreator
copilot plugin install archreator@archreator
```

### OpenAI Codex

```console
codex plugin marketplace add roanboc/archreator
codex plugin add archreator@archreator
```

### Other skill-capable agents

Clone this repository and make the ten skill folders under
`plugins/archreator/skills/` available through the agent's skill directory.
Copy the files under `plugins/archreator/scaffold/` only when establishing a
model in a repository that does not already have equivalent entry files.

## Start or refresh a model

Ask the agent to model the initiative, solution, domain or enterprise. The
`model-context` skill creates or refreshes `architecture/README.md`, identifies
the model boundary and creates only the layer content needed for the request.

In an existing repository, ArChreator preserves unrelated files and does not
replace the project README. In a repository with architecture documentation,
it first determines which facts remain current and which structure is useful.

## Use the runtime directly

The runtime is optional for people and useful for repeatable checks:

```console
python plugins/archreator/scripts/archreator.py --repo . check
python plugins/archreator/scripts/archreator.py --repo . trace ACMP1 --direction both --depth 2
python plugins/archreator/scripts/archreator.py --repo . work --name impact-order-service
python plugins/archreator/scripts/archreator.py --repo . portal
```

The commands always read current Markdown. See the
[runtime guide](../plugins/archreator/scripts/README.md).

## Generated outputs

Scopes, briefs and their PDFs live under `.archreator/work/<run>/`. The portal
lives under `.archreator/work/portal/`. Both locations are ignored and created
only on request. See [Portal use](./portal.md).
