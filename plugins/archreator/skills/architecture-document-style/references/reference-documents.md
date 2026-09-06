# Reference documents

_Reference for [`architecture-document-style`](../SKILL.md) § What is here, and
what is one file away._

Read this when adding source material to `architecture/reference/`, or writing
anything down from a meeting.

`architecture/reference/` holds the material the model was built from, exactly
as it was provided: meeting transcripts, presentations, specifications,
spreadsheets, whatever somebody sent. **It is not part of the model.** Nothing
in it defines an element or carries an identifier, and the validators do not
read it — a transcript in which somebody says `CAP3` is a person talking, not
a definition. It exists so that a claim in the model can be taken back to what
it came from.

**Naming.** `YYYY-MM-DD-<short-description>.<ext>`, in plain ASCII with
hyphens — `2026-08-24-operations-review-transcript.md`,
`2026-03-02-target-operating-model.pptx`.

The date is, in order of preference: **when the meeting happened**; failing
that, **when the document was shared**; failing that, **when it was added to
the repository**. Take the first one that can be established, and say which in
the index when it is not the first.

**The original filename is preserved in the index, not on disk.** A file
called `BigView Strategy FINAL v3.pptx` keeps that name in a column where it is
searchable and matches the sender's copy; on disk it becomes a dated slug,
because spaces and capitals in a path break links and tooling.

**Every file gets a row in `architecture/reference/README.md`**: the date and
what fixed it, the original name, who provided it, and what in the model was
derived from it. A reference document nothing derives from is still worth
keeping and its row says so.

**Reference documents are not published.** The portal and the PDF exist to
hand a reader the model; a raw transcript carries everything else that was in
the room that day, to an audience that was not.

## A summary of a meeting records facts, not judgements

**Write down what can be checked**: decisions taken, constraints stated,
numbers quoted, systems and teams named, dates, owners, what somebody
committed to, what was explicitly left open.

**Do not write down readings of people**: who seemed frustrated, who is
difficult to work with, whose team is disorganised, what a tone implied, who
appeared not to understand their own process. Nor the emotional weather of the
room — tension, resistance, enthusiasm — as though it were a finding.

A judgement is unfalsifiable, so nobody can correct it, and a repository keeps
it: long after everyone has forgotten the meeting, the sentence is still there,
searchable, attached to a named person.

Where a difficulty is real and architecturally relevant, it is written as what
it is: a constraint, a risk, an assessment, a driver — an `ASM` or a `DRV`
element with a source, not an aside about somebody. "Two teams disagree on who
owns customer data" is a finding. "Team A is territorial" is not.

**Nothing checks this.** No validator can tell a fact from a judgement. It is a
rule a writer follows and a reviewer reads for.

