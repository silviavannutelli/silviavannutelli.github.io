(function () {
  'use strict';

  var doc = document;
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function $(sel, root) { return (root || doc).querySelector(sel); }
  function $all(sel, root) { return Array.prototype.slice.call((root || doc).querySelectorAll(sel)); }

  /* ---------- Mobile menu ---------- */

  function initMenu() {
    var btn = $('[data-menu-toggle]');
    var sheet = $('#menu-sheet');
    if (!btn || !sheet) return;

    function setOpen(open) {
      sheet.classList.toggle('is-open', open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      var use = btn.querySelector('use');
      if (use) use.setAttribute('href', 'assets/img/icons.svg#' + (open ? 'i-close' : 'i-menu'));
    }

    btn.addEventListener('click', function () {
      setOpen(!sheet.classList.contains('is-open'));
    });
    doc.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && sheet.classList.contains('is-open')) { setOpen(false); btn.focus(); }
    });
    doc.addEventListener('click', function (e) {
      if (!sheet.classList.contains('is-open')) return;
      if (sheet.contains(e.target) || btn.contains(e.target)) return;
      setOpen(false);
    });
    $all('a, button', sheet).forEach(function (el) {
      el.addEventListener('click', function () { setOpen(false); });
    });
  }

  /* ---------- Toast ---------- */

  var toastTimer = null;
  function toast(msg) {
    var el = $('#toast');
    if (!el) {
      el = doc.createElement('div');
      el.id = 'toast';
      el.className = 'toast';
      el.setAttribute('role', 'status');
      el.setAttribute('aria-live', 'polite');
      doc.body.appendChild(el);
    }
    el.textContent = msg;
    el.classList.add('is-on');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { el.classList.remove('is-on'); }, 2000);
  }

  /* ---------- Contact dialog ---------- */

  function initContact() {
    var dialog = $('#contact');
    if (!dialog || typeof dialog.showModal !== 'function') return;
    var lastTrigger = null;

    function open(trigger) {
      lastTrigger = trigger || null;
      dialog.classList.remove('is-closing');
      dialog.showModal();
    }

    function close() {
      if (!dialog.open) return;
      if (reduceMotion) { dialog.close(); return; }
      dialog.classList.add('is-closing');
      setTimeout(function () {
        dialog.classList.remove('is-closing');
        dialog.close();
      }, 200);
    }

    $all('[data-contact]').forEach(function (el) {
      el.addEventListener('click', function (e) {
        e.preventDefault();
        open(el);
      });
    });

    $all('[data-contact-close]', dialog).forEach(function (el) {
      el.addEventListener('click', close);
    });

    dialog.addEventListener('cancel', function (e) {
      e.preventDefault();
      close();
    });

    dialog.addEventListener('click', function (e) {
      if (e.target !== dialog) return;
      var r = dialog.getBoundingClientRect();
      var inside = e.clientX >= r.left && e.clientX <= r.right && e.clientY >= r.top && e.clientY <= r.bottom;
      if (!inside) close();
    });

    dialog.addEventListener('close', function () {
      if (lastTrigger && typeof lastTrigger.focus === 'function') lastTrigger.focus();
    });

    if (location.hash === '#contact') open();

    var copyBtn = $('[data-copy]', dialog);
    if (copyBtn) {
      copyBtn.addEventListener('click', function () {
        var text = copyBtn.getAttribute('data-copy');
        var done = function () {
          var use = copyBtn.querySelector('use');
          if (use) {
            use.setAttribute('href', 'assets/img/icons.svg#i-check');
            setTimeout(function () { use.setAttribute('href', 'assets/img/icons.svg#i-copy'); }, 1600);
          }
          toast('Email copied');
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(done, function () { toast(text); });
        } else {
          toast(text);
        }
      });
    }
  }

  /* ---------- Reveal on scroll ---------- */

  function initReveal() {
    var items = $all('.reveal');
    if (!items.length) return;
    if (reduceMotion || !('IntersectionObserver' in window)) {
      items.forEach(function (el) { el.classList.add('is-in'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-in');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0, rootMargin: '0px 0px -8% 0px' });
    items.forEach(function (el) { io.observe(el); });

    // Safety net: never leave content hidden.
    setTimeout(function () {
      items.forEach(function (el) {
        var r = el.getBoundingClientRect();
        if (r.top < window.innerHeight) el.classList.add('is-in');
      });
    }, 1500);
  }

  /* ---------- Work-in-progress window ---------- */

  function initWip() {
    var root = $('[data-wip]');
    if (!root) return;
    var tabs = $all('[role="tab"]', root);
    var panels = $all('[role="tabpanel"]', root);
    var countEl = $('[data-wip-current]', root);
    var toggle = $('[data-wip-toggle]', root);
    if (!tabs.length) return;

    var DURATION = 7000;
    var index = 0;
    var playing = !reduceMotion;
    var hovering = false;
    var start = 0;
    var elapsed = 0;
    var raf = null;

    function bar(i) { return tabs[i].querySelector('.bar i'); }

    function select(i, focus) {
      i = (i + tabs.length) % tabs.length;
      tabs.forEach(function (t, k) {
        var on = k === i;
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.tabIndex = on ? 0 : -1;
        var b = bar(k);
        if (b) b.className = 'p0';
      });
      panels.forEach(function (p, k) {
        var on = k === i;
        p.hidden = !on;
        p.classList.remove('is-entering');
        if (on && !reduceMotion) {
          void p.offsetWidth;
          p.classList.add('is-entering');
        }
      });
      index = i;
      elapsed = 0;
      start = performance.now();
      if (countEl) countEl.textContent = String(i + 1);
      if (focus) tabs[i].focus();
      var list = tabs[i].closest('ul');
      if (list && list.scrollWidth > list.clientWidth) {
        var li = tabs[i].parentElement;
        list.scrollTo({ left: li.offsetLeft - 10, behavior: reduceMotion ? 'auto' : 'smooth' });
      }
    }

    function tick(now) {
      if (playing && !hovering && !doc.hidden) {
        elapsed += now - start;
        var p = Math.min(elapsed / DURATION, 1);
        var b = bar(index);
        if (b) b.className = 'p' + Math.round(p * 100);
        if (p >= 1) select(index + 1, false);
      }
      start = now;
      raf = requestAnimationFrame(tick);
    }

    function setPlaying(on) {
      playing = on;
      if (toggle) {
        toggle.setAttribute('aria-pressed', on ? 'false' : 'true');
        toggle.setAttribute('aria-label', on ? 'Pause rotation' : 'Play rotation');
        var use = toggle.querySelector('use');
        if (use) use.setAttribute('href', 'assets/img/icons.svg#' + (on ? 'i-pause' : 'i-play'));
      }
    }

    tabs.forEach(function (t, k) {
      t.addEventListener('click', function () { select(k, false); });
      t.addEventListener('keydown', function (e) {
        var key = e.key;
        if (key === 'ArrowDown' || key === 'ArrowRight') { e.preventDefault(); setPlaying(false); select(index + 1, true); }
        else if (key === 'ArrowUp' || key === 'ArrowLeft') { e.preventDefault(); setPlaying(false); select(index - 1, true); }
        else if (key === 'Home') { e.preventDefault(); setPlaying(false); select(0, true); }
        else if (key === 'End') { e.preventDefault(); setPlaying(false); select(tabs.length - 1, true); }
      });
    });

    var prev = $('[data-wip-prev]', root);
    var next = $('[data-wip-next]', root);
    if (prev) prev.addEventListener('click', function () { select(index - 1, false); });
    if (next) next.addEventListener('click', function () { select(index + 1, false); });
    if (toggle) toggle.addEventListener('click', function () { setPlaying(!playing); });

    root.addEventListener('mouseenter', function () { hovering = true; });
    root.addEventListener('mouseleave', function () { hovering = false; });
    root.addEventListener('focusin', function () { hovering = true; });
    root.addEventListener('focusout', function (e) {
      if (!root.contains(e.relatedTarget)) hovering = false;
    });

    setPlaying(playing);
    select(0, false);
    raf = requestAnimationFrame(tick);
  }

  /* ---------- Research filters ---------- */

  function initFilters() {
    var bar = $('[data-filters]');
    if (!bar) return;
    var buttons = $all('button[data-filter]', bar);
    var groups = $all('[data-group]');

    function apply(filter, push) {
      if (!buttons.some(function (b) { return b.getAttribute('data-filter') === filter; })) filter = 'all';
      buttons.forEach(function (b) {
        b.setAttribute('aria-pressed', b.getAttribute('data-filter') === filter ? 'true' : 'false');
      });
      groups.forEach(function (g) {
        g.hidden = !(filter === 'all' || g.getAttribute('data-group') === filter);
        if (!g.hidden) $all('.reveal', g).forEach(function (el) { el.classList.add('is-in'); });
      });
      if (push) {
        var url = filter === 'all' ? location.pathname : location.pathname + '#' + filter;
        history.replaceState(null, '', url);
      }
    }

    buttons.forEach(function (b) {
      b.addEventListener('click', function () { apply(b.getAttribute('data-filter'), true); });
    });

    var initial = (location.hash || '').replace('#', '');
    if (!/^[a-z0-9-]+$/.test(initial)) initial = '';
    if (initial) {
      apply(initial, false);
      var target = doc.getElementById(initial);
      if (target) setTimeout(function () { target.scrollIntoView(); }, 60);
    }
  }

  /* ---------- Expanders (abstracts, course descriptions) ---------- */

  function initExpanders() {
    $all('[data-expand]').forEach(function (btn) {
      var target = doc.getElementById(btn.getAttribute('aria-controls'));
      if (!target) return;
      var label = btn.querySelector('.lbl');
      var closedText = label ? label.textContent : '';
      var openText = btn.getAttribute('data-open-label') || 'Hide';
      btn.addEventListener('click', function () {
        var open = btn.getAttribute('aria-expanded') !== 'true';
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
        target.classList.toggle('is-open', open);
        target.setAttribute('aria-hidden', open ? 'false' : 'true');
        if (label) label.textContent = open ? openText : closedText;
      });
    });
  }

  /* ---------- CV table of contents ---------- */

  function initToc() {
    var links = $all('.cv-toc a');
    if (!links.length || !('IntersectionObserver' in window)) return;
    var map = {};
    links.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        links.forEach(function (a) { a.classList.remove('is-active'); });
        var a = map[entry.target.id];
        if (a) a.classList.add('is-active');
      });
    }, { rootMargin: '-20% 0px -70% 0px' });
    Object.keys(map).forEach(function (id) {
      var el = doc.getElementById(id);
      if (el) io.observe(el);
    });
  }

  function initYear() {
    $all('[data-year]').forEach(function (el) { el.textContent = String(new Date().getFullYear()); });
  }

  function boot() {
    initMenu();
    initContact();
    initReveal();
    initWip();
    initFilters();
    initExpanders();
    initToc();
    initYear();
  }

  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
