#!/usr/bin/env python3
"""Draw a part of the model for somebody who has never read the model.

`build_brief.py` draws for a reader of the model: identifiers, glyphs, the
layers by name. This draws for the person the model is *about*. The same
elements and the same relationships, in the words the documents already use
for them, arranged by the question each one answers: why, who does what, what
it needs to know, what software does it.

Two tools draw with it. `build_preview.py` shows what a change claims, so the
Requester can confirm it where they are. `build_overview.py` shows a whole
model on one page.

**Nothing here reads a model.** The callers parse; this takes plain dicts and
returns text. That keeps it importable from a test with no project behind it,
and keeps the parse in the one place it lives.

**Three carriers come out, because a conversation renders what it renders.**

- a picture, as SVG, which stands alone as a file and also sits inside a page;
- the same graph as Mermaid source, for a conversation that renders a fence;
- a page: the picture, and a reading column that answers a click.

**One drawing, two grounds.** Every mark carries a literal light-theme colour
as an attribute and a class beside it. As a file the attributes are all there
is. Inside a page the stylesheet wins over the attributes, so the same marks
follow the page's theme.

**The layout is small on purpose.** Columns by question, a few sweeps to
untangle the rows, one curve per relationship. A change is a dozen elements,
and a view that needs a real graph library is showing too much.
"""
from __future__ import annotations

import html
import json
import re
from collections import defaultdict

# --------------------------------------------------------------------------
# The questions, in the order the method assesses its layers. The key is the
# element's own group, read from its identifier prefix; the heading is what a
# person who has never heard of a layer would call it.
# --------------------------------------------------------------------------
QUESTIONS: list[tuple[str, str]] = [
    ("Canvas (VPC)", "Who it is for"),
    ("Canvas (BMC)", "How it pays its way"),
    ("Motivation", "Why it exists"),
    ("Strategy", "What it must be good at"),
    ("Business", "Who does what"),
    ("Information", "What it needs to know"),
    ("Application", "The software"),
    ("Technology", "Where it runs"),
    ("Implementation & Migration", "Where it is heading"),
]
HEADING = dict(QUESTIONS)
ORDER = {group: index for index, (group, _) in enumerate(QUESTIONS)}

# An element type in everyday words. A type this does not know keeps its own
# name, lower-cased, which is still a word and never an identifier.
KIND = {
    "Stakeholder": "who cares", "Driver": "pressure", "Assessment": "finding",
    "Goal": "goal", "Outcome": "result", "Principle": "principle",
    "Capability": "ability", "Resource": "resource", "Course of Action": "plan",
    "Value Stream": "how value flows",
    "Actor": "who", "Role": "role", "Business Collaboration": "working together",
    "Product": "product", "Business Service": "service",
    "Business Process": "process", "Business Object": "thing it handles",
    "Business Interface": "channel", "Contract": "agreement",
    "Business Rule": "rule", "Value": "value",
    "Data Object": "information",
    "Application Service": "what the software does",
    "Application Component": "software",
    "Technology Service": "platform service", "Node": "platform", "Artifact": "file",
    "Plateau": "stage", "Gap": "gap",
    "Job": "job to be done", "Pain": "pain", "Gain": "gain",
    "Pain Reliever": "pain reliever", "Gain Creator": "gain creator",
    "Key Partner": "partner", "Key Activity": "activity", "Key Resource": "resource",
    "Value Proposition": "offer", "Customer Relationship": "relationship",
    "Channel": "channel", "Customer Segment": "customers",
    "Revenue Stream": "income", "Cost": "cost",
}

# The palette `architecture/README.md` fixes, one pair per group: fill, line.
# Used when the drawing shows a model rather than a change.
GROUP_FILL = {
    "Motivation": ("#e6d6f5", "#7e57c2"),
    "Strategy": ("#f5deaa", "#b08a2e"),
    "Business": ("#fffbb5", "#a89400"),
    "Information": ("#c2f0ff", "#0288d1"),
    "Application": ("#9adcf0", "#0277bd"),
    "Technology": ("#c9e7b7", "#558b2f"),
    "Implementation & Migration": ("#ffd6d6", "#c47f7f"),
    "Canvas (VPC)": ("#ece4d8", "#a8946f"),
    "Canvas (BMC)": ("#ece4d8", "#a8946f"),
}
GROUP_CLASS = {group: f"q{index}" for index, (group, _) in enumerate(QUESTIONS)}

# What a change did to a mark: fill, line, text. `same` is context, shown
# because it touches something that moved.
STATUS_FILL = {
    "new": ("#e2f3da", "#2f7a1f", "#1d1a24"),
    "changed": ("#fdefc9", "#8f5b00", "#1d1a24"),
    "removed": ("#fbe1e1", "#b3261e", "#756e86"),
    "same": ("#f1eff5", "#b0aabd", "#1d1a24"),
}
STATUS_WORD = {"new": "new", "changed": "changed", "removed": "removed", "same": ""}

# The notation's glyphs, and the three status glyphs. A person who was never
# taught the notation reads them as noise, so a plain view drops them.
# `test_plain_view.py` holds this against the notation reference.
GLYPHS = "◍✳⌕◎◉⚑✦▤◈➤⇉⚇⚉▣⬭⊸❒⧉⚙▧▦⊞⬮⬒⬯⎔≡⊘✖✔⊖⊕⇄▲▼○◐●▭"

