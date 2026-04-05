# certified-journeys · New Course Generation Prompt

Copy this entire prompt into Claude (or any capable LLM). Fill in the `[COURSE INPUT]` section at the top, then send.

Courses come in **two types** — set `COURSE_TYPE` accordingly:

| Type | Use when | Day-card action | Output B |
|------|----------|-----------------|---------|
| `notebook` | Hands-on technical (Python, data engineering, ML) | 📓 Notebook + Colab buttons | Jupyter `.ipynb` per day |
| `standard` | Certification prep, theory-heavy (Scrum, cloud certs, BI) | 📝 Per-day notes textarea | `notes/day-NN.md` templates |

---

## [COURSE INPUT] — Fill this in before sending

```
COURSE_TYPE:      notebook | standard
COURSE_ID:        e.g. kafka-certified, cka-certified
COURSE_FULL_NAME: e.g. Apache Kafka Streams Developer
ICON:             2-letter abbreviation, e.g. KF
ACCENT_COLOR:     hex, e.g. #E8890C
ACCENT_LIGHT:     light version, e.g. #FEF3E2
ACCENT_DARK:      darkened version, e.g. #A05A00
ACCENT_DARK_DIM:  dark-mode tinted bg, e.g. #2A1500
PROVIDER:         e.g. Confluent, HashiCorp, Google, Self-paced
COST:             e.g. $150, Free
TOTAL_DAYS:       integer, typically 10–21
DIFFICULTY:       Beginner / Intermediate / Advanced
TAGS:             comma-separated, e.g. Streaming, Java, Kafka
EXAM_LINK:        official exam/cert page URL
EXAM_QUESTIONS:   integer or null
EXAM_MINUTES:     integer or null
EXAM_PASS_SCORE:  e.g. 70%, N/A if no formal exam
EXAM_NOTES:       free text about the exam format

DAYS:
  One entry per day —
  Day N | Title | Badge (learn/practice/review/exam) | Tasks (bullet list) | Resources (bullet list with URLs where known) | Tip | hasScore (true/false)

  For tasks and resources, mark primary reading/reference links with [URL]:
    - Read the official docs [https://docs.example.com]
    - Plain text task (no link)

TOPICS:
  4–8 topic groups, each with:
  Name | Accent color (hex) | Day indices (0-based, comma-separated)
```

---

## Prompt (send everything below this line)

---

You are generating a new certified-journeys course. I will give you course metadata and day-by-day content. You will produce:

- **Always** — Output A: `courses/[COURSE_ID]/index.html`
- **If `notebook` type** — Output B: `courses/[COURSE_ID]/notebooks/day-NN-slug.ipynb` per day
- **If `standard` type** — Output B: `courses/[COURSE_ID]/notes/day-NN.md` per day

Follow every spec exactly. Do not add features not described. Produce the full files.

---

## COURSE METADATA

```
[paste your filled-in [COURSE INPUT] block here]
```

---

## OUTPUT A SPEC — `index.html` tracker

### File structure

Single self-contained HTML file. No external JS, no build tools, no npm. Google Fonts only.

