from __future__ import annotations

import streamlit as st

from app.db.session import get_session
from app.services.executive import ExecutiveService


def _normalize_responses(state):
    if not state:
        return []

    responses = state.get("responses_saved", {})

    if isinstance(responses, dict):
        return list(responses.values())

    if isinstance(responses, list):
        return responses

    return []


def _extract_selected_value(item):
    if isinstance(item, dict):
        return (item.get("selected_value") or item.get("value") or "").strip().lower()
    return ""


def _build_auto_summary(company, assessment, state):
    response_items = _normalize_responses(state)
    total_answers = len(response_items)

    yes_count = 0
    partial_count = 0
    no_count = 0
    na_count = 0

    for item in response_items:
        value = _extract_selected_value(item)

        if value == "yes":
            yes_count += 1
        elif value == "partial":
            partial_count += 1
        elif value == "no":
            no_count += 1
        elif value in {"n/a", "na", "not_applicable"}:
            na_count += 1

    summary = (
        f"Assessment '{assessment.name}' for company '{company.name}' contains "
        f"{total_answers} recorded answers. "
        f"Positive controls: {yes_count}, partial controls: {partial_count}, "
        f"negative controls: {no_count}, not applicable: {na_count}."
    )

    strengths = (
        f"- {yes_count} controls were marked as implemented.\n"
        f"- The assessment is structured under framework '{assessment.framework_name}'."
    )

    gaps = (
        f"- {no_count} controls were marked as not implemented.\n"
        f"- {partial_count} controls were marked as partially implemented."
    )

    recommendations = (
        "- Prioritize controls marked as 'no'.\n"
        "- Define remediation actions for controls marked as 'partial'.\n"
        "- Attach evidence and rationale for critical controls."
    )

    return summary, strengths, gaps, recommendations


def render_executive_section(data, lang, actor, company, assessment, state):
    if not actor:
        st.error("Authentication required")
        return

    st.header("Executive Summary")

    session = get_session()
    service = ExecutiveService(session)

    try:
        existing = service.get(actor, assessment.id)

        auto_summary, auto_strengths, auto_gaps, auto_recommendations = _build_auto_summary(
            company,
            assessment,
            state,
        )

        summary_text = st.text_area(
            "Summary",
            value=(existing.summary_text if existing and existing.summary_text else auto_summary),
            height=180,
            key=f"exec_summary_{assessment.id}",
        )

        strengths_text = st.text_area(
            "Strengths",
            value=(existing.strengths_text if existing and existing.strengths_text else auto_strengths),
            height=140,
            key=f"exec_strengths_{assessment.id}",
        )

        gaps_text = st.text_area(
            "Gaps",
            value=(existing.gaps_text if existing and existing.gaps_text else auto_gaps),
            height=140,
            key=f"exec_gaps_{assessment.id}",
        )

        recommendations_text = st.text_area(
            "Recommendations",
            value=(
                existing.recommendations_text
                if existing and existing.recommendations_text
                else auto_recommendations
            ),
            height=160,
            key=f"exec_recommendations_{assessment.id}",
        )

        if st.button("Save executive summary", key=f"btn_exec_save_{assessment.id}"):
            service.save(
                actor,
                assessment.id,
                summary_text=summary_text,
                strengths_text=strengths_text,
                gaps_text=gaps_text,
                recommendations_text=recommendations_text,
            )
            st.success("Executive summary saved.")
            st.rerun()

    except Exception as exc:
        st.error(str(exc))
    finally:
        session.close()