# The drawing's measures. Bands run down the page, one per question, and each
# band holds a row of at most PER_ROW boxes, so a drawing is never wider than
# a page and grows downward, the direction a reader already scrolls in.
PER_ROW = 4
NODE_W = 188
PAD_X = 12
NAME_PX = 13
KIND_PX = 10
LINE_H = 16
SLOT_GAP = 26
ROW_GAP = 30
BAND_GAP = 46
BAND_HEAD = 30
BAND_FOOT = 14
EDGE = 16


# --------------------------------------------------------------------------
# Words
# --------------------------------------------------------------------------
_ID = r"(?:[A-Z][A-Z0-9_]*\.)*[A-Z]{1,5}\d+(?:\.\d+)*"
_BRACKETED_ID = re.compile(r"\[`(" + _ID + r")`\]\s*")
_CODE_ID = re.compile(r"`(" + _ID + r")`")
_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def plain(text: str, names: dict[str, str] | None = None) -> str:
    """A cell of the model in words alone.

    An identifier beside its name goes, and one standing by itself becomes the
    name it stands for. Links keep their text, emphasis and glyphs go. What is
    left is what the document says, which is the only thing a preview may say.
    """
    names = names or {}
    out = _LINK.sub(r"\1", text or "")
    out = _BRACKETED_ID.sub("", out)
    out = _CODE_ID.sub(lambda m: names.get(m.group(1), names.get(m.group(1).split(".")[-1], "")), out)
    out = out.replace("**", "").replace("`", "").replace("<br>", " ").replace("<br/>", " ")
    out = "".join(ch for ch in out if ch not in GLYPHS)
    out = re.sub(r"«[^»]*»\s*", "", out)
    out = re.sub(r"\s+([,.;:])", r"\1", out)
    return re.sub(r"\s+", " ", out).strip(" ·—–-").strip()


def kind_of(element_type: str) -> str:
    return KIND.get(element_type, (element_type or "element").lower())


_NARROW = set("iljtfrI.,:;'|!()[]/ ")
_WIDE = set("mwMW@%—")


def text_width(text: str, px: float) -> float:
    """A fair guess at how wide a run of sans text draws.

    A drawing made without a browser cannot measure, so it estimates, and
    errs wide: a line that wraps early is untidy, one that overflows its box
    is wrong.
    """
    total = 0.0
    for ch in text:
        if ch in _NARROW:
            total += 0.33
        elif ch in _WIDE:
            total += 0.9
        elif ch.isupper():
            total += 0.7
        elif ch.isdigit():
            total += 0.58
        else:
            total += 0.56
    return total * px


def wrap(text: str, max_px: float, px: float, max_lines: int = 3) -> list[str]:
    """Greedy lines that fit, with an ellipsis where the text had to stop."""
    lines: list[str] = []
    current = ""
    for word in (text or "").split():
        while text_width(word, px) > max_px and len(word) > 4:
            cut = max(3, int(len(word) * max_px / text_width(word, px)) - 1)
            head, word = word[:cut] + "-", word[cut:]
            if current:
                lines.append(current)
                current = ""
            lines.append(head)
        trial = f"{current} {word}".strip()
        if not current or text_width(trial, px) <= max_px:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while last and text_width(last + "…", px) > max_px:
            last = last[:-1]
        lines[-1] = last.rstrip() + "…"
    return lines or [""]


def esc(text: str) -> str:
    return html.escape(text or "", quote=True)


# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------
def _point(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u ** 3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t ** 3 * d
                 for a, b, c, d in zip(p0, p1, p2, p3))


def _hits(box, boxes) -> bool:
    x, y, w, h = box
    return any(x < bx + bw and bx < x + w and y < by + bh and by < y + h for bx, by, bw, bh in boxes)


def _slots(nodes: list[dict], edges: list[dict]) -> tuple[dict[str, tuple[int, int]], list[str], int]:
    """Which band row and which column each box takes.

    Columns are shared by every band, so a box can sit under the one it is
    connected to and the line between them runs straight down. A few passes
    up and down the bands let each one settle against its neighbours. Not
    optimal, and it does not need to be: it only has to stop a dozen
    relationships crossing for no reason.
    """
    groups: dict[str, list[dict]] = defaultdict(list)
    for node in nodes:
        groups[node["group"]].append(node)
    rank = {"new": 0, "changed": 1, "removed": 2, "same": 3}
    for members in groups.values():
        members.sort(key=lambda n: (rank.get(n.get("status", "same"), 3), n["name"].lower()))
    order = sorted(groups, key=lambda g: ORDER.get(g, 99))
    width = max(2, min(PER_ROW, max(len(m) for m in groups.values())))
    near: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        near[edge["a"]].append(edge["b"])
        near[edge["b"]].append(edge["a"])

    slot: dict[str, tuple[int, int]] = {}

    def settle(group: str) -> None:
        members = groups[group]
        wish = {}
        for index, node in enumerate(members):
            others = [slot[k][1] for k in near[node["key"]] if k in slot and k != node["key"]]
            mine = slot.get(node["key"], (0, index % width))[1]
            wish[node["key"]] = sum(others) / len(others) if others else mine
        ranked = sorted(members, key=lambda n: (wish[n["key"]], members.index(n)))
        for row, start in enumerate(range(0, len(ranked), width)):
            free = list(range(width))
            for node in ranked[start:start + width]:
                best = min(free, key=lambda c: (abs(c - wish[node["key"]]), c))
                free.remove(best)
                slot[node["key"]] = (row, best)

    for sweep in range(4):
        for group in (order if sweep % 2 == 0 else reversed(order)):
            settle(group)
    return slot, order, width


