# Scripts

_[← Project home](../README.md)_

Two validators that keep this project's architecture documents honest, and
four tools — one for the reader who queries the model, three for the readers a
repository does not reach. They came with the
scaffold, so this project has had them since its first commit, and CI should
run both validators on every pull request.

```bash
python3 scripts/check_links.py    # relative links and HTML anchors resolve
python3 scripts/check_model.py    # element-ID references resolve
python3 scripts/build_model.py    # project the model into .model/
python3 scripts/query_model.py coverage      # what is grounded, and what is not
python3 scripts/query_model.py trace CAP3    # what a change to one element touches
python3 scripts/build_docs.py     # the model as a website, in .docs/site/
python3 scripts/export_pdf.py     # the model as one PDF, in .docs/
```

Both validators exit `0` when everything resolves and `1` otherwise, printing
what failed. The other four are tools rather than gates: nothing has to be
green for them, and nothing breaks if they are never run.

| File | What it is |
| ---- | ---------- |
| `check_links.py` | Executable. Every relative Markdown link and every HTML `href`, `src` and `#fragment` points at something that exists |
| `check_model.py` | Executable. Every backticked element ID resolves to a definition, none is defined twice, none is both live and retired, a levelled ID has its parent defined, every document that defines an element declares how far it has been validated, no relationship table restates an element's name differently from the catalogue that defines it, and every reference that names another model either resolves in this repository or is declared in `architecture/imports.md` |
| `build_model.py` | Executable. Writes `.model/model.json` and `.model/model.db` — the model as nodes and edges, for a rendered view or a report. Every edge carries where it was declared and whether it is pending. `--inventory` prints one line per element instead |
| `query_model.py` | Executable. Reads `model.db` and answers the two questions a table cannot. `trace <ID>` follows relationships outward and says what a change to one element would touch; `coverage` reports what names a realizing artifact, what is explicitly Pending, and what its own catalogue leaves blank beside grounded neighbours. Builds the projection first if it is missing |
| `build_brief.py` | Executable. Writes one disposable Markdown brief into `.docs/briefs/` for a named scope — the elements in it, generated views of how they depend on each other across the layers, and what the documents already say |
| `build_docs.py` | Executable. Stages the documents into `.docs/src/` and builds the portal into `.docs/site/`, publishes this model's projection under `site/projection/`, and reports links pointing at files it does not publish. `--serve` rebuilds as the model is edited. Also the staging hook `mkdocs.yml` runs |
| `export_pdf.py` | Executable. Prints the portal's single-page view to `.docs/architecture.pdf` with a headless browser, and checks that the diagrams were drawn rather than left as source text. What the PDF leaves out is the `print-site` `exclude` list in `mkdocs.yml`; `--config mkdocs-<audience>.yml` exports a second PDF from a config that inherits it |
| `neighbourhood.sql` | Data, read by `query_model.py` **and by `build_brief.py`**. The traversal itself — everything within N hops of one element, as a recursive CTE, walking a model-qualified identifier so it crosses a federation boundary without knowing it did. It is a file rather than a function because two readers execute it, and a walk written twice drifts |
| `model_graph.py` | Library, imported by the others. The single parse of the document convention — element IDs, catalogue tables, relationship tables, and the resolution of a bare identifier inside a domain |
| `element-prefixes.json` | Data, read by `model_graph.py`. The element-ID prefixes and what each stands for |

## Briefs

`build_brief.py` is for a reader with a question about one part of the model.
Name a scope and it writes a single Markdown document into `.docs/briefs/`:
the elements in it, **generated views of how they depend on each other across
the layers**, and the paragraphs the documents already write about them.

```bash
python3 scripts/build_brief.py --element BSVC1 --depth 2
python3 scripts/build_brief.py --domain SALES
```

The walk is `neighbourhood.sql`, the same traversal `query_model.py trace`
runs. The prose is the model's own, carried verbatim - nothing is summarized,
because a paraphrase in a generated document is a claim nobody approved.

**A brief is disposable and says so on its face.** It carries the revision it
was generated from and a line telling a reader that the repository is the
model. It is never committed: `.docs/` is gitignored, and a brief that gets
mailed around and quoted eight months later is the second source of truth this
method exists to prevent.

**A generated view never replaces an authored one.** The layer documents keep
their own diagrams - those are curated selections, and the notation says a
selection that looks complete is worse than several honest parts. A brief adds
the view nobody drew: the chain from business and information down to
application and technology, which lives in no single document.

