# Customer Churn Prediction for a Subscription Business

Early-warning system that flags subscription customers likely to cancel within
30 days, so the retention team can intervene proactively. Implements the course
proposal end to end: data adaptation, modeling, evaluation, explainability,
batch scoring, and a business-impact + sensitivity analysis.

## Problem
Supervised binary classification. Target `churn_30d` (1 = cancels within 30 days).
Primary metric **F2-score** (recall-weighted — missing a churner costs more than a
false alert); AUC monitored for discriminative power. Time-based validation to
avoid leakage.

## Data
Base: public [Kaggle Telco Customer Churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)
(7,043 customers). Adapted to a SaaS scenario:
- Columns reinterpreted (`tenure`→months subscribed, `Contract`→plan type, …).
- Five synthetic engagement features (logins, features used, support tickets,
  days since last interaction, usage change) — conditioned on the churn label with
  heavy overlap + ~8% label noise. See [`reports/feature_notes.md`](reports/feature_notes.md).
- Churners downsampled to a realistic **5%** churn rate → **5,446 customers, 5.0%**.
  *(Kept all non-churners; the proposal's "~7,000" isn't reachable at 5% given only
  5,174 non-churners — documented honestly.)*

## Results (test set)
| Model | F2 | AUC | Recall | Precision |
|---|---|---|---|---|
| Logistic Regression | 0.56 | 0.94 | 0.87 | 0.23 |
| Random Forest (best) | 0.58 | 0.93 | 0.84 | 0.26 |
| XGBoost | 0.53 | 0.93 | 0.78 | 0.23 |

Meets the proposal targets (AUC > 0.80, recall > 0.75). Low precision is expected
at a 5% base rate with a recall-first threshold.

## Business impact
The 20% churn-reduction target is **derived**: `reduction = recall × intervention_success_rate`
(0.84 × ~24% ≈ 20%). Proposal-aligned P&L reproduces **~€22k year 1 / €42k year 2+**.
A sensitivity analysis varies the success rate; a second lens shows that per-contact
outreach cost (driven by precision) can flip ROI negative — so **precision / top-N
targeting** is the key lever before scaling outreach.

## Run it
```bash
pip install -r requirements.txt
python src/data_prep.py        # build data/processed/saas_churn.csv
python src/eda.py              # outputs/eda/*.png
python src/train.py            # model.joblib, metrics.json, figures
python src/explain.py          # SHAP figures
python src/score.py            # outputs/churn_scores.csv
python src/business_impact.py  # business_impact.json, sensitivity figure
```
Or open the executed **`churn_prediction.ipynb`** (rebuild with `python build_notebook.py`).

## Live demo
Interactive web app to query the trained model for a single customer and get a
probability, risk tier, suggested action and a per-request explanation of the
top drivers:
```bash
python app.py   # http://127.0.0.1:5000
```
Use the **at-risk** / **loyal** example buttons to see a high- vs low-risk prediction.

## Layout
```
data/raw|processed   • src/*.py   • outputs/ (metrics, model, scores, figures)
reports/feature_notes.md   • churn_prediction.ipynb   • requirements.txt
```
