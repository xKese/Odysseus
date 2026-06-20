// static/js/standardanfragen/panel.js
// Standardanfragen-Bibliothek-UI fuer Meeder & Seifer (Phase 4).

(function () {
  'use strict';

  const API = '/api/standardanfragen';
  const $ = (id) => document.getElementById(id);
  let themes = [];
  let currentSlug = null;

  async function fetchJson(url, options = {}) {
    const res = await fetch(url, {
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
      ...options,
    });
    if (!res.ok) throw new Error(`${res.status}: ${await res.text().catch(() => res.statusText)}`);
    return res.json();
  }

  async function postJson(url, body) {
    return fetchJson(url, { method: 'POST', body: JSON.stringify(body || {}) });
  }

  function escapeHtml(str) {
    return String(str ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  async function loadThemes() {
    const target = $('standardanfragen-list');
    target.innerHTML = 'Lade…';
    try {
      const data = await fetchJson(API);
      themes = data.themes || [];
      if (!themes.length) {
        target.innerHTML = '<div style="opacity:0.7;">Noch keine Standardanfragen in der Bibliothek.</div>';
        return;
      }
      target.innerHTML = themes.map((t) => `
        <div class="standardanfragen-card" data-slug="${escapeHtml(t.slug)}" style="padding:8px;border:1px solid var(--border);border-radius:6px;margin-bottom:6px;cursor:pointer;${currentSlug === t.slug ? 'background:color-mix(in srgb, var(--accent-primary,#1F3864) 12%, transparent);' : ''}">
          <div><strong>${escapeHtml(t.name)}</strong></div>
          <div style="opacity:0.6;font-size:0.85em;margin-top:2px;">${t.stichwort_count} Stichworte</div>
        </div>
      `).join('');
      target.querySelectorAll('.standardanfragen-card').forEach((el) => {
        el.addEventListener('click', () => openTheme(el.dataset.slug));
      });
    } catch (e) {
      target.innerHTML = `<div style="color:var(--accent-error,#c00);">Fehler: ${escapeHtml(e.message)}</div>`;
    }
  }

  async function openTheme(slug) {
    currentSlug = slug;
    const target = $('standardanfragen-detail');
    target.innerHTML = 'Lade…';
    await loadThemes();  // re-highlight
    try {
      const data = await fetchJson(`${API}/${encodeURIComponent(slug)}`);
      target.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:10px;">
          <h3 style="margin:0;">${escapeHtml(data.name)}</h3>
          <code style="opacity:0.6;font-size:0.85em;">${escapeHtml(data.slug)}</code>
        </div>
        <h4 style="margin:6px 0 4px 0;">Stichworte fuer das Matching</h4>
        <ul style="margin:0 0 12px 0;padding-left:20px;">
          ${data.stichworte.map((s) => `<li>${escapeHtml(s)}</li>`).join('')}
        </ul>
        <h4 style="margin:6px 0 4px 0;">Antwort-Template</h4>
        <pre style="white-space:pre-wrap;background:var(--panel);padding:10px;border:1px solid var(--border);border-radius:6px;max-height:50vh;overflow:auto;font-size:0.9em;">${escapeHtml(data.antwort_template)}</pre>
        <div style="margin-top:8px;opacity:0.7;font-size:0.85em;">Platzhalter werden ueber den Skill <code>standardanfrage</code> oder per <code>POST /api/standardanfragen/${escapeHtml(data.slug)}/render</code> befuellt.</div>
      `;
    } catch (e) {
      target.innerHTML = `<div style="color:var(--accent-error,#c00);">Fehler: ${escapeHtml(e.message)}</div>`;
    }
  }

  async function runMatch() {
    const input = $('standardanfragen-match-input');
    const target = $('standardanfragen-match-result');
    const frage = input.value.trim();
    if (!frage) {
      target.innerHTML = '<div style="opacity:0.6;">Bitte Frage eintippen.</div>';
      return;
    }
    target.innerHTML = 'Suche…';
    try {
      const data = await postJson(`${API}/match`, { frage });
      const cands = data.candidates || [];
      const best = data.best_match;
      target.innerHTML = `
        <div style="margin-bottom:6px;">
          <strong>Bester Treffer:</strong>
          ${best ? `<a href="#" data-slug="${escapeHtml(best.slug)}" class="standardanfragen-match-link" style="color:var(--accent-primary,#1F3864);">${escapeHtml(best.name)}</a> (Score ${best.score.toFixed(2)})` : '<em>Kein Treffer ueber Schwelle (' + data.threshold + ').</em>'}
        </div>
        <div style="opacity:0.7;font-size:0.85em;">Kandidaten:</div>
        <ul style="margin:4px 0 0 0;padding-left:18px;font-size:0.85em;">
          ${cands.map((c) => `<li><a href="#" data-slug="${escapeHtml(c.slug)}" class="standardanfragen-match-link" style="color:var(--accent-primary,#1F3864);">${escapeHtml(c.name)}</a> (${c.score.toFixed(2)})</li>`).join('')}
        </ul>
      `;
      target.querySelectorAll('.standardanfragen-match-link').forEach((a) => {
        a.addEventListener('click', (e) => {
          e.preventDefault();
          openTheme(a.dataset.slug);
        });
      });
    } catch (e) {
      target.innerHTML = `<div style="color:var(--accent-error,#c00);">Fehler: ${escapeHtml(e.message)}</div>`;
    }
  }

  async function openPanel() {
    $('standardanfragen-modal').classList.remove('hidden');
    currentSlug = null;
    await loadThemes();
  }

  function closePanel() {
    $('standardanfragen-modal').classList.add('hidden');
  }

  function init() {
    const rail = $('rail-faq');
    if (rail) rail.addEventListener('click', openPanel);
    const close = $('close-standardanfragen-modal');
    if (close) close.addEventListener('click', closePanel);
    const matchBtn = $('standardanfragen-match-btn');
    if (matchBtn) matchBtn.addEventListener('click', runMatch);
    const input = $('standardanfragen-match-input');
    if (input) input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) runMatch();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
