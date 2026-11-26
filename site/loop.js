/* The loop, from an idea to a tested solution, as data and one function that
   draws it. The landing page steps through it; the film animates it. One
   picture, described once, so the two cannot disagree.

   Everything is laid out by hand on a 1200 x 596 grid: lanes for who acts,
   columns for the six steps. Text is wrapped by hand too, so the drawing
   needs no measuring and looks the same wherever it is drawn. */
(function (root) {
  'use strict';
  var NS = 'http://www.w3.org/2000/svg';

  var LOOP = {
    w: 1200, h: 596,
    phases: [
      { x: 132, w: 156, text: '1  IDEA' },
      { x: 298, w: 342, text: '2  REFINE, AS MANY ROUNDS AS IT TAKES' },
      { x: 650, w: 152, text: '3  HAND OVER' },
      { x: 812, w: 146, text: '4  DESIGN' },
      { x: 968, w: 122, text: '5  BUILD, TEST' },
      { x: 1100, w: 92, text: '6  LAND' }
    ],
    lanes: [
      { y: 60, h: 88, name: ['You'] },
      { y: 148, h: 182, name: ['ArChreator'] },
      { y: 330, h: 90, name: ['Your delivery', 'framework'] },
      { y: 420, h: 90, name: ['A coding', 'agent'] }
    ],
    nodes: [
      { id: 'u1', kind: 'you', step: 1, x: 140, y: 79, w: 140, h: 50, lines: ['Say your idea,', 'in plain words'] },
      { id: 'u2', kind: 'you', step: 2, x: 310, y: 79, w: 150, h: 50, lines: ['Answer its question,', 'or correct the picture'] },
      { id: 'u3', kind: 'you', step: 2, x: 480, y: 79, w: 150, h: 50, lines: ['Confirm what', 'the change says'] },
      { id: 'u6', kind: 'you', step: 6, x: 1101, y: 79, w: 90, h: 50, lines: ['Review', 'and merge'] },
      { id: 'a1', kind: 'arc', step: 2, x: 310, y: 170, w: 150, h: 66, lines: ['Work out what it', 'means for your', 'business, top down'] },
      { id: 'a2', kind: 'arc', step: 2, x: 480, y: 170, w: 150, h: 66, lines: ['Show you a picture', 'of what changes'] },
      { id: 'as', kind: 'stop', step: 2, x: 310, y: 256, w: 150, h: 58, lines: ['Stop and ask when', 'something clashes', 'or reads two ways'] },
      { id: 'a3', kind: 'arc', step: 3, x: 660, y: 170, w: 134, h: 66, lines: ['A short note of the', 'change, and a list of', 'the software needed'] },
      { id: 'a4', kind: 'arc', step: 3, x: 660, y: 256, w: 134, h: 58, lines: ['Your rules, carried', 'into the design'] },
      { id: 'a6', kind: 'arc', step: 6, x: 1101, y: 170, w: 90, h: 66, lines: ['Check the', 'model is', 'still true'] },
      { id: 'd1', kind: 'dlv', step: 4, x: 812, y: 345, w: 146, h: 60, lines: ['Design it, your', 'framework’s way'] },
      { id: 'c1', kind: 'cod', step: 5, x: 972, y: 435, w: 116, h: 60, lines: ['Build it,', 'test it'] },
      { id: 'k1', kind: 'done', step: 3, x: 132, y: 530, w: 662, h: 54, lines: ['Your business, defined and confirmed by you: the part that lasts'] },
      { id: 'k2', kind: 'done', step: 5, x: 812, y: 530, w: 379, h: 54, lines: ['The solution, built and tested'] }
    ],
    edges: [
      { id: 'e1', step: 1, pts: [[210, 129], [210, 203], [310, 203]] },
      { id: 'e2', step: 2, kind: 'loop', pts: [[360, 129], [360, 170]], label: 'answer', at: [360, 150] },
      { id: 'e3', step: 2, kind: 'loop', pts: [[460, 203], [480, 203]] },
      { id: 'e4', step: 2, kind: 'loop', pts: [[510, 170], [510, 150], [425, 150], [425, 129]], label: 'not yet', at: [468, 150] },
      { id: 'e5', step: 2, pts: [[590, 170], [590, 129]], label: 'reads true', at: [590, 150] },
      { id: 'e6', step: 2, kind: 'back', pts: [[385, 236], [385, 256]] },
      { id: 'e7', step: 2, kind: 'back', pts: [[310, 285], [298, 285], [298, 104], [310, 104]] },
      { id: 'e8', step: 3, pts: [[630, 104], [727, 104], [727, 170]], label: 'confirmed', at: [682, 104] },
      { id: 'e9', step: 4, pts: [[794, 203], [905, 203], [905, 345]], label: 'what to build', at: [850, 203] },
      { id: 'e10', step: 4, pts: [[794, 285], [852, 285], [852, 345]], label: 'your rules', at: [826, 285] },
      { id: 'e11', step: 5, pts: [[958, 375], [1030, 375], [1030, 435]], label: 'design and tasks', at: [1030, 412] },
      { id: 'e12', step: 6, pts: [[1088, 465], [1146, 465], [1146, 236]], label: 'pull request', at: [1146, 380] },
      { id: 'e13', step: 6, pts: [[1146, 170], [1146, 129]], label: 'all green', at: [1146, 150] },
      { id: 'e14', step: 4, kind: 'back', pts: [[812, 375], [430, 375], [430, 314]], label: 'a design question that changes what you meant', at: [588, 375] },
      { id: 'e15', step: 5, kind: 'back', pts: [[972, 465], [350, 465], [350, 314]], label: 'what building and testing taught you', at: [545, 465] },
      { id: 'e16', step: 3, pts: [[727, 314], [727, 530]], label: 'kept true on every change', at: [727, 508] },
      { id: 'e17', step: 5, pts: [[1030, 495], [1030, 530]] }
    ]
  };

  function el(name, attrs, parent) {
    var node = document.createElementNS(NS, name);
    for (var key in attrs) node.setAttribute(key, attrs[key]);
    if (parent) parent.appendChild(node);
    return node;
  }

  function path(pts, r) {
    var d = 'M' + pts[0][0] + ',' + pts[0][1];
    for (var i = 1; i < pts.length - 1; i++) {
      var a = pts[i - 1], b = pts[i], c = pts[i + 1];
      var toward = function (p, q) {
        var dx = q[0] - p[0], dy = q[1] - p[1], n = Math.max(Math.abs(dx), Math.abs(dy)) || 1;
        return [p[0] + dx / n * r, p[1] + dy / n * r];
      };
      var p1 = toward(b, a), p2 = toward(b, c);
      d += ' L' + p1[0].toFixed(1) + ',' + p1[1].toFixed(1) + ' Q' + b[0] + ',' + b[1] + ' ' + p2[0].toFixed(1) + ',' + p2[1].toFixed(1);
    }
    return d + ' L' + pts[pts.length - 1][0] + ',' + pts[pts.length - 1][1];
  }

  /* Draw the loop into `host`. Returns the svg, every part by id, and
     `step(n)`: highlight one step, or all of it with 0. With `onPick`, the
     six step chips along the top become buttons that call it. */
  function render(host, uid, onPick) {
    uid = uid || 'lp';
    var svg = el('svg', { viewBox: '0 0 ' + LOOP.w + ' ' + LOOP.h, 'class': 'lp', role: onPick ? 'group' : 'img',
      'aria-label': 'The loop: you say an idea; ArChreator turns it into a picture of your business that you correct and confirm; your delivery framework designs the software; a coding agent builds and tests it; checks run and you merge.' });
    var defs = el('defs', {}, svg);
    ['plain', 'loop', 'back'].forEach(function (kind) {
      var m = el('marker', { id: uid + '-' + kind, viewBox: '0 0 10 10', refX: 9, refY: 5, markerWidth: 9, markerHeight: 9,
        markerUnits: 'userSpaceOnUse', orient: 'auto-start-reverse' }, defs);
      el('path', { d: 'M0,0 L10,5 L0,10 z', 'class': 'lp-head ' + kind }, m);
    });
    var parts = {};
    LOOP.lanes.forEach(function (lane) {
      el('rect', { x: 8, y: lane.y, width: LOOP.w - 16, height: lane.h, 'class': 'lp-lane' }, svg);
      lane.name.forEach(function (line, i) {
        el('text', { x: 20, y: lane.y + lane.h / 2 + 5 + (i - (lane.name.length - 1) / 2) * 16, 'class': 'lp-lane-name' }, svg).textContent = line;
      });
    });
    LOOP.phases.forEach(function (phase, i) {
      var g = el('g', { 'class': 'lp-phase lp-part s' + (i + 1) }, svg);
      el('rect', { x: phase.x, y: 16, width: phase.w, height: 26, rx: 5 }, g);
      el('text', { x: phase.x + phase.w / 2, y: 33, 'text-anchor': 'middle' }, g).textContent = phase.text;
      parts['p' + (i + 1)] = g;
      if (onPick) {
        g.classList.add('lp-pick');
        g.setAttribute('role', 'button');
        g.setAttribute('tabindex', '0');
        g.setAttribute('aria-label', 'Step ' + phase.text.replace(/\s+/g, ' ').toLowerCase());
        g.addEventListener('click', function () { onPick(i + 1); });
        g.addEventListener('keydown', function (e) {
          if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onPick(i + 1); }
        });
      }
    });
    LOOP.edges.forEach(function (edge) {
      var kind = edge.kind || 'plain';
      var g = el('g', { 'class': 'lp-edge lp-part ' + kind + ' s' + edge.step }, svg);
      el('path', { d: path(edge.pts, 7), 'marker-end': 'url(#' + uid + '-' + kind + ')' }, g);
      if (edge.label) {
        var width = edge.label.length * 5.4 + 10;
        el('rect', { x: edge.at[0] - width / 2, y: edge.at[1] - 8, width: width, height: 16, rx: 3, 'class': 'bg' }, g);
        el('text', { x: edge.at[0], y: edge.at[1] + 4, 'text-anchor': 'middle' }, g).textContent = edge.label;
      }
      parts[edge.id] = g;
    });
    LOOP.nodes.forEach(function (node) {
      var g = el('g', { 'class': 'lp-node lp-part lp-' + node.kind + ' s' + node.step }, svg);
      el('rect', { x: node.x, y: node.y, width: node.w, height: node.h, rx: 6 }, g);
      var step = node.kind === 'done' ? 18 : 15.5;
      node.lines.forEach(function (line, i) {
        el('text', { x: node.x + node.w / 2, y: node.y + node.h / 2 + 4.4 + (i - (node.lines.length - 1) / 2) * step,
          'text-anchor': 'middle' }, g).textContent = line;
      });
      parts[node.id] = g;
    });
    host.appendChild(svg);
    return {
      svg: svg, parts: parts,
      step: function (n) {
        svg.classList.toggle('stepping', n > 0);
        Object.keys(parts).forEach(function (id) { parts[id].classList.toggle('on', parts[id].classList.contains('s' + n)); });
      }
    };
  }

  root.ArchLoop = { LOOP: LOOP, render: render };
})(window);
