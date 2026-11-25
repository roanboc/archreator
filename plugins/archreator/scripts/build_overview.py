#!/usr/bin/env python3
"""Show a whole model on one page, to somebody who never read the model.

    build_overview.py --project .

A brief answers one question about the model for a reader of the model, and a
preview shows one change for the person who has to confirm it. This is the
third reading: everything the model holds, for the people the business is
made of, who will never open the repository and should not need a notation
to read about their own work.

**One question at a time.** Why it exists, what it must be good at, who does
what, what it needs to know, what software does it, where it runs. Each is a
tab: its elements drawn with what they touch in the other questions, and
listed underneath in the words their documents use. Selecting anything says
what it is and what it is connected to, and follows a connection across.

**It is one self-contained file.** No server, no account, no network. It
opens from a disk or a mail attachment, and a host that shows pages beside a
conversation can show it there, private to whoever asked. That is what a
project on a private repository shows its own people instead of a published
site.

**Nothing in it is the model's notation**, for the same reason a preview has
none: no identifier, no glyph, no layer number. And nothing in it is judged
or summarized. A cell is quoted as written, and an element whose document
nobody has confirmed yet says so.

It draws with `plain_view.py` and reads the model with `build_preview.py`'s
own reading, so the three tools cannot disagree about what an element says.
Written to `.archreator/work/overview/`, disposable, never committed.
"""
import argparse
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

if {"-h", "--help"} & set(sys.argv[1:]):
    print(__doc__)
    sys.exit(0)

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_preview as reading  # noqa: E402 - finds the project and its parser
import plain_view as pv  # noqa: E402

ROOT = reading._ROOT
DERIVED = ROOT / ".archreator" / "work" / "overview"
# Past this many elements one question is drawn a kind at a time.
ONE_DRAWING = 24
# How many things from other questions a drawing carries for context.
PARTNERS = 10


def subject_of(explicit: str | None) -> str:
    """What the model is about: said on its front door, or its folder's name."""
    if explicit:
        return explicit
    front = ROOT / reading.model_graph.MODEL_DIR / "README.md"
    if front.is_file():
        for line in front.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                return title.split(" — ", 1)[1].strip() if " — " in title else title
    return ROOT.name


def stamp_of() -> str:
    revision = reading.git("rev-parse", "--short", "HEAD").stdout.strip()
    branch = reading.git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    when = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f"Branch {branch} at {revision} · {when}" if revision else f"Read from the files as they stand · {when}"


