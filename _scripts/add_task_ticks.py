#!/usr/bin/env python3
"""
Add per-task tick checkboxes + per-day progress bar to all 6 courses.

Changes:
1. CSS: replace task-bullet with task-tick; add task.done style; add task-progress bar
2. State: add tasksDone:{} field
3. renderTask: tick checkbox with onclick="tickTask(di,ti)"
4. New tickTask() function: toggle tick, auto-complete day when all done
5. renderSchedule: progress bar above task list; pass (t,j) indices; complete-btn reflects tick state
"""
import os, re

BASE = '/home/ht/Documents/GitHub_HT/certified-journeys.github.io/courses'
ALL_COURSES = ['pspo-certified', 'aws-ml-certified', 'terraform-certified', 'powerbi-certified',
               'dlt-certified', 'polars-certified']

# ── CSS ──────────────────────────────────────────────────────────────────────

OLD_TASK_BULLET_CSS = (
    '.task-bullet{width:5px;height:5px;border-radius:50%;background:var(--green);flex-shrink:0;margin-top:6px;}'
)

NEW_TASK_TICK_CSS = (
    '.task-tick{width:16px;height:16px;border-radius:4px;border:1.5px solid var(--border2);'
    'flex-shrink:0;cursor:pointer;display:flex;align-items:center;justify-content:center;'
    'transition:all .15s;margin-top:2px;background:none;padding:0;}'
    '.task-tick:hover{border-color:var(--green);}'
    '.task-tick.ticked{background:var(--green);border-color:var(--green);}'
    '.task-tick.ticked::after{content:"✓";font-size:10px;color:#fff;font-weight:700;line-height:1;}'
    '.task.task-done>span{text-decoration:line-through;color:var(--text3);}'
    '.task-progress{height:3px;border-radius:99px;background:var(--surface2);margin-bottom:8px;overflow:hidden;}'
    '.task-progress-fill{height:100%;background:var(--green);border-radius:99px;transition:width .3s;}'
)

# ── State ─────────────────────────────────────────────────────────────────────

OLD_STATE = (
    "let state={completed:[],scores:{},hours:{},completedAt:{},openDay:null,"
    "startDate:null,lastActivity:null,status:'not_started'};"
)
NEW_STATE = (
    "let state={completed:[],scores:{},hours:{},completedAt:{},tasksDone:{},"
    "openDay:null,startDate:null,lastActivity:null,status:'not_started'};"
)

# ── renderTask ────────────────────────────────────────────────────────────────

OLD_RENDER_TASK = (
    "function renderTask(t){if(typeof t==='string')return`<div class=\"task\">"
    "<div class=\"task-bullet\"></div><span>${t}</span></div>`;"
    "return`<div class=\"task\"><div class=\"task-bullet\"></div>"
    "<span>${t.text}</span>${t.url?`<a class=\"task-link\" href=\"${t.url}\" target=\"_blank\" rel=\"noopener\">↗</a>`:''}</div>`;}"
)

NEW_RENDER_TASK = (
    "function renderTask(t,di,ti){"
    "const done=(state.tasksDone[di]||[]).includes(ti);"
    "const text=typeof t==='string'?t:t.text;"
    "const link=(typeof t==='object'&&t.url)?`<a class=\"task-link\" href=\"${t.url}\" target=\"_blank\" rel=\"noopener\">↗</a>`:'';"
    "return`<div class=\"task${done?' task-done':''}\">"
    "<button class=\"task-tick${done?' ticked':''}\" onclick=\"event.stopPropagation();tickTask(${di},${ti})\"></button>"
    "<span>${text}</span>${link}</div>`;}"
)

# ── tickTask function (insert after renderTask) ───────────────────────────────

TICK_TASK_FN = """
function tickTask(di,ti){
  const arr=state.tasksDone[di]||(state.tasksDone[di]=[]);
  const idx=arr.indexOf(ti);
  if(idx===-1)arr.push(ti);else arr.splice(idx,1);
  const total=days[di].tasks.length;
  const done=arr.length;
  if(done===total&&!isCompleted(di)){toggleComplete(di);return;}
  if(done<total&&isCompleted(di)){state.completed=state.completed.filter(x=>x!==di);delete state.completedAt[di];}
  saveState();renderSchedule();
}"""

AFTER_RENDER_TASK = (
    "function renderRes(r){"
)

# ── task-list in renderSchedule ───────────────────────────────────────────────

OLD_TASK_LIST = (
    '        <div class="task-list">${d.tasks.map(renderTask).join(\'\')}</div>'
)
NEW_TASK_LIST = (
    '        ${(()=>{const tot=d.tasks.length;const done=(state.tasksDone[i]||[]).length;'
    'return tot?`<div class="task-progress"><div class="task-progress-fill" style="width:${Math.round(done/tot*100)}%"></div></div>`:\'\'})()}'
    '\n        <div class="task-list">${d.tasks.map((t,j)=>renderTask(t,i,j)).join(\'\')}</div>'
)

# ── complete-btn text ─────────────────────────────────────────────────────────
# No text change needed — "Mark as complete" / "✓ Completed" stays as-is.
# The button auto-completes via tickTask when all tasks are ticked.


def process(course_id):
    path = os.path.join(BASE, course_id, 'index.html')
    with open(path, encoding='utf-8') as f:
        html = f.read()

    log = []

    # 1. CSS: task-bullet → task-tick + progress bar
    if OLD_TASK_BULLET_CSS in html:
        html = html.replace(OLD_TASK_BULLET_CSS, NEW_TASK_TICK_CSS)
        log.append('replaced task-bullet CSS with task-tick + progress bar')

    # 2. State: add tasksDone
    if OLD_STATE in html:
        html = html.replace(OLD_STATE, NEW_STATE)
        log.append('added tasksDone to state')

    # 3. renderTask: use tick buttons
    if OLD_RENDER_TASK in html:
        html = html.replace(OLD_RENDER_TASK, NEW_RENDER_TASK)
        log.append('updated renderTask')

    # 4. tickTask function (insert before renderRes)
    if 'function tickTask' not in html and AFTER_RENDER_TASK in html:
        html = html.replace(AFTER_RENDER_TASK, TICK_TASK_FN + '\n' + AFTER_RENDER_TASK)
        log.append('added tickTask function')

    # 5. task-list: add progress bar + pass indices
    if OLD_TASK_LIST in html:
        html = html.replace(OLD_TASK_LIST, NEW_TASK_LIST)
        log.append('added progress bar + index args to task-list')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'✓ {course_id}: {", ".join(log) if log else "already up to date"}')


for c in ALL_COURSES:
    process(c)

print('\nDone.')
