# ArChreator repository

This repository contains the ArChreator plugin, its minimal project scaffold,
source-fresh runtime and public documentation. Worked customer models belong in
their own repositories.

## Layout

| Path | Purpose |
| --- | --- |
| `plugins/archreator/skills/` | Typed AIP-derived procedures, document templates, rulebooks and lazy discovery references |
| `plugins/archreator/scaffold/` | The files a new model needs before any layer content exists |
| `plugins/archreator/scripts/` | Source-fresh validation, traversal, work-area and scoped PDF commands |
| `plugins/archreator/portal/` | On-demand static portal generation |
| `docs/` | Human explanation, adoption, portal and standards guidance |
| `site/` | Public landing and getting-started pages |

## Product rules

- Humans are the customers. Agents consume the same plain, structured context.
- Independent builders receive guidance; enterprise architects retain direct
  standard navigation and an on-demand portal.
- Customer repositories contain only locally useful architecture artifacts.
  `architecture/README.md` records absent, external and out-of-scope areas.
- Element catalogues begin `ID | Name | …` for stable ordering. Prose,
  relationships, diagrams and briefs reference the element as `Name [ID]`.
- Every canonical file is self-locating. Populated hierarchy levels have
  distinct files and every nested definition names its parent.
- ArchiMate types and relationships are canonical secondary metadata. Names,
  descriptions and visuals lead the reading experience.
- Human decisions are exception-driven: unresolved gaps, inconsistencies,
  material authorization and required acceptance.
- Scopes, briefs and scoped PDFs are ignored work products. Whole-model PDF,
  SQLite, graph projections and compatibility layers do not belong here.
- Federation identity, ownership and contract semantics remain explicit;
  transport and aggregation wait for a real use case.

## Validation

Use the bundled Python runtime or Python 3.11 or later:

```console
python -m unittest discover plugins/archreator/scripts/tests
python -m unittest discover plugins/archreator/portal -p "test_*.py"
python plugins/archreator/scripts/check_method.py
python plugins/archreator/scripts/archreator.py --repo plugins/archreator/scaffold check
python plugins/archreator/scripts/archreator.py --repo plugins/archreator/scaffold portal
```

Run the skill and plugin validators when their development tools are available.
No validation command may create committed output in the scaffold.

## Conventions

- Documentation language is English; filenames remain plain ASCII.
- Use Conventional Commit prefixes.
- Use relative links to a specific file.
- Keep one source for each fact and test any unavoidable copy.
- A document describes its subject, not its drafting history.
