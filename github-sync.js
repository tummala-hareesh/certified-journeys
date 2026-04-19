'use strict';
const GHSync = (() => {
  const CREDS_KEY       = 'cj_github_creds';
  const LAST_SYNCED_KEY = 'cj_last_synced';

  let creds       = null;
  let fileSHA     = null;
  let allProgress = {};   // in-memory cache of every course's state
  let saveTimer   = null;

  // ── init ─────────────────────────────────────────────────────────────────

  function loadCreds() {
    try { const s = localStorage.getItem(CREDS_KEY); if (s) creds = JSON.parse(s); } catch(e) {}
  }

  // Seed allProgress from every cj_*_v1 key already in localStorage so a
  // push from one course never overwrites another course's locally-saved data.
  function seedFromLocalStorage() {
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (!key || !/^cj_.+_v1$/.test(key)) continue;
      try {
        const id = key.slice(3, -3); // strip "cj_" prefix and "_v1" suffix
        const s  = localStorage.getItem(key);
        if (s) allProgress[id] = JSON.parse(s);
      } catch(e) {}
    }
  }

  // ── credentials ───────────────────────────────────────────────────────────

  function saveCreds(c) {
    creds = c;
    try {
      if (c) localStorage.setItem(CREDS_KEY, JSON.stringify(c));
      else   localStorage.removeItem(CREDS_KEY);
    } catch(e) {}
  }

  function getCreds()     { return creds; }
  function isConnected()  { return !!(creds && creds.pat && creds.owner && creds.repo); }

  // ── GitHub API helpers ────────────────────────────────────────────────────

  function hdrs() {
    return {
      'Authorization':       `Bearer ${creds.pat}`,
      'Accept':              'application/vnd.github+json',
      'X-GitHub-Api-Version':'2022-11-28',
      'Content-Type':        'application/json',
    };
  }

  function apiUrl() {
    return `https://api.github.com/repos/${creds.owner}/${creds.repo}/contents/progress.json`;
  }

  // ── last-synced timestamp ─────────────────────────────────────────────────

  function getLastSynced() { return localStorage.getItem(LAST_SYNCED_KEY); }

  function markSynced() {
    const ts = new Date().toISOString();
    localStorage.setItem(LAST_SYNCED_KEY, ts);
    try { window.dispatchEvent(new CustomEvent('cj-synced', { detail: ts })); } catch(e) {}
  }

  // ── GitHub read/write ─────────────────────────────────────────────────────

  async function fetchAll() {
    if (!isConnected()) return null;
    try {
      const branch = creds.branch || 'main';
      const res    = await fetch(`${apiUrl()}?ref=${branch}`, { headers: hdrs() });
      if (res.status === 404) { fileSHA = null; return {}; }
      if (!res.ok) return null;
      const data = await res.json();
      fileSHA    = data.sha;
      const raw  = data.content.replace(/\n/g, '');
      return JSON.parse(new TextDecoder().decode(
        Uint8Array.from(atob(raw), c => c.charCodeAt(0))
      ));
    } catch(e) { console.warn('GHSync.fetchAll:', e); return null; }
  }

  async function pushAll(onDone) {
    if (!isConnected()) { if (onDone) onDone(false); return false; }
    try {
      const branch  = creds.branch || 'main';
      const encoded = new TextEncoder().encode(JSON.stringify(allProgress, null, 2));
      const content = btoa(String.fromCharCode(...encoded));
      const body    = { message: 'chore: sync progress', content, branch };
      if (fileSHA) body.sha = fileSHA;
      const res = await fetch(apiUrl(), {
        method: 'PUT', headers: hdrs(), body: JSON.stringify(body),
      });
      if (!res.ok) { if (onDone) onDone(false); return false; }
      const data = await res.json();
      fileSHA = data.content.sha;
      markSynced();
      if (onDone) onDone(true);
      return true;
    } catch(e) { console.warn('GHSync.pushAll:', e); if (onDone) onDone(false); return false; }
  }

  // ── public API (backward-compatible with course pages) ───────────────────

  // Called by each course page on load.
  // Fetches the single progress.json and returns this course's slice.
  async function fetchState(courseId) {
    const all = await fetchAll();
    if (all === null) return null;                   // network error
    allProgress = { ...allProgress, ...all };        // GitHub wins on conflict
    return allProgress[courseId] || null;
  }

  // Called by each course page on every change.
  // Updates the in-memory cache and debounces a full push.
  function saveDebounced(courseId, courseState, delay, onStart, onDone) {
    allProgress[courseId] = courseState;
    clearTimeout(saveTimer);
    if (onStart) onStart();
    saveTimer = setTimeout(() => pushAll(onDone), delay || 2500);
  }

  // Kept for backward compatibility
  async function pushState(courseId, courseState, onDone) {
    allProgress[courseId] = courseState;
    return pushAll(onDone);
  }

  async function testConnection() {
    if (!isConnected()) return { ok: false, msg: 'No credentials set.' };
    try {
      const res = await fetch(
        `https://api.github.com/repos/${creds.owner}/${creds.repo}`,
        { headers: hdrs() }
      );
      if (res.status === 401) return { ok: false, msg: 'Invalid token.' };
      if (res.status === 404) return { ok: false, msg: 'Repo not found — check owner/repo.' };
      if (!res.ok)            return { ok: false, msg: `GitHub error ${res.status}.` };
      const d = await res.json();
      return { ok: true, msg: `Connected · ${d.full_name}` };
    } catch(e) { return { ok: false, msg: 'Network error.' }; }
  }

  function exportConfig() {
    if (!creds) return '';
    return btoa(JSON.stringify(creds));
  }

  function importConfig(str) {
    try {
      const c = JSON.parse(atob(str.trim()));
      if (!c || !c.pat || !c.owner || !c.repo) return null;
      return c;
    } catch { return null; }
  }

  loadCreds();
  seedFromLocalStorage();

  return {
    isConnected, saveCreds, getCreds,
    fetchState, fetchAll, pushAll, pushState, saveDebounced,
    testConnection, exportConfig, importConfig, getLastSynced,
  };
})();
