from __future__ import annotations

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_pdf_report(
    *,
    company_name: str,
    assessment_name: str,
    framework_name: str,
    responses,
    domain_scores,
    executive_summary=None,
    recommendations=None,
):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>GRC Assessment Report</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"<b>Company:</b> {company_name}", styles["Normal"]))
    story.append(Paragraph(f"<b>Assessment:</b> {assessment_name}", styles["Normal"]))
    story.append(Paragraph(f"<b>Framework:</b> {framework_name}", styles["Normal"]))
    story.append(Spacer(1, 16))

    story.append(Paragraph("<b>Domain Scores</b>", styles["Heading2"]))
    if domain_scores:
        table_data = [["Domain", "Score"]]
        for domain_name, score in domain_scores.items():
            table_data.append([str(domain_name), str(score)])

        table = Table(table_data, colWidths=[330, 100])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        story.append(table)
    else:
        story.append(Paragraph("No domain scores available.", styles["Normal"]))

    story.append(Spacer(1, 16))
    story.append(Paragraph("<b>Executive Summary</b>", styles["Heading2"]))
    if executive_summary:
        if getattr(executive_summary, "summary_text", ""):
            story.append(Paragraph(getattr(executive_summary, "summary_text"), styles["BodyText"]))
            story.append(Spacer(1, 8))
        if getattr(executive_summary, "strengths_text", ""):
            story.append(Paragraph("<b>Strengths</b>", styles["Heading3"]))
            story.append(Paragraph(getattr(executive_summary, "strengths_text"), styles["BodyText"]))
            story.append(Spacer(1, 8))
        if getattr(executive_summary, "gaps_text", ""):
            story.append(Paragraph("<b>Gaps</b>", styles["Heading3"]))
            story.append(Paragraph(getattr(executive_summary, "gaps_text"), styles["BodyText"]))
            story.append(Spacer(1, 8))
        if getattr(executive_summary, "recommendations_text", ""):
            story.append(Paragraph("<b>Management Recommendations</b>", styles["Heading3"]))
            story.append(Paragraph(getattr(executive_summary, "recommendations_text"), styles["BodyText"]))
    else:
        story.append(Paragraph("No executive summary available.", styles["Normal"]))

    story.append(Spacer(1, 16))
    story.append(Paragraph("<b>Recommendations</b>", styles["Heading2"]))
    if recommendations:
        rec_data = [["Priority", "Title", "Description", "Domain"]]
        for rec in recommendations:
            rec_data.append(
                [
                    getattr(rec, "priority", ""),
                    getattr(rec, "title", ""),
                    getattr(rec, "description", "") or "",
                    getattr(rec, "domain_name", "") or "",
                ]
            )

        rec_table = Table(rec_data, colWidths=[60, 140, 220, 80])
        rec_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.beige]),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        story.append(rec_table)
    else:
        story.append(Paragraph("No recommendations available.", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()