def layout(nodes: list[dict], edges: list[dict], *, labels: str = "auto") -> dict:
    """Where everything goes. Pure arithmetic; the drawing follows from it."""
    slot, order, width = _slots(nodes, edges)
    place: dict[str, dict] = {}
    bands: list[dict] = []
    total_w = EDGE * 2 + width * NODE_W + (width - 1) * SLOT_GAP
    y = 10.0
    for group in order:
        members = [n for n in nodes if n["group"] == group]
        rows = max(slot[n["key"]][0] for n in members) + 1
        top = y
        y += BAND_HEAD
        for row in range(rows):
            here = [n for n in members if slot[n["key"]][0] == row]
            tall = 0.0
            for node in here:
                lines = wrap(node["name"], NODE_W - 2 * PAD_X, NAME_PX * 1.04)
                node_h = 10 + KIND_PX + 6 + LINE_H * len(lines) + 8
                tall = max(tall, node_h)
                place[node["key"]] = {
                    "x": EDGE + slot[node["key"]][1] * (NODE_W + SLOT_GAP), "y": y,
                    "w": NODE_W, "h": node_h, "lines": lines, "row": (group, row),
                }
            y += tall + (ROW_GAP if row < rows - 1 else 0)
        y += BAND_FOOT
        bands.append({"group": group, "heading": HEADING.get(group, group), "y": top, "h": y - top})
        y += BAND_GAP
    total_h = y - BAND_GAP + 10

    # Ports: relationships leaving one side of a box spread along it, in the
    # order of where they are going, so they fan rather than pile up.
    drawn = [e for e in edges if e["a"] in place and e["b"] in place and e["a"] != e["b"]]
    sides: dict[tuple[str, str], list[tuple[float, int, str]]] = defaultdict(list)
    for index, edge in enumerate(drawn):
        a, b = place[edge["a"]], place[edge["b"]]
        if a["row"] == b["row"]:
            sides[(edge["a"], "B")].append((b["x"], index, "a"))
            sides[(edge["b"], "B")].append((a["x"], index, "b"))
        elif a["y"] < b["y"]:
            sides[(edge["a"], "B")].append((b["x"], index, "a"))
            sides[(edge["b"], "T")].append((a["x"], index, "b"))
        else:
            sides[(edge["a"], "T")].append((b["x"], index, "a"))
            sides[(edge["b"], "B")].append((a["x"], index, "b"))
    anchor: dict[tuple[int, str], tuple[float, float]] = {}
    for (key, side), uses in sides.items():
        box = place[key]
        uses.sort()
        for position, (_, index, end) in enumerate(uses):
            ax = box["x"] + box["w"] * (position + 1) / (len(uses) + 1)
            ay = box["y"] + (box["h"] if side == "B" else 0)
            anchor[(index, end)] = (ax, ay)

    show_all = labels == "all" or (labels == "auto" and len(drawn) <= 16)
    node_boxes = [(p["x"] - 2, p["y"] - 9, p["w"] + 4, p["h"] + 11) for p in place.values()]
    # A band's heading is as much in the way of a label as a box is.
    node_boxes += [(EDGE - 4, band["y"] + 6, text_width(band["heading"].upper(), 11) + 30, 20) for band in bands]
    taken: list[tuple[float, float, float, float]] = []
    routes = []
    for index, edge in enumerate(drawn):
        p0, p3 = anchor[(index, "a")], anchor[(index, "b")]
        a, b = place[edge["a"]], place[edge["b"]]
        if a["row"] == b["row"]:
            # Two boxes in one row: the line dips under the row and comes back.
            dip = 18 + min(14, abs(p3[0] - p0[0]) * 0.03)
            p1, p2 = (p0[0], p0[1] + dip), (p3[0], p3[1] + dip)
        else:
            reach = max(24, abs(p3[1] - p0[1]) * 0.45) * (1 if p3[1] > p0[1] else -1)
            p1, p2 = (p0[0], p0[1] + reach), (p3[0], p3[1] - reach)
        route = {"edge": edge, "d": "M{:.1f},{:.1f} C{:.1f},{:.1f} {:.1f},{:.1f} {:.1f},{:.1f}".format(*p0, *p1, *p2, *p3)}
        word = edge.get("word", "")
        if word and (show_all or edge.get("status", "same") != "same"):
            w = text_width(word, 10.5) + 10
            for t in (0.5, 0.4, 0.6, 0.32, 0.68, 0.24, 0.76):
                cx, cy = _point(p0, p1, p2, p3, t)
                cx = min(max(cx, w / 2 + 4), total_w - w / 2 - 4)
                box = (cx - w / 2, cy - 8, w, 16)
                if not _hits(box, node_boxes) and not _hits(box, taken):
                    taken.append(box)
                    route["label"] = {"x": cx, "y": cy, "w": w, "text": word}
                    break
        routes.append(route)
    return {"place": place, "bands": bands, "routes": routes, "w": total_w, "h": total_h}


