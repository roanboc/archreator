# Views

_[← EA home](../README.md)_

**Optional.** A project with nothing here publishes no views, and the
navigator behaves exactly as it would have.

A **view** is a saved arrangement of the graph: which model, which layers,
what is focused and how far, which layout, and where somebody dragged the
boxes. It is a lens over the model and never part of it.

## Where a view lives, and why there are three answers

| Where | For | Written by |
| ----- | --- | ---------- |
| The reader's browser | Their own working views, kept between visits | The navigator |
| An exported `.view.json` file | Sending one to somebody | The reader, deliberately |
| **This folder** | Views a team agrees on, published with the portal | A person, through a pull request |

**The navigator cannot write here, and that is the point.** It reads a view
and applies it; it has no way to create one in the repository. A page that
could add files under `architecture/` would be a model editor, and everything
that makes this safe to hand to anyone rests on it not being one.

A view committed here is a change like any other: it arrives in a pull
request, somebody reads it, and it is published when it merges.

## The file

One JSON file per view. Export one from the navigator and commit it — the
shape is whatever the navigator wrote, and it carries a `name` the picker
shows.

```json
{
  "name": "How a change reaches production",
  "view": { "model": "…", "layout": "layered", "hidden": [], "positions": {} }
}
```

## What a view is not

**It is not a document.** It shows elements; it says nothing about them that
the model does not already say. A view that needed a caption to make sense is
a view whose model is missing a sentence.

**It is not approved.** No gate covers this folder, because nothing here
asserts anything. If a view is being used to argue something, the argument
belongs in a document where somebody can disagree with it.

**It does not survive a rename.** A view names elements by identifier. An
identifier is assigned once and never reused, so a view breaks only when an
element is retired — and then it should.
