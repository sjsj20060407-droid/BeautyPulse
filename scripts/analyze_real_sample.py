"""Create privacy-safe aggregates from a local Xiaohongshu export.

No post-level data, account names, URLs, tokens, titles, or descriptions are
written to the repository. Results describe the collected convenience sample
only and must not be interpreted as platform-wide market estimates.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from beautypulse.adapters import adapt_mediacrawler
from beautypulse.cleaning import clean_posts
from beautypulse.features import add_features


def safe_group(frame: pd.DataFrame, keys: list[str], minimum: int) -> pd.DataFrame:
    return (
        frame.groupby(keys, dropna=False)
        .agg(
            posts=("post_id_hash", "size"),
            median_likes=("like_count", "median"),
            median_saves=("collect_count", "median"),
            median_comments=("comment_count", "median"),
            median_shares=("share_count", "median"),
            median_engagement=("engagement_score", "median"),
            median_save_like_ratio=("save_like_ratio", "median"),
        )
        .reset_index()
        .query("posts >= @minimum")
        .sort_values(["posts", "median_engagement"], ascending=False)
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", default=str(ROOT / "reports" / "real_sample"))
    parser.add_argument("--minimum-group-size", type=int, default=5)
    args = parser.parse_args()

    raw = pd.read_csv(args.input, encoding="utf-8-sig")
    normalized = adapt_mediacrawler(raw, "xiaohongshu")
    metric_source = {
        "like_count": "liked_count",
        "collect_count": "collected_count",
        "comment_count": "comment_count",
        "share_count": "share_count",
    }
    for metric, source in metric_source.items():
        normalized[f"{metric}_missing"] = pd.to_numeric(raw.get(source), errors="coerce").isna()
    clean = clean_posts(normalized, ROOT / "config" / "brands.csv")
    # Missing metrics are not zero engagement. Restore them to NA after the
    # generic cleaner so medians exclude unavailable observations.
    for metric in metric_source:
        clean.loc[clean[f"{metric}_missing"], metric] = pd.NA
    frame = add_features(clean)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)

    missing = {f"missing_{key}_rate": round(float(pd.to_numeric(raw.get(source), errors="coerce").isna().mean()), 4)
               for key, source in metric_source.items()}
    quality = {
        "source_rows": int(len(raw)),
        "unique_posts": int(len(frame)),
        "duplicate_rows_removed": int(len(raw) - len(frame)),
        "date_min_utc": frame["publish_time"].min().isoformat() if frame["publish_time"].notna().any() else None,
        "date_max_utc": frame["publish_time"].max().isoformat() if frame["publish_time"].notna().any() else None,
        "brand_match_rate": round(float(frame["brand"].ne("unknown").mean()), 4),
        "minimum_reported_group_size": args.minimum_group_size,
        "sampling_note": "Convenience search sample; descriptive only, not representative of Xiaohongshu.",
        "distribution_note": "Counts cluster below 10,000; possible export/search sampling effects were not independently verified.",
        **missing,
    }
    (output / "data_quality.json").write_text(json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8")

    safe_group(frame, ["market_group"], args.minimum_group_size).to_csv(
        output / "market_summary.csv", index=False, encoding="utf-8-sig")
    brand = safe_group(frame.query("brand != 'unknown'"), ["market_group", "brand"], args.minimum_group_size)
    brand.to_csv(output / "brand_summary.csv", index=False, encoding="utf-8-sig")
    safe_group(frame, ["keyword"], args.minimum_group_size).to_csv(
        output / "search_keyword_summary.csv", index=False, encoding="utf-8-sig")

    top = brand.sort_values("posts", ascending=False).head(15).sort_values("posts")
    if not top.empty:
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns

            sns.set_theme(style="whitegrid")
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.barh(top["brand"], top["posts"], color="#c8789a")
            ax.set(title="Brand mentions in the collected sample", xlabel="Unique posts", ylabel="")
            fig.text(0.99, 0.01, "Convenience search sample collected 2026-07-09 — descriptive only",
                     ha="right", fontsize=8, color="#666666")
            fig.tight_layout(rect=(0, 0.03, 1, 1))
            fig.savefig(output / "brand_sample_coverage.png", dpi=180)
            plt.close(fig)
        except ImportError:
            # Aggregate tables remain the source of truth when optional chart
            # dependencies are unavailable in a restricted environment.
            pass

    print(json.dumps(quality, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
