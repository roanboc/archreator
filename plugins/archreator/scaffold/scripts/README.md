# Scripts

_[← Project home](../README.md)_

Two validators that keep this project's architecture documents honest, and
three tools for the readers a repository does not reach. They came with the
scaffold, so this project has had them since its first commit, and CI should
run both validators on every pull request.

```bash
python3 scripts/check_links.py    # relative links and HTML anchors resolve
python3 scripts/check_model.py    # element-ID references resolve
python3 scripts/build_model.py    # project the model into .model/
python3 scripts/build_docs.py     # the model as a website, in .docs/site/
python3 scripts/export_pdf.py     # the model as one PDF, in .docs/
```

Both validators exit `0` when everything resolves and `1` otherwise, printing
what failed. The other three are tools rather than gates: nothing has to be
green for them, and nothing breaks if they are never run.

| File | What it is |
| ---- | ---------- |
| `check_links.py` | Executable. Every relative Markdown link and every HTML `href`, `src` and `#fragment` points at something that exists |
| `check_model.py` | Executable. Every backticked element ID resolves to a definition, none is defined twice, none is both live and retired, and a levelled ID has its parent defined |
| `build_model.py` | Executable. Writes `.model/model.json` and `.model/model.db` — the model as nodes and edges, for a rendered view or a report. `--inventory` prints one line per element instead |
| `build_docs.py` | Executable. Stages the documents into `.docs/src/` and builds the portal into `.docs/site/`. `--serve` rebuilds as the model is edited. Also the staging hook `mkdocs.yml` runs |
| `export_pdf.py` | Executable. Prints the portal's single-page view to `.docs/architecture.pdf` with a headless browser, and checks that the diagrams were drawn rather than left as source text |
| `model_graph.py` | Library, imported by the others. The single parse of the document convention — element IDs, catalogue tables, Mermaid edges |
| `element-prefixes.json` | Data, read by `model_graph.py`. The element-ID prefixes and what each stands for |

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
published view of the model, a dashboard, a report.

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

## What each one cannot do

`check_model.py` verifies that a *reference* resolves. `check_links.py`
verifies that a *link* resolves. **Neither reads what a "Realized by" cell
claims about a path**, so a cell naming a directory that no longer exists
passes both silently. Checking that is a step in the change process, not
something these scripts can do for you.

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
