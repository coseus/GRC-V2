from app.frameworks.loader import load_framework_data

def filter_framework_by_control_types(data: dict, selected_types: list[str]) -> dict:
    if not selected_types:
        return data
    domains = []
    for domain in data["domains"]:
        questions = [q for q in domain["questions"] if q.get("control_type") in selected_types]
        if questions:
            d = dict(domain)
            d["questions"] = questions
            domains.append(d)
    return {"meta": data["meta"], "domains": domains}

def load_and_filter_framework(framework_code: str, selected_types: list[str] | None = None):
    data = load_framework_data(framework_code)
    return filter_framework_by_control_types(data, selected_types or [])
