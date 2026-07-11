"""Generate deterministic synthetic records for a fully runnable public demo."""

from pathlib import Path
import hashlib
import random

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
random.seed(20260711); np.random.seed(20260711)
brands = pd.read_csv(ROOT / "config" / "brands.csv")
platforms = ["xiaohongshu", "douyin"]
selling = ["持妆实测", "黄皮显白", "轻薄服帖", "学生党平替", "遮瑕力在线", "水光奶油肌"]
pain = ["", "但有点卡粉", "下午会暗沉", "略微沾杯", "干皮可能拔干", "敏感肌先试用"]
categories = {"lip": ["唇釉", "口红", "唇泥"], "base": ["粉底液", "气垫", "粉饼"], "eye": ["眼影", "眉笔", "睫毛膏"]}
rows=[]; start=pd.Timestamp("2026-01-01",tz="UTC")
for _, b in brands.iterrows():
    allowed=b["focus_categories"].split("|")
    for platform in platforms:
        for i in range(5):
            category=random.choice(allowed); product=random.choice(categories[category]); s=random.choice(selling); p=random.choice(pain)
            base=np.random.lognormal(mean=5.3 if platform=="xiaohongshu" else 5.7,sigma=1.0)
            if b["price_tier"] in {"premium","luxury"}: base*=1.12
            likes=int(base); comments=int(max(1,likes*np.random.uniform(.025,.12))); collects=int(max(0,likes*np.random.uniform(.05,.40))); shares=int(max(0,likes*np.random.uniform(.01,.10)))
            raw=f"demo-{b['brand']}-{platform}-{i}"; h=hashlib.sha256(raw.encode()).hexdigest()[:20]
            day=random.randint(0,179)
            rows.append({
                "platform":platform,"post_id_hash":h,"brand":b["brand"],"market_group":b["market_group"],
                "country_or_region":b["country_or_region"],"price_tier":b["price_tier"],"product_category":category,
                "keyword":f"{b['brand']} {product} 测评","publish_time":start+pd.Timedelta(days=day),
                "collect_time":start+pd.Timedelta(days=180),"title":f"{b['brand']} {product}｜{s}",
                "description":f"通勤使用8小时记录，{s}。{p}".strip(),"hashtags":f"#{product} #{b['market_group']}",
                "like_count":likes,"comment_count":comments,"collect_count":collects,"share_count":shares,
                "author_follower_bucket":random.choice(["1k-10k","10k-100k","100k-1m"]),"is_sponsored_hint":False,
            })
out=ROOT/"data"/"sample";out.mkdir(parents=True,exist_ok=True)
pd.DataFrame(rows).to_csv(out/"demo_posts.csv",index=False,encoding="utf-8-sig")
print(f"created {len(rows)} synthetic rows: {out/'demo_posts.csv'}")
