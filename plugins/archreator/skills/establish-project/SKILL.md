---
name: establish-project
description: Use when a project has the archreator method available but no model yet — there is no architecture/ folder, CLAUDE.md or README.md still contain placeholder markers, architecture/ holds only layer READMEs, or the user says they just installed the plugin, cloned or generated the repository and wants to start. Emits the scaffold, walks the first-commit checklist, assesses and announces the modeling depth, and hands off to the right discovery track. Not needed once CLAUDE.md declares a depth.
metadata:
  aip:
    spec: https://github.com/zach-blumenfeld/aip/tree/v0.3a3
    schemaId: https://github.com/roanboc/archreator/schemas/gated-procedure.schema.json
---

```yaml
purpose: >
  Bridge an installed method and a modeled project. Emit the scaffold, turn it
  into this project, declare how deeply the project intends to model itself,
  and hand off to discovery. Everything after that is the ordinary
  align-change-through-layers process; there is no separate template mode to
  graduate out of.

trigger_when:
  - A project has the method available but no architecture/ folder.
  - CLAUDE.md or README.md still contain <placeholder> markers.
  - architecture/ holds only layer READMEs and no elements.
  - The user says they just installed the plugin, cloned or generated the repository, and wants to start.

do_not_use_when:
  - CLAUDE.md already declares a modeling depth — the project is bootstrapped, and a change goes through align-change-through-layers.
  - The request is a change to an existing model rather than a first setup.

realizes_process:
  - BPROC1.1

applies_at_depth: [1, 2, 3]

invariants:
  - >
    Run this before anything else on a fresh project. An agent that skips
    straight to align-change-through-layers finds placeholder strategy,
    triggers discovery, and produces a strategy layer for a project with no
    name, no declared language and no declared depth.
  - >
    Ask, do not infer. The two questions in the first step are answered by the
    Requester in their own words, not guessed from the repository.
  - >
    The scaffold is the only thing that lands. The method stays where the
    plugin installed it, which is why there is nothing of archreator's to
    delete afterwards.
  - >
    Never pick the depth silently. A Requester who is told can correct you in
    one sentence; a Requester who is told nothing finds out three initiatives
    later.

scope_and_approval: >
  This procedure writes freely into a project that has no model yet — copying
  the scaffold and replacing its placeholders needs no gate, because nothing it
  overwrites was ever approved. It carries no gate of its own. The first
  approval belongs to the discovery it hands off to, at Gate 0 or Gate 1.

steps:
  - name: establish-subject-and-depth
    description: >
      Ask what the project is, in one or two sentences, and whether the subject
      is an application being built or an organization whose way of working is
      the deliverable. Pick a modeling depth from those answers, then state it
      out loud with its reason and its exit.
    actor: Agent
    analysis: >
      An app, tool, site or service being built is Depth 1. A company,
      department or service line whose way of working is the deliverable is
      Depth 2. Several business lines needing to be understood separately is
      Depth 3. Depth is about the subject, not the effort — a large application
      is still Depth 1. When in doubt go shallower: deepening is a normal
      initiative, while unwinding an over-modeled project throws away documents
      the Requester already approved.
    one_of:
      - 1 — Application
      - 2 — Organization
      - 3 — Enterprise
    outputs:
      - name: declared-depth
        type: integer
        description: The depth, stated to the Requester with its reason and how to change it later.
      - name: project-description
        type: string
        description: What the project is, in the Requester's own words.

  - name: emit-the-scaffold
    description: >
      Copy the scaffold whole from templates/ in the plugin into the project
      root — CLAUDE.md, README.md, CONTRIBUTING.md, architecture/ with scope/
      and decisions/ inside it, and scripts/ with the two validators.
    actor: Agent
    inputs:
      - name: declared-depth
        type: integer
    produces:
      - CLAUDE.md
      - README.md
      - CONTRIBUTING.md
      - architecture/
      - scripts/
    outputs:
      - name: scaffold-in-place
        type: boolean

  - name: make-it-this-project
    description: >
      In one pass, so the first commit is coherent: fill CLAUDE.md with the real
      name, description, layout, commands and the declared depth; write
      README.md as the project's own front door rather than archreator's with
      names swapped; decide and record the documentation language; leave
      CONTRIBUTING.md § Development workflow as its TEMPLATE comment until a
      stack exists; and keep or delete the optional files deliberately.
    actor: Agent
    inputs:
      - name: scaffold-in-place
        type: boolean
      - name: project-description
        type: string
    analysis: >
      The optional files are a judgement, not a default. Keep
      architecture/scope/open-questions.md only where a stakeholder cannot be
      consulted synchronously, and architecture/decisions/ only where the
      project will make enough architecture-significant calls to justify a log.
      Delete either otherwise; both can come back later. If the documentation
      language is not English, architecture-document-style requires a
      stereotype-correspondence table in architecture/README.md so the ArchiMate
      vocabulary stays traceable.
    produces:
      - CLAUDE.md
      - README.md
    outputs:
      - name: placeholders-cleared
        type: boolean

  - name: set-the-layers-to-the-depth
    description: >
      All six layer folders stay at every depth. Set each layer README's table
      to what exists or to "not started" — an unfilled layer is a known gap, a
      missing folder is an unknown one. At Depth 1 leave 0_business-design/ and
      domains/ empty and say so; at Depth 2 domains/ stays empty and discovery
      fills the canvases; at Depth 3 the enterprise level is modeled first and
      domains after.
    actor: Agent
    inputs:
      - name: declared-depth
        type: integer
    produces:
      - architecture/
    outputs:
      - name: layers-declared
        type: boolean

  - name: open-the-first-initiative
    description: >
      Create scope document 1_*.md in architecture/scope/ and index it in
      architecture/scope/README.md. Discovery is a full initiative, and this is
      the project's first — which is why the index is not empty on day one.
    actor: Agent
    uses_template: write-scope-document
    inputs:
      - name: project-description
        type: string
    produces:
      - architecture/scope/
    outputs:
      - name: first-scope-document
        type: string

  - name: hand-off-to-discovery
    description: >
      Hand off by depth, then close the loop: the request that started all this
      is still unbuilt, so say so and offer to open it as the next initiative.
    actor: Agent
    inputs:
      - name: declared-depth
        type: integer
      - name: first-scope-document
        type: string

hands_off_to:
  - skill: discover-strategy
    when: Depth 1 — a light pass over stakeholders, drivers, goals and the Principles that gate every later change.
    returns: A filled 1_strategy/ approved at Gate 1. Bootstrap is finished; the next change re-enters align-change-through-layers.
  - skill: discover-business-model
    when: Depth 2 or 3 — the canvases come first and are approved at Gate 0, before anything is derived from them.
    returns: Approved canvases, which discover-strategy then derives the strategy layer from at Gate 1.
  - skill: model-domains
    when: Depth 3, after the enterprise level is modeled — one charter per business line.
    returns: A domain per business line, each with its exposed and consumed services.
  - skill: stack-selection
    when: No stack is chosen yet and the subject is a small application.
    returns: A recorded choice in architecture/5_technology/1_technology-services.md.

done_when:
  - CLAUDE.md and README.md contain no <placeholder> markers.
  - CLAUDE.md declares the modeling depth.
  - The documentation language is decided and recorded.
  - The scaffold has been copied out of the plugin's templates/, and the optional files are kept or deleted deliberately.
  - Every layer README's table says either what exists or "not started".
  - Scope document 1_*.md exists and is indexed.
  - python3 scripts/check_links.py and python3 scripts/check_model.py both pass — they came with the scaffold, so every project has them from its first commit.

scenarios:
  - need: "\"I want to build a small tool that reformats our export files.\""
    context: The repository is a fresh copy of the scaffold; nothing is filled in.
    action: >
      Depth 1. Announced as: "You're building one application, so I'll treat
      this as Depth 1 — a light strategy layer (goals and principles, enough to
      judge changes against), no business-model canvases, and one approval gate
      before code. If this turns into modelling how the business works, say so
      and we'll deepen it — that's a normal change, not a restart." Then hand
      off to discover-strategy.
    outcome: >
      A named project with a declared depth the Requester could have corrected
      in one sentence, and a first scope document covering the discovery.
  - need: "\"We're three consultants and I want to document how we actually work.\""
    context: The subject is the organization itself rather than anything being built.
    action: >
      Depth 2 — the way the business works is the deliverable, not a side note.
      Hand off to discover-business-model for the canvases at Gate 0 before
      anything is derived from them.
    outcome: A model whose strategy layer is derived from approved canvases rather than guessed.

anti_patterns:
  - Inferring the subject or the depth from the repository instead of asking the Requester.
  - Picking a depth without saying which, why, and how to change it later.
  - Writing the strategy here. Bootstrap hands off to discovery, which does it with the Requester against gates.
  - Deleting a layer folder the project is not filling in yet, rather than marking it "not started".
  - Leaving the Requester's original request unmentioned once discovery finishes, so a docs-only PR reads as the process having failed to build anything.
```
