from __future__ import annotations

import io
from datetime import date, datetime
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas


class TimelinePdfBuilder:
    """Generates a vertical spine timeline PDF for Chronicle events."""

    PAGE_SIZE = LETTER
    MARGIN = 0.75 * inch
    CARD_WIDTH = 2.8 * inch
    CARD_HEIGHT = 1.25 * inch
    ROW_GAP = 1.4 * inch
    SPINE_COLOR = colors.HexColor("#334155")
    CARD_BORDER = colors.HexColor("#0f172a")
    CARD_FILL = colors.HexColor("#1e293b")
    ACCENT_COLOR = colors.HexColor("#38bdf8")

    def __init__(self, events: Iterable[dict]):
        # Normalise payload into dictionaries to avoid mutating ORM instances
        normalised = []
        for event in events:
            title = (event.get("title") or "").strip() or "Untitled Event"
            description = (event.get("description") or "").strip()
            event_date = self._coerce_datetime(event.get("date"))
            normalised.append(
                {
                    "title": title,
                    "description": description,
                    "date": event_date,
                }
            )
        self._events = normalised

    @staticmethod
    def _coerce_datetime(value) -> datetime:
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
        current_y = height - self.MARGIN - 0.75 * inch

        if not self._events:
            self._draw_page_header(pdf, spine_x, height)
            self._draw_empty_state(pdf, spine_x, current_y)
        else:
            for index, event in enumerate(self._events):
                if current_y < self.MARGIN + self.CARD_HEIGHT:
                    pdf.showPage()
                    current_y = height - self.MARGIN - 0.75 * inch
                    self._draw_page_header(pdf, spine_x, height)

                if index == 0 or current_y == height - self.MARGIN - 0.75 * inch:
                    self._draw_page_header(pdf, spine_x, height)

                side = -1 if index % 2 == 0 else 1
                self._draw_spine_segment(pdf, spine_x, current_y)
                self._draw_event_card(pdf, spine_x, current_y, event, side)

                current_y -= self.ROW_GAP

        pdf.save()
        buffer.seek(0)
        return buffer

    def _draw_page_header(self, pdf: canvas.Canvas, spine_x: float, height: float) -> None:
        top = height - self.MARGIN
        pdf.setFont("Helvetica-Bold", 20)
        pdf.setFillColor(colors.HexColor("#e2e8f0"))
        pdf.drawString(self.MARGIN, top, "Chronicle Timeline")

        pdf.setFont("Helvetica", 10)
        pdf.setFillColor(colors.HexColor("#94a3b8"))
        subtitle = datetime.utcnow().strftime("Exported %d %b %Y %H:%M UTC")
        pdf.drawString(self.MARGIN, top - 16, subtitle)

        # spine
        pdf.setStrokeColor(self.SPINE_COLOR)
        pdf.setLineWidth(2)
        pdf.line(spine_x, self.MARGIN, spine_x, top - 30)

    def _draw_spine_segment(self, pdf: canvas.Canvas, spine_x: float, y: float) -> None:
        pdf.setFillColor(self.ACCENT_COLOR)
        pdf.circle(spine_x, y, 6, stroke=0, fill=1)

    def _draw_event_card(
        self,
        pdf: canvas.Canvas,
        spine_x: float,
        y: float,
        event: dict,
        side: int,
    ) -> None:
        card_x = spine_x + side * (0.45 * inch)
        if side < 0:
            card_x -= self.CARD_WIDTH
        card_y = y - self.CARD_HEIGHT / 2

        # connector
        pdf.setStrokeColor(self.ACCENT_COLOR)
        pdf.setLineWidth(1.4)
        if side < 0:
            pdf.line(spine_x, y, card_x + self.CARD_WIDTH, y)
        else:
            pdf.line(spine_x, y, card_x, y)

        # card background
        pdf.setFillColor(self.CARD_FILL)
        pdf.setStrokeColor(self.CARD_BORDER)
        pdf.roundRect(card_x, card_y, self.CARD_WIDTH, self.CARD_HEIGHT, 10, fill=1, stroke=1)

        inner_x = card_x + 12
        inner_y = card_y + self.CARD_HEIGHT - 16

        pdf.setFillColor(colors.HexColor("#f8fafc"))
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(inner_x, inner_y, event["title"][:60])

        date_text = event["date"].strftime("%B %d, %Y")
        pdf.setFillColor(colors.HexColor("#38bdf8"))
        pdf.setFont("Helvetica", 9)
        pdf.drawString(inner_x, inner_y - 14, date_text)

        description = event["description"]
        if description:
            text_lines = simpleSplit(description, "Helvetica", 9, self.CARD_WIDTH - 24)
            pdf.setFillColor(colors.HexColor("#cbd5f5") if text_lines else colors.HexColor("#f8fafc"))
            pdf.setFont("Helvetica", 9)
            offset = 30
            for line in text_lines[:5]:
                pdf.drawString(inner_x, inner_y - offset, line)
                offset += 12

    def _draw_empty_state(self, pdf: canvas.Canvas, spine_x: float, y: float) -> None:
        pdf.setFillColor(colors.HexColor("#94a3b8"))
        pdf.setFont("Helvetica-Oblique", 12)
        pdf.drawCentredString(spine_x, y, "No events recorded yet. Add events to preview the timeline.")


def build_timeline_pdf(events: Iterable[dict]) -> io.BytesIO:
    """Public helper used by FastAPI route."""
    return TimelinePdfBuilder(events).build()
