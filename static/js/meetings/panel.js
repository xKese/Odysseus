// static/js/meetings/panel.js
// Anlageausschuss-Sitzungspanel fuer Meeder & Seifer (Phase 2).

(function () {
  'use strict';

  const API = '/api/meetings';
  const $ = (id) => document.getElementById(id);
  let meetings = [];
  let currentMeeting = null;
  // Phase 4: Filter-Tab fuer meeting_type. 'all' zeigt alle Typen.
  let currentTypeFilter = 'all';

  const TYPE_LABELS = {
    anlageausschuss: 'Anlageausschuss',
    mandant: 'Mandantentermin',
    extern: 'Extern',
  };

  function typeBadge(type) {
    const colors = { anlageausschuss: '#1F3864', mandant: '#2E7D32', extern: '#666' };
    const lbl = TYPE_LABELS[type] || type || '—';
    const col = colors[type] || '#999';
    return `<span style="background:${col};color:#fff;padding:2px 8px;border-radius:10px;font-size:0.75em;">${escapeHtml(lbl)}</span>`;
  }

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

  function fmtDateTime(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    if (isNaN(d.getTime())) return iso;
    return d.toLocaleString('de-DE', { dateStyle: 'short', timeStyle: 'short' });
  }

  function statusBadge(status) {
    const map = {
      planned: { lbl: 'Geplant', col: '#1F3864' },
      held: { lbl: 'Stattgefunden', col: '#5B9BD5' },
      protocol: { lbl: 'Protokoll', col: '#C09000' },
      approved: { lbl: 'Freigegeben', col: '#2E7D32' },
    };
    const m = map[status] || { lbl: status || '—', col: '#666' };
    return `<span style="background:${m.col};color:#fff;padding:2px 8px;border-radius:10px;font-size:0.8em;">${escapeHtml(m.lbl)}</span>`;
  }

  function renderTypeFilters() {
    const wrap = $('meetings-type-filter');
    if (!wrap) return;
    const opts = [
      { id: 'all', lbl: 'Alle' },
      { id: 'anlageausschuss', lbl: 'Anlageausschuss' },
      { id: 'mandant', lbl: 'Mandantentermin' },
      { id: 'extern', lbl: 'Extern' },
    ];
    wrap.innerHTML = opts.map((o) => `
      <button data-type="${o.id}" class="meetings-type-chip" style="padding:4px 10px;border:1px solid var(--border);border-radius:14px;background:${currentTypeFilter === o.id ? 'var(--accent-primary,#1F3864)' : 'var(--panel)'};color:${currentTypeFilter === o.id ? '#fff' : 'var(--fg)'};cursor:pointer;font-size:0.85em;">${escapeHtml(o.lbl)}</button>
    `).join('');
    wrap.querySelectorAll('.meetings-type-chip').forEach((b) => {
      b.addEventListener('click', () => {
        currentTypeFilter = b.dataset.type;
        renderTypeFilters();
        loadMeetings();
      });
    });
  }

  async function loadMeetings() {
    renderTypeFilters();
    const target = $('meetings-list');
    target.innerHTML = 'Lade…';
    try {
      const url = currentTypeFilter && currentTypeFilter !== 'all'
        ? `${API}?type=${encodeURIComponent(currentTypeFilter)}`
        : API;
      const data = await fetchJson(url);
      meetings = data.meetings || [];
      if (!meetings.length) {
        target.innerHTML = '<div style="opacity:0.7;">Noch keine Sitzungen in dieser Auswahl — oben rechts auf "+ Neue Sitzung" klicken.</div>';
        return;
      }
      target.innerHTML = meetings.map((m) => {
        const mandantLine = m.meeting_type === 'mandant' && m.mandant_name
          ? `<div style="opacity:0.7;font-size:0.85em;margin-top:2px;">Mandant: ${escapeHtml(m.mandant_name)}</div>`
          : '';
        return `
          <div class="meeting-card" data-meeting-id="${escapeHtml(m.id)}" style="padding:10px;border:1px solid var(--border);border-radius:8px;margin-bottom:8px;cursor:pointer;">
            <div style="display:flex;justify-content:space-between;align-items:baseline;gap:8px;flex-wrap:wrap;">
              <strong>${escapeHtml(m.title)}</strong>
              <div style="display:flex;gap:4px;">${typeBadge(m.meeting_type)} ${statusBadge(m.status)}</div>
            </div>
            <div style="opacity:0.7;font-size:0.9em;margin-top:4px;">${fmtDateTime(m.meeting_date)} · ${escapeHtml(m.location || '')}</div>
            ${mandantLine}
            <div style="opacity:0.55;font-size:0.85em;margin-top:2px;">${(m.attendees || []).length} Teilnehmer</div>
          </div>
        `;
      }).join('');
      target.querySelectorAll('.meeting-card').forEach((el) => {
        el.addEventListener('click', () => openMeeting(el.dataset.meetingId));
      });
    } catch (e) {
      target.innerHTML = `<div style="color:var(--accent-error,#c00);">Fehler: ${escapeHtml(e.message)}</div>`;
    }
  }

  async function openMeeting(id) {
    const target = $('meetings-detail');
    target.classList.remove('hidden');
    target.innerHTML = 'Lade…';
    try {
      const m = await fetchJson(`${API}/${id}`);
      currentMeeting = m;
      const attached = m.attached_documents || [];
      target.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:10px;">
          <h3 style="margin:0;">${escapeHtml(m.title)}</h3>
          <div>
            <select id="meeting-status-select" style="padding:6px;background:var(--input-bg,var(--panel));color:var(--fg);border:1px solid var(--border);border-radius:6px;">
              <option value="planned" ${m.status === 'planned' ? 'selected' : ''}>Geplant</option>
              <option value="held" ${m.status === 'held' ? 'selected' : ''}>Stattgefunden</option>
              <option value="protocol" ${m.status === 'protocol' ? 'selected' : ''}>Protokoll</option>
              <option value="approved" ${m.status === 'approved' ? 'selected' : ''}>Freigegeben</option>
            </select>
            <button id="meeting-delete-btn" class="secondary-btn">Loeschen</button>
            <button id="meeting-close-btn" class="secondary-btn">Schliessen</button>
          </div>
        </div>
        <p style="margin:4px 0;opacity:0.85;">${fmtDateTime(m.meeting_date)} · ${escapeHtml(m.location || '')}</p>
        <p style="margin:4px 0;opacity:0.7;font-size:0.9em;">Teilnehmer: ${(m.attendees || []).map(escapeHtml).join(', ') || '—'}</p>

        <h4 style="margin:14px 0 6px 0;">Verknuepfte Dokumente</h4>
        <div id="meeting-attached">
          ${!attached.length ? '<div style="opacity:0.7;">Noch keine Dokumente verknuepft.</div>' : attached.map((d) => `
            <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 8px;border-bottom:1px solid var(--border);">
              <div>
                <strong>${escapeHtml(d.title)}</strong>
                <span style="margin-left:8px;font-size:0.85em;opacity:0.7;">${escapeHtml(d.release_status || 'draft')}</span>
              </div>
              <button data-doc-id="${escapeHtml(d.id)}" class="meeting-detach-btn secondary-btn">Entfernen</button>
            </div>
          `).join('')}
        </div>

        <div style="margin-top:10px;padding:8px;border:1px dashed var(--border);border-radius:6px;">
          <strong>Document anhaengen</strong>
          <div style="display:flex;gap:6px;margin-top:6px;">
            <input id="meeting-doc-id-input" placeholder="Document-ID" style="flex:1;padding:6px;background:var(--input-bg,var(--panel));color:var(--fg);border:1px solid var(--border);border-radius:6px;">
            <select id="meeting-doc-role" style="padding:6px;background:var(--input-bg,var(--panel));color:var(--fg);border:1px solid var(--border);border-radius:6px;">
              <option value="decision">Beschluss/Bericht</option>
              <option value="protocol">Protokoll</option>
            </select>
            <button id="meeting-attach-btn" class="primary-btn">Anhaengen</button>
          </div>
        </div>
      `;
      $('meeting-close-btn').addEventListener('click', () => { target.classList.add('hidden'); currentMeeting = null; });
      $('meeting-delete-btn').addEventListener('click', deleteMeeting);
      $('meeting-status-select').addEventListener('change', changeStatus);
      $('meeting-attach-btn').addEventListener('click', attachDoc);
      target.querySelectorAll('.meeting-detach-btn').forEach((b) => {
        b.addEventListener('click', () => detachDoc(b.dataset.docId));
      });
    } catch (e) {
      target.innerHTML = `<div style="color:var(--accent-error,#c00);">Fehler: ${escapeHtml(e.message)}</div>`;
    }
  }

  async function deleteMeeting() {
    if (!currentMeeting) return;
    if (!confirm('Sitzung wirklich loeschen? Verknuepfte Dokumente bleiben bestehen.')) return;
    try {
      await deleteUrl(`${API}/${currentMeeting.id}`);
      $('meetings-detail').classList.add('hidden');
      currentMeeting = null;
      await loadMeetings();
    } catch (e) {
      alert(`Fehler: ${e.message}`);
    }
  }

  async function changeStatus(evt) {
    if (!currentMeeting) return;
    const status = evt.target.value;
    try {
      await putJson(`${API}/${currentMeeting.id}`, { status });
      await openMeeting(currentMeeting.id);
      await loadMeetings();
    } catch (e) {
      alert(`Fehler: ${e.message}`);
    }
  }

  async function attachDoc() {
    if (!currentMeeting) return;
    const docId = $('meeting-doc-id-input').value.trim();
    const role = $('meeting-doc-role').value;
    if (!docId) return;
    try {
      await postJson(`${API}/${currentMeeting.id}/documents`, { document_id: docId, role });
      $('meeting-doc-id-input').value = '';
      await openMeeting(currentMeeting.id);
    } catch (e) {
      alert(`Fehler: ${e.message}`);
    }
  }

  async function detachDoc(docId) {
    if (!currentMeeting) return;
    if (!confirm('Document von Sitzung entfernen? Das Document selbst bleibt bestehen.')) return;
    try {
      await deleteUrl(`${API}/${currentMeeting.id}/documents/${docId}`);
      await openMeeting(currentMeeting.id);
    } catch (e) {
      alert(`Fehler: ${e.message}`);
    }
  }

  async function createMeeting(evt) {
    evt.preventDefault();
    const title = $('meetings-title').value.trim();
    const dateRaw = $('meetings-date').value;
    const location = $('meetings-location').value.trim();
    const attendees = $('meetings-attendees').value
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);
    const meeting_type = ($('meetings-type') && $('meetings-type').value) || 'anlageausschuss';
    const mandant_name = ($('meetings-mandant') && $('meetings-mandant').value || '').trim();
    if (!title || !dateRaw) return;
    if (meeting_type === 'mandant' && !mandant_name) {
      alert('Bei Mandantentermin ist der Mandantenname Pflicht.');
      return;
    }
    try {
      await postJson(API, {
        title,
        meeting_date: dateRaw + (dateRaw.length === 16 ? ':00' : ''),
        location,
        attendees,
        meeting_type,
        mandant_name: mandant_name || null,
      });
      $('meetings-title').value = '';
      $('meetings-date').value = '';
      $('meetings-location').value = '';
      $('meetings-attendees').value = '';
      if ($('meetings-mandant')) $('meetings-mandant').value = '';
      if ($('meetings-type')) $('meetings-type').value = 'anlageausschuss';
      toggleMandantField();
      $('meetings-new-form').classList.add('hidden');
      await loadMeetings();
    } catch (e) {
      alert(`Fehler: ${e.message}`);
    }
  }

  function toggleMandantField() {
    const select = $('meetings-type');
    const wrap = $('meetings-mandant-wrap');
    if (!select || !wrap) return;
    wrap.style.display = select.value === 'mandant' ? '' : 'none';
  }

  async function openPanel() {
    $('meetings-modal').classList.remove('hidden');
    await loadMeetings();
  }

  function closePanel() {
    $('meetings-modal').classList.add('hidden');
  }

  function init() {
    const rail = $('rail-meetings');
    if (rail) rail.addEventListener('click', openPanel);
    const close = $('close-meetings-modal');
    if (close) close.addEventListener('click', closePanel);
    const newBtn = $('meetings-new-btn');
    if (newBtn) newBtn.addEventListener('click', () => $('meetings-new-form').classList.toggle('hidden'));
    const cancelBtn = $('meetings-create-cancel');
    if (cancelBtn) cancelBtn.addEventListener('click', () => $('meetings-new-form').classList.add('hidden'));
    const form = $('meetings-create-form');
    if (form) form.addEventListener('submit', createMeeting);
    const typeSel = $('meetings-type');
    if (typeSel) typeSel.addEventListener('change', toggleMandantField);
    toggleMandantField();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
