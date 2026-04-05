#!/usr/bin/env python3
"""
Three changes across all standard courses (pspo, aws-ml, terraform, powerbi):

1. Remove notes completely from Daily Plan:
   - notes CSS block
   - saveNote / getNote JS functions
   - notes-wrap div in renderSchedule

2. Connect Topics ↔ Daily Plan:
   - Daily Plan: add topic pills to each open day card (below tip-box)
   - Topics tab: add clickable day-number buttons under each topic's bar

3. Delete static notes/ directories.
   Delete the unused add_pat_sync.py script.
"""
import re, os, shutil, glob

BASE  = '/home/ht/Documents/GitHub_HT/certified-journeys.github.io/courses'
SCRIPTS = '/home/ht/Documents/GitHub_HT/certified-journeys.github.io/_scripts'

STANDARD = ['pspo-certified', 'aws-ml-certified', 'terraform-certified', 'powerbi-certified']

# ── strings to REMOVE ─────────────────────────────────────────────────────────

NOTES_CSS = """\
/* Day notes */
.notes-wrap{margin-bottom:10px;}
.notes-label{font-size:11px;color:var(--text3);margin-bottom:4px;display:block;}
.notes-area{width:100%;min-height:72px;font-size:12px;padding:8px 10px;border:.5px solid var(--border2);border-radius:var(--radius-sm);background:var(--surface);color:var(--text);font-family:'DM Mono',monospace;resize:vertical;line-height:1.5;transition:border-color .15s;}
.notes-area:focus{outline:none;border-color:var(--blue);}"""

NOTES_JS = (
    "\nfunction saveNote(i,v){const k=STORAGE_KEY+'_note_'+i;"
    "try{v.trim()?localStorage.setItem(k,v):localStorage.removeItem(k);}catch(e){}}"
    "\nfunction getNote(i){try{const v=localStorage.getItem(STORAGE_KEY+'_note_'+i);"
    "return v?(v+'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'):'';}catch(e){return '';}}"
)

NOTES_ROW = (
    '<div class="notes-wrap"><label class="notes-label">📝 Day notes</label>'
    '<textarea class="notes-area" placeholder="Your notes for today…" '
    'oninput="saveNote(${i},this.value)">${getNote(i)}</textarea></div>'
)

# ── strings to ADD ────────────────────────────────────────────────────────────

# CSS: topic pills on day cards + day-number buttons in topics tab
TOPIC_CONNECT_CSS = """\
/* Topic ↔ Day connections */
.day-topic-pills{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:10px;}
.day-topic-pill{font-size:10px;padding:2px 9px;border-radius:99px;border:.5px solid;font-weight:500;cursor:pointer;transition:opacity .15s;white-space:nowrap;}
.day-topic-pill:hover{opacity:.7;}
.topic-days{display:flex;flex-wrap:wrap;gap:5px;margin-top:8px;}
.topic-day-btn{font-size:11px;padding:2px 8px;border-radius:99px;border:.5px solid var(--border2);background:var(--surface2);color:var(--text2);cursor:pointer;font-family:'DM Mono',monospace;transition:all .15s;}
.topic-day-btn:hover{background:var(--surface3);color:var(--text);}
.topic-day-btn.done{background:var(--green-light);color:var(--green-dark);border-color:var(--green);}"""

# Add CSS after the last .t-pct rule
AFTER_T_PCT = '.t-pct{font-size:11px;color:var(--text3);font-family:\'DM Mono\',monospace;}'

# JS: reverse-index and helper (insert after badgeLabel)
AFTER_BADGE_LABEL = "function badgeLabel(b){return{learn:'Learn',practice:'Practice',review:'Review',exam:'Exam'}[b];}"

TOPIC_INDEX_JS = """
// Topic ↔ Day reverse index
const dayTopics=(()=>{const m={};topics.forEach(t=>t.days.forEach(d=>{(m[d]=m[d]||[]).push(t);}));return m;})();
function goToDay(i){
  showPanel('schedule',document.querySelector('.tab'));
  setTimeout(()=>{
    state.openDay=i;saveState();renderSchedule();
    const el=document.querySelector('.day-card:nth-child('+(i+1)+')');
    if(el)el.scrollIntoView({behavior:'smooth',block:'start'});
  },50);
}"""

# renderSchedule: add topic pills in day body, after tip-box
OLD_TIP_THEN_TASKS = (
    '        <div class="tip-box"><p><strong>💡 Tip:</strong> ${d.tip}</p></div>\n'
    '        <div class="task-list">${d.tasks.map(renderTask).join(\'\')}</div>'
)
NEW_TIP_THEN_TASKS = (
    '        <div class="tip-box"><p><strong>💡 Tip:</strong> ${d.tip}</p></div>\n'
    '        ${(dayTopics[i]||[]).length?`<div class="day-topic-pills">${(dayTopics[i]||[]).map(t=>`<span class="day-topic-pill" style="background:${t.color}18;color:${t.color};border-color:${t.color}40" onclick="event.stopPropagation();showPanel(\'topics\',document.querySelectorAll(\'.tab\')[1])" title="View topic in Topics tab">${t.name}</span>`).join(\'\')}</div>`:\'\'}\n'
    '        <div class="task-list">${d.tasks.map(renderTask).join(\'\')}</div>'
)

