from __future__ import annotations

import io
import os
from datetime import date, datetime
from typing import Iterable, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER, landscape
from reportlab.lib.units import inch
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas


PHASES = [
    ("Phase 1 — Mediation & Orders", datetime(2025, 10, 2, 23, 59, 59)),
    ("Phase 2 — Realtor Transition & Marketing", datetime(2025, 10, 3, 0, 0, 0), datetime(2025, 10, 29, 23, 59, 59)),
    ("Phase 3 — Enforcement & Hearing Prep", datetime(2025, 10, 30, 0, 0, 0)),
]


class TimelinePdfBuilder:
    """Builds a courtroom-readable timeline PDF following the project spec.

    Produces up to 3 pages (one per phase), landscape US Letter, 0.5" margins.
    """

    PAGE_SIZE = landscape(LETTER)
    MARGIN = 0.5 * inch
    CARD_WIDTH = 3.33 * inch  # ~320px at 96dpi
    CARD_PADDING = 10
    CARD_BORDER_RADIUS = 8
    CARD_MAX_PER_PAGE = 8

    # Typography
    TITLE_SIZE = 10
    DATE_SIZE = 10
    BODY_SIZE = 10
    SOURCE_SIZE = 9

    # Colors (neutral palette)
    SPINE_COLOR = colors.HexColor("#94a3b8")
    BACKGROUND = colors.white
    DEFAULT_BORDER = colors.HexColor("#6B7280")

    ACTOR_BORDER_MAP = {
        "Tom Ashby": colors.HexColor("#003366"),
        "Tom": colors.HexColor("#003366"),
        "Lisa Ashby": colors.HexColor("#7A1F1F"),
        "Lisa": colors.HexColor("#7A1F1F"),
        "Jeff Daniels": colors.HexColor("#444444"),
        "Jeff": colors.HexColor("#444444"),
        "Brody Miles": colors.HexColor("#1A595B"),
        "Court": colors.HexColor("#1A595B"),
    }

    def __init__(self, events: Iterable[dict], highlight_violations: bool = False, updated: str | None = None):
        # Keep flags for future use (highlighting not implemented yet)
        self.highlight_violations = bool(highlight_violations)
        self.last_updated_override = updated

        self._original = [self._normalise(ev) for ev in events or []]

        # Ensure events are sorted by date
        self._original.sort(key=lambda e: e["date"]) if self._original else None

    def _normalise(self, event: dict) -> dict:
        title = (event.get("title") or "").strip() or "Untitled Event"
        description = (event.get("description") or "").strip()
        date_val = self._coerce_datetime(event.get("date"))
        actor = (event.get("actor") or "").strip()
        evidence = (event.get("evidence_links") or "").strip()
        return {
            "title": title,
            "description": description,
            "date": date_val,
            "actor": actor,
            "evidence_links": evidence,
        }

    def _coerce_datetime(self, value) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time())
        if isinstance(value, str):
            cleaned = value.replace("Z", "+00:00")
            return datetime.fromisoformat(cleaned)
        raise ValueError("Invalid date value in event payload")

    def build(self) -> io.BytesIO:
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=self.PAGE_SIZE)

        width, height = self.PAGE_SIZE
        spine_x = width / 2

        # Group events into phases according to spec
        phase_events = self._group_into_phases(self._original)

        total_pages = 3
        page_num = 0
        last_updated = self.last_updated_override or datetime.utcnow().strftime("%Y-%m-%d")

        # If there are no events at all, render one-page empty state
        if not any(len(v) for v in phase_events):
            page_num = 1
            self._draw_phase_page(pdf, spine_x, width, height, 1, total_pages, [], last_updated)
        else:
            for idx, evs in enumerate(phase_events, start=1):
                page_num += 1
                self._draw_phase_page(pdf, spine_x, width, height, idx, total_pages, evs, last_updated)

        pdf.save()
        buffer.seek(0)
        return buffer

    def _group_into_phases(self, events: List[dict]) -> List[List[dict]]:
        p1_cutoff = datetime(2025, 10, 2, 23, 59, 59)
        p2_start = datetime(2025, 10, 3, 0, 0, 0)
        p2_end = datetime(2025, 10, 29, 23, 59, 59)
        p3_start = datetime(2025, 10, 30, 0, 0, 0)

        phase1 = [e for e in events if e["date"] <= p1_cutoff]
        phase2 = [e for e in events if p2_start <= e["date"] <= p2_end]
        phase3 = [e for e in events if e["date"] >= p3_start]

        return [phase1, phase2, phase3]

    def _draw_phase_page(self, pdf: canvas.Canvas, spine_x: float, width: float, height: float, phase_index: int, total_pages: int, events: List[dict], last_updated: str) -> None:
        # Prepare page
        pdf.setFillColor(self.BACKGROUND)
        pdf.rect(0, 0, width, height, fill=1, stroke=0)

        # Header - left aligned, 11pt bold same as body per spec
        phase_titles = {
            1: "Phase 1: Mediation & Orders",
            2: "Phase 2: Realtor Transition & Marketing",
            3: "Phase 3: Enforcement & Hearing Prep",
        }
        header_text = f"Ashby v. Ashby — {phase_titles.get(phase_index, '')}"
        pdf.setFont("Helvetica-Bold", 11)
        pdf.setFillColor(colors.HexColor("#111111"))
        pdf.drawString(self.MARGIN, height - self.MARGIN + 6, header_text)

        # Draw spine
        pdf.setStrokeColor(self.SPINE_COLOR)
        pdf.setLineWidth(2)
        pdf.line(spine_x, self.MARGIN, spine_x, height - self.MARGIN - 18)

        # Draw events (max CARD_MAX_PER_PAGE)
        shown = 0
        # Start directly below header; don't reserve space for missing first card
        start_y = height - self.MARGIN - 28
        min_gap = 18  # px approx (points) -> we'll use points; 18pt ~= 0.25in
        available_height = start_y - (self.MARGIN + 40)
        gap = max(min_gap, available_height / max(1, self.CARD_MAX_PER_PAGE))
        for i, ev in enumerate(events[: self.CARD_MAX_PER_PAGE]):
            side = -1 if i % 2 == 0 else 1
            y = start_y - (i * gap)
            # No dot markers on spine per round 2
            self._draw_card(pdf, spine_x, y, ev, side)
            shown += 1

        # Truncation note
        if len(events) > shown:
            note = f"+ {len(events) - shown} additional events not shown (see CSV)"
            pdf.setFont("Helvetica", 9)
            pdf.setFillColor(colors.HexColor("#374151"))
            # bottom-right per spec
            pdf.drawRightString(width - self.MARGIN, self.MARGIN + 18, note)

        # Footer
        footer = f"Ashby v. Ashby — Chronological Exhibit — Page {phase_index} of {total_pages}  |  Last Updated {last_updated}"
        pdf.setFont("Helvetica", 9)
        pdf.setFillColor(colors.HexColor("#374151"))
        pdf.drawRightString(width - self.MARGIN, self.MARGIN + 8, footer)

        # Finish page
        pdf.showPage()

    # removed spine dot markers intentionally - spec requires a clean spine

    def _draw_card(self, pdf: canvas.Canvas, spine_x: float, y: float, event: dict, side: int) -> None:
        # Compute card coordinates
        spacing = 0.25 * inch
        card_x = spine_x + side * (spacing + self.CARD_WIDTH / 2)
        if side < 0:
            card_x = spine_x - spacing - self.CARD_WIDTH
        card_y = y - (self.CARD_WIDTH * 0.12)
        card_h = 1.6 * inch

        # Border color by actor
        border_color = self.ACTOR_BORDER_MAP.get(event.get("actor"), self.DEFAULT_BORDER)

        # Draw rounded rect (white fill, colored border)
        pdf.setFillColor(colors.white)
        pdf.setStrokeColor(border_color)
        pdf.setLineWidth(1.5)
        pdf.roundRect(card_x, card_y, self.CARD_WIDTH, card_h, self.CARD_BORDER_RADIUS, stroke=1, fill=1)

        inner_x = card_x + self.CARD_PADDING
        inner_y = card_y + card_h - self.CARD_PADDING

        # Title and date - legal style Month D, YYYY
        pdf.setFont("Helvetica-Bold", self.TITLE_SIZE)
        pdf.setFillColor(colors.HexColor("#000000"))
        try:
            date_text = event['date'].strftime("%B %-d, %Y")
        except Exception:
            # Fallback for platforms that don't support %-d
            date_text = event['date'].strftime("%B %d, %Y").replace(" 0", " ")
        title_text = f"{date_text} — {event['title']}"
        pdf.drawString(inner_x, inner_y - 2, title_text[:140])

        # Description (clamped to 30 words) with soft hyphenation for long words
        raw_body = event.get("description", "") or ""
        body = self._clamp_words(raw_body, 30)
        body = self._soft_hyphenate(body, 12)
        pdf.setFont("Helvetica", self.BODY_SIZE)
        pdf.setFillColor(colors.HexColor("#111111"))
        wrap_width = self.CARD_WIDTH - (2 * self.CARD_PADDING)
        lines = simpleSplit(body, "Helvetica", self.BODY_SIZE, wrap_width)
        offset = 16
        # ensure at least 18pt vertical gap between cards by limiting lines
        for line in lines[:4]:
            # replace soft hyphen with normal hyphen for display if line break occurs
            display_line = line.replace("\u00AD", "-")
            pdf.drawString(inner_x, inner_y - offset - 12, display_line)
            offset += 12

        # Source line derivation
        src = self._derive_source(event.get("evidence_links"))
        pdf.setFont("Helvetica-Oblique", self.SOURCE_SIZE)
        pdf.setFillColor(colors.HexColor("#555555"))
        pdf.drawString(inner_x, card_y + self.CARD_PADDING, f"Source: {src}")

    def _soft_hyphenate(self, text: str, maxlen: int = 12) -> str:
        """Insert soft hyphens into very long words so the renderer can wrap them."""
        parts = []
        for word in text.split():
            if len(word) > maxlen:
                # insert soft hyphen every maxlen characters
                chunks = [word[i:i+maxlen] for i in range(0, len(word), maxlen)]
                parts.append("\u00AD".join(chunks))
            else:
                parts.append(word)
        return " ".join(parts)

    def _derive_source(self, evidence_links: str) -> str:
        import re
        if not evidence_links or not str(evidence_links).strip():
            return "Exhibit pending"
        # split on common separators and take first
        for sep in [';', ',', '\n']:
            if sep in evidence_links:
                parts = [p.strip() for p in evidence_links.split(sep) if p.strip()]
                if parts:
                    evidence_links = parts[0]
                    break
        name = os.path.basename(evidence_links.strip())
        # remove extension
        base = re.sub(r"\.[A-Za-z0-9]+$", "", name)
        pretty = re.sub(r"[_-]+", " ", base).strip()
        return pretty.title() if pretty else "Exhibit pending"

    def _clamp_words(self, text: str, limit: int) -> str:
        if not text:
            return ""
        words = text.split()
        if len(words) <= limit:
            return text
        return " ".join(words[:limit]) + "…"


def build_timeline_pdf(events: Iterable[dict], highlight_violations: bool = False, updated: str | None = None) -> io.BytesIO:
    """Public helper used by FastAPI route and CLI.

    Parameters:
    - events: iterable of event dicts
    - highlight_violations: stub flag passed through (not implemented)
    - updated: optional YYYY-MM-DD string to override footer last-updated date
    """
    return TimelinePdfBuilder(events, highlight_violations=highlight_violations, updated=updated).build()
