---
name: answer-architecture-question
description: Procedure — use this when someone wants a focused, human-readable brief about an architecture element, domain, data concern, solution, impact, or decision. Confirms the reader's viewpoint, resolves a model anchor, and generates a disposable Markdown brief from the model.
metadata:
  archreator:
    kind: gated-procedure
    realizes_process: BPROC3.3
    gates: none
---

# ⚙ Answer an architecture question

A reader arrives with a question, not a layer list. Confirm what they need to
understand, centre the question on something the model actually contains, and
generate one disposable brief. The Markdown model remains authoritative; the
brief is a reproducible reading of it.

## ⊕ When to use this

| The situation | What it looks like |
| ------------- | ------------------ |
| Understand one topic | "What do I need to know about this service, domain or component?" |
| Explain architecture to a person | They need a document rather than a graph or repository tour |
| Assess impact | They want the connected chain across the layers for one proposed change |
| Prepare a decision | They need the reason, affected capabilities and material solution impacts together |

## ⊖ When not to

| The situation | Use instead |
| ------------- | ----------- |
| The model is being changed | `align-change-through-layers`; a brief never edits the model |
| The whole model must be published | `model.py portal` — a brief answers one question, a portal carries the model |
| The user asks a precise graph query | `model.py trace` or `model.py coverage` |
| The model is empty or known to be stale | Establish, discover or restate it before presenting a derived answer |

## ⌖ Where this sits

Realizes `BPROC3.3`. It carries **no gate** because it asserts nothing new:
the brief contains declared relationships, catalogue facts and verbatim model
prose. It is generated under `.archreator/work/briefs/`, never committed, and says on its
face that the repository is the model.

## ◈ Invariants

- Confirm the reader's focus before generating, even when one option appears
  likely. Recommend one and make correction easy; do not ask them to choose
  ArchiMate layers.
- Use exactly one focus: `business`, `information`, `solution`, `impact` or
  `decision`. Combined viewpoints are separate briefs.
- Resolve the anchor against the model. Suggest actual names and identifiers
  when the request is ambiguous; never invent an identifier.
- Pass the confirmed focus to the plugin's `build_brief.py` — it ships beside
  the skills, not in the project, and reads a project through `--project`. Do
  not imitate its graph selection or write a competing summary.
- Return the generated Markdown as disposable output. Do not move it into the
  architecture tree or treat it as approved evidence.

## ⚙ Steps

### 1. Confirm the question's focus

Ask: **What should this architecture view help you understand?** Present these
five options in human language, with the inferred option first and recommended:

| Focus | Offer it as | Use when |
| ----- | ----------- | -------- |
| `business` | **Business and operations** | Capabilities, services, actors, processes and why they exist |
| `information` | **Information and data** | Information, ownership, use, flow and the applications managing it |
| `solution` | **Solution and technology** | Applications, integrations, components, platforms and deployment |
| `impact` | **End-to-end impact** | One topic or change traced through every connected layer |
| `decision` | **Decision overview** | The reason, affected capabilities, key impacts and transition |

Recommend `impact` for a change unless the request clearly centres another
question. If the user already chose a focus, confirm it in one sentence rather
than asking the same question again.

### 2. Resolve the anchor and scope

Use the identifier when the user supplied one. Otherwise inspect the model and
offer the closest actual elements, domains or types with both name and ID. Ask
only when more than one candidate would materially change the answer. Add
`--project` when the same identifier exists in more than one model.

Use a two-hop element walk by default. Preserve an explicitly requested depth,
domain, layer or type filter. A focus is presentation and relevance, not a
replacement for the named scope.

### 3. Generate the brief

Run the matching command from the project root. `build_brief.py` lives in the
plugin's `scripts/` — not in the project — and `--project` points it at the
model, for example:

```bash
python3 <plugin>/scripts/build_brief.py --project . --element BSVC1 --depth 2 --focus business
python3 <plugin>/scripts/build_brief.py --project . --element DOBJ4 --depth 2 --focus information
python3 <plugin>/scripts/build_brief.py --project . --domain SALES --focus impact
```

If the view is omitted because the selected scope is too large, narrow the
scope with the user; do not silently choose a different question.

### 4. Hand the reading back

Give the path to the generated brief and state its focus, anchor and boundary.
Remind the reader that it is disposable and should be regenerated after the
model changes. Answer follow-up questions from the model or generate a second
brief with a different confirmed focus.

## ⇥ Hands off to

- `align-change-through-layers` when the answer becomes a requested change.
- `record-decision` when the conversation takes a consequential call that
  needs durable rationale.
- The reader, when the brief answers the question without changing the model.

## ⚠ Anti-patterns

- Asking "which layers?" instead of what the reader wants to understand.
- Selecting every layer just in case.
- Inferring an anchor identifier from a name without checking the model.
- Generating before confirming the focus.
- Summarizing or editorializing model prose inside the disposable brief.
- Committing a generated brief as architecture content.

## ☑ Done when

- The user confirmed one of the five focuses.
- The anchor or scope resolves to model content and any ambiguity is settled.
- `build_brief.py` ran with the confirmed `--focus` and relevant scope flags.
- The output names its focus, scope, depth, emphasis and boundary.
- The user receives the disposable brief and knows the repository remains the model.
