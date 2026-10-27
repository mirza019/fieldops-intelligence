from __future__ import annotations

from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from analytics.kpis import KPI_CATALOG


def build_management_report(
    values: dict[str, float | None],
    output: Path | None = None,
    period: str = "Current synthetic snapshot",
) -> bytes:
    buffer = BytesIO()
    document = SimpleDocTemplate(
        str(output) if output else buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="FieldOps Intelligence Management Report",
    )
    styles = getSampleStyleSheet()
    story = [
        Spacer(1, 30 * mm),
        Paragraph("FieldOps Intelligence", styles["Title"]),
        Paragraph("Management Performance Report", styles["Heading1"]),
        Paragraph(f"Reporting period: {period}", styles["BodyText"]),
        Paragraph("Source: governed synthetic analytical snapshot", styles["BodyText"]),
        Paragraph(
            "AI commentary is deterministic demo narrative; all figures originate from calculated KPI evidence.",
            styles["BodyText"],
        ),
        PageBreak(),
        Paragraph("Executive KPI Scorecard", styles["Heading1"]),
    ]
    rows = [["KPI", "Actual", "Target", "Status"]]
    for code, value in values.items():
        spec = KPI_CATALOG.get(code)
        if not spec:
            continue
        actual = (
            "N/A" if value is None else (f"{value:.1%}" if spec.unit == "%" else f"{value:,.1f}")
        )
        target = f"{spec.target:.1%}" if spec.unit == "%" else f"{spec.target:,.1f}"
        favorable = value is not None and (
            value >= spec.target if spec.better == "higher" else value <= spec.target
        )
        rows.append(
            [f"{code} - {spec.name}", actual, target, "On target" if favorable else "Attention"]
        )
    scorecard = Table(rows, colWidths=[86 * mm, 28 * mm, 28 * mm, 28 * mm], repeatRows=1)
    scorecard.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#10333A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C8D4D9")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6F7")]),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.extend(
        [
            scorecard,
            Spacer(1, 8 * mm),
            Paragraph("Management interpretation", styles["Heading2"]),
            Paragraph(
                "Review attention items with regional, service-type, parts-delay, and repeat-visit evidence. Observed association does not establish that an intervention caused subsequent KPI movement.",
                styles["BodyText"],
            ),
            Paragraph("Recommended next step", styles["Heading2"]),
            Paragraph(
                "Open a manager-reviewed DMAIC case for the largest verified contributor, assign an owner and due date, and compare results with an explicit baseline and control period.",
                styles["BodyText"],
            ),
        ]
    )

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#52656B"))
        canvas.drawString(18 * mm, 10 * mm, "Synthetic portfolio data - not operational advice")
        canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {doc.page}")
        canvas.restoreState()

    document.build(story, onFirstPage=footer, onLaterPages=footer)
    return output.read_bytes() if output else buffer.getvalue()
