// static/js/onboarding/panel.js
// Onboarding-Panel fuer Meeder & Seifer (Phase 4).

(function () {
  'use strict';

  const API = '/api/onboarding';
  const $ = (id) => document.getElementById(id);
  let onboardings = [];
  let currentId = null;

  const STATUS_META = {
    started:       { lbl: 'Gestartet',        col: '#1F3864' },
    docs_pending:  { lbl: 'Unterlagen offen', col: '#C09000' },
    review:        { lbl: 'Pruefung',         col: '#5B9BD5' },
    completed:     { lbl: 'Abgeschlossen',    col: '#2E7D32' },
    abandoned:     { lbl: 'Verworfen',        col: '#999' },
  };

  const TYPE_LABEL = {
    vermoegensverwaltung: 'Vermoegensverwaltung',
    family_office: 'Family Office',
    beratung: 'Beratung',
  };

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

  async function putJson(url, body) {
    return fetchJson(url, { method: 'PUT', body: JSON.stringify(body || {}) });
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

  function fmtDate(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    if (isNaN(d.getTime())) return iso;
    return d.toLocaleDateString('de-DE');
  }

  function statusBadge(s) {
    const m = STATUS_META[s] || { lbl: s || '—', col: '#666' };
    return `<span style="background:${m.col};color:#fff;padding:2px 8px;border-radius:10px;font-size:0.8em;">${escapeHtml(m.lbl)}</span>`;
  }

  function checklistProgress(checklist) {
    if (!Array.isArray(checklist) || !checklist.length) return { done: 0, total: 0, pct: 0 };
    const done = checklist.filter((c) => c.status === 'done').length;
    return { done, total: checklist.length, pct: Math.round((done / checklist.length) * 100) };
  }

  async function loadList() {
    const target = $('onboarding-list');
    target.innerHTML = 'Lade…';
    try {
      const data = await fetchJson(API);
      onboardings = data.onboardings || [];
      if (!onboardings.length) {
        target.innerHTML = '<div style="opacity:0.7;">Noch kein Onboarding — oben rechts auf "+ Neumandat" klicken.</div>';
        return;
      }
      target.innerHTML = onboardings.map((o) => {
        const prog = checklistProgress(o.checklist);
        return `
          <div class="onboarding-card" data-id="${escapeHtml(o.id)}" style="padding:10px;border:1px solid var(--border);border-radius:8px;margin-bottom:8px;cursor:pointer;">
            <div style="display:flex;justify-content:space-between;align-items:baseline;gap:8px;flex-wrap:wrap;">
              <strong>${escapeHtml(o.mandant_name)}</strong>
              ${statusBadge(o.status)}
            </div>
            <div style="opacity:0.7;font-size:0.9em;margin-top:4px;">${escapeHtml(TYPE_LABEL[o.onboarding_type] || o.onboarding_type)} · Start ${fmtDate(o.started_at)}${o.target_completion_date ? ' · Ziel ' + fmtDate(o.target_completion_date) : ''}</div>
            <div style="opacity:0.55;font-size:0.85em;margin-top:2px;">Checkliste: ${prog.done}/${prog.total} (${prog.pct}%)</div>
          </div>
        `;
      }).join('');
      target.querySelectorAll('.onboarding-card').forEach((el) => {
        el.addEventListener('click', () => openDetail(el.dataset.id));
      });
    } catch (e) {
      target.innerHTML = `<div style="color:var(--accent-error,#c00);">Fehler: ${escapeHtml(e.message)}</div>`;
    }
  }

  async function openDetail(id) {
    currentId = id;
    const target = $('onboarding-detail');
    target.classList.remove('hidden');
    target.innerHTML = 'Lade…';
    try {
      const o = await fetchJson(`${API}/${encodeURIComponent(id)}`);
      const prog = checklistProgress(o.checklist);
      const welcome = o.welcome_document ? `
        <div style="margin-top:8px;padding:6px 8px;border:1px dashed var(--border);border-radius:6px;font-size:0.9em;">
          Willkommensschreiben: <strong>${escapeHtml(o.welcome_document.title)}</strong>
          <span style="margin-left:6px;font-size:0.85em;opacity:0.6;">(${escapeHtml(o.welcome_document.release_status)})</span>
        </div>` : '';
      target.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:10px;gap:8px;flex-wrap:wrap;">
          <h3 style="margin:0;">${escapeHtml(o.mandant_name)} <span style="font-weight:normal;opacity:0.7;font-size:0.85em;">· ${escapeHtml(TYPE_LABEL[o.onboarding_type] || o.onboarding_type)}</span></h3>
          <div style="display:flex;gap:6px;align-items:center;">
            <select id="onboarding-status-select" style="padding:6px;background:var(--input-bg,var(--panel));color:var(--fg);border:1px solid var(--border);border-radius:6px;">
              ${Object.entries(STATUS_META).map(([k, m]) => `<option value="${k}" ${o.status === k ? 'selected' : ''}>${m.lbl}</option>`).join('')}
            </select>
            <button id="onboarding-delete-btn" class="secondary-btn">Loeschen</button>
            <button id="onboarding-close-btn" class="secondary-btn">Schliessen</button>
          </div>
        </div>
        <div style="font-size:0.9em;opacity:0.85;">
          Start: ${fmtDate(o.started_at)}
          ${o.target_completion_date ? ' · Ziel: ' + fmtDate(o.target_completion_date) : ''}
          ${o.completed_at ? ' · Abgeschlossen: ' + fmtDate(o.completed_at) : ''}
        </div>
        ${welcome}
        <h4 style="margin:14px 0 6px 0;">Checkliste (${prog.done}/${prog.total} erledigt)</h4>
        <div id="onboarding-checklist"></div>
        <h4 style="margin:14px 0 6px 0;">Notizen</h4>
        <textarea id="onboarding-notes-edit" rows="3" style="width:100%;padding:6px;background:var(--input-bg,var(--panel));color:var(--fg);border:1px solid var(--border);border-radius:6px;">${escapeHtml(o.notes || '')}</textarea>
        <button id="onboarding-notes-save" class="primary-btn" style="margin-top:6px;">Notizen speichern</button>
      `;
      renderChecklist(o.checklist || []);
      $('onboarding-close-btn').addEventListener('click', () => { target.classList.add('hidden'); currentId = null; });
      $('onboarding-delete-btn').addEventListener('click', deleteOnboarding);
      $('onboarding-status-select').addEventListener('change', (e) => changeStatus(e.target.value));
      $('onboarding-notes-save').addEventListener('click', saveNotes);
    } catch (e) {
      target.innerHTML = `<div style="color:var(--accent-error,#c00);">Fehler: ${escapeHtml(e.message)}</div>`;
    }
  }

  function renderChecklist(list) {
    const wrap = $('onboarding-checklist');
    if (!list.length) {
      wrap.innerHTML = '<div style="opacity:0.7;">Keine Schritte in der Checkliste.</div>';
      return;
    }
    wrap.innerHTML = list.map((c, idx) => `
      <div style="display:flex;justify-content:space-between;align-items:center;padding:6px;border-bottom:1px solid var(--border);gap:8px;">
        <div style="flex:1;">
          <strong style="${c.status === 'done' ? 'text-decoration:line-through;opacity:0.6;' : ''}">${escapeHtml(c.step)}</strong>
          ${c.evidence_document_id ? `<div style="opacity:0.55;font-size:0.8em;">Beleg: ${escapeHtml(c.evidence_document_id.slice(0, 8))}…</div>` : ''}
        </div>
        <select data-step-index="${idx}" class="onboarding-checklist-status" style="padding:4px;background:var(--input-bg,var(--panel));color:var(--fg);border:1px solid var(--border);border-radius:6px;font-size:0.85em;">
          <option value="pending" ${c.status === 'pending' ? 'selected' : ''}>offen</option>
          <option value="done" ${c.status === 'done' ? 'selected' : ''}>erledigt</option>
          <option value="skipped" ${c.status === 'skipped' ? 'selected' : ''}>uebersprungen</option>
        </select>
      </div>
    `).join('');
    wrap.querySelectorAll('.onboarding-checklist-status').forEach((sel) => {
      sel.addEventListener('change', () => updateChecklistStep(Number(sel.dataset.stepIndex), sel.value));
    });
  }

  async function updateChecklistStep(idx, status) {
    try {
      const data = await postJson(`${API}/${encodeURIComponent(currentId)}/checklist`, {
        step_index: idx,
        status,
      });
      renderChecklist(data.checklist || []);
      await loadList();
    } catch (e) {
      alert(`Fehler: ${e.message}`);
    }
  }

  async function changeStatus(newStatus) {
    try {
      await putJson(`${API}/${encodeURIComponent(currentId)}`, { status: newStatus });
      await openDetail(currentId);
      await loadList();
    } catch (e) {
      alert(`Fehler: ${e.message}`);
    }
  }

  async function saveNotes() {
    try {
      await putJson(`${API}/${encodeURIComponent(currentId)}`, {
        notes: $('onboarding-notes-edit').value,
      });
    } catch (e) {
      alert(`Fehler: ${e.message}`);
    }
  }

  async function deleteOnboarding() {
    if (!confirm('Onboarding-Prozess wirklich loeschen? Verknuepfte Documents bleiben bestehen.')) return;
    try {
      await deleteUrl(`${API}/${encodeURIComponent(currentId)}`);
      $('onboarding-detail').classList.add('hidden');
      currentId = null;
      await loadList();
    } catch (e) {
      alert(`Fehler: ${e.message}`);
    }
  }

  async function createOnboarding(evt) {
    evt.preventDefault();
    const mandant_name = $('onboarding-mandant').value.trim();
    const onboarding_type = $('onboarding-type').value;
    const target_completion_date = $('onboarding-target').value || null;
    const notes = $('onboarding-notes').value.trim();
    if (!mandant_name) return;
    try {
      await postJson(API, {
        mandant_name,
        onboarding_type,
        target_completion_date,
        notes,
      });
      $('onboarding-mandant').value = '';
      $('onboarding-target').value = '';
      $('onboarding-notes').value = '';
      $('onboarding-new-form').classList.add('hidden');
      await loadList();
    } catch (e) {
      alert(`Fehler: ${e.message}`);
    }
  }

  async function openPanel() {
    $('onboarding-modal').classList.remove('hidden');
    await loadList();
  }

  function closePanel() {
    $('onboarding-modal').classList.add('hidden');
  }

  function init() {
    const rail = $('rail-onboarding');
    if (rail) rail.addEventListener('click', openPanel);
    const close = $('close-onboarding-modal');
    if (close) close.addEventListener('click', closePanel);
    const newBtn = $('onboarding-new-btn');
    if (newBtn) newBtn.addEventListener('click', () => $('onboarding-new-form').classList.toggle('hidden'));
    const cancelBtn = $('onboarding-create-cancel');
    if (cancelBtn) cancelBtn.addEventListener('click', () => $('onboarding-new-form').classList.add('hidden'));
    const form = $('onboarding-create-form');
    if (form) form.addEventListener('submit', createOnboarding);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