# --------------------------------------------------------------------------
# The picture
# --------------------------------------------------------------------------
def svg(nodes: list[dict], edges: list[dict], *, title: str, mode: str = "change",
        uid: str = "v", labels: str = "auto") -> str:
    """The drawing, as one SVG that stands alone and also sits inside a page.

    `mode` says what the colour means: `change` colours a mark by what the
    change did to it, `model` by the question it answers.
    """
    if not nodes:
        return ""
    plan = layout(nodes, edges, labels=labels)
    place = plan["place"]
    w, h = plan["w"], plan["h"]
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" '
        f'height="{h:.0f}" role="group" aria-label="{esc(title)}" class="pv pv-{mode}" '
        f'font-family="system-ui, -apple-system, \'Segoe UI\', Roboto, Helvetica, Arial, sans-serif">',
        f"<title>{esc(title)}</title>",
        "<defs>",
    ]
    for status, (_, line, _) in STATUS_FILL.items():
        colour = "#8b8499" if status == "same" else line
        out.append(
            f'<marker id="{uid}-{status}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" '
            f'markerHeight="9" markerUnits="userSpaceOnUse" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
            f'fill="{colour}" class="pv-head pv-{status}"/></marker>'
        )
    out.append("</defs>")
    out.append(f'<rect class="pv-bg" width="{w:.0f}" height="{h:.0f}" fill="#ffffff"/>')
    for band in plan["bands"]:
        out.append(
            f'<rect class="pv-band" x="6" y="{band["y"]:.0f}" width="{w - 12:.0f}" '
            f'height="{band["h"]:.0f}" rx="6" fill="#f6f4f9"/>'
            f'<text class="pv-heading" x="{EDGE}" y="{band["y"] + 19:.0f}" font-size="11" font-weight="700" '
            f'letter-spacing="0.9" fill="#4d475b">{esc(band["heading"].upper())}</text>'
        )
    for route in plan["routes"]:
        edge = route["edge"]
        status = edge.get("status", "same")
        colour = "#8b8499" if status == "same" else STATUS_FILL[status][1]
        dash = ' stroke-dasharray="5 4"' if status == "removed" or edge.get("pending") else ""
        out.append(
            f'<g class="pv-edge pv-{status}" data-a="{esc(edge["a"])}" data-b="{esc(edge["b"])}">'
            f'<path d="{route["d"]}" fill="none" stroke="{colour}" stroke-width="{1.2 if status == "same" else 1.8}"'
            f'{dash} marker-end="url(#{uid}-{status})"/>'
        )
        label = route.get("label")
        if label:
            out.append(
                f'<rect class="pv-label-bg" x="{label["x"] - label["w"] / 2:.1f}" y="{label["y"] - 8:.1f}" '
                f'width="{label["w"]:.1f}" height="16" rx="3" fill="#ffffff"/>'
                f'<text class="pv-label" x="{label["x"]:.1f}" y="{label["y"] + 3.6:.1f}" text-anchor="middle" '
                f'font-size="10.5" fill="{"#4d475b" if status == "same" else colour}">{esc(label["text"])}</text>'
            )
        out.append("</g>")
    for node in nodes:
        box = place[node["key"]]
        status = node.get("status", "same")
        if mode == "model":
            fill, line = GROUP_FILL.get(node["group"], ("#eeeeee", "#999999"))
            ink = "#1d1a24"
        else:
            fill, line, ink = STATUS_FILL[status]
        tag = STATUS_WORD.get(status, "") if mode == "change" else ""
        said = ", ".join(part for part in (tag, node["name"], node.get("kind", "")) if part)
        dash = ' stroke-dasharray="5 4"' if status == "removed" else ""
        classes = f'pv-node pv-{status} pv-{GROUP_CLASS.get(node["group"], "qx")}'
        out.append(
            f'<g class="{classes}" data-k="{esc(node["key"])}" tabindex="0" role="button" aria-label="{esc(said)}">'
            f'<title>{esc(node["name"])}</title>'
            f'<rect class="pv-box" x="{box["x"]:.1f}" y="{box["y"]:.1f}" width="{box["w"]}" height="{box["h"]:.1f}" '
            f'rx="4" fill="{fill}" stroke="{line}" stroke-width="{1.2 if status == "same" else 1.8}"{dash}/>'
            f'<text class="pv-kind" x="{box["x"] + PAD_X:.1f}" y="{box["y"] + 10 + KIND_PX - 2:.1f}" '
            f'font-size="{KIND_PX}" letter-spacing="0.7" fill="#756e86">{esc(node.get("kind", "").upper())}</text>'
        )
        if tag:
            tag_w = text_width(tag.upper(), 9.5) + 12
            out.append(
                f'<rect class="pv-tag-bg" x="{box["x"] + box["w"] - tag_w - 8:.1f}" y="{box["y"] - 7:.1f}" '
                f'width="{tag_w:.1f}" height="14" rx="7" fill="{line}"/>'
                f'<text class="pv-tag" x="{box["x"] + box["w"] - 8 - tag_w / 2:.1f}" y="{box["y"] + 3.2:.1f}" '
                f'text-anchor="middle" font-size="9.5" font-weight="700" letter-spacing="0.5" fill="#ffffff">'
                f"{esc(tag.upper())}</text>"
            )
        strike = ' text-decoration="line-through"' if status == "removed" else ""
        for index, line_text in enumerate(box["lines"]):
            out.append(
                f'<text class="pv-name" x="{box["x"] + PAD_X:.1f}" '
                f'y="{box["y"] + 10 + KIND_PX + 6 + LINE_H * index + 11:.1f}" font-size="{NAME_PX}" '
                f'font-weight="600" fill="{ink}"{strike}>{esc(line_text)}</text>'
            )
        out.append("</g>")
    out.append("</svg>")
    return "".join(out)


