# Xiaohongshu pilot sample: data note

## What is in this folder

These tables summarize a local search export collected on 9 July 2026. The
source had 683 rows and 645 unique posts. Only grouped results are published;
post text, account names, IDs, URLs and access tokens remain outside the
repository.

## What the sample can support

- CANMAKE, Mistine, WAKEMAKE and AMUSE have the largest usable brand samples.
- The brand dictionary assigns one brand to 80.2% of unique posts. Ambiguous
  multi-brand searches remain unassigned unless the post content identifies a
  single brand.
- Groups with fewer than five posts are suppressed. This avoids presenting a
  one-off viral post as a brand-level pattern.
- Missing engagement values are excluded from medians, not replaced with zero.

## What it cannot support

This is a convenience sample shaped by selected keywords and Xiaohongshu's
search ranking. Publication dates span September 2017 to July 2026, so it is not
a July 2026 popularity ranking. Like counts are missing for 12.9% of source
rows, and observed counts cluster below 10,000; possible export or search
sampling effects have not been independently verified. Comparisons are
descriptive and should not be generalized to all Xiaohongshu beauty content.

## Files

- `data_quality.json`: row counts, date coverage, match rate and missingness
- `brand_summary.csv`: privacy-safe brand aggregates (`n >= 5`)
- `market_summary.csv`: market-group aggregates (`n >= 5`)
- `search_keyword_summary.csv`: query-level aggregates (`n >= 5`)
- `multisource_brand_coverage_v2.csv`: three-source presence audit; it intentionally does
  not combine engagement and sales rank into a misleading single score

The first verified Makeup snapshot was transcribed from six dated screenshots
covering ranks 1–30. Only ranks 1–20 enter the analysis. Displayed sale-price
ranges are preserved, and no hidden product option or undisplayed specification
is inferred.
