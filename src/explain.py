"""
SHAP interpretability for the persisted best model.
Produces a global feature-importance summary and one individual explanation,
so the retention team can see WHY a customer is flagged.

Outputs: outputs/figures/shap_summary.png, outputs/figures/shap_customer.png
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from joblib import load

import pipeline as P

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
FIG = OUT / "figures"


def main() -> None:
    bundle = load(OUT / "model.joblib")
    pre, model, names = bundle["preprocessor"], bundle["model"], bundle["feature_names"]

    df = P.load()
    _, _, te = P.chronological_split(df)
    Xte, _ = P.xy(te)
    Xte_p = pre.transform(Xte)
    Xdf = pd.DataFrame(Xte_p, columns=names)

    explainer = shap.TreeExplainer(model)
    sv = explainer.shap_values(Xdf)
    # binary tree models may return a list [neg, pos]; take the positive class
    if isinstance(sv, list):
        sv = sv[1]
    if sv.ndim == 3:
        sv = sv[:, :, 1]

    shap.summary_plot(sv, Xdf, show=False, max_display=12)
    plt.title(f"SHAP global importance — {bundle['best']}")
    plt.tight_layout(); plt.savefig(FIG / "shap_summary.png", dpi=110); plt.close()

    # explain the single highest-risk customer in the test set
    proba = model.predict_proba(Xte_p)[:, 1]
    i = int(np.argmax(proba))
    base = explainer.expected_value
    base = base[1] if isinstance(base, (list, np.ndarray)) and np.ndim(base) else float(base)
    shap.plots._waterfall.waterfall_legacy(
        base, sv[i], feature_names=names, max_display=12, show=False)
    plt.title(f"Why customer {te.iloc[i]['customer_id']} is high-risk "
              f"(p={proba[i]:.2f})")
    plt.tight_layout(); plt.savefig(FIG / "shap_customer.png", dpi=110,
                                    bbox_inches="tight"); plt.close()

    order = np.argsort(np.abs(sv).mean(0))[::-1][:8]
    print("top drivers:", [names[j] for j in order])
    print(f"figures saved -> {FIG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
