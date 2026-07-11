"""Combine source-level coverage without pretending signals are equivalent."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--xhs-brand-summary", required=True)
    parser.add_argument("--oliveyoung", required=True)
    parser.add_argument("--google-trends")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    xhs = pd.read_csv(args.xhs_brand_summary, encoding="utf-8-sig")
    oy = pd.read_csv(args.oliveyoung, encoding="utf-8-sig")
    xhs_view = xhs[["brand", "posts", "median_engagement"]].rename(
        columns={"posts": "xhs_posts", "median_engagement": "xhs_median_engagement"})
    oy_view = (
        oy.groupby("brand", as_index=False)
        .agg(oliveyoung_best_rank=("rank", "min"), oliveyoung_ranked_products=("rank", "size"))
    )
    combined = xhs_view.merge(oy_view, on="brand", how="outer")
    if args.google_trends:
        trends = pd.read_csv(args.google_trends, encoding="utf-8-sig")
        trends = trends[["brand", "recent_rank", "recent_13w_mean", "zero_share"]].rename(
            columns={"recent_rank": "google_trends_recent_rank"})
        combined = combined.merge(trends, on="brand", how="outer")
    combined["xhs_observed"] = combined["xhs_posts"].notna()
    combined["oliveyoung_observed"] = combined["oliveyoung_best_rank"].notna()
    combined["cross_source_observed"] = combined["xhs_observed"] & combined["oliveyoung_observed"]
    combined["google_trends_observed"] = combined.get("recent_13w_mean", pd.Series(index=combined.index, dtype=float)).notna()
    combined["sources_observed"] = (
        combined[["xhs_observed", "oliveyoung_observed", "google_trends_observed"]].sum(axis=1)
    )
    combined["interpretation"] = "coverage only; engagement and sales rank are not directly comparable"
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    combined.sort_values(["sources_observed", "xhs_posts"], ascending=False).to_csv(
        output, index=False, encoding="utf-8-sig")
    print(f"saved {len(combined)} brand coverage rows -> {output}")


if __name__ == "__main__":
    main()
