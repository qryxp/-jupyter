"""域C 自媒体 · 多列（3列）派生指标。

互动率（4列：点赞+收藏+评论/阅读播放）已在 engagement.py，这里放其余
需要 3 个字段同时参与才能算的指标。字段在 @metric(fields=[...]) 登记，
供 da.能力探测(df) 判断可算性。
"""
from .._registry import metric
from ..core.utils import 列存在, 聚合, 安全除法


@metric(name="内容投产比", domain="自媒体", category="变现指标",
        fields=["商单收入", "制作成本", "投放成本"],
        formula="内容投产比 = 商单收入 / (制作成本 + 投放成本)",
        可选列=["制作成本", "投放成本"])
def 内容投产比(df, by=None):
    列存在(df, "商单收入", "制作成本", "投放成本")

    def f(d):
        return 安全除法(d["商单收入"].sum(),
                       d["制作成本"].sum() + d["投放成本"].sum())
    return 聚合(df, by, f)


@metric(name="掉粉率", domain="自媒体", category="增长指标",
        fields=["掉粉数", "期初粉丝数", "新增粉丝数"],
        formula="掉粉率 = 掉粉数 / (期初粉丝数 + 新增粉丝数)")
def 掉粉率(df, by=None):
    列存在(df, "掉粉数", "期初粉丝数", "新增粉丝数")

    def f(d):
        return 安全除法(d["掉粉数"].sum(),
                       d["期初粉丝数"].sum() + d["新增粉丝数"].sum())
    return 聚合(df, by, f)


@metric(name="千粉月收益", domain="自媒体", category="变现指标",
        fields=["商单收入", "粉丝数", "月份数"],
        formula="千粉月收益 = 商单收入 / (粉丝数 / 1000) / 月份数")
def 千粉月收益(df, by=None):
    列存在(df, "商单收入", "粉丝数", "月份数")

    def f(d):
        return 安全除法(d["商单收入"].sum(),
                       安全除法(d["粉丝数"].sum(), 1000) * d["月份数"].sum())
    return 聚合(df, by, f)
