"""
Train and evaluate churn models.

- Chronological train/val/test split (from pipeline.py).
- SMOTE applied to the TRAIN fold only, after preprocessing.
- Models: Logistic Regression (baseline), Random Forest, XGBoost.
- Primary metric: F2-score (recall-weighted). The decision threshold is tuned on
  the validation set to maximise F2, then frozen for the test evaluation.
- Best model + preprocessor + threshold are persisted for scoring/SHAP.

Outputs: outputs/metrics.json, outputs/figures/*.png, outputs/model.joblib
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from imblearn.over_sampling import SMOTE
from joblib import dump
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay, fbeta_score, precision_recall_curve,
    precision_score, recall_score, roc_auc_score,
)
from xgboost import XGBClassifier

import pipeline as P

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
FIG = OUT / "figures"
SEED = 42


def tune_threshold(y_true, proba):
    """Pick the probability cutoff that maximises F2 on the given set."""
    prec, rec, thr = precision_recall_curve(y_true, proba)
    # precision_recall_curve returns one more point than thresholds
    f2 = (5 * prec * rec) / (4 * prec + rec + 1e-12)
    best = np.nanargmax(f2[:-1])
    return float(thr[best]), float(f2[best])


def evaluate(name, model, Xv, yv, Xt, yt):
    """Tune threshold on val, report metrics on test."""
    pv = model.predict_proba(Xv)[:, 1]
    pt = model.predict_proba(Xt)[:, 1]
    thr, _ = tune_threshold(yv, pv)
    yhat = (pt >= thr).astype(int)
    return {
        "model": name,
        "threshold": round(thr, 3),
        "f2": round(fbeta_score(yt, yhat, beta=2), 3),
        "auc": round(roc_auc_score(yt, pt), 3),
        "recall": round(recall_score(yt, yhat), 3),
        "precision": round(precision_score(yt, yhat, zero_division=0), 3),
    }, pt, yhat


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    df = P.load()
    tr, va, te = P.chronological_split(df)
    print(f"split rows  train={len(tr)} val={len(va)} test={len(te)}")
    print(f"churn rate  train={tr[P.TARGET].mean():.2%} "
          f"val={va[P.TARGET].mean():.2%} test={te[P.TARGET].mean():.2%}")

    Xtr, ytr = P.xy(tr)
    Xva, yva = P.xy(va)
    Xte, yte = P.xy(te)

    pre = P.build_preprocessor()
    Xtr_p = pre.fit_transform(Xtr)
    Xva_p = pre.transform(Xva)
    Xte_p = pre.transform(Xte)

    # SMOTE on train only -> balances the 5% minority before fitting
    Xtr_bal, ytr_bal = SMOTE(random_state=SEED).fit_resample(Xtr_p, ytr)
    print(f"train after SMOTE: {np.bincount(ytr_bal)}")

    n_neg, n_pos = np.bincount(ytr)
    models = {
        "logreg": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "random_forest": RandomForestClassifier(
            n_estimators=400, max_depth=8, min_samples_leaf=5,
            class_weight="balanced", random_state=SEED, n_jobs=-1),
        "xgboost": XGBClassifier(
            n_estimators=400, max_depth=4, learning_rate=0.05,
            subsample=0.9, colsample_bytree=0.9,
            scale_pos_weight=n_neg / n_pos, eval_metric="logloss",
            random_state=SEED, n_jobs=-1),
    }

    results, fitted, probas = [], {}, {}
    for name, model in models.items():
        # LogReg/XGB train on SMOTE-balanced data; RF uses class_weight on raw.
        if name == "random_forest":
            model.fit(Xtr_p, ytr)
        else:
            model.fit(Xtr_bal, ytr_bal)
        row, pt, yhat = evaluate(name, model, Xva_p, yva, Xte_p, yte)
        results.append(row)
        fitted[name] = model
        probas[name] = (pt, yhat)
        print(row)

    # pick best by F2 (primary), AUC as tie-breaker
    best = max(results, key=lambda r: (r["f2"], r["auc"]))["model"]
    print(f"\nbest model = {best}")

    # PR curves
    fig, ax = plt.subplots(figsize=(7, 5.5))
    for name in models:
        pt, _ = probas[name]
        prec, rec, _ = precision_recall_curve(yte, pt)
        ax.plot(rec, prec, label=f"{name} (AUC={next(r['auc'] for r in results if r['model']==name)})")
    ax.axhline(yte.mean(), ls="--", c="grey", label=f"baseline ({yte.mean():.2%})")
    ax.set(xlabel="Recall", ylabel="Precision", title="Precision-Recall (test)")
    ax.legend()
    fig.tight_layout(); fig.savefig(FIG / "pr_curves.png", dpi=110); plt.close(fig)

    # confusion matrix for best
    _, yhat_best = probas[best]
    fig, ax = plt.subplots(figsize=(4.5, 4))
    ConfusionMatrixDisplay.from_predictions(yte, yhat_best, ax=ax, colorbar=False)
    ax.set_title(f"Confusion matrix — {best} (test)")
    fig.tight_layout(); fig.savefig(FIG / "confusion_matrix.png", dpi=110); plt.close(fig)

    # persist best model bundle for scoring + SHAP
    thr = next(r["threshold"] for r in results if r["model"] == best)
    dump({"preprocessor": pre, "model": fitted[best], "threshold": thr,
          "best": best, "feature_names": P.feature_names(pre)},
         OUT / "model.joblib")
    (OUT / "metrics.json").write_text(json.dumps(
        {"results": results, "best": best,
         "test_churn_rate": round(float(yte.mean()), 4)}, indent=2))
    print(f"\nsaved -> outputs/model.joblib, outputs/metrics.json, figures/")


if __name__ == "__main__":
    main()
