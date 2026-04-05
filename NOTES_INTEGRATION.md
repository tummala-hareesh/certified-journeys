# Notes-to-Markdown Integration Guide

> **TL;DR** — add one `<script>` tag to each course tracker and you're done.

---

## What this adds

When `notes-sync.js` is loaded inside a course tracker it:

1. **Injects a Notes panel** at the bottom of the page (no layout changes needed).
2. **Saves notes in `localStorage`** under a course-scoped key so progress persists.
3. **Commits every note as a `.md` file** to `courses/{courseId}/` via the GitHub Contents API.
4. **Falls back to a browser download** if no GitHub PAT is configured.

Example resulting file tree after a study session:

```
courses/
  pspo-certified/
    index.html                          ← existing tracker
    2025-04-04-day-3-key-concepts.md    ← ✅ new – auto-committed
    2025-04-05-sprint-goal-summary.md   ← ✅ new – auto-committed
  aws-ml-certified/
    index.html
    2025-04-06-feature-engineering-notes.md
  ...
```

---

## Step 1 — Add `notes-sync.js` to the repo root

Copy `notes-sync.js` to the repository root (same level as `index.html`).

```
certified-journeys.github.io/
  index.html
  notes-sync.js          ← place here
  courses/
    pspo-certified/
      index.html
    aws-ml-certified/
      index.html
    ...
```

---

## Step 2 — Add one `<script>` tag to each course tracker

In each `courses/{courseId}/index.html`, add **just before `</body>`**:

```html
<!-- Notes-to-Markdown sync (shared utility) -->
<script src="../../notes-sync.js"></script>
```

The script auto-detects the `courseId` from the URL path
(`/courses/pspo-certified/` → `pspo-certified`).

If your file doesn't live exactly two levels below the repo root, pass the
`data-course-id` attribute explicitly:

```html
<script src="../../notes-sync.js" data-course-id="pspo-certified"></script>
```

---

## Course-by-course patch

### courses/pspo-certified/index.html
```html
<!-- before </body> -->
<script src="../../notes-sync.js"></script>
```

### courses/aws-ml-certified/index.html
```html
<script src="../../notes-sync.js"></script>
```

### courses/dlt-certified/index.html
```html
<script src="../../notes-sync.js"></script>
```

### courses/polars-certified/index.html
```html
<script src="../../notes-sync.js"></script>
```

### courses/terraform-certified/index.html
```html
<script src="../../notes-sync.js"></script>
```

### courses/powerbi-certified/index.html
```html
<script src="../../notes-sync.js"></script>
```

---

## Step 3 — Configure GitHub sync (first-time, in-browser)

1. Open any course tracker in your browser.
2. Scroll to the **📝 Notes** panel at the bottom.
3. Expand **"Configure GitHub sync"** and paste your Personal Access Token.

**Required PAT permissions:**
- Classic token → `repo` scope
- Fine-grained token → `Contents: Read and Write` for the target repository

The token is stored in `localStorage` only — never sent anywhere except
`api.github.com`.

---

## How each `.md` file looks

```markdown
# Day 3 key concepts

**Course:** pspo-certified
**Day:** Day 3
**Created:** 2025-04-04T14:23:00.000Z
**Tags:** scrum, product-owner, backlog

---

- The Product Backlog is an ordered list of everything needed in the product.
- Only the PO is responsible for ordering it.
- Sprint Goal gives the team flexibility while preserving coherence.
```

---

## Principles

- Zero external dependencies — pure vanilla JS, no build step.
- Follows the project's localStorage-only privacy model for the local copy.
- The GitHub API call is the only network request and is fully opt-in.
- MIT licensed — fork freely.
