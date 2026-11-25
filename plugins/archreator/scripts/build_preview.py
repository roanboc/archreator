#!/usr/bin/env python3
"""Show what a change claims, as views a person can confirm where they are.

A preview is what the Requester is shown before a change lands: what is now
true about their subject that was not before, and every call taken for them.
`conversation-previews` says what it holds. This draws the part of it a table
cannot carry - the changed elements, and what they touch.

    build_preview.py --project .
    build_preview.py --project . --base main --question "Does a walk-in count as a booking?" \\
        --option "Yes" --option "No, it is its own thing" --default 2
    build_preview.py --project . --about why --about abilities
    build_preview.py --project . --stdout          # the Markdown, for a conversation that takes it

**It compares two readings of the model and draws the difference.** The
branch as it stands on disk, and the commit it left the default branch at.
Both are parsed fresh with the same parser, so nothing here can disagree with
the validators about what an element is.

**It writes three carriers, because a conversation renders what it renders.**
A page for a host that can show one beside the conversation, a picture for one
that shows images, and Markdown with the diagram's source for one that renders
a fence. The table under each is always readable. All three land in
`.archreator/work/previews/`, disposable, never committed.

**Nothing in them is the model's own notation.** No identifier, no glyph, no
layer number: elements are named as their documents name them and grouped by
the question each answers. The Requester is shown their business, not the
model of it. A reader who wants the rows opens the branch.

**Nothing here is summarized or judged.** What changed is what the two
readings differ in; a cell is quoted as written. The one sentence of why is
the first paragraph of the scope document the branch added, and the question,
where there is one, is the agent's and is passed in.
"""
import argparse
import importlib.util
import io
import re
import subprocess
import sys
import tarfile
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


# --------------------------------------------------------------------------
# This tool runs from the plugin and reads a project, exactly as `model.py`
# and `build_brief.py` do: the parse it needs lives in that project's
# `scripts/`, and one copy of it is the point.
# --------------------------------------------------------------------------
def _project_root(argv: list[str]) -> Path:
    for index, argument in enumerate(argv):
        if argument == "--project" and index + 1 < len(argv):
            return Path(argv[index + 1]).resolve()
        if argument.startswith("--project="):
            return Path(argument.split("=", 1)[1]).resolve()
    return Path.cwd().resolve()


def _find_parse(root: Path) -> Path | None:
    """The project's parse - beside it, or at the enclosing repository root."""
    if not root.is_dir():
        return None
    for candidate in (root, *root.parents):
        parse = candidate / "scripts" / "model_graph.py"
        if parse.is_file():
            if candidate != root and not (root / "architecture").is_dir():
                return None
            return parse
        if (candidate / ".git").exists():
            return None
    return None


_ROOT = _project_root(sys.argv[1:])
_PARSE = _find_parse(_ROOT)
if _PARSE is None:
    if {"-h", "--help"} & set(sys.argv[1:]):
        print(__doc__)
        sys.exit(0)
    sys.exit(
        f"No archreator project at {_ROOT}: expected a directory holding "
        f"architecture/, with scripts/model_graph.py beside it or at the "
        f"enclosing repository root.\n"
        f"Run this from a project's root, or pass --project <path>."
    )
