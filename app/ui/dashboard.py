from __future__ import annotations

import streamlit as st

from app.charts.dashboard import generate_bar_chart
from app.charts.scoring import (
    calculate_overall_score,
    calculate_scores,
    get_maturity_level,
)


def _normalize_responses(state):
    if not state:
        return {}

    responses = state.get("responses_saved", {})

    if isinstance(responses, dict):
        return responses

    if isinstance(responses, list):
        normalized = {}
        for idx, item in enumerate(responses):
            if isinstance(item, dict):
                key = item.get("question_code") or item.get("id") or f"q_{idx}"
                normalized[key] = item
        return normalized

    return {}


def render_dashboard_section(data, lang, actor, company, assessment, assessment_state):
    if not actor:
        st.error("Authentication required")
        return

    st.header("Executive Dashboard")

    responses = _normalize_responses(assessment_state)
    if not responses:
        st.info("Nu exista raspunsuri salvate pentru aceasta evaluare.")
        return

    domain_scores = calculate_scores(responses)
    overall = calculate_overall_score(domain_scores)

    c1, c2 = st.columns(2)
    c1.metric("Overall score", f"{overall:.1f}/100")
    c2.metric("Maturity", get_maturity_level(overall))

    if domain_scores:
        st.image(generate_bar_chart(domain_scores), use_container_width=True)
    else:
        st.info("Nu au putut fi calculate scorurile pe domenii.")