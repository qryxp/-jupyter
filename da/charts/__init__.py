"""图表生成模块 📊 —— Seaborn / Plotly / PyEcharts 三引擎，命令式中文调用。

两种调用方式（都支持预设）：
  ① 极简统一入口（推荐初学者）：只给中文图表类型名
        da.图表.画(df, 类型="柱状图", x="地区", y="销售额", 预设="商务蓝")
  ② 直接调函数：
        da.图表.柱状图(df, x="地区", y="销售额", engine="seaborn", 预设="活力橙")

看某图表的"优调好的源码"
------------------------
    da.图表.查看配方(da.图表.柱状图)
    da.show_recipe(da.图表.柱状图)

看全部图表 / 预设
------------------
    da.图表.图表清单()
    da.图表.预设清单()
    da.图表.预设示例()          # 打印每种预设的调用代码，抄着用
    da.图表.设定(默认引擎="plotly", 默认预设="商务蓝")   # 配一次，以后省略
"""
from .base import (图表, 图表清单, 查看配方, ENGINES, 预设库,
                   预设清单, 预设示例, 设定, 画,
                   图表注册表, 检查引擎, _require, 聚合填充)
from .bar import 柱状图, 堆叠柱状图
from .line import 折线图, 面积图
from .pie import 饼图, 环形图
from .scatter import 散点图, 气泡图
from .dist import 热力图, 箱线图, 直方图
from .boards import (看板, 自定义看板, 看板清单, 看板模板,
                     地区销售看板, 渠道对比看板, 收益趋势看板,
                     品类销售看板, 账号表现看板, 接单效率看板)
from . import _自定义看板  # noqa: F401  自定义看板（da.更新.加看板 写入）

# 英文别名（IDE 自动补全更稳时可用）
bar = 柱状图
stacked_bar = 堆叠柱状图
line = 折线图
area = 面积图
pie = 饼图
donut = 环形图
scatter = 散点图
bubble = 气泡图
heatmap = 热力图
boxplot = 箱线图
histogram = 直方图
board = 看板
custom_board = 自定义看板
board_list = 看板清单

__all__ = [
    # 中文
    "柱状图", "堆叠柱状图", "折线图", "面积图", "饼图", "环形图",
    "散点图", "气泡图", "热力图", "箱线图", "直方图",
    "画", "设定", "预设清单", "预设示例", "图表清单", "查看配方", "ENGINES",
    # 看板
    "看板", "自定义看板", "看板清单", "看板模板",
    "地区销售看板", "渠道对比看板", "收益趋势看板",
    "品类销售看板", "账号表现看板", "接单效率看板",
    # 英文别名
    "bar", "stacked_bar", "line", "area", "pie", "donut",
    "scatter", "bubble", "heatmap", "boxplot", "histogram",
    "board", "custom_board", "board_list",
]
