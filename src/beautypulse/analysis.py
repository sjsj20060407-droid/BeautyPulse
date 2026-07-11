from __future__ import annotations

from pathlib import Path

import pandas as pd


def summary_tables(frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
    market = (
        frame.groupby("market_group", dropna=False)
        .agg(posts=("post_id_hash", "count"), median_engagement=("engagement_score", "median"),
             mean_save_like_ratio=("save_like_ratio", "mean"), negative_share=("sentiment", lambda x: (x == "negative").mean()))
        .reset_index().sort_values("median_engagement", ascending=False)
    )
    brand = (
        frame[frame["brand"] != "unknown"].groupby(["market_group", "brand"], dropna=False)
        .agg(posts=("post_id_hash", "count"), median_engagement=("engagement_score", "median"),
             high_engagement_posts=("is_high_engagement", "sum"))
        .reset_index().sort_values(["market_group", "median_engagement"], ascending=[True, False])
    )
    platform = (
        frame.groupby(["platform", "product_category"])
        .agg(posts=("post_id_hash", "count"), median_engagement=("engagement_score", "median"),
             median_save_like_ratio=("save_like_ratio", "median"))
        .reset_index()
    )
    sentiment = (
        frame.groupby(["market_group", "sentiment"]).size().rename("posts").reset_index()
    )
    return {"market_summary": market, "brand_summary": brand, "platform_category": platform, "sentiment_summary": sentiment}


def save_tables(tables: dict[str, pd.DataFrame], report_dir: str | Path) -> None:
    report_dir = Path(report_dir); report_dir.mkdir(parents=True, exist_ok=True)
    for name, table in tables.items():
        table.to_csv(report_dir / f"{name}.csv", index=False, encoding="utf-8-sig")


def save_charts(frame: pd.DataFrame, report_dir: str | Path) -> None:
    import matplotlib.pyplot as plt
    import seaborn as sns
    report_dir = Path(report_dir); report_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", font_scale=0.9)
    order = frame.groupby("market_group")["engagement_score"].median().sort_values().index
    fig, ax = plt.subplots(figsize=(10, 5.8))
    sns.boxplot(data=frame, y="market_group", x="log_engagement", order=order, showfliers=False, ax=ax, color="#7eb6d8")
    ax.set(title="Engagement distribution by beauty market group", xlabel="log(1 + weighted engagement)", ylabel="")
    fig.text(0.99, 0.01, "Synthetic demo — not real market findings", ha="right", fontsize=8, color="#777777")
    fig.tight_layout(rect=(0, 0.025, 1, 1)); fig.savefig(report_dir / "market_engagement.png", dpi=180); plt.close(fig)

    pivot = frame.pivot_table(index="market_group", columns="sentiment", values="post_id_hash", aggfunc="count", fill_value=0)
    pivot = pivot.div(pivot.sum(axis=1), axis=0)
    fig, ax = plt.subplots(figsize=(10, 5.8)); pivot.plot(kind="barh", stacked=True, ax=ax, color=["#d96b62", "#b8c4ce", "#4d9f78"])
    ax.set(title="Heuristic sentiment mix by market group", xlabel="share of posts", ylabel=""); ax.legend(title="sentiment")
    fig.text(0.99, 0.01, "Synthetic demo — not real market findings", ha="right", fontsize=8, color="#777777")
    fig.tight_layout(rect=(0, 0.025, 1, 1)); fig.savefig(report_dir / "sentiment_mix.png", dpi=180); plt.close(fig)

    top = frame.groupby("brand")["engagement_score"].median().sort_values(ascending=False).head(15).sort_values()
    fig, ax = plt.subplots(figsize=(10, 6)); top.plot(kind="barh", ax=ax, color="#c27a9b")
    ax.set(title="Top brands by median weighted engagement", xlabel="median weighted engagement", ylabel="")
    fig.text(0.99, 0.01, "Synthetic demo — not real market findings", ha="right", fontsize=8, color="#777777")
    fig.tight_layout(rect=(0, 0.025, 1, 1)); fig.savefig(report_dir / "top_brands.png", dpi=180); plt.close(fig)
