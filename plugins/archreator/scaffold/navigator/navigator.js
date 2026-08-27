/* The model as a graph somebody can read, search and keep.
 *
 * Four things here are deliberate and worth knowing before changing anything.
 *
 * **The traversal is not written here.** Walking outward from an element runs
 * `neighbourhood.sql`, the same file `query_model.py` executes for `trace`. A
 * walk implemented once in Python and once in JavaScript drifts, and the copy
 * that drifts is this one, because nothing tests a browser.
 *
 * **There are no libraries.** sql.js is unavoidable — reading SQLite in a
 * browser needs it — and it is fetched at build time, pinned and verified.
 * Everything else, layout included, is written here rather than pulled in.
 *
 * **Nothing here writes to the model.** The page reads a projection and stores
 * a reader's own views in their own browser. A view is a lens; the Markdown is
 * the model. That boundary is what makes it safe to hand this to anyone.
 *
 * **Nothing here summarises.** An excerpt is the paragraph the document
 * contains. A panel that paraphrased would be a second model with no way to
 * tell it had drifted.
 */
(function () {
  "use strict";

  /* ---- constants --------------------------------------------------------- */

  var PALETTE = {
    "Motivation": "--motivation",
    "Strategy": "--strategy",
    "Business": "--business",
    "Information": "--information",
    "Application": "--application",
    "Technology": "--technology",
    "Implementation & Migration": "--implementation",
    "Canvas (VPC)": "--canvas",
    "Canvas (BMC)": "--canvas"
  };
  // The order the method reads its own layers in — `architecture/README.md`
  // § Layers, in assessment order. The layered view is that order made
  // vertical, which is the whole reason it answers a different question from
  // the force view.
  var LAYER_ORDER = [
    "Motivation", "Strategy", "Business", "Information",
    "Application", "Technology", "Implementation & Migration",
    "Canvas (VPC)", "Canvas (BMC)"
  ];
  // Glyph per element type, from `architecture/README.md` § Element glyphs.
  // Carried here because the projection types a prefix and does not carry its
  // glyph; a missing one degrades to no glyph, never to a wrong one.
  var GLYPHS = {
    "Stakeholder": "◍", "Driver": "✳", "Assessment": "⌕", "Goal": "◎",
    "Outcome": "◉", "Principle": "⚑",
    "Capability": "✦", "Resource": "▤", "Course of Action": "➤", "Value Stream": "⇉",
    "Actor": "⚇", "Role": "⚉", "Business Collaboration": "⧉", "Product": "▣",
    "Business Service": "⬭", "Business Process": "⚙", "Business Object": "▧",
    "Business Interface": "⊸", "Contract": "❒", "Business Rule": "⚖", "Value": "◈",
    "Data Object": "▦",
    "Application Service": "⬮", "Application Component": "⊞",
    "Technology Service": "⬯", "Node": "⬒", "Artifact": "⎔",
    "Plateau": "≡", "Gap": "⊘",
    "Job": "⚙", "Pain": "✖", "Gain": "✔", "Pain Reliever": "⊖", "Gain Creator": "⊕",
    "Key Partner": "⧉", "Key Activity": "⚙", "Key Resource": "▤",
    "Value Proposition": "◈", "Customer Relationship": "⇄", "Channel": "⊸",
    "Customer Segment": "◍", "Revenue Stream": "▲", "Cost": "▼"
  };
  var BOX_W_MAX = 226, BOX_W_MIN = 78, BOX_H = 34, BOX_H2 = 46, PAD = 9;
  var FACETS = ["type", "layer", "model", "status", "grounded"];
  var STORE = "archreator.navigator.views";

  /* ---- state ------------------------------------------------------------- */

  var svg = document.getElementById("graph");
  var statusBox = document.getElementById("status");
  var detail = document.getElementById("detail");
  var controls = document.getElementById("controls");
  var qInput = document.getElementById("q");
  var suggest = document.getElementById("suggest");

  var db = null, sql = "", SQLjs = null;
  var project = "";
  var nodes = [], edges = [], byGid = {};
  var view = null, root = null, depth = 2;
  var hidden = new Set(), pinned = {}, positions = {};
  var camera = { x: 0, y: 0, k: 1 };
  var layoutMode = "layered";
  var unreachable = [], history = [], historyAt = -1, suppressHistory = false;
  var hits = new Set();          // search results, highlighted
  var ownHash = "";              // the hash this page last wrote itself
  var suggestIndex = -1, suggestItems = [];

  /* ---- small helpers ----------------------------------------------------- */

  function say(html, fail) {
    statusBox.classList.remove("hidden");
    statusBox.innerHTML = fail ? '<div class="fail">' + html + "</div>" : html;
  }
  function clearStatus() { statusBox.classList.add("hidden"); }
  function css(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }
  function colour(group) { return css(PALETTE[group] || "--canvas") || "#ccc"; }
  function esc(text) {
    return String(text == null ? "" : text).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  /* An excerpt is Markdown, because the document it came from is. This renders
   * the inline marks a paragraph actually uses and nothing else — bold, code,
   * links, em-dashes stay as they are. It escapes first and marks up second,
   * so nothing in a document can inject markup into this page.
   *
   * A link becomes its text: the target is a repository-relative path that
   * means nothing from here, and a link that goes nowhere is worse than none. */
  function markdown(text) {
    return esc(text)
      .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1")
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/(^|[\s(])\*([^*]+)\*/g, "$1<em>$2</em>");
  }

  var measurer = document.createElement("canvas").getContext("2d");
  function textWidth(text, font) {
    measurer.font = font;
    return measurer.measureText(text).width;
  }
  function rows(query, params) {
    var out = [], statement = db.prepare(query);
    if (params) statement.bind(params);
    while (statement.step()) out.push(statement.getAsObject());
    statement.free();
    return out;
  }

  /* ---- data -------------------------------------------------------------- */

  function loadAll() {
    nodes = rows(
      "SELECT project || '::' || id AS gid, project, id, name, type," +
      " layer_group AS grp, layer_no, doc, status, realized_by, retired, domain, attrs" +
      " FROM nodes ORDER BY project, id");
    edges = rows(
      "SELECT project || '::' || src AS src," +
      " CASE WHEN dst_project = '' THEN project ELSE dst_project END || '::' || dst AS dst," +
      " rel, origin, pending FROM edges");
    byGid = {};
    nodes.forEach(function (n) {
      n.label = n.name || n.id;
      var glyphRoom = (GLYPHS[n.type] ? 13 : 0);
      var wanted = Math.max(textWidth(n.label, "600 11px system-ui") + glyphRoom,
                            textWidth(n.id, "9px ui-monospace"));
      n.w = Math.max(BOX_W_MIN, Math.min(BOX_W_MAX, wanted + PAD * 2));
      // A name that will not fit on one line gets two before it gets an
      // ellipsis. Most element names are short phrases, and cutting one in
      // half to save twelve pixels of height is a bad trade in a page whose
      // whole point is that the names are readable.
      n.lines = wrap(n.label, n.w - PAD * 2 - glyphRoom, "600 11px system-ui", 2);
      n.h = n.lines.length > 1 ? BOX_H2 : BOX_H;
      byGid[n.gid] = n;
    });
  }

  function excerptsFor(node) {
    return rows("SELECT doc, heading, body FROM excerpts WHERE project = :p AND element = :e",
      { ":p": node.project, ":e": node.id });
  }
  function relationsFor(node) {
    return rows(
      "SELECT rel, origin, pending, 'out' AS way," +
      " CASE WHEN dst_project = '' THEN project ELSE dst_project END || '::' || dst AS other" +
      " FROM edges WHERE project = :p AND src = :i" +
      " UNION ALL SELECT rel, origin, pending, 'in', project || '::' || src" +
      " FROM edges WHERE (CASE WHEN dst_project = '' THEN project ELSE dst_project END) = :p" +
      "   AND dst = :i", { ":p": node.project, ":i": node.id });
  }

  /* ---- layout ------------------------------------------------------------ */

  function shownNodes() { return nodes.filter(visible); }

  function layout() {
    var live = shownNodes();
    if (!live.length) { positions = {}; return; }
    if (layoutMode === "layered") layered(live);
    else force(live);
    Object.keys(pinned).forEach(function (gid) {
      if (positions[gid]) {
        positions[gid].x = pinned[gid][0];
        positions[gid].y = pinned[gid][1];
      }
    });
  }

  /* One row per layer, in the order the method assesses them. This is the
   * view that answers "what realizes what": an edge that goes up the page is
   * a realization, and one that stays in a row is a peer relationship. */
  function layered(live) {
    var lanes = {}, order = [];
    live.forEach(function (n) {
      var key = n.grp || "—";
      if (!lanes[key]) { lanes[key] = []; order.push(key); }
      lanes[key].push(n);
    });
    order.sort(function (a, b) {
      var ia = LAYER_ORDER.indexOf(a), ib = LAYER_ORDER.indexOf(b);
      return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib);
    });
    positions = {};
    var y = 0, laneWidth = 0;
    order.forEach(function (key) {
      var members = lanes[key];
      // Wrap a crowded lane rather than letting it run off the canvas: about
      // as wide as it is tall keeps a lane readable at a glance.
      var perRow = Math.max(1, Math.ceil(Math.sqrt(members.length * 2.6)));
      var x = 0, rowTop = y, col = 0;
      members.forEach(function (n) {
        positions[n.gid] = { x: x + n.w / 2, y: rowTop + BOX_H2 / 2, vx: 0, vy: 0 };
        x += n.w + 14; col++;
        if (col >= perRow) { col = 0; x = 0; rowTop += BOX_H2 + 14; }
        laneWidth = Math.max(laneWidth, x);
      });
      var rowsUsed = Math.ceil(members.length / perRow);
      lanes[key] = { top: y, height: rowsUsed * (BOX_H2 + 14), label: key };
      y += rowsUsed * (BOX_H2 + 14) + 34;
    });
    positions.__lanes = order.map(function (k) { return lanes[k]; });
    positions.__laneWidth = laneWidth;
  }

  function force(live) {
    var count = live.length || 1, radius = Math.sqrt(count) * 62;
    positions = {};
    live.forEach(function (n, i) {
      var a = (i / count) * Math.PI * 2;
      positions[n.gid] = { x: Math.cos(a) * radius, y: Math.sin(a) * radius, vx: 0, vy: 0 };
    });
    var links = edges.filter(function (e) { return positions[e.src] && positions[e.dst]; });
    for (var tick = 0; tick < 300; tick++) {
      var cooling = 1 - tick / 300;
      for (var a = 0; a < live.length; a++) {
        for (var b = a + 1; b < live.length; b++) {
          var p = positions[live[a].gid], q = positions[live[b].gid];
          var dx = q.x - p.x, dy = q.y - p.y;
          var d2 = dx * dx + dy * dy || 0.01, d = Math.sqrt(d2);
          // Boxes are wide, so they repel by their width rather than as points.
          var f = (5200 + (live[a].w + live[b].w) * 12) / d2;
          var fx = (dx / d) * f, fy = (dy / d) * f;
          p.vx -= fx; p.vy -= fy; q.vx += fx; q.vy += fy;
        }
      }
      links.forEach(function (l) {
        var p = positions[l.src], q = positions[l.dst];
        var dx = q.x - p.x, dy = q.y - p.y;
        var d = Math.sqrt(dx * dx + dy * dy) || 0.01;
        var pull = (d - 150) * 0.02;
        p.vx += (dx / d) * pull; p.vy += (dy / d) * pull;
        q.vx -= (dx / d) * pull; q.vy -= (dy / d) * pull;
      });
      live.forEach(function (n) {
        var p = positions[n.gid];
        p.vx -= p.x * 0.0016; p.vy -= p.y * 0.0016;
        p.x += p.vx * cooling; p.y += p.vy * cooling;
        p.vx *= 0.82; p.vy *= 0.82;
      });
    }
  }

  function fit(ids) {
    var xs = [], ys = [];
    (ids || shownNodes().map(function (n) { return n.gid; })).forEach(function (gid) {
      var p = positions[gid], n = byGid[gid];
      if (!p || !n) return;
      xs.push(p.x - n.w / 2, p.x + n.w / 2);
      ys.push(p.y - n.h / 2, p.y + n.h / 2);
    });
    if (!xs.length) return;
    var box = svg.getBoundingClientRect();
    var minX = Math.min.apply(null, xs), maxX = Math.max.apply(null, xs);
    var minY = Math.min.apply(null, ys), maxY = Math.max.apply(null, ys);
    var w = maxX - minX || 1, h = maxY - minY || 1;
    camera.k = Math.max(0.08, Math.min((box.width - 90) / w, (box.height - 90) / h, 1.9));
    camera.x = box.width / 2 - ((maxX + minX) / 2) * camera.k;
    camera.y = box.height / 2 - ((maxY + minY) / 2) * camera.k;
  }

  function reframe() { layout(); fit(); render(); }
  function relayout() { layout(); fit(); render(); }

  /* ---- render ------------------------------------------------------------ */

  function visible(node) {
    if (hidden.has(node.grp || "")) return false;
    if (view) return view.has(node.gid);
    return node.project === project;
  }

  function render() {
    var showIdentifier = document.getElementById("show-identifier").checked;
    var showPending = document.getElementById("show-pending").checked;
    var showLabels = document.getElementById("show-labels").checked;
    var shown = {};
    shownNodes().forEach(function (n) { shown[n.gid] = n; });

    var parts = ['<g transform="translate(' + camera.x + ',' + camera.y +
      ') scale(' + camera.k + ')">'];

    if (layoutMode === "layered" && positions.__lanes) {
      positions.__lanes.forEach(function (lane) {
        parts.push('<text class="lane-label" x="-8" y="' + (lane.top - 8) + '">' +
          esc(lane.label) + "</text>");
        parts.push('<line class="lane" x1="-8" y1="' + (lane.top - 4) + '" x2="' +
          (positions.__laneWidth + 20) + '" y2="' + (lane.top - 4) + '"/>');
      });
    }

    var drawn = 0;
    edges.forEach(function (edge) {
      if (!shown[edge.src] || !shown[edge.dst]) return;
      if (edge.origin === "identifier" && !showIdentifier) return;
      if (edge.pending && !showPending) return;
      var p = positions[edge.src], q = positions[edge.dst];
      if (!p || !q) return;
      drawn++;
      var cls = "edge" + (edge.origin === "identifier" ? " identifier" : "") +
        (edge.pending ? " pending" : "");
      parts.push('<line class="' + cls + '" x1="' + p.x + '" y1="' + p.y +
        '" x2="' + q.x + '" y2="' + q.y + '"><title>' +
        esc(nameOf(edge.src) + " — " + edge.rel + " → " + nameOf(edge.dst)) +
        "</title></line>");
      if (showLabels) {
        parts.push('<text class="edge-label" text-anchor="middle" x="' +
          ((p.x + q.x) / 2) + '" y="' + ((p.y + q.y) / 2 - 2) + '">' +
          esc(edge.rel) + "</text>");
      }
    });

    Object.keys(shown).forEach(function (gid) {
      var n = shown[gid], p = positions[gid];
      if (!p) return;
      var glyph = GLYPHS[n.type] || "";
      var cls = "node" + (gid === root ? " root" : "") +
        (n.project !== project ? " elsewhere" : "") +
        (Number(n.retired) ? " retired" : "") + (hits.has(gid) ? " hit" : "");
      parts.push(
        '<g class="' + cls + '" data-id="' + esc(gid) + '" transform="translate(' +
        (p.x - n.w / 2) + "," + (p.y - n.h / 2) + ')">' +
        '<rect width="' + n.w + '" height="' + n.h + '" rx="4" fill="' +
        colour(n.grp) + '"></rect>' +
        (glyph ? '<text class="glyph" x="' + PAD + '" y="15">' + glyph + "</text>" : "") +
        n.lines.map(function (line, i) {
          return '<text class="name" x="' + (PAD + (glyph ? 13 : 0)) + '" y="' +
            (15 + i * 12) + '">' + esc(line) + "</text>";
        }).join("") +
        '<text class="id" x="' + PAD + '" y="' + (n.h - 7) + '">' + esc(n.id) + "</text>" +
        "<title>" + esc(n.gid + (n.name ? " · " + n.name : "") +
          (n.type ? "\n" + n.type : "")) + "</title></g>");
    });
    parts.push("</g>");
    svg.innerHTML = parts.join("");
    document.getElementById("counts").textContent =
      Object.keys(shown).length + " of " + nodes.length + " element(s), " +
      drawn + " relationship(s) shown." + (hits.size ? " " + hits.size + " matched." : "");
    clearStatus();
  }

  function wrap(text, width, font, maxLines) {
    if (textWidth(text, font) <= width) return [text];
    var words = text.split(" "), lines = [], line = "";
    words.forEach(function (word) {
      var next = line ? line + " " + word : word;
      if (textWidth(next, font) <= width || !line) line = next;
      else { lines.push(line); line = word; }
    });
    if (line) lines.push(line);
    if (lines.length <= maxLines) return lines;
    var kept = lines.slice(0, maxLines);
    kept[maxLines - 1] = clip(kept[maxLines - 1] + " " + lines[maxLines], width, font);
    return kept;
  }

  function clip(text, width, font) {
    if (textWidth(text, font) <= width) return text;
    var cut = text;
    while (cut.length > 1 && textWidth(cut + "…", font) > width) cut = cut.slice(0, -1);
    return cut + "…";
  }
  function nameOf(gid) {
    var n = byGid[gid];
    return n ? (n.name || n.id) : gid;
  }

  /* ---- search ------------------------------------------------------------
   *
   * No language model runs in a static page, so "intelligent" has to mean
   * structured and guiding rather than clever. The suggestions are the
   * guidance: a reader typing `type:` is shown the element types this model
   * actually has, with counts, and learns the vocabulary from the thing they
   * are searching — which is the only vocabulary that will match.
   */

  function facetValues(name) {
    var column = { type: "type", layer: "layer_group", model: "project", status: "status" }[name];
    if (name === "grounded") {
      return [
        { value: "yes", count: nodes.filter(function (n) { return n.realized_by; }).length },
        { value: "no", count: nodes.filter(function (n) { return !n.realized_by; }).length }
      ];
    }
    var counts = {};
    nodes.forEach(function (n) {
      var v = n[column === "layer_group" ? "grp" : column] || "";
      if (v) counts[v] = (counts[v] || 0) + 1;
    });
    return Object.keys(counts).sort().map(function (v) {
      return { value: v, count: counts[v] };
    });
  }

  function parseQuery(text) {
    var terms = [], free = [];
    text.split(/\s+/).forEach(function (part) {
      if (!part) return;
      var m = part.match(/^(\w+):(.*)$/);
      if (m && FACETS.indexOf(m[1].toLowerCase()) !== -1) {
        terms.push({ key: m[1].toLowerCase(), value: m[2].replace(/^"|"$/g, "").toLowerCase() });
      } else free.push(part.toLowerCase());
    });
    return { terms: terms, free: free.join(" ") };
  }

  function matches(node, q) {
    for (var i = 0; i < q.terms.length; i++) {
      var t = q.terms[i], got;
      if (t.key === "type") got = (node.type || "").toLowerCase();
      else if (t.key === "layer") got = (node.grp || "").toLowerCase();
      else if (t.key === "model") got = (node.project || "").toLowerCase();
      else if (t.key === "status") got = (node.status || "").toLowerCase();
      else if (t.key === "grounded") got = node.realized_by ? "yes" : "no";
      if (!t.value) continue;
      if (got.indexOf(t.value) === -1) return false;
    }
    if (!q.free) return true;
    return (node.id + " " + node.label + " " + (node.type || "")).toLowerCase()
      .indexOf(q.free) !== -1;
  }

  function runSearch(text) {
    var q = parseQuery(text);
    var found = text.trim() ? nodes.filter(function (n) { return matches(n, q); }) : [];
    hits = new Set(found.map(function (n) { return n.gid; }));
    return found;
  }

  function renderSuggest(text) {
    var caretWord = text.split(/\s+/).pop() || "";
    var facetOpen = caretWord.match(/^(\w+):(.*)$/);
    var html = [], items = [];

    // A facet whose value is already one this model has is finished, not being
    // typed — so show what it matched rather than repeating the menu.
    var settled = facetOpen && FACETS.indexOf(facetOpen[1].toLowerCase()) !== -1 &&
      facetValues(facetOpen[1].toLowerCase()).some(function (v) {
        return v.value.toLowerCase() === facetOpen[2].replace(/^"|"$/g, "").toLowerCase();
      });

    if (facetOpen && !settled && FACETS.indexOf(facetOpen[1].toLowerCase()) !== -1) {
      var name = facetOpen[1].toLowerCase(), typed = facetOpen[2].toLowerCase();
      html.push('<div class="group">' + esc(name) + " — what this model has</div>");
      facetValues(name)
        .filter(function (v) { return v.value.toLowerCase().indexOf(typed) !== -1; })
        .slice(0, 12).forEach(function (v) {
          items.push({ kind: "facet", key: name, value: v.value });
          html.push('<button type="button" data-i="' + (items.length - 1) + '">' +
            '<span>' + esc(v.value) + "</span>" +
            '<span class="meta">' + v.count + "</span></button>");
        });
    } else if (!text.trim()) {
      html.push('<div class="group">Narrow by</div>');
      FACETS.forEach(function (f) {
        items.push({ kind: "facet-open", key: f });
        html.push('<button type="button" data-i="' + (items.length - 1) + '">' +
          '<span class="id">' + esc(f) + ":</span><span>" +
          esc({ type: "element type", layer: "ArchiMate layer", model: "which model",
                status: "how far it is validated", grounded: "names what realizes it" }[f]) +
          "</span></button>");
      });
    } else {
      var found = runSearch(text);
      html.push('<div class="group">' + found.length + " element" +
        (found.length === 1 ? "" : "s") + "</div>");
      found.slice(0, 30).forEach(function (n) {
        items.push({ kind: "element", gid: n.gid });
        html.push('<button type="button" data-i="' + (items.length - 1) + '">' +
          '<span class="id">' + esc(n.id) + "</span><span>" + esc(n.label) + "</span>" +
          '<span class="meta">' + esc(n.type || "") + "</span></button>");
      });
      if (!found.length) html.push('<div class="none">Nothing matches. Try a facet — ' +
        'type <code>type:</code> to see what this model has.</div>');
    }
    suggestItems = items;
    suggestIndex = -1;
    suggest.innerHTML = html.join("");
    suggest.hidden = false;
    suggest.querySelectorAll("button").forEach(function (b) {
      b.addEventListener("mousedown", function (event) {
        event.preventDefault();
        choose(Number(b.dataset.i));
      });
    });
    render();
  }

  function choose(index) {
    var item = suggestItems[index];
    if (!item) return;
    if (item.kind === "facet-open") {
      qInput.value = item.key + ":";
      renderSuggest(qInput.value);
    } else if (item.kind === "facet") {
      var parts = qInput.value.split(/\s+/);
      parts[parts.length - 1] = item.key + ":" +
        (/\s/.test(item.value) ? '"' + item.value + '"' : item.value);
      qInput.value = parts.join(" ") + " ";
      renderSuggest(qInput.value);
    } else {
      suggest.hidden = true;
      select(item.gid, true);
    }
    qInput.focus();
  }

  /* ---- detail panel ------------------------------------------------------ */

  function select(gid, andFocus) {
    var node = byGid[gid];
    if (!node) return;
    if (node.project !== project && !view) {
      document.getElementById("project").value = node.project;
      switchProject(node.project, true);
    }
    if (!suppressHistory) {
      history = history.slice(0, historyAt + 1);
      history.push(gid);
      historyAt = history.length - 1;
      updateHistoryButtons();
    }
    showDetail(node);
    if (andFocus) focusOn(gid, depth);
    else { root = gid; render(); }
    ownHash = "#e=" + encodeURIComponent(gid) + "&depth=" + depth +
      "&layout=" + layoutMode;
    location.hash = ownHash;
  }

  function showDetail(node) {
    detail.hidden = false;
    var attrs = {};
    try { attrs = JSON.parse(node.attrs || "{}"); } catch (e) { attrs = {}; }
    var docHref = node.project === project
      ? "../" + node.doc.split("/").slice(1).join("/").replace(/\.md$/, "/") : "";
    var out = [
      "<h2>" + esc(node.name || node.id) + "</h2>",
      '<p class="kind">' + esc(node.id) + " · " + esc(node.type || "?") +
        (node.project !== project ? ' · <span class="badge">' + esc(node.project) + "</span>" : "") +
        (Number(node.retired) ? ' · <span class="badge">retired</span>' : "") + "</p>"
    ];

    if (node.status && node.status !== "validated") {
      out.push('<p><span class="badge">' + esc(node.status) +
        "</span> — not approved at a gate, so nothing here may be built on.</p>");
    }

    var shownAttrs = Object.keys(attrs).filter(function (k) { return attrs[k]; });
    if (shownAttrs.length) {
      out.push("<h3>Catalogue</h3><dl>");
      shownAttrs.forEach(function (k) {
        out.push("<dt>" + esc(k) + "</dt><dd>" + markdown(attrs[k]) + "</dd>");
      });
      out.push("</dl>");
    }

    var excerpts = excerptsFor(node);
    if (excerpts.length) {
      out.push("<h3>What the documents say</h3>");
      excerpts.forEach(function (x) {
        out.push('<p class="excerpt">' + markdown(x.body) +
          '<span class="src">' + esc(x.heading ? x.heading + " — " : "") +
          esc(x.doc) + "</span></p>");
      });
    }

    var related = relationsFor(node);
    if (related.length) {
      out.push("<h3>Relationships — " + related.length + "</h3>");
      related.forEach(function (r) {
        var other = byGid[r.other];
        out.push('<div class="rel"><span class="verb">' +
          (r.way === "out" ? "→ " : "← ") + esc(r.rel) +
          (Number(r.pending) ? " (planned)" : "") + '</span>' +
          '<button type="button" data-go="' + esc(r.other) + '">' +
          esc(other ? (other.name || other.id) : r.other) + "</button></div>");
      });
    }

    out.push("<h3>Source</h3><dl><dt>Defined in</dt><dd>" +
      (docHref ? '<a href="' + esc(docHref) + '">' + esc(node.doc) + "</a>"
               : esc(node.doc) + ' <span class="badge">another model</span>') +
      "</dd></dl>");

    out.push('<div class="actions">' +
      '<button type="button" id="walk">walk outward</button>' +
      '<button type="button" id="copy-link">copy link</button></div>');
    detail.innerHTML = out.join("");

    detail.querySelectorAll("[data-go]").forEach(function (b) {
      b.addEventListener("click", function () { select(b.dataset.go, false); });
    });
    document.getElementById("walk").addEventListener("click", function () {
      focusOn(node.gid, depth);
    });
    document.getElementById("copy-link").addEventListener("click", function () {
      navigator.clipboard.writeText(location.href).then(function () {
        document.getElementById("copy-link").textContent = "copied";
      }, function () { /* clipboard refused; the address bar still has it */ });
    });
  }

  /* ---- focus ------------------------------------------------------------- */

  function focusOn(gid, hops) {
    depth = hops;
    var found = rows(sql, { ":root": gid, ":depth": hops });
    var keep = new Set([gid]);
    found.forEach(function (r) { keep.add(r.src); keep.add(r.dst); });
    view = keep;
    root = gid;
    // A walk answers "what does this touch", and a layer filter that hides
    // most of the answer turns it into a wrong one. Focusing switches on
    // whatever the walk reached, and the checkboxes say so.
    keep.forEach(function (id) {
      var n = byGid[id];
      if (n) hidden.delete(n.grp || "");
    });
    document.querySelectorAll("#layers input").forEach(function (i) {
      i.checked = !hidden.has(i.dataset.group);
    });
    document.getElementById("focus-on").hidden = false;
    document.getElementById("focus-none").hidden = true;
    var n = byGid[gid];
    document.getElementById("focus-name").textContent =
      (n ? n.id : gid) + (n && n.name ? " · " + n.name : "");
    pinned = {};
    relayout();
  }

  function clearFocus() {
    view = null; root = null; pinned = {};
    document.getElementById("focus-on").hidden = true;
    document.getElementById("focus-none").hidden = false;
    relayout();
  }

  function switchProject(name, quiet) {
    project = name;
    view = null; root = null; pinned = {};
    document.getElementById("focus-on").hidden = true;
    document.getElementById("focus-none").hidden = false;
    buildLayerFilter(quiet);
    relayout();
  }

  /* ---- controls ---------------------------------------------------------- */

  function openingGroups() {
    return rows(
      "SELECT DISTINCT layer_group AS grp FROM nodes" +
      " WHERE project = :p AND layer_no <> '' AND layer_no <> '0'" +
      " AND layer_no = (SELECT MIN(layer_no) FROM nodes" +
      "   WHERE project = :p AND layer_no <> '' AND layer_no <> '0')",
      { ":p": project }).map(function (r) { return r.grp || ""; });
  }

  function buildLayerFilter(keepHidden) {
    var groups = [];
    nodes.filter(function (n) { return n.project === project; }).forEach(function (n) {
      if (groups.indexOf(n.grp || "") === -1) groups.push(n.grp || "");
    });
    groups.sort(function (a, b) {
      var ia = LAYER_ORDER.indexOf(a), ib = LAYER_ORDER.indexOf(b);
      return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib);
    });
    if (!keepHidden) {
      // Opens on the model's first numbered layer. The whole model at once is
      // a hairball, and the method already says where to start reading.
      var opening = openingGroups();
      hidden = new Set();
      if (opening.length) {
        groups.forEach(function (g) { if (opening.indexOf(g) === -1) hidden.add(g); });
      }
    }
    var box = document.getElementById("layers");
    box.innerHTML = groups.map(function (g) {
      return '<label><input type="checkbox" data-group="' + esc(g) + '"' +
        (hidden.has(g) ? "" : " checked") + '><span class="swatch" style="background:' +
        colour(g) + '"></span>' + esc(g || "—") + "</label>";
    }).join("");
    box.querySelectorAll("input").forEach(function (i) {
      i.addEventListener("change", function () {
        if (i.checked) hidden.delete(i.dataset.group); else hidden.add(i.dataset.group);
        relayout();
      });
    });
    buildLegend();
  }

  function buildLegend() {
    var groups = [];
    nodes.filter(function (n) { return n.project === project; }).forEach(function (n) {
      if (groups.indexOf(n.grp || "") === -1) groups.push(n.grp || "");
    });
    document.getElementById("legend").innerHTML =
      '<div class="line"><svg width="26" height="8"><line x1="0" y1="4" x2="26" y2="4" stroke="' +
        css("--edge") + '" stroke-width="1.5"/></svg> stated in a catalogue or a table</div>' +
      '<div class="line"><svg width="26" height="8"><line x1="0" y1="4" x2="26" y2="4" stroke="' +
        css("--edge") + '" stroke-width="1.5" stroke-dasharray="1 3"/></svg> structure, from the identifier</div>' +
      '<div class="line"><svg width="26" height="8"><line x1="0" y1="4" x2="26" y2="4" stroke="' +
        css("--edge") + '" stroke-width="1.5" stroke-dasharray="5 4"/></svg> planned, not yet true</div>' +
      '<div class="line"><svg width="26" height="14"><rect x="1" y="2" width="22" height="10" rx="2" fill="none" stroke="' +
        css("--box-stroke") + '" stroke-dasharray="3 2"/></svg> element in another model</div>';
  }

  /* ---- views -------------------------------------------------------------
   *
   * A view is a lens: filters, focus, layout, the boxes somebody moved, and
   * where they were looking. It is never model content — the page cannot write
   * to `architecture/`, and a view that could would be a second model.
   *
   * Personal views live in this browser. A view worth sharing is exported as a
   * file and committed by a person, through the ordinary process, like any
   * other change.
   */

  function storedViews() {
    try { return JSON.parse(localStorage.getItem(STORE) || "{}"); }
    catch (e) { return {}; }
  }
  function putViews(all) {
    try { localStorage.setItem(STORE, JSON.stringify(all)); }
    catch (e) { /* private mode, or a full quota: the view is lost, not the page */ }
  }
  function currentView() {
    var places = {};
    shownNodes().forEach(function (n) {
      var p = positions[n.gid];
      if (p) places[n.gid] = [Math.round(p.x), Math.round(p.y)];
    });
    return {
      model: project, layout: layoutMode, hidden: Array.from(hidden),
      focus: root, depth: depth, focused: !!view,
      positions: places, camera: { x: camera.x, y: camera.y, k: camera.k }
    };
  }
  function applyView(v) {
    if (!v) return;
    if (v.model && v.model !== project) {
      document.getElementById("project").value = v.model;
      project = v.model;
    }
    layoutMode = v.layout || "layered";
    document.getElementById("layout").value = layoutMode;
    hidden = new Set(v.hidden || []);
    buildLayerFilter(true);
    if (v.focused && v.focus) focusOn(v.focus, v.depth || 2);
    else { view = null; root = v.focus || null; layout(); }
    pinned = {};
    Object.keys(v.positions || {}).forEach(function (gid) { pinned[gid] = v.positions[gid]; });
    layout();
    if (v.camera) camera = { x: v.camera.x, y: v.camera.y, k: v.camera.k };
    else fit();
    render();
  }
  function refreshViewList(selected) {
    var all = storedViews();
    var list = document.getElementById("view-list");
    var names = Object.keys(all).sort();
    list.innerHTML = '<option value="">— saved views —</option>' +
      (published.length ? '<optgroup label="published">' + published.map(function (v) {
        return '<option value="published:' + esc(v.name) + '">' + esc(v.name) + "</option>";
      }).join("") + "</optgroup>" : "") +
      (names.length ? '<optgroup label="yours">' + names.map(function (n) {
        return '<option value="mine:' + esc(n) + '">' + esc(n) + "</option>";
      }).join("") + "</optgroup>" : "");
    if (selected) list.value = selected;
  }
  var published = [];

  /* ---- interaction ------------------------------------------------------- */

  var press = null, MOVED = 4;

  svg.addEventListener("pointerdown", function (event) {
    var group = event.target.closest ? event.target.closest(".node") : null;
    press = { x: event.clientX, y: event.clientY, node: group, moved: false,
              start: group ? Object.assign({}, positions[group.dataset.id]) : null };
    svg.classList.add("dragging");
    svg.setPointerCapture(event.pointerId);
  });
  svg.addEventListener("pointermove", function (event) {
    if (!press) return;
    var dx = event.clientX - press.x, dy = event.clientY - press.y;
    if (!press.moved && Math.abs(dx) < MOVED && Math.abs(dy) < MOVED) return;
    press.moved = true;
    if (press.node) {
      // Dragging a box moves that box, and remembers that a person put it
      // there — which is what makes a saved view worth saving.
      var gid = press.node.dataset.id, p = positions[gid];
      p.x += dx / camera.k; p.y += dy / camera.k;
      pinned[gid] = [p.x, p.y];
    } else {
      camera.x += dx; camera.y += dy;
    }
    press.x = event.clientX; press.y = event.clientY;
    render();
  });
  svg.addEventListener("pointerup", function (event) {
    svg.classList.remove("dragging");
    if (svg.hasPointerCapture(event.pointerId)) svg.releasePointerCapture(event.pointerId);
    if (press && !press.moved && press.node) select(press.node.dataset.id, false);
    press = null;
  });
  svg.addEventListener("pointercancel", function () {
    svg.classList.remove("dragging"); press = null;
  });
  svg.addEventListener("wheel", function (event) {
    event.preventDefault();
    var box = svg.getBoundingClientRect();
    var mx = event.clientX - box.left, my = event.clientY - box.top;
    var factor = event.deltaY < 0 ? 1.12 : 1 / 1.12;
    camera.x = mx - (mx - camera.x) * factor;
    camera.y = my - (my - camera.y) * factor;
    camera.k *= factor;
    render();
  }, { passive: false });

  function updateHistoryButtons() {
    document.getElementById("nav-back").disabled = historyAt <= 0;
    document.getElementById("nav-forward").disabled = historyAt >= history.length - 1;
  }
  function go(delta) {
    var next = historyAt + delta;
    if (next < 0 || next >= history.length) return;
    historyAt = next;
    suppressHistory = true;
    select(history[next], false);
    suppressHistory = false;
    updateHistoryButtons();
  }

  function exportPNG() {
    var box = svg.getBoundingClientRect();
    var clone = svg.cloneNode(true);
    clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
    clone.setAttribute("width", box.width);
    clone.setAttribute("height", box.height);
    var style = document.createElement("style");
    style.textContent = document.querySelector('link[href$="navigator.css"]')
      ? inlineStyles() : "";
    clone.insertBefore(style, clone.firstChild);
    var blob = new Blob(
      ['<?xml version="1.0"?>', new XMLSerializer().serializeToString(clone)],
      { type: "image/svg+xml" });
    var url = URL.createObjectURL(blob);
    var image = new Image();
    image.onload = function () {
      var canvas = document.createElement("canvas");
      canvas.width = box.width * 2; canvas.height = box.height * 2;
      var ctx = canvas.getContext("2d");
      ctx.fillStyle = css("--bg") || "#fff";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.scale(2, 2);
      ctx.drawImage(image, 0, 0);
      URL.revokeObjectURL(url);
      var a = document.createElement("a");
      a.download = (project.replace(/\W+/g, "-") || "model") + "-view.png";
      a.href = canvas.toDataURL("image/png");
      a.click();
    };
    image.src = url;
  }
  function inlineStyles() {
    // The exported SVG leaves the page, so the few rules its text and boxes
    // need travel with it. Anything not listed here simply renders plain.
    return ".node rect{stroke:#6b7480;stroke-width:1}" +
      ".node .name{font:600 11px system-ui;fill:#24292f}" +
      ".node .id{font:9px ui-monospace,monospace;fill:#4b5563}" +
      ".node .glyph{font:11px system-ui;fill:#24292f}" +
      ".node.root rect{stroke:#0b62c4;stroke-width:2.5}" +
      ".node.elsewhere rect{stroke-dasharray:3 2}" +
      ".edge{stroke:#9aa4b0;fill:none}" +
      ".edge.identifier{stroke-dasharray:1 3}.edge.pending{stroke-dasharray:5 4}" +
      ".edge-label{font:8px system-ui;fill:#5b636d}" +
      ".lane{fill:none;stroke:#d7dce3;stroke-dasharray:4 4}" +
      ".lane-label{font:10px system-ui;fill:#5b636d}";
  }

  function readHash() {
    var params = {};
    location.hash.replace(/^#/, "").split("&").forEach(function (pair) {
      var kv = pair.split("=");
      if (kv[0]) params[kv[0]] = decodeURIComponent(kv[1] || "");
    });
    return params;
  }

  /* ---- wiring ------------------------------------------------------------ */

  document.getElementById("show-identifier").addEventListener("change", render);
  document.getElementById("show-pending").addEventListener("change", render);
  document.getElementById("show-labels").addEventListener("change", render);
  document.getElementById("clear-focus").addEventListener("click", clearFocus);
  document.getElementById("all-layers").addEventListener("click", function () {
    hidden.clear();
    document.querySelectorAll("#layers input").forEach(function (i) { i.checked = true; });
    relayout();
  });
  document.getElementById("no-layers").addEventListener("click", function () {
    document.querySelectorAll("#layers input").forEach(function (i) {
      i.checked = false; hidden.add(i.dataset.group);
    });
    relayout();
  });
  document.getElementById("depth").addEventListener("input", function (event) {
    document.getElementById("depth-out").textContent = event.target.value;
    if (root && view) focusOn(root, Number(event.target.value));
    else depth = Number(event.target.value);
  });
  document.getElementById("project").addEventListener("change", function (event) {
    switchProject(event.target.value);
  });
  document.getElementById("layout").addEventListener("change", function (event) {
    layoutMode = event.target.value;
    pinned = {};
    relayout();
  });
  document.getElementById("fit-view").addEventListener("click", function () { fit(); render(); });
  document.getElementById("png").addEventListener("click", exportPNG);
  document.getElementById("nav-back").addEventListener("click", function () { go(-1); });
  document.getElementById("nav-forward").addEventListener("click", function () { go(1); });

  qInput.addEventListener("input", function () { renderSuggest(qInput.value); });
  qInput.addEventListener("focus", function () { renderSuggest(qInput.value); });
  qInput.addEventListener("blur", function () {
    setTimeout(function () { suggest.hidden = true; }, 120);
  });
  qInput.addEventListener("keydown", function (event) {
    if (event.key === "Escape") { qInput.value = ""; hits = new Set(); suggest.hidden = true; render(); return; }
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      var n = suggestItems.length;
      if (!n) return;
      suggestIndex = (suggestIndex + (event.key === "ArrowDown" ? 1 : -1) + n) % n;
      suggest.querySelectorAll("button").forEach(function (b, i) {
        b.classList.toggle("on", i === suggestIndex);
        if (i === suggestIndex) b.scrollIntoView({ block: "nearest" });
      });
    }
    if (event.key === "Enter") {
      event.preventDefault();
      choose(suggestIndex >= 0 ? suggestIndex : 0);
    }
  });
  document.addEventListener("keydown", function (event) {
    if (event.key === "/" && document.activeElement !== qInput) {
      event.preventDefault(); qInput.focus(); qInput.select();
    }
  });

  document.getElementById("view-save").addEventListener("click", function () {
    var name = prompt("Name this view");
    if (!name) return;
    var all = storedViews();
    all[name] = currentView();
    putViews(all);
    refreshViewList("mine:" + name);
  });
  document.getElementById("view-delete").addEventListener("click", function () {
    var value = document.getElementById("view-list").value;
    if (value.indexOf("mine:") !== 0) return;
    var all = storedViews();
    delete all[value.slice(5)];
    putViews(all);
    refreshViewList();
  });
  document.getElementById("view-list").addEventListener("change", function (event) {
    var value = event.target.value;
    if (!value) return;
    if (value.indexOf("mine:") === 0) applyView(storedViews()[value.slice(5)]);
    else {
      var found = published.find(function (v) { return v.name === value.slice(10); });
      applyView(found && found.view);
    }
  });
  document.getElementById("view-export").addEventListener("click", function () {
    var value = document.getElementById("view-list").value;
    var name = value.indexOf("mine:") === 0 ? value.slice(5) : "current";
    var body = { name: name, view: value.indexOf("mine:") === 0
      ? storedViews()[name] : currentView() };
    var a = document.createElement("a");
    a.download = name.replace(/\W+/g, "-") + ".view.json";
    a.href = URL.createObjectURL(new Blob([JSON.stringify(body, null, 2)],
      { type: "application/json" }));
    a.click();
  });
  document.getElementById("view-import").addEventListener("click", function () {
    document.getElementById("view-file").click();
  });
  document.getElementById("view-file").addEventListener("change", function (event) {
    var file = event.target.files[0];
    if (!file) return;
    file.text().then(function (text) {
      var body = JSON.parse(text);
      var all = storedViews();
      all[body.name || file.name] = body.view || body;
      putViews(all);
      refreshViewList("mine:" + (body.name || file.name));
      applyView(body.view || body);
    }).catch(function () {
      alert("That file is not a view this page can read.");
    });
  });

  window.addEventListener("resize", function () { fit(); render(); });

  /* A link pasted into the address bar of an already-open page is a
   * same-document navigation: nothing reloads, and without this nothing would
   * happen. `select` writes the hash itself, so a change this listener caused
   * is ignored rather than looping. */
  window.addEventListener("hashchange", function () {
    if (location.hash === ownHash) return;
    var params = readHash();
    if (params.layout && params.layout !== layoutMode) {
      layoutMode = params.layout === "force" ? "force" : "layered";
      document.getElementById("layout").value = layoutMode;
      pinned = {};
      relayout();
    }
    if (params.e && byGid[params.e]) {
      depth = Number(params.depth) || depth;
      document.getElementById("depth").value = depth;
      document.getElementById("depth-out").textContent = depth;
      select(params.e, true);
    }
  });

  /* ---- federation --------------------------------------------------------- */

  function copyInto(source, present) {
    ["nodes", "edges", "mentions", "excerpts"].forEach(function (table) {
      var got;
      try { got = source.exec("SELECT * FROM " + table); } catch (e) { return; }
      if (!got.length) return;
      var columns = got[0].columns;
      var insert = db.prepare("INSERT INTO " + table + " (" + columns.join(",") +
        ") VALUES (" + columns.map(function () { return "?"; }).join(",") + ")");
      got[0].values.forEach(function (row) {
        if (present[row[columns.indexOf("project")]]) return;
        insert.bind(row); insert.step(); insert.reset();
      });
      insert.free();
    });
  }

  function federate(SQL) {
    return fetch("./federation.json").then(function (r) {
      return r.ok ? r.json() : null;
    }).catch(function () { return null; }).then(function (index) {
      if (!index || !Array.isArray(index.models)) return;
      var present = {};
      rows("SELECT DISTINCT project FROM nodes").forEach(function (r) { present[r.project] = true; });
      return Promise.all(index.models.map(function (model) {
        var base = model.projection.replace(/\/?$/, "/");
        return fetch(base + "model.db").then(function (r) {
          if (!r.ok) throw new Error("HTTP " + r.status);
          return r.arrayBuffer();
        }).then(function (buffer) {
          var other = new SQL.Database(new Uint8Array(buffer));
          try { copyInto(other, present); } finally { other.close(); }
          rows("SELECT DISTINCT project FROM nodes").forEach(function (r) {
            present[r.project] = true;
          });
        }).catch(function (error) {
          unreachable.push(model.name + " — " + error.message);
        });
      }));
    });
  }

  /* ---- start -------------------------------------------------------------- */

  function fail(what, why) {
    say("<p><strong>" + esc(what) + "</strong></p><p>" + why + "</p>", true);
  }

  if (typeof initSqlJs !== "function") {
    fail("The SQLite reader is missing.",
      "This page reads <code>model.db</code> with sql.js, which the build fetches " +
      "beside it. The build reported that it could not, and published the page anyway " +
      "rather than failing over a graph viewer. Re-run <code>scripts/build_docs.py</code> " +
      "with network access to fetch it.");
    return;
  }

  say("Loading the projection…");
  Promise.all([
    initSqlJs({ locateFile: function (f) { return "./" + f; } }),
    fetch("./model.db").then(function (r) {
      if (!r.ok) throw new Error("model.db " + r.status);
      return r.arrayBuffer();
    }),
    fetch("./neighbourhood.sql").then(function (r) {
      if (!r.ok) throw new Error("neighbourhood.sql " + r.status);
      return r.text();
    }),
    fetch("./views.json").then(function (r) { return r.ok ? r.json() : null; })
      .catch(function () { return null; })
  ]).then(function (loaded) {
    SQLjs = loaded[0];
    db = new SQLjs.Database(new Uint8Array(loaded[1]));
    sql = loaded[2];
    published = (loaded[3] && loaded[3].views) || [];
    return federate(SQLjs);
  }).then(function () {
    loadAll();
    var projects = rows("SELECT DISTINCT project FROM nodes ORDER BY project")
      .map(function (r) { return r.project; });
    if (!projects.length) {
      fail("This model has no elements yet.",
        "The projection is empty, which is what an unfilled scaffold looks like. " +
        "Fill in a layer and rebuild.");
      return;
    }
    var picker = document.getElementById("project");
    picker.innerHTML = projects.map(function (p) {
      return '<option value="' + esc(p) + '">' + esc(p) + "</option>";
    }).join("");
    picker.parentElement.hidden = projects.length < 2;
    controls.hidden = false;
    document.getElementById("search-box").hidden = false;
    document.getElementById("subtitle").textContent =
      "Opens on the model's first layer. Search to find anything; click a box to read " +
      "what the documents say about it; drag to arrange, and save the arrangement as a view." +
      (projects.length > 1 ? " " + projects.length + " models." : "");
    if (unreachable.length) {
      var box = document.createElement("p");
      box.className = "warn";
      box.textContent = unreachable.length + " model(s) in the index could not be " +
        "reached and are not shown: " + unreachable.join("; ") + ".";
      document.querySelector(".brand").appendChild(box);
    }
    refreshViewList();
    var params = readHash();
    project = projects.indexOf(params.model) >= 0 ? params.model : projects[0];
    picker.value = project;
    layoutMode = params.layout === "force" ? "force" : "layered";
    document.getElementById("layout").value = layoutMode;
    switchProject(project);
    if (params.e && byGid[params.e]) {
      depth = Number(params.depth) || 2;
      document.getElementById("depth").value = depth;
      document.getElementById("depth-out").textContent = depth;
      select(params.e, true);
    }
    updateHistoryButtons();
  }).catch(function (error) {
    fail("The projection could not be read.",
      "<code>" + esc(error.message) + "</code>. This page needs <code>model.db</code> " +
      "and <code>neighbourhood.sql</code> beside it, and a server rather than a " +
      "<code>file://</code> path — browsers refuse to fetch local files.");
  });
})();
