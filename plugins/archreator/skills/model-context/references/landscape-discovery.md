# Landscape discovery

Use this route when an organization, domain or solution already operates but
its current business, information, application or technology context is
missing, unreliable or too incomplete for the question at hand. This is a
baseline exercise, not a change or target-state design.

Do not use it for a greenfield subject, a single requested change, or a model
that merely needs stale facts refreshed. Model only as far as the current
purpose requires, and declare where the sweep stopped.

## Inputs

- the model boundary and authoritative owner;
- existing architecture and relevant parent or peer models;
- repositories, deployment configuration and operational evidence in scope;
- process material, contracts, inventories and reports; and
- access to people who can resolve material conflicts the evidence cannot.

## Discovery sequence

1. **Bound the sweep.** State the included organizations, domains, products,
   geographies, environments and externally operated services. Name explicit
   exclusions and ownership elsewhere. If the boundary contains several
   independently accountable business lines, assess domain boundaries before
   describing one tangled estate.
2. **Collect evidence before recollection.** Inspect repositories and deploy
   configuration, licence and invoice lists, identity-provider or single
   sign-on entries, runbooks, on-call ownership, incident history, existing
   process material, reports and dashboards. Interviews then resolve intent,
   ownership and conflicting sources.
3. **Reconcile the evidence.** Differences between inventories are findings,
   not noise. Record which source supports a fact and mark an unknown owner,
   missing artifact or contradictory description as a specific gap. Never
   select the most plausible answer silently.
4. **Describe business and information.** Identify actors and roles, offered
   services, end-to-end processes, business objects, rules, information
   concepts, ownership, lifecycle and movement. Build process and capability
   catalogues breadth first; decompose only where a named pain or decision
   needs it. Include AI and hybrid actors with their authority and escalation.
5. **Describe application and technology.** Identify applications,
   components, services, interfaces, integrations, platforms, runtimes,
   deployment and operational ownership. Ground each element in an observable
   repository path, running service, tenant, contract, team or specific gap.
6. **Connect the layers.** Declare the relationships that explain who uses or
   realizes a service, where information is handled, what applications
   support work and what technology hosts them. An inventory without these
   relationships is not yet useful architecture context.
7. **Declare coverage.** Say what was examined, what was unavailable, what is
   owned elsewhere and where evidence remains inconsistent. Stop at the agreed
   boundary rather than sweeping until questions disappear.
8. **Resolve only material uncertainty.** Ask a focused human question when a
   gap or inconsistency would change ownership, meaning, impact or the answer
   the model is meant to support. Present the evidence, choices, consequences
   and recommendation. Apply the answer to the model and discard the
   conversation around it.

## Judgement tests

- Current evidence wins over an old diagram, while the disagreement remains a
  gap until its significance is understood.
- Describe an awkward or duplicated estate as it runs; improvement belongs in
  a roadmap or later change.
- A department is not automatically a process, and a repository is not
  automatically an application component.
- Similar names are not proof of one element; different names are not proof of
  several. Consolidate only when identity and responsibility agree.
- A partial baseline is valid when its boundary and coverage are explicit.
- Detail below the level needed by the current question must earn its cost.

## Outputs

Create only areas with supported local content under
`architecture/2_business/` through `architecture/5_technology/`. Update
`architecture/README.md` so each area is Local, External, Out of scope or a
specific Gap, and link every local canonical document.

For the modeled boundary, retain:

- supported elements and their owners or explicit ownership gaps;
- traversable relationships with a plain-language meaning;
- source or grounding evidence where a claim needs checking;
- coverage and unavailable context; and
- inconsistencies that remain material to later questions or changes.

Keep raw source material only when it is useful and appropriate to retain;
do not publish private evidence through the portal by default. Do not create
empty layer files, generic pending rows or a mandatory approval record.

## Anti-patterns

- Inventing a requirement so an existing estate can be modeled as a change.
- Recording an organization chart as its process model.
- Rationalizing, renaming or hiding awkward systems while describing them.
- Assigning an owner because a team probably owns the system.
- Treating a licence list or repository list as a complete application model.
- Decomposing every process to the same depth.
- Hiding exclusions so partial coverage appears complete.
- Recording personal interpretations of people rather than verifiable facts,
  constraints or disagreements.
