# Contributing

Contributions should make ArChreator easier to understand, navigate or use in a
real change. Complexity must earn its place through observed customer value.

## Before changing the method

Describe the customer problem and the simpler behavior that resolves it. Check
the change against both routes: a builder using guidance and an enterprise
architect navigating directly. Do not add an artifact, instruction or runtime
dependency merely to represent a possible future use case.

## Repository expectations

- Keep the typed skill surface small and discriminating. A new skill needs a
  distinct activation boundary, process binding and output contract.
- Add project files lazily; never restore empty layer scaffolding.
- Preserve the Markdown element and relationship contract.
- Keep generated scopes, briefs, PDFs and portals out of source control.
- Do not add SQLite, cached graph state or whole-model PDF export.
- Treat federation implementation as evidence-led work.

## Checks

Run the commands in [AGENTS.md](./AGENTS.md#validation). Add focused tests for
observable behavior rather than exact generated wording. A pull request should
explain the customer effect, complexity added or removed, and verification.
