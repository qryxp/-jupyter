"""域A 技能外包 · 渠道指标。"""
from .._registry import metric
from ..core.utils import 列存在, 聚合, 安全除法


@metric(name="单渠道转化率", domain="技能外包", category="渠道指标",
        fields=["渠道来源", "咨询量"],
        formula="单渠道转化率 = 各渠道成交数 / 该渠道咨询量")
def 单渠道转化率(df):
    列存在(df, "渠道来源", "咨询量")

    def f(d):
        return 安全除法(len(d), d["咨询量"].sum())
    return df.groupby("渠道来源").apply(f)


@metric(name="老客复购率", domain="技能外包", category="渠道指标",
        fields=["是否老客"],
        formula="老客复购率 = 老客订单数 / 总订单数")
def 老客复购率(df, by=None):
    列存在(df, "是否老客")

    def f(d):
        s = d["是否老客"].astype(str).str.strip().str.lower()
        老 = s.isin(["老客", "是", "复购", "1", "true", "y", "yes"])
        return float(老.mean()) if len(s) else 0.0
    return 聚合(df, by, f)