### Head

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>[COURSE_FULL_NAME] · certified-journeys</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>/* all CSS inline */</style>
</head>
```

### CSS variables (required — copy exactly, only change accent vars)

```css
:root {
  --green:[ACCENT_COLOR]; --green-light:[ACCENT_LIGHT]; --green-dark:[ACCENT_DARK];
  --blue:#378ADD; --blue-light:#EAF3FD; --blue-dark:#185FA5;
  --amber:#BA7517; --amber-light:#FDF3E3;
  --coral:#D85A30; --coral-light:#FAEDE8; --coral-dark:#993C1D;
  --purple:#7F77DD; --purple-light:#EEEDFE;
  --orange:#E8890C; --orange-light:#FEF3E2;
  --teal:#0891B2; --teal-light:#E0F5FA;
  --bg:#F5F4F0; --surface:#FFFFFF; --surface2:#EEECE5; --surface3:#E8E6DF;
  --border:rgba(0,0,0,0.08); --border2:rgba(0,0,0,0.16);
  --text:#18181A; --text2:#52524E; --text3:#8C8B85;
  --radius:14px; --radius-sm:9px; --radius-xs:5px;
  --shadow:0 1px 3px rgba(0,0,0,0.08),0 4px 16px rgba(0,0,0,0.04);
  --shadow-md:0 4px 12px rgba(0,0,0,0.1),0 1px 3px rgba(0,0,0,0.06);
}
@media(prefers-color-scheme:dark){:root{
  --bg:#111113; --surface:#1C1C1F; --surface2:#252528; --surface3:#2E2E33;
  --border:rgba(255,255,255,0.08); --border2:rgba(255,255,255,0.15);
  --text:#F0EFEA; --text2:#A09F9B; --text3:#5E5D58;
  --green-light:[ACCENT_DARK_DIM];
  --blue-light:#061E38; --amber-light:#221900;
  --coral-light:#2A0E05; --purple-light:#161440;
  --orange-light:#1F1200; --teal-light:#021E26;
}}
```

### Day-card action row CSS — choose one based on COURSE_TYPE

**If `notebook`:**
```css
/* Notebook links */
.nb-row{display:flex;gap:8px;margin-bottom:10px;flex-wrap:wrap;}
.nb-btn{font-size:12px;padding:6px 14px;border-radius:99px;border:.5px solid var(--border2);color:var(--text2);background:none;text-decoration:none;display:inline-flex;align-items:center;gap:5px;transition:all .15s;font-family:inherit;}
.nb-btn:hover{background:var(--surface2);color:var(--text);text-decoration:none;}
.nb-btn-colab{background:#F9AB00;border-color:#F9AB00;color:#000;}
.nb-btn-colab:hover{background:#e09900;color:#000;text-decoration:none;}
```

**If `standard`:**
```css
/* Day notes */
.notes-wrap{margin-bottom:10px;}
.notes-label{font-size:11px;color:var(--text3);margin-bottom:4px;display:block;}
.notes-area{width:100%;min-height:72px;font-size:12px;padding:8px 10px;border:.5px solid var(--border2);border-radius:var(--radius-sm);background:var(--surface);color:var(--text);font-family:'DM Mono',monospace;resize:vertical;line-height:1.5;transition:border-color .15s;}
.notes-area:focus{outline:none;border-color:var(--blue);}
```

### Linked task and resource CSS (required for both types)

```css
/* Linked resources & tasks */
a.res-pill{text-decoration:none;cursor:pointer;}
a.res-pill:hover{background:var(--surface3);border-color:var(--border2);color:var(--text);}
.task-link{color:var(--blue-dark);font-size:11px;margin-left:6px;flex-shrink:0;opacity:0.7;line-height:1.5;}
.task-link:hover{opacity:1;text-decoration:none;}
```

### All other required CSS classes

Layout: `.app`, `.breadcrumb`, `.breadcrumb-sep`  
Hero: `.course-hero`, `.course-hero-top`, `.course-icon-wrap`, `.course-icon`, `.course-title-block`, `.tag-row`, `.tag`, `.hero-meta`, `.meta-item`, `.meta-label`, `.meta-val`  
Progress: `.prog-strip`, `.prog-strip-top`, `.prog-label`, `.prog-pct`, `.bar-bg`, `.bar-fill`, `.readiness` (+ `.early`, `.close`, `.ready`), `.stats-grid`, `.stat`, `.stat-label`, `.stat-val` (+ `.ok`, `.warn`, `.danger`)  
Tabs: `.tabs`, `.tab` (+ `.active`), `.panel` (+ `.active`)  
Day cards: `.day-card` (+ `.completed`, `.open`), `.day-header`, `.day-num`, `.day-meta`, `.day-title`, `.day-sub`, `.day-badge`, `.chevron`, `.day-body`, `.tip-box`, `.task-list`, `.task`, `.task-bullet`, `.resources-row`, `.res-pill`, `.score-row`, `.score-badge`, `.hours-row`, `.complete-btn` (+ `.done`)  
Topics: `.topic-grid`, `.topic-card`, `.t-bar-bg`, `.t-bar-fill`, `.t-pct`  
AI: `.ai-card`, `.ai-card-head`, `.ai-icon`, `.ai-card-title`, `.ai-card-sub`, `.ai-card-body`, `.ai-prompt-box`, `.ai-link-btn`  
Exam: `.exam-grid`, `.exam-card`, `.exam-card-label`, `.exam-card-val`, `.exam-card-sub`  
Resources: `.res-section`, `.res-section-title`, `.res-link-list`, `.res-link-item`, `.res-link-index`, `.res-link-body`, `.res-link-desc`  
Shared: `.info-box`, `.badge-learn`, `.badge-practice`, `.badge-review`, `.badge-exam`, `.page-footer`  
Responsive: `@media(max-width:640px)` for `.topic-grid`, `.hero-meta`, `.stats-grid`

### HTML body structure (tabs differ by COURSE_TYPE)

```html
<body>
<div class="app">

  <!-- 1. Breadcrumb -->
  <div class="breadcrumb">
    <a href="../../index.html">certified-journeys</a>
    <span class="breadcrumb-sep">›</span>
    <span>[COURSE_FULL_NAME]</span>
  </div>

  <!-- 2. Course hero (icon, title, tags, 4 meta items) -->
  <div class="course-hero"> ... </div>

  <!-- 3. Progress strip (bar, pct, readiness, stats grid) -->
  <div class="prog-strip"> ... </div>

  <!-- 4. Tabs — notebook courses have 5 tabs, standard courses have 5 tabs -->
  <!-- notebook:  📅 Daily Plan | 📚 Topics | 🤖 AI Tools | 🔗 Resources | 🎓 Exam Prep -->
  <!-- standard:  📅 Daily Plan | 📚 Topics | 🤖 AI Tools | 🔗 Resources | 🎓 Exam Prep -->
  <div class="tabs">
    <button class="tab active" onclick="showPanel('schedule',this)">📅 Daily Plan</button>
    <button class="tab" onclick="showPanel('topics',this)">📚 Topics</button>
    <button class="tab" onclick="showPanel('ai',this)">🤖 AI Tools</button>
    <button class="tab" onclick="showPanel('resources',this)">🔗 Resources</button>
    <button class="tab" onclick="showPanel('exam',this)">🎓 Exam Prep</button>
  </div>

  <!-- 5. Panels (rendered by JS) -->
  <div id="panel-schedule"  class="panel active"></div>
  <div id="panel-topics"    class="panel"></div>
  <div id="panel-ai"        class="panel"></div>
  <div id="panel-resources" class="panel"></div>
  <div id="panel-exam"      class="panel"></div>

  <!-- 6. Footer -->
  <div class="page-footer">
    Progress saved locally · <span id="sk-display">cj_[COURSE_ID]_v1</span> · No account needed · <a href="../../index.html">← All journeys</a>
  </div>

</div>
```

> Both course types use the same 5-tab layout. Notes are inline per-day for standard courses (not a separate tab).

### JavaScript — data constants

```js
const COURSE_ID   = '[COURSE_ID]';
const STORAGE_KEY = 'cj_[COURSE_ID]_v1';
const TOTAL_DAYS  = [TOTAL_DAYS];

// ── notebook type only ──────────────────────────────────────────────────────
// One slug per day, matching filenames in notebooks/
const NOTEBOOKS = [
  'day-01-slug',
  // ...
];
// ── end notebook only ───────────────────────────────────────────────────────

// Tasks and resources support plain strings OR {text, url} objects.
// Use {text, url} for any item that has a primary source link.
const days = [
  {
    title:     "string",
    badge:     "learn" | "practice" | "review" | "exam",
    sub:       "Day N · Theme",
    tasks: [
      {text: "Read the official docs", url: "https://docs.example.com"},  // ↗ link shown
      "Plain text task — no link needed",
    ],
    resources: [
      {text: "Official Docs", url: "https://docs.example.com"},  // becomes <a> pill
      "No-link resource as plain string",
    ],
    tip:      "string",
    hasScore: false,
  },
  // ...
];

const topics = [
  {name: "string", color: "#hex", days: [0, 1, 2]},
  // ...
];

const exam = {
  questions:  null | number,
  minutes:    null | number,
  passScore:  "string",
  cost:       "[COST]",
  provider:   "[PROVIDER]",
  link:       "[EXAM_LINK]",
  notes:      "string"
};
```

### JavaScript — state and functions

```js
let state = {
  completed:    [],
  scores:       {},
  hours:        {},
  completedAt:  {},
  openDay:      null,
  startDate:    null,
  lastActivity: null,
  status:       'not_started'
};
```

**Required functions — implement all:**

- `loadState()`, `saveState()`, `broadcastStatus()`, `resetAll()`
- `isCompleted(i)`, `toggleComplete(i)`, `toggleDay(i)`
- `logScore(i, val)`, `logHours(i, val)`
- `scoreClass(s)`, `badgeClass(b)`, `badgeLabel(b)`
- `renderTask(t)`, `renderRes(r)` — helpers for linked tasks/resources (see below)
- `updateStats()`
- `renderSchedule()` — day card body differs by COURSE_TYPE (see below)
- `renderTopics()`
- `renderAI()` — 3 cards: NotebookLM audio, NotebookLM flashcards, Claude prompts
- `renderExam()` — 4 stat cards + readiness checklist
- `renderResources()` — 4 sections: Core Reading, Hands-On, Ecosystem, Upgrade Path
- `showPanel(name, btn)`, `renderAll()`
- **`standard` type only:** `saveNote(i, val)`, `getNote(i)`

#### `renderTask` and `renderRes` helpers (required for both types)

```js
function renderTask(t) {
  if (typeof t === 'string')
    return `<div class="task"><div class="task-bullet"></div><span>${t}</span></div>`;
  return `<div class="task"><div class="task-bullet"></div><span>${t.text}</span>${
    t.url ? `<a class="task-link" href="${t.url}" target="_blank" rel="noopener">↗</a>` : ''
  }</div>`;
}

function renderRes(r) {
  if (typeof r === 'string')
    return `<span class="res-pill">📎 ${r}</span>`;
  return r.url
    ? `<a class="res-pill" href="${r.url}" target="_blank" rel="noopener">📎 ${r.text}</a>`
    : `<span class="res-pill">📎 ${r.text}</span>`;
}
```

#### `renderSchedule` — day card body (differs by COURSE_TYPE)

**`notebook` type** — day card body opens with notebook buttons:

```js
`<!-- action row -->
<div class="nb-row">
  <a class="nb-btn" href="notebooks/${NOTEBOOKS[i]}.ipynb" target="_blank">📓 Open notebook</a>
  <a class="nb-btn nb-btn-colab"
     href="https://colab.research.google.com/github/certified-journeys/certified-journeys.github.io/blob/main/courses/[COURSE_ID]/notebooks/${NOTEBOOKS[i]}.ipynb"
     target="_blank">▶ Open in Colab</a>
</div>
<div class="tip-box"><p><strong>💡 Tip:</strong> ${d.tip}</p></div>
<div class="task-list">${d.tasks.map(renderTask).join('')}</div>
<div class="resources-row">${d.resources.map(renderRes).join('')}</div>
<!-- score row only if d.hasScore -->
<div class="hours-row">...</div>
<button class="complete-btn ...">...</button>`
```

**`standard` type** — day card body opens with notes textarea:

```js
`<!-- action row -->
<div class="notes-wrap">
  <label class="notes-label">📝 Day notes</label>
  <textarea class="notes-area"
    placeholder="Your notes for today…"
    oninput="saveNote(${i}, this.value)">${getNote(i)}</textarea>
</div>
<div class="tip-box"><p><strong>💡 Tip:</strong> ${d.tip}</p></div>
<div class="task-list">${d.tasks.map(renderTask).join('')}</div>
<div class="resources-row">${d.resources.map(renderRes).join('')}</div>
<!-- score row only if d.hasScore -->
<div class="hours-row">...</div>
<button class="complete-btn ...">...</button>`
```

**`standard` type** — notes JS helpers:

```js
function saveNote(i, v) {
  const k = STORAGE_KEY + '_note_' + i;
  try { v.trim() ? localStorage.setItem(k, v) : localStorage.removeItem(k); } catch(e) {}
}
function getNote(i) {
  try {
    const v = localStorage.getItem(STORAGE_KEY + '_note_' + i);
    return v ? (v + '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;') : '';
  } catch(e) { return ''; }
}
```

#### `broadcastStatus` (required)

```js
function broadcastStatus() {
  const summary = {
    id: COURSE_ID, status: state.status,
    completed: state.completed.length, total: TOTAL_DAYS,
    scores: Object.values(state.scores).filter(s => s > 0),
    totalHours: Object.values(state.hours).reduce((a, b) => a + b, 0),
    completedAt: state.completedAt, startDate: state.startDate,
    lastActivity: state.lastActivity
  };
  try { localStorage.setItem('cj_summary_' + COURSE_ID, JSON.stringify(summary)); } catch(e) {}
}
```

#### `renderAI` — three cards (required content)

Card 1 — **NotebookLM Audio Podcast**: prompt for a 10-minute podcast covering key concepts, exam traps, and must-know items for [COURSE_FULL_NAME]. Link: `https://notebooklm.google.com`

Card 2 — **NotebookLM Flashcards**: prompt for 20 Q&A pairs focused on concept distinctions, misconceptions, scenario questions. Link: `https://notebooklm.google.com`

Card 3 — **Claude Deep Dive Prompts**: three prompts — (1) explain like a senior engineer, (2) exam scenario questions, (3) gap analysis study plan. All tailored to [COURSE_FULL_NAME].

#### `renderResources` — four sections (required)

- **Core Reading** — official docs, primary spec, main reference
- **Hands-On Resources** — tutorials, labs, community forums
- **Ecosystem & Tooling** — related tools, packages, integrations
- **Upgrade Path** — what to study next, follow-on certs

Each link item:
```html
<div class="res-link-item">
  <span class="res-link-index">01</span>
  <div class="res-link-body">
    <a href="URL" target="_blank">Title</a>
    <div class="res-link-desc">One-line description</div>
  </div>
</div>
```

Minimum 3 links per section (12 total).

#### `renderExam` checklist (required items)

- Completed all [TOTAL_DAYS] days of the study plan
- Scored [EXAM_PASS_SCORE] or higher on practice exams
- Can explain every Topics tab item without notes
- Written a cheat sheet from memory and verified it
- Consistent scores — not one lucky attempt

### Init (last lines of `<script>`)

```js
loadState();
renderAll();
```

---

## OUTPUT B SPEC — Secondary files (differs by COURSE_TYPE)

### If `notebook` — Jupyter notebooks

**One file per day:** `courses/[COURSE_ID]/notebooks/day-NN-slug.ipynb`

**Slug:** 1–3 word kebab-case summary of the day title.

**Format:** Valid **nbformat 4.5** JSON:

```json
{
  "nbformat": 4,
  "nbformat_minor": 5,
  "metadata": {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.10.0"},
    "colab": {"provenance": []}
  },
  "cells": [ ... ]
}
```

> **`language_info` is required.** Without it, VS Code and JupyterLab cannot identify the kernel.

Every **markdown cell:**
```json
{"cell_type": "markdown", "id": "a1b2c3d4", "metadata": {}, "source": ["line 1\n"]}
```

Every **code cell:**
```json
{"cell_type": "code", "id": "e5f6a7b8", "metadata": {}, "execution_count": null, "outputs": [], "source": ["line 1\n"]}
```

> **`id` required on every cell** (8-char hex, unique per cell). Missing ids → "error loading this notebook".  
> **`outputs` and `execution_count` required on every code cell**, even when empty/null.

**Required cell sequence:**

Cell 1 — Header (markdown):
```markdown
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/certified-journeys/certified-journeys.github.io/blob/main/courses/[COURSE_ID]/notebooks/day-NN-slug.ipynb#scrollTo=[FIRST_CELL_ID])

---
# Day N · [Day Title]
**certified-journeys / [COURSE_ID]** · [Sub label]

> **Goal for today:** [one sentence — what the learner can do by the end]
```

> **Colab URL:** repo is always `certified-journeys/certified-journeys.github.io`. Path includes full `courses/[COURSE_ID]/notebooks/` prefix. Append `#scrollTo=[FIRST_CELL_ID]`.

Cell 2 — Install (code): `%pip install -q [packages]`

Cells 3–N — For each task, an alternating triple:
1. **Concept (markdown):** one concept, comparison table where helpful, `##` heading with `Step N ·` prefix, max ~15 lines
2. **Code:** working, runnable, inline comments on non-obvious lines
3. **"What just happened?" (markdown):** 3–5 bullets, key insight in bold

Second-to-last — Challenge (code):
```python
# Challenge: [clear instruction]
# Your solution here
# [scaffold — not the full answer]
```

Last — Recap (markdown):
```markdown
---
## Day N key concepts recap
| Concept | What to remember |
|---|---|

> **Tip:** [day tip]

---
## What's next
**Day N+1** → [brief preview]

Mark Day N complete in your [tracker](../index.html).
```

**Depth requirements:**

| Badge | Min code cells | Min markdown cells | Min total lines |
|-------|---------------|-------------------|-----------------|
| `learn` | 5 | 8 | 150 |
| `practice` | 8 | 5 | 200 |
| `review` | 4 | 10 | 150 |
| `exam` (capstone) | 10 | 8 | 250 |

**Code quality rules:**
- All code must run without errors in a fresh Colab environment after the install cell
- No pseudocode, no `# TODO` stubs (except in the Challenge cell)
- Use free local alternatives for paid cloud services (DuckDB not BigQuery, JSONPlaceholder not real APIs) and document the production equivalent
- Import packages at the top of the first code cell that uses them

---

### If `standard` — Notes templates

**One file per day:** `courses/[COURSE_ID]/notes/day-NN.md`

```markdown
# Day N: [Day Title]

## Notes

_Add your notes here._

## Key takeaways

- 

## Questions to follow up

- 
```

No Jupyter notebooks are generated for standard courses.

---

## Quality checklist

### Both types
- [ ] `broadcastStatus()` writes to `cj_summary_[COURSE_ID]`
- [ ] `STORAGE_KEY` is `cj_[COURSE_ID]_v1`
- [ ] All 5 panels render without JS errors
- [ ] `renderTask(t)` and `renderRes(r)` helpers are present and used in `renderSchedule`
- [ ] All `{text, url}` objects in `tasks` and `resources` have real, working URLs
- [ ] `renderResources()` has 4 sections, 12+ links
- [ ] `renderAI()` has 3 cards with prompts tailored to this course
- [ ] Dark mode CSS variables are correct
- [ ] `.breadcrumb-sep` rule has no trailing `"`

### `notebook` type only
- [ ] `const NOTEBOOKS` array present, one slug per day
- [ ] Every day card has `.nb-row` with both notebook and Colab buttons
- [ ] Colab URL uses repo `certified-journeys/certified-journeys.github.io`
- [ ] Colab URL path is `/blob/main/courses/[COURSE_ID]/notebooks/[filename].ipynb#scrollTo=[first_cell_id]`
- [ ] `nbformat: 4`, `nbformat_minor: 5` at notebook top level
- [ ] `metadata.language_info.name` is `"python"`
- [ ] Every cell has a unique `"id"` (8-char hex)
- [ ] Every code cell has `"outputs": []` and `"execution_count": null`
- [ ] Notebook filenames match `NOTEBOOKS` array exactly
- [ ] All code cells are runnable (no pseudocode outside Challenge)
- [ ] Challenge cell has scaffold, not full solution

### `standard` type only
- [ ] No `const NOTEBOOKS` array present
- [ ] No `.nb-row` or `.nb-btn` in HTML or CSS
- [ ] Every day card has `.notes-wrap` with `.notes-area` textarea
- [ ] `saveNote(i, val)` and `getNote(i)` functions present
- [ ] `notes/day-01.md` through `notes/day-NN.md` template files generated

---

## Output file structure

**`notebook` type:**
```
courses/[COURSE_ID]/
  index.html
  notebooks/
    day-01-[slug].ipynb
    ...
    day-NN-[slug].ipynb
```

**`standard` type:**
```
courses/[COURSE_ID]/
  index.html
  notes/
    day-01.md
    ...
    day-NN.md
```

Output each file with a header:

```
## FILE: courses/[COURSE_ID]/index.html
[full content]

## FILE: courses/[COURSE_ID]/notebooks/day-01-[slug].ipynb   ← notebook only
[full content]

## FILE: courses/[COURSE_ID]/notes/day-01.md                 ← standard only
[full content]
```

---

*certified-journeys prompt v3 · two course types (notebook / standard) · linked tasks & resources · per-day notes textarea*
