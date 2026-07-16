"""
Shared pipeline pieces: chronological split and the feature preprocessor.
Kept separate so training, SHAP and scoring all use identical transforms.
"""
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "saas_churn.csv"

TARGET = "churn_30d"
ID_COLS = ["customer_id", "snapshot_date"]
CATEGORICAL = ["plan_type", "payment_method"]
NUMERIC = [
    "months_subscribed", "monthly_fee", "total_spend", "addon_services",
    "paperless_billing", "is_senior", "has_partner", "has_dependents",
    "logins_30d", "features_used", "open_tickets_30d",
    "days_since_last_interaction", "usage_change_pct",
]


def load() -> pd.DataFrame:
    df = pd.read_csv(DATA, parse_dates=["snapshot_date"])
    return df.sort_values("snapshot_date").reset_index(drop=True)


def chronological_split(df: pd.DataFrame, train=0.70, val=0.15):
    """Time-based split: earliest snapshots train, latest test (no leakage)."""
    n = len(df)
    i_train, i_val = int(n * train), int(n * (train + val))
    return df.iloc[:i_train], df.iloc[i_train:i_val], df.iloc[i_val:]


def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        [
            ("num", StandardScaler(), NUMERIC),
            ("cat", OneHotEncoder(handle_unknown="ignore", drop="first"), CATEGORICAL),
        ]
    )


def feature_names(preprocessor: ColumnTransformer) -> list[str]:
    cat = preprocessor.named_transformers_["cat"].get_feature_names_out(CATEGORICAL)
    return NUMERIC + list(cat)


def xy(df: pd.DataFrame):
    return df.drop(columns=ID_COLS + [TARGET]), df[TARGET]
