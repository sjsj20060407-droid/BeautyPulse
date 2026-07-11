"""Adapters for normalized imports from external collection tools.

MediaCrawler is an optional external dependency. This project does not import,
bundle, or automate it; it only reads exported CSV/JSON files.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pandas as pd

from .schema import CANONICAL_COLUMNS

ALIASES = {
    "post_id": ["note_id", "aweme_id", "post_id", "id"],
    "title": ["title", "note_title", "content_title"],
    "description": ["desc", "description", "content", "note_desc"],
    "hashtags": ["tag_list", "tags", "hashtags"],
    "keyword": ["source_keyword", "keyword", "search_keyword"],
    "publish_time": ["time", "publish_time", "create_time", "create_timestamp"],
    "collect_time": ["last_modify_ts", "collect_time", "crawl_time"],
    "like_count": ["liked_count", "like_count", "digg_count"],
    "comment_count": ["comment_count", "comments_count"],
    "collect_count": ["collected_count", "collect_count", "favorite_count"],
    "share_count": ["share_count", "shared_count"],
    "author_follower_count": ["fans", "follower_count", "followers"],
}


def _first_existing(frame: pd.DataFrame, candidates: list[str], default=None):
    for name in candidates:
        if name in frame.columns:
            return frame[name]
    return pd.Series([default] * len(frame), index=frame.index)


def hash_identifier(value: object, salt: str | None = None) -> str:
    salt = salt or os.getenv("BEAUTYPULSE_HASH_SALT", "public-portfolio-demo")
    return hashlib.sha256(f"{salt}|{value}".encode("utf-8")).hexdigest()[:20]


def follower_bucket(value: object) -> str:
    try:
        n = float(value)
    except (TypeError, ValueError):
        return "unknown"
    if n < 1_000:
        return "<1k"
    if n < 10_000:
        return "1k-10k"
    if n < 100_000:
        return "10k-100k"
    if n < 1_000_000:
        return "100k-1m"
    return ">=1m"


def parse_platform_datetime(series: pd.Series) -> pd.Series:
    """Parse ISO strings or Unix seconds/milliseconds using magnitude."""
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().mean() >= 0.8:
        median = numeric.dropna().median()
        unit = "ms" if median >= 100_000_000_000 else "s" if median >= 100_000_000 else "ns"
        return pd.to_datetime(numeric, unit=unit, errors="coerce", utc=True)
    return pd.to_datetime(series, errors="coerce", utc=True)


def adapt_mediacrawler(frame: pd.DataFrame, platform: str) -> pd.DataFrame:
    """Convert a MediaCrawler-style export to a privacy-safe common schema."""
    out = pd.DataFrame(index=frame.index)
    raw_ids = _first_existing(frame, ALIASES["post_id"], "missing")
    out["platform"] = platform.lower()
    out["post_id_hash"] = raw_ids.map(hash_identifier)
    for target in ["title", "description", "hashtags", "keyword", "publish_time", "collect_time"]:
        out[target] = _first_existing(frame, ALIASES[target], "")
    out["publish_time"] = parse_platform_datetime(out["publish_time"])
    out["collect_time"] = parse_platform_datetime(out["collect_time"])
    for target in ["like_count", "comment_count", "collect_count", "share_count"]:
        out[target] = _first_existing(frame, ALIASES[target], 0)
    followers = _first_existing(frame, ALIASES["author_follower_count"], None)
    out["author_follower_bucket"] = followers.map(follower_bucket)
    out["is_sponsored_hint"] = False
    for col in ["brand", "market_group", "country_or_region", "price_tier", "product_category"]:
        out[col] = "unknown"
    return out.reindex(columns=CANONICAL_COLUMNS)


def read_external_export(path: str | Path, platform: str) -> pd.DataFrame:
    path = Path(path)
    if path.suffix.lower() == ".csv":
        frame = pd.read_csv(path)
    elif path.suffix.lower() in {".json", ".jsonl"}:
        frame = pd.read_json(path, lines=path.suffix.lower() == ".jsonl")
    else:
        raise ValueError(f"Unsupported input format: {path.suffix}")
    return adapt_mediacrawler(frame, platform)
