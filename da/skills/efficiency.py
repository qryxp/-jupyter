"""域A 技能外包 · 产能与质量指标。"""
from .._registry import metric
from ..core.utils import 列存在, 聚合, 安全除法


@metric(name="客单价", domain="技能外包", category="收益指标",
        fields=["实收金额"],
        formula="客单价 = 实收金额合计 / 接单量")
def 客单价(df, by=None):
    列存在(df, "实收金额")

    def f(d):
        return 安全除法(d["实收金额"].sum(), len(d))
    return 聚合(df, by, f)


@metric(name="时薪", domain="技能外包", category="产能指标",
        fields=["实收金额", "交付时长h"],
        formula="时薪 = 实收金额合计 / 交付时长合计(h)")
def 时薪(df, by=None):
    列存在(df, "实收金额", "交付时长h")

    def f(d):
        return 安全除法(d["实收金额"].sum(), d["交付时长h"].sum())
    return 聚合(df, by, f)


@metric(name="返工率", domain="技能外包", category="质量指标",
        fields=["返工次数"],
        formula="返工率 = (返工次数>0 的订单数) / 总订单数")
def 返工率(df, by=None):
    列存在(df, "返工次数")

    def f(d):
        return float((d["返工次数"] > 0).mean())
    return 聚合(df, by, f)
