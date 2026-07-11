from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"))
st.set_page_config(page_title="BeautyPulse",page_icon="💄",layout="wide")
st.title("BeautyPulse｜多国美妆内容洞察")
st.caption("公开演示使用合成数据；真实项目仅展示脱敏聚合结果。")
path=ROOT/"data"/"processed"/"posts.csv"
if not path.exists(): st.error("请先运行 scripts/run_pipeline.py");st.stop()
df=pd.read_csv(path,parse_dates=["publish_time","collect_time"])
with st.sidebar:
    platforms=st.multiselect("平台",sorted(df.platform.unique()),default=sorted(df.platform.unique()))
    markets=st.multiselect("市场分组",sorted(df.market_group.unique()),default=sorted(df.market_group.unique()))
    categories=st.multiselect("品类",sorted(df.product_category.unique()),default=sorted(df.product_category.unique()))
view=df[df.platform.isin(platforms)&df.market_group.isin(markets)&df.product_category.isin(categories)]
c1,c2,c3,c4=st.columns(4);c1.metric("内容数",f"{len(view):,}");c2.metric("品牌数",view.brand.nunique());c3.metric("互动量中位数",f"{view.engagement_score.median():,.0f}");c4.metric("高互动内容",int(view.is_high_engagement.sum()))
left,right=st.columns(2)
with left:
    market=view.groupby("market_group",as_index=False).engagement_score.median().sort_values("engagement_score")
    st.plotly_chart(px.bar(market,x="engagement_score",y="market_group",orientation="h",title="各市场分组互动量中位数"),use_container_width=True)
with right:
    sent=view.groupby(["market_group","sentiment"]).size().rename("posts").reset_index()
    st.plotly_chart(px.bar(sent,x="market_group",y="posts",color="sentiment",title="启发式情感构成",barmode="relative"),use_container_width=True)
brand=view.groupby(["market_group","brand"],as_index=False).agg(posts=("post_id_hash","count"),median_engagement=("engagement_score","median")).sort_values("median_engagement",ascending=False)
st.subheader("品牌表现");st.dataframe(brand,use_container_width=True,hide_index=True)
st.info("互动得分为项目自定义探索指标：点赞 + 2×评论 + 2×收藏 + 3×分享，不代表平台官方口径。")

trend_path=ROOT/"data"/"external_aggregates"/"google_trends_weekly_calibrated.csv"
trend_summary_path=ROOT/"data"/"external_aggregates"/"google_trends_brand_summary.csv"
if trend_path.exists() and trend_summary_path.exists():
    st.divider();st.header("Google Trends｜全球搜索兴趣")
    trends=pd.read_csv(trend_path,parse_dates=["date"])
    trend_summary=pd.read_csv(trend_summary_path)
    selected=st.multiselect("趋势品牌",trend_summary.sort_values("recent_rank").brand.tolist(),default=trend_summary.sort_values("recent_rank").brand.head(6).tolist())
    trend_view=trends[trends.brand.isin(selected)]
    st.plotly_chart(px.line(trend_view,x="date",y="calibrated_index",color="brand",title="过去12个月周度相对搜索兴趣"),use_container_width=True)
    display=trend_summary.sort_values("recent_rank")[["recent_rank","brand","recent_13w_mean","zero_share","below_one_weeks"]]
    st.dataframe(display,use_container_width=True,hide_index=True)
    st.warning("跨批次指数通过3CE和MISTINE桥接，仅用于相对比较，不是搜索量。低于1的值以0.5进行敏感性估计；零值较多的品牌应谨慎解释。")

oy_path=ROOT/"data"/"external_aggregates"/"oliveyoung_makeup_top20_2026-07-11.csv"
if oy_path.exists():
    st.divider();st.header("Olive Young｜Top in Korea Makeup")
    oy=pd.read_csv(oy_path)
    st.caption("2026-07-11官方榜单快照；排名与小红书互动量不在同一尺度。")
    st.dataframe(oy[["rank","brand","product_name","rating","current_price_usd"]],use_container_width=True,hide_index=True)
