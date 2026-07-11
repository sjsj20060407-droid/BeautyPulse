import pandas as pd
from beautypulse.features import add_features

def test_features_and_engagement_score():
    frame=pd.DataFrame([{"platform":"xiaohongshu","post_id_hash":"x","title":"持妆显白","description":"下午暗沉卡粉","hashtags":"#粉底液","product_category":"unknown","like_count":100,"comment_count":10,"collect_count":20,"share_count":5}])
    out=add_features(frame)
    assert out.loc[0,"product_category"] == "base"
    assert "long_wear" in out.loc[0,"selling_points"]
    assert "oxidation" in out.loc[0,"pain_points"]
    assert out.loc[0,"engagement_score"] == 175
