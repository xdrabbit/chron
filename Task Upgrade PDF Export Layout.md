###  **Task: Upgrade PDF Export Layout – “Courtroom-Readable Timeline”**

**Goal:**
 Keep all existing logic (CSV import, FTS5 search, event storage) exactly as is.
 Upgrade the **Export PDF** renderer to follow the attached *Courtroom-Readable Timeline* spec.

**Scope:**

- Do **not** modify CSV parsing or data model.
- Only change how the export PDF lays out events.

**Layout requirements:**

1. Group events by phase:

   - Phase 1 – Mediation & Orders (≤ Oct 2 2025)
   - Phase 2 – Realtor Transition & Marketing (Oct 3–Oct 29 2025)
   - Phase 3 – Enforcement & Hearing Prep (≥ Oct 30 2025)

2. One page per phase, landscape US Letter (8.5 × 11 in, 0.5″ margins).

3. Center vertical spine line, alternate event boxes left/right.

4. Event box template:

   ```
   [DATE] — [TITLE]
   [≤ 30-word factual summary]
   Source: [filename from evidence_links]
   ```

5. Neutral colors, readable fonts (Helvetica 10 pt), no red or emoji.

6. Actor color mapping (border only):

   - Tom Ashby #003366
   - Lisa Ashby #7A1F1F
   - Jeff Daniels #444444
   - Brody Miles/Court #1A595B

7. Footer per page:
    `Ashby v. Ashby — Chronological Exhibit — Page X of Y  |  Last Updated YYYY-MM-DD`

**Acceptance criteria:**

- Loads existing CSV data and exports PDF with above layout.
- Alternating event boxes render cleanly, max 8 per page.
- Font sizes and margins consistent; PDF opens correctly in Acrobat/Chrome.
- “+ N additional events not shown (see CSV)” note appears if truncated.

**Reference:**
 Use the “Courtroom-Readable Timeline” brief for visual guidance (provided by Tom & Nyra).





# Implementation Directive — Courtroom Timeline PDF

## Goal

Render a **judge-readable timeline PDF** from a CSV input. The renderer does **no interpretation** of data; it formats and lays out events per the rules below.

------

## Input

- **File:** CSV (UTF-8)
- **Required headers (exact):**
   `title,description,date,timeline,actor,emotion,tags,evidence_links`
- **Date format:** `YYYY-MM-DD` (optional time allowed, ignored in layout)
- **Scope filter:** Only rows where `timeline == "House Sale"`.

**Example row**

```
Realtor Feedback Confirms Odor and Clutter,"Jeff Daniels reported odor and clutter; recommended declutter, carpet treatment, sign and lockbox.",2025-10-13,House Sale,Jeff Daniels,professional,"realtor_feedback;/odor;/clutter","/evidence/emails/2025-10-13_JeffDanielsFeedback.pdf"
```

------

## Output

- **PDF** (US Letter, 8.5×11), **landscape**, 0.5" margins
- **Pages:** up to 3, one per phase (see Phase logic)
- **Footer:** `Ashby v. Ashby — Chronological Exhibit — Page X of Y   |   Last Updated: YYYY-MM-DD`

------

## Phase logic

Group events chronologically into these pages:

1. **Phase 1 — Mediation & Orders** (up to Oct 2, 2025)
2. **Phase 2 — Realtor Transition & Marketing** (Oct 3–Oct 29, 2025)
3. **Phase 3 — Enforcement & Hearing Prep** (Oct 30, 2025 →)

Each page gets a header label:
 `Ashby v. Ashby — Phase N (Title)`

------

## Layout Rules

- Vertical **timeline spine** centered (2px, #94a3b8 slate).

- **Event card** boxes alternate left/right of spine (odd rows left, even rows right).

- **Max events per page:** 8 (truncate with “+ N additional events not shown” note).

- **Card content template:**

  ```
  [DATE] — [TITLE]
  [≤ 30-word factual description]
  Source: [derived from evidence_links or “Exhibit pending”]
  ```

- **Typography**

  - Font: Helvetica/Arial (fallback system sans)
  - Date: 10pt bold small caps (#111)
  - Title: 10pt bold (#000)
  - Body: 10pt regular (#111), 1.15 line height
  - Source: 9pt italic (#555)

- **Card width:** ~320px; padding 10–12px; border-radius 8px; shadow subtle

- **Color cue by `actor` (card border only):**

  - Tom Ashby → `#003366`
  - Lisa Ashby → `#7A1F1F`
  - Jeff Daniels → `#444444`
  - Brody/Court → `#1A595B`
  - Default → `#6B7280`

- **Source line derivation:** take filename from `evidence_links` if present, render as:
   `Source: 2025-10-13_JeffDanielsFeedback.pdf`
   (No URL linking required; this is a visual exhibit cue.)

------

## Behavior & Edge Cases

- **Empty or bad CSV:** render a 1-page PDF with “No events found for timeline ‘House Sale’.”
- **Long descriptions:** clamp to ~30 words; append “…” (do not overflow box).
- **Too many events:** show first 8 per phase; append line at bottom:
   “+ N additional events not shown (see CSV)”.
- **Missing fields:** if `title` or `date` missing, skip row; log warning.
- **Time in `date`:** ignore time in display (show `MMM DD YYYY`).

------

## CLI / API

- CLI (preferred):

  ```
  timeline-render \
    --csv ./real-data-import.csv \
    --out ./chronicle-timeline.pdf \
    --updated "2025-10-29"
  ```

- Return non-zero exit code on error; write stderr logs.

------

## Acceptance Criteria (what we’ll check)

1. **Loads** our CSV and filters to `timeline == "House Sale"`.
2. **Three pages**, correct phase headers, spine visible, alternating cards.
3. Each card shows **DATE — TITLE**, ≤30-word description, and **Source** file name.
4. Actor border colors applied per mapping.
5. Footer shows **case caption, page X of Y, Last Updated date**.
6. Handles >8 events per phase with the “+ N additional…” note.
7. PDF opens cleanly in Acrobat and browser viewers.

------

## Pseudocode (render loop)

```pseudo
events = csv.read().filter(timeline == "House Sale")
events.sort_by(date)

phase1 = events.where(date <= 2025-10-02)
phase2 = events.where(2025-10-03 <= date <= 2025-10-29)
phase3 = events.where(date >= 2025-10-30)

for phase in [phase1, phase2, phase3]:
  new_pdf_page(landscape)
  draw_header("Ashby v. Ashby — Phase N (Title)")
  draw_timeline_spine()
  shown = 0
  for i, ev in enumerate(phase):
    if shown == 8: break
    side = "left" if i % 2 == 0 else "right"
    color = actor_color_map.get(ev.actor, default)
    box = layout_card(side, width=320, border=color)
    box.text(format_date(ev.date) + " — " + ev.title, style=title)
    box.text(clamp(ev.description, 30_words), style=body)
    src = basename(ev.evidence_links) or "Exhibit pending"
    box.text("Source: " + src, style=source)
    shown += 1
  if phase.count > shown:
    draw_note(f"+ {phase.count - shown} additional events not shown (see CSV)")
  draw_footer(case_caption, page_num, last_updated)
```

------

## “Do / Don’t” Quick Guide

- **Do:** keep verbs neutral (“reported,” “requested,” “declined”).
- **Do:** keep everything legible at 100% zoom.
- **Don’t:** use red text, emoji, or judgmental language.
- **Don’t:** wrap beyond 30 words per card.

------

