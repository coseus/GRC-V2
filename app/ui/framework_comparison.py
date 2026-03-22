from __future__ import annotations

import streamlit as st

from app.db.session import get_session
from app.services.assessments import AssessmentService


def render_framework_comparison_section(actor, company, lang):
    if not actor:
        st.error("Utilizator neautentificat.")
        return

    session = get_session()
    service = AssessmentService(session)

    try:
        assessments = service.list_for_company(actor, company.id)

        st.subheader("Framework Comparison")

        if not assessments:
            st.info("Nu exista evaluari pentru aceasta companie.")
            return

        rows = []
        for item in assessments:
            rows.append(
                {
                    "ID": item.id,
                    "Name": item.name,
                    "Framework": item.framework_name,
                    "Code": item.framework_code,
                    "Version": item.framework_version,
                    "Status": item.status,
                    "Locked": "Yes" if item.is_locked else "No",
                    "Updated": item.updated_at.strftime("%Y-%m-%d %H:%M") if item.updated_at else "",
                }
            )

        st.dataframe(rows, use_container_width=True)
    except Exception as exc:
        st.error(str(exc))
    finally:
        session.close()