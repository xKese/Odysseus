// static/js/knowledge/panel.js
// Hauswissen-Plattform fuer Meeder & Seifer (Phase 1).
// Bewusst frameworkfrei und selbstständig — registriert sich am Rail-Button
// und am Schliessen-Knopf und rendert alle Listen/Forms direkt in das
// bereits in index.html eingehaengte Skelett.

(function () {
  'use strict';

  const API = '/api/knowledge';
  const $ = (id) => document.getElementById(id);

  let isAdmin = false;
  let collections = [];
  let currentCollection = null;
  let aclEditingId = null;

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
      const txt = await res.text().catch(() => res.statusText);
      throw new Error(`${res.status}: ${txt}`);
    }
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

  async function probeAdmin() {
    try {
      // /api/auth/status liefert {is_admin, authenticated, username, privileges, ...}
      const status = await fetchJson('/api/auth/status');
      return !!(status && status.is_admin);
    } catch {
      return false;
    }
  }

  // ----------------------------------------------------------------
  // Rendering
  // ----------------------------------------------------------------

  function escapeHtml(str) {
    return String(str ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  async function loadCollections() {
    const target = $('knowledge-collection-list');
    target.innerHTML = 'Lade Sammlungen…';
    try {
      const data = await fetchJson(`${API}/collections`);
      collections = data.collections || [];
      if (!collections.length) {
        target.innerHTML = '<div style="opacity:0.7;">Noch keine Sammlung freigegeben. ' +
          (isAdmin ? 'Im Admin-Tab eine anlegen.' : 'Bitte beim Administrator anfragen.') + '</div>';
        return;
      }
      target.innerHTML = collections.map((c) => `
        <div class="knowledge-card" data-collection-id="${escapeHtml(c.id)}" style="padding:10px;border:1px solid var(--border);border-radius:8px;margin-bottom:8px;cursor:pointer;">
          <div style="display:flex;justify-content:space-between;align-items:baseline;">
            <strong>${escapeHtml(c.name)}</strong>
            <span style="opacity:0.6;font-size:0.85em;">${c.doc_count || 0} Dokument${(c.doc_count || 0) === 1 ? '' : 'e'}</span>
          </div>
          <div style="opacity:0.75;font-size:0.9em;margin-top:4px;">${escapeHtml(c.description)}</div>
          <div style="opacity:0.5;font-size:0.8em;margin-top:2px;">slug: <code>${escapeHtml(c.slug)}</code></div>
        </div>
      `).join('');
      target.querySelectorAll('.knowledge-card').forEach((el) => {
        el.addEventListener('click', () => openCollection(el.dataset.collectionId));
      });
    } catch (e) {
      target.innerHTML = `<div style="color:var(--accent-error,#c00);">Fehler: ${escapeHtml(e.message)}</div>`;
    }
  }

  async function openCollection(id) {
    const c = collections.find((x) => x.id === id);
    if (!c) return;
    currentCollection = c;
    const detail = $('knowledge-collection-detail');
    detail.classList.remove('hidden');
    detail.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:10px;">
        <h3 style="margin:0;">${escapeHtml(c.name)}</h3>
        <button id="knowledge-detail-close" class="secondary-btn">Schliessen</button>
      </div>
      <div style="display:flex;gap:6px;margin-bottom:10px;">
        <input id="knowledge-search-input" type="text" placeholder="Suchen in ${escapeHtml(c.name)}…" style="flex:1;padding:6px;background:var(--input-bg,var(--panel));color:var(--fg);border:1px solid var(--border);border-radius:6px;">
        <button id="knowledge-search-btn" class="primary-btn">Suchen</button>
      </div>
      <div id="knowledge-search-results" style="margin-bottom:14px;"></div>
      <hr style="border:none;border-top:1px solid var(--border);margin:14px 0;">
      <h4 style="margin:0 0 8px 0;">Dokumente</h4>
      <div id="knowledge-doc-upload" style="margin-bottom:8px;"></div>
      <div id="knowledge-doc-list">Lade…</div>
    `;
    $('knowledge-detail-close').addEventListener('click', () => {
      detail.classList.add('hidden');
      currentCollection = null;
    });
    $('knowledge-search-btn').addEventListener('click', runSearch);
    $('knowledge-search-input').addEventListener('keydown', (e) => {
      if (e.key === 'Enter') runSearch();
    });
    renderUploadControl();
    await loadDocuments();
  }

  function renderUploadControl() {
    const target = $('knowledge-doc-upload');
    target.innerHTML = `
      <input type="file" id="knowledge-doc-file" accept=".pdf,.txt,.md,.csv,.json,.yaml,.html,.htm">
      <button id="knowledge-doc-upload-btn" class="primary-btn">Hochladen</button>
      <span id="knowledge-upload-status" style="margin-left:8px;opacity:0.7;font-size:0.9em;"></span>
    `;
    $('knowledge-doc-upload-btn').addEventListener('click', uploadDocument);
  }

  async function loadDocuments() {
    if (!currentCollection) return;
    const target = $('knowledge-doc-list');
    target.innerHTML = 'Lade…';
    try {
      const data = await fetchJson(`${API}/collections/${currentCollection.id}/documents`);
      const docs = data.documents || [];
      if (!docs.length) {
        target.innerHTML = '<div style="opacity:0.7;">Noch keine Dokumente in dieser Sammlung.</div>';
        return;
      }
      target.innerHTML = docs.map((d) => `
        <div class="knowledge-doc-row" style="display:flex;justify-content:space-between;align-items:center;padding:6px;border-bottom:1px solid var(--border);">
          <div>
            <div><strong>${escapeHtml(d.filename)}</strong></div>
            <div style="opacity:0.6;font-size:0.85em;">
              ${(d.size / 1024).toFixed(1)} KB · ${d.chunk_count} Chunk${d.chunk_count === 1 ? '' : 's'} · ${escapeHtml(d.uploaded_by || 'unbekannt')}
            </div>
          </div>
          <button data-doc-id="${escapeHtml(d.id)}" class="knowledge-doc-delete secondary-btn">Loeschen</button>
        </div>
      `).join('');
      target.querySelectorAll('.knowledge-doc-delete').forEach((b) => {
        b.addEventListener('click', () => deleteDocument(b.dataset.docId));
      });
    } catch (e) {
      target.innerHTML = `<div style="color:var(--accent-error,#c00);">Fehler: ${escapeHtml(e.message)}</div>`;
    }
  }

  async function uploadDocument() {
    if (!currentCollection) return;
    const fileInput = $('knowledge-doc-file');
    const status = $('knowledge-upload-status');
    const f = fileInput.files && fileInput.files[0];
    if (!f) {
      status.textContent = 'Bitte zuerst eine Datei auswaehlen.';
      return;
    }
    status.textContent = 'Wird hochgeladen…';
    const fd = new FormData();
    fd.append('file', f);
    try {
      const res = await fetch(`${API}/collections/${currentCollection.id}/documents`, {
        method: 'POST',
        credentials: 'same-origin',
        body: fd,
      });
      if (!res.ok) throw new Error(`${res.status}: ${await res.text().catch(() => res.statusText)}`);
      const data = await res.json();
      status.textContent = `OK: ${data.filename} (${data.chunk_count} Chunks)`;
      fileInput.value = '';
      await loadDocuments();
      await loadCollections();
    } catch (e) {
      status.textContent = `Fehler: ${e.message}`;
    }
  }

  async function deleteDocument(docId) {
    if (!currentCollection) return;
    if (!confirm('Dokument wirklich loeschen? Die Vektor-Eintraege werden ebenfalls entfernt.')) return;
    try {
      await deleteUrl(`${API}/collections/${currentCollection.id}/documents/${docId}`);
      await loadDocuments();
      await loadCollections();
    } catch (e) {
      alert(`Fehler: ${e.message}`);
    }
  }

  async function runSearch() {
    if (!currentCollection) return;
    const q = $('knowledge-search-input').value.trim();
    const target = $('knowledge-search-results');
    if (!q) {
      target.innerHTML = '';
      return;
    }
    target.innerHTML = 'Suche…';
    try {
      const data = await postJson(`${API}/collections/${currentCollection.id}/search`, { query: q, k: 5 });
      const results = data.results || [];
      if (!results.length) {
        target.innerHTML = '<div style="opacity:0.7;">Keine Treffer in dieser Sammlung.</div>';
        return;
      }
      target.innerHTML = results.map((r, i) => `
        <div style="padding:8px;border:1px solid var(--border);border-radius:6px;margin-bottom:6px;">
          <div style="opacity:0.6;font-size:0.85em;">
            #${i + 1} · Score ${(r.similarity || 0).toFixed(3)} · ${escapeHtml((r.metadata && r.metadata.filename) || 'unbekannt')}
          </div>
          <div style="margin-top:4px;white-space:pre-wrap;">${escapeHtml(r.document || '').slice(0, 600)}${(r.document || '').length > 600 ? '…' : ''}</div>
        </div>
      `).join('');
    } catch (e) {
      target.innerHTML = `<div style="color:var(--accent-error,#c00);">Fehler: ${escapeHtml(e.message)}</div>`;
    }
  }

  // ----------------------------------------------------------------
  // Admin tab
  // ----------------------------------------------------------------

  async function createCollection(evt) {
    evt.preventDefault();
    const name = $('knowledge-new-name').value.trim();
    const slug = $('knowledge-new-slug').value.trim();
    const description = $('knowledge-new-description').value.trim();
    if (!name) return;
    try {
      const created = await postJson(`${API}/collections`, { name, slug, description });
      $('knowledge-new-name').value = '';
      $('knowledge-new-slug').value = '';
      $('knowledge-new-description').value = '';
      await loadCollections();
      openAclEditor(created.id, created.name);
    } catch (e) {
      alert(`Fehler beim Anlegen: ${e.message}`);
    }
  }

  async function openAclEditor(collectionId, name) {
    aclEditingId = collectionId;
    $('knowledge-acl-editor').style.display = 'block';
    $('knowledge-acl-name').textContent = '— ' + name;
    await renderAclGrants();
  }

  async function renderAclGrants() {
    if (!aclEditingId) return;
    const target = $('knowledge-acl-grants');
    target.innerHTML = 'Lade…';
    try {
      const data = await fetchJson(`${API}/collections/${aclEditingId}/acl`);
      const grants = data.grants || [];
      if (!grants.length) {
        target.innerHTML = '<div style="opacity:0.7;">Noch keine Rolle freigegeben.</div>';
        return;
      }
      target.innerHTML = grants.map((g, idx) => `
        <div style="display:flex;justify-content:space-between;align-items:center;padding:4px 0;">
          <span><strong>${escapeHtml(g.role)}</strong> · ${escapeHtml(g.permission)}</span>
          <button data-grant-idx="${idx}" class="knowledge-acl-remove secondary-btn">Entfernen</button>
        </div>
      `).join('');
      target.querySelectorAll('.knowledge-acl-remove').forEach((b) => {
        b.addEventListener('click', async () => {
          const idx = Number(b.dataset.grantIdx);
          const next = grants.filter((_, i) => i !== idx);
          await putJson(`${API}/collections/${aclEditingId}/acl`, { grants: next });
          await renderAclGrants();
        });
      });
    } catch (e) {
      target.innerHTML = `<div style="color:var(--accent-error,#c00);">Fehler: ${escapeHtml(e.message)}</div>`;
    }
  }

  async function addAclGrant() {
    if (!aclEditingId) return;
    const role = $('knowledge-acl-role').value;
    const permission = $('knowledge-acl-permission').value;
    try {
      const data = await fetchJson(`${API}/collections/${aclEditingId}/acl`);
      const grants = (data.grants || []).filter((g) => g.role !== role);
      grants.push({ role, permission });
      await putJson(`${API}/collections/${aclEditingId}/acl`, { grants });
      await renderAclGrants();
    } catch (e) {
      alert(`Fehler: ${e.message}`);
    }
  }

  // ----------------------------------------------------------------
  // Open / close
  // ----------------------------------------------------------------

  async function openPanel() {
    isAdmin = await probeAdmin();
    $('knowledge-admin-tab').style.display = isAdmin ? '' : 'none';
    $('knowledge-modal').classList.remove('hidden');
    await loadCollections();
  }

  function closePanel() {
    $('knowledge-modal').classList.add('hidden');
  }

  function switchTab(name) {
    document.querySelectorAll('#knowledge-tabs .admin-tab').forEach((t) => {
      t.classList.toggle('active', t.dataset.knowledgeTab === name);
    });
    $('knowledge-tab-browse').classList.toggle('hidden', name !== 'browse');
    $('knowledge-tab-admin').classList.toggle('hidden', name !== 'admin');
  }

  // ----------------------------------------------------------------
  // Wire up
  // ----------------------------------------------------------------

  function init() {
    const rail = $('rail-knowledge');
    if (rail) rail.addEventListener('click', openPanel);
    const close = $('close-knowledge-modal');
    if (close) close.addEventListener('click', closePanel);

    document.querySelectorAll('#knowledge-tabs .admin-tab').forEach((t) => {
      t.addEventListener('click', () => switchTab(t.dataset.knowledgeTab));
    });

    const form = $('knowledge-new-collection-form');
    if (form) form.addEventListener('submit', createCollection);

    const aclAdd = $('knowledge-acl-add');
    if (aclAdd) aclAdd.addEventListener('click', addAclGrant);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
