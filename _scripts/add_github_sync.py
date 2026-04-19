#!/usr/bin/env python3
"""
Add GitHub sync to all 7 courses:
1. CSS: sync badge + modal styles
2. HTML: replace footer text; add modal + script tag before <script>
3. JS: loadState → async; saveState → calls GHSync; new modal/badge functions; init → .then()
"""
import re, os

BASE = '/home/ht/Documents/GitHub_HT/certified-journeys.github.io/courses'
ALL_COURSES = ['pspo-certified', 'aws-ml-certified', 'terraform-certified',
               'powerbi-certified', 'dlt-certified', 'polars-certified']

# ── CSS ──────────────────────────────────────────────────────────────────────

SYNC_CSS = """\
/* GitHub sync badge */
.sync-badge{display:inline-flex;align-items:center;gap:5px;font-size:11px;padding:3px 10px;border-radius:99px;border:.5px solid var(--border2);background:none;color:var(--text3);cursor:pointer;font-family:inherit;transition:all .2s;}
.sync-badge:hover{background:var(--surface2);color:var(--text2);}
.sync-badge.connected{color:var(--green-dark);border-color:var(--green);}
.sync-badge.syncing{color:var(--blue-dark);border-color:var(--blue);}
.sync-badge.error{color:var(--coral-dark);border-color:var(--coral);}
/* GitHub sync modal */
.gh-modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:200;align-items:center;justify-content:center;}
.gh-modal.open{display:flex;}
.gh-modal-box{background:var(--surface);border:.5px solid var(--border2);border-radius:var(--radius);padding:1.5rem;width:min(460px,92vw);box-shadow:var(--shadow-md);}
.gh-modal-box h3{font-size:15px;font-weight:600;margin-bottom:4px;}
.gh-modal-sub{font-size:12px;color:var(--text2);margin-bottom:1.1rem;line-height:1.6;}
.gh-field{margin-bottom:10px;}
.gh-field label{display:block;font-size:11px;font-weight:500;color:var(--text2);margin-bottom:3px;}
.gh-field input{width:100%;font-size:13px;padding:7px 10px;border:.5px solid var(--border2);border-radius:var(--radius-sm);background:var(--surface);color:var(--text);font-family:'DM Mono',monospace;transition:border-color .15s;}
.gh-field input:focus{outline:none;border-color:var(--blue);}
.gh-modal-actions{display:flex;gap:8px;margin-top:1rem;align-items:center;flex-wrap:wrap;}
.gh-btn-save{font-size:13px;padding:8px 18px;border-radius:var(--radius-sm);border:.5px solid var(--green);background:var(--green);color:#fff;cursor:pointer;font-family:inherit;font-weight:500;transition:background .15s;}
.gh-btn-save:hover{background:var(--green-dark);}
.gh-btn-cancel{font-size:13px;padding:8px 14px;border-radius:var(--radius-sm);border:.5px solid var(--border2);background:none;color:var(--text2);cursor:pointer;font-family:inherit;}
.gh-btn-disconnect{font-size:12px;padding:6px 12px;border-radius:var(--radius-sm);border:.5px solid var(--coral);background:none;color:var(--coral-dark);cursor:pointer;font-family:inherit;}
.gh-modal-msg{font-size:12px;margin-left:auto;color:var(--text3);}
.gh-modal-msg.ok{color:var(--green-dark);}
.gh-modal-msg.err{color:var(--coral-dark);}"""

CSS_ANCHOR = '</style>'

# ── Footer ────────────────────────────────────────────────────────────────────
# Match the full footer div so we can replace with the new version (course-agnostic)
FOOTER_RE = re.compile(
    r'<div class="page-footer">Progress saved locally · '
    r'<span id="sk-display">[^<]+</span> · No account needed · '
    r'<a href="[^"]+">← All journeys</a></div>'
)
NEW_FOOTER = (
    '<div class="page-footer">'
    '<button class="sync-badge" id="sync-badge" onclick="openGHModal()">☁ Connect GitHub</button>'
    ' · <span id="sk-display"></span> · '
    '<a href="../../index.html">← All journeys</a></div>'
)

