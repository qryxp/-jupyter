"""域B 小微电商 · 转化漏斗（曝光→点击→下单→付款）。"""
from .._registry import metric
from ..core.utils import 列存在, 聚合, 安全除法


@metric(name="曝光点击率", domain="小微电商", category="转化漏斗",
        fields=["曝光", "点击"], formula="点击率 = 点击 / 曝光")
def 曝光点击率(df, by=None):
    列存在(df, "曝光", "点击")

    def f(d):
        return 安全除法(d["点击"].sum(), d["曝光"].sum())
    return 聚合(df, by, f)


@metric(name="点击下单率", domain="小微电商", category="转化漏斗",
        fields=["点击", "销量"], formula="下单率 = 销量 / 点击")
def 点击下单率(df, by=None):
    列存在(df, "点击", "销量")

    def f(d):
        return 安全除法(d["销量"].sum(), d["点击"].sum())
    return 聚合(df, by, f)


@metric(name="整体转化率", domain="小微电商", category="转化漏斗",
        fields=["曝光", "销量"], formula="整体转化率 = 销量 / 曝光")
def 整体转化率(df, by=None):
    列存在(df, "曝光", "销量")

    def f(d):
        return 安全除法(d["销量"].sum(), d["曝光"].sum())
    return 聚合(df, by, f)
