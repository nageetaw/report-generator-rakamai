from typing import List, Dict
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

from app.services.report_generation.base import BaseReportExporter


class PDFReportGenerator(BaseReportExporter):
    def export(self, *, transcript: str, notes: str, output_path: str) -> None:
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40,
        )

        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("Meeting Notes", styles["Title"]))
        story.append(Spacer(1, 0.3 * inch))

        story.extend(self._block(notes, styles))
        story.append(Spacer(1, 0.4 * inch))

        story.append(Paragraph("Transcript", styles["Heading2"]))
        story.append(Spacer(1, 0.2 * inch))
        story.extend(self._block(transcript, styles))

        doc.build(story)

    def _block(self, text: str, styles: Dict) -> List:
        blocks = []
        for line in text.splitlines():
            if line.strip():
                blocks.append(Paragraph(line, styles["Normal"]))
                blocks.append(Spacer(1, 0.15 * inch))
        return blocks
