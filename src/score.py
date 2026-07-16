"""
Batch scoring: the production-style output the Customer Success team consumes.
Every customer gets a churn probability, a risk tier, and a suggested action.

Risk tiers (by probability):
  high   >= tuned threshold      -> personal outreach from success manager
  medium >= 0.5 * threshold      -> targeted email + usage guide
  low    otherwise               -> no action / monitor

Output: outputs/churn_scores.csv
"""
from pathlib import Path

import pandas as pd
from joblib import load

import pipeline as P

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"

ACTIONS = {
    "high": "Personal outreach from a success manager + retention offer",
    "medium": "Automated targeted email + onboarding/usage guide",
    "low": "No action — keep monitoring",
}


def tier(p: float, thr: float) -> str:
    if p >= thr:
        return "high"
    if p >= thr * 0.5:
        return "medium"
    return "low"


def main() -> None:
    bundle = load(OUT / "model.joblib")
    pre, model, thr = bundle["preprocessor"], bundle["model"], bundle["threshold"]

    # score the most recent snapshot batch (the test period = "this week's" batch)
    df = P.load()
    _, _, te = P.chronological_split(df)
    Xte, _ = P.xy(te)
    proba = model.predict_proba(pre.transform(Xte))[:, 1]

    out = te[["customer_id", "snapshot_date", "plan_type",
              "months_subscribed", "monthly_fee"]].copy()
    out["churn_probability"] = proba.round(4)
    out["risk_tier"] = [tier(p, thr) for p in proba]
    out["suggested_action"] = out["risk_tier"].map(ACTIONS)
    out = out.sort_values("churn_probability", ascending=False).reset_index(drop=True)

    out.to_csv(OUT / "churn_scores.csv", index=False)
    counts = out["risk_tier"].value_counts()
    print(f"scored {len(out)} customers")
    print(counts.to_string())
    print(f"\nhigh-risk sample:\n{out.head(5).to_string(index=False)}")
    print(f"\nsaved -> outputs/churn_scores.csv")


if __name__ == "__main__":
    main()
