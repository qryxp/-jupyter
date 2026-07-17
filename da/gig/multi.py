"""域D 零工平台 · 多列（3列/4列）派生指标。

综合履约分（4列加权）、复购加权中标率（3列）、任务接标时效（3列，用
已算好的时长小时列，避免日期解析麻烦）。字段在 @metric(fields=[...]) 登记，
供 da.能力探测(df) 判断可算性。
"""
from .._registry import metric
from ..core.utils import 列存在, 聚合, 安全除法


@metric(name="综合履约分", domain="零工平台", category="质量指标",
        fields=["准时交付率", "好评率", "纠纷率", "复购率"],
        formula="综合履约分 = 准时交付率×0.4 + 好评率×0.4 + (1−纠纷率)×0.1 + 复购率×0.1")
def 综合履约分(df, by=None):
    列存在(df, "准时交付率", "好评率", "纠纷率", "复购率")

    def f(d):
        return (d["准时交付率"].mean() * 0.4
                + d["好评率"].mean() * 0.4
                + (1 - d["纠纷率"].mean()) * 0.1
                + d["复购率"].mean() * 0.1)
    return 聚合(df, by, f)


@metric(name="复购加权中标率", domain="零工平台", category="接单指标",
        fields=["中标数", "投标数", "复购数"],
        formula="复购加权中标率 = (中标数 + 复购数×0.5) / 投标数",
        可选列=["复购数"])
def 复购加权中标率(df, by=None):
    列存在(df, "中标数", "投标数", "复购数")

    def f(d):
        return 安全除法(d["中标数"].sum() + d["复购数"].sum() * 0.5,
                       d["投标数"].sum())
    return 聚合(df, by, f)


@metric(name="任务接标时效", domain="零工平台", category="时效指标",
        fields=["首标时长h", "定标时长h", "平均交付时长h"],
        formula="任务接标时效 = (首标时长h + 定标时长h + 平均交付时长h) 的平均小时")
def 任务接标时效(df, by=None):
    列存在(df, "首标时长h", "定标时长h", "平均交付时长h")

    def f(d):
        return (d["首标时长h"] + d["定标时长h"] + d["平均交付时长h"]).mean()
    return 聚合(df, by, f)
