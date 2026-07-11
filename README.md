# BeautyPulse 💄

> Cross-market beauty content analytics for RedNote (Xiaohongshu) and Douyin

BeautyPulse is a portfolio project that compares how beauty brands from South
Korea, Thailand, Japan, international luxury groups, and Chinese price tiers
perform on Chinese content platforms. The repository focuses on reproducible
data cleaning, privacy-safe schema design, transparent text features and an
interactive dashboard—not crawling scale.

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB)
![Tests](https://img.shields.io/badge/tests-pytest-0A9EDC)
![Data](https://img.shields.io/badge/public%20data-synthetic%20%2B%20aggregates-green)
![License](https://img.shields.io/badge/code-MIT-blue)

## Questions answered

- Which market groups and brands have stronger engagement distributions?
- How do Xiaohongshu and Douyin differ after controlling for product category?
- Which selling points—long wear, coverage, brightening or value—are prominent?
- Which pain points—dryness, oxidation, transfer or irritation—appear in reviews?
- Do K-beauty products discovered through Olive Young trends receive attention
  on Chinese platforms?

## Multi-source design

One platform is not treated as market truth. Xiaohongshu describes discussion,
Olive Young's daily sales ranking validates Korean commercial momentum, and
Google Trends adds regional search interest. TikTok Research API is documented
as an optional approved source. See
[`docs/data_source_plan.md`](docs/data_source_plan.md) and
[`config/source_registry.csv`](config/source_registry.csv).

## Repository layout

```text
beautypulse/
├── config/                 # brand and keyword dictionaries
├── dashboard/app.py        # Streamlit dashboard
├── data/sample/            # synthetic public demonstration data
├── docs/                   # methodology, compliance and resume notes
├── reports/                # generated tables and figures
├── scripts/                # demo generator and end-to-end pipeline
├── src/beautypulse/        # adapters, cleaning, features and analysis
└── tests/                  # unit tests
```

## Quick start

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt

python scripts/generate_demo_data.py
python scripts/run_pipeline.py
pytest -q
streamlit run dashboard/app.py
```

Official ranking and trend exports can be validated with:

```bash
python scripts/import_market_signal.py --source google_trends \
  --input local_trends.csv --output data/processed/google_trends.csv
python scripts/import_market_signal.py --source oliveyoung \
  --input local_ranking.csv --output data/processed/oliveyoung_rankings.csv
```

`data/external_aggregates/oliveyoung_global_homepage_2026-07-11.csv`
is a small, dated trial snapshot of products visibly listed in the official
global homepage Best Sellers module. It is not presented as the Makeup category
or as a historical ranking. The source page is dynamic, so subsequent snapshots
should be recorded with their observation date rather than silently replacing
this file.

The first verified category snapshot is
`data/external_aggregates/oliveyoung_makeup_top20_2026-07-11.csv`. It contains
ranks 1–20 from `Top in Korea > Makeup`, transcribed from dated screenshots and
validated for complete, unique ranks. WAKEMAKE, 3CE and rom&nd appear in both
this ranking and the Xiaohongshu pilot sample. This is cross-source coverage,
not evidence that engagement and sales rank share the same scale or cause one
another.

## Google Trends pilot

Three official UI exports cover 53 aligned weeks from 6 July 2025 to 5 July
2026 and 13 brands. Because each Google Trends request is independently scaled,
3CE bridges the K-beauty and Japan/Thailand batches, while MISTINE bridges the
Japan/Thailand and C-beauty batches. `process_google_trends.py` records the
factors and retains the original index alongside a calibrated relative index.

For the latest 13 weeks, Shiseido and Laneige have the strongest relative
signals, followed by Judydoll. HERA is zero throughout this global Google sample
and several smaller brands frequently appear as zero or below one. These values
indicate insufficient visible search signal, not zero consumer awareness.
Google Trends is normalized search interest rather than absolute query volume.

Generated files:

- `data/external_aggregates/google_trends_weekly_calibrated.csv`
- `data/external_aggregates/google_trends_brand_summary.csv`
- `data/external_aggregates/google_trends_quality.json`
- `reports/real_sample/multisource_brand_coverage_v2.csv`

The generated public demo uses deterministic synthetic records. It is useful
for testing the entire pipeline but must not be presented as real consumer
evidence.

## Real pilot sample

The repository also includes privacy-safe aggregates from a Xiaohongshu search
export collected on 9 July 2026. The input contained 683 rows and 645 unique
posts; 38 duplicate rows were removed. The original post-level file stays
local. No nickname, title, description, URL, note ID or access token is
published.

The sample is useful for demonstrating data quality checks and the difference
between coverage and representativeness. It is **not** a current popularity
ranking: publication dates span 2017–2026, results came from selected search
queries, and 12.9% of like counts were unavailable. Missing metrics are excluded
from their medians rather than treated as zero. Groups with fewer than five
posts are suppressed.

Reproduce the aggregate report from a local export:

```bash
python scripts/analyze_real_sample.py \
  --input /path/to/search_contents.csv \
  --output-dir reports/real_sample
```

## Importing an external export

[MediaCrawler](https://github.com/NanmiCoder/MediaCrawler) can export public
search results for learning and research. It is an optional external tool and
is **not bundled here**. Its current license restricts use to non-commercial
learning and prohibits large-scale crawling.

```python
from beautypulse.adapters import read_external_export

posts = read_external_export("local_xhs_export.csv", platform="xiaohongshu")
posts.to_csv("data/raw/xhs_normalized.csv", index=False)
```

Never commit raw exports. The adapter hashes post IDs, coarsens follower counts
and drops author names, avatars and profile URLs. Read
[`docs/compliance.md`](docs/compliance.md) before collecting any real data.

## Key design decisions

### Comparable categories

The primary comparison uses lip and base makeup. Mixing all beauty categories
would confound country and price-tier effects with different product mixes.

### Engagement score

```text
likes + 2 × comments + 2 × saves + 3 × shares
```

This is an explicit project heuristic, not an official platform metric. The
pipeline retains every raw count and also calculates within-platform/category
percentiles.

### Transparent NLP baseline

The first version uses visible Chinese lexicons for selling points, pain points
and sentiment. This makes errors inspectable and creates a baseline for a later
supervised model.

## Example outputs

After running the pipeline:

- `reports/market_summary.csv`
- `reports/brand_summary.csv`
- `reports/market_engagement.png`
- `reports/sentiment_mix.png`
- `reports/top_brands.png`

## Limitations

Search and recommendation results are algorithmically selected; engagement is
long-tailed and cumulative; sponsorship labels may be incomplete; heuristic
sentiment cannot reliably detect sarcasm or mixed opinions. Findings are
descriptive and should not be framed as causal or nationally representative.

## External references

- [MediaCrawler repository](https://github.com/NanmiCoder/MediaCrawler)
- [Olive Young Global Bestsellers](https://global.oliveyoung.com/display/page/best-seller)

## Author

Shi Jing — Data Science and Big Data Technology student interested in beauty
and consumer analytics.