sys.path.insert(0, str(_PARSE.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import model_graph  # noqa: E402
import plain_view as pv  # noqa: E402

REPO = model_graph.REPO_ROOT
DERIVED = _ROOT / ".archreator" / "work" / "previews"
# Past this many changed elements one picture stops being one screen, and the
# preview is drawn as one view per question instead.
ONE_VIEW = 24
# How many unchanged neighbours a view carries for context before it says it
# left some out.
CONTEXT = 6

ABOUT = {
    "customers": "Canvas (VPC)", "model": "Canvas (BMC)", "why": "Motivation",
    "abilities": "Strategy", "business": "Business", "information": "Information",
    "software": "Application", "platform": "Technology", "heading": "Implementation & Migration",
}
_ID = r"(?:[A-Z][A-Z0-9_]*\.)*[A-Z]{1,5}\d+(?:\.\d+)*"
_ID_LIST = re.compile(r"[\s,;/·+&—–\-\[\]]*(?:" + _ID + r"[\s,;/·+&—–\-\[\]]*)+")
# A cell that records where a row came from rather than what is true of the
# subject: an interpretation the agent adopted, or a confirmation given.
_PROVENANCE = re.compile(r"^\W*(?:adopted|confirmed|adoptad[oa]|confirmad[oa])\b", re.I)
_CALL = re.compile(r"^\W*(?:adopted|adoptad[oa])\s*[—–:\-]+\s*(.+)$", re.I | re.S)


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True, check=False)


def base_of(explicit: str | None) -> str:
    """The commit this branch left the default branch at, or "" with none.

    The merge base, never the tip: the question is what this branch changed,
    not what the default branch has done since.
    """
    candidates = [explicit] if explicit else ["origin/HEAD", "origin/main", "origin/master", "main", "master"]
    for candidate in candidates:
        found = git("merge-base", "HEAD", candidate)
        if found.returncode == 0 and found.stdout.strip():
            return found.stdout.strip()
        if explicit:
            exact = git("rev-parse", "--verify", f"{candidate}^{{commit}}")
            if exact.returncode == 0:
                return exact.stdout.strip()
    return ""


def snapshot(ref: str, into: Path) -> bool:
    """Every model the repository held at `ref`, written out under `into`."""
    listing = git("ls-tree", "-r", "--name-only", "-z", ref)
    roots: set[str] = set()
    for name in listing.stdout.split("\0"):
        parts = name.split("/")
        if name.endswith(".md") and model_graph.MODEL_DIR in parts[:-1]:
            roots.add("/".join(parts[: parts.index(model_graph.MODEL_DIR) + 1]))
    if not roots:
        return False
    archive = subprocess.run(
        ["git", "-C", str(REPO), "archive", "--format=tar", ref, "--", *sorted(roots)],
        capture_output=True, check=False,
    )
    if archive.returncode != 0:
        return False
    with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tar:
        try:
            tar.extractall(into, filter="data")
        except TypeError:  # pragma: no cover - a Python without extraction filters
            tar.extractall(into)
    return True


def parser_at(root: Path):
    """A second copy of the project's parser, pointed at another tree.

    The parser reads the repository it was loaded from. Loading the same file
    again under another name, and telling that copy where its repository is,
    is what lets one process read the branch and its base without either
    reading the other's files.
    """
    spec = importlib.util.spec_from_file_location("model_graph_base", _PARSE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.REPO_ROOT = root
    return module


def read(graph) -> dict:
    """Every model the parser finds, keyed as the parser keys it."""
    found = {}
    for project in graph.find_projects():
        parsed = graph.parse_project(project, detail=True)
        if parsed.elements:
            found[graph.project_key(project)] = parsed
    return found


def names_of(models: dict, here: str) -> dict[str, str]:
    """Identifier to name, for this model and - qualified - its neighbours."""
    names: dict[str, str] = {}
    for key, parsed in models.items():
        for element in parsed.elements.values():
            names[f"{key}::{element.id}"] = element.name
            if key == here:
                names[element.id] = element.name
                names.setdefault(element.local, element.name)
    return names


def say(value: str, names: dict[str, str]) -> str:
    """A cell in words. An identifier the model knows becomes its name."""
    def known(match: re.Match) -> str:
        return names.get(match.group(1), match.group(0))
    out = re.sub(r"\[(" + _ID + r")\]\s*", lambda m: "" if m.group(1) in names else m.group(0), value or "")
    out = re.sub(r"(?<![\w.])(" + _ID + r")(?![\w])", known, out)
    return pv.plain(out, names)


def facts(element, names: dict[str, str]) -> tuple[dict[str, str], list[str]]:
    """What a row says about its element, and the calls recorded on it.

    A column of identifiers is a relationship and is drawn, not quoted. The
    cell that restates the name gives up only its gloss. A cell recording
    where the row came from is not a fact about the subject; an adopted call
    is lifted out of it, because that is what a Requester most needs to see.
    """
    told: dict[str, str] = {}
    calls: list[str] = []
    name = pv.plain(element.name)
    for header, value in element.attrs.items():
        if not value or _ID_LIST.fullmatch(value):
            continue
        call = _CALL.match(value)
        if call:
            calls.append(say(call.group(1), names))
        if _PROVENANCE.match(value):
            continue
        text = say(value, names)
        if name and text.lower().startswith(name.lower()):
            gloss = text[len(name):].lstrip(" :—–-.")
            if gloss:
                told[""] = gloss[0].upper() + gloss[1:]
            continue
        if text:
            told[header] = text
    return told, calls


def word_of(edge) -> str:
    if edge.origin == "identifier":
        return "includes"
    word = re.sub(r"\s+", " ", edge.rel or "").strip()
    return word[:1].lower() + word[1:] if word else "relates to"


def edge_key(project: str, edge) -> tuple[str, str, str]:
    far = f"{edge.dst_project}::{edge.dst}" if edge.dst_project else f"{project}::{edge.dst}"
    return f"{project}::{edge.src}", far, word_of(edge).lower()


def compare(head: dict, base: dict, here: str) -> dict:
    """What the branch says that its base did not, and the other way round."""
    now = head.get(here)
    was = base.get(here)
    now_el = {k: e for k, e in (now.elements.items() if now else []) if not e.retired}
    was_el = {k: e for k, e in (was.elements.items() if was else []) if not e.retired}
    now_names, was_names = names_of(head, here), names_of(base, here)

    status: dict[str, str] = {}
    cells: dict[str, list] = {}
    renamed: dict[str, str] = {}
    calls: list[tuple[str, str]] = []
    told_now = {k: facts(e, now_names) for k, e in now_el.items()}
    for key, element in now_el.items():
        told, said = told_now[key]
        if key not in was_el:
            status[key] = "new"
            cells[key] = [(label, text, "", False) for label, text in told.items()]
            calls += [(key, call) for call in said]
            continue
        before, _ = facts(was_el[key], was_names)
        moved = {label for label in [*told, *before] if told.get(label, "") != before.get(label, "")}
        old_name = pv.plain(was_el[key].name)
        if moved or old_name != pv.plain(element.name):
            status[key] = "changed"
            if old_name != pv.plain(element.name):
                renamed[key] = old_name
            # What moved leads, in the row's own order; a cell the change
            # emptied is still said, so a deletion cannot pass unseen.
            first = [(label, told.get(label, "") or "(taken out)", before.get(label, ""), True)
                     for label in dict.fromkeys([*told, *before]) if label in moved]
            cells[key] = first + [(label, text, "", False) for label, text in told.items() if label not in moved]
            calls += [(key, call) for call in said]
        else:
            cells[key] = [(label, text, "", False) for label, text in told.items()]
    for key, element in was_el.items():
        if key not in now_el:
            status[key] = "removed"
            told, _ = facts(element, was_names)
            cells[key] = [(label, text, "", False) for label, text in told.items()]

    now_edges = {edge_key(here, e): e for e in (now.edges if now else [])}
    was_edges = {edge_key(here, e): e for e in (was.edges if was else [])}
    edges: dict[tuple, tuple[str, object]] = {}
    for key, edge in now_edges.items():
        edges[key] = ("same" if key in was_edges else "new", edge)
    for key, edge in was_edges.items():
        if key not in now_edges:
            edges[key] = ("removed", edge)
    return {
        "here": here, "head": head, "base": base, "now": now_el, "was": was_el,
        "status": status, "cells": cells, "renamed": renamed, "calls": calls, "edges": edges,
    }


def element_at(diff: dict, qualified: str):
    """The element a qualified key names, on the branch first, then its base."""
    project, _, local = qualified.partition("::")
    for side in (diff["head"], diff["base"]):
        parsed = side.get(project)
        if parsed and local in parsed.elements:
            return parsed.elements[local]
    return None


def views(diff: dict, about: set[str]) -> tuple[list[dict], dict, int, dict]:
    """The pictures the change needs: one, or one per question when it is large."""
    here = diff["here"]
    moved = {f"{here}::{k}": s for k, s in diff["status"].items()}
    links = []
    for (src, dst, _), (state, edge) in diff["edges"].items():
        if element_at(diff, src) is None or element_at(diff, dst) is None:
            continue
        links.append((src, dst, state, edge))
        if state != "same":
            moved.setdefault(src, "same")
            moved.setdefault(dst, "same")
    # `moved` now holds every element the change touched: those it added,
    # changed or removed, and the ends of every relationship it did.
    def group(key: str) -> str:
        return element_at(diff, key).group

    focus = {k for k in moved if not about or group(k) in about}
    left_out = 0
    # The drawing, the page and the diagram source name an element by a short
    # key of their own, so nothing a reader can open carries an identifier.
    short: dict[str, str] = {}

    def key_of(qualified: str) -> str:
        return short.setdefault(qualified, f"n{len(short) + 1}")

    def build(members: set[str], partners: set[str], title: str) -> dict:
        shown = members | partners
        nodes, edges = [], []
        for key in sorted(shown):
            element = element_at(diff, key)
            project, _, local = key.partition("::")
            mine = project == here
            nodes.append({
                "key": key_of(key), "name": pv.plain(element.name) or "(unnamed)",
                "kind": pv.kind_of(element.type), "group": element.group,
                "status": moved.get(key, "same") if mine else "same",
                "was": diff["renamed"].get(local, "") if mine else "",
                "detail": diff["cells"].get(local, []) if mine else [],
            })
        for src, dst, state, edge in links:
            if src in shown and dst in shown and (state != "same" or src in members or dst in members):
                edges.append({"a": key_of(src), "b": key_of(dst), "word": word_of(edge),
                              "status": state, "pending": edge.pending})
        return {"title": title, "nodes": nodes, "edges": edges}

    def neighbours(members: set[str], pool: set[str] | None, limit: int) -> tuple[set[str], int]:
        degree: dict[str, int] = defaultdict(int)
        for src, dst, state, _ in links:
            for a, b in ((src, dst), (dst, src)):
                if a in members and b not in members and (pool is None or b in pool):
                    degree[b] += 4 if state != "same" else (2 if group(a) != group(b) else 1)
        ranked = sorted(degree, key=lambda k: (-degree[k], k))
        return set(ranked[:limit]), max(0, len(ranked) - limit)

    out: list[dict] = []
    if len(focus) <= ONE_VIEW:
        context, left_out = neighbours(focus, None, CONTEXT)
        if focus:
            out.append(build(focus, context, "What changes"))
    else:
        by_group: dict[str, set[str]] = defaultdict(set)
        for key in focus:
            by_group[group(key)].add(key)
        for name in sorted(by_group, key=lambda g: pv.ORDER.get(g, 99)):
            partners, more = neighbours(by_group[name], set(moved), CONTEXT)
            left_out += more
            out.append(build(by_group[name], partners, pv.HEADING.get(name, name)))
    return out, {key: state for key, state in moved.items()}, left_out, short


def scope_note(base: str) -> tuple[str, str]:
    """(title, first paragraph) of the scope document this branch added.

    The method writes one before implementing, and its opening paragraph is
    what the initiative changes and why. That is the preview's one sentence
    of why, in words somebody already wrote on the branch.
    """
    folder = _ROOT / model_graph.MODEL_DIR / "scope"
    if not folder.is_dir():
        return "", ""
    rel = str(folder.relative_to(REPO)).replace("\\", "/")
    changed = set()
    if base:
        changed |= set(git("diff", "--name-only", base, "--", rel).stdout.split())
    changed |= set(git("ls-files", "--others", "--exclude-standard", "--", rel).stdout.split())
    numbered = []
    for name in changed:
        match = re.match(r"(\d+)_.+\.md$", Path(name).name)
        if match and (REPO / name).is_file():
            numbered.append((int(match.group(1)), REPO / name))
    if not numbered:
        return "", ""
    text = max(numbered)[1].read_text(encoding="utf-8")
    title = ""
    for block in re.split(r"\n\s*\n", text):
        block = block.strip()
        if not title:
            if block.startswith("# "):
                title = block.splitlines()[0][2:].split(" — ", 1)[-1].strip()
            continue
        # The nav line, the viewpoint and delivery lines, a table, a heading:
        # none of them is the paragraph that says what changes and why.
        if not block or block.startswith(("_[", "**", "<!--", "|", "#", "```", ">")):
            continue
        return title, " ".join(line.strip() for line in block.splitlines())
    return title, ""


def stamp_of(base: str) -> str:
    branch = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    revision = git("rev-parse", "--short", "HEAD").stdout.strip()
    if not revision:
        return "Read from the files as they stand, outside a repository"
    rel = "." if _ROOT == REPO else str(_ROOT.relative_to(REPO))
    dirty = bool(git("status", "--porcelain", "--", rel).stdout.strip())
    when = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    said = f"Branch {branch} at {revision}"
    if dirty:
        said += ", with changes not yet committed"
    if base:
        said += f", compared with {base[:7]}"
    return f"{said} · {when}"


def counts(moved: dict) -> dict[str, int]:
    tally = {"new": 0, "changed": 0, "removed": 0}
    for state in moved.values():
        if state in tally:
            tally[state] += 1
    return tally


def sentence(tally: dict[str, int], relations: dict[str, int]) -> str:
    """The change in one line: how many things, then how many connections."""
    parts = [f"{tally[state]} {state}" for state in ("new", "changed", "removed") if tally[state]]
    said = (", ".join(parts) if parts else "Nothing added, changed or removed") + "."
    links = []
    if relations["new"]:
        links.append(f'{relations["new"]} new connection{"" if relations["new"] == 1 else "s"}')
    if relations["removed"]:
        links.append(f'{relations["removed"]} taken away')
    if links:
        said += " " + (links[0][0].upper() + links[0][1:] if len(links) == 1 and relations["removed"] and not relations["new"]
                       else ", ".join(links)).replace("taken away", "connection taken away" if not relations["new"] else "taken away") + "."
    return said


def listed(diff: dict, moved: dict, state: str) -> list[dict]:
    here = diff["here"]
    rows = []
    for key, value in moved.items():
        if value != state or not key.startswith(here + "::"):
            continue
        element = element_at(diff, key)
        local = key.partition("::")[2]
        rows.append({
            "key": key, "name": pv.plain(element.name), "kind": pv.kind_of(element.type),
            "was": diff["renamed"].get(local, ""), "cells": diff["cells"].get(local, []),
        })
    return sorted(rows, key=lambda r: r["name"].lower())


def markdown(title, stamp, why, drawn, diff, moved, summary, calls, ask, left_out) -> str:
    out = [f"## {title}", "", f"_{stamp}._", ""]
    if why:
        out += [why, ""]
    out += [summary, ""]
    for view in drawn:
        if len(drawn) > 1:
            out += [f"### {view['title']}", ""]
        out += ["```mermaid", pv.mermaid(view["nodes"], view["edges"]), "```", ""]
    if left_out:
        out += [f"_{left_out} unchanged thing(s) that touch these are not drawn._", ""]
    for state, heading in (("new", "New"), ("changed", "Changed"), ("removed", "Removed")):
        rows = listed(diff, moved, state)
        if not rows:
            continue
        out.append(f"**{heading}**")
        out.append("")
        for row in rows:
            line = f"- **{row['name']}** ({row['kind']})"
            if row["was"]:
                line += f" — was “{row['was']}”"
            told = []
            for label, text, old, was_moved in row["cells"]:
                if state == "changed" and not was_moved:
                    continue
                piece = f"{label}: " if label else ""
                if old:
                    told.append(f"{piece}“{old}” → “{text}”")
                else:
                    told.append(f"{piece}{'added — ' if was_moved else ''}{text}")
            if told and state != "removed":
                line += ". " + " · ".join(told[:3])
            out.append(line)
        out.append("")
    if calls:
        out += ["**Calls taken for you**", ""]
        out += [f"- **{name}** — {call}" for name, call in calls]
        out.append("")
    if ask["question"]:
        out += ["**One question**", "", ask["question"], ""]
        for index, option in enumerate(ask["options"], start=1):
            mine = " _(what was assumed)_" if index == ask["default"] else ""
            out.append(f"{index}. {option}{mine}")
        if ask["options"]:
            out.append("")
    else:
        out += ["**Nothing is needed from you.** Say so if something here is not true.", ""]
    return "\n".join(out).rstrip() + "\n"


def page(title, stamp, why, drawn, diff, moved, summary, calls, ask, left_out, short) -> str:
    e = pv.esc
    data_nodes: dict[str, dict] = {}
    body = [f'<p class="stamp">{e(stamp)}</p>', f"<h1>{e(title)}</h1>"]
    if why:
        body.append(f'<p class="why">{e(why)}</p>')
    body.append('<div class="stage"><div>')
    for index, view in enumerate(drawn):
        picture = pv.svg(view["nodes"], view["edges"], title=view["title"], uid=f"v{index}")
        width = int(float(re.search(r'viewBox="0 0 (\d+)', picture).group(1)) * 0.74)
        body.append('<figure class="view">')
        if len(drawn) > 1:
            body.append(f"<h2>{e(view['title'])}</h2>")
        caption = summary if len(drawn) == 1 else ""
        if index == len(drawn) - 1 and left_out:
            caption += f" {left_out} unchanged thing(s) that touch these are not drawn."
        body.append(f'<div class="drawing" style="--min:{width}px">{picture}</div>')
        if caption:
            body.append(f"<figcaption>{e(caption.strip())} Select anything in the drawing to read it.</figcaption>")
        body.append("</figure>")
        names = {n["key"]: n["name"] for n in view["nodes"]}
        for node in view["nodes"]:
            entry = data_nodes.setdefault(node["key"], {
                "name": node["name"], "kind": node["kind"], "where": pv.HEADING.get(node["group"], node["group"]),
                "status": node["status"], "was": node["was"],
                "detail": [list(cell) for cell in node["detail"]], "links": [],
            })
            seen = {(l["to"], l["word"], l["out"]) for l in entry["links"]}
            for edge in view["edges"]:
                for mine, other, out in ((edge["a"], edge["b"], True), (edge["b"], edge["a"], False)):
                    if mine == node["key"] and (other, edge["word"], out) not in seen:
                        seen.add((other, edge["word"], out))
                        entry["links"].append({"to": other, "name": names.get(other, ""), "word": edge["word"],
                                               "out": out, "status": edge["status"]})
    if not drawn:
        body.append(f'<p class="why">{e(summary)}</p>')
    body.append('</div><aside class="reading" id="pv-reading" aria-live="polite"></aside></div>')

    body.append('<div class="lists">')
    for state, heading in (("new", "New"), ("changed", "Changed"), ("removed", "Removed")):
        rows = listed(diff, moved, state)
        if not rows:
            continue
        body.append(f"<section><h2>{heading} · {len(rows)}</h2><ul>")
        for row in rows:
            item = f'<li><strong>{e(row["name"])}</strong> <span class="kind">{e(row["kind"])}</span>'
            if row["was"]:
                item += f'<p><span class="was">{e(row["was"])}</span></p>'
            for label, text, old, was_moved in row["cells"]:
                if state == "removed":
                    break
                if state == "changed" and not was_moved:
                    continue
                lead = f"{e(label)}: " if label else ""
                if old:
                    item += f'<p>{lead}<span class="was">{e(old)}</span> → {e(text)}</p>'
                else:
                    item += f"<p>{lead}{'<em>added</em> — ' if was_moved else ''}{e(text)}</p>"
            body.append(item + "</li>")
        body.append("</ul></section>")
    body.append("</div>")
    if calls:
        body.append('<section class="calls"><h2>Calls taken for you</h2><ul>')
        body += [f"<li><strong>{e(name)}</strong> — {e(call)}</li>" for name, call in calls]
        body.append("</ul></section>")
    body.append('<section class="ask">')
    if ask["question"]:
        body.append(f"<h2>One question</h2><p>{e(ask['question'])}</p>")
        if ask["options"]:
            body.append("<ol>")
            for index, option in enumerate(ask["options"], start=1):
                mine = ' <span class="mine">— what was assumed</span>' if index == ask["default"] else ""
                body.append(f"<li>{e(option)}{mine}</li>")
            body.append("</ol>")
        body.append('<p class="how">Answer in the conversation, in your own words if none of these fits.</p>')
    else:
        body.append("<h2>Nothing is needed from you</h2><p>Say so in the conversation if something here is not true.</p>")
    body.append("</section>")
    body.append(
        "<footer>This page is one reading of the branch, made to be confirmed and then thrown away. "
        "The repository stays the record: when something here is wrong, the files change first and the "
        "page is made again from them.</footer>"
    )
    start = next((short[k] for state in ("new", "changed", "removed") for k, v in moved.items()
                  if v == state and short.get(k) in data_nodes), next(iter(data_nodes), ""))
    return pv.page(title=title, body="\n".join(body),
                   data={"mode": "change", "nodes": data_nodes, "start": start, "first": {}})


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):  # pragma: no cover
            pass
    parser = argparse.ArgumentParser(
        description="Show what a change claims, as views a person can confirm where they are.")
    parser.add_argument("--project", default=".", help="the project to read (default: the current directory)")
    parser.add_argument("--base", help="what to compare the branch with (default: where it left the default branch)")
    parser.add_argument("--about", action="append", choices=sorted(ABOUT), default=[],
                        help="narrow the preview to one question; repeatable")
    parser.add_argument("--title", help="the preview's heading (default: the scope document's title)")
    parser.add_argument("--why", help="the one sentence of why (default: the scope document's first paragraph)")
    parser.add_argument("--question", help="the one question that needs the Requester's answer")
    parser.add_argument("--option", action="append", default=[], help="an answer the model already allows; repeatable")
    parser.add_argument("--default", type=int, default=0, help="which option, counted from 1, was assumed")
    parser.add_argument("--stamp", help="replace the line naming the branch and revision")
    parser.add_argument("--name", help="the file name to write under, without an extension")
    parser.add_argument("--to", type=Path, default=DERIVED, help="where to write the preview")
    parser.add_argument("--stdout", action="store_true", help="print the Markdown instead of writing files")
    args = parser.parse_args()

    here = model_graph.project_key(_ROOT)
    head = read(model_graph)
    if here not in head:
        print(f"{_ROOT} defines no elements yet - there is nothing to preview.")
        return 1
    base = base_of(args.base)
    if args.base and not base:
        print(f"`{args.base}` names no commit in this repository.")
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        before = read(parser_at(Path(tmp))) if base and snapshot(base, Path(tmp)) else {}
        diff = compare(head, before, here)
    drawn, moved, left_out, short = views(diff, {ABOUT[a] for a in args.about})

    names = names_of(head, here)
    noted_title, noted_why = scope_note(base)
    title = args.title or noted_title or f"What changes about {_ROOT.name}"
    why = args.why if args.why is not None else say(noted_why, names)
    stamp = args.stamp or stamp_of(base)
    mine = {k: v for k, v in moved.items() if k.startswith(here + "::")}
    relations = {"new": 0, "removed": 0}
    for state, _ in diff["edges"].values():
        if state in relations:
            relations[state] += 1
    summary = sentence(counts(mine), relations)
    calls = [(pv.plain(diff["now"][key].name), call) for key, call in diff["calls"]]
    ask = {"question": args.question or "", "options": args.option, "default": args.default}

    text = markdown(title, stamp, why, drawn, diff, moved, summary, calls, ask, left_out)
    if args.stdout:
        print(text)
        return 0
    branch = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip() or "working-tree"
    slug = re.sub(r"[^\w.-]+", "-", args.name or branch).strip("-").lower() or "preview"
    args.to.mkdir(parents=True, exist_ok=True)
    written = []
    (args.to / f"{slug}.md").write_text(text, encoding="utf-8")
    written.append(args.to / f"{slug}.md")
    for index, view in enumerate(drawn):
        suffix = "" if len(drawn) == 1 else f"-{index + 1}"
        picture = pv.svg(view["nodes"], view["edges"], title=view["title"], uid=f"v{index}")
        (args.to / f"{slug}{suffix}.svg").write_text(picture, encoding="utf-8")
        written.append(args.to / f"{slug}{suffix}.svg")
    (args.to / f"{slug}.html").write_text(
        page(title, stamp, why, drawn, diff, moved, summary, calls, ask, left_out, short), encoding="utf-8")
    written.append(args.to / f"{slug}.html")

    print(summary)
    if not base:
        print("No base to compare with, so everything the model holds is shown as new.")
    for path in written:
        print(f"  {path.relative_to(REPO) if path.is_relative_to(REPO) else path}")
    print("Show the richest of these the conversation renders: the page, else the picture, "
          "else the Markdown. Disposable - the branch stays the record.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
