"""域B 小微电商 · 可交付项目。

- 爆款滞销分层   ：按销量把 SKU 标成 爆款/平销/滞销
- 利润敏感度分析 ：涨价 1 元影响多少净利
- 库存周转预警   ：周转率过低预警
"""
import pandas as pd

from ..core.utils import 列存在, 安全除法


def 爆款滞销分层(df, 爆款阈值=None, 滞销阈值=0):
    列存在(df, "SKU", "销量")
    s = df.groupby("SKU")["销量"].sum()
    if 爆款阈值 is None:
        爆款阈值 = s.quantile(0.8)
    out = s.reset_index()
    out["分层"] = out["销量"].apply(lambda v: "爆款" if v >= 爆款阈值 else ("滞销" if v <= 滞销阈值 else "平销"))
    return out


def 利润敏感度分析(df, 涨价=1):
    列存在(df, "单价", "销量", "成本", "平台扣点")
    原净利 = ((df["单价"] - df["成本"]) * df["销量"] - df["平台扣点"]).sum()
    新净利 = (((df["单价"] + 涨价) - df["成本"]) * df["销量"] - df["平台扣点"]).sum()
    return {
        "原净利": round(原净利, 2),
        "涨价后净利": round(新净利, 2),
        "净利多赚": round(新净利 - 原净利, 2),
        "单位涨价": 涨价,
    }


def 库存周转预警(df, 周转预警线=0.2):
    列存在(df, "SKU", "销量", "库存")
    g = df.groupby("SKU").agg(销量=("销量", "sum"), 库存=("库存", "sum"))
    g["周转率"] = g.apply(lambda r: 安全除法(r["销量"], r["库存"]), axis=1)
    g["预警"] = g["周转率"].apply(lambda v: "⚠️周转慢" if v < 周转预警线 else "✅健康")
    return g.reset_index()
