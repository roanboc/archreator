# Scripts

_[← Project home](../README.md)_

Two validators that keep this project's architecture documents honest. They
came with the scaffold, so this project has had them since its first commit,
and CI should run both on every pull request.

```bash
python3 scripts/check_links.py    # relative links and HTML anchors resolve
python3 scripts/check_model.py    # element-ID references resolve
```

Both exit `0` when everything resolves and `1` otherwise, printing what failed.

| File | What it is |
| ---- | ---------- |
| `check_links.py` | Executable. Every relative Markdown link and every HTML `href`, `src` and `#fragment` points at something that exists |
| `check_model.py` | Executable. Every backticked element ID resolves to a definition, none is defined twice, none is both live and retired, and a levelled ID has its parent defined |
| `element-prefixes.json` | Data, read by `check_model.py`. The element-ID prefixes and what each stands for |

## What each one cannot do

`check_model.py` verifies that a *reference* resolves. `check_links.py`
verifies that a *link* resolves. **Neither reads what a "Realized by" cell
claims about a path**, so a cell naming a directory that no longer exists
passes both silently. Checking that is a step in the change process, not
something these scripts can do for you.

## `element-prefixes.json`

It is data, not configuration — regenerated from the method rather than
hand-edited. Adding a prefix here does not make it part of the method's
vocabulary; it makes `check_model.py` stop objecting to one the method does
not have.

If this project genuinely needs an element type the method does not define,
that is a decision worth recording rather than a line worth adding quietly.
