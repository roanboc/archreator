#!/usr/bin/env python3
"""Write one disposable brief about one part of the model.

A reader with a question about a domain, a function or a use case has two bad
options: open all of the model and hold the relevant rows in their head, or
open a graph and reconstruct the question by clicking. This is the third — name
a scope, get a document.

    python3 scripts/build_brief.py --element BSVC1 --depth 2
    python3 scripts/build_brief.py --domain SALES
    python3 scripts/build_brief.py --layer Application --type "Application Component"
    python3 scripts/build_brief.py --element DOBJ4 --focus information

**The walk is `model_graph.neighbourhood`**, the same traversal `model.py trace`
runs. One question — what is connected to this — asked by two readers and
answered once.

**Nothing here is summarized.** An element arrives with its catalogue row and
with the paragraphs the model already writes about it, verbatim. A paraphrase
in a generated document is a claim nobody approved, and there would be no way
to tell it had drifted from what was.

**Everything it writes is disposable.** A brief is a snapshot of a revision,
never committed, and it says so on its first line — a generated document that
does not announce itself gets mailed around and quoted eight months later,
which is the second source of truth this method exists to prevent.

**A generated view never replaces an authored one.** The layer documents keep
their diagrams: those are curated selections, and the notation is explicit that
a selection which looks complete is worse than several honest parts. What a
brief adds is the view nobody drew — the chain from business and information
down to application and technology, which lives in no single document because
each document diagrams its own layer.
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# --------------------------------------------------------------------------
# This tool runs from the plugin and reads a project. The parse it needs -
# `model_graph.py` - lives in that project's `scripts/`, beside the two
# validators, because a project has to be able to check itself with no plugin
# installed and no network.
#
# **One copy of the parse, not two.** Shipping a second copy here would put the
# document convention in two files that drift apart silently, which is the
# thing `model_graph.py` exists to prevent one level down. So this imports the
# project's copy, and says plainly what to do when there is none.
# --------------------------------------------------------------------------
def _project_root(argv: list[str]) -> Path:
    for index, argument in enumerate(argv):
        if argument == "--project" and index + 1 < len(argv):
            return Path(argv[index + 1]).resolve()
        if argument.startswith("--project="):
            return Path(argument.split("=", 1)[1]).resolve()
    return Path.cwd().resolve()


_ROOT = _project_root(sys.argv[1:])
_PARSE = _ROOT / "scripts" / "model_graph.py"
if not _PARSE.is_file():
    sys.exit(
        f"No archreator project at {_ROOT}: expected scripts/model_graph.py.\n"
        f"Run this from a project's root, or pass --project <path>."
    )
sys.path.insert(0, str(_PARSE.parent))

import model
from model_graph import (
    PREFIX_GROUPS,
    PREFIX_TYPES,
    REPO_ROOT,
    find_projects,
    neighbourhood,
    parse_project,
    prefix_of,
    project_key,
)

DERIVED = REPO_ROOT / ".archreator" / "work" / "briefs"
# The order the method assesses its layers in — `architecture/README.md`
# § Layers, in assessment order. The layered view is that order made vertical,
# which is what makes it answer "what realizes what" rather than "what is near
# what".
LAYER_ORDER = [
    "Motivation", "Strategy", "Business", "Information",
    "Application", "Technology", "Implementation & Migration",
    "Canvas (VPC)", "Canvas (BMC)",
]
# The palette `architecture/README.md` fixes. Restated here because Mermaid has
# no cross-file `classDef` and a generated diagram has to carry its own; the
# document remains the single source, and this is a copy with a comment on it.
LAYER_FILL = {
    "Motivation": ("#e6d6f5", "#7e57c2"),
    "Strategy": ("#f5deaa", "#c8a24a"),
    "Business": ("#fffbb5", "#b8a200"),
    "Information": ("#c2f0ff", "#0288d1"),
    "Application": ("#9adcf0", "#0277bd"),
    "Technology": ("#c9e7b7", "#558b2f"),
    "Implementation & Migration": ("#ffd6d6", "#d99b9b"),
    "Canvas (VPC)": ("#ece4d8", "#a8946f"),
    "Canvas (BMC)": ("#ece4d8", "#a8946f"),
}
# Past this many elements a diagram stops being a picture and becomes a wall.
# The brief says what it dropped rather than drawing it — see § the boundary.
MAX_IN_VIEW = 45

FOCUS_PRESETS = {
    "business": {
        "label": "Business and operations",
        "primary": {"Motivation", "Strategy", "Business"},
        "support": {"Information", "Application"},
        "emphasis": "why the organisation exists and how it delivers value",
        "deemphasized": "technology and unrelated solution detail",
        "heading": "How the operating model fits together",
    },
    "information": {
        "label": "Information and data",
        "primary": {"Business", "Information", "Application"},
        "support": {"Strategy", "Technology"},
        "emphasis": "information use, flow, ownership and realizing applications",
        "deemphasized": "unrelated motivation and technology detail",
        "heading": "How information is used and realized",
    },
    "solution": {
        "label": "Solution and technology",
        "primary": {"Application", "Technology"},
        "support": {"Business", "Information"},
        "emphasis": "applications, integrations, platforms and deployment",
        "deemphasized": "unrelated strategy and operating-model detail",
        "heading": "How the solution is realized and deployed",
    },
    "impact": {
        "label": "End-to-end impact",
        "primary": set(LAYER_ORDER),
        "support": set(),
        "emphasis": "the connected dependency chain across every layer",
        "deemphasized": "elements outside the requested traversal",
        "heading": "How this reaches across the layers",
    },
    "decision": {
        "label": "Decision overview",
        "primary": {"Motivation", "Strategy", "Business", "Implementation & Migration"},
        "support": {"Information", "Application", "Technology"},
        "emphasis": "the reason, affected capabilities, solution impacts and transition",
        "deemphasized": "implementation detail not directly affected by the decision",
        "heading": "How the decision reaches the architecture",
    },
}


class Store:
    """The model, read fresh, in the shape the brief asks questions in.

    This replaced a read-only SQLite file. The queries below were SQL, and the
    database they ran against had to be rebuilt to stay true — which, in the
    largest real model built on this method, it had not been: it answered from
    a projection that predated a course of action somebody had added, with
    nothing to tell the reader. Parsing the documents takes well under a
    second, so the store is now built per run and cannot be stale.

    Rows are dicts, which answer `row["name"]` exactly as `sqlite3.Row` did.
    """

    def __init__(self, projects: list[dict]) -> None:
        self.nodes: list[dict] = []
        self.edges: list[dict] = []
        self._excerpts: dict[tuple[str, str], list[dict]] = {}
        for entry in projects:
            name = entry["project"]
            for element in entry["elements"]:
                # `layer_group` is what the brief calls the element's own layer.
                self.nodes.append({**element, "project": name,
                                   "layer_group": element["group"]})
            for edge in entry["edges"]:
                self.edges.append({
                    "s": f"{name}::{edge['src']}",
                    "d": f"{edge['dst_project'] or name}::{edge['dst']}",
                    "rel": edge["rel"],
                    "origin": edge["origin"],
                    "pending": edge["pending"],
                })
            for excerpt in entry["excerpts"]:
                self._excerpts.setdefault((name, excerpt["element"]), []).append(excerpt)
        self.nodes.sort(key=lambda n: (n["project"], n["id"]))

    def has_project(self, name: str) -> bool:
        return any(n["project"] == name for n in self.nodes)

    def excerpts_for(self, project: str, element: str) -> list[dict]:
        return self._excerpts.get((project, element), [])


def read_model() -> Store | None:
    projects = model.collect()
    return Store(projects) if projects else None


def gid(row) -> str:
    return f"{row['project']}::{row['id']}"


def select(store: "Store", parsed_all: list, args) -> tuple[list[dict], str, list[str]]:
    """The elements in scope, how the scope was stated, and what it excluded.

    Anchors first: an element named on the command line, walked outward. Then
    filters, which narrow whatever the anchors reached — or, with no anchor,
    select from the whole model.
    """
    tests, said = [], []
    if args.scope:
        # An exact model name wins over a substring, because
        # `product-archreator` naming `product-archreator/site` as well is
        # never what somebody meant by typing the parent's name.
        exact = store.has_project(args.scope)
        if exact:
            tests.append(lambda n: n["project"] == args.scope)
            said.append(f"model `{args.scope}`")
        else:
            tests.append(lambda n: args.scope in n["project"])
            said.append(f"model matching `{args.scope}`")
    if args.domain:
        tests.append(lambda n: (n["domain"] or "").upper() == args.domain.upper())
        said.append(f"domain `{args.domain.upper()}`")
    if args.layer:
        tests.append(lambda n: (n["layer_group"] or "").lower() == args.layer.lower())
        said.append(f"the {args.layer} layer")
    if args.type:
        tests.append(lambda n: (n["type"] or "").lower() == args.type.lower())
        said.append(f"elements of type {args.type}")

    rows = [n for n in store.nodes if all(test(n) for test in tests)]

    if not args.element:
        return rows, ", ".join(said) or "the whole model", []

    anchors = [r for r in rows if r["id"].upper() == args.element.upper()]
    if not anchors and not any((args.scope, args.domain, args.layer, args.type)):
        anchors = [n for n in store.nodes if n["id"].upper() == args.element.upper()]
    if not anchors:
        return [], f"`{args.element}`", []
    if len(anchors) > 1:
        names = ", ".join(a["project"] for a in anchors)
        print(f"`{args.element}` is defined in {len(anchors)} models ({names}).")
        print("Narrow it with --scope.")
        return [], "", []

    anchor = anchors[0]
    home = next(p for p in parsed_all if project_key(p.project) == anchor["project"])
    others = [p for p in parsed_all if p is not home]
    walked, _ = neighbourhood(home, gid(anchor), args.depth, extra=others)
    reached = set(walked) | {gid(anchor)}
    inside = [r for r in rows if gid(r) in reached]
    if not any(gid(r) == gid(anchor) for r in inside):
        inside.insert(0, anchor)
    # What the filters cut out of the walk is worth naming: it is the
    # difference between a scope and an accident.
    dropped = sorted(reached - {gid(r) for r in inside})
    scope = f"`{anchor['id']}` — {anchor['name'] or 'unnamed'}, within {args.depth} hop(s)"
    if said:
        scope += ", narrowed to " + ", ".join(said)
    return inside, scope, dropped


def edges_within(store: "Store", ids: set[str]) -> list[dict]:
    return [e for e in store.edges
            if e["s"] in ids and e["d"] in ids and e["s"] != e["d"]]


def apply_focus(store: "Store", rows: list[dict], focus: str | None,
                anchor_id: str | None = None) -> tuple[list[dict], list[str]]:
    """Apply a reader viewpoint after scope selection, without changing facts.

    Primary-layer elements survive. Supporting-layer elements survive only
    when directly connected to a primary element. The named anchor always
    survives and acts as primary context even when its layer is not primary
    for the chosen viewpoint.
    """
    if not focus or focus == "impact":
        return rows, []

    preset = FOCUS_PRESETS[focus]
    by_id = {gid(row): row for row in rows}
    primary = {
        element for element, row in by_id.items()
        if (row["layer_group"] or "—") in preset["primary"]
    }
    if anchor_id:
        primary.update(
            element for element, row in by_id.items()
            if row["id"].upper() == anchor_id.upper()
        )

    kept = set(primary)
    candidates = {
        element for element, row in by_id.items()
        if (row["layer_group"] or "—") in preset["support"]
    }
    for edge in store.edges:
        if edge["s"] in primary and edge["d"] in candidates:
            kept.add(edge["d"])
        if edge["d"] in primary and edge["s"] in candidates:
            kept.add(edge["s"])

    # A focus with no primary-layer match still returns the protected anchor.
    focused = [row for row in rows if gid(row) in kept]
    excluded = sorted(set(by_id) - kept)
    return focused, excluded


def mermaid_id(value: str) -> str:
    return "n" + re.sub(r"\W", "_", value)


def safe(text: str) -> str:
    """A label Mermaid will not choke on.

    A quote ends the label early and a pipe ends an edge label early, so both
    go. Nothing else is touched: the words are the model's, and a diagram that
    silently rewrote them would be saying something the documents do not.
    """
    return re.sub(r"\s+", " ", (text or "").replace('"', "'").replace("|", "/")).strip()


def glyph_of(element_type: str) -> str:
    from_map = {
        "Stakeholder": "◍", "Driver": "✳", "Assessment": "⌕", "Goal": "◎",
        "Outcome": "◉", "Principle": "⚑", "Capability": "✦", "Resource": "▤",
        "Course of Action": "➤", "Value Stream": "⇉", "Actor": "⚇", "Role": "⚉",
        "Product": "▣", "Business Service": "⬭", "Business Process": "⚙",
        "Business Object": "▧", "Business Interface": "⊸", "Contract": "❒",
        "Data Object": "▦", "Application Service": "⬮", "Application Component": "⊞",
        "Technology Service": "⬯", "Node": "⬒", "Artifact": "⎔",
        "Plateau": "≡", "Gap": "⊘",
    }
    return from_map.get(element_type, "•")


def layered_view(rows: list[dict], edges: list[dict]) -> str:
    """The view the brief exists for: a scope, seen across the layers.

    One subgraph per layer in assessment order, and **only the relationships
    that cross a layer are drawn**. Within-layer edges are what make a scope of
    forty elements unreadable, and they are the ones each layer document
    already draws for itself. What no document draws is the chain down — a
    business service, the information it uses, the component that realizes it,
    the node it runs on — and that is what is left.
    """
    layer_of = {gid(r): (r["layer_group"] or "—") for r in rows}
    crossing = [e for e in edges if layer_of.get(e["s"]) != layer_of.get(e["d"])]
    if not crossing:
        return ""
    # **Only what actually crosses.** An element with no cross-layer
    # relationship is in the scope and is not part of its dependency chain;
    # drawing it fills a band with boxes that explain nothing. It is in the
    # tables below, where a reader can see it without it being in the way.
    involved = {e["s"] for e in crossing} | {e["d"] for e in crossing}
    shown = [r for r in rows if gid(r) in involved]

    by_layer = defaultdict(list)
    for row in shown:
        by_layer[row["layer_group"] or "—"].append(row)
    order = sorted(by_layer, key=lambda g: LAYER_ORDER.index(g) if g in LAYER_ORDER else 99)
    if len(order) < 2:
        return ""

    # `LR` rather than `TB`: Mermaid stacks subgraphs top-to-bottom in a
    # left-to-right flowchart and places them side by side in a top-down one,
    # which is the one arrangement a *layered* view must not have. The bands
    # run down the page and the elements inside each run across it.
    lines = ["```mermaid", "flowchart LR"]
    for group in order:
        lines.append(f'  subgraph L{mermaid_id(group)}["{group}"]')
        lines.append("    direction LR")
        for row in sorted(by_layer[group], key=lambda r: r["id"]):
            label = safe(f'{glyph_of(row["type"])} {row["name"] or row["id"]} [{row["id"]}]')
            lines.append(f'    {mermaid_id(gid(row))}["{label}"]:::c{mermaid_id(group)}')
        lines.append("  end")

    # **Every arrow is drawn down the stack, and the label is unchanged.**
    # Realization points upward in the model — a business service realizes a
    # capability — and Mermaid puts a target below its source, so drawing the
    # stated direction stands the layers on their heads. Orienting the arrow
    # top-down is what makes it a layered view; the label stays the word the
    # model wrote, read from the lower end. That is the same bargain the
    # projection already struck when it accepted that a `Provided by` column
    # names a relationship from the far side.
    rank = {group: index for index, group in enumerate(order)}
    for edge in crossing:
        arrow = "-.->" if edge["pending"] else "-->"
        a, b = edge["s"], edge["d"]
        if rank.get(layer_of.get(a), 99) > rank.get(layer_of.get(b), 99):
            a, b = b, a
        lines.append(f'  {mermaid_id(a)} {arrow}|{safe(edge["rel"])}| {mermaid_id(b)}')
    for group in order:
        fill, stroke = LAYER_FILL.get(group, ("#eeeeee", "#999999"))
        lines.append(f"  classDef c{mermaid_id(group)} fill:{fill},stroke:{stroke},color:#333")
    lines.append("```")
    return "\n".join(lines)


def motivation_view(rows: list[dict], edges: list[dict]) -> str:
    """Why the scope exists — its motivation and strategy elements, and nothing else."""
    keep = {gid(r) for r in rows if (r["layer_group"] or "") in ("Motivation", "Strategy")}
    if len(keep) < 2:
        return ""
    lines = ["```mermaid", "flowchart LR"]
    for row in sorted([r for r in rows if gid(r) in keep], key=lambda r: r["id"]):
        group = row["layer_group"]
        label = safe(f'{glyph_of(row["type"])} {row["name"] or row["id"]} [{row["id"]}]')
        lines.append(f'  {mermaid_id(gid(row))}["{label}"]:::c{mermaid_id(group)}')
    for edge in edges:
        if edge["s"] in keep and edge["d"] in keep:
            arrow = "-.->" if edge["pending"] else "-->"
            lines.append(
                f'  {mermaid_id(edge["s"])} {arrow}|{safe(edge["rel"])}| {mermaid_id(edge["d"])}')
    for group in ("Motivation", "Strategy"):
        fill, stroke = LAYER_FILL[group]
        lines.append(f"  classDef c{mermaid_id(group)} fill:{fill},stroke:{stroke},color:#333")
    lines.append("```")
    return "\n".join(lines)


def brief(store: "Store", rows, scope, dropped, focus_dropped, args) -> str:
    ids = {gid(r) for r in rows}
    edges = edges_within(store, ids)
    # From git, not from a written file: the point of the stamp is to say which
    # revision this reading came from, and a stamp copied out of a projection
    # says which revision the projection came from instead.
    revision = model.revision()

    when = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    out = [
        f"# Brief — {scope}",
        "",
        "> **This is a disposable document.** It was generated on "
        f"{when}" + (f" from revision `{revision[:12]}`" if revision else "") + ", it is "
        "not committed, and it will be wrong as soon as the model moves. "
        "**The repository is the model**; this is one reading of it, assembled "
        "to answer one question. Regenerate it rather than keeping it, and do "
        "not quote it as a record.",
        "",
    ]
    if args.focus:
        preset = FOCUS_PRESETS[args.focus]
        out += [
            "| | |",
            "| --- | --- |",
            f"| **Focus** | {preset['label']} |",
            f"| **Anchor / scope** | {scope} |",
            f"| **Depth** | {args.depth} relationship hop(s) |",
            f"| **Emphasizes** | {preset['emphasis']} |",
            f"| **De-emphasizes** | {preset['deemphasized']} |",
            "",
        ]
    out += [
        f"{len(rows)} element(s), {len(edges)} relationship(s) between them.",
        "",
    ]

    if len(rows) > MAX_IN_VIEW:
        out += [
            f"> The scope holds {len(rows)} elements, past the {MAX_IN_VIEW} a diagram "
            "can show without becoming a wall. The views below are omitted; narrow "
            "the scope with `--layer`, `--type` or a smaller `--depth`.",
            "",
        ]
    else:
        view = layered_view(rows, edges)
        if view:
            heading = FOCUS_PRESETS[args.focus]["heading"] if args.focus else "How this reaches across the layers"
            out += [f"## {heading}", "",
                    "Only relationships that **cross** a layer are drawn, and only the "
                    "elements that have one. The relationships inside a layer are what each "
                    "layer document already diagrams; the chain down is what no document "
                    "draws.", "",
                    "Every arrow runs down the stack and carries the word the model uses — "
                    "so a `Realizes` between two bands is read from the lower one. Elements "
                    "in scope with no cross-layer relationship are in the tables below "
                    "rather than in the picture.", "", view, ""]
        motive = motivation_view(rows, edges)
        if motive:
            out += ["## Why it exists", "", motive, ""]
        if not view and not motive:
            # Say it rather than print nothing. A scope narrowed to one layer
            # has no chain to draw, and a reader who asked for the view the
            # brief exists for should learn that instead of wondering.
            out += [
                "> **No cross-layer view.** Nothing in this scope depends on "
                "anything in another layer — usually because the scope is one "
                "layer wide. Widen it with a larger `--depth`, or drop "
                "`--layer`, to see the chain down.",
                "",
            ]

    by_layer = defaultdict(list)
    for row in rows:
        by_layer[row["layer_group"] or "—"].append(row)
    out += ["## The elements", ""]
    for group in sorted(by_layer, key=lambda g: LAYER_ORDER.index(g) if g in LAYER_ORDER else 99):
        out += [f"### {group}", ""]
        for row in sorted(by_layer[group], key=lambda r: r["id"]):
            out += element_section(store, row, edges, ids)
    out += boundary(store, rows, dropped, focus_dropped, ids, args.focus)
    return "\n".join(out) + "\n"


def element_section(store: "Store", row, edges, ids) -> list[str]:
    out = [f"#### {row['id']} — {row['name'] or 'unnamed'}", ""]
    facts = [f"**{row['type'] or 'element'}**"]
    if row["status"] and row["status"] != "validated":
        facts.append(f"_{row['status']} — not approved at a gate_")
    if row["retired"]:
        facts.append("_retired_")
    out += [" · ".join(facts), ""]

    # Already a dict: attrs come straight from the parse now, not through a
    # JSON column that had to be decoded on the way back out.
    attrs = row["attrs"] or {}
    filled = {k: v for k, v in attrs.items() if v and k.lower() != "name"}
    if filled:
        out += ["| | |", "| --- | --- |"]
        out += [f"| {k} | {v} |" for k, v in filled.items()]
        out.append("")

    said = store.excerpts_for(row["project"], row["id"])
    for excerpt in said:
        out += [f"> {excerpt['body']}", "",
                f"> — _{excerpt['heading']}_, `{excerpt['doc']}`" if excerpt["heading"]
                else f"> — `{excerpt['doc']}`", ""]

    related = [e for e in edges if e["s"] == gid(row) or e["d"] == gid(row)]
    if related:
        out.append("Related here: " + ", ".join(sorted({
            f"{e['rel']} `{(e['d'] if e['s'] == gid(row) else e['s']).split('::')[-1]}`"
            for e in related
        })) + ".")
        out.append("")
    out += [f"Defined in `{row['doc']}`.", ""]
    return out


def boundary(store: "Store", rows, dropped, focus_dropped, ids, focus=None) -> list[str]:
    """What the scope left out. A brief that looks complete is the failure mode."""
    out = ["## What this leaves out", ""]
    total = len(store.nodes)
    out.append(f"The model holds {total} element(s); this brief carries {len(rows)}.")
    out.append("")
    if dropped:
        out += [f"{len(dropped)} element(s) the walk reached were cut by the filters: " +
                ", ".join(f"`{d.split('::')[-1]}`" for d in sorted(dropped)[:20]) +
                ("…" if len(dropped) > 20 else "") + ".", ""]
    if focus_dropped:
        label = FOCUS_PRESETS[focus]["label"] if focus else "the selected focus"
        out += [f"{len(focus_dropped)} reached element(s) were de-emphasized by **{label}**: " +
                ", ".join(f"`{d.split('::')[-1]}`" for d in focus_dropped[:20]) +
                ("…" if len(focus_dropped) > 20 else "") + ".", ""]
    just_outside = store.edges
    edge_of_scope = sorted({
        (r["d"] if r["s"] in ids else r["s"])
        for r in just_outside
        if (r["s"] in ids) != (r["d"] in ids)
    })
    if edge_of_scope:
        out += ["Directly connected and **not** included — one hop beyond the edge:", ""]
        out += [f"- `{e.split('::')[-1]}`" for e in edge_of_scope[:25]]
        if len(edge_of_scope) > 25:
            out.append(f"- …and {len(edge_of_scope) - 25} more")
        out.append("")
    out += ["Widen with a larger `--depth`, or drop a filter.", ""]
    return out


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):  # pragma: no cover
            pass

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--element", help="an element identifier to walk outward from")
    parser.add_argument("--depth", type=int, default=2, help="hops from the anchor (default: 2)")
    parser.add_argument("--domain", help="only elements in this domain")
    parser.add_argument("--layer", help="only this layer group — Business, Application, …")
    parser.add_argument("--type", help="only this element type — Capability, Node, …")
    parser.add_argument("--project", default=".",
                        help="the project to read (default: the working directory)")
    parser.add_argument("--scope", help="only models whose path contains this")
    parser.add_argument("--focus", choices=FOCUS_PRESETS,
                        help="reader viewpoint: business, information, solution, impact or decision")
    parser.add_argument("--to", type=Path, default=DERIVED, help="where to write the brief")
    parser.add_argument("--stdout", action="store_true", help="print it instead of writing it")
    args = parser.parse_args()

    if not any((args.element, args.domain, args.layer, args.type, args.scope)):
        parser.error("name a scope: --element, --domain, --layer, --type or --scope")

    store = read_model()
    if store is None:
        print("No model found — nothing to brief.")
        return 0
    parsed_all = [p for p in (parse_project(x, detail=True) for x in find_projects())
                  if p.elements]
    rows, scope, dropped = select(store, parsed_all, args)
    if not rows:
        if scope:
            print(f"Nothing in scope for {scope}.")
        return 1
    rows, focus_dropped = apply_focus(store, rows, args.focus, args.element)
    if not rows:
        print(f"Nothing remains in scope for the {args.focus} focus.")
        return 1
    body = brief(store, rows, scope, dropped, focus_dropped, args)

    if args.stdout:
        print(body)
        return 0
    slug = re.sub(r"\W+", "-", (args.element or args.domain or args.layer or
                                args.type or args.scope)).strip("-").lower()
    if args.focus:
        slug += f"-{args.focus}"
    args.to.mkdir(parents=True, exist_ok=True)
    path = args.to / f"{slug}.md"
    path.write_text(body, encoding="utf-8")
    where = path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path
    print(f"Brief written to {where} — {len(rows)} element(s). Disposable: it is not "
          f"committed, and the repository stays the model.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
