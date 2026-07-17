"""域B 小微电商 · 规模/风险/盈利/库存 指标。

合并了「销售与交易口径词典」里的补充项：净销售额、订单数(去重)、
客单价ATV、件单价、连带率、金额口径退款率、坪效、人效。
"""
from .._registry import metric
from ..core.utils import 列存在, 聚合, 安全除法


@metric(name="销售额", domain="小微电商", category="规模指标",
        fields=["单价", "销量"], formula="销售额 = Σ(单价 × 销量)")
def 销售额(df, by=None):
    列存在(df, "单价", "销量")

    def f(d):
        return (d["单价"] * d["销量"]).sum()
    return 聚合(df, by, f)


@metric(name="GMV", domain="小微电商", category="规模指标",
        fields=["单价", "销量"], formula="GMV = Σ(单价 × 销量)（含退款的虚荣指标）")
def GMV(df, by=None):
    列存在(df, "单价", "销量")

    def f(d):
        return (d["单价"] * d["销量"]).sum()
    return 聚合(df, by, f)


@metric(name="净销售额", domain="小微电商", category="规模指标",
        fields=["实付金额", "退款金额"],
        formula="净销售额 = Σ实付金额 − Σ退款金额（真金白银，以此为准）")
def 净销售额(df, by=None):
    列存在(df, "实付金额", "退款金额")

    def f(d):
        return d["实付金额"].sum() - d["退款金额"].sum()
    return 聚合(df, by, f)


@metric(name="订单数", domain="小微电商", category="规模指标",
        fields=["订单ID"], formula="订单数 = COUNT(DISTINCT 订单ID)")
def 订单数(df, by=None):
    列存在(df, "订单ID")

    def f(d):
        return d["订单ID"].nunique()
    return 聚合(df, by, f)


@metric(name="客单价ATV", domain="小微电商", category="规模指标",
        fields=["实付金额", "退款金额", "订单ID"],
        formula="客单价ATV = 净销售额 / 订单数")
def 客单价ATV(df, by=None):
    列存在(df, "实付金额", "退款金额", "订单ID")

    def f(d):
        return 安全除法(d["实付金额"].sum() - d["退款金额"].sum(), d["订单ID"].nunique())
    return 聚合(df, by, f)


@metric(name="件单价", domain="小微电商", category="规模指标",
        fields=["实付金额", "退款金额", "销量"],
        formula="件单价 = 净销售额 / Σ销量")
def 件单价(df, by=None):
    列存在(df, "实付金额", "退款金额", "销量")

    def f(d):
        return 安全除法(d["实付金额"].sum() - d["退款金额"].sum(), d["销量"].sum())
    return 聚合(df, by, f)


@metric(name="连带率", domain="小微电商", category="规模指标",
        fields=["销量", "订单ID"], formula="连带率 = Σ销量 / 订单数（一单买几件）")
def 连带率(df, by=None):
    列存在(df, "销量", "订单ID")

    def f(d):
        return 安全除法(d["销量"].sum(), d["订单ID"].nunique())
    return 聚合(df, by, f)


@metric(name="GMV退款修正", domain="小微电商", category="规模指标",
        fields=["单价", "销量", "退款数"], formula="GMV退款修正 = Σ((销量 − 退款数) × 单价)")
def GMV退款修正(df, by=None):
    列存在(df, "单价", "销量", "退款数")

    def f(d):
        return ((d["销量"] - d["退款数"]) * d["单价"]).sum()
    return 聚合(df, by, f)


@metric(name="退款率", domain="小微电商", category="风险指标",
        fields=["退款数", "销量"], formula="退款率 = Σ退款数 / Σ销量")
def 退款率(df, by=None):
    列存在(df, "退款数", "销量")

    def f(d):
        return 安全除法(d["退款数"].sum(), d["销量"].sum())
    return 聚合(df, by, f)


@metric(name="金额退款率", domain="小微电商", category="风险指标",
        fields=["退款金额", "实付金额"], formula="金额退款率 = Σ退款金额 / Σ实付金额")
def 金额退款率(df, by=None):
    列存在(df, "退款金额", "实付金额")

    def f(d):
        return 安全除法(d["退款金额"].sum(), d["实付金额"].sum())
    return 聚合(df, by, f)


@metric(name="销售毛利率", domain="小微电商", category="盈利指标",
        fields=["单价", "销量", "成本", "平台扣点"],
        formula="毛利率 = (销售额 − 成本×销量 − 平台扣点) / 销售额")
def 销售毛利率(df, by=None):
    列存在(df, "单价", "销量", "成本", "平台扣点")

    def f(d):
        销售额 = (d["单价"] * d["销量"]).sum()
        成本额 = (d["成本"] * d["销量"]).sum()
        return 安全除法(销售额 - 成本额 - d["平台扣点"].sum(), 销售额)
    return 聚合(df, by, f)


@metric(name="动销率", domain="小微电商", category="库存指标",
        fields=["SKU", "销量"], formula="动销率 = 有销量的SKU数 / 总SKU数")
def 动销率(df):
    列存在(df, "SKU", "销量")
    return 安全除法((df.groupby("SKU")["销量"].sum() > 0).sum(), df["SKU"].nunique())


@metric(name="坪效", domain="小微电商", category="线下指标",
        fields=["销售额", "门店面积"], formula="坪效 = 销售额 / 门店面积")
def 坪效(df, by=None):
    列存在(df, "销售额", "门店面积")

    def f(d):
        return 安全除法(d["销售额"].sum(), d["门店面积"].sum())
    return 聚合(df, by, f)


@metric(name="人效", domain="小微电商", category="线下指标",
        fields=["销售额", "员工人数"], formula="人效 = 销售额 / 员工人数")
def 人效(df, by=None):
    列存在(df, "销售额", "员工人数")

    def f(d):
        return 安全除法(d["销售额"].sum(), d["员工人数"].sum())
    return 聚合(df, by, f)
