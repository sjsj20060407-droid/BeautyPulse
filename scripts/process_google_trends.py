"""Normalize and bridge several Google Trends UI exports.

Google Trends UI values are scaled within each request. Shared anchor terms
bridge requests into relative units; the result is still an index, not search
volume. Values displayed as '<1' are retained as censored observations and use
0.5 only for the documented sensitivity estimate.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd


BRAND_NAMES = {
    "3ce": "3CE", "赫妍": "HERA", "hera": "HERA", "amuse": "AMUSE",
    "laneige": "Laneige", "wakemake": "WAKEMAKE", "shiseido": "Shiseido",
    "canmake": "CANMAKE", "decorté": "DECORTÉ", "黛珂": "DECORTÉ",
    "mistine": "Mistine", "sivanna colors": "Sivanna Colors",
    "judydoll": "Judydoll", "proya": "Proya", "maogeping": "MAOGEPING",
}


def clean_header(value: object) -> str:
    text = re.sub(r":\s*\([^)]*\)\s*$", "", str(value)).strip()
    return BRAND_NAMES.get(text.lower(), text)


def read_export(path: str | Path, group: str) -> pd.DataFrame:
    path = Path(path)
    is_excel = path.read_bytes()[:2] == b"PK"
    wide = pd.read_excel(path, header=2) if is_excel else pd.read_csv(path, skiprows=2)
    wide = wide.rename(columns={wide.columns[0]: "date", **{c: clean_header(c) for c in wide.columns[1:]}})
    wide["date"] = pd.to_datetime(wide["date"], errors="raise")
    long = wide.melt(id_vars="date", var_name="brand", value_name="display_value")
    long["is_below_one"] = long["display_value"].astype(str).str.strip().eq("<1")
    long["raw_index"] = pd.to_numeric(long["display_value"].replace("<1", 0.5), errors="coerce")
    if long["raw_index"].isna().any():
        raise ValueError(f"Unparseable Trends value in {path}")
    long["source_group"] = group
    return long.drop(columns="display_value")


def anchor_factor(reference: pd.DataFrame, target: pd.DataFrame, anchor: str) -> float:
    left = reference.query("brand == @anchor").set_index("date")["raw_index"]
    right = target.query("brand == @anchor").set_index("date")["raw_index"]
    aligned = pd.concat([left.rename("left"), right.rename("right")], axis=1).dropna()
    denominator = aligned["right"].sum()
    if denominator <= 0 or aligned.empty:
        raise ValueError(f"Anchor {anchor} has insufficient overlap")
    return float(aligned["left"].sum() / denominator)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--group1", required=True)
    parser.add_argument("--group2", required=True)
    parser.add_argument("--group3", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--collected-at", default="2026-07-11")
    args = parser.parse_args()

    g1 = read_export(args.group1, "group_1_kbeauty")
    g2 = read_export(args.group2, "group_2_jp_thai")
    g3 = read_export(args.group3, "group_3_cbeauty")
    expected_dates = g1["date"].drop_duplicates().sort_values().reset_index(drop=True)
    for name, frame in [("group2", g2), ("group3", g3)]:
        dates = frame["date"].drop_duplicates().sort_values().reset_index(drop=True)
        if not dates.equals(expected_dates):
            raise ValueError(f"{name} dates do not align with group1")

    factor_2 = anchor_factor(g1, g2, "3CE")
    factor_3 = factor_2 * anchor_factor(g2, g3, "Mistine")
    g1["bridge_factor"] = 1.0
    g2["bridge_factor"] = factor_2
    g3["bridge_factor"] = factor_3

    # Keep each bridge term once to avoid double-counting it in summaries.
    combined = pd.concat([
        g1,
        g2.query("brand != '3CE'"),
        g3.query("brand != 'Mistine'"),
    ], ignore_index=True)
    combined["calibrated_index"] = combined["raw_index"] * combined["bridge_factor"]
    combined["collected_at"] = args.collected_at
    combined["geo"] = "Worldwide"
    combined["category"] = "Beauty & Fitness"
    combined["search_type"] = "Web Search"
    combined["source_url"] = "https://trends.google.com/trends/explore"

    cutoff = combined["date"].max() - pd.Timedelta(weeks=12)
    recent = combined[combined["date"] >= cutoff].groupby("brand")["calibrated_index"].mean()
    summary = (
        combined.groupby("brand")
        .agg(
            weeks=("date", "nunique"),
            mean_index=("calibrated_index", "mean"),
            median_index=("calibrated_index", "median"),
            peak_index=("calibrated_index", "max"),
            zero_share=("raw_index", lambda x: float((x == 0).mean())),
            below_one_weeks=("is_below_one", "sum"),
        )
        .join(recent.rename("recent_13w_mean"))
        .reset_index()
    )
    peak_dates = combined.loc[combined.groupby("brand")["calibrated_index"].idxmax(), ["brand", "date"]]
    summary = summary.merge(peak_dates.rename(columns={"date": "peak_date"}), on="brand")
    summary["recent_rank"] = summary["recent_13w_mean"].rank(method="min", ascending=False).astype(int)
    summary = summary.sort_values("recent_rank")

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    combined.to_csv(output / "google_trends_weekly_calibrated.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(output / "google_trends_brand_summary.csv", index=False, encoding="utf-8-sig")
    quality = {
        "weeks": int(len(expected_dates)),
        "date_min": expected_dates.min().date().isoformat(),
        "date_max": expected_dates.max().date().isoformat(),
        "brands": int(combined["brand"].nunique()),
        "group2_to_group1_factor_via_3CE": factor_2,
        "group3_to_group1_factor_via_Mistine": factor_3,
        "below_one_treatment": "flagged as censored; 0.5 used for sensitivity estimate",
        "interpretation": "relative calibrated index; not absolute search volume",
    }
    (output / "google_trends_quality.json").write_text(json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(quality, ensure_ascii=False, indent=2))
    print(summary[["recent_rank", "brand", "recent_13w_mean", "zero_share"]].to_string(index=False))


if __name__ == "__main__":
    main()
