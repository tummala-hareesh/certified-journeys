'use strict';
const GHSync = (() => {
  const CREDS_KEY       = 'cj_gist_creds';
  const LAST_SYNCED_KEY = 'cj_last_synced';
  const FILENAME        = 'certified-journeys-progress.json';

  let creds       = null; // { pat, gistId }
  let allProgress = {};   // in-memory cache of every course
  let saveTimer   = null;

  // ── init ─────────────────────────────────────────────────

  function loadCreds() {
    try { const s = localStorage.getItem(CREDS_KEY); if (s) creds = JSON.parse(s); } catch(e) {}
    // migrate old repo-based creds — they don't have gistId so discard them
    if (creds && !creds.gistId) { creds = null; localStorage.removeItem(CREDS_KEY); }
  }

  // Pre-populate allProgress from any course state already in localStorage so a
  // push from one course never overwrites another course's locally-saved data.
  function seedFromLocalStorage() {
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (!key || !/^cj_.+_v1$/.test(key)) continue;
      try {
        const id = key.slice(3, -3);
        const s  = localStorage.getItem(key);
        if (s) allProgress[id] = JSON.parse(s);
      } catch(e) {}
    }
  }

  // ── credentials ───────────────────────────────────────────

  function saveCreds(c) {
    creds = c;
    try {
      if (c) localStorage.setItem(CREDS_KEY, JSON.stringify(c));
      else   localStorage.removeItem(CREDS_KEY);
    } catch(e) {}
  }

  function getCreds()    { return creds; }
  function isConnected() { return !!(creds && creds.pat && creds.gistId); }

  // ── GitHub Gist API ───────────────────────────────────────

  function hdrs(pat) {
    return {
      'Authorization':        `Bearer ${pat || creds.pat}`,
      'Accept':               'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'Content-Type':         'application/json',
    };
  }

  // ── last-synced timestamp ─────────────────────────────────

  function getLastSynced() { return localStorage.getItem(LAST_SYNCED_KEY); }

  function markSynced() {
    const ts = new Date().toISOString();
    localStorage.setItem(LAST_SYNCED_KEY, ts);
    try { window.dispatchEvent(new CustomEvent('cj-synced', { detail: ts })); } catch(e) {}
  }

  // ── find or create gist (called once on connect) ──────────

  async function findOrCreateGist(pat) {
    const h = hdrs(pat);
    // Search the user's gists for one containing our progress file
    for (let page = 1; page <= 5; page++) {
      const res = await fetch(
        `https://api.github.com/gists?per_page=100&page=${page}`,
        { headers: h }
      );
      if (!res.ok) break;
      const list = await res.json();
      const hit  = list.find(g => g.files && g.files[FILENAME]);
      if (hit) return hit.id;
      if (list.length < 100) break; // last page
    }
    // None found — create a new secret gist
    const res = await fetch('https://api.github.com/gists', {
      method:  'POST',
      headers: h,
      body: JSON.stringify({
        description: 'certified-journeys — course progress',
        public:      false,
        files:       { [FILENAME]: { content: JSON.stringify({}, null, 2) } },
      }),
    });
    if (!res.ok) return null;
    const data = await res.json();
    return data.id;
  }

  // ── public: connect (called from main page UI) ────────────
  // Only requires a PAT — gist is auto-found or created.

  async function connect(pat) {
    if (!pat) return { ok: false, msg: 'Enter your Personal Access Token.' };
    try {
      // 1. Validate token & get username
      const userRes = await fetch('https://api.github.com/user', { headers: hdrs(pat) });
      if (userRes.status === 401) return { ok: false, msg: 'Invalid token.' };
      if (!userRes.ok) return { ok: false, msg: `GitHub error ${userRes.status}.` };
      const user = await userRes.json();

      // 2. Find or create the progress gist
      const gistId = await findOrCreateGist(pat);
      if (!gistId) return { ok: false, msg: 'Could not access gists. Make sure the token has Gist scope.' };

      saveCreds({ pat, gistId });
      return { ok: true, msg: `Connected as ${user.login}`, gistId };
    } catch(e) {
      return { ok: false, msg: 'Network error — check your connection.' };
    }
  }

  // ── fetch all progress from the gist ─────────────────────

  async function fetchAll() {
    if (!isConnected()) return null;
    try {
      const res = await fetch(
        `https://api.github.com/gists/${creds.gistId}`,
        { headers: hdrs() }
      );
      if (res.status === 404) return {};
      if (!res.ok) return null;
      const data = await res.json();
      const file = data.files[FILENAME];
      if (!file) return {};
      // file.content may be truncated for large gists — fall back to raw_url
      const text = file.truncated
        ? await (await fetch(file.raw_url)).text()
        : file.content;
      return JSON.parse(text);
    } catch(e) { console.warn('GHSync.fetchAll:', e); return null; }
  }

  // ── push allProgress to the gist ─────────────────────────

  async function pushAll(onDone) {
    if (!isConnected()) { if (onDone) onDone(false); return false; }
    try {
      const res = await fetch(`https://api.github.com/gists/${creds.gistId}`, {
        method:  'PATCH',
        headers: hdrs(),
        body: JSON.stringify({
          files: { [FILENAME]: { content: JSON.stringify(allProgress, null, 2) } },
        }),
      });
      if (!res.ok) { if (onDone) onDone(false); return false; }
      markSynced();
      if (onDone) onDone(true);
      return true;
    } catch(e) { console.warn('GHSync.pushAll:', e); if (onDone) onDone(false); return false; }
  }

  // ── course-page API (backward-compatible) ─────────────────

  async function fetchState(courseId) {
    const all = await fetchAll();
    if (all === null) return null;
    allProgress = { ...allProgress, ...all }; // GitHub wins on conflict
    return allProgress[courseId] || null;
  }

  function saveDebounced(courseId, courseState, delay, onStart, onDone) {
    allProgress[courseId] = courseState;
    clearTimeout(saveTimer);
    if (onStart) onStart();
    saveTimer = setTimeout(() => pushAll(onDone), delay || 2500);
  }

  async function pushState(courseId, courseState, onDone) {
    allProgress[courseId] = courseState;
    return pushAll(onDone);
  }

  async function testConnection() {
    if (!isConnected()) return { ok: false, msg: 'Not connected.' };
    try {
      const res = await fetch(
        `https://api.github.com/gists/${creds.gistId}`,
        { headers: hdrs() }
      );
      if (res.status === 401) return { ok: false, msg: 'Invalid token.' };
      if (res.status === 404) return { ok: false, msg: 'Gist not found.' };
      if (!res.ok)            return { ok: false, msg: `Error ${res.status}.` };
      return { ok: true };
    } catch(e) { return { ok: false, msg: 'Network error.' }; }
  }

  // Transfer code — base64 of { pat, gistId }
  function exportConfig() {
    if (!creds) return '';
    return btoa(JSON.stringify({ pat: creds.pat, gistId: creds.gistId }));
  }

  function importConfig(str) {
    try {
      const c = JSON.parse(atob(str.trim()));
      if (!c || !c.pat || !c.gistId) return null;
      return c;
    } catch { return null; }
  }

  loadCreds();
  seedFromLocalStorage();

  return {
    isConnected, saveCreds, getCreds, connect,
    fetchState, pushState, saveDebounced,
    testConnection, exportConfig, importConfig, getLastSynced,
  };
})();
