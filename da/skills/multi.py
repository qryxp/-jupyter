"""域A 技能外包 · 多列（3列/4列）派生指标。

这里专门放「需要 3 个或 4 个原始字段同时参与，才算得出来」的指标，
与 profit.py / efficiency.py（多为 2 列指标）区分开，方便你按"列数"找。
公式里出现的每个字段都会在 @metric(fields=[...]) 里登记，
供 da.能力探测(df) 判断「这份数据够不够算这个指标」。
"""
from .._registry import metric
from ..core.utils import 列存在, 聚合, 安全除法


@metric(name="单均净利润", domain="技能外包", category="收益指标",
        fields=["实收金额", "平台抽成", "成本"],
        formula="单均净利润 = 实收金额 − 平台抽成 − 成本",
        可选列=["平台抽成", "成本"])
def 单均净利润(df, by=None):
    列存在(df, "实收金额", "平台抽成", "成本")

    def f(d):
        return d["实收金额"].sum() - d["平台抽成"].sum() - d["成本"].sum()
    return 聚合(df, by, f)


@metric(name="综合成本率", domain="技能外包", category="成本指标",
        fields=["实收金额", "平台抽成", "成本", "税费"],
        formula="综合成本率 = (平台抽成 + 成本 + 税费) / 实收金额",
        可选列=["税费"])
def 综合成本率(df, by=None):
    列存在(df, "实收金额", "平台抽成", "成本", "税费")

    def f(d):
        return 安全除法(d["平台抽成"].sum() + d["成本"].sum() + d["税费"].sum(),
                       d["实收金额"].sum())
    return 聚合(df, by, f)


@metric(name="时薪净利", domain="技能外包", category="产能指标",
        fields=["实收金额", "平台抽成", "成本", "交付时长h"],
        formula="时薪净利 = (实收金额 − 平台抽成 − 成本) / 交付时长h",
        可选列=["平台抽成", "成本"])
def 时薪净利(df, by=None):
    列存在(df, "实收金额", "平台抽成", "成本", "交付时长h")

    def f(d):
        return 安全除法(d["实收金额"].sum() - d["平台抽成"].sum() - d["成本"].sum(),
                       d["交付时长h"].sum())
    return 聚合(df, by, f)


@metric(name="渠道净收益率", domain="技能外包", category="渠道指标",
        fields=["实收金额", "平台抽成", "成本", "报价金额", "渠道来源"],
        formula="渠道净收益率 = (实收金额 − 平台抽成 − 成本) / 报价金额  （按 渠道来源 分组）",
        可选列=["平台抽成", "成本"])
def 渠道净收益率(df, by="渠道来源"):
    列存在(df, "实收金额", "平台抽成", "成本", "报价金额", "渠道来源")

    def f(d):
        return 安全除法(d["实收金额"].sum() - d["平台抽成"].sum() - d["成本"].sum(),
                       d["报价金额"].sum())
    return 聚合(df, by, f)