# --------------------------------------------------------------------------
# The same graph for a conversation that renders a fence
# --------------------------------------------------------------------------
def _safe(text: str) -> str:
    """A label Mermaid will not choke on: no quote, no pipe, no bracket."""
    text = re.sub(r"\s+", " ", text or "")
    return text.replace('"', "'").replace("|", "/").replace("[", "(").replace("]", ")").strip()


def mermaid(nodes: list[dict], edges: list[dict], *, mode: str = "change") -> str:
    """The graph as Mermaid source, grouped by question, without a fence."""
    if not nodes:
        return ""
    keys = {n["key"] for n in nodes}
    lines = ["flowchart LR"]
    by_group: dict[str, list[dict]] = defaultdict(list)
    for node in nodes:
        by_group[node["group"]].append(node)
    for group in sorted(by_group, key=lambda g: ORDER.get(g, 99)):
        lines.append(f'  subgraph {GROUP_CLASS.get(group, "qx")}["{_safe(HEADING.get(group, group))}"]')
        for node in by_group[group]:
            status = node.get("status", "same")
            tag = f" ({STATUS_WORD[status]})" if mode == "change" and STATUS_WORD.get(status) else ""
            css = status if mode == "change" else GROUP_CLASS.get(group, "qx") + "c"
            lines.append(f'    {node["key"]}["{_safe(node["name"])}{tag}"]:::{css}')
        lines.append("  end")
    for edge in edges:
        if edge["a"] not in keys or edge["b"] not in keys:
            continue
        status = edge.get("status", "same")
        arrow = "-.->" if status == "removed" or edge.get("pending") else "-->"
        word = _safe(edge.get("word", ""))
        if word and status != "same" and mode == "change":
            word = f"{word} ({STATUS_WORD[status]})"
        label = f'|"{word}"|' if word else ""
        lines.append(f'  {edge["a"]} {arrow}{label} {edge["b"]}')
    if mode == "change":
        for status, (fill, line, ink) in STATUS_FILL.items():
            extra = ",stroke-dasharray: 5 4" if status == "removed" else ""
            lines.append(f"  classDef {status} fill:{fill},stroke:{line},color:{ink}{extra}")
    else:
        for group in by_group:
            fill, line = GROUP_FILL.get(group, ("#eeeeee", "#999999"))
            lines.append(f'  classDef {GROUP_CLASS.get(group, "qx")}c fill:{fill},stroke:{line},color:#1d1a24')
    return "\n".join(lines)


