// static/js/portfolio/panel.js
// Portfolio-Panel fuer Meeder & Seifer (Phase 2).
// Self-contained, kein Framework. Listet Portfolios, erlaubt Anlegen,
// zeigt Snapshots und Summary pro Snapshot, unterstuetzt CSV-/XLSX-Upload.

(function () {
  'use strict';

  const API = '/api/portfolios';
  const $ = (id) => document.getElementById(id);
  let portfolios = [];
  let currentPortfolio = null;
  let currentSnapshot = null;

  // ----------------------------------------------------------------
  // Fetch helpers
  // ----------------------------------------------------------------

  async function fetchJson(url, options = {}) {
    const res = await fetch(url, {
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
      ...options,
    });
    if (!res.ok) {
      throw new Error(`${res.status}: ${await res.text().catch(() => res.statusText)}`);
    }
    return res.json();
  }

  async function postJson(url, body) {
    return fetchJson(url, { method: 'POST', body: JSON.stringify(body || {}) });
  }

  async function deleteUrl(url) {
    const res = await fetch(url, { method: 'DELETE', credentials: 'same-origin' });
    if (!res.ok) throw new Error(`${res.status}: ${await res.text().catch(() => res.statusText)}`);
    return res.json().catch(() => ({}));
  }

  function escapeHtml(str) {
    return String(str ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function fmtMoney(val, currency) {
    if (val == null || val === '') return '—';
    const n = typeof val === 'number' ? val : Number(val);
    if (!isFinite(n)) return escapeHtml(val);
    return n.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
      + (currency ? ` ${currency}` : '');
  }

  function fmtDate(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    if (isNaN(d.getTime())) return iso;
    return d.toLocaleDateString('de-DE');
  }

  // ----------------------------------------------------------------
  // Portfolio list
  // ----------------------------------------------------------------

  async function loadPortfolios() {
    const target = $('portfolio-list');
    target.innerHTML = 'Lade…';
    try {
      const data = await fetchJson(API);
      portfolios = data.portfolios || [];
      if (!portfolios.length) {
        target.innerHTML = '<div style="opacity:0.7;">Noch keine Portfolios — oben rechts auf "+ Neues Portfolio" klicken.</div>';
        return;
      }
      target.innerHTML = portfolios.map((p) => `
        <div class="portfolio-card" data-portfolio-id="${escapeHtml(p.id)}" style="padding:10px;border:1px solid var(--border);border-radius:8px;margin-bottom:8px;cursor:pointer;">
          <div style="display:flex;justify-content:space-between;align-items:baseline;">
            <strong>${escapeHtml(p.mandant_name)}</strong>
            <span style="opacity:0.6;font-size:0.85em;">${p.snapshot_count || 0} Snapshot${(p.snapshot_count || 0) === 1 ? '' : 's'}</span>
          </div>
          <div style="opacity:0.7;font-size:0.9em;margin-top:4px;">${escapeHtml(p.description) || '—'}</div>
          <div style="opacity:0.5;font-size:0.8em;margin-top:2px;">Basis: ${escapeHtml(p.base_currency)}</div>
        </div>
      `).join('');
      target.querySelectorAll('.portfolio-card').forEach((el) => {
        el.addEventListener('click', () => openPortfolio(el.dataset.portfolioId));
      });
    } catch (e) {
      target.innerHTML = `<div style="color:var(--accent-error,#c00);">Fehler: ${escapeHtml(e.message)}</div>`;
    }
  }

  // ----------------------------------------------------------------
  // Portfolio detail (snapshots)
  // ----------------------------------------------------------------

  async function openPortfolio(id) {
    const p = portfolios.find((x) => x.id === id);
    if (!p) return;
    currentPortfolio = p;
    currentSnapshot = null;
    const detail = $('portfolio-detail');
    detail.classList.remove('hidden');
    detail.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:10px;">
        <h3 style="margin:0;">${escapeHtml(p.mandant_name)}</h3>
        <div>
          <button id="portfolio-detail-delete" class="secondary-btn">Portfolio loeschen</button>
          <button id="portfolio-detail-close" class="secondary-btn">Schliessen</button>
        </div>
      </div>
      <div style="margin-bottom:12px;padding:8px;border:1px dashed var(--border);border-radius:6px;">
        <div style="font-weight:600;margin-bottom:6px;">Snapshot hochladen</div>
        <form id="portfolio-upload-form" style="display:flex;flex-wrap:wrap;gap:6px;align-items:center;">
          <input type="file" id="portfolio-upload-file" accept=".csv,.xlsx,.xls">
          <label>Stichtag <input type="date" id="portfolio-upload-stichtag" required></label>
          <button type="submit" class="primary-btn">Hochladen</button>
          <span id="portfolio-upload-status" style="opacity:0.7;font-size:0.9em;"></span>
        </form>
      </div>
      <h4 style="margin:0 0 6px 0;">Snapshots</h4>
      <div id="portfolio-snapshot-list">Lade…</div>
      <div id="portfolio-snapshot-detail" style="margin-top:10px;"></div>
    `;
    $('portfolio-detail-close').addEventListener('click', () => {
      detail.classList.add('hidden');
      currentPortfolio = null;
    });
    $('portfolio-detail-delete').addEventListener('click', deletePortfolio);
    $('portfolio-upload-form').addEventListener('submit', uploadSnapshot);
    await loadSnapshots();
  }

  async function deletePortfolio() {
    if (!currentPortfolio) return;
    if (!confirm(`Portfolio "${currentPortfolio.mandant_name}" wirklich loeschen? Alle Snapshots gehen mit.`)) return;
    try {
      await deleteUrl(`${API}/${currentPortfolio.id}`);
      $('portfolio-detail').classList.add('hidden');
      currentPortfolio = null;
      await loadPortfolios();
    } catch (e) {
      alert(`Fehler: ${e.message}`);
    }
  }

  async function loadSnapshots() {
    if (!currentPortfolio) return;
    const target = $('portfolio-snapshot-list');
    target.innerHTML = 'Lade…';
    try {
      const data = await fetchJson(`${API}/${currentPortfolio.id}/snapshots`);
      const snaps = data.snapshots || [];
      if (!snaps.length) {
        target.innerHTML = '<div style="opacity:0.7;">Noch kein Snapshot — Datei oben hochladen.</div>';
        return;
      }
      target.innerHTML = snaps.map((s) => `
        <div class="portfolio-snap-row" data-snap-id="${escapeHtml(s.id)}" style="display:flex;justify-content:space-between;align-items:center;padding:6px 8px;border-bottom:1px solid var(--border);cursor:pointer;">
          <div>
            <strong>${fmtDate(s.stichtag)}</strong>
            <span style="opacity:0.6;font-size:0.9em;margin-left:8px;">${s.position_count} Positionen · ${fmtMoney(s.total_value, currentPortfolio.base_currency)}</span>
          </div>
          <div style="opacity:0.6;font-size:0.85em;">${escapeHtml(s.source_filename || '')}</div>
        </div>
      `).join('');
      target.querySelectorAll('.portfolio-snap-row').forEach((el) => {
        el.addEventListener('click', () => openSnapshot(el.dataset.snapId));
      });
    } catch (e) {
      target.innerHTML = `<div style="color:var(--accent-error,#c00);">Fehler: ${escapeHtml(e.message)}</div>`;
    }
  }

  async function uploadSnapshot(evt) {
    evt.preventDefault();
    if (!currentPortfolio) return;
    const file = $('portfolio-upload-file').files[0];
    const stichtag = $('portfolio-upload-stichtag').value;
    const status = $('portfolio-upload-status');
    if (!file || !stichtag) {
      status.textContent = 'Datei und Stichtag angeben.';
      return;
    }
    status.textContent = 'Wird hochgeladen…';
    const fd = new FormData();
    fd.append('file', file);
    fd.append('stichtag', stichtag);
    try {
      const res = await fetch(`${API}/${currentPortfolio.id}/snapshots`, {
        method: 'POST',
        credentials: 'same-origin',
        body: fd,
      });
      if (!res.ok) throw new Error(`${res.status}: ${await res.text().catch(() => res.statusText)}`);
      const data = await res.json();
      status.textContent = `OK: ${data.position_count} Positionen importiert.`;
      $('portfolio-upload-file').value = '';
      await loadSnapshots();
      await loadPortfolios();
    } catch (e) {
      status.textContent = `Fehler: ${e.message}`;
    }
  }

  async function openSnapshot(snapId) {
    if (!currentPortfolio) return;
    const target = $('portfolio-snapshot-detail');
    target.innerHTML = 'Lade…';
    try {
      const [detail, summary] = await Promise.all([
        fetchJson(`${API}/${currentPortfolio.id}/snapshots/${snapId}`),
        fetchJson(`${API}/${currentPortfolio.id}/snapshots/${snapId}/summary`),
      ]);
      currentSnapshot = detail.snapshot;
      const cur = currentPortfolio.base_currency || 'EUR';
      const alloc = summary.allocation || [];
      const top = summary.top_positions || [];
      target.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:baseline;margin-top:14px;">
          <h4 style="margin:0;">Snapshot ${fmtDate(detail.snapshot.stichtag)}</h4>
          <button id="portfolio-snap-delete" class="secondary-btn">Snapshot loeschen</button>
        </div>
        <p style="margin:4px 0;opacity:0.8;">Gesamtwert: <strong>${fmtMoney(summary.total_value, cur)}</strong> · ${detail.positions.length} Positionen</p>

        <h5 style="margin:10px 0 4px 0;">Allokation</h5>
        <table style="width:100%;border-collapse:collapse;">
          <thead><tr style="background:#1F3864;color:#fff;"><th style="text-align:left;padding:4px 6px;">Asset-Klasse</th><th style="text-align:right;padding:4px 6px;">Marktwert</th><th style="text-align:right;padding:4px 6px;">Anteil</th></tr></thead>
          <tbody>
            ${alloc.map((a, i) => `
              <tr style="background:${i % 2 ? '#F2F2F2' : '#fff'};color:#000;">
                <td style="padding:4px 6px;">${escapeHtml(a.asset_class)}</td>
                <td style="text-align:right;padding:4px 6px;">${fmtMoney(a.market_value, cur)}</td>
                <td style="text-align:right;padding:4px 6px;">${a.weight_percent != null ? a.weight_percent.toFixed(2) + '%' : '—'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>

        <h5 style="margin:10px 0 4px 0;">Top-Positionen</h5>
        <table style="width:100%;border-collapse:collapse;">
          <thead><tr style="background:#1F3864;color:#fff;"><th style="text-align:left;padding:4px 6px;">Name</th><th style="text-align:left;padding:4px 6px;">ISIN</th><th style="text-align:right;padding:4px 6px;">Marktwert</th><th style="text-align:right;padding:4px 6px;">Anteil</th></tr></thead>
          <tbody>
            ${top.map((p, i) => `
              <tr style="background:${i % 2 ? '#F2F2F2' : '#fff'};color:#000;">
                <td style="padding:4px 6px;">${escapeHtml(p.name)}</td>
                <td style="padding:4px 6px;">${escapeHtml(p.isin || '—')}</td>
                <td style="text-align:right;padding:4px 6px;">${fmtMoney(p.market_value, p.currency || cur)}</td>
                <td style="text-align:right;padding:4px 6px;">${escapeHtml(p.weight_percent || '—')}${p.weight_percent ? ' %' : ''}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>

        <details style="margin-top:10px;">
          <summary style="cursor:pointer;">Alle Positionen (${detail.positions.length})</summary>
          <table style="width:100%;border-collapse:collapse;margin-top:6px;font-size:0.9em;">
            <thead><tr><th style="text-align:left;padding:2px 4px;border-bottom:1px solid var(--border);">Name</th><th style="text-align:left;padding:2px 4px;border-bottom:1px solid var(--border);">ISIN</th><th style="text-align:left;padding:2px 4px;border-bottom:1px solid var(--border);">Klasse</th><th style="text-align:right;padding:2px 4px;border-bottom:1px solid var(--border);">Marktwert</th></tr></thead>
            <tbody>
              ${detail.positions.map((p) => `
                <tr><td style="padding:2px 4px;">${escapeHtml(p.name)}</td><td style="padding:2px 4px;">${escapeHtml(p.isin || '—')}</td><td style="padding:2px 4px;">${escapeHtml(p.asset_class || '—')}</td><td style="text-align:right;padding:2px 4px;">${fmtMoney(p.market_value, p.currency)}</td></tr>
              `).join('')}
            </tbody>
          </table>
        </details>
      `;
      $('portfolio-snap-delete').addEventListener('click', async () => {
        if (!confirm('Snapshot wirklich loeschen?')) return;
        try {
          await deleteUrl(`${API}/${currentPortfolio.id}/snapshots/${snapId}`);
          target.innerHTML = '';
          await loadSnapshots();
          await loadPortfolios();
        } catch (e) {
          alert(`Fehler: ${e.message}`);
        }
      });
    } catch (e) {
      target.innerHTML = `<div style="color:var(--accent-error,#c00);">Fehler: ${escapeHtml(e.message)}</div>`;
    }
  }

  // ----------------------------------------------------------------
  // Create portfolio
  // ----------------------------------------------------------------

  async function createPortfolio(evt) {
    evt.preventDefault();
    const mandant_name = $('portfolio-mandant').value.trim();
    const description = $('portfolio-desc').value.trim();
    const base_currency = ($('portfolio-currency').value || 'EUR').trim().toUpperCase();
    if (!mandant_name) return;
    try {
      await postJson(API, { mandant_name, description, base_currency });
      $('portfolio-mandant').value = '';
      $('portfolio-desc').value = '';
      $('portfolio-new-form').classList.add('hidden');
      await loadPortfolios();
    } catch (e) {
      alert(`Fehler: ${e.message}`);
    }
  }

  // ----------------------------------------------------------------
  // Open / close panel
  // ----------------------------------------------------------------

  async function openPanel() {
    $('portfolio-modal').classList.remove('hidden');
    await loadPortfolios();
  }

  function closePanel() {
    $('portfolio-modal').classList.add('hidden');
  }

  function init() {
    const rail = $('rail-portfolio');
    if (rail) rail.addEventListener('click', openPanel);
    const close = $('close-portfolio-modal');
    if (close) close.addEventListener('click', closePanel);
    const newBtn = $('portfolio-new-btn');
    if (newBtn) newBtn.addEventListener('click', () => $('portfolio-new-form').classList.toggle('hidden'));
    const cancelBtn = $('portfolio-create-cancel');
    if (cancelBtn) cancelBtn.addEventListener('click', () => $('portfolio-new-form').classList.add('hidden'));
    const form = $('portfolio-create-form');
    if (form) form.addEventListener('submit', createPortfolio);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
