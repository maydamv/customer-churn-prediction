"""Exploratory data analysis: figures saved to outputs/eda/."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "saas_churn.csv"
OUT = ROOT / "outputs" / "eda"

ENGAGEMENT = [
    "logins_30d", "features_used", "open_tickets_30d",
    "days_since_last_interaction", "usage_change_pct",
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA)
    sns.set_theme(style="whitegrid")

    print(f"shape={df.shape}  churn_rate={df['churn_30d'].mean():.2%}")
    miss = df.isna().sum()
    print("\nmissing values:", miss[miss > 0].to_dict() or "none")
    print("\nchurn by plan_type:\n", df.groupby("plan_type")["churn_30d"].mean())

    # 1) engagement features by churn class (the core hypothesis)
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for ax, col in zip(axes.ravel(), ENGAGEMENT):
        sns.kdeplot(data=df, x=col, hue="churn_30d", common_norm=False,
                    fill=True, alpha=0.4, ax=ax)
        ax.set_title(col)
    axes.ravel()[-1].axis("off")
    fig.suptitle("Engagement features by churn class (0=stay, 1=churn)")
    fig.tight_layout()
    fig.savefig(OUT / "engagement_by_churn.png", dpi=110)
    plt.close(fig)

    # 2) correlation of numeric features with the target
    num = df.select_dtypes("number")
    corr = num.corr()["churn_30d"].drop("churn_30d").sort_values()
    fig, ax = plt.subplots(figsize=(7, 6))
    corr.plot.barh(ax=ax, color=(corr > 0).map({True: "#d1495b", False: "#30638e"}))
    ax.set_title("Correlation with churn_30d")
    fig.tight_layout()
    fig.savefig(OUT / "target_correlation.png", dpi=110)
    plt.close(fig)

    # 3) churn rate by plan and tenure bucket
    df["tenure_bucket"] = pd.cut(df["months_subscribed"], [0, 6, 12, 24, 48, 100],
                                 labels=["0-6", "7-12", "13-24", "25-48", "49+"])
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    df.groupby("plan_type")["churn_30d"].mean().plot.bar(ax=axes[0], color="#d1495b")
    axes[0].set_title("Churn rate by plan")
    df.groupby("tenure_bucket", observed=True)["churn_30d"].mean().plot.bar(
        ax=axes[1], color="#edae49")
    axes[1].set_title("Churn rate by tenure bucket")
    for ax in axes:
        ax.set_ylabel("churn rate")
    fig.tight_layout()
    fig.savefig(OUT / "churn_by_segment.png", dpi=110)
    plt.close(fig)

    print(f"\nfigures saved -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