# --------------------------------------------------------------------------
# The page
# --------------------------------------------------------------------------
# Layout: one sheet. The drawing leads; the reading column sits beside it and
# drops under it on a phone. Every colour is a token, defined light first and
# redefined for the dark ground twice - once for a device set dark, once for a
# viewer who chose dark - so a page shown inside a host follows the host.
PAGE_CSS = """
:root{
  --ground:#fbfafc; --sheet:#ffffff; --ink:#1d1a24; --ink-2:#4d475b; --ink-3:#756e86; --rule:#dcd7e6;
  --accent:#6a45b5; --wire:#8b8499; --band:#f6f4f9;
  --new:#2f7a1f; --new-bg:#e2f3da; --changed:#8f5b00; --changed-bg:#fdefc9;
  --removed:#b3261e; --removed-bg:#fbe1e1; --same-bg:#f1eff5; --same-line:#b0aabd; --on-tag:#ffffff;
  --q0:#ece4d8; --q0l:#a8946f; --q1:#ece4d8; --q1l:#a8946f; --q2:#e6d6f5; --q2l:#7e57c2;
  --q3:#f5deaa; --q3l:#b08a2e; --q4:#fffbb5; --q4l:#a89400; --q5:#c2f0ff; --q5l:#0288d1;
  --q6:#9adcf0; --q6l:#0277bd; --q7:#c9e7b7; --q7l:#558b2f; --q8:#ffd6d6; --q8l:#c47f7f;
  --display:"Iowan Old Style","Palatino Linotype",Palatino,"Book Antiqua",Georgia,serif;
  --body:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --mono:ui-monospace,"SF Mono",SFMono-Regular,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#15121b; --sheet:#1c1824; --ink:#f1edf8; --ink-2:#c5bdd6; --ink-3:#9a92ad; --rule:#342d43;
    --accent:#b497f0; --wire:#8f87a3; --band:#1a1622;
    --new:#8fd07a; --new-bg:#1f3318; --changed:#f0c05a; --changed-bg:#3a2c0c;
    --removed:#ff9d94; --removed-bg:#3c1a18; --same-bg:#262130; --same-line:#5a5270; --on-tag:#15121b;
    --q0:#3a3327; --q0l:#b7a27a; --q1:#3a3327; --q1l:#b7a27a; --q2:#33274a; --q2l:#b497f0;
    --q3:#40351a; --q3l:#dcb65c; --q4:#3d3a10; --q4l:#d6c84a; --q5:#12384a; --q5l:#5cc0f2;
    --q6:#0f3344; --q6l:#4fb3e6; --q7:#22381a; --q7l:#93cf6a; --q8:#44201f; --q8l:#e79a9a;
    color-scheme:dark;
  }
}
:root[data-theme="dark"]{
  --ground:#15121b; --sheet:#1c1824; --ink:#f1edf8; --ink-2:#c5bdd6; --ink-3:#9a92ad; --rule:#342d43;
  --accent:#b497f0; --wire:#8f87a3; --band:#1a1622;
  --new:#8fd07a; --new-bg:#1f3318; --changed:#f0c05a; --changed-bg:#3a2c0c;
  --removed:#ff9d94; --removed-bg:#3c1a18; --same-bg:#262130; --same-line:#5a5270; --on-tag:#15121b;
  --q0:#3a3327; --q0l:#b7a27a; --q1:#3a3327; --q1l:#b7a27a; --q2:#33274a; --q2l:#b497f0;
  --q3:#40351a; --q3l:#dcb65c; --q4:#3d3a10; --q4l:#d6c84a; --q5:#12384a; --q5l:#5cc0f2;
  --q6:#0f3344; --q6l:#4fb3e6; --q7:#22381a; --q7l:#93cf6a; --q8:#44201f; --q8l:#e79a9a;
  color-scheme:dark;
}
*,*::before,*::after{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font-family:var(--body);font-size:15px;line-height:1.55;-webkit-font-smoothing:antialiased}
table{font:inherit;color:inherit}
.sheet{max-width:1240px;margin:0 auto;padding-block:28px 56px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.stamp{font-family:var(--mono);font-size:12px;color:var(--ink-3);letter-spacing:.02em;margin:0 0 10px;overflow-wrap:anywhere}
h1{font-family:var(--display);font-weight:600;font-size:clamp(1.6rem,1.2rem + 1.6vw,2.3rem);line-height:1.15;letter-spacing:-.01em;margin:0 0 12px;text-wrap:balance}
h2{font-size:.78rem;font-weight:700;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-3);margin:0 0 10px}
.why{max-width:68ch;color:var(--ink-2);font-size:1.02rem;margin:0 0 22px}
.stage{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:20px;align-items:start;margin-bottom:26px}
.stage.solo{grid-template-columns:minmax(0,1fr)}
figure{margin:0;min-width:0}
.drawing{background:var(--sheet);border:1px solid var(--rule);border-radius:6px;overflow-x:auto}
.drawing svg{display:block;width:100%;height:auto;min-width:var(--min,560px)}
figcaption{font-size:.86rem;color:var(--ink-3);margin-top:8px;max-width:72ch}
.view + .view{margin-top:22px}
.reading{background:var(--sheet);border:1px solid var(--rule);border-radius:6px;padding:16px 18px;position:sticky;top:16px;min-width:0}
.reading .kind{font-size:.72rem;font-weight:700;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-3);margin:0 0 4px}
.reading h3{font-family:var(--display);font-weight:600;font-size:1.25rem;line-height:1.2;margin:0 0 8px;overflow-wrap:anywhere}
.reading .state{font-size:.9rem;margin:0 0 12px;color:var(--ink-2)}
.reading dl{margin:0 0 12px}
.reading dt{font-size:.72rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:var(--ink-3);margin-top:10px}
.reading dd{margin:2px 0 0;color:var(--ink-2);overflow-wrap:anywhere}
.reading ul{list-style:none;margin:0;padding:0;display:grid;gap:4px}
.reading button{font:inherit;color:var(--ink);background:none;border:0;border-bottom:1px solid var(--rule);padding:6px 0;width:100%;text-align:left;cursor:pointer;display:flex;gap:8px;align-items:baseline}
.reading button:hover,.reading button:focus-visible{color:var(--accent);border-bottom-color:var(--accent);outline:none}
.reading button .word{font-size:.8rem;color:var(--ink-3);flex:0 0 auto}
.pill{display:inline-block;font-size:.68rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;padding:2px 8px;border-radius:999px;color:var(--on-tag);vertical-align:.12em;margin-right:6px}
.pill.new{background:var(--new)}.pill.changed{background:var(--changed)}.pill.removed{background:var(--removed)}
.lists{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:22px 28px;margin-bottom:26px}
.lists section{min-width:0}
.lists ul{list-style:none;margin:0;padding:0;display:grid;gap:10px}
.lists li{border-top:1px solid var(--rule);padding-top:8px;overflow-wrap:anywhere}
.lists li strong{font-weight:650}
.lists li .kind{color:var(--ink-3);font-size:.85rem}
.lists li p{margin:3px 0 0;color:var(--ink-2);font-size:.93rem}
.was{color:var(--ink-3);text-decoration:line-through;text-decoration-thickness:1px}
.calls,.ask{background:var(--sheet);border:1px solid var(--rule);border-radius:6px;padding:16px 18px;margin-bottom:18px}
.calls ul{margin:0;padding-left:1.1rem;display:grid;gap:6px}
.calls li{overflow-wrap:anywhere}
.ask{border-color:var(--accent)}
.ask h2{color:var(--accent)}
.ask p{margin:0 0 8px;font-size:1.05rem;max-width:68ch}
.ask ol{margin:0 0 8px;padding-left:1.3rem;display:grid;gap:4px}
.ask .mine{font-size:.8rem;color:var(--ink-3)}
.ask .how{font-size:.86rem;color:var(--ink-3);margin:8px 0 0}
.tabs{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 14px}
.tabs button{font:inherit;font-size:.9rem;font-weight:600;color:var(--ink-2);background:var(--sheet);border:1px solid var(--rule);border-radius:999px;padding:6px 13px;cursor:pointer}
.tabs button[aria-selected="true"]{color:var(--sheet);background:var(--ink);border-color:var(--ink)}
.tabs button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.tabs .n{font-weight:500;opacity:.7;margin-left:4px;font-variant-numeric:tabular-nums}
footer{font-size:.84rem;color:var(--ink-3);border-top:1px solid var(--rule);padding-top:14px;max-width:80ch}
.pv-bg{fill:transparent}
.pv-band{fill:var(--band)}
.pv-heading{fill:var(--ink-2)}
.pv-kind{fill:var(--ink-3)}
.pv-name{fill:var(--ink)}
.pv-label{fill:var(--ink-2)}
.pv-label-bg{fill:var(--sheet)}
.pv-edge path{stroke:var(--wire)}
.pv-head{fill:var(--wire)}
.pv-change .pv-node .pv-box{fill:var(--same-bg);stroke:var(--same-line)}
.pv-change .pv-node.pv-new .pv-box{fill:var(--new-bg);stroke:var(--new)}
.pv-change .pv-node.pv-changed .pv-box{fill:var(--changed-bg);stroke:var(--changed)}
.pv-change .pv-node.pv-removed .pv-box{fill:var(--removed-bg);stroke:var(--removed)}
.pv-change .pv-node.pv-removed .pv-name{fill:var(--ink-3)}
.pv-node.pv-new .pv-tag-bg{fill:var(--new)}.pv-node.pv-changed .pv-tag-bg{fill:var(--changed)}.pv-node.pv-removed .pv-tag-bg{fill:var(--removed)}
.pv-tag{fill:var(--on-tag)}
.pv-edge.pv-new path{stroke:var(--new)}.pv-edge.pv-new .pv-label{fill:var(--new)}.pv-head.pv-new{fill:var(--new)}
.pv-edge.pv-removed path{stroke:var(--removed)}.pv-edge.pv-removed .pv-label{fill:var(--removed)}.pv-head.pv-removed{fill:var(--removed)}
.pv-model .pv-q0 .pv-box{fill:var(--q0);stroke:var(--q0l)}.pv-model .pv-q1 .pv-box{fill:var(--q1);stroke:var(--q1l)}
.pv-model .pv-q2 .pv-box{fill:var(--q2);stroke:var(--q2l)}.pv-model .pv-q3 .pv-box{fill:var(--q3);stroke:var(--q3l)}
.pv-model .pv-q4 .pv-box{fill:var(--q4);stroke:var(--q4l)}.pv-model .pv-q5 .pv-box{fill:var(--q5);stroke:var(--q5l)}
.pv-model .pv-q6 .pv-box{fill:var(--q6);stroke:var(--q6l)}.pv-model .pv-q7 .pv-box{fill:var(--q7);stroke:var(--q7l)}
.pv-model .pv-q8 .pv-box{fill:var(--q8);stroke:var(--q8l)}
.pv-node{cursor:pointer;outline:none}
.pv-node:focus-visible .pv-box,.pv-node.on .pv-box{stroke:var(--accent);stroke-width:2.6}
.pv.picked .pv-node:not(.on):not(.near){opacity:.38}
.pv.picked .pv-edge:not(.on){opacity:.16}
.pv.picked .pv-edge.on path{stroke-width:2.2}
@media (max-width:900px){.stage{grid-template-columns:minmax(0,1fr)}.reading{position:static}}
@media (prefers-reduced-motion:no-preference){.pv-node,.pv-edge{transition:opacity .15s}}
"""

