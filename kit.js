// Small shared helpers for the games: saved bests, the end-of-game dialog,
// confetti. Plain script, no build step; exposes window.Kit.
(function () {
  const PREFIX = 'kids-games:';

  // Best effort: private browsing or blocked storage just means nothing is saved.
  const store = {
    get(key, fallback) {
      try {
        const raw = localStorage.getItem(PREFIX + key);
        return raw == null ? fallback : JSON.parse(raw);
      } catch (e) { return fallback; }
    },
    set(key, value) {
      try { localStorage.setItem(PREFIX + key, JSON.stringify(value)); } catch (e) {}
    }
  };

  function best(key) { return store.get('best:' + key, null); }

  // Saves `value` if it beats the stored best. Returns { best, isNew }.
  function record(key, value, { lowerIsBetter = false } = {}) {
    const prev = best(key);
    const isNew = prev == null || (lowerIsBetter ? value < prev : value > prev);
    if (isNew) store.set('best:' + key, value);
    return { best: isNew ? value : prev, isNew: isNew && prev != null };
  }

  function esc(s) {
    return String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }

  // dialog({ emoji, title, html, badge, actions: [{ label, ghost, onClick }] })
  // `html` is trusted markup from the game; `title` and labels are escaped.
  function dialog({ emoji = '', title = '', html = '', badge = '', actions = [] }) {
    const overlay = document.createElement('div');
    overlay.className = 'overlay';
    overlay.innerHTML =
      `<div class="dialog" role="dialog" aria-modal="true" aria-label="${esc(title)}">` +
      (emoji ? `<div class="emoji" aria-hidden="true">${emoji}</div>` : '') +
      `<h2>${esc(title)}</h2>${html}` +
      (badge ? `<div class="badge">${esc(badge)}</div>` : '') +
      '<div class="actions"></div></div>';
    const close = () => overlay.remove();
    const row = overlay.querySelector('.actions');
    actions.forEach(({ label, ghost, onClick }) => {
      const b = document.createElement('button');
      b.className = 'btn' + (ghost ? ' ghost' : ' big');
      b.textContent = label;
      b.addEventListener('click', () => { close(); if (onClick) onClick(); });
      row.appendChild(b);
    });
    document.body.appendChild(overlay);
    const first = row.querySelector('button');
    if (first) first.focus({ preventScroll: true });
    return close;
  }

  function celebrate(colors = ['#E85D75', '#2EB872', '#F2A93B', '#5B5BD6', '#8a8aff', '#ffffff']) {
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const box = document.createElement('div');
    box.className = 'confetti';
    for (let i = 0; i < 90; i++) {
      const p = document.createElement('i');
      p.style.left = Math.random() * 100 + 'vw';
      p.style.background = colors[i % colors.length];
      p.style.animationDuration = 1.6 + Math.random() * 1.6 + 's';
      p.style.animationDelay = Math.random() * 0.5 + 's';
      p.style.setProperty('--dx', (Math.random() * 40 - 20) + 'vw');
      p.style.setProperty('--rot', (Math.random() * 900 - 450) + 'deg');
      box.appendChild(p);
    }
    document.body.appendChild(box);
    setTimeout(() => box.remove(), 4000);
  }

  // Re-trigger a one-shot CSS animation class (e.g. .bump on a stat).
  function pulse(el, cls = 'bump') {
    el.classList.remove(cls);
    void el.offsetWidth;
    el.classList.add(cls);
  }

  window.Kit = { store, best, record, esc, dialog, celebrate, pulse };
})();
