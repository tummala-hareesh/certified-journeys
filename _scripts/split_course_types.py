#!/usr/bin/env python3
"""
Split courses into two types:
  NOTEBOOK courses (dlt, polars): keep notebook + Colab buttons — no change
  STANDARD courses (pspo, aws-ml, terraform, powerbi):
    - Remove const NOTEBOOKS=[...] block
    - Replace nb-row (notebook + Colab buttons) with a per-day notes textarea
    - Replace nb CSS with notes CSS
    - Add saveNote / getNote JS helpers
    - Create notes/ directory with template day-XX.md files
"""
import re, os

BASE = '/home/ht/Documents/GitHub_HT/certified-journeys.github.io/courses'

NOTEBOOK_COURSES = {'dlt-certified', 'polars-certified'}

STANDARD_COURSES = {
    'pspo-certified':      14,
    'aws-ml-certified':    21,
    'terraform-certified': 14,
    'powerbi-certified':   14,
}

# ── CSS: replace notebook block with notes block ────────────────────────────
OLD_NB_CSS = (
    '/* Notebook links */\n'
    '.nb-row{display:flex;gap:8px;margin-bottom:10px;flex-wrap:wrap;}\n'
    '.nb-btn{font-size:12px;padding:6px 14px;border-radius:99px;border:.5px solid var(--border2);color:var(--text2);background:none;text-decoration:none;display:inline-flex;align-items:center;gap:5px;transition:all .15s;font-family:inherit;}\n'
    '.nb-btn:hover{background:var(--surface2);color:var(--text);text-decoration:none;}\n'
    '.nb-btn-colab{background:#F9AB00;border-color:#F9AB00;color:#000;}\n'
    '.nb-btn-colab:hover{background:#e09900;color:#000;text-decoration:none;}'
)
NEW_NOTES_CSS = (
    '/* Day notes */\n'
    '.notes-wrap{margin-bottom:10px;}\n'
    '.notes-label{font-size:11px;color:var(--text3);margin-bottom:4px;display:block;}\n'
    '.notes-area{width:100%;min-height:72px;font-size:12px;padding:8px 10px;border:.5px solid var(--border2);border-radius:var(--radius-sm);background:var(--surface);color:var(--text);font-family:\'DM Mono\',monospace;resize:vertical;line-height:1.5;transition:border-color .15s;}\n'
    '.notes-area:focus{outline:none;border-color:var(--blue);}'
)

# ── JS helpers to add (after logHours function) ─────────────────────────────
AFTER_LOG_HOURS = "function logHours(i,val){const v=parseFloat(val);if(!isNaN(v)&&v>=0){state.hours[i]=v;saveState();updateStats();}}"
NOTES_JS = (
    "\nfunction saveNote(i,v){const k=STORAGE_KEY+'_note_'+i;"
    "try{v.trim()?localStorage.setItem(k,v):localStorage.removeItem(k);}catch(e){}}"
    "\nfunction getNote(i){try{const v=localStorage.getItem(STORAGE_KEY+'_note_'+i);"
    "return v?(v+'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'):'';}catch(e){return '';}}"
)

# ── renderSchedule: replace nb-row with notes-wrap ──────────────────────────
NB_ROW_PATTERN = re.compile(
    r'<div class="nb-row">.*?</div>',
    re.DOTALL
)
NOTES_ROW_TEMPLATE = (
    '<div class="notes-wrap">'
    '<label class="notes-label">📝 Day notes</label>'
    '<textarea class="notes-area" placeholder="Your notes for today…" '
    'oninput="saveNote(${i},this.value)">${getNote(i)}</textarea>'
    '</div>'
)

# ── Notes file template ──────────────────────────────────────────────────────
def notes_template(course_title, day_num, day_title):
    return f"# Day {day_num}: {day_title}\n\n## Notes\n\n_Add your notes here._\n\n## Key takeaways\n\n- \n\n## Questions to follow up\n\n- \n"


def process_standard_course(course_id, total_days):
    path = os.path.join(BASE, course_id, 'index.html')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Remove const NOTEBOOKS=[...]; block (may span multiple lines)
    content = re.sub(
        r'const NOTEBOOKS=\[[\s\S]*?\];\n?',
        '',
        content,
        count=1
    )

    # 2. Replace notebook CSS with notes CSS
    if OLD_NB_CSS in content:
        content = content.replace(OLD_NB_CSS, NEW_NOTES_CSS)

    # 3. Replace nb-row with notes-wrap in renderSchedule
    if NB_ROW_PATTERN.search(content):
        content = NB_ROW_PATTERN.sub(NOTES_ROW_TEMPLATE, content, count=1)

    # 4. Add saveNote / getNote JS helpers
    if 'function saveNote' not in content and AFTER_LOG_HOURS in content:
        content = content.replace(AFTER_LOG_HOURS, AFTER_LOG_HOURS + NOTES_JS)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'✓ {course_id} — HTML updated')

    # 5. Create notes/ directory and template files
    notes_dir = os.path.join(BASE, course_id, 'notes')
    os.makedirs(notes_dir, exist_ok=True)

    # Extract day titles from the days JSON for the template headers
    # (simple approach: use generic titles if extraction fails)
    day_titles = {}
    try:
        pos = content.index('const days=') + len('const days=')
        depth = 0
        end = pos
        for i, c in enumerate(content[pos:]):
            if c == '[': depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    end = pos + i + 1
                    break
        import json
        days = json.loads(content[pos:end])
        day_titles = {i: d['title'] for i, d in enumerate(days)}
    except Exception:
        pass

    created = 0
    for n in range(1, total_days + 1):
        fname = os.path.join(notes_dir, f'day-{n:02d}.md')
        if not os.path.exists(fname):
            title = day_titles.get(n - 1, f'Day {n}')
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(notes_template(course_id, n, title))
            created += 1

    print(f'  → notes/ directory: {created} template files created')


for course_id, total_days in STANDARD_COURSES.items():
    process_standard_course(course_id, total_days)

print('\nNotebook courses (dlt, polars) — unchanged.')
print('Done.')
