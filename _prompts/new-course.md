# certified-journeys · New Course Generation Prompt

Copy this entire prompt into Claude (or any capable LLM). Fill in the `[COURSE INPUT]` section at the top, then send. The model will output:

1. A complete `courses/[COURSE_ID]/index.html` tracker
2. A complete `courses/[COURSE_ID]/notebooks/day-NN-slug.ipynb` file for every day

---

## [COURSE INPUT] — Fill this in before sending

```
COURSE_ID:        e.g. polars-certified, terraform-certified, kafka-certified
COURSE_FULL_NAME: e.g. Apache Kafka Streams Developer
ICON:             2-letter abbreviation, e.g. KF
ACCENT_COLOR:     hex, e.g. #E8890C
ACCENT_LIGHT:     light version for dark-mode backgrounds, e.g. #2A1500
PROVIDER:         e.g. Confluent, HashiCorp, Google, Self-paced
COST:             e.g. $150, Free
TOTAL_DAYS:       integer, typically 10–21
DIFFICULTY:       Beginner / Intermediate / Advanced
TAGS:             comma-separated, e.g. Streaming, Java, Kafka
EXAM_LINK:        official exam/cert page URL
EXAM_QUESTIONS:   integer or null
EXAM_MINUTES:     integer or null
EXAM_PASS_SCORE:  e.g. 70%, null if no formal exam
EXAM_NOTES:       free text about the exam format
UPGRADE_NOTE:     what to study next after this cert

DAYS:
  Provide one entry per day in this format —
  Day N | Title | Badge (learn/practice/review/exam) | Tasks (bullet list) | Resources (bullet list) | Tip | hasScore (true/false)

TOPICS:
  Provide 4–8 topic groups, each with:
  Name | Accent color (hex) | Day indices that cover it (0-based, comma-separated)
```

---

## Prompt (send everything below this line)

---

You are generating a new certified-journeys course. I will give you course metadata and day-by-day content. You will produce two outputs:

**Output A** — `courses/[COURSE_ID]/index.html` — the course tracker  
**Output B** — `courses/[COURSE_ID]/notebooks/day-NN-slug.ipynb` — one Jupyter notebook per day

Follow every spec below exactly. Do not add features not described. Do not simplify or summarise — produce the full files.

---

## COURSE METADATA

```
[paste your filled-in [COURSE INPUT] block here]
```

---

## OUTPUT A SPEC — `index.html` tracker

### File structure

Produce a single self-contained HTML file. No external JS, no build tools, no npm. The only external resources allowed are Google Fonts.

