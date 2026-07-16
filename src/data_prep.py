"""
Data preparation: adapt the public Telco Customer Churn dataset to a generic
digital-subscription (SaaS) churn scenario.

Steps
-----
1. Load raw Telco CSV and clean it (fix TotalCharges).
2. Reinterpret existing columns to a SaaS vocabulary.
3. Engineer 5 synthetic engagement features whose distributions are conditioned
   on the real churn label (with heavy overlap/noise so the task stays hard).
4. Downsample churners to bring the churn rate to ~5% (a healthy SaaS business).
5. Add a synthetic snapshot_date spread over 12 months to enable a time-based
   split downstream, and derive the target `churn_30d`.

The synthetic engagement features are documented in reports/feature_notes.md,
including how faithfully they represent real behaviour and what production data
would replace them.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "telco_churn.csv"
OUT = ROOT / "data" / "processed" / "saas_churn.csv"

SEED = 42
TARGET_CHURN_RATE = 0.05


def load_raw() -> pd.DataFrame:
    df = pd.read_csv(RAW)
    # TotalCharges has blank strings for tenure==0 customers -> coerce & impute.
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df["TotalCharges"] = df["TotalCharges"].fillna(df["MonthlyCharges"] * df["tenure"])
    df["churn"] = (df["Churn"] == "Yes").astype(int)
    return df


def reinterpret_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map Telco columns onto a generic SaaS subscription vocabulary."""
    plan_map = {"Month-to-month": "monthly", "One year": "annual", "Two year": "biennial"}
    out = pd.DataFrame(
        {
            "customer_id": df["customerID"],
            "months_subscribed": df["tenure"],          # tenure -> lifetime in months
            "monthly_fee": df["MonthlyCharges"],         # MonthlyCharges -> subscription fee
            "total_spend": df["TotalCharges"],
            "plan_type": df["Contract"].map(plan_map),   # Contract -> plan tier
            "payment_method": df["PaymentMethod"],
            "paperless_billing": (df["PaperlessBilling"] == "Yes").astype(int),
            "is_senior": df["SeniorCitizen"],
            "has_partner": (df["Partner"] == "Yes").astype(int),
            "has_dependents": (df["Dependents"] == "Yes").astype(int),
            # a proxy for product breadth: how many add-on services are active
            "addon_services": (
                df[["OnlineSecurity", "OnlineBackup", "DeviceProtection",
                    "TechSupport", "StreamingTV", "StreamingMovies"]] == "Yes"
            ).sum(axis=1),
            "churn": df["churn"],
        }
    )
    return out


def add_engagement_features(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """
    Generate behavioural signals the literature flags as the strongest churn
    predictors (García et al., 2018; Amin et al., 2019). Distributions differ by
    churn class but overlap heavily on purpose, so the model must combine signals
    rather than read a single give-away feature.
    """
    n = len(df)
    churn = df["churn"].to_numpy()

    def by_class(churn_params, stay_params, kind="normal"):
        out = np.empty(n)
        for label, (a, b) in [(1, churn_params), (0, stay_params)]:
            mask = churn == label
            k = mask.sum()
            if kind == "normal":
                out[mask] = rng.normal(a, b, k)
            elif kind == "poisson":
                out[mask] = rng.poisson(a, k)
        return out

    # Distributions overlap heavily on purpose: churners lean one way on average
    # but individual customers vary a lot, so no single feature is a give-away
    # and the model must combine several weak signals (realistic difficulty).

    # logins in last 30 days: churners log in somewhat less
    logins = by_class((11, 7), (16, 8))
    df["logins_30d"] = np.clip(np.round(logins), 0, None).astype(int)

    # key features used (out of 10): churners explore fewer
    feats = by_class((4.4, 2.7), (6.0, 2.6))
    df["features_used"] = np.clip(np.round(feats), 0, 10).astype(int)

    # open support tickets (30d): churners have slightly more unresolved issues
    df["open_tickets_30d"] = np.clip(
        by_class((0.95, 0), (0.5, 0), kind="poisson"), 0, None
    ).astype(int)

    # days since last interaction: churners drift away
    days = by_class((14, 11), (8, 8))
    df["days_since_last_interaction"] = np.clip(np.round(days), 0, None).astype(int)

    # % change in usage frequency vs previous period: churners decline
    usage_change = by_class((-14, 26), (2, 22))
    df["usage_change_pct"] = np.round(usage_change, 1)

    # Label noise: ~8% of customers behave against type (feature signals and
    # outcome disagree), capping achievable AUC at a believable level.
    flip = rng.random(n) < 0.08
    for col, (lo, hi) in {
        "logins_30d": (0, 30), "features_used": (0, 10),
        "open_tickets_30d": (0, 4), "days_since_last_interaction": (0, 45),
    }.items():
        noisy = rng.integers(lo, hi + 1, n)
        df[col] = np.where(flip, noisy, df[col]).astype(int)
    return df


def downsample_to_target_rate(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """
    Keep every non-churner and downsample churners so churn ~= TARGET_CHURN_RATE,
    mirroring a healthy subscription business (2-5% monthly churn).
    """
    stay = df[df["churn"] == 0]
    churn = df[df["churn"] == 1]
    # rate = n_churn / (n_churn + n_stay)  ->  n_churn = rate/(1-rate) * n_stay
    n_churn_target = int(round(TARGET_CHURN_RATE / (1 - TARGET_CHURN_RATE) * len(stay)))
    churn_ds = churn.sample(n=n_churn_target, random_state=int(rng.integers(1e9)))
    out = pd.concat([stay, churn_ds], ignore_index=True)
    return out.sample(frac=1.0, random_state=SEED).reset_index(drop=True)


def add_snapshot_date(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """
    Assign each customer a scoring snapshot spread over 12 months. This is
    independent of tenure/churn, so it enables a genuine time-based train/val/test
    split (train on earlier snapshots, test on later) without confounding the
    target. In production this would be the real weekly batch-scoring date.
    """
    start = np.datetime64("2024-01-01")
    day_offsets = rng.integers(0, 365, len(df))
    df["snapshot_date"] = start + day_offsets.astype("timedelta64[D]")
    df["churn_30d"] = df["churn"]  # target: cancels within the 30d horizon
    return df.drop(columns=["churn"]).sort_values("snapshot_date").reset_index(drop=True)


def main() -> None:
    rng = np.random.default_rng(SEED)
    raw = load_raw()
    df = reinterpret_columns(raw)
    df = add_engagement_features(df, rng)
    df = downsample_to_target_rate(df, rng)
    df = add_snapshot_date(df, rng)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)

    rate = df["churn_30d"].mean()
    print(f"rows={len(df)}  features={df.shape[1]}  churn_rate={rate:.3%}")
    print(f"churners={int(df['churn_30d'].sum())}  saved -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
