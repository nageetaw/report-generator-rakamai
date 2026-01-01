from typing import List, Dict
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.platypus import ListFlowable, ListItem


class PDFReportGenerator:
    """Utility to build PDF reports from transcript and structured notes."""

    def _section(self, title: str, items: List, styles: Dict) -> List:
        """Create a titled section with bullet items for the PDF story."""

        blocks = []

        blocks.append(Paragraph(title, styles["Heading2"]))
        blocks.append(Spacer(1, 0.15 * inch))

        if items:
            blocks.append(
                ListFlowable(
                    [
                        ListItem(Paragraph(item, styles["Normal"]), leftIndent=15)
                        for item in items
                    ],
                    bulletType="bullet",
                    start="circle",
                )
            )
        else:
            blocks.append(Paragraph("None.", styles["Normal"]))

        blocks.append(Spacer(1, 0.3 * inch))
        return blocks

    def export(self, *, transcript: str, notes: dict, output_path: str) -> None:
        """Render the full report PDF at `output_path` using `notes` and `transcript`."""

        doc = SimpleDocTemplate(output_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph(notes["title"], styles["Title"]))
        story.append(Spacer(1, 0.4 * inch))

        story.extend(
            self._section("Topics Discussed", notes["topics_discussed"], styles)
        )

        story.extend(self._section("Decisions Made", notes["decisions_made"], styles))

        story.extend(self._section("Action Items", notes["action_items"], styles))

        story.extend(
            self._section("Key Points / Areas of Focus", notes["key_points"], styles)
        )

        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph("Transcript", styles["Heading2"]))
        story.append(Spacer(1, 0.2 * inch))

        for line in transcript.splitlines():
            story.append(Paragraph(line, styles["Normal"]))

        doc.build(story)

    def _block(self, text: str, styles: Dict) -> List:
        """Split text into paragraph blocks suitable for the PDF story."""

        blocks = []
        for line in text.splitlines():
            if line.strip():
                blocks.append(Paragraph(line, styles["Normal"]))
                blocks.append(Spacer(1, 0.15 * inch))
        return blocks
