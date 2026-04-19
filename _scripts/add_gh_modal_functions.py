"""
Add missing GitHub sync modal functions + cross-device transfer UI to all 7 course files.
Run from repo root: python3 _scripts/add_gh_modal_functions.py
"""
import os, re

COURSES_DIR = os.path.join(os.path.dirname(__file__), '..', 'courses')

# ── Transfer UI row — inserted after the Branch field, before gh-modal-actions ──
TRANSFER_HTML = '''    <div class="gh-field" style="margin-top:1rem;padding-top:1rem;border-top:.5px solid var(--border2)">
      <label>Transfer to another device <span style="font-weight:400;color:var(--text3);font-size:11px">— copy on device 1, paste on device 2</span></label>
      <div style="display:flex;gap:6px;margin-top:4px">
        <input id="gh-config-str" type="text" placeholder="Config appears here when connected — or paste from another device" style="flex:1;font-size:11px" autocomplete="off"/>
        <button class="gh-btn-cancel" onclick="copyGHConfig()">Copy</button>
        <button class="gh-btn-cancel" onclick="importGHConfig()">Import</button>
      </div>
    </div>'''

# ── Modal functions — inserted before broadcastStatus() ──
MODAL_FUNCTIONS = '''function updateSyncBadge(st){
  const b=document.getElementById('sync-badge');if(!b)return;
  const map={connected:'☁ Synced',syncing:'☁ Syncing…',error:'☁ Sync error',disconnected:'☁ Connect GitHub'};
  b.textContent=map[st]||'☁ Connect GitHub';
  b.className='sync-badge'+(st==='connected'?' sync-ok':st==='syncing'?' sync-busy':st==='error'?' sync-err':'');
}
function openGHModal(){
  const c=GHSync.getCreds();
  if(c){document.getElementById('gh-pat').value=c.pat||'';document.getElementById('gh-owner').value=c.owner||'';document.getElementById('gh-repo').value=c.repo||'';document.getElementById('gh-branch').value=c.branch||'main';}
  document.getElementById('gh-disconnect-btn').style.display=GHSync.isConnected()?'inline-flex':'none';
  document.getElementById('gh-modal-msg').textContent='';
  const cfg=GHSync.exportConfig();const inp=document.getElementById('gh-config-str');if(inp)inp.value=cfg||'';
  document.getElementById('gh-modal').classList.add('open');
}
function closeGHModal(){document.getElementById('gh-modal').classList.remove('open');}
async function saveGHCreds(){
  const pat=document.getElementById('gh-pat').value.trim();
  const owner=document.getElementById('gh-owner').value.trim();
  const repo=document.getElementById('gh-repo').value.trim();
  const branch=document.getElementById('gh-branch').value.trim()||'main';
  const msg=document.getElementById('gh-modal-msg');
  if(!pat||!owner||!repo){msg.textContent='All fields required.';msg.className='gh-modal-msg err';return;}
  msg.textContent='Testing…';msg.className='gh-modal-msg';
  GHSync.saveCreds({pat,owner,repo,branch});
  const r=await GHSync.testConnection();
  if(r.ok){msg.textContent=r.msg;msg.className='gh-modal-msg ok';document.getElementById('gh-disconnect-btn').style.display='inline-flex';updateSyncBadge('connected');setTimeout(closeGHModal,1200);}
  else{msg.textContent=r.msg;msg.className='gh-modal-msg err';GHSync.saveCreds(null);}
}
function disconnectGH(){
  GHSync.saveCreds(null);
  ['gh-pat','gh-owner','gh-repo','gh-config-str'].forEach(id=>{const el=document.getElementById(id);if(el)el.value='';});
  document.getElementById('gh-branch').value='';
  document.getElementById('gh-disconnect-btn').style.display='none';
  updateSyncBadge('disconnected');closeGHModal();
}
function copyGHConfig(){
  const cfg=GHSync.exportConfig();const msg=document.getElementById('gh-modal-msg');
  if(!cfg){msg.textContent='Connect first to copy config.';msg.className='gh-modal-msg err';return;}
  navigator.clipboard.writeText(cfg).then(()=>{msg.textContent='Copied! Paste this on your other device.';msg.className='gh-modal-msg ok';setTimeout(()=>{msg.textContent='';},3000);});
}
function importGHConfig(){
  const str=(document.getElementById('gh-config-str').value||'').trim();
  const msg=document.getElementById('gh-modal-msg');
  const c=GHSync.importConfig(str);
  if(!c){msg.textContent='Invalid config string.';msg.className='gh-modal-msg err';return;}
  document.getElementById('gh-pat').value=c.pat||'';
  document.getElementById('gh-owner').value=c.owner||'';
  document.getElementById('gh-repo').value=c.repo||'';
  document.getElementById('gh-branch').value=c.branch||'main';
  msg.textContent='Imported — click Test & Save to connect.';msg.className='gh-modal-msg ok';
}
'''

ANCHOR_BROADCAST = 'function broadcastStatus(){'
ANCHOR_BRANCH    = '<div class="gh-field"><label>Branch</label>'
ANCHOR_ACTIONS   = '    <div class="gh-modal-actions">'

def process(path):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    changed = False

    # 1. Add transfer UI after Branch field (before gh-modal-actions)
    if 'gh-config-str' not in html:
        html = html.replace(
            ANCHOR_ACTIONS,
            TRANSFER_HTML + '\n' + ANCHOR_ACTIONS
        )
        changed = True
        print(f'  + transfer UI')

    # 2. Add modal functions before broadcastStatus()
    if 'function updateSyncBadge' not in html:
        html = html.replace(
            ANCHOR_BROADCAST,
            MODAL_FUNCTIONS + ANCHOR_BROADCAST
        )
        changed = True
        print(f'  + modal functions')

    if changed:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
    else:
        print(f'  (already up to date)')

for course in sorted(os.listdir(COURSES_DIR)):
    idx = os.path.join(COURSES_DIR, course, 'index.html')
    if os.path.isfile(idx):
        print(f'\n{course}:')
        process(idx)

print('\nDone.')
