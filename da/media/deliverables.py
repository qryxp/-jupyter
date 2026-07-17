"""域C 自媒体 · 可交付项目。

- 账号估值模型 ：给甲方看的参考估值
- 内容类型AB对比：不同内容类型的互动率/商单收入对比
"""
import pandas as pd

from ..core.utils import 列存在, 安全除法


def 账号估值模型(df, 估值月数=12, 估值倍数=2):
    列存在(df, "粉丝数", "商单收入")
    粉丝数 = int(df["粉丝数"].iloc[0])
    年预期 = df["商单收入"].sum() * 估值月数
    return {
        "粉丝数": 粉丝数,
        "年预期商单收入": round(年预期, 2),
        "估值(参考)": round(年预期 * 估值倍数, 2),
    }


def 内容类型AB对比(df):
    列存在(df, "内容类型", "点赞", "收藏", "评论", "阅读播放", "商单收入")

    def f(d):
        return pd.Series({
            "平均互动率": 安全除法((d["点赞"] + d["收藏"] + d["评论"]).sum(), d["阅读播放"].sum()),
            "平均商单收入": round(d["商单收入"].mean(), 2),
        })
    return df.groupby("内容类型").apply(f).reset_index()
