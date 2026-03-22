import pandas as pd

def generate_roadmap_csv(recommendations: list[dict]) -> str:
    df = pd.DataFrame(recommendations)
    if df.empty:
        return ""
    for c in ["risk","responsible","deadline","domain_name","text","status","source"]:
        if c not in df.columns:
            df[c] = ""
    order = {"Critical":1,"High":2,"Medium":3,"Low":4}
    df["_risk_order"] = df["risk"].map(order).fillna(99)
    df = df.sort_values(by=["_risk_order","responsible","deadline","domain_name","text"])
    df = df.rename(columns={"risk":"Risk","responsible":"Owner","deadline":"Deadline","domain_name":"Domain","text":"Recommendation","status":"Status","source":"Source"})
    return df[["Risk","Owner","Deadline","Domain","Recommendation","Status","Source"]].to_csv(index=False)
