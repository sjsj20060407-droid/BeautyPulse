from __future__ import annotations

import re

import numpy as np
import pandas as pd

SELLING_POINTS = {
    "long_wear": ["持妆", "不脱妆", "越夜越美丽"],
    "coverage": ["遮瑕", "高遮盖", "毛孔"],
    "brightening": ["显白", "提亮", "黄皮友好"],
    "texture": ["轻薄", "服帖", "奶油肌", "水光"],
    "value": ["平价", "性价比", "平替", "学生党"],
}
PAIN_POINTS = {
    "dryness": ["拔干", "卡粉", "起皮"],
    "oxidation": ["氧化", "暗沉"],
    "transfer": ["沾杯", "掉色", "蹭口罩"],
    "irritation": ["过敏", "刺痛", "闷痘"],
    "shade_mismatch": ["色差", "假白", "不适合黄皮"],
}
POSITIVE = ["好看", "推荐", "惊喜", "回购", "绝了", "服帖", "显白", "高级"]
NEGATIVE = ["踩雷", "难用", "拔干", "卡粉", "氧化", "暗沉", "沾杯", "过敏", "失望"]
SPONSORED_HINTS = ["广告", "合作", "赞助", "品牌赠送", "商业合作", "体验官"]


def _labels(text: str, lexicon: dict[str, list[str]]) -> str:
    return "|".join(name for name, words in lexicon.items() if any(word in text for word in words)) or "none"


def infer_category(text: str) -> str:
    if re.search(r"唇釉|口红|唇泥|唇膏", text):
        return "lip"
    if re.search(r"粉底|气垫|遮瑕|粉饼|底妆", text):
        return "base"
    if re.search(r"眼影|眼线|睫毛|眉", text):
        return "eye"
    return "other"


def add_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    text = (out["title"].fillna("") + " " + out["description"].fillna("") + " " + out["hashtags"].fillna(""))
    inferred = text.map(infer_category)
    mask = out["product_category"].isin(["", "unknown", None])
    out.loc[mask, "product_category"] = inferred[mask]
    out["selling_points"] = text.map(lambda x: _labels(x, SELLING_POINTS))
    out["pain_points"] = text.map(lambda x: _labels(x, PAIN_POINTS))
    out["sentiment_score"] = text.map(lambda x: sum(w in x for w in POSITIVE) - sum(w in x for w in NEGATIVE))
    out["sentiment"] = np.select(
        [out["sentiment_score"] > 0, out["sentiment_score"] < 0], ["positive", "negative"], default="neutral"
    )
    out["is_sponsored_hint"] = text.map(lambda x: any(word in x for word in SPONSORED_HINTS))
    out["engagement_score"] = (
        out["like_count"] + 2 * out["comment_count"] + 2 * out["collect_count"] + 3 * out["share_count"]
    )
    out["log_engagement"] = np.log1p(out["engagement_score"])
    out["save_like_ratio"] = np.where(out["like_count"] > 0, out["collect_count"] / out["like_count"], np.nan)
    out["comment_like_ratio"] = np.where(out["like_count"] > 0, out["comment_count"] / out["like_count"], np.nan)
    group = out.groupby(["platform", "product_category"])["engagement_score"]
    out["engagement_percentile"] = group.rank(pct=True, method="average")
    out["is_high_engagement"] = out["engagement_percentile"] >= 0.90
    return out
