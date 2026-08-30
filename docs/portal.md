# Portal use

_[Repository README](../README.md) · [Adopting ArChreator](./adopting.md)_

The portal is a supported human interface to the canonical architecture. Use
it when someone needs search, visual navigation, a shareable static site, or a
clearer surface for explaining architecture to business readers.

## Build it on request

```console
python plugins/archreator/scripts/archreator.py --repo . portal
```

The command reads the current repository and writes
`.archreator/work/portal/index.html`. It does not create project configuration,
SQLite, a graph projection or PDF output.

Preview it with any static file server:

```console
python -m http.server 8000 --directory .archreator/work/portal
```

## Publish it

Publish the generated directory to a static host only when a real audience,
privacy boundary and accountable owner are known. Add host-specific
configuration at that time; it does not belong in every project scaffold.

The portal is derived output. Every architecture claim must resolve to the
canonical Markdown, and rebuilding must replace rather than accumulate stale
pages. Raw reference material is not published unless the owner explicitly
puts it in scope.

## PDF boundary

The complete model is consumed in the repository or portal. PDF export applies
only to a requested temporary scope or focused brief under
`.archreator/work/<run>/`.
