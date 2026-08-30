# Strategy discovery

Use this route when the model has no reliable strategy context, or when new
evidence materially changes stakeholders, drivers, goals, principles,
capabilities or the value stream. If an organization has no usable business
design, run business-model discovery first. If supported business design
exists, derive from it and ask only about what it leaves open.

For an existing strategy, refresh rather than restart: retain what remains
true, remove what no longer does and concentrate on contradictions, missing
evidence and the change that triggered the work.

## Inputs

- the model boundary, level, owner and parent context;
- supported business-design facts when the business is in scope;
- existing strategy documents and decisions;
- relevant obligations, constraints and observable operating evidence; and
- the outcome or question that made strategy context necessary.

## Discovery sequence

Work theme by theme in small batches. Use the organization's language, reflect
the emerging answer after each theme and consolidate before enumerating.

1. **Stakeholders and drivers.** Who benefits, pays, operates, governs,
   regulates or can stop the work? What pressure matters to each: cost, time,
   risk, obligation, opportunity or service quality? Derive known customers
   and partners from business design instead of asking for them again.
2. **Goals and outcomes.** What must become true for the subject to be worth
   sustaining or changing? How would the accountable person recognize
   success, and what is explicitly not a goal? Prefer observable outcomes over
   activity statements.
3. **Principles and constraints.** What must always or never be true when
   choices are made? Keep principles few, load-bearing and testable. “Role
   determines access” can reject a design; “be secure” cannot.
4. **Capabilities and resources.** What must the subject be able to do, and
   what people, information, systems, funding or partnerships enable it? For
   an organization, use the process-and-capability rules: an industry
   reference may propose a catalogue, but only evidence or an accountable
   person can confirm it.
5. **Value stream.** From the first stakeholder need to the outcome received,
   what stages create value and which capabilities support each stage? A
   stage without a beneficiary or capability is a gap to examine.
6. **Key business context.** Identify only the actors, roles, services,
   processes, business objects, contracts, rules and shared terms needed to
   make the strategy coherent. For AI or hybrid actors, state autonomy,
   concrete decision rights and escalation.
7. **Test coherence.** Trace goals to drivers and stakeholders, principles to
   choices they constrain, value stages to capabilities, and capabilities to
   resources or an explicit gap.

## Judgement tests

- A goal states a result, not the project or activity intended to produce it.
- A principle earns its place only when it can rule a plausible option in or
  out.
- Two elements that differ only in wording or degree should be consolidated.
- Product- or domain-specific strategy refines enterprise direction; it does
  not restate it.
- Business-design evidence is an input, not an instruction to copy every
  canvas element into strategy.
- Ask for human resolution only when missing or inconsistent meaning would
  materially change direction. Show the relevant evidence, interpretations,
  consequences and a recommendation rather than asking a broad architecture
  question.

## Outputs

Create only the strategy documents that carry supported facts under
`architecture/1_strategy/`. Keep them small enough to navigate directly and
split them only when a subject is independently useful or owned.

The resulting context should make visible:

- stakeholders and the drivers that matter to them;
- goals and observable outcomes;
- the few principles and constraints that govern choices;
- capabilities, resources and real gaps;
- the value stream and the capabilities supporting its stages; and
- links to the key business facts needed to understand the strategy.

Link sources or named decisions beside claims that need provenance. Update the
front door and ownership boundary. Keep future plateaus and initiative
sequences in `architecture/6_transition/`, not in the current strategy files.
Do not create empty catalogues or require a fixed approval record.

## Anti-patterns

- Asking questions already answered by supported business design.
- Filling strategy with what projects of this kind usually want.
- Twenty goals or principles that no later decision can realistically test.
- Capabilities written as activities, or processes presented as capabilities.
- A value stream that ends with internal completion rather than stakeholder
  value.
- Copying enterprise facts into a domain or solution model.
- Building solution detail before a material contradiction in direction has
  been resolved.
