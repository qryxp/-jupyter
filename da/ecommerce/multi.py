"""域B 小微电商 · 多列（3列/4列）派生指标。

注意：部分指标输入里用到了「销售额」「销售成本」这种**派生列**。
如果原始表只有 单价/销量/成本单价 等，先用 da.小微电商.销售额(df) 等
算出来再加进去，或直接用下面带「单价/销量/成本」四列版的等价公式。
所有字段都在 @metric(fields=[...]) 登记，供 da.能力探测(df) 判断可算性。
"""
from .._registry import metric
from ..core.utils import 列存在, 聚合, 安全除法


@metric(name="销售毛利额", domain="小微电商", category="盈利指标",
        fields=["销售额", "成本", "平台扣点"],
        formula="销售毛利额 = 销售额 − 成本 − 平台扣点",
        可选列=["成本", "平台扣点"])
def 销售毛利额(df, by=None):
    列存在(df, "销售额", "成本", "平台扣点")

    def f(d):
        return d["销售额"].sum() - d["成本"].sum() - d["平台扣点"].sum()
    return 聚合(df, by, f)


@metric(name="销售净利率", domain="小微电商", category="盈利指标",
        fields=["销售额", "成本", "平台扣点", "推广费"],
        formula="销售净利率 = (销售额 − 成本 − 平台扣点 − 推广费) / 销售额",
        可选列=["成本", "平台扣点", "推广费"])
def 销售净利率(df, by=None):
    列存在(df, "销售额", "成本", "平台扣点", "推广费")

    def f(d):
        return 安全除法(d["销售额"].sum() - d["成本"].sum()
                       - d["平台扣点"].sum() - d["推广费"].sum(),
                       d["销售额"].sum())
    return 聚合(df, by, f)


@metric(name="盈亏平衡销量", domain="小微电商", category="盈利指标",
        fields=["固定成本", "单价", "单位变动成本"],
        formula="盈亏平衡销量 = 固定成本 / (单价 − 单位变动成本)")
def 盈亏平衡销量(df, by=None):
    列存在(df, "固定成本", "单价", "单位变动成本")

    def f(d):
        return 安全除法(d["固定成本"].sum(),
                       (d["单价"] - d["单位变动成本"]).sum())
    return 聚合(df, by, f)


@metric(name="库存周转天数", domain="小微电商", category="库存指标",
        fields=["期长天数", "销售成本", "平均库存"],
        formula="库存周转天数 = 期长天数 / (销售成本 / 平均库存)")
def 库存周转天数(df, by=None):
    列存在(df, "期长天数", "销售成本", "平均库存")

    def f(d):
        return 安全除法(d["期长天数"].sum(),
                       安全除法(d["销售成本"].sum(), d["平均库存"].sum()))
    return 聚合(df, by, f)


@metric(name="推广净ROI", domain="小微电商", category="投放指标",
        fields=["销售额", "成本", "推广费"],
        formula="推广净ROI = (销售额 − 成本 − 推广费) / 推广费",
        可选列=["成本"])
def 推广净ROI(df, by=None):
    列存在(df, "销售额", "成本", "推广费")

    def f(d):
        return 安全除法(d["销售额"].sum() - d["成本"].sum() - d["推广费"].sum(),
                       d["推广费"].sum())
    return 聚合(df, by, f)
