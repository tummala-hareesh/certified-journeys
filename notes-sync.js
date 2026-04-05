/**
 * notes-sync.js
 * ─────────────────────────────────────────────────────────────────────────────
 * Drop this file at the repo root.  Each course tracker includes it with:
 *   <script src="../../notes-sync.js"></script>
 *
 * What it does
 * ────────────
 * 1. Injects a "📝 Notes" panel into the page (works alongside any existing UI).
 * 2. Persists every note in localStorage under a course-scoped key.
 * 3. On save it writes a .md file to  courses/{courseId}/  via the GitHub
 *    Contents API (PUT /repos/{owner}/{repo}/contents/{path}).
 * 4. If no GitHub PAT is configured it falls back to a browser download, with
 *    a suggestion for the correct save path.
 *
 * GitHub PAT requirements
 * ───────────────────────
 * The PAT needs the `repo` scope (or `contents:write` for fine-grained tokens).
 * It is stored in localStorage under `cj_github_pat` – never sent anywhere
 * except api.github.com.
 *
 * Auto-detection
 * ──────────────
 * Owner + repo are derived from window.location so the script works on the
 * canonical site AND on any fork hosted as a different GitHub Pages domain.
 *   e.g.  https://alice.github.io/certified-journeys.github.io/courses/pspo-certified/index.html
 *          → owner = alice,  repo = certified-journeys.github.io
 *   e.g.  https://certified-journeys.github.io/courses/pspo-certified/index.html
 *          → owner = certified-journeys,  repo = certified-journeys.github.io
 *
 * Course ID auto-detection
 * ────────────────────────
 * Derived from the second-to-last path segment, e.g. /courses/pspo-certified/
 *   → courseId = "pspo-certified"
 * Override by adding  data-course-id="my-course"  to the <script> tag.
 */

