"""域A 技能外包 · 收益/产能/质量/渠道 指标。"""
from .._registry import metric
from ..core.utils import 列存在, 聚合, 安全除法


@metric(name="净到手率", domain="技能外包", category="收益指标",
        fields=["报价金额", "实收金额", "平台抽成", "成本", "税费", "返工折损"],
        formula="净到手率 = (实收金额 − 平台抽成 − 成本 − 税费 − 返工折损) / 报价金额",
        description="副业最该盯的数：真正落袋占报价的比例")
def 净到手率(df, by=None):
    列存在(df, "报价金额", "实收金额", "平台抽成", "成本", "税费", "返工折损")

    def f(d):
        净 = (d["实收金额"] - d["平台抽成"] - d["成本"] - d["税费"] - d["返工折损"])
        return 安全除法(净.sum(), d["报价金额"].sum())
    return 聚合(df, by, f)


@metric(name="毛利率", domain="技能外包", category="收益指标",
        fields=["实收金额", "成本"],
        formula="毛利率 = (实收金额 − 成本) / 实收金额")
def 毛利率(df, by=None):
    列存在(df, "实收金额", "成本")

    def f(d):
        return 安全除法((d["实收金额"] - d["成本"]).sum(), d["实收金额"].sum())
    return 聚合(df, by, f)


def 返工折损估算(df, 单次返工成本=100):
    """估算每单返工折损 = 返工次数 × 单次返工成本，返回 Series。

    用法：在算净到手率前，先
        df['返工折损'] = da.技能外包.返工折损估算(df, 单次返工成本=150).values
    """
    列存在(df, "返工次数")
    return df["返工次数"] * 单次返工成本
