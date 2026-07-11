from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from .schema import CANONICAL_COLUMNS, COUNT_COLUMNS, TEXT_COLUMNS

COUNT_SUFFIXES = {"k": 1_000, "w": 10_000, "万": 10_000, "m": 1_000_000}


def parse_count(value: object) -> int:
    if pd.isna(value) or value == "":
        return 0
    if isinstance(value, (int, float)):
        return max(0, int(value))
    text = str(value).strip().lower().replace(",", "")
    match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)([kwm万]?)\+?", text)
    if not match:
        return 0
    number, suffix = match.groups()
    return max(0, int(float(number) * COUNT_SUFFIXES.get(suffix, 1)))


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = re.sub(r"https?://\S+", " ", str(value))
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def load_brand_dictionary(path: str | Path) -> pd.DataFrame:
    brands = pd.read_csv(path).fillna("")
    brands["match_terms"] = brands.apply(
        lambda row: sorted(
            {row["brand"].lower(), *[x.strip().lower() for x in row["brand_aliases"].split("|") if x.strip()]},
            key=len,
            reverse=True,
        ),
        axis=1,
    )
    return brands


def attach_brand_metadata(frame: pd.DataFrame, brands: pd.DataFrame) -> pd.DataFrame:
    records = brands.to_dict("records")

    def match(row):
        content = " ".join(str(row.get(x, "")) for x in ["title", "description", "hashtags"]).lower()
        keyword = str(row.get("keyword", "")).lower()

        def unique_match(text):
            matches = [item for item in records if any(term in text for term in item["match_terms"])]
            return matches[0] if len(matches) == 1 else None

        # Content is stronger evidence than a search query. Multi-brand queries
        # are deliberately left unknown when the content itself is ambiguous.
        item = unique_match(content) or unique_match(keyword)
        if item:
            return pd.Series({
                "brand": item["brand"], "market_group": item["market_group"],
                "country_or_region": item["country_or_region"], "price_tier": item["price_tier"],
            })
        return pd.Series({"brand": "unknown", "market_group": "unknown", "country_or_region": "unknown", "price_tier": "unknown"})

    metadata = frame.apply(match, axis=1)
    out = frame.copy()
    for col in metadata.columns:
        unknown = out[col].isna() | out[col].astype(str).str.lower().eq("unknown")
        out.loc[unknown, col] = metadata.loc[unknown, col]
    return out


def clean_posts(frame: pd.DataFrame, brand_path: str | Path) -> pd.DataFrame:
    out = frame.copy()
    for col in CANONICAL_COLUMNS:
        if col not in out:
            out[col] = 0 if col in COUNT_COLUMNS else ""
    for col in COUNT_COLUMNS:
        out[col] = out[col].map(parse_count).astype("int64")
    for col in TEXT_COLUMNS:
        out[col] = out[col].map(normalize_text)
    for col in ["publish_time", "collect_time"]:
        out[col] = pd.to_datetime(out[col], errors="coerce", utc=True)
    out = out.drop_duplicates(subset=["platform", "post_id_hash"], keep="last")
    out = attach_brand_metadata(out, load_brand_dictionary(brand_path))
    out["product_category"] = out["product_category"].replace("", "unknown").fillna("unknown")
    return out.reset_index(drop=True)
