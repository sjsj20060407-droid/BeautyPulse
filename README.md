# BeautyPulse 💄

> Cross-market beauty content analytics for RedNote (Xiaohongshu) and Douyin

BeautyPulse is a portfolio project that compares how beauty brands from South
Korea, Thailand, Japan, international luxury groups, and Chinese price tiers
perform on Chinese content platforms. The repository focuses on reproducible
data cleaning, privacy-safe schema design, transparent text features and an
interactive dashboard—not crawling scale.

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB)
![Tests](https://img.shields.io/badge/tests-pytest-0A9EDC)
![Data](https://img.shields.io/badge/public%20data-synthetic-green)
![License](https://img.shields.io/badge/code-MIT-blue)

## Questions answered

- Which market groups and brands have stronger engagement distributions?
- How do Xiaohongshu and Douyin differ after controlling for product category?
- Which selling points—long wear, coverage, brightening or value—are prominent?
- Which pain points—dryness, oxidation, transfer or irritation—appear in reviews?
- Do K-beauty products discovered through Olive Young trends receive attention
  on Chinese platforms?

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

The generated public demo uses deterministic synthetic records. It is useful
for testing the entire pipeline but must not be presented as real consumer
evidence.

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
