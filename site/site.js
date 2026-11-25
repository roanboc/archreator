/* What the landing page does when somebody touches it. The page reads whole
   without any of this: every caption and every folder's note is in the HTML,
   and the script only decides which one is in front. */
(function () {
  'use strict';

  /* ---- the loop: six steps, each lighting its part of the drawing ---- */
  var frame = document.getElementById('loop');
  if (frame && window.ArchLoop) {
    var buttons = [].slice.call(document.querySelectorAll('.steps button'));
    var play = document.getElementById('loop-play');
    var caption = document.getElementById('loop-caption');
    var atRest = caption ? caption.innerHTML : '';
    var current = 0, timer = null;
    var loop = window.ArchLoop.render(frame, 'loop', function (n) { stop(); show(current === n ? 0 : n); });
    var centres = [210, 470, 727, 885, 1030, 1146];

    function show(n) {
      current = n;
      loop.step(n);
      buttons.forEach(function (b, i) { b.setAttribute('aria-pressed', i + 1 === n ? 'true' : 'false'); });
      if (caption) {
        if (n) {
          // The words are the step card's own, so they are written once.
          var card = buttons[n - 1];
          caption.textContent = '';
          var lead = document.createElement('b');
          lead.textContent = n + ' · ' + card.querySelector('h3').textContent + '. ';
          caption.appendChild(lead);
          caption.appendChild(document.createTextNode(card.querySelector('p').textContent));
        } else { caption.innerHTML = atRest; }
      }
      if (n && frame.scrollWidth > frame.clientWidth) {
        var x = centres[n - 1] / window.ArchLoop.LOOP.w * frame.scrollWidth - frame.clientWidth / 2;
        frame.scrollTo({ left: Math.max(0, x), behavior: 'smooth' });
      }
    }
    function stop() {
      if (timer) { clearInterval(timer); timer = null; }
      if (play) play.textContent = 'Play the six steps';
    }
    buttons.forEach(function (b, i) {
      b.addEventListener('click', function () { stop(); show(current === i + 1 ? 0 : i + 1); });
    });
    if (play) {
      play.addEventListener('click', function () {
        if (timer) { stop(); show(0); return; }
        play.textContent = 'Stop';
        show(1);
        timer = setInterval(function () {
          if (current >= buttons.length) { stop(); show(0); } else { show(current + 1); }
        }, 3800);
      });
    }
  }

  /* ---- the hero's picture: the example the tool really wrote, drawn in
          this page's colours rather than as a flat image ---- */
  var picture = document.getElementById('hero-picture');
  if (picture && window.fetch && location.protocol !== 'file:') {
    fetch(picture.getAttribute('data-src')).then(function (r) { return r.ok ? r.text() : ''; }).then(function (text) {
      if (text.indexOf('<svg') !== 0) return;
      var holder = document.createElement('div');
      holder.innerHTML = text;
      var svg = holder.querySelector('svg');
      if (!svg) return;
      svg.removeAttribute('width'); svg.removeAttribute('height');
      svg.setAttribute('role', 'img');
      svg.querySelectorAll('[tabindex]').forEach(function (g) { g.removeAttribute('tabindex'); g.removeAttribute('role'); });
      picture.textContent = '';
      picture.appendChild(svg);
    }).catch(function () {});
  }

  /* ---- the repository: pick a folder, read what it is for ---- */
  var tree = document.querySelector('.tree');
  if (tree) {
    var notes = [].slice.call(document.querySelectorAll('.shelf article'));
    var picks = [].slice.call(tree.querySelectorAll('button'));
    var open = function (key) {
      picks.forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-for') === key ? 'true' : 'false'); });
      notes.forEach(function (n) { n.hidden = n.id !== key; });
    };
    picks.forEach(function (b) { b.addEventListener('click', function () { open(b.getAttribute('data-for')); }); });
    open('at-strategy');
  }

  /* ---- copy a command ---- */
  [].slice.call(document.querySelectorAll('.copy')).forEach(function (b) {
    b.addEventListener('click', function () {
      var text = document.getElementById(b.getAttribute('data-copy')).textContent;
      var done = function () { b.textContent = 'Copied'; setTimeout(function () { b.textContent = 'Copy'; }, 1600); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, function () {});
    });
  });

  /* ---- the example page takes the height it needs, so it never scrolls
          inside its own frame ---- */
  var example = document.getElementById('example');
  if (example) {
    var fit = function () {
      try {
        var doc = example.contentDocument;
        if (doc && doc.documentElement) example.style.height = Math.max(520, doc.documentElement.scrollHeight) + 'px';
      } catch (e) { /* opened from a disk: the fixed height stands */ }
    };
    example.addEventListener('load', function () {
      fit();
      try { example.contentDocument.addEventListener('click', function () { setTimeout(fit, 60); }); } catch (e) {}
    });
    window.addEventListener('resize', fit);
  }
})();
