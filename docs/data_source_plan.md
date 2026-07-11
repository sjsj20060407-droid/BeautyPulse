# Multi-source data plan

BeautyPulse uses triangulation rather than treating one platform as ground
truth. Each source answers a different question.

| Layer | Source | What it measures | Update rhythm | Main limitation |
|---|---|---|---|---|
| Content | Xiaohongshu sample | Topics and visible engagement | Monthly pilot | Search-ranked convenience sample |
| Commerce | Olive Young Best Sellers | Korean online/offline sales rank | Weekly snapshot | Strong for K-beauty, not China demand |
| Demand | Google Trends | Relative search interest | Weekly/monthly export | Relative index, not sales volume |
| Social validation | TikTok Research API | Video views, likes, saves and hashtags | Optional monthly | Approval required; metrics can lag |

## Recommended collection design

Freeze the brand list before collecting. For each month, retain Xiaohongshu
posts published within the latest 90 days and aim for at least 30 usable posts
per focal brand. Record the query, collection date and number of missing fields.
Do not repeatedly request pages after the platform returns a risk-control or
verification response.

Save the top 20 Olive Young products in the makeup categories once a week. Keep
`snapshot_date`, category, rank, brand, product, rating and displayed price.
Several dated snapshots are more valuable than one large scrape because they
show rank persistence and new entries.

Export Google Trends comparisons in stable batches with one anchor term shared
between batches. Use China for Chinese demand and South Korea/Japan/Thailand for
home-market context. UI values are normalized within each request, so numbers
from unrelated exports must not be compared directly without an anchor.

## Analysis rules

- Separate **coverage**, **engagement**, **search interest** and **sales rank**;
  they are not interchangeable measures of popularity.
- Use medians and interquartile ranges for engagement.
- Report sample size beside every brand statistic and suppress `n < 5`.
- Compare recent posts within the same publication window.
- Label every table with source, snapshot date, geography and sampling method.
- Publish only aggregated social results; keep post-level exports local.

## Practical target for the portfolio

A defensible first release needs roughly 10–12 focal brands, 30–50 recent
Xiaohongshu posts per brand where available, 8–12 weekly Olive Young snapshots,
and 12 months of weekly Google Trends interest. This is enough to demonstrate
data engineering and analytical judgment without claiming platform-wide
coverage.