(function () {
  "use strict";

  /* ── 1. Resolve owner / repo from the Pages URL ─────────────────────── */
  function resolveGitHub() {
    const { hostname, pathname } = window.location;

    // Standard GitHub Pages:  {owner}.github.io  (possibly with a repo sub-path)
    const ghPagesMatch = hostname.match(/^([^.]+)\.github\.io$/i);
    if (!ghPagesMatch) {
      // Local dev or custom domain – fall back to env var or return null
      return { owner: null, repo: null };
    }
    const owner = ghPagesMatch[1];
    // If the site root is at /{repo}/ the first non-empty path segment is the repo
    const parts = pathname.split("/").filter(Boolean);
    // If deployed at username.github.io/courses/... → repo is the gh-pages repo name
    // Heuristic: if the first segment is "courses" → project page at root → repo = hostname
    const repo =
      parts[0] && parts[0] !== "courses"
        ? parts[0] // project page  e.g. /certified-journeys.github.io/courses/...
        : `${owner}.github.io`; // user/org page deployed at root
    return { owner, repo };
  }

  /* ── 2. Resolve courseId from URL or data attribute ─────────────────── */
  function resolveCourseId() {
    // Allow override via <script src="..." data-course-id="pspo-certified">
    const scripts = document.querySelectorAll('script[src*="notes-sync"]');
    for (const s of scripts) {
      if (s.dataset.courseId) return s.dataset.courseId;
    }
    // Derive from URL: /courses/{courseId}/index.html
    const parts = window.location.pathname.split("/").filter(Boolean);
    const idx = parts.indexOf("courses");
    if (idx !== -1 && parts[idx + 1]) return parts[idx + 1];
    return "unknown-course";
  }

  /* ── 3. LocalStorage helpers ─────────────────────────────────────────── */
  const COURSE_ID = resolveCourseId();
  const LS_NOTES_KEY = `cj_notes_${COURSE_ID}`;
  const LS_PAT_KEY = "cj_github_pat";

  function loadNotes() {
    try {
      return JSON.parse(localStorage.getItem(LS_NOTES_KEY) || "[]");
    } catch {
      return [];
    }
  }

  function saveNotes(notes) {
    localStorage.setItem(LS_NOTES_KEY, JSON.stringify(notes));
  }

  function getPAT() {
    return localStorage.getItem(LS_PAT_KEY) || "";
  }

  function setPAT(pat) {
    if (pat) localStorage.setItem(LS_PAT_KEY, pat);
    else localStorage.removeItem(LS_PAT_KEY);
  }

  /* ── 4. Markdown file generation ─────────────────────────────────────── */
  function toSlug(str) {
    return str
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "")
      .slice(0, 50);
  }

  function buildMarkdown(note) {
    const lines = [
      `# ${note.title}`,
      "",
      `**Course:** ${COURSE_ID}`,
      `**Day:** ${note.day || "—"}`,
      `**Created:** ${new Date(note.createdAt).toISOString()}`,
      `**Tags:** ${note.tags || "—"}`,
      "",
      "---",
      "",
      note.content,
      "",
    ];
    return lines.join("\n");
  }

  function noteFilename(note) {
    const date = new Date(note.createdAt).toISOString().slice(0, 10);
    const slug = toSlug(note.title) || "note";
    return `${date}-${slug}.md`;
  }

  /* ── 5. GitHub API commit ────────────────────────────────────────────── */
  async function commitToGitHub(note) {
    const { owner, repo } = resolveGitHub();
    const pat = getPAT();

    if (!owner || !repo || !pat) return false;

    const filename = noteFilename(note);
    const filePath = `courses/${COURSE_ID}/${filename}`;
    const content = buildMarkdown(note);
    const encoded = btoa(unescape(encodeURIComponent(content))); // UTF-8 safe base64

    const apiUrl = `https://api.github.com/repos/${owner}/${repo}/contents/${filePath}`;

    try {
      // Check if file already exists (for updating it)
      let sha;
      const checkResp = await fetch(apiUrl, {
        headers: {
          Authorization: `Bearer ${pat}`,
          Accept: "application/vnd.github+json",
        },
      });
      if (checkResp.ok) {
        const existing = await checkResp.json();
        sha = existing.sha;
      }

      const body = {
        message: `docs(${COURSE_ID}): add note "${note.title}"`,
        content: encoded,
        ...(sha ? { sha } : {}),
      };

      const resp = await fetch(apiUrl, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${pat}`,
          Accept: "application/vnd.github+json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      return resp.ok;
    } catch (err) {
      console.error("[notes-sync] GitHub commit failed:", err);
      return false;
    }
  }

  /* ── 6. Browser download fallback ───────────────────────────────────── */
  function downloadMd(note) {
    const filename = noteFilename(note);
    const content = buildMarkdown(note);
    const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }

  /* ── 7. Inject styles ────────────────────────────────────────────────── */
  function injectStyles() {
    if (document.getElementById("cj-notes-styles")) return;
    const style = document.createElement("style");
    style.id = "cj-notes-styles";
    style.textContent = `
      #cj-notes-panel {
        font-family: 'DM Sans', system-ui, sans-serif;
        background: var(--surface, #fff);
        border: 0.5px solid var(--border, rgba(0,0,0,0.08));
        border-radius: var(--radius, 14px);
        padding: 1.25rem;
        margin-top: 1.5rem;
        box-shadow: var(--shadow, 0 1px 3px rgba(0,0,0,0.08));
      }
      #cj-notes-panel h3 {
        font-size: 14px;
        font-weight: 600;
        color: var(--text, #18181a);
        text-transform: uppercase;
        letter-spacing: .05em;
        margin: 0 0 1rem 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
      }
      #cj-notes-panel h3 span { flex:1; }
      .cj-note-form { display: flex; flex-direction: column; gap: 8px; margin-bottom: 1rem; }
      .cj-note-form input,
      .cj-note-form textarea,
      .cj-note-form select {
        font-family: inherit;
        font-size: 13px;
        padding: 8px 12px;
        border-radius: var(--radius-sm, 9px);
        border: 0.5px solid var(--border2, rgba(0,0,0,0.16));
        background: var(--surface, #fff);
        color: var(--text, #18181a);
        width: 100%;
        box-sizing: border-box;
        outline: none;
        transition: border-color .18s;
      }
      .cj-note-form input:focus,
      .cj-note-form textarea:focus { border-color: var(--green, #1d9e75); }
      .cj-note-form textarea { resize: vertical; min-height: 90px; line-height: 1.6; }
      .cj-note-form-row { display: flex; gap: 8px; }
      .cj-note-form-row > * { flex: 1; }
      .cj-btn-row { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
      .cj-btn {
        font-family: inherit;
        font-size: 12px;
        padding: 7px 16px;
        border-radius: 99px;
        border: 0.5px solid var(--border2, rgba(0,0,0,0.16));
        background: none;
        color: var(--text2, #52524e);
        cursor: pointer;
        transition: all .18s;
        display: inline-flex;
        align-items: center;
        gap: 5px;
      }
      .cj-btn:hover { background: var(--surface2, #eee); color: var(--text, #18181a); }
      .cj-btn-primary {
        background: var(--green, #1d9e75);
        color: #fff;
        border-color: var(--green, #1d9e75);
      }
      .cj-btn-primary:hover { background: var(--green-dark, #0f6e56); border-color: var(--green-dark, #0f6e56); }
      .cj-btn-danger { color: var(--coral, #d85a30); }
      .cj-btn-danger:hover { background: var(--coral-light, #faede8); }
      .cj-status {
        font-size: 11px;
        padding: 3px 10px;
        border-radius: 99px;
        background: var(--surface2, #eee);
        color: var(--text3, #8c8b85);
        margin-left: auto;
      }
      .cj-status.success { background: var(--green-light, #e8f8f2); color: var(--green-dark, #0f6e56); }
      .cj-status.error   { background: var(--coral-light, #faede8); color: var(--coral-dark, #993c1d); }
      .cj-notes-list { display: flex; flex-direction: column; gap: 6px; margin-top: 1rem; }
      .cj-note-item {
        background: var(--surface2, #f5f4f0);
        border-radius: var(--radius-sm, 9px);
        padding: 10px 12px;
        display: flex;
        align-items: flex-start;
        gap: 10px;
        font-size: 12px;
      }
      .cj-note-item-body { flex: 1; min-width: 0; }
      .cj-note-item-title {
        font-size: 13px;
        font-weight: 500;
        color: var(--text, #18181a);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 2px;
      }
      .cj-note-item-meta { font-size: 11px; color: var(--text3, #8c8b85); }
      .cj-note-item-preview {
        font-size: 12px;
        color: var(--text2, #52524e);
        margin-top: 4px;
        overflow: hidden;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
      }
      .cj-note-actions { display: flex; gap: 4px; flex-shrink: 0; }
      .cj-icon-btn {
        font-family: inherit;
        font-size: 12px;
        padding: 4px 8px;
        border-radius: 6px;
        border: none;
        background: none;
        color: var(--text3, #8c8b85);
        cursor: pointer;
        transition: all .15s;
      }
      .cj-icon-btn:hover { background: var(--surface3, #e8e6df); color: var(--text, #18181a); }
      .cj-pat-section {
        background: var(--surface2, #f5f4f0);
        border-radius: var(--radius-sm, 9px);
        padding: 10px 12px;
        margin-top: 12px;
        font-size: 12px;
        color: var(--text2, #52524e);
      }
      .cj-pat-section summary {
        cursor: pointer;
        font-size: 12px;
        color: var(--text3, #8c8b85);
        user-select: none;
      }
      .cj-pat-section summary:hover { color: var(--text, #18181a); }
      .cj-pat-row {
        display: flex;
        gap: 6px;
        margin-top: 8px;
        align-items: center;
      }
      .cj-pat-row input {
        flex: 1;
        font-family: 'DM Mono', monospace;
        font-size: 12px;
        padding: 6px 10px;
        border-radius: var(--radius-sm, 9px);
        border: 0.5px solid var(--border2, rgba(0,0,0,0.16));
        background: var(--surface, #fff);
        color: var(--text, #18181a);
        outline: none;
      }
      .cj-empty-state {
        text-align: center;
        padding: 1.5rem 0;
        font-size: 13px;
        color: var(--text3, #8c8b85);
      }
    `;
    document.head.appendChild(style);
  }

  /* ── 8. Render the notes panel ───────────────────────────────────────── */
  function render() {
    const panel = document.getElementById("cj-notes-panel");
    if (!panel) return;

    const notes = loadNotes();
    const pat = getPAT();
    const { owner, repo } = resolveGitHub();
    const canCommit = !!(owner && repo && pat);

    panel.innerHTML = `
      <h3>
        <span>📝 Notes — ${COURSE_ID}</span>
      </h3>

      <!-- New note form -->
      <div class="cj-note-form" id="cj-note-form">
        <input id="cj-note-title" type="text" placeholder="Note title (e.g. Day 3 key concepts)" />
        <div class="cj-note-form-row">
          <input id="cj-note-day" type="text" placeholder="Day / topic reference" />
          <input id="cj-note-tags" type="text" placeholder="Tags (comma-separated)" />
        </div>
        <textarea id="cj-note-content" placeholder="Write your notes in Markdown…"></textarea>
        <div class="cj-btn-row">
          <button class="cj-btn cj-btn-primary" onclick="window.__cjNotes.save()">
            💾 Save note
          </button>
          <button class="cj-btn" onclick="window.__cjNotes.downloadLatest()">
            ⬇ Download .md
          </button>
          <span class="cj-status" id="cj-save-status" style="display:none;"></span>
        </div>
      </div>

      <!-- Saved notes list -->
      <div class="cj-notes-list" id="cj-notes-list">
        ${
          notes.length === 0
            ? `<div class="cj-empty-state">No notes yet — write your first one above.</div>`
            : notes
                .slice()
                .reverse()
                .map(
                  (n) => `
            <div class="cj-note-item" data-id="${n.id}">
              <div class="cj-note-item-body">
                <div class="cj-note-item-title">${escHtml(n.title)}</div>
                <div class="cj-note-item-meta">
                  ${n.day ? `Day: ${escHtml(n.day)} · ` : ""}
                  ${new Date(n.createdAt).toLocaleDateString("en-CA", { month: "short", day: "numeric", year: "2-digit" })}
                  ${n.tags ? ` · ${escHtml(n.tags)}` : ""}
                  ${n.syncedAt ? ` · ✅ synced` : ""}
                </div>
                <div class="cj-note-item-preview">${escHtml(n.content.slice(0, 120))}${n.content.length > 120 ? "…" : ""}</div>
              </div>
              <div class="cj-note-actions">
                <button class="cj-icon-btn" title="Download .md" onclick="window.__cjNotes.downloadNote('${n.id}')">⬇</button>
                <button class="cj-icon-btn" title="Re-sync to GitHub" onclick="window.__cjNotes.resync('${n.id}')">🔁</button>
                <button class="cj-icon-btn cj-btn-danger" title="Delete" onclick="window.__cjNotes.deleteNote('${n.id}')">✕</button>
              </div>
            </div>`
                )
                .join("")
        }
      </div>

      <!-- GitHub PAT configuration -->
      <details class="cj-pat-section" ${canCommit ? "" : "open"}>
        <summary>
          ${canCommit ? `✅ GitHub sync active → <code>${owner}/${repo}/courses/${COURSE_ID}/</code>` : "⚙ Configure GitHub sync (optional)"}
        </summary>
        <p style="margin-top:8px;line-height:1.6;">
          Enter a GitHub Personal Access Token with <code>repo</code> scope (or 
          <code>contents: write</code> for fine-grained tokens) to automatically 
          commit each note as a <code>.md</code> file inside 
          <code>courses/${COURSE_ID}/</code>.
          The token is stored only in your browser's localStorage.
        </p>
        <div class="cj-pat-row">
          <input id="cj-pat-input" type="password" placeholder="ghp_…" value="${escHtml(pat)}" />
          <button class="cj-btn cj-btn-primary" onclick="window.__cjNotes.savePAT()">Save</button>
          ${pat ? `<button class="cj-btn cj-btn-danger" onclick="window.__cjNotes.clearPAT()">Clear</button>` : ""}
        </div>
      </details>
    `;
  }

  function escHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function setStatus(msg, type = "info", duration = 3000) {
    const el = document.getElementById("cj-save-status");
    if (!el) return;
    el.textContent = msg;
    el.className = `cj-status ${type}`;
    el.style.display = "inline-block";
    if (duration) setTimeout(() => (el.style.display = "none"), duration);
  }

  /* ── 9. Public API ───────────────────────────────────────────────────── */
  window.__cjNotes = {
    async save() {
      const title = document.getElementById("cj-note-title")?.value.trim();
      const content = document.getElementById("cj-note-content")?.value.trim();
      const day = document.getElementById("cj-note-day")?.value.trim();
      const tags = document.getElementById("cj-note-tags")?.value.trim();

      if (!title) { setStatus("⚠ Please enter a title.", "error", 2500); return; }
      if (!content) { setStatus("⚠ Please enter some content.", "error", 2500); return; }

      const note = {
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
        title,
        content,
        day,
        tags,
        createdAt: Date.now(),
        syncedAt: null,
      };

      const notes = loadNotes();
      notes.push(note);
      saveNotes(notes);

      setStatus("Saving…", "info", 0);

      const committed = await commitToGitHub(note);
      if (committed) {
        note.syncedAt = Date.now();
        notes[notes.length - 1] = note;
        saveNotes(notes);
        setStatus("✅ Note saved & committed to GitHub!", "success");
      } else if (getPAT()) {
        setStatus("⚠ GitHub commit failed — saved locally only.", "error");
      } else {
        setStatus("💾 Saved locally. Configure GitHub sync below to auto-commit.", "info");
      }

      // Clear form
      ["cj-note-title","cj-note-content","cj-note-day","cj-note-tags"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = "";
      });

      render();
    },

    downloadNote(id) {
      const note = loadNotes().find((n) => n.id === id);
      if (note) downloadMd(note);
    },

    downloadLatest() {
      const notes = loadNotes();
      if (!notes.length) { setStatus("No notes to download yet.", "error", 2000); return; }
      downloadMd(notes[notes.length - 1]);
    },

    async resync(id) {
      const notes = loadNotes();
      const idx = notes.findIndex((n) => n.id === id);
      if (idx === -1) return;
      const note = notes[idx];

      if (!getPAT()) {
        setStatus("⚠ No PAT configured — cannot sync.", "error"); return;
      }

      setStatus("Syncing…", "info", 0);
      const ok = await commitToGitHub(note);
      if (ok) {
        notes[idx].syncedAt = Date.now();
        saveNotes(notes);
        setStatus("✅ Synced!", "success");
        render();
      } else {
        setStatus("❌ Sync failed.", "error");
      }
    },

    deleteNote(id) {
      if (!confirm("Delete this note? (It will remain in GitHub if already committed.)")) return;
      saveNotes(loadNotes().filter((n) => n.id !== id));
      render();
    },

    savePAT() {
      const val = document.getElementById("cj-pat-input")?.value.trim();
      setPAT(val);
      render();
      setStatus(val ? "✅ Token saved!" : "Token cleared.", "success");
    },

    clearPAT() {
      setPAT("");
      render();
    },
  };

  /* ── 10. Mount the panel ─────────────────────────────────────────────── */
  function mount() {
    // Don't double-mount
    if (document.getElementById("cj-notes-panel")) return;

    injectStyles();

    const panel = document.createElement("div");
    panel.id = "cj-notes-panel";

    // Try to insert after a known anchor, otherwise append to body
    const anchors = [
      document.querySelector(".day-content"),
      document.querySelector(".content"),
      document.querySelector("main"),
      document.querySelector(".page"),
      document.body,
    ];
    const target = anchors.find(Boolean);
    target.appendChild(panel);

    render();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }
})();
