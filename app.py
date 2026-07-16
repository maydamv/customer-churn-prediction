"""
Demo web app: query the trained churn model interactively.

Loads outputs/model.joblib (preprocessor + best model + tuned F2 threshold),
serves a form, and returns churn probability, risk tier, suggested action and a
per-request explanation (top features pushing the prediction up/down).

Run:  python app.py   ->  http://127.0.0.1:5000
"""
from pathlib import Path

import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request
from joblib import load

ROOT = Path(__file__).resolve().parent
BUNDLE = load(ROOT / "outputs" / "model.joblib")
PRE = BUNDLE["preprocessor"]
MODEL = BUNDLE["model"]
THRESHOLD = BUNDLE["threshold"]
FEATURE_NAMES = BUNDLE["feature_names"]
BEST = BUNDLE["best"]

RAW_COLUMNS = [
    "months_subscribed", "monthly_fee", "total_spend", "addon_services",
    "paperless_billing", "is_senior", "has_partner", "has_dependents",
    "logins_30d", "features_used", "open_tickets_30d",
    "days_since_last_interaction", "usage_change_pct",
    "plan_type", "payment_method",
]
NUMERIC = RAW_COLUMNS[:13]

ACTIONS = {
    "high": "Personal outreach from a success manager + retention offer",
    "medium": "Automated targeted email + onboarding/usage guide",
    "low": "No action — keep monitoring",
}

# built once: SHAP explainer for the trained tree model (fast for a single row)
try:
    import shap
    EXPLAINER = shap.TreeExplainer(MODEL)
except Exception:  # pragma: no cover - explanation is optional
    EXPLAINER = None

app = Flask(__name__)


def tier(p: float) -> str:
    if p >= THRESHOLD:
        return "high"
    if p >= THRESHOLD * 0.5:
        return "medium"
    return "low"


def explain_row(X_transformed) -> list[dict]:
    """Return the features that pushed this prediction the most (signed)."""
    if EXPLAINER is None:
        return []
    try:
        sv = EXPLAINER.shap_values(X_transformed)
        if isinstance(sv, list):
            sv = sv[1]
        sv = np.asarray(sv)
        if sv.ndim == 3:
            sv = sv[:, :, 1]
        row = sv[0]
        order = np.argsort(np.abs(row))[::-1][:5]
        return [{"feature": FEATURE_NAMES[i], "impact": round(float(row[i]), 4)}
                for i in order]
    except Exception:
        return []


@app.get("/")
def index():
    return render_template("index.html", model_name=BEST, threshold=THRESHOLD)


@app.post("/predict")
def predict():
    data = request.get_json(force=True)
    row = {}
    for col in RAW_COLUMNS:
        val = data.get(col)
        if col in NUMERIC:
            val = float(val)
        row[col] = val
    X = pd.DataFrame([row], columns=RAW_COLUMNS)
    Xt = PRE.transform(X)

    proba = float(MODEL.predict_proba(Xt)[:, 1][0])
    t = tier(proba)
    return jsonify({
        "probability": round(proba, 4),
        "percent": round(proba * 100, 1),
        "risk_tier": t,
        "will_churn": bool(proba >= THRESHOLD),
        "suggested_action": ACTIONS[t],
        "threshold": THRESHOLD,
        "drivers": explain_row(Xt),
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
