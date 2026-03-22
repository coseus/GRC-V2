from __future__ import annotations


def _normalize_responses(responses):
    if responses is None:
        return {}

    if isinstance(responses, dict):
        return responses

    if isinstance(responses, list):
        normalized = {}
        for idx, item in enumerate(responses):
            if not isinstance(item, dict):
                continue

            key = (
                item.get("question_code")
                or item.get("question_id")
                or item.get("id")
                or f"q_{idx}"
            )
            normalized[key] = item
        return normalized

    return {}


def calculate_scores(responses):
    responses = _normalize_responses(responses)

    domain_totals = {}
    domain_counts = {}

    for _, payload in responses.items():
        if not isinstance(payload, dict):
            continue

        domain_name = (
            payload.get("domain_name")
            or payload.get("domain")
            or payload.get("domain_code")
            or payload.get("domain_id")
            or "General"
        )

        score = payload.get("score")
        if score is None:
            continue

        try:
            numeric_score = float(score)
        except (TypeError, ValueError):
            continue

        weight = payload.get("weight", 1)
        try:
            weight = float(weight)
        except (TypeError, ValueError):
            weight = 1.0

        domain_totals[domain_name] = domain_totals.get(domain_name, 0.0) + (numeric_score * weight)
        domain_counts[domain_name] = domain_counts.get(domain_name, 0.0) + weight

    result = {}
    for domain_name, total in domain_totals.items():
        count = domain_counts.get(domain_name, 0.0)
        result[domain_name] = round(total / count, 2) if count else 0.0

    return result


def calculate_overall_score(domain_scores):
    if not domain_scores:
        return 0.0
    return round(sum(domain_scores.values()) / len(domain_scores), 2)


def get_maturity_level(score: float):
    if score >= 85:
        return "Optimized"
    if score >= 70:
        return "Managed"
    if score >= 50:
        return "Defined"
    if score >= 30:
        return "Developing"
    return "Initial"