`build_docs.py` and `export_pdf.py` need MkDocs, which they declare inline:
`uv run scripts/build_docs.py` fetches it into a throwaway environment and
installs nothing. Without `uv`, install it once with
`pip install mkdocs-material mkdocs-print-site-plugin`. The PDF also needs a
Chromium-family browser, and says where the page to print is when there is
none.

## The projection is derived, and stays that way

The Markdown under `architecture/` is the source of truth. `build_model.py`
writes a second representation of it, which is a thing worth being uneasy
about — a derived store that falls behind the source is exactly the drift the
one-fact-one-place rule exists to prevent.

Three things keep it honest. It is **regenerated** from scratch on every run,
never hand-edited. It is **gitignored**, so no stale copy can be committed.
And **nothing reads it that could have read the Markdown instead** — an agent
reads the documents natively, so this exists for the consumers that cannot: a
report, a dashboard, and `query_model.py`, whose traversals are the reason a
graph is worth materializing at all.

Delete `.model/` and nothing is lost.

## So are the portal and the PDF

Everything under `.docs/` is the same arrangement, one level up: `src/` is a
staged copy of the Markdown, `site/` is the portal built from it, and the PDF
is that portal printed. All three are rebuilt on every run, all three are
gitignored, and none of them holds a sentence the documents do not.

The staging keeps every repository path, which is what lets each page in the
portal link back to the file that produced it — the "edit this page" pencil
opens the real Markdown in git, so a reader who disagrees with a page can
change it through the ordinary process. **A rendering nobody can trace back to
its source is how a published copy quietly becomes a second model.**

## `query_model.py` reports; it never fails a build

Every element must name what realizes it. That is the one rule the validators
do not enforce, and deliberately: telling a repository path from a team name is
fuzzy, and a check that fails wrongly teaches people to ignore the checks that
do not.

So `coverage` prints and **always exits 0**. There is no `--strict`, because
adding one would invite exactly the CI gate the reasoning above rules out. It
also judges by catalogue table rather than by element — a table that grounds
none of its rows is not modeling realization at all, and reporting each of its
elements is how a report becomes noise. What it does report is a table that
grounds some rows and leaves others blank, which is an omission rather than a
convention.

## Two folders the tools treat differently

`architecture/reference/` holds source documents as they were provided. The
validators and the projection do not read it — a transcript in which somebody
says an element identifier is a person talking — and the portal and the PDF do
not publish it. A raw transcript carries everything else that was in the room
that day, to an audience that was not.

Because `reference/` is unpublished, a link into it resolves in the repository
and 404s on the site — a draft catalogue citing the transcript it was built
from is the ordinary case. `check_links.py` cannot see that: it proves a link
resolves *here*. So `build_docs.py` reports every staged link pointing at a
file it did not publish, as a note rather than an error. Publishing a partial
view is a legitimate choice; the person making it should know what it costs.

`architecture/scope/`, `architecture/decisions/` and the other narrative
folders are unread for the older reason: a merged scope document is immutable
and will outlive the elements it names, so reference-checking it is incoherent
rather than merely awkward.

## What each one cannot do

`check_model.py` verifies that a *reference* resolves. `check_links.py`
verifies that a *link* resolves. **Neither reads what a "Realized by" cell
claims about a path**, so a cell naming a directory that no longer exists
passes both silently. `query_model.py coverage` finds the cell that is *empty*;
whether a path it names still exists is a step in the change process, not
something these scripts can do for you.

`query_model.py` cannot say what nothing points at. The projection drops a
reference made inside the document that defines the element, so an element
named only by its own neighbours looks unreferenced — and answering the
question properly would mean re-reading the Markdown, which is the one thing a
consumer of the projection should not do.

`build_model.py` reads structure from the identifier, the numbered folder and
the notation — all of which survive translation, so it works the same on a
model written in any language. **The one exception is its `realized_by`
column**, which has to guess which heading names a realization and is empty
when it cannot. The full row is always in `attrs`, so consult that rather than
trusting the guess. It also reports rows where the cell after the ID does not
look like a name, which is a finding about the document rather than an error.

## `element-prefixes.json`

It is data, not configuration — regenerated from the method rather than
hand-edited. Adding a prefix here does not make it part of the method's
vocabulary; it makes `check_model.py` stop objecting to one the method does
not have.

If this project genuinely needs an element type the method does not define,
that is a decision worth recording rather than a line worth adding quietly.
