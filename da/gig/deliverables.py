"""域D 零工平台 · 可交付项目。"""
from ..core.utils import 列存在


def 评价分布(df):
    """统计评价分分布（给平台/个人看板用）。"""
    列存在(df, "评价分")
    return (df["评价分"].value_counts().sort_index()
            .rename("单数").reset_index().rename(columns={"index": "评分", "评价分": "评分"}))