### Head

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>[COURSE_FULL_NAME] · certified-journeys</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  /* all CSS inline — no external stylesheet */
</style>
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
  --green-light:[ACCENT_DARK_DIM]; /* dark-mode tinted bg for the accent colour */
  --blue-light:#061E38; --amber-light:#221900;
  --coral-light:#2A0E05; --purple-light:#161440;
  --orange-light:#1F1200; --teal-light:#021E26;
}}
```

### Required CSS classes (include all of these)

Layout: `.app`, `.breadcrumb`, `.breadcrumb-sep`  
Hero: `.course-hero`, `.course-hero-top`, `.course-icon-wrap`, `.course-icon`, `.course-title-block`, `.tag-row`, `.tag`, `.hero-meta`, `.meta-item`, `.meta-label`, `.meta-val`  
Progress strip: `.prog-strip`, `.prog-strip-top`, `.prog-label`, `.prog-pct`, `.bar-bg`, `.bar-fill`, `.readiness` (with `.early`, `.close`, `.ready` modifiers), `.stats-grid`, `.stat`, `.stat-label`, `.stat-val` (with `.ok`, `.warn`, `.danger` modifiers)  
Tabs: `.tabs`, `.tab` (with `.active`), `.panel` (with `.active`)  
Day cards: `.day-card` (with `.completed`, `.open`), `.day-header`, `.day-num`, `.day-meta`, `.day-title`, `.day-sub`, `.day-badge`, `.chevron`, `.day-body`, `.tip-box`, `.task-list`, `.task`, `.task-bullet`, `.resources-row`, `.res-pill`, `.score-row`, `.score-badge`, `.hours-row`, `.complete-btn` (with `.done`)  
Notebooks: `.nb-row`, `.nb-btn`, `.nb-btn-colab`  
Topics: `.topic-grid`, `.topic-card`, `.t-bar-bg`, `.t-bar-fill`, `.t-pct`  
Notes: `.notes-wrap`, `.note-card`, `.note-card-head`, `.note-saved`, `textarea`  
AI: `.ai-card`, `.ai-card-head`, `.ai-icon`, `.ai-card-title`, `.ai-card-sub`, `.ai-card-body`, `.ai-prompt-box`, `.ai-link-btn`  
Exam: `.exam-grid`, `.exam-card`, `.exam-card-label`, `.exam-card-val`, `.exam-card-sub`  
Resources: `.res-section`, `.res-section-title`, `.res-link-list`, `.res-link-item`, `.res-link-index`, `.res-link-body`, `.res-link-desc`  
Shared: `.info-box`, `.badge-learn`, `.badge-practice`, `.badge-review`, `.badge-exam`, `.page-footer`  
Responsive: `@media(max-width:640px)` breakpoint for `.topic-grid`, `.hero-meta`, `.stats-grid`

### Notebook button CSS (required)

```css
.nb-row{display:flex;gap:8px;margin-bottom:10px;flex-wrap:wrap;}
.nb-btn{font-size:12px;padding:6px 14px;border-radius:99px;border:.5px solid var(--border2);color:var(--text2);background:none;text-decoration:none;display:inline-flex;align-items:center;gap:5px;transition:all .15s;font-family:inherit;}
.nb-btn:hover{background:var(--surface2);color:var(--text);text-decoration:none;}
.nb-btn-colab{background:#F9AB00;border-color:#F9AB00;color:#000;}
.nb-btn-colab:hover{background:#e09900;color:#000;text-decoration:none;}
```

### HTML body structure (required — in this order)

```html
<body>
<div class="app">

  <!-- 1. Breadcrumb -->
  <div class="breadcrumb">
    <a href="../../index.html">certified-journeys</a>
    <span class="breadcrumb-sep">›</span>
    <span>[COURSE_FULL_NAME]</span>
  </div>

  <!-- 2. Course hero -->
  <div class="course-hero">
    <div class="course-hero-top">
      <div class="course-icon-wrap">
        <div class="course-icon" style="background:var(--green-light);color:var(--green);">[ICON]</div>
        <div class="course-title-block">
          <h1>[COURSE_FULL_NAME]</h1>
          <p>[PROVIDER] · [DIFFICULTY] · [TOTAL_DAYS] days · [COST]</p>
          <div class="tag-row"><!-- one .tag per tag --></div>
        </div>
      </div>
    </div>
    <div class="hero-meta">
      <!-- 4 meta items: Provider, Cost, Days, Difficulty -->
    </div>
  </div>

  <!-- 3. Progress strip -->
  <div class="prog-strip">
    <!-- progress bar, pct display, readiness row -->
    <!-- stats grid: Days done, Avg score, Hours logged, Days left -->
  </div>

  <!-- 4. Tabs -->
  <div class="tabs">
    <button class="tab active" onclick="showPanel('schedule',this)">📅 Daily Plan</button>
    <button class="tab" onclick="showPanel('topics',this)">📚 Topics</button>
    <button class="tab" onclick="showPanel('notes',this)">📝 Notes</button>
    <button class="tab" onclick="showPanel('ai',this)">🤖 AI Tools</button>
    <button class="tab" onclick="showPanel('resources',this)">🔗 Resources</button>
    <button class="tab" onclick="showPanel('exam',this)">🎓 Exam Prep</button>
  </div>

  <!-- 5. Panels (all empty — rendered by JS) -->
  <div id="panel-schedule" class="panel active"></div>
  <div id="panel-topics"   class="panel"></div>
  <div id="panel-notes"    class="panel"></div>
  <div id="panel-ai"       class="panel"></div>
  <div id="panel-resources" class="panel"></div>
  <div id="panel-exam"     class="panel"></div>

  <!-- 6. Footer -->
  <div class="page-footer">
    Progress saved locally · <span id="sk-display">cj_[COURSE_ID]_v1</span> · No account needed · <a href="../../index.html">← All journeys</a>
  </div>

</div>
```

### JavaScript — data constants (required shape)

```js
const COURSE_ID   = '[COURSE_ID]';
const STORAGE_KEY = 'cj_[COURSE_ID]_v1';
const TOTAL_DAYS  = [TOTAL_DAYS];

// One entry per day — generate from your DAYS input
const days = [
  {
    title:     "string",
    badge:     "learn" | "practice" | "review" | "exam",
    sub:       "Day N · Theme",
    tasks:     ["task string", ...],
    resources: ["resource string", ...],
    tip:       "string",
    hasScore:  false  // true only for practice exam days
  },
  // ...
];

// 4–8 topic groups — generate from your TOPICS input
const topics = [
  { name: "string", color: "#hex", days: [0, 1, 2] },  // 0-based day indices
  // ...
];

// Exam details
const exam = {
  questions:  null | number,
  minutes:    null | number,
  passScore:  "string",
  cost:       "[COST]",
  provider:   "[PROVIDER]",
  link:       "[EXAM_LINK]",
  notes:      "string"
};

// Notebook slugs — one per day, matching filenames in notebooks/
const NOTEBOOKS = [
  'day-01-slug',
  // ...
];
```

### JavaScript — state and functions (required — include all)

```js
let state = {
  completed:    [],
  scores:       {},
  hours:        {},
  completedAt:  {},
  notes:        {},
  openDay:      null,
  startDate:    null,
  lastActivity: null,
  status:       'not_started'
};

// Required functions — implement all:
// loadState(), saveState(), broadcastStatus(), resetAll()
// isCompleted(i), toggleComplete(i), toggleDay(i)
// logScore(i, val), logHours(i, val)
// scoreClass(s), badgeClass(b), badgeLabel(b)
// updateStats()
// renderSchedule()   — includes .nb-row with notebook + Colab buttons
// renderTopics()
// saveNote(key, val)
// renderNotes()      — general, week1, week2 + per-day + reflections cards
// renderAI()         — 3 cards: NotebookLM audio, NotebookLM flashcards, Claude prompts
// renderExam()       — 4 stat cards + readiness checklist
// renderResources()  — grouped by: Core Reading, Hands-On, Ecosystem, Upgrade Path
// showPanel(name, btn)
// renderAll()
```

#### `renderSchedule` — day card body (required structure)

Every day card body must render in this order:

```js
`<div class="nb-row">
  <a class="nb-btn" href="notebooks/${NOTEBOOKS[i]}.ipynb" target="_blank">📓 Open notebook</a>
  <a class="nb-btn nb-btn-colab" href="https://colab.research.google.com/github/certified-journeys/[COURSE_ID]/blob/main/notebooks/${NOTEBOOKS[i]}.ipynb" target="_blank">▶ Open in Colab</a>
</div>
<div class="tip-box"><p><strong>💡 Tip:</strong> ${d.tip}</p></div>
<div class="task-list"><!-- tasks --></div>
<div class="resources-row"><!-- resource pills --></div>
<!-- score row only if d.hasScore -->
<div class="hours-row"><!-- hours input --></div>
<button class="complete-btn ..."><!-- mark complete --></button>`
```

#### `renderAI` — three cards (required content)

Card 1 — **NotebookLM Audio Podcast**: prompt template asking for a 10-minute podcast episode covering key concepts, exam traps, and must-know items for [COURSE_FULL_NAME]. Link to `https://notebooklm.google.com`.

Card 2 — **NotebookLM Flashcards**: prompt template asking for 20 flashcard Q&A pairs focused on concept distinctions, misconceptions, and scenario-based questions for [COURSE_FULL_NAME]. Link to `https://notebooklm.google.com`.

Card 3 — **Claude Deep Dive Prompts**: three prompt templates — (1) explain like a senior engineer, (2) exam scenario questions, (3) gap analysis study plan. All tailored to [COURSE_FULL_NAME].

#### `renderResources` — four sections (required)

- **Core Reading** — official docs, primary spec, main reference
- **Hands-On Resources** — tutorials, labs, community forums
- **Ecosystem & Tooling** — related tools, packages, integrations
- **Upgrade Path** — what to study next, links to follow-on certs

Each link item follows this structure:
```html
<div class="res-link-item">
  <span class="res-link-index">01</span>
  <div class="res-link-body">
    <a href="URL" target="_blank">Title</a>
    <div class="res-link-desc">One-line description</div>
  </div>
</div>
```

Include at least 3 links per section (12 minimum total).

#### `renderExam` — readiness checklist (required)

The checklist must include:
- Completed all [TOTAL_DAYS] days of the study plan
- Scored [EXAM_PASS_SCORE] or higher on practice exams
- Can explain every topic in the Topics tab without notes
- Have written out a cheat sheet from memory and verified it
- Scoring consistently — not just lucky on one attempt

#### `broadcastStatus` — localStorage summary (required)

```js
function broadcastStatus() {
  const summary = {
    id:           COURSE_ID,
    status:       state.status,
    completed:    state.completed.length,
    total:        TOTAL_DAYS,
    scores:       Object.values(state.scores).filter(s => s > 0),
    totalHours:   Object.values(state.hours).reduce((a, b) => a + b, 0),
    completedAt:  state.completedAt,
    startDate:    state.startDate,
    lastActivity: state.lastActivity
  };
  try { localStorage.setItem('cj_summary_' + COURSE_ID, JSON.stringify(summary)); } catch(e) {}
}
```

### Init (required — last lines of `<script>`)

```js
loadState();
renderAll();
```

---

## OUTPUT B SPEC — Jupyter notebooks (one per day)

### File naming

`day-01-[slug].ipynb`, `day-02-[slug].ipynb`, ... where slug is a 1–3 word kebab-case summary of the day's title.

### Format

Valid nbformat 4 JSON. All cells must use the standard structure:

```json
{
  "cell_type": "markdown" | "code",
  "metadata": {},
  "source": ["line 1\n", "line 2\n"]
}
```

For code cells also include:
```json
"execution_count": null,
"outputs": []
```

### Required cell sequence (every notebook must follow this order)

**Cell 1 — Header (markdown)**
```markdown
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/certified-journeys/[COURSE_ID]/blob/main/notebooks/day-NN-slug.ipynb)

---
# Day N · [Day Title]
**certified-journeys / [COURSE_ID]** · [Sub label]

> **Goal for today:** [one sentence stating what the learner will be able to do by the end]

---
```

**Cell 2 — Install (code)**
```python
%pip install -q [required packages]
```
Only include packages beyond the standard library. Use specific extras where needed (e.g. `"dlt[duckdb]"`).

**Cells 3–N — Lesson body**

Follow this alternating pattern:
1. **Concept cell (markdown)**: Explain ONE concept at a time. Use a comparison table where possible. Use `##` headings with `Step N ·` prefix. Max ~15 lines.
2. **Code cell**: Working, runnable code that demonstrates the concept just explained. Add inline comments on every non-obvious line.
3. **"What just happened?" cell (markdown)**: 3–5 bullet points explaining what the code did and why it matters. Highlight the key insight in bold.

Repeat for each task in the day's task list. Every task becomes at least one concept+code+explanation triple.

**Second-to-last cell — Challenge (code)**

```python
# Challenge: [clear instruction — what to build or modify]
# Your solution here

# Starter code or scaffold (not the full answer)
```

**Last cell — Recap (markdown)**

```markdown
---
## Day N key concepts recap

| Concept | What to remember |
|---|---|
| ... | ... |

> **Tip:** [the day's tip from the days array]

---
## What's next

**Day N+1** → [brief preview of next day's topic]

Mark Day N complete in your [tracker](../index.html).
```

For the final day (capstone), replace "What's next" with a completion message and links to the next certification in the upgrade path.

### Code quality rules

- All code must actually run without errors in a fresh Colab environment after the install cell
- No pseudocode. No `# TODO` stubs (except in the Challenge cell)
- No `...` as placeholder unless it is the Challenge scaffold
- For courses requiring credentials (cloud APIs, paid services): use a clearly-labelled free alternative for the notebook (e.g. DuckDB instead of BigQuery, JSONPlaceholder instead of a real API) and note the production equivalent in a markdown cell
- For non-Python courses (e.g. Terraform, Scrum): use Python to simulate/validate the concepts where possible, and use markdown + annotated config blocks for the parts that can't run in Python
- Import all packages at the top of the first code cell that uses them, not scattered throughout

### Notebook depth requirements

| Day type | Min code cells | Min markdown cells | Min total lines |
|---|---|---|---|
| `learn` | 5 | 8 | 150 |
| `practice` | 8 | 5 | 200 |
| `review` | 4 | 10 | 150 |
| `exam` (capstone) | 10 | 8 | 250 |

---

## Quality checklist (verify before outputting)

**Tracker (index.html)**
- [ ] `broadcastStatus()` writes to `cj_summary_[COURSE_ID]` in localStorage
- [ ] `STORAGE_KEY` is `cj_[COURSE_ID]_v1`
- [ ] All 6 panels render without JS errors
- [ ] Every day card has `.nb-row` with both notebook and Colab buttons
- [ ] `renderResources()` has 4 sections, 12+ links
- [ ] `renderAI()` has 3 cards with tailored prompts for this course
- [ ] Dark mode CSS variables are set

**Notebooks**
- [ ] Every notebook has the Colab badge with the correct GitHub URL
- [ ] Every notebook ends with a link back to `../index.html`
- [ ] Notebook filenames match `NOTEBOOKS` array in `index.html` exactly
- [ ] All code cells are runnable (no pseudocode outside Challenge cell)
- [ ] Each day's tasks are all covered by at least one code cell
- [ ] Challenge cell has a scaffold but not the full solution
- [ ] Solution is in a `<details>` block in markdown

---

## Example output structure

```
courses/[COURSE_ID]/
  index.html
  notebooks/
    day-01-[slug].ipynb
    day-02-[slug].ipynb
    ...
    day-NN-[slug].ipynb
```

Output each file preceded by a markdown header:

```
## FILE: courses/[COURSE_ID]/index.html
[full file content]

## FILE: courses/[COURSE_ID]/notebooks/day-01-[slug].ipynb
[full file content]
```

---

*certified-journeys prompt template v1 · generated for the dlt-certified course pattern*
