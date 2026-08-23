# Publishing the model

_[← Repository README](../README.md) · [The method](./method.md)_

The Markdown under `architecture/` is the model. Everything on this page is a
**rendering** of it, for the readers a repository does not reach: the
stakeholder who will not clone anything, the executive who wants a document in
a mail attachment, the auditor who needs a dated copy, the colleague who
searches rather than browses.

Two things ship in the scaffold, both derived and both disposable:

| | What it is | Run |
| --- | --- | --- |
| **The portal** | The model as a searchable website — every document, every diagram, navigation from the folder numbering | `python3 scripts/build_docs.py` |
| **The document** | The whole model as one PDF, printed from the portal's own single-page view | `python3 scripts/export_pdf.py` |

## The rule that makes this safe

A published copy of a model is the classic way to end up with two models. The
discipline is the one
[`build_model.py`](../plugins/archreator/scaffold/scripts/build_model.py) already lives
under, and it is three rules:

- **Regenerated, never edited.** Every run rebuilds the portal from the
  Markdown. There is no page you can fix in the portal and nowhere to fix it.
- **Gitignored.** Everything lands in `.docs/`, which is never committed. A
  derived file in the history is a derived file that can go stale.
- **Nothing reads it that could have read the Markdown.** An agent reads the
  documents; this exists for the consumers that cannot.

Delete `.docs/` and nothing is lost.

`stack-selection` § A persisted projection needs one of four triggers lists
the trigger this answers — *a dashboard, a report or a rendered model
cannot read Markdown tables*. It answers it in a different way than the SQLite
projection does, and the two are not alternatives: **the projection answers
questions about the model, the portal lets someone read it.** A project that
wants both runs both; most want neither until somebody outside the repository
needs to see the model.

## What the portal publishes, and why it is staged

MkDocs publishes one directory. A project keeps its documents where they
belong instead, so `build_docs.py` copies them into `.docs/src/` first —
`architecture/`, `docs/`, `scripts/`, and the Markdown files in the project
root — **keeping every path exactly as it is in the repository**.

That last part is what makes the portal honest. Because `architecture/README.md`
is still at `architecture/README.md` in the staged tree, the "edit this page"
pencil on every page opens *that* file in git. A reader who disagrees with a
page is one click from the file that produced it.

Navigation comes from the numbering the method already imposes: `1_strategy`
sorts before `2_business` because the folders were numbered in the order the
layers are assessed. Nothing declares a table of contents, so a new document
appears in the portal the moment it exists.

## The feedback the portal is for

Publishing widens the audience, and a wider audience has questions. The point
is that a question has somewhere to go **back into the model** rather than into
a reply nobody records:

```mermaid
flowchart LR
  reader(["⚇ A reader on a portal page"])
  q["⚙ Raises a question, as an issue naming the page"]
  triage{"Is the model wrong, or only unclear?"}
  oq["⚙ Logged in scope/open-questions.md"]
  init["⚙ Opened as an initiative"]
  model(["▧ The Markdown changes, and the portal follows"])

  reader --> q --> triage
  triage -->|"unclear — a question to answer"| oq
  triage -->|"wrong — a change to make"| init
  oq --> model
  init --> model

  classDef business fill:#fffbb5,stroke:#c8c04a,color:#333
  class reader,q,oq,init,model business
```

Every page carries three things, and each is a way back to the source:

- **Its source path**, so nobody mistakes the rendering for the model.
- **The pencil**, which opens that file in git — a correction becomes a pull
  request through the ordinary process, not an exception to it.
- **"Raise a question about this page"**, which opens an issue prefilled with
  the page it came from. The scaffold ships the issue form and the workflow
  that publishes the portal, both under `.github/`.

An answered question ends up in one of two places: `architecture/scope/open-questions.md`
when it is a question the model owes an answer to, or a new initiative when it
is a change — the same two places a question raised in a conversation ends up.
Neither is new machinery. The portal only gives the question a door.

## Running it

```bash
python3 scripts/build_docs.py             # build the portal into .docs/site/
python3 scripts/build_docs.py --serve     # ... and rebuild as the model is edited
python3 scripts/export_pdf.py             # the whole model as .docs/architecture.pdf
```

Both scripts declare their dependencies inline, so `uv run scripts/build_docs.py`
fetches MkDocs into a throwaway environment and installs nothing. Without `uv`,
install them once: `pip install mkdocs-material mkdocs-print-site-plugin`.

The PDF needs a Chromium-family browser — Chromium, Chrome or Edge — which it
finds on `PATH`, at the usual install location, or wherever `--browser` and
`CHROME_PATH` point. There is no second renderer: the PDF is the portal's own
print page, printed. Without a browser the export still builds that page and
says where it is, so any browser's Print → Save as PDF produces the same
document by hand.

**The diagrams are checked.** The theme fetches Mermaid from a CDN while a page
renders, so a machine with no route to it prints every diagram as the source
text that would have drawn it — a document that looks finished and is not. The
export loads the page a second time, counts the diagrams that were drawn
against the ones the model wrote, and says so when they do not match.

## Deploying it

The scaffold ships `.github/workflows/publish-docs.yml`, which builds the
portal on every push to the default branch and deploys it to GitHub Pages, with
the PDF attached to the run as an artifact. It needs Pages switched on for the
repository (Settings → Pages → Source: GitHub Actions) and nothing else.

Publishing an architecture is a disclosure decision, not a technical one. A
public repository's model is already public; a private one's is not, and a
Pages site published from it can be. **Decide who the portal is for before
turning the workflow on**, and record the call with `record-decision` if it is
not obvious.

## What it does not do

- **It does not validate anything.** `check_links.py` and `check_model.py` are
  the gates; this is a tool, like the projection. Nothing has to be green for
  it and nothing breaks if it is never run.
- **It renders, it does not summarize.** A page in the portal says exactly what
  the file says. If the portal reads badly, the document reads badly.
- **It needs the network at view time.** The theme loads Mermaid and its web
  fonts from a CDN when a page is opened. A portal for a network that blocks
  them needs a local copy of the library, added through `extra_javascript` in
  `mkdocs.yml`.
- **It is not the model.** It is a copy of the model on the day it was built.
  The Markdown in git is what anyone should argue with.
