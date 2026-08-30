# ArChreator runtime

`archreator.py` reads the Markdown under `architecture/` each time it runs. It
does not build or retain a second model.

An element definition catalogue begins with
`ID | Name | ArchiMate type | Description`; the ID comes first so definitions
remain easy to order. Everywhere an element is referenced—prose, relationships,
diagrams, briefs and process content—write the visible name and identity together
as `Order service [ACMP1]`. A relationship table therefore uses
`From | Relationship | To | Meaning` with `Name [ID]` in both endpoint cells;
`Meaning` may be empty.

Bare IDs are not document references. They are accepted only as explicit query
arguments, such as the `ACMP1` passed to `trace`. IDs must contain a number, such
as `CAP1`, `ACMP2.1` or `sales::SERVICE3`. Relationships come only from
relationship tables, except same-type hierarchy: a dotted-ID child's `Parent`
cell declares its Composition relationship.

Every canonical file below `architecture/README.md` has an H1 and a
`**Location:**` line. A nested element such as Order validation [BPROC2.2]
must have a `Parent` column containing Fulfil customer demand [BPROC2]; the
parent ID must match the child ID with its final numeric segment removed.

## Commands

Run the script from any project by pointing `--repo` at its root:

```console
python plugins/archreator/scripts/archreator.py --repo . check
python plugins/archreator/scripts/archreator.py --repo . trace ACMP1 --direction both --depth 2
python plugins/archreator/scripts/archreator.py --repo . work --name decision-payment-provider
python plugins/archreator/scripts/archreator.py --repo . pdf .archreator/work/decision-payment-provider/decision.md --kind brief
python plugins/archreator/scripts/archreator.py --repo . portal
```

`check` reports noncanonical element catalogues, duplicate and invalid element
IDs, missing page orientation, missing or inconsistent parent references,
malformed relationship endpoints, stale visible reference names, and broken
relative Markdown links or anchors.

`trace` walks declared relationships from an element. `forward` follows
outgoing relationships, `reverse` finds what depends on the element, and
`both` does both. The result is a short Markdown table whose element references
also use `Name [ID]`, suitable for a person or an agent.

`work` creates `.archreator/work/<run>/` and ensures `/.archreator/work/` is in
the repository `.gitignore`. Generated scopes, decision briefs, impact briefs,
understanding briefs and their exports belong there. Nothing creates this
folder before it is requested.

`pdf` exports one requested scope or brief. Its Markdown input and PDF output
must both be inside `.archreator/work/`; the command cannot point at
`architecture/` and cannot publish the whole model. PDF export is the only
optional feature and needs ReportLab:

```console
python -m pip install reportlab
```

`portal` builds the optional, human-facing site only when requested. Its output
is `.archreator/work/portal/index.html`. Use `--source-base-url` when links back
to the repository cannot be detected automatically.

## Python API

The same file can be imported without installing a package:

```python
from archreator import build_portal_output, ensure_work_directory, export_pdf, load_model, trace

model = load_model(".")
affected = trace(model, "ACMP1", direction="reverse", depth=3)
work = ensure_work_directory(".", "impact-acmp1")
```

`load_model` always returns a new `Model`. The useful values are
`model.elements`, `model.relationships` and `model.issues`. No call requires a
build step.

## Tests

```console
python -m unittest discover plugins/archreator/scripts/tests
```

The PDF test skips cleanly when ReportLab is not installed.
