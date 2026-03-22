from __future__ import annotations

from app.exports.excel_export import generate_excel_report
from app.exports.pdf_export import generate_pdf_report
from app.exports.word_export import generate_word_report
from app.services.auth import require_role


class ExportService:
    def __init__(self, session):
        self.session = session

    def export_pdf(
        self,
        actor,
        *,
        company,
        assessment,
        responses,
        domain_scores,
        executive_summary=None,
        recommendations=None,
    ):
        require_role(actor, "viewer")

        return generate_pdf_report(
            company_name=company.name,
            assessment_name=assessment.name,
            framework_name=assessment.framework_name,
            responses=responses or [],
            domain_scores=domain_scores or {},
            executive_summary=executive_summary,
            recommendations=recommendations or [],
        )

    def export_word(
        self,
        actor,
        *,
        company,
        assessment,
        responses,
        domain_scores,
        executive_summary=None,
        recommendations=None,
    ):
        require_role(actor, "viewer")

        return generate_word_report(
            company_name=company.name,
            assessment_name=assessment.name,
            framework_name=assessment.framework_name,
            responses=responses or [],
            domain_scores=domain_scores or {},
            executive_summary=executive_summary,
            recommendations=recommendations or [],
        )

    def export_excel(
        self,
        actor,
        *,
        company,
        assessment,
        responses,
        domain_scores,
        executive_summary=None,
        recommendations=None,
    ):
        require_role(actor, "viewer")

        return generate_excel_report(
            company_name=company.name,
            assessment_name=assessment.name,
            framework_name=assessment.framework_name,
            responses=responses or [],
            domain_scores=domain_scores or {},
            executive_summary=executive_summary,
            recommendations=recommendations or [],
        )