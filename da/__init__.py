"""个人网络接单数据分析指标计算库 `da`。

导入方式
--------
    import da
    import pandas as pd

中文调用（推荐，最顺手）
------------------------
    da.技能外包.净到手率(df)
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
