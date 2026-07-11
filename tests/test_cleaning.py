from pathlib import Path

import pandas as pd
from beautypulse.cleaning import attach_brand_metadata, load_brand_dictionary, normalize_text, parse_count
from beautypulse.adapters import adapt_mediacrawler, parse_platform_datetime

def test_parse_count_suffixes():
    assert parse_count("1.2万") == 12000
    assert parse_count("3k") == 3000
    assert parse_count("1,250") == 1250
    assert parse_count(None) == 0

def test_normalize_text_removes_url_and_spaces():
    assert normalize_text("  好用  https://example.com  推荐 ") == "好用 推荐"

def test_adapter_drops_identity_fields_and_hashes_id():
    raw = pd.DataFrame([{"note_id": "raw-123", "title": "测试", "nickname": "do-not-keep", "liked_count": "1.2万"}])
    out = adapt_mediacrawler(raw, "xiaohongshu")
    assert "nickname" not in out.columns
    assert out.loc[0, "post_id_hash"] != "raw-123"
    assert len(out.loc[0, "post_id_hash"]) == 20

def test_millisecond_timestamp_parser():
    result = parse_platform_datetime(pd.Series([1735689600000]))
    assert str(result.iloc[0]) == "2025-01-01 00:00:00+00:00"


def test_multi_brand_keyword_is_not_forced_to_first_brand():
    brands = load_brand_dictionary(Path(__file__).parents[1] / "config" / "brands.csv")
    frame = pd.DataFrame([{
        "title": "今日妆容", "description": "", "hashtags": "",
        "keyword": "黛珂、CANMAKE", "brand": "unknown", "market_group": "unknown",
        "country_or_region": "unknown", "price_tier": "unknown",
    }])
    assert attach_brand_metadata(frame, brands).loc[0, "brand"] == "unknown"
