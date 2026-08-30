# Architecture

This page is the front door to the initiative or business modeled in this
repository. Replace the bracketed values when the model is established.

## Model boundary

| Field | Current value |
| --- | --- |
| Name | [Name the model] |
| Purpose | [State what this model helps people understand or change] |
| Level | [Enterprise, Domain, or Solution] |
| Accountable owner | [Name the accountable person or role] |
| Parent model | None, or [model name and source] |
| Documentation language | English |

## Architecture status

A layer is **Local** when this repository owns its content, **External** when a
named parent or related model owns it, **Out of scope** when it is not needed,
and **Gap** when it is needed but not yet understood. A local layer links to its
`README.md`; no folder exists for the other states.

| Order | Concern | Status | Location or owner |
| --- | --- | --- | --- |
| 0 | Business design | [Status] | [Local file, external model, reason, or gap] |
| 1 | Strategy | [Status] | [Local file, external model, reason, or gap] |
| 2 | Business | [Status] | [Local file, external model, reason, or gap] |
| 3 | Information | [Status] | [Local file, external model, reason, or gap] |
| 4 | Application | [Status] | [Local file, external model, reason, or gap] |
| 5 | Technology | [Status] | [Local file, external model, reason, or gap] |
| 6 | Transition | [Status] | [Local file, external model, reason, or gap] |

## Related models

List only models this one currently depends on or exposes a contract to. Keep
transport and storage choices out until a real federation use case requires
them.

| Model | Level | Owner | Source | Relationship |
| --- | --- | --- | --- | --- |
| [Model name] | [Level] | [Owner] | [Repository or accessible source] | [What this model consumes or exposes] |
