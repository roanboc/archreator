/* The film, as a function of time. `FILM.seek(t)` places every mark where it
   belongs at second `t` and returns; nothing is left running. The renderer
   asks for one frame after another, and a page that loads this file can
   scrub it. The times come from timeline.js, which the voice tool wrote from
   the lengths of the spoken lines, so picture and sound share one clock. */
(function () {
  'use strict';
  var T = window.FILM_TIMELINE;
  var at = {};
  T.lines.forEach(function (line) { at[line.key] = line; });
  var $ = function (id) { return document.getElementById(id); };
  var clamp = function (x) { return Math.max(0, Math.min(1, x)); };
  var ease = function (x) { x = clamp(x); return x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2; };
  var L = function (key, offset) { return at[key].start + (offset || 0); };

  /* ---- scenes: each is on from its start to its end, with a short fade ---- */
  var scenes = [
    { el: $('s-gap'), from: 0, to: T.scenes.fix[1], first: true },
    { el: $('s-loop'), from: T.scenes.loop[0], to: T.scenes.loop[1] },
    { el: $('s-repo'), from: T.scenes.repo[0], to: T.scenes.repo[1] },
    { el: $('s-end'), from: T.scenes.end[0], to: T.duration + 1, last: true }
  ];

  /* ---- cues: a mark arrives at a time, rising a little as it does ---- */
  var cues = [];
  var arrive = function (el, t, rise) { cues.push({ el: el, t: t, rise: rise === undefined ? 18 : rise }); };

  arrive($('g-said'), 0.25);
  arrive($('road-a'), L('gap/1', 0.1), 0); arrive($('road-b'), L('fix/1', 0.0), 0);
  arrive($('ga-0'), L('gap/1', 0.2), 0); arrive($('ga-1'), L('gap/1', 0.5), 0);
  arrive($('ga-2'), L('gap/2', 2.3), 0); arrive($('ga-3'), L('gap/2', 4.2), 0);
  arrive($('ga-4'), L('gap/3', 0.5), 0);
  arrive($('gb-0'), L('fix/1', 0.1), 0); arrive($('gb-1'), L('fix/1', 0.5), 0);
  arrive($('gb-2'), L('fix/2', 0.9), 0); arrive($('gb-3'), L('fix/2', 2.9), 0); arrive($('gb-4'), L('fix/2', 3.9), 0);

  /* ---- the loop: its parts arrive with the words that name them ---- */
  var loop = window.ArchLoop.render($('loop'), 'film');
  var svg = loop.svg, parts = loop.parts;
  svg.removeAttribute('role');
  svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
  var drawn = [];
  var reveal = function (id, t) {
    var g = parts[id], line = g.querySelector('path');
    var solid = line && !g.classList.contains('back');
    drawn.push({ g: g, t: t, path: solid ? line : null, len: solid ? line.getTotalLength() : 0 });
  };
  [['p1', 'loop/1', 0.0], ['u1', 'loop/1', 1.5],
   ['e1', 'loop/2', 0.1], ['p2', 'loop/2', 0.3], ['a1', 'loop/2', 0.6],
   ['e3', 'loop/3', 0.2], ['a2', 'loop/3', 0.5],
   ['e4', 'loop/4', 0.1], ['u2', 'loop/4', 0.4], ['e2', 'loop/4', 1.4],
   ['e5', 'loop/5', 0.2], ['u3', 'loop/5', 0.5],
   ['p3', 'loop/6', 0.1], ['e8', 'loop/6', 0.3], ['a3', 'loop/6', 1.0], ['a4', 'loop/6', 4.0],
   ['p4', 'loop/7', 0.1], ['e9', 'loop/7', 0.2], ['e10', 'loop/7', 0.3], ['d1', 'loop/7', 0.7],
   ['p5', 'loop/7', 2.8], ['e11', 'loop/7', 2.9], ['c1', 'loop/7', 3.2],
   ['as', 'loop/8', 0.4], ['e14', 'loop/8', 0.9], ['e15', 'loop/8', 1.7], ['e6', 'loop/8', 3.6], ['e7', 'loop/8', 3.8],
   ['p6', 'loop/9', 0.1], ['e12', 'loop/9', 0.2], ['a6', 'loop/9', 0.7], ['e13', 'loop/9', 3.0], ['u6', 'loop/9', 3.2],
   ['e16', 'loop/10', 0.3], ['e17', 'loop/10', 0.3], ['k2', 'loop/10', 1.7], ['k1', 'loop/10', 2.7]
  ].forEach(function (c) { reveal(c[0], L(c[1], c[2])); });

  /* The camera: which part of the drawing fills the frame, and from when.
     Close enough to read on a small screen, wide again at the end. */
  var views = [
    { t: T.scenes.loop[0], v: [110, 52, 480, 218] },
    { t: L('loop/2', -0.4), v: [110, 52, 600, 273] },
    { t: L('loop/4', -0.4), v: [286, 52, 520, 236] },
    { t: L('loop/6', -0.4), v: [420, 52, 640, 291] },
    { t: L('loop/7', -0.4), v: [464, 162, 736, 334.5] },
    { t: L('loop/8', -0.4), v: [130, 46, 1070, 486] },
    { t: L('loop/9', -0.4), v: [800, 60, 400, 182] },
    { t: L('loop/10', -0.4), v: [0, -2, 1200, 600] }
  ];
  /* The step the camera is on, said in words above the drawing: the chips
     along the drawing's own top are out of frame while it is close. */
  var titles = [
    { t: T.scenes.loop[0], text: '1 · You say the idea' },
    { t: L('loop/2', -0.2), text: '2 · It becomes a picture you can correct' },
    { t: L('loop/6', -0.2), text: '3 · It hands over' },
    { t: L('loop/7', -0.2), text: '4 · Your framework designs' },
    { t: L('loop/7', 2.7), text: '5 · An agent builds and tests' },
    { t: L('loop/8', -0.2), text: 'When building teaches you something' },
    { t: L('loop/9', -0.2), text: '6 · It is checked, and you merge' },
    { t: L('loop/10', -0.2), text: 'What you end up with' }
  ];
  var MOVE = 1.2;
  /* The frame is 1760 x 800; a view of another shape is letterboxed inside
     it by the browser, so each is widened here to that shape first. */
  views.forEach(function (k) {
    var want = 1760 / 800, w = k.v[2], h = k.v[3];
    if (w / h < want) { var nw = h * want; k.v = [k.v[0] - (nw - w) / 2, k.v[1], nw, h]; }
    else { var nh = w / want; k.v = [k.v[0], k.v[1] - (nh - h) / 2, w, nh]; }
  });
  var loopEdges = ['e2', 'e3', 'e4'].map(function (id) { return parts[id].querySelector('path'); });

  /* ---- the repository: one row lit at a time, and its card beside it ---- */
  var rows = ['r-root', 'r-agents', 'r-arch', 'r-0', 'r-1', 'r-2', 'r-3', 'r-4', 'r-5', 'r-scope', 'r-scripts', 'r-work'];
  rows.forEach(function (id, i) { arrive($(id), L('repo/1', 0.15 + i * 0.07), 0); });
  var lit = [
    ['repo/1', null, 'c-all'], ['repo/2', 'r-agents', 'c-agents'], ['repo/3', 'r-arch', 'c-arch'],
    ['repo/4a', 'r-1', 'c-1'], ['repo/4b', 'r-2', 'c-2'], ['repo/4c', 'r-3', 'c-3'], ['repo/4d', 'r-4', 'c-4'], ['repo/4e', 'r-5', 'c-5'],
    ['repo/5', 'r-scope', 'c-scope'], ['repo/6', 'r-scripts', 'c-scripts'], ['repo/7', 'r-work', 'c-work']
  ].map(function (x, i, all) {
    return { from: L(x[0], -0.12), to: i + 1 < all.length ? L(all[i + 1][0], -0.12) : T.scenes.repo[1] + 1,
             row: x[1] && $(x[1]), card: $(x[2]) };
  });

  arrive($('e-line'), L('end/1', 0.3)); arrive($('e-cmd'), L('end/1', 2.6)); arrive($('e-url'), L('end/1', 4.4), 0); arrive($('e-voice'), L('end/1', 4.4), 0);

  function seek(t) {
    scenes.forEach(function (s) {
      var a = s.first ? 1 : ease((t - s.from) / 0.5);
      var b = s.last ? 1 : 1 - ease((t - (s.to - 0.45)) / 0.45);
      s.el.style.opacity = t < s.from || t >= s.to ? 0 : Math.min(a, b);
    });
    $('brandmark').style.opacity = 1 - ease((t - (T.scenes.end[0] - 0.4)) / 0.4);

    cues.forEach(function (c) {
      var p = ease((t - c.t) / 0.45);
      c.el.style.opacity = p;
      c.el.style.transform = c.rise ? 'translateY(' + ((1 - p) * c.rise).toFixed(2) + 'px)' : '';
    });

    drawn.forEach(function (d) {
      var p = clamp((t - d.t) / 0.55);
      d.g.style.opacity = d.path ? clamp(p * 4) : ease(p);
      if (d.path) {
        d.path.style.strokeDasharray = d.len;
        d.path.style.strokeDashoffset = (d.len * (1 - ease(p))).toFixed(2);
        d.path.style.markerEnd = p > 0.92 ? '' : 'none';
        var label = d.g.querySelectorAll('rect, text');
        for (var i = 0; i < label.length; i++) label[i].style.opacity = ease((p - 0.5) * 2);
      }
    });

    var k = 0;
    while (k + 1 < views.length && t >= views[k + 1].t) k++;
    var from = views[Math.max(0, k - 1)].v, to = views[k].v, p = k === 0 ? 1 : ease((t - views[k].t) / MOVE);
    svg.setAttribute('viewBox', from.map(function (x, i) { return (x + (to[i] - x) * p).toFixed(2); }).join(' '));

    var title = titles[0];
    titles.forEach(function (x) { if (t >= x.t) title = x; });
    $('loop-step').textContent = title.text;
    $('loop-step').style.opacity = Math.min(1, ease((t - title.t) / 0.3) + (title === titles[0] ? 1 : 0));

    /* "Round and round": the three lines of the conversation swell twice. */
    var round = clamp((t - L('loop/4', 1.9)) / 1.9);
    var swell = round > 0 && round < 1 ? Math.pow(Math.sin(round * Math.PI * 2), 2) : 0;
    loopEdges.forEach(function (e) { e.style.strokeWidth = (2.4 + 3.2 * swell).toFixed(2); });
    /* "That second one lasts": the definition's box holds the eye. */
    var last = clamp((t - L('loop/10', 5.0)) / 1.6);
    var hold = last > 0 ? Math.sin(Math.min(last, 1) * Math.PI) : 0;
    parts.k1.querySelector('rect').style.strokeWidth = (2 + 5 * hold).toFixed(2);

    lit.forEach(function (x) {
      var on = t >= x.from && t < x.to;
      if (x.row) x.row.classList.toggle('on', on);
      x.card.style.opacity = on ? Math.min(ease((t - x.from) / 0.3), 1 - ease((t - (x.to - 0.2)) / 0.2)) : 0;
    });
  }

  window.FILM = { duration: T.duration, seek: seek, lines: T.lines };
  /* Opened by a person, the page shows one moment: film.html?t=42 */
  var asked = /[?&]t=([0-9.]+)/.exec(location.search);
  seek(asked ? parseFloat(asked[1]) : 0);
})();