# renderTopics: add clickable day buttons under each topic's bar
OLD_RENDER_TOPICS = (
    "      return `<div class=\"topic-card\"><h4>${t.name}</h4>"
    "<div class=\"t-bar-bg\"><div class=\"t-bar-fill\" style=\"width:${pct}%;background:${t.color}\"></div></div>"
    "<div class=\"t-pct\">${pct}% covered · ${cov}/${t.days.length} sessions</div></div>`;"
)
NEW_RENDER_TOPICS = (
    "      const dayBtns=t.days.map(d=>`<button class=\"topic-day-btn${state.completed.includes(d)?' done':''}\" onclick=\"goToDay(${d})\">Day ${d+1}</button>`).join('');\n"
    "      return `<div class=\"topic-card\"><h4>${t.name}</h4>"
    "<div class=\"t-bar-bg\"><div class=\"t-bar-fill\" style=\"width:${pct}%;background:${t.color}\"></div></div>"
    "<div class=\"t-pct\">${pct}% covered · ${cov}/${t.days.length} sessions</div>"
    "<div class=\"topic-days\">${dayBtns}</div></div>`;"
)


def process(course_id):
    path = os.path.join(BASE, course_id, 'index.html')
    with open(path, encoding='utf-8') as f:
        html = f.read()

    log = []

    # ── 1. Remove notes ──────────────────────────────────────────────────────
    if NOTES_CSS in html:
        html = html.replace(NOTES_CSS, '')
        log.append('removed notes CSS')

    if NOTES_JS in html:
        html = html.replace(NOTES_JS, '')
        log.append('removed notes JS')

    if NOTES_ROW in html:
        html = html.replace(NOTES_ROW, '')
        log.append('removed notes row')

    # ── 2. Add topic connection CSS ──────────────────────────────────────────
    if 'day-topic-pills' not in html and AFTER_T_PCT in html:
        html = html.replace(AFTER_T_PCT, AFTER_T_PCT + '\n' + TOPIC_CONNECT_CSS)
        log.append('added topic-connect CSS')

    # ── 3. Add JS reverse index + goToDay ───────────────────────────────────
    if 'dayTopics' not in html and AFTER_BADGE_LABEL in html:
        html = html.replace(AFTER_BADGE_LABEL, AFTER_BADGE_LABEL + TOPIC_INDEX_JS)
        log.append('added dayTopics JS')

    # ── 4. renderSchedule: topic pills in day body ───────────────────────────
    if 'day-topic-pills' not in html or OLD_TIP_THEN_TASKS in html:
        if OLD_TIP_THEN_TASKS in html:
            html = html.replace(OLD_TIP_THEN_TASKS, NEW_TIP_THEN_TASKS)
            log.append('added topic pills to day cards')

    # ── 5. renderTopics: clickable day buttons ───────────────────────────────
    if 'topic-day-btn' not in html and OLD_RENDER_TOPICS in html:
        html = html.replace(OLD_RENDER_TOPICS, NEW_RENDER_TOPICS)
        log.append('added day buttons to topics')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'✓ {course_id}: {", ".join(log)}')

    # ── 6. Delete notes/ directory ───────────────────────────────────────────
    notes_dir = os.path.join(BASE, course_id, 'notes')
    if os.path.isdir(notes_dir):
        shutil.rmtree(notes_dir)
        print(f'  → deleted notes/')


# Run on all standard courses
for c in STANDARD:
    process(c)

# Also apply topic connection to notebook courses (dlt, polars) —
# they don't have notes but benefit from the topics connection too
print()
for c in ['dlt-certified', 'polars-certified']:
    path = os.path.join(BASE, c, 'index.html')
    with open(path, encoding='utf-8') as f:
        html = f.read()
    log = []

    if 'day-topic-pills' not in html and AFTER_T_PCT in html:
        html = html.replace(AFTER_T_PCT, AFTER_T_PCT + '\n' + TOPIC_CONNECT_CSS)
        log.append('topic-connect CSS')

    if 'dayTopics' not in html and AFTER_BADGE_LABEL in html:
        html = html.replace(AFTER_BADGE_LABEL, AFTER_BADGE_LABEL + TOPIC_INDEX_JS)
        log.append('dayTopics JS')

    if OLD_TIP_THEN_TASKS in html:
        html = html.replace(OLD_TIP_THEN_TASKS, NEW_TIP_THEN_TASKS)
        log.append('topic pills in day cards')

    if 'topic-day-btn' not in html and OLD_RENDER_TOPICS in html:
        html = html.replace(OLD_RENDER_TOPICS, NEW_RENDER_TOPICS)
        log.append('day buttons in topics')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'✓ {c}: {", ".join(log) if log else "already up to date"}')

# Delete the unused PAT sync script
pat_script = os.path.join(SCRIPTS, 'add_pat_sync.py')
if os.path.exists(pat_script):
    os.remove(pat_script)
    print(f'\nDeleted _scripts/add_pat_sync.py')

print('\nDone.')