def build(subject: str, stamp: str) -> tuple[str, int]:
    models = reading.read(reading.model_graph)
    here = reading.model_graph.project_key(ROOT)
    parsed = models.get(here)
    if parsed is None:
        return "", 0
    names = reading.names_of(models, here)
    live = {f"{here}::{k}": e for k, e in parsed.elements.items() if not e.retired}

    def element_at(key: str):
        if key in live:
            return live[key]
        project, _, local = key.partition("::")
        other = models.get(project)
        return other.elements.get(local) if other else None

    links = []
    for edge in parsed.edges:
        src, dst, _ = reading.edge_key(here, edge)
        if src in live and element_at(dst) is not None and src != dst:
            links.append((src, dst, edge))

    short: dict[str, str] = {}
    data: dict[str, dict] = {}

    def key_of(qualified: str) -> str:
        return short.setdefault(qualified, f"n{len(short) + 1}")

    def node(key: str) -> dict:
        element = element_at(key)
        told, _ = reading.facts(element, names) if key in live else ({}, [])
        entry = {
            "key": key_of(key), "name": pv.plain(element.name) or "(unnamed)",
            "kind": pv.kind_of(element.type), "group": element.group, "status": "same",
            "detail": [(label, text, "", False) for label, text in told.items()],
        }
        data.setdefault(entry["key"], {
            "name": entry["name"], "kind": entry["kind"], "where": pv.HEADING.get(element.group, element.group),
            "status": "same", "was": "", "detail": [list(cell) for cell in entry["detail"]], "links": [],
            "tab": pv.GROUP_CLASS.get(element.group, "qx") if key in live else "",
            "draft": key in live and bool(element.status) and element.status != "validated",
        })
        return entry

    # Every connection is said once on each of its two ends, whichever tab drew it.
    for src, dst, edge in links:
        for mine, other, out in ((src, dst, True), (dst, src, False)):
            node(mine)
            node(other)
            data[key_of(mine)]["links"].append({
                "to": key_of(other), "name": pv.plain(element_at(other).name),
                "word": reading.word_of(edge), "out": out, "status": "same",
            })

    by_group: dict[str, list[str]] = defaultdict(list)
    for key, element in live.items():
        by_group[element.group].append(key)
    e = pv.esc
    tabs, views, first = [], [], {}
    for group in sorted(by_group, key=lambda g: pv.ORDER.get(g, 99)):
        tab = pv.GROUP_CLASS.get(group, "qx")
        members = sorted(by_group[group], key=lambda k: pv.plain(live[k].name).lower())
        tabs.append(f'<button type="button" role="tab" data-tab="{tab}" aria-selected="false">'
                    f'{e(pv.HEADING.get(group, group))}<span class="n">{len(members)}</span></button>')
        first[tab] = key_of(members[0])
        if len(members) <= ONE_DRAWING:
            chunks = [("", members)]
        else:
            kinds: dict[str, list[str]] = defaultdict(list)
            for key in members:
                kinds[pv.kind_of(live[key].type)].append(key)
            chunks = [(kind, kinds[kind]) for kind in sorted(kinds)]
        for index, (kind, chunk) in enumerate(chunks):
            inside = set(chunk)
            degree: dict[str, int] = defaultdict(int)
            for src, dst, _ in links:
                for a, b in ((src, dst), (dst, src)):
                    if a in inside and b not in inside:
                        degree[b] += 1
            ranked = sorted(degree, key=lambda k: (-degree[k], k))
            partners = set(ranked[:PARTNERS])
            shown = inside | partners
            nodes = [node(key) for key in sorted(shown)]
            edges = [{"a": key_of(src), "b": key_of(dst), "word": reading.word_of(edge), "status": "same",
                      "pending": edge.pending}
                     for src, dst, edge in links if src in shown and dst in shown and (src in inside or dst in inside)]
            heading = pv.HEADING.get(group, group) + (f": {kind}" if kind else "")
            picture = pv.svg(nodes, edges, title=heading, mode="model", uid=f"{tab}-{index}")
            width = int(float(picture.split('viewBox="0 0 ', 1)[1].split(" ", 1)[0]) * 0.74)
            rows = []
            for key in chunk:
                entry = data[key_of(key)]
                gloss = next((text for label, text, *_ in entry["detail"] if not label), "")
                rows.append(f'<li><strong>{e(entry["name"])}</strong> <span class="kind">{e(entry["kind"])}</span>'
                            + (f"<p>{e(gloss)}</p>" if gloss else "") + "</li>")
            left = len(ranked) - len(partners)
            caption = (f"{len(chunk)} here" + (f", with {len(partners)} they touch elsewhere" if partners else "")
                       + (f"; {left} more are not drawn" if left > 0 else "") + ". Select anything to read it.")
            views.append(
                f'<figure class="view" data-tab="{tab}">'
                + (f"<h2>{e(kind)}</h2>" if kind else "")
                + f'<div class="drawing" style="--min:{width}px">{picture}</div>'
                f"<figcaption>{e(caption)}</figcaption>"
                f'<div class="lists" style="margin-top:18px"><section><ul>{"".join(rows)}</ul></section></div>'
                "</figure>"
            )
    title = f"{subject[:1].upper()}{subject[1:]} on one page"
    body = "\n".join([
        f'<p class="stamp">{e(stamp)}</p>', f"<h1>{e(title)}</h1>",
        '<p class="why">What it knows about itself, one question at a time. Nothing here is a summary: '
        "each line is what its own documents say.</p>",
        f'<div class="tabs" role="tablist">{"".join(tabs)}</div>',
        '<div class="stage"><div>', *views, "</div>",
        '<aside class="reading" id="pv-reading" aria-live="polite"></aside></div>',
        "<footer>This page is one reading of the repository, made on request. The repository stays the record: "
        "when something here is wrong, the files change and the page is made again from them.</footer>",
    ])
    start = first[next(iter(first))] if first else ""
    return pv.page(title=title, body=body, data={"mode": "model", "nodes": data, "start": start, "first": first}), len(live)


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):  # pragma: no cover
            pass
    parser = argparse.ArgumentParser(description="Show a whole model on one page, in its own words.")
    parser.add_argument("--project", default=".", help="the project to read (default: the current directory)")
    parser.add_argument("--title", help="what the model is about (default: its front door's title)")
    parser.add_argument("--stamp", help="replace the line naming the branch and revision")
    parser.add_argument("--name", default="index", help="the file name to write under, without an extension")
    parser.add_argument("--to", type=Path, default=DERIVED, help="where to write the page")
    args = parser.parse_args()

    text, count = build(subject_of(args.title), args.stamp or stamp_of())
    if not count:
        print(f"{ROOT} defines no elements yet - there is nothing to show.")
        return 1
    args.to.mkdir(parents=True, exist_ok=True)
    path = args.to / f"{args.name}.html"
    path.write_text(text, encoding="utf-8")
    repo = reading.REPO
    print(f"{count} elements on one page: {path.relative_to(repo) if path.is_relative_to(repo) else path}")
    print("One self-contained file: open it in a browser, or show it beside the conversation where the host can. "
          "Showing it to anybody else is publishing. Disposable - the repository stays the record.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
