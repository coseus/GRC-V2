from __future__ import annotations

import streamlit as st

from app.charts.scoring import calculate_scores
from app.db.session import get_session
from app.services.backup_service import BackupService
from app.services.executive import ExecutiveService
from app.services.export_service import ExportService
from app.services.recommendations import RecommendationService


def render_import_export_section(data, lang, user, company, assessment, assessment_state):
    if not user:
        st.error("Authentication required")
        return

    st.header("Import / Export")

    session = get_session()
    executive_service = ExecutiveService(session)
    export_service = ExportService(session)
    recommendation_service = RecommendationService(session)
    backup_service = BackupService(session)

    try:
        responses = (assessment_state or {}).get("responses_saved", [])
        domain_scores = calculate_scores(responses)

        summary = executive_service.get(user, assessment.id)
        recommendations = recommendation_service.list_for_assessment(user, assessment.id)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Generate recommendations", key=f"gen_reco_{assessment.id}"):
                try:
                    recommendation_service.regenerate_from_scores(
                        user,
                        assessment.id,
                        domain_scores,
                    )
                    st.success("Recommendations generated.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

        with col2:
            st.caption(f"Recommendations: {len(recommendations)}")

        st.write("### Current domain scores")
        if domain_scores:
            st.json(domain_scores)
        else:
            st.info("Nu exista suficiente raspunsuri pentru calculul scorurilor.")

        st.write("### Executive summary preview")
        if summary:
            st.text_area(
                "Summary",
                value=summary.summary_text or "",
                height=120,
                disabled=True,
                key=f"summary_preview_{assessment.id}",
            )
            st.text_area(
                "Strengths",
                value=summary.strengths_text or "",
                height=100,
                disabled=True,
                key=f"strengths_preview_{assessment.id}",
            )
            st.text_area(
                "Gaps",
                value=summary.gaps_text or "",
                height=100,
                disabled=True,
                key=f"gaps_preview_{assessment.id}",
            )
            st.text_area(
                "Recommendations",
                value=summary.recommendations_text or "",
                height=120,
                disabled=True,
                key=f"recs_preview_{assessment.id}",
            )
        else:
            st.info("Nu exista executive summary salvat.")

        st.write("### Generated recommendations")
        if recommendations:
            for rec in recommendations:
                st.markdown(f"**[{rec.priority.upper()}] {rec.title}**")
                if rec.description:
                    st.write(rec.description)
        else:
            st.info("Nu exista recomandari generate.")

        st.write("### Export documente")
        pdf_bytes = export_service.export_pdf(
            user,
            company=company,
            assessment=assessment,
            responses=responses,
            domain_scores=domain_scores,
            executive_summary=summary,
            recommendations=recommendations,
        )
        word_bytes = export_service.export_word(
            user,
            company=company,
            assessment=assessment,
            responses=responses,
            domain_scores=domain_scores,
            executive_summary=summary,
            recommendations=recommendations,
        )
        excel_bytes = export_service.export_excel(
            user,
            company=company,
            assessment=assessment,
            responses=responses,
            domain_scores=domain_scores,
            executive_summary=summary,
            recommendations=recommendations,
        )

        c_pdf, c_word, c_excel = st.columns(3)
        with c_pdf:
            st.download_button(
                label="Descarca PDF",
                data=pdf_bytes,
                file_name=f"{company.name}_{assessment.name}.pdf".replace(" ", "_"),
                mime="application/pdf",
                key=f"download_pdf_{assessment.id}",
                use_container_width=True,
            )
        with c_word:
            st.download_button(
                label="Descarca Word",
                data=word_bytes,
                file_name=f"{company.name}_{assessment.name}.docx".replace(" ", "_"),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key=f"download_word_{assessment.id}",
                use_container_width=True,
            )
        with c_excel:
            st.download_button(
                label="Descarca Excel",
                data=excel_bytes,
                file_name=f"{company.name}_{assessment.name}.xlsx".replace(" ", "_"),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"download_excel_{assessment.id}",
                use_container_width=True,
            )

        st.write("### Export / Import JSON evaluare")
        json_bytes = backup_service.export_assessment_json(user, company, assessment)
        st.download_button(
            label="Descarca JSON evaluare",
            data=json_bytes,
            file_name=f"{company.name}_{assessment.name}.json".replace(" ", "_"),
            mime="application/json",
            key=f"download_json_{assessment.id}",
            use_container_width=True,
        )

        uploaded_json = st.file_uploader(
            "Importa JSON in evaluarea curenta",
            type=["json"],
            key=f"upload_json_{assessment.id}",
        )
        if uploaded_json is not None:
            if st.button("Importa JSON", key=f"btn_import_json_{assessment.id}"):
                try:
                    backup_service.import_assessment_json(
                        user,
                        company=company,
                        assessment=assessment,
                        json_bytes=uploaded_json.read(),
                    )
                    st.success("JSON importat cu succes.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

        if getattr(user, "role", "") == "admin":
            st.write("### Backup / Restore baza de date")
            db_bytes = backup_service.export_sqlite_db(user)
            st.download_button(
                label="Descarca backup DB",
                data=db_bytes,
                file_name="assessment.db",
                mime="application/octet-stream",
                key="download_db_backup",
                use_container_width=True,
            )

            uploaded_db = st.file_uploader(
                "Restore DB SQLite",
                type=["db", "sqlite", "sqlite3"],
                key="upload_db_restore",
            )
            if uploaded_db is not None:
                if st.button("Restore DB", key="btn_restore_db"):
                    try:
                        backup_service.import_sqlite_db(user, uploaded_db.read())
                        st.success("DB restaurata. Reincarca aplicatia.")
                    except Exception as exc:
                        st.error(str(exc))

    finally:
        session.close()