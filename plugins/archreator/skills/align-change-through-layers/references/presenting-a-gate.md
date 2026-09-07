# Presenting a gate

_Reference for [`align-change-through-layers`](../SKILL.md) § The gates. Read it
before a gate is presented._

## Where a gate happens

| Surface | Use it when |
| ------- | ----------- |
| **The conversation** | The Requester is in the session with you |
| **A pull-request comment** | The Requester is not in the session, or the approval should be reviewable by others. The reply *is* the record |
| **A published view of the model** | Stakeholders read the model but never open GitHub. Only once the project publishes a site |

Whichever surface is used, the approval is transcribed into the Approvals table
with its date and what was shown.

## Show the Requester what they are approving

**Every gate presentation carries full clickable links to the exact content
under review** — one per document, resolving to the branch the work is on, not
to the default branch:

```
https://github.com/<owner>/<repo>/blob/<branch>/<path>
```

Not a repository-relative path, not a file name, not "see the canvases": an
approval granted against a summary is an approval of the summary. Link the
branch, never the default branch, and give one link per document rather than a
link to a folder. In a pull-request comment write the full URLs — GitHub
renders relative links there inconsistently.
