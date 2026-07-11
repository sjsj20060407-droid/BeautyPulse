"""Validate an official ranking or search-trend CSV export.

This importer deliberately accepts local exports instead of automating access
to websites. It keeps source dates and URLs so every observation is auditable.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


SCHEMAS = {
    "google_trends": ["date", "brand", "geo", "search_interest", "source_collected_at"],
    "oliveyoung": ["snapshot_date", "category", "rank", "brand", "product_name", "rating", "current_price_usd", "source_url"],
}


def validate(frame: pd.DataFrame, source: str) -> pd.DataFrame:
    missing = [column for column in SCHEMAS[source] if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    out = frame[SCHEMAS[source]].copy()
    if source == "google_trends":
        out["date"] = pd.to_datetime(out["date"], errors="raise").dt.date
        out["source_collected_at"] = pd.to_datetime(out["source_collected_at"], errors="raise").dt.date
        out["search_interest"] = pd.to_numeric(out["search_interest"], errors="raise")
        if not out["search_interest"].between(0, 100).all():
            raise ValueError("Google Trends UI exports must be scaled from 0 to 100")
    else:
        out["snapshot_date"] = pd.to_datetime(out["snapshot_date"], errors="raise").dt.date
        out["rank"] = pd.to_numeric(out["rank"], errors="raise").astype(int)
        if (out["rank"] < 1).any() or out.duplicated(["snapshot_date", "category", "rank"]).any():
            raise ValueError("Ranks must be positive and unique within each dated category")
    return out.drop_duplicates().sort_values(SCHEMAS[source][:2]).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, choices=SCHEMAS)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    clean = validate(pd.read_csv(args.input, encoding="utf-8-sig"), args.source)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(output, index=False, encoding="utf-8-sig")
    print(f"validated {len(clean)} {args.source} rows -> {output}")


if __name__ == "__main__":
    main()

