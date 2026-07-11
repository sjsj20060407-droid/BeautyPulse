# Data dictionary

| Field | Type | Meaning |
|---|---|---|
| platform | string | `xiaohongshu` or `douyin` |
| post_id_hash | string | Salted irreversible identifier used for deduplication |
| brand | string | Normalized brand name |
| market_group | string | K-beauty, Thai beauty, J-beauty, international luxury, affordable or premium C-beauty |
| country_or_region | string | Brand origin used by this project |
| price_tier | string | affordable, mid, premium or luxury |
| product_category | string | lip, base, eye or other |
| keyword | string | Search keyword that produced the observation |
| publish_time | UTC datetime | Content publication time where available |
| collect_time | UTC datetime | Observation time; required because engagement changes |
| title / description / hashtags | string | Public content text, excluded from the public real-data release |
| like/comment/collect/share_count | integer | Platform-visible interaction counts at collection time |
| author_follower_bucket | category | Coarsened follower range; no account name or profile URL |
| is_sponsored_hint | boolean | Text-disclosure hint, not a legal conclusion |
| engagement_score | integer | likes + 2 comments + 2 saves + 3 shares |
| selling_points / pain_points | category list | Transparent lexicon-based text labels |
| sentiment | category | Heuristic positive, neutral or negative label |
| engagement_percentile | float | Within-platform and within-category percentile |

The engagement score is a project-specific exploratory index. Raw interaction
counts remain available so readers can replace the weights.
