"""Generate the deliverable notebook churn_prediction.ipynb from the src modules."""
from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parent
nb = nbf.v4.new_notebook()
c = []
md = lambda s: c.append(nbf.v4.new_markdown_cell(s))
code = lambda s: c.append(nbf.v4.new_code_cell(s))

md("""# Customer Churn Prediction for a Subscription Business
End-to-end implementation of the proposal: supervised binary classification to
flag customers likely to cancel within 30 days, with SMOTE for class imbalance,
F2-optimised thresholds, SHAP explanations, batch scoring, and a business-impact
& sensitivity analysis.

**Pipeline:** `data_prep` → `eda` → `train` → `explain` → `score` → `business_impact`.""")

md("## 0. Setup")
code("""import sys, json
sys.path.append('src')
import pandas as pd
from IPython.display import Image, display
pd.set_option('display.max_columns', 30)""")

md("""## 1. Data preparation
Real Kaggle **Telco Customer Churn** (7,043 rows) adapted to a SaaS scenario:
columns reinterpreted, five synthetic engagement features added (conditioned on
the churn label, with overlap + label noise), churners downsampled to a realistic
**5%** churn rate. See `reports/feature_notes.md` for feature realism.""")
code("""import data_prep; data_prep.main()
df = pd.read_csv('data/processed/saas_churn.csv')
print('churn rate:', round(df['churn_30d'].mean(), 4))
df.head()""")

md("""## 2. Exploratory analysis
Engagement features separate churners; monthly plans and short tenure churn most.""")
code("""import eda; eda.main()
for f in ['engagement_by_churn','churn_by_segment','target_correlation']:
    display(Image(f'outputs/eda/{f}.png'))""")

md("""## 3. Modeling & evaluation
Chronological train/val/test split (no leakage), SMOTE on train only. Three models;
the decision threshold is tuned on validation to maximise **F2** (recall-weighted).
Target from the proposal: **AUC > 0.80, churner recall > 0.75**.""")
code("""import train; train.main()
metrics = json.loads(open('outputs/metrics.json').read())
display(pd.DataFrame(metrics['results']))
print('best model:', metrics['best'])
for f in ['pr_curves','confusion_matrix']:
    display(Image(f'outputs/figures/{f}.png'))""")

md("""## 4. Interpretability (SHAP)
Global drivers and an individual explanation, so the retention team knows *why*
a customer is flagged.""")
code("""import explain; explain.main()
for f in ['shap_summary','shap_customer']:
    display(Image(f'outputs/figures/{f}.png'))""")

md("""## 5. Batch scoring output
The production-style table the Customer Success team consumes: probability, risk
tier, and a suggested action per customer.""")
code("""import score; score.main()
pd.read_csv('outputs/churn_scores.csv').head(10)""")

md("""## 6. Business impact & sensitivity
The 20% churn-reduction target is **derived**, not assumed:
`reduction = recall × intervention_success_rate`. We vary the success rate, and
separately show how false-positive outreach cost (driven by precision) erodes ROI —
directly addressing the reviewer's feedback.""")
code("""import business_impact; business_impact.main()
bi = json.loads(open('outputs/business_impact.json').read())
display(pd.DataFrame(bi['scenarios']))
display(pd.DataFrame(bi['outreach_sensitivity']))
display(Image('outputs/figures/sensitivity.png'))""")

md("""## 7. Conclusions
- The model meets the proposal's technical targets (AUC ≈ 0.93, churner recall ≈ 0.84).
- At a 5% base rate, a recall-first threshold flags many false positives (low
  precision) — the retention **discount** model still yields the proposal's
  ~€22k Y1 / €42k Y2+, but adding per-contact outreach cost turns ROI negative,
  so **precision / top-N targeting is the key lever** before scaling outreach.
- Synthetic features are literature-grounded but simplified; production telemetry
  (events, support, billing, logged outcomes) would replace them and let the
  intervention-success rate be measured rather than assumed.""")

nb["cells"] = c
out = ROOT / "churn_prediction.ipynb"
nbf.write(nb, out)
print("wrote", out.name)