# ── Modal + script tag (inserted before the inline <script> block) ─────────────

MODAL_AND_SCRIPT = """\

<!-- GitHub sync modal -->
<div class="gh-modal" id="gh-modal" onclick="if(event.target===this)closeGHModal()">
  <div class="gh-modal-box">
    <h3>☁ GitHub Sync</h3>
    <p class="gh-modal-sub">Progress is committed to <code>courses/COURSE_ID/progress.json</code> in your repo on every change.<br>
    Generate a <strong>Fine-grained token</strong> with <em>Contents: Read &amp; Write</em> on this repo.</p>
    <div class="gh-field"><label>Personal Access Token</label><input id="gh-pat" type="password" placeholder="github_pat_…" autocomplete="off"></div>
    <div class="gh-field"><label>Owner (your GitHub username or org)</label><input id="gh-owner" type="text" placeholder="your-username"></div>
    <div class="gh-field"><label>Repository</label><input id="gh-repo" type="text" placeholder="certified-journeys.github.io"></div>
    <div class="gh-field"><label>Branch</label><input id="gh-branch" type="text" placeholder="main"></div>
    <div class="gh-modal-actions">
      <button class="gh-btn-save" onclick="saveGHCreds()">Test &amp; Save</button>
      <button class="gh-btn-cancel" onclick="closeGHModal()">Cancel</button>
      <button class="gh-btn-disconnect" id="gh-disconnect-btn" style="display:none" onclick="disconnectGH()">Disconnect</button>
      <span class="gh-modal-msg" id="gh-modal-msg"></span>
    </div>
  </div>
</div>

<script src="../../github-sync.js"></script>"""

# ── JS: loadState (async) ─────────────────────────────────────────────────────

OLD_LOAD_STATE = (
    'function loadState(){try{const s=localStorage.getItem(STORAGE_KEY);'
    'if(s)state={...state,...JSON.parse(s)};}catch(e){}}'
)
NEW_LOAD_STATE = (
    'async function loadState(){'
    'try{const s=localStorage.getItem(STORAGE_KEY);if(s)state={...state,...JSON.parse(s)};}catch(e){}'
    'if(GHSync.isConnected()){'
    'updateSyncBadge("syncing");'
    'const gh=await GHSync.fetchState(COURSE_ID);'
    'if(gh){state={...state,...gh};try{localStorage.setItem(STORAGE_KEY,JSON.stringify(state));}catch(e){}}'
    'updateSyncBadge(gh?"connected":"error");'
    '}else{updateSyncBadge("disconnected");}}'
)

# ── JS: saveState (add GHSync debounced push at end) ─────────────────────────

OLD_SAVE_END = '  broadcastStatus();\n}'
NEW_SAVE_END = (
    '  broadcastStatus();\n'
    '  if(GHSync.isConnected())GHSync.saveDebounced(COURSE_ID,state,2500,'
    '()=>updateSyncBadge("syncing"),ok=>updateSyncBadge(ok?"connected":"error"));\n'
    '}'
)

# ── JS: modal + badge functions (insert before renderAll) ─────────────────────