# The page's whole behaviour: a pick in the drawing fills the reading column,
# and a pick in the reading column moves the drawing. No library, no network.
PAGE_JS = """
(function(){
  var data = JSON.parse(document.getElementById('pv-data').textContent);
  var reading = document.getElementById('pv-reading');
  var words = data.words;
  function el(tag, cls, text){ var e=document.createElement(tag); if(cls) e.className=cls; if(text!=null) e.textContent=text; return e; }
  function show(key, from){
    var n = data.nodes[key]; if(!n) return;
    document.querySelectorAll('svg.pv').forEach(function(s){
      var here = s.querySelector('.pv-node[data-k="'+key+'"]');
      s.classList.toggle('picked', !!here && from==='user');
      s.querySelectorAll('.pv-node').forEach(function(g){ g.classList.remove('on','near'); });
      s.querySelectorAll('.pv-edge').forEach(function(g){
        var on = g.getAttribute('data-a')===key || g.getAttribute('data-b')===key;
        g.classList.toggle('on', on);
        if(on){ var o = g.getAttribute('data-a')===key ? g.getAttribute('data-b') : g.getAttribute('data-a');
          var og = s.querySelector('.pv-node[data-k="'+o+'"]'); if(og) og.classList.add('near'); }
      });
      if(here) here.classList.add('on');
    });
    if(!reading) return;
    reading.textContent='';
    reading.appendChild(el('p','kind', n.kind + (n.where ? ' · ' + n.where : '')));
    reading.appendChild(el('h3', null, n.name));
    if(n.status && n.status!=='same'){
      var st = el('p','state'); var pill = el('span','pill '+n.status, words[n.status]); st.appendChild(pill);
      st.appendChild(document.createTextNode(n.status==='changed' && n.was ? words.was + ' \\u201c' + n.was + '\\u201d' : words[n.status+'_long']));
      reading.appendChild(st);
    } else if(data.mode==='change'){ reading.appendChild(el('p','state', words.same_long)); }
    if(n.detail && n.detail.length){
      var dl = el('dl');
      n.detail.forEach(function(d){ if(d[0]) dl.appendChild(el('dt',null,d[0])); var dd=el('dd');
        if(d[3]){ dd.appendChild(el('span','pill changed', d[2] ? words.changed : words.added)); }
        if(d[2]){ dd.appendChild(el('span','was',d[2])); dd.appendChild(document.createTextNode(' \\u2192 ')); }
        dd.appendChild(document.createTextNode(d[1])); dl.appendChild(dd); });
      reading.appendChild(dl);
    }
    if(n.links && n.links.length){
      reading.appendChild(el('h2', null, words.touches));
      var ul = el('ul');
      n.links.forEach(function(l){ var li=el('li'); var b=el('button'); b.type='button';
        b.appendChild(el('span','word', l.out ? l.word + ' \\u2192' : '\\u2190 ' + l.word));
        b.appendChild(el('span', null, data.nodes[l.to] ? data.nodes[l.to].name : l.name));
        if(l.status && l.status!=='same') b.appendChild(el('span','pill '+l.status, words[l.status]));
        b.addEventListener('click', function(){ jump(l.to); }); li.appendChild(b); ul.appendChild(li); });
      reading.appendChild(ul);
    }
    if(from==='user' && window.matchMedia('(max-width:900px)').matches) reading.scrollIntoView({block:'nearest',behavior:'smooth'});
  }
  function jump(key){
    var n = data.nodes[key]; if(!n) return;
    if(n.tab && typeof window.pvTab==='function') window.pvTab(n.tab);
    show(key,'user');
  }
  document.querySelectorAll('.pv-node').forEach(function(g){
    g.addEventListener('click', function(){ show(g.getAttribute('data-k'),'user'); });
    g.addEventListener('keydown', function(e){ if(e.key==='Enter'||e.key===' '){ e.preventDefault(); show(g.getAttribute('data-k'),'user'); } });
  });
  var tabs = document.querySelectorAll('.tabs button');
  window.pvTab = function(id){
    tabs.forEach(function(b){ b.setAttribute('aria-selected', b.getAttribute('data-tab')===id ? 'true':'false'); });
    document.querySelectorAll('.view[data-tab]').forEach(function(v){ v.hidden = v.getAttribute('data-tab')!==id; });
  };
  tabs.forEach(function(b){ b.addEventListener('click', function(){ window.pvTab(b.getAttribute('data-tab')); if(data.first[b.getAttribute('data-tab')]) show(data.first[b.getAttribute('data-tab')]); }); });
  if(data.start) show(data.start);
})();
"""

WORDS = {
    "new": "new", "changed": "changed", "removed": "removed",
    "new_long": "New in this change.", "changed_long": "Changed by this change.",
    "removed_long": "Removed by this change.",
    "same_long": "Not changed. Shown because it touches something that is.",
    "was": "Was", "touches": "What it touches", "added": "added",
}


def page(*, title: str, body: str, data: dict, lang: str = "en") -> str:
    """One self-contained page: styles, the body given, the data, the script.

    No address is fetched and nothing is loaded, so the file opens from a
    disk, from a mail attachment, or inside a host that shows pages beside a
    conversation. The document tags a browser can infer are left for it to
    infer, which is what lets a host wrap the same file in its own frame.
    """
    payload = json.dumps({**data, "words": WORDS}, ensure_ascii=False).replace("</", "<\\/")
    return (
        "<!doctype html>\n"
        f'<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        f"<title>{esc(title)}</title>\n<style>{PAGE_CSS}</style>\n"
        f'<div class="sheet" lang="{esc(lang)}">\n{body}\n</div>\n'
        f'<script type="application/json" id="pv-data">{payload}</script>\n'
        f"<script>{PAGE_JS}</script>\n"
    )
