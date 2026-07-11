"""Normalize a local MediaCrawler CSV/JSON export.

Example:
    python scripts/import_external.py --platform xiaohongshu --input local.csv
"""

from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from beautypulse.adapters import read_external_export
from beautypulse.cleaning import clean_posts
from beautypulse.features import add_features

parser = argparse.ArgumentParser()
parser.add_argument("--platform", required=True, choices=["xiaohongshu", "douyin"])
parser.add_argument("--input", required=True)
parser.add_argument("--output", default=str(ROOT / "data" / "processed" / "external_posts.csv"))
args = parser.parse_args()

normalized = read_external_export(args.input, args.platform)
cleaned = clean_posts(normalized, ROOT / "config" / "brands.csv")
featured = add_features(cleaned)
output = Path(args.output); output.parent.mkdir(parents=True, exist_ok=True)
featured.to_csv(output, index=False, encoding="utf-8-sig")
print(f"normalized rows: {len(featured)}")
print(f"saved privacy-safe output: {output}")
