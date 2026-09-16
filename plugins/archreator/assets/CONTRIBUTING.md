# Contributing

<!--
  TEMPLATE — `establish-project` fills in § Development workflow once a
  stack exists. Keep § Actors: the skills reference it by name, and a project
  whose roles are unwritten has nobody to merge anything.
-->

How changes are made in this project. The rule that governs them and the
declared modeling depth are in [`AGENTS.md`](./AGENTS.md); the model itself
is in [`architecture/`](./architecture/README.md).

## Actors

Every change moves through three roles. Nothing here assumes a human fills
the middle one — an AI agent and a person follow the same steps against the
same documents.

| Role | Who | Does |
| ---- | --- | ---- |
| **Requester** | \<who owns the product> | Says what should change — a requirement or a problem, not a diff, in plain words |
| **Agent** | An AI agent (or a person) | Aligns the change through the architecture layers, writes a scope document, builds directly from the request, and opens a PR — stopping only for a contradiction, an ambiguity, or something needing authorization |
| **Reviewer** | \<who reviews and merges> | Reviews and merges. The merge is the approval; nothing ships without it |

What stops the work, and how it's presented, is defined once, in the
`align-change-through-layers` skill § Where this stops — this page does not
restate it.

## Development workflow

<!--
  TEMPLATE — `establish-project` leaves this until the project has a
  stack. Fill in the real lint/typecheck/test/build commands then, rather
  than inventing them now.
-->

**\<placeholder> — no stack chosen yet.** The three validators already apply,
and must be green before pushing; CI runs the same:

```bash
python3 scripts/check_links.py    # relative links and HTML anchors resolve
python3 scripts/check_model.py    # element-ID references resolve
python3 scripts/check_prose.py    # every model page speaks about its subject
```

## Questions from outside the repository

The model can also be read as a website, generated on request rather than
published on merge — see the archreator method's `docs/adopting.md`. It is a
rendering: the Markdown in this repository stays the model.

If the published site carries comment threads, a thread is a conversation
about a document and never the record of a change. Those questions are triaged
like anything else a Requester says: one that turns out to be a change becomes
an initiative and is built and merged like any other. **Answering in the thread
and nowhere else leaves the model exactly as wrong as it was.**

## Pull requests

The body covers the whole branch (`git diff main...HEAD`), links the
initiative's scope document, and gives every affected architecture layer a
verdict, including an explicit "no change". A pure bug fix states what broke,
the root cause, and the fix.
