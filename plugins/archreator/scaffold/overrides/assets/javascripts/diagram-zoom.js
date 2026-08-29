/*
  A diagram is model content rendered for a person. This viewer moves the
  already-rendered Mermaid host into a modal stage, then returns that exact
  node to its source position. Material uses a closed shadow root for the SVG,
  so cloning or reading the drawing is neither possible nor necessary.
*/
(function () {
  "use strict";

  if (window.__archreatorDiagramZoom) return;
  window.__archreatorDiagramZoom = true;

  var host = null;
  var placeholder = null;
  var returnFocus = null;
  var previousOverflow = "";
  var scale = 1;
  var x = 0;
  var y = 0;
  var dragging = false;
  var lastX = 0;
  var lastY = 0;
  var moved = 0;

  function overlay() {
    return document.getElementById("ar-zoom");
  }

  function stage() {
    return document.getElementById("ar-zoom-stage");
  }

  function apply() {
    var target = stage();
    if (target) {
      target.style.transform =
        "translate(" + x + "px," + y + "px) scale(" + scale + ")";
    }
  }

  function fit() {
    var target = stage();
    if (!host || !target) return;
    target.style.transform = "";
    var box = host.getBoundingClientRect();
    if (!box.width || !box.height) {
      apply();
      return;
    }
    scale = Math.min(
      (window.innerWidth * 0.92) / box.width,
      (window.innerHeight * 0.84) / box.height
    );
    x = (window.innerWidth - box.width * scale) / 2;
    y = (window.innerHeight - box.height * scale) / 2;
    apply();
  }

  function zoom(factor, cx, cy) {
    var next = Math.min(Math.max(scale * factor, 0.1), 20);
    x = cx - (cx - x) * (next / scale);
    y = cy - (cy - y) * (next / scale);
    scale = next;
    apply();
  }

  function prepareDiagram(node) {
    var dialog = overlay();
    if (!dialog || !node || dialog.contains(node)) return;
    if (!node.hasAttribute("tabindex")) node.setAttribute("tabindex", "0");
    node.setAttribute("aria-haspopup", "dialog");
    if (!node.hasAttribute("aria-label")) {
      node.setAttribute(
        "aria-label",
        dialog.getAttribute("data-open-label") || "Open diagram full screen"
      );
    }
  }

  function prepareAll(root) {
    var scope = root && root.querySelectorAll ? root : document;
    if (scope.matches && scope.matches(".mermaid")) prepareDiagram(scope);
    scope.querySelectorAll(".mermaid").forEach(prepareDiagram);
  }

  function open(node) {
    var dialog = overlay();
    var target = stage();
    if (!dialog || !target || host || !node) return;

    host = node;
    placeholder = document.createComment("ar-zoom");
    returnFocus = document.activeElement;
    previousOverflow = document.body.style.overflow;
    host.replaceWith(placeholder);
    target.appendChild(host);
    dialog.hidden = false;
    document.body.style.overflow = "hidden";
    scale = 1;
    x = 0;
    y = 0;

    requestAnimationFrame(function () {
      fit();
      var closeButton = dialog.querySelector('[data-ar-zoom="close"]');
      if (closeButton) closeButton.focus();
    });
  }

  function close(restoreFocus) {
    var dialog = overlay();
    if (!host) {
      if (dialog) dialog.hidden = true;
      return;
    }

    if (placeholder && placeholder.parentNode) {
      placeholder.replaceWith(host);
    } else {
      host.remove();
    }
    var focusTarget = returnFocus;
    host = null;
    placeholder = null;
    returnFocus = null;
    dragging = false;
    document.body.style.overflow = previousOverflow;
    if (dialog) dialog.hidden = true;

    if (restoreFocus !== false && focusTarget && focusTarget.isConnected) {
      focusTarget.focus();
    }
  }

  function focusableControls(dialog) {
    return Array.from(dialog.querySelectorAll("button:not([disabled])"));
  }

  document.addEventListener("click", function (event) {
    var target = event.target;
    if (!target || !target.closest) return;

    var dialog = overlay();
    var action = target.getAttribute &&
      target.getAttribute("data-ar-zoom");

    if (dialog && !dialog.hidden) {
      if (action === "in") {
        zoom(1.25, window.innerWidth / 2, window.innerHeight / 2);
      } else if (action === "out") {
        zoom(0.8, window.innerWidth / 2, window.innerHeight / 2);
      } else if (action === "fit") {
        fit();
      } else if (action === "close" ||
                 (target === dialog && moved < 5)) {
        close();
      }
      return;
    }

    var diagram = target.closest(".mermaid");
    if (!diagram || String(window.getSelection() || "")) return;
    open(diagram);
  });

  document.addEventListener("keydown", function (event) {
    var dialog = overlay();

    if (!dialog || dialog.hidden) {
      if ((event.key === "Enter" || event.key === " ") &&
          event.target && event.target.matches &&
          event.target.matches(".mermaid")) {
        event.preventDefault();
        open(event.target);
      }
      return;
    }

    if (event.key === "Escape") {
      event.preventDefault();
      close();
    } else if (event.key === "+" || event.key === "=") {
      event.preventDefault();
      zoom(1.25, window.innerWidth / 2, window.innerHeight / 2);
    } else if (event.key === "-") {
      event.preventDefault();
      zoom(0.8, window.innerWidth / 2, window.innerHeight / 2);
    } else if (event.key === "0") {
      event.preventDefault();
      fit();
    } else if (event.key === "Tab") {
      var controls = focusableControls(dialog);
      if (!controls.length) {
        event.preventDefault();
        return;
      }
      var first = controls[0];
      var last = controls[controls.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }
  });

  document.addEventListener("wheel", function (event) {
    var dialog = overlay();
    if (!dialog || dialog.hidden || !dialog.contains(event.target)) return;
    event.preventDefault();
    zoom(
      event.deltaY < 0 ? 1.12 : 0.89,
      event.clientX,
      event.clientY
    );
  }, { passive: false });

  document.addEventListener("pointerdown", function (event) {
    var dialog = overlay();
    if (!dialog || dialog.hidden || !dialog.contains(event.target)) return;
    if (event.target.closest && event.target.closest(".ar-zoom__bar")) return;
    dragging = true;
    moved = 0;
    lastX = event.clientX;
    lastY = event.clientY;
    dialog.setPointerCapture(event.pointerId);
  });

  document.addEventListener("pointermove", function (event) {
    if (!dragging) return;
    var dx = event.clientX - lastX;
    var dy = event.clientY - lastY;
    moved += Math.abs(dx) + Math.abs(dy);
    x += dx;
    y += dy;
    lastX = event.clientX;
    lastY = event.clientY;
    apply();
  });

  document.addEventListener("pointerup", function () {
    dragging = false;
  });
  document.addEventListener("pointercancel", function () {
    dragging = false;
  });

  function pageReady() {
    close(false);
    prepareAll(document);
  }

  if (typeof document$ !== "undefined" && document$.subscribe) {
    document$.subscribe(pageReady);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", pageReady, { once: true });
  } else {
    pageReady();
  }

  new MutationObserver(function (records) {
    records.forEach(function (record) {
      record.addedNodes.forEach(function (node) {
        if (node.nodeType === 1) prepareAll(node);
      });
    });
  }).observe(document.documentElement, { childList: true, subtree: true });

  window.addEventListener("beforeunload", function () {
    close(false);
  });
})();
