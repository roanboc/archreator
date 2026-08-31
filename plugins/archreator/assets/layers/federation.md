# Federation

_[← EA home](./README.md)_

**Used by the topmost model of a federation only** — the organization, or the
parent business function where no organization is modeled. A project that
stands alone leaves this file as it is, and nothing reads it.

**Status:** ○ Not started.

A federation is several models that belong together and are maintained apart:
one organization and the products it builds, or business lines past the point
where [`domains/`](./domains/README.md) stops helping — that folder caps the
tree at three levels and says that beyond it you want separate repositories
federated by contract.

## Nobody owns the union

There is no central model here and there is not meant to be one. A model that
held every other model's elements would **restate** what those models own,
which the tier rule in `architecture-document-style` forbids, and its owner
would need approval rights over elements they did not write.

What is centralized is **this list**. The graph is a view, assembled when
somebody opens it, owned by no one.

## The index

Each row names one model in the federation and where its projection is
published. This table is the source, and it is what gives a
`other-model::CAP1` reference a model name to resolve against.

| Model | Subject | Projection |
| ----- | ------- | ---------- |
|       |         |            |

**Read by position, not by header word** — cell 1 is the model's name, cell 2
what it models, cell 3 where its **projection** is published. The same rule the
rest of the notation follows, for the same reason: a model may be written in
any language.

Cell 3 names where a projection of that model is published, for a consumer
that cannot read its Markdown — `model.json`, written by `model.py export`.
Leave it empty when nothing publishes one; a model is federated by being
declared here, not by exporting anything.

**A location is a URL or a relative path.** A model published beside this one
uses a relative path; a model in another repository uses its full HTTPS URL.
Only a **published** projection can be federated — a reader is a page in
somebody's browser, and it can reach what the web can reach.

## What this cannot do

**Private repositories are out of reach.** A static page cannot authenticate,
and giving it a way to would trade away the property that makes it worth
having — that it is a file on a static host with nothing to operate and nothing
to secure.

**Nothing checks that a location still answers.** A URL here can rot: a model
moves, is renamed, or stops publishing. Nothing fails a build over it: the
alternative is a validator making network calls on every pull request, which is
a slow, flaky check on a fact that changes rarely. A reader who follows a dead
location learns it the ordinary way.

**A relationship still does not cross a model.** Elements are scoped per
model, and a federated view shows several graphs at once rather than one graph.
That is worth having on its own, and it is not the same thing.
