#!/usr/bin/env python3
"""
Add notes_by_day.md link to every day card in all 7 courses.

Category 1 — notebook (dlt, polars):
  nb-row already has notebook + Colab buttons → append notes link to that row

Category 2 — standard (pspo, aws-ml, terraform, powerbi):
  no existing action row → add nb-row CSS + insert nb-row with notes link only

Both: create notes/day-NN.md template files.
"""
import os, re, json, shutil

BASE = '/home/ht/Documents/GitHub_HT/certified-journeys.github.io/courses'

NOTEBOOK_COURSES = ['dlt-certified', 'polars-certified']
STANDARD_COURSES = ['pspo-certified', 'aws-ml-certified', 'terraform-certified', 'powerbi-certified']

NOTES_LINK = (
    '<a class="nb-btn" href="notes/day-${String(i+1).padStart(2,\'0\')}.md" '
    'target="_blank">📝 notes_by_day.md</a>'
)

# CSS to add to standard courses (they lost nb-row/nb-btn when notes was removed)
NB_CSS_BLOCK = (
    '/* Action row */\n'
    '.nb-row{display:flex;gap:8px;margin-bottom:10px;flex-wrap:wrap;}\n'
    '.nb-btn{font-size:12px;padding:6px 14px;border-radius:99px;border:.5px solid var(--border2);'
    'color:var(--text2);background:none;text-decoration:none;display:inline-flex;align-items:center;'
    'gap:5px;transition:all .15s;font-family:inherit;}\n'
    '.nb-btn:hover{background:var(--surface2);color:var(--text);text-decoration:none;}'
)

# Anchor after which we insert the CSS in standard courses
AFTER_DAY_BODY_CSS = (
    '.day-card.open .day-body{display:block;}'
)

# The blank line inside day-body left after notes removal (standard courses)
OLD_DAY_BODY_OPEN = '      <div class="day-body">\n        \n        <div class="tip-box">'
NEW_DAY_BODY_OPEN = (
    '      <div class="day-body">\n'
    f'<div class="nb-row">{NOTES_LINK}</div>\n'
    '        <div class="tip-box">'
)

# Notebook courses: append notes link before closing </div> of nb-row in renderSchedule
# Match end of Colab button inside the JS template string
COLAB_END = 'target="_blank">▶ Open in Colab</a></div>'
COLAB_END_WITH_NOTES = f'target="_blank">▶ Open in Colab</a>{NOTES_LINK}</div>'

NOTES_TEMPLATE = """\
# Day {day}: {title}

## Notes

_Your notes for today._

## Key takeaways

-

## Questions

-
"""


def extract_days(html):
    """Extract days list from const days=[...] in the HTML."""
    pos = html.index('const days=') + len('const days=')
    depth = 0
    end = pos
    for i, c in enumerate(html[pos:]):
        if c == '[':   depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                end = pos + i + 1
                break
    return json.loads(html[pos:end])


def make_notes_files(course_id, days_list):
    notes_dir = os.path.join(BASE, course_id, 'notes')
    os.makedirs(notes_dir, exist_ok=True)
    created = 0
    for i, d in enumerate(days_list):
        path = os.path.join(notes_dir, f'day-{i+1:02d}.md')
        if not os.path.exists(path):
            title = d['title'] if isinstance(d, dict) else str(d)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(NOTES_TEMPLATE.format(day=i+1, title=title))
            created += 1
    return created


# ── Standard courses ─────────────────────────────────────────────────────────
for course_id in STANDARD_COURSES:
    path = os.path.join(BASE, course_id, 'index.html')
    with open(path, encoding='utf-8') as f:
        html = f.read()

    log = []

    # Add nb-row / nb-btn CSS if absent
    if '.nb-row' not in html and AFTER_DAY_BODY_CSS in html:
        html = html.replace(AFTER_DAY_BODY_CSS,
                            AFTER_DAY_BODY_CSS + '\n' + NB_CSS_BLOCK)
        log.append('added nb CSS')

    # Insert notes link into day body
    if 'notes_by_day.md' not in html and OLD_DAY_BODY_OPEN in html:
        html = html.replace(OLD_DAY_BODY_OPEN, NEW_DAY_BODY_OPEN)
        log.append('inserted notes link')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

    # Create notes files
    days_list = extract_days(html)
    n = make_notes_files(course_id, days_list)
    log.append(f'created {n} notes files')
    print(f'✓ {course_id}: {", ".join(log)}')


# ── Notebook courses ──────────────────────────────────────────────────────────
for course_id in NOTEBOOK_COURSES:
    path = os.path.join(BASE, course_id, 'index.html')
    with open(path, encoding='utf-8') as f:
        html = f.read()

    log = []

    # Append notes link to the Colab button row
    if 'notes_by_day.md' not in html and COLAB_END in html:
        html = html.replace(COLAB_END, COLAB_END_WITH_NOTES, 1)
        log.append('appended notes link to nb-row')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

    days_list = extract_days(html)
    n = make_notes_files(course_id, days_list)
    log.append(f'created {n} notes files')
    print(f'✓ {course_id}: {", ".join(log)}')

print('\nDone.')
