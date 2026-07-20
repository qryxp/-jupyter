"""个人网络接单数据分析指标计算库 `da`。

导入方式
--------
    import da
    import pandas as pd

中文调用（推荐，最顺手）
------------------------
    da.技能外包.净到手率(df)     # 带域（明确归属时用）
    da.净到手率(df)             # 顶层直呼（不记域也能用，等价上方）
    da.小微电商.销售额(df)
    da.自媒体.互动率(df)
    da.零工平台.中标率(df)

英文调用（等价，IDE 自动补全更稳）
----------------------------------
    da.skills.净到手率(df)          # 模块名英文、指标名中文
    da.skills.net_to_hand_rate(df)  # 全英文别名（可选）

看一个指标的算法配方
--------------------
    da.show_recipe(da.技能外包.净到手率)

看全部指标的多层级清单
----------------------
    da.list_metrics()                 # 全部
    da.list_metrics("技能外包")       # 只看某个域
"""
from . import core, clean, skills, ecommerce, media, gig, charts, 脚手架, 更新
from ._registry import metrics_in, get_registry, 可算指标, 能力探测, 一键计算
from .core.recipe import list_metrics, show_recipe

# 业务域中文别名：让你像说话一样调用
技能外包 = skills
小微电商 = ecommerce
自媒体 = media
零工平台 = gig
数据清洗 = clean
图表 = charts

__all__ = [
    "core", "clean", "skills", "ecommerce", "media", "gig", "charts",
    "脚手架", "更新",
    "技能外包", "小微电商", "自媒体", "零工平台", "数据清洗", "图表",
    "list_metrics", "show_recipe", "metrics_in", "get_registry",
    "可算指标", "能力探测", "一键计算",
]


# ───────────────────────────────────────────────────────────────
# 顶层直呼指标（无需记属于哪个域）
#    da.净到手率(df)  ≡  da.技能外包.净到手率(df)
# 实现：模块级 __getattr__ 在普通属性查不到时，按中文名查注册表返回函数。
# 注意：指标中文名在全部域中须唯一（注册表为 dict，同名后者覆盖前者）。
# ───────────────────────────────────────────────────────────────
def __getattr__(name):
    """顶层按中文名直呼指标，省去记所属业务域。"""
    from ._registry import get_registry
    reg = get_registry()
    if name in reg:
        return reg[name].func
    raise AttributeError(
        f"da 没有属性 {name!r}。\n"
        f"  · 查全部指标：da.list_metrics()\n"
        f"  · 看当前数据能算哪些：da.能力探测(df)\n"
        f"  · 若 {name!r} 是指标，请确认它已用 @metric 注册（且中文名唯一）。"
    )


def __dir__():
    names = list(globals().keys())
    from ._registry import get_registry
    names += list(get_registry().keys())
    return sorted(set(names))
