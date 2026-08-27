/* The model as a graph, read from the projection in the browser.
 *
 * Two things here are deliberate and worth knowing before changing anything.
 *
 * **The traversal is not written here.** Walking outward from an element runs
 * `neighbourhood.sql`, the same file `query_model.py` executes for `trace`. A
 * walk implemented once in Python and once in JavaScript drifts, and the copy
 * that drifts is this one, because nothing tests a browser. Everything else
 * here is presentation.
 *
 * **There are no libraries.** sql.js is unavoidable — reading SQLite in a
 * browser needs it — and it is fetched at build time, pinned and verified. The
 * layout below is about sixty lines of force simulation, which is cheaper than
 * a dependency the method would have to keep, review and explain.
 */
(function () {
  "use strict";

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

  var svg = document.getElementById("graph");
  var statusBox = document.getElementById("status");
  var detail = document.getElementById("detail");
  var controls = document.getElementById("controls");

  var db = null;
  var sql = "";            // neighbourhood.sql, fetched once
  var project = "";
  var nodes = [];          // {id, name, type, group, doc, status, realized_by, retired}
  var edges = [];          // {src, dst, rel, origin, pending}
  var view = null;         // null = whole model; otherwise a Set of ids
  var root = null;
  var hidden = new Set();  // layer groups switched off
  var camera = { x: 0, y: 0, k: 1 };
  var unreachable = [];    // federated models that could not be fetched

  function say(html, fail) {
    statusBox.classList.remove("hidden");
    statusBox.innerHTML = fail ? '<div class="fail">' + html + "</div>" : html;
  }
  function clearStatus() { statusBox.classList.add("hidden"); }
  function colour(group) {
    var name = PALETTE[group] || "--canvas";
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || "#ccc";
  }
  function esc(text) {
    return String(text == null ? "" : text).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  /* ---- data ------------------------------------------------------------ */

  function rows(query, params) {
    var out = [];
    var statement = db.prepare(query);
    if (params) statement.bind(params);
    while (statement.step()) out.push(statement.getAsObject());
    statement.free();
    return out;
  }

  /* Which layers a reader should see first.
   *
   * The whole model at once is a hairball: 184 elements and 326 relationships
   * is legible filtered and illegible whole. The method already says where to
   * start — `architecture/README.md` § Reading order is top-down through the
   * numbered folders — so the page opens on the lowest numbered layer that has
   * anything in it, skipping layer 0, which an application project does not
   * use. Everything else is one checkbox away, and the subtitle says so.
   */
  function openingGroups() {
    var found = rows(
      "SELECT DISTINCT layer_group AS grp FROM nodes" +
      " WHERE project = :p AND layer_no <> '' AND layer_no <> '0'" +
      " AND layer_no = (SELECT MIN(layer_no) FROM nodes" +
      "   WHERE project = :p AND layer_no <> '' AND layer_no <> '0')",
      { ":p": project }
    ).map(function (r) { return r.grp || ""; });
    return found;
  }

  /* Everything, keyed by a qualified identifier.
   *
   * Two models may each own a `G1`, so the key a node is looked up by has to
   * carry the model — the same qualification `neighbourhood.sql` walks on and
   * a document writes when it references across a boundary. The model picker
   * became a filter rather than a loader when relationships started crossing:
   * a neighbour in another model has to be drawable, or a federated walk shows
   * a hole where the answer was.
   */
  function loadProject(name) {
    project = name;
    nodes = rows(
      "SELECT project || '::' || id AS gid, project, id, name, type," +
      " layer_group AS grp, doc, status, realized_by, retired, domain" +
      " FROM nodes ORDER BY project, id");
    edges = rows(
      "SELECT project || '::' || src AS src," +
      " CASE WHEN dst_project = '' THEN project ELSE dst_project END || '::' || dst AS dst," +
      " rel, origin, pending FROM edges");
    view = null;
    root = null;
    var opening = openingGroups();
    hidden = new Set();
    if (opening.length) {
      nodes.forEach(function (n) {
        if (opening.indexOf(n.grp || "") === -1) hidden.add(n.grp || "");
      });
    }
    buildLayerFilter();
    layout();
    reframe();
  }

  /* Walk outward from one element — the shared query, not a local traversal. */
  function focusOn(id, depth) {
    var found = rows(sql, { ":root": id, ":depth": depth });
    var keep = new Set([id]);
    found.forEach(function (row) { keep.add(row.src); keep.add(row.dst); });
    view = keep;
    root = id;
    reframe();
    document.getElementById("focus-on").hidden = false;
    document.getElementById("focus-none").hidden = true;
    var element = nodes.find(function (n) { return n.gid === id; });
    document.getElementById("focus-name").textContent =
      (element ? element.id : id) + (element && element.name ? " · " + element.name : "");
  }

  function clearFocus() {
    view = null; root = null;
    document.getElementById("focus-on").hidden = true;
    document.getElementById("focus-none").hidden = false;
    reframe();
  }

  /* ---- layout ----------------------------------------------------------- */

  var positions = {};

  function layout() {
    var live = nodes;
    var count = live.length || 1;
    var radius = Math.sqrt(count) * 46;
    positions = {};
    live.forEach(function (node, index) {
      // A ring start beats random: the simulation converges from it in far
      // fewer ticks, and the result is stable between reloads.
      var angle = (index / count) * Math.PI * 2;
      positions[node.gid] = {
        x: Math.cos(angle) * radius, y: Math.sin(angle) * radius, vx: 0, vy: 0
      };
    });
    var links = edges.filter(function (e) {
      return positions[e.src] && positions[e.dst];
    });
    for (var tick = 0; tick < 320; tick++) {
      var cooling = 1 - tick / 320;
      // Repulsion, all pairs. At a few hundred nodes this is fast enough that
      // a quadtree would be optimising the wrong thing.
      for (var a = 0; a < live.length; a++) {
        for (var b = a + 1; b < live.length; b++) {
          var p = positions[live[a].gid], q = positions[live[b].gid];
          var dx = q.x - p.x, dy = q.y - p.y;
          var d2 = dx * dx + dy * dy || 0.01;
          var force = 2600 / d2;
          var d = Math.sqrt(d2);
          var fx = (dx / d) * force, fy = (dy / d) * force;
          p.vx -= fx; p.vy -= fy; q.vx += fx; q.vy += fy;
        }
      }
      links.forEach(function (link) {
        var p = positions[link.src], q = positions[link.dst];
        var dx = q.x - p.x, dy = q.y - p.y;
        var d = Math.sqrt(dx * dx + dy * dy) || 0.01;
        var pull = (d - 110) * 0.02;
        var fx = (dx / d) * pull, fy = (dy / d) * pull;
        p.vx += fx; p.vy += fy; q.vx -= fx; q.vy -= fy;
      });
      live.forEach(function (node) {
        var p = positions[node.gid];
        p.vx -= p.x * 0.002; p.vy -= p.y * 0.002;   // gentle centring
        p.x += p.vx * cooling; p.y += p.vy * cooling;
        p.vx *= 0.82; p.vy *= 0.82;
      });
    }
    fit();
  }

  /* Frame what is on screen, not what exists.
   *
   * Positions are computed once for the whole model, so a filtered or focused
   * subset keeps whatever corner of that layout it happened to occupy. Fitting
   * to the visible set is what makes a two-hop walk fill the canvas instead of
   * sitting in a quarter of it. */
  function fit(ids) {
    var xs = [], ys = [];
    (ids || Object.keys(positions)).forEach(function (id) {
      if (!positions[id]) return;
      xs.push(positions[id].x); ys.push(positions[id].y);
    });
    if (!xs.length) return;
    var box = svg.getBoundingClientRect();
    var w = Math.max.apply(null, xs) - Math.min.apply(null, xs) || 1;
    var h = Math.max.apply(null, ys) - Math.min.apply(null, ys) || 1;
    camera.k = Math.min((box.width - 120) / w, (box.height - 120) / h, 2.2) || 1;
    camera.x = box.width / 2 - ((Math.max.apply(null, xs) + Math.min.apply(null, xs)) / 2) * camera.k;
    camera.y = box.height / 2 - ((Math.max.apply(null, ys) + Math.min.apply(null, ys)) / 2) * camera.k;
  }

  /* ---- render ----------------------------------------------------------- */

  function visible(node) {
    if (hidden.has(node.grp || "")) return false;
    if (view) return view.has(node.gid);
    // Outside a focus, one model at a time: a federated graph drawn whole is
    // several hairballs rather than one.
    return node.project === project;
  }

  function visibleIds() {
    return nodes.filter(visible).map(function (n) { return n.gid; });
  }

  function reframe() {
    fit(visibleIds());
    render();
  }

  function render() {
    var showIdentifier = document.getElementById("show-identifier").checked;
    var showPending = document.getElementById("show-pending").checked;
    var shown = {};
    nodes.forEach(function (n) { if (visible(n)) shown[n.gid] = n; });

    var parts = ['<g transform="translate(' + camera.x + ',' + camera.y + ') scale(' + camera.k + ')">'];
    var drawn = 0;
    edges.forEach(function (edge) {
      if (!shown[edge.src] || !shown[edge.dst]) return;
      if (edge.origin === "identifier" && !showIdentifier) return;
      if (edge.pending && !showPending) return;
      var p = positions[edge.src], q = positions[edge.dst];
      if (!p || !q) return;
      drawn++;
      var classes = "edge" + (edge.origin === "identifier" ? " identifier" : "") +
        (edge.pending ? " pending" : "");
      parts.push('<line class="' + classes + '" x1="' + p.x + '" y1="' + p.y +
        '" x2="' + q.x + '" y2="' + q.y + '"><title>' + esc(edge.src + " — " +
        edge.rel + " — " + edge.dst) + "</title></line>");
    });
    // Labels are drawn only when they can be read. Past that they overlap into
    // a grey smear; short of it, an unlabelled graph is a shape rather than
    // information, which is the worse failure of the two. The thresholds are
    // tuned against the opening view — one layer of a real model, around a
    // hundred elements — and the tooltip and detail panel name every node
    // either way.
    var count = Object.keys(shown).length;
    var labels = count <= 110 || camera.k >= 0.9;
    Object.keys(shown).forEach(function (id) {
      var node = shown[id], p = positions[id];
      if (!p) return;
      var size = node.gid === root ? 9 : 6;
      parts.push('<g class="node' + (node.gid === root ? " root" : "") +
        (node.project !== project ? " elsewhere" : "") +
        '" data-id="' + esc(id) + '" transform="translate(' + p.x + ',' + p.y + ')">' +
        '<circle r="' + size + '" fill="' + colour(node.grp) + '"></circle>' +
        (labels ? '<text x="' + (size + 3) + '" y="3">' + esc(node.id) + "</text>" : "") +
        "<title>" + esc(node.gid + (node.name ? " · " + node.name : "")) + "</title></g>");
    });
    parts.push("</g>");
    svg.innerHTML = parts.join("");
    document.getElementById("counts").textContent =
      Object.keys(shown).length + " of " + nodes.length + " element(s), " +
      drawn + " relationship(s) shown.";
    clearStatus();
  }

  /* ---- controls ---------------------------------------------------------- */

  function buildLayerFilter() {
    var groups = [];
    nodes.forEach(function (n) {
      if (groups.indexOf(n.grp || "") === -1) groups.push(n.grp || "");
    });
    groups.sort();
    var box = document.getElementById("layers");
    box.innerHTML = groups.map(function (group) {
      return '<label><input type="checkbox" data-group="' + esc(group) + '"' +
        (hidden.has(group) ? "" : " checked") + ">" +
        '<span class="swatch" style="background:' + colour(group) + '"></span>' +
        esc(group || "—") + "</label>";
    }).join("");
    box.querySelectorAll("input").forEach(function (input) {
      input.addEventListener("change", function () {
        if (input.checked) hidden.delete(input.dataset.group);
        else hidden.add(input.dataset.group);
        reframe();
      });
    });
  }

  function showDetail(id) {
    var node = nodes.find(function (n) { return n.gid === id; });
    if (!node) return;
    detail.hidden = false;
    // A document in another model is published under that model's own portal,
    // which this page cannot address. Naming it beats linking somewhere wrong.
    var docHref = node.project === project
      ? "../" + node.doc.split("/").slice(1).join("/").replace(/\.md$/, "/")
      : "";
    detail.innerHTML =
      "<h2>" + esc(node.name || node.id) + "</h2>" +
      '<p class="kind">' + esc(node.id) + " · " + esc(node.type || "?") +
      (node.project !== project ? ' · <span class="badge">' + esc(node.project) + "</span>" : "") +
      (node.retired ? ' · <span class="badge">retired</span>' : "") + "</p>" +
      "<dl>" +
      (node.status && node.status !== "validated"
        ? "<dt>Standing</dt><dd><span class=\"badge\">" + esc(node.status) +
          "</span> — not approved at a gate</dd>" : "") +
      (node.realized_by ? "<dt>Realized by</dt><dd>" + esc(node.realized_by) + "</dd>" : "") +
      (node.domain ? "<dt>Domain</dt><dd>" + esc(node.domain) + "</dd>" : "") +
      "<dt>Defined in</dt><dd>" + (docHref
        ? "<a href=\"" + esc(docHref) + "\">" + esc(node.doc) + "</a>"
        : esc(node.doc) + " <span class=\"badge\">another model</span>") + "</dd>" +
      "</dl>" +
      '<p><button type="button" id="walk">walk outward from here</button></p>';
    document.getElementById("walk").addEventListener("click", function () {
      focusOn(node.gid, Number(document.getElementById("depth").value));
    });
  }

  /* Pan, zoom, and select.
   *
   * All three come off the same pointer stream, and they have to: capturing the
   * pointer for a drag retargets the click that follows it to the <svg>, so a
   * separate click listener never sees the node it was aimed at. A press that
   * does not move is a selection; one that moves is a pan.
   */
  var press = null;
  var MOVED = 4;  // px before a press counts as a drag rather than a click

  svg.addEventListener("pointerdown", function (event) {
    var group = event.target.closest ? event.target.closest(".node") : null;
    press = { x: event.clientX, y: event.clientY, node: group, moved: false };
    svg.classList.add("dragging");
    svg.setPointerCapture(event.pointerId);
  });
  svg.addEventListener("pointermove", function (event) {
    if (!press) return;
    var dx = event.clientX - press.x, dy = event.clientY - press.y;
    if (!press.moved && Math.abs(dx) < MOVED && Math.abs(dy) < MOVED) return;
    press.moved = true;
    camera.x += dx;
    camera.y += dy;
    press.x = event.clientX;
    press.y = event.clientY;
    render();
  });
  svg.addEventListener("pointerup", function (event) {
    svg.classList.remove("dragging");
    if (svg.hasPointerCapture(event.pointerId)) svg.releasePointerCapture(event.pointerId);
    if (press && !press.moved && press.node) showDetail(press.node.dataset.id);
    press = null;
  });
  svg.addEventListener("pointercancel", function () {
    svg.classList.remove("dragging");
    press = null;
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

  document.getElementById("show-identifier").addEventListener("change", render);
  document.getElementById("show-pending").addEventListener("change", render);
  document.getElementById("clear-focus").addEventListener("click", clearFocus);
  document.getElementById("all-layers").addEventListener("click", function () {
    hidden.clear();
    document.querySelectorAll("#layers input").forEach(function (i) { i.checked = true; });
    reframe();
  });
  document.getElementById("no-layers").addEventListener("click", function () {
    document.querySelectorAll("#layers input").forEach(function (i) {
      i.checked = false; hidden.add(i.dataset.group);
    });
    reframe();
  });
  document.getElementById("depth").addEventListener("input", function (event) {
    document.getElementById("depth-out").textContent = event.target.value;
    if (root) focusOn(root, Number(event.target.value));
  });
  document.getElementById("project").addEventListener("change", function (event) {
    loadProject(event.target.value);
  });

  /* ---- federation --------------------------------------------------------
   *
   * Where a `federation.json` sits beside this page, the models it names are
   * loaded into the database this page already has — INSERT ... SELECT from
   * each fetched projection, so no column mapping is written twice. The
   * projection's own schema is the schema; nothing here restates it.
   *
   * Where there is no index, none of this runs and the page reads its own
   * projection exactly as it would have. A project that is not in a federation
   * should not have to know what one is.
   */

  function copyInto(source, present) {
    ["nodes", "edges", "mentions"].forEach(function (table) {
      var got = source.exec("SELECT * FROM " + table);
      if (!got.length) return;
      var columns = got[0].columns;
      var placeholders = columns.map(function () { return "?"; }).join(",");
      var insert = db.prepare(
        "INSERT INTO " + table + " (" + columns.join(",") + ") VALUES (" + placeholders + ")");
      got[0].values.forEach(function (row) {
        // A model already in this database is not loaded twice: the topmost
        // model of a federation lists itself, and it is the one already open.
        var project = row[columns.indexOf("project")];
        if (present[project]) return;
        insert.bind(row);
        insert.step();
        insert.reset();
      });
      insert.free();
    });
  }

  function federate(SQL) {
    return fetch("./federation.json").then(function (response) {
      if (!response.ok) return null;      // no index: not a federation
      return response.json();
    }).catch(function () {
      return null;
    }).then(function (index) {
      if (!index || !Array.isArray(index.models)) return;
      var present = {};
      rows("SELECT DISTINCT project FROM nodes").forEach(function (r) {
        present[r.project] = true;
      });
      return Promise.all(index.models.map(function (model) {
        var base = model.projection.replace(/\/?$/, "/");
        return fetch(base + "model.db").then(function (response) {
          if (!response.ok) throw new Error("HTTP " + response.status);
          return response.arrayBuffer();
        }).then(function (buffer) {
          var other = new SQL.Database(new Uint8Array(buffer));
          try {
            copyInto(other, present);
          } finally {
            other.close();
          }
          rows("SELECT DISTINCT project FROM nodes").forEach(function (r) {
            present[r.project] = true;
          });
        }).catch(function (error) {
          unreachable.push(model.name + " — " + error.message);
        });
      }));
    });
  }

  /* ---- start ------------------------------------------------------------- */

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
    initSqlJs({ locateFile: function (file) { return "./" + file; } }),
    fetch("./model.db").then(function (r) {
      if (!r.ok) throw new Error("model.db " + r.status);
      return r.arrayBuffer();
    }),
    fetch("./neighbourhood.sql").then(function (r) {
      if (!r.ok) throw new Error("neighbourhood.sql " + r.status);
      return r.text();
    })
  ]).then(function (loaded) {
    db = new loaded[0].Database(new Uint8Array(loaded[1]));
    sql = loaded[2];
    return federate(loaded[0]).then(function () { return loaded[0]; });
  }).then(function () {
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
    var federated = projects.length > 1
      ? " " + projects.length + " models, shown one at a time — a relationship does not " +
        "cross a model, so these are several graphs rather than one."
      : "";
    document.getElementById("subtitle").textContent =
      "Opens on the model's first layer — switch the others on at the left. Click an " +
      "element to see what it is; walk outward to see what a change to it would touch." +
      federated;
    if (unreachable.length) {
      var box = document.createElement("p");
      box.className = "warn";
      box.textContent = unreachable.length + " model(s) in the index could not be " +
        "reached and are not shown: " + unreachable.join("; ") + ".";
      document.querySelector("header").appendChild(box);
    }
    loadProject(projects[0]);
  }).catch(function (error) {
    fail("The projection could not be read.",
      "<code>" + esc(error.message) + "</code>. This page needs <code>model.db</code> " +
      "and <code>neighbourhood.sql</code> beside it, and a server rather than a " +
      "<code>file://</code> path — browsers refuse to fetch local files.");
  });

  window.addEventListener("resize", reframe);
})();
