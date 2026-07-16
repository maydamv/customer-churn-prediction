"""
Business impact and sensitivity analysis.

Directly addresses the reviewer's feedback: instead of asserting a fixed 20%
churn reduction, we DERIVE it from the model and run a sensitivity analysis.

Derivation
----------
Reduction in churn = recall x intervention_success_rate
  - recall (from the test set): share of real churners the model flags as high-risk
  - intervention_success_rate (s): share of correctly-flagged churners actually
    retained by the offered action (a business assumption, varied below)

Cost model (per month, scaled to a 10,000-subscriber base)
  - at-risk churners           = base * monthly_churn         = 500
  - true churners flagged      = 500 * recall
  - total high-risk flagged    = flagged_true / precision      (includes false positives)
  - intervention cost          = flagged_total * cost_per_intervention  (we pay for every contact)
  - customers saved            = flagged_true * s
Annual P&L
  - revenue retained           = saved * ARPU * 12
  - minus intervention cost, system opex (500/mo), and (year 1) 20k setup
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"

# assumptions from the proposal
BASE = 10_000
CHURN = 0.05
ARPU = 50
COST_PER_INTERVENTION = 10       # per flagged customer / month
SETUP = 20_000
OPEX_MONTHLY = 500
LIFETIME_MONTHS = 12             # a saved customer keeps paying ~12 more months


def scenario(recall, precision, s, outreach_unit=0.0):
    """
    Proposal-aligned P&L: the recurring €10 is the discount given to a RETAINED
    customer (folded into their margin), matching the submitted document.
    `outreach_unit` optionally adds a one-time cost per high-risk contact
    (including false positives) to expose the precision sensitivity.
    """
    at_risk = BASE * CHURN
    flagged_true = at_risk * recall
    flagged_total = flagged_true / max(precision, 1e-6)
    saved = flagged_true * s

    net_margin_annual = saved * (ARPU - COST_PER_INTERVENTION) * 12
    opex_annual = OPEX_MONTHLY * 12
    outreach_annual = flagged_total * outreach_unit * 12  # 0 in the base model

    net_y1 = net_margin_annual - opex_annual - outreach_annual - SETUP
    net_y2 = net_margin_annual - opex_annual - outreach_annual
    total_cost_y1 = opex_annual + outreach_annual + SETUP
    return {
        "intervention_success_rate": round(s, 2),
        "churn_reduction_pct": round(saved / at_risk * 100, 1),
        "customers_saved_per_month": round(saved, 1),
        "flagged_per_month": round(flagged_total, 0),
        "net_benefit_year1": round(net_y1),
        "net_benefit_year2plus": round(net_y2),
        "roi_year1_pct": round(net_y1 / total_cost_y1 * 100),
    }


def main() -> None:
    metrics = json.loads((OUT / "metrics.json").read_text())
    best = next(r for r in metrics["results"] if r["model"] == metrics["best"])
    recall, precision = best["recall"], best["precision"]
    print(f"using {metrics['best']}: recall={recall} precision={precision}\n")

    rates = [0.15, 0.20, 0.24, 0.30, 0.40]
    rows = [scenario(recall, precision, s) for s in rates]

    hdr = ["success_rate", "churn_reduction%", "saved/mo", "flagged/mo",
           "net_Y1(EUR)", "net_Y2+(EUR)", "ROI_Y1%"]
    print(" | ".join(f"{h:>16}" for h in hdr))
    for r in rows:
        print(" | ".join(f"{v:>16}" for v in [
            r["intervention_success_rate"], r["churn_reduction_pct"],
            r["customers_saved_per_month"], r["flagged_per_month"],
            r["net_benefit_year1"], r["net_benefit_year2plus"], r["roi_year1_pct"]]))

    # central case ~= the proposal's 20% target
    central = min(rows, key=lambda r: abs(r["churn_reduction_pct"] - 20))
    print(f"\n~20% reduction is reached at success_rate="
          f"{central['intervention_success_rate']} "
          f"(recall {recall} x {central['intervention_success_rate']} "
          f"= {round(recall*central['intervention_success_rate']*100)}%)")

    # second lens: how one-time outreach cost per contact erodes the base ROI
    # (precision matters — we contact ~1/precision customers per real churner)
    print("\nprecision sensitivity (central success rate, adding outreach cost):")
    print(f"{'outreach/contact(EUR)':>24} | {'net_Y1(EUR)':>12} | {'ROI_Y1%':>8}")
    outreach_rows = []
    for unit in [0, 5, 10, 20]:
        r = scenario(recall, precision, central["intervention_success_rate"], unit)
        outreach_rows.append({"outreach_unit": unit, **r})
        print(f"{unit:>24} | {r['net_benefit_year1']:>12} | {r['roi_year1_pct']:>8}")

    # sensitivity figure
    fig, ax = plt.subplots(figsize=(8, 5))
    xs = [r["churn_reduction_pct"] for r in rows]
    ax.plot(xs, [r["net_benefit_year1"] for r in rows], "o-", label="Net benefit Y1")
    ax.plot(xs, [r["net_benefit_year2plus"] for r in rows], "s-", label="Net benefit Y2+")
    ax.axhline(0, color="grey", ls="--")
    ax.axvline(central["churn_reduction_pct"], color="#d1495b", ls=":",
               label="~20% target")
    ax.set(xlabel="Churn reduction (%)", ylabel="Annual net benefit (EUR)",
           title="Sensitivity of ROI to intervention effectiveness")
    ax.legend(); fig.tight_layout()
    fig.savefig(OUT / "figures" / "sensitivity.png", dpi=110); plt.close(fig)

    (OUT / "business_impact.json").write_text(json.dumps(
        {"model": metrics["best"], "recall": recall, "precision": precision,
         "scenarios": rows, "central_case": central,
         "outreach_sensitivity": outreach_rows}, indent=2))
    print("\nsaved -> outputs/business_impact.json, figures/sensitivity.png")


if __name__ == "__main__":
    main()
