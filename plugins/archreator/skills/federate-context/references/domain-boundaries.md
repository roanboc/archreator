# Domain boundaries

Use this reference when an enterprise model may need separately accountable
domains, when adding a real domain, or when a question or change crosses an
existing domain boundary. Do not split a single solution, a small organization
or a team merely to mirror an organization chart.

Federation connects independently useful models. It does not turn one model
into a copy of the others, and it does not require a central platform before a
real cross-model use case proves one necessary.

## Inputs

- the enterprise or parent model and the facts it owns;
- the candidate domain's customers, economics, decisions and capabilities;
- known services other parts of the organization consume;
- accountable owners and affected consumers; and
- the concrete cross-domain question or change that makes the boundary useful.

## Decide whether a domain exists

A domain should behave like a business within the larger business. Assess
whether it has:

1. its own customers, internal or external;
2. distinct economics, funding or value accountability;
3. meaningful decision rights exercised inside the boundary;
4. capabilities that form a coherent purpose; and
5. a named interface: services or contracts others can consume.

Normally at least two tests should hold, and these two questions must have
credible answers:

- **What does the domain expose?** If nothing stable can be named, the
  proposed boundary gives other models nothing to depend on.
- **Who can say yes inside it?** If every meaningful decision escalates out,
  the boundary has no operational authority.

State the verdict and the tests that support it. Ask for human resolution only
when conflicting evidence or unclear authority would materially change the
boundary. Do not create a domain folder to preserve an undecided possibility.

## Write the charter and authority boundary

The domain's front door is its charter. Keep it concise and include only facts
that make the domain independently understandable:

- purpose and the larger outcome it serves;
- accountable owner and decision rights;
- customers and what they need;
- facts and capabilities the domain owns;
- enterprise direction or shared facts it inherits rather than restates;
- exposed services or contracts and what realizes them;
- consumed services or contracts and their owning models;
- escalation for decisions outside the domain's authority; and
- related enterprise, peer and solution models.

For AI or hybrid operation, name autonomy, concrete decision rights and a
human or organizational escalation role. An exposed service without a real
owner or realization is a specific gap, not an aspiration presented as a
contract.

## Preserve ownership and contracts

- One model owns each element definition. Other models link to it and may
  refine what it explicitly exposes; they do not restate it.
- A domain owns its outgoing relationship assertions. Incoming relationships
  are derived from their source models when those models are available.
- Other domains may depend on exposed contracts, not internal processes,
  resources or implementation detail.
- Adding an exposed service needs authority from its owner. Changing or
  removing one must identify affected consumers and obtain any material
  authorization those contracts require.
- A cross-domain change remains one connected change with every affected owner
  and repository visible. Splitting it into unrelated local changes hides the
  contract impact.

## Qualify identifiers

Use identifiers that remain readable without requiring global numbering:

| Context | Anchor inside the human-first reference | Example reference |
| --- | --- | --- |
| Inside the owning domain | Local ID | Order service [BSVC1] |
| Elsewhere in the same multi-domain model | Domain-qualified ID | Order service [SALES.BSVC1] |
| From another model | Model and optional domain qualification | Order service [customer-platform::SALES.BSVC1] |

The domain namespace precedes the element prefix; numeric segments after the
prefix retain hierarchical meaning, such as Validate an order
[SALES.BPROC2.1]. The model name comes from the related-model entry in
`architecture/README.md`. Do not invent globally unique numbering or reference
an undeclared model.

Every cross-model relationship keeps its direction, canonical ArchiMate
relationship where one fits, plain-language meaning, owning source and target
revision when available. If the target cannot be read, report unavailable
context rather than treating it as absent.

## Outputs

Create a domain model or charter only after the boundary is useful and carries
real content. Update the participating front doors with authority, parent,
peer or child relationships and direct source navigation. Record exposed and
consumed contracts as traversable relationships, plus specific unresolved
ownership or evidence gaps.

A lower-level model refines exposed context. It may add its own goals,
services, information representations, components and runtime detail, but it
must link back to the parent fact rather than duplicate its description.

## Defer transport

Use accessible Markdown and direct links for the first real cases. Do not add
a registry, central graph, SQLite database, automatic cloning, remote fetch,
replication, cache or mandatory synchronization schema in anticipation of
scale. Let an observed enterprise-domain-solution use case determine transport,
authentication, freshness and failure handling.

An on-demand portal may combine readable models, but it must preserve each
source, revision and authority boundary and show unavailable context. It is a
view, not the federation authority.

## Anti-patterns

- Treating teams or reporting lines as domains without customers or contracts.
- Writing domain layers before the charter reveals a useful interface.
- Exposing a service that consumers should not safely build against.
- Reaching through another domain's contract to its internal elements.
- Copying enterprise facts into every domain or solution.
- Hiding a contract change inside separate repository changes.
- Designing transport, registries or synchronization before a real use case
  supplies their requirements.