GH_JS_FUNCTIONS = """\
function updateSyncBadge(s){
  const el=document.getElementById('sync-badge');if(!el)return;
  const L={disconnected:'☁ Connect GitHub',connected:'✓ Synced',syncing:'↑ Syncing…',error:'⚠ Sync failed'};
  el.textContent=L[s]||L.disconnected;
  el.className='sync-badge'+(s==='connected'?' connected':s==='syncing'?' syncing':s==='error'?' error':'');
}
function openGHModal(){
  const c=GHSync.getCreds()||{};
  document.getElementById('gh-pat').value=c.pat||'';
  document.getElementById('gh-owner').value=c.owner||'';
  document.getElementById('gh-repo').value=c.repo||'';
  document.getElementById('gh-branch').value=c.branch||'main';
  document.getElementById('gh-modal-msg').textContent='';
  document.getElementById('gh-modal-msg').className='gh-modal-msg';
  document.getElementById('gh-disconnect-btn').style.display=GHSync.isConnected()?'':'none';
  document.getElementById('gh-modal').classList.add('open');
}
function closeGHModal(){document.getElementById('gh-modal').classList.remove('open');}
async function saveGHCreds(){
  const msg=document.getElementById('gh-modal-msg');
  msg.textContent='Testing…';msg.className='gh-modal-msg';
  const c={
    pat:document.getElementById('gh-pat').value.trim(),
    owner:document.getElementById('gh-owner').value.trim(),
    repo:document.getElementById('gh-repo').value.trim(),
    branch:document.getElementById('gh-branch').value.trim()||'main',
  };
  if(!c.pat||!c.owner||!c.repo){msg.textContent='Fill in all required fields.';msg.className='gh-modal-msg err';return;}
  GHSync.saveCreds(c);
  const r=await GHSync.testConnection();
  msg.textContent=r.msg;msg.className='gh-modal-msg '+(r.ok?'ok':'err');
  if(r.ok){
    document.getElementById('gh-disconnect-btn').style.display='';
    updateSyncBadge('syncing');
    const gh=await GHSync.fetchState(COURSE_ID);
    if(gh){state={...state,...gh};try{localStorage.setItem(STORAGE_KEY,JSON.stringify(state));}catch(e){}renderAll();}
    updateSyncBadge('connected');
    setTimeout(closeGHModal,1200);
  }
}
function disconnectGH(){GHSync.saveCreds(null);updateSyncBadge('disconnected');document.getElementById('gh-disconnect-btn').style.display='none';closeGHModal();}
"""

BEFORE_RENDER_ALL = 'function renderAll(){'

# ── Init ──────────────────────────────────────────────────────────────────────

OLD_INIT = 'loadState();\nrenderAll();'
NEW_INIT = 'loadState().then(renderAll);'


def process(course_id):
    path = os.path.join(BASE, course_id, 'index.html')
    html = open(path, encoding='utf-8').read()
    log = []

    # 1. CSS
    if 'sync-badge' not in html:
        html = html.replace(CSS_ANCHOR, SYNC_CSS + '\n' + CSS_ANCHOR, 1)
        log.append('added sync CSS')

    # 2. Footer
    if FOOTER_RE.search(html):
        html = FOOTER_RE.sub(NEW_FOOTER, html)
        # Restore the sk-display value (course-specific)
        html = html.replace('<span id="sk-display"></span>',
                            f'<span id="sk-display">cj_{course_id}_v1</span>')
        log.append('updated footer')

    # 3. Modal + github-sync.js script tag (before the inline <script>)
    if 'id="gh-modal"' not in html:
        # Insert before the last (inline) <script> tag
        parts = html.rsplit('\n\n<script>', 1)
        html = parts[0] + MODAL_AND_SCRIPT + '\n\n<script>' + parts[1]
        log.append('added modal + script tag')

    # 4. loadState → async
    if 'async function loadState' not in html and OLD_LOAD_STATE in html:
        html = html.replace(OLD_LOAD_STATE, NEW_LOAD_STATE)
        log.append('made loadState async')

    # 5. saveState → add GHSync push
    # Count occurrences to be safe
    if 'saveDebounced' not in html:
        # Replace only the first broadcastStatus();\n} that belongs to saveState
        # saveState is the first function with this closing pattern
        html = html.replace(OLD_SAVE_END, NEW_SAVE_END, 1)
        log.append('added GHSync push to saveState')

    # 6. GH modal/badge JS functions
    if 'openGHModal' not in html and BEFORE_RENDER_ALL in html:
        html = html.replace(BEFORE_RENDER_ALL, GH_JS_FUNCTIONS + BEFORE_RENDER_ALL, 1)
        log.append('added GH JS functions')

    # 7. Init
    if OLD_INIT in html:
        html = html.replace(OLD_INIT, NEW_INIT)
        log.append('updated init to async')

    open(path, 'w', encoding='utf-8').write(html)
    print(f'✓ {course_id}: {", ".join(log) if log else "already up to date"}')


for c in ALL_COURSES:
    process(c)

print('\nDone.')
