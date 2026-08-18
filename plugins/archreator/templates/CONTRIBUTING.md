# Contributing

<!--
  TEMPLATE — `establish-project` fills in § Development workflow once a
  stack exists. Keep § Actors: the skills reference it by name, and a project
  whose roles are unwritten has gates nobody can grant.
-->

How changes are made in this project. The rule that governs them and the
declared modeling depth are in [`CLAUDE.md`](./CLAUDE.md); the model itself
is in [`architecture/`](./architecture/README.md).

## Actors

Every change moves through three roles. Nothing here assumes a human fills
the middle one — an AI agent and a person follow the same steps, in the same
order, against the same documents.

| Role | Who | Does |
| ---- | --- | ---- |
| **Requester** | \<who owns the product> | Says what should change — a requirement or a problem, not a diff. **Grants the gate approvals** before any code is written |
| **Agent** | An AI agent (or a person) | Aligns the change through the architecture layers, stops at each gate for the Requester's approval, writes a scope document, implements, and opens a PR |
| **Reviewer** | \<who reviews and merges> | Reviews and merges. Nothing ships without a human approving it |

Which gate applies when is defined once, in the `align-change-through-layers`
skill — this page does not restate it. An approval that isn't recorded didn't
happen: every gate is written into the scope document's Approvals table, with
who approved, when, and what was shown.

## Development workflow

<!--
  TEMPLATE — `establish-project` leaves this until the project has a
  stack. Fill in the real lint/typecheck/test/build commands then, rather
  than inventing them now.
-->

**\<placeholder> — no stack chosen yet.** The two validators already apply,
and must be green before pushing; CI runs the same:

```bash
python3 scripts/check_links.py    # relative links and HTML anchors resolve
python3 scripts/check_model.py    # element-ID references resolve
```

## Pull requests

The body covers the whole branch (`git diff main...HEAD`), not just the
latest commit; links the initiative's scope document; and gives every
affected architecture layer a verdict, including an explicit "no change".
A pure bug fix states what broke, the root cause, and the fix.
