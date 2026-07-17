"""图表模块基础设施。

- 三引擎懒加载（seaborn / plotly / pyecharts）：只有用到某引擎才 import，
  没装的引擎不会拖垮整个包导入，方便"拷到别的电脑"分步安装。
- @图表 注册器：给每个图表函数附上 recipe（优调好的源码）与 chart_meta。
- 聚合填充：把"明细数据"按类别汇总成"可直接画图的两列"，实现你说的
  "给一份各地区销售额，自动出柱状图"。
- 样式预设（presets）：内置几套调好的配色/主题，调用填名字即可。
- 统一入口 画()：只需记"一个动词 + 中文图表类型名"，不用记函数名。
"""
import functools
import inspect
from dataclasses import dataclass
from typing import Callable, List

import pandas as pd

# 支持的三类绘图引擎
ENGINES = ["plotly", "seaborn", "pyecharts"]


@dataclass
class ChartMeta:
    """图表的元数据（与指标的 Metric 平行，但字段不同）。"""
    name: str
    engines: List[str]
    params: str
    description: str = ""
    func: Callable = None


_CHART_REGISTRY: dict = {}


def 图表(name, engines=None, params="", description=""):
    """装饰器：标记一个函数为"可调用图表"，自动附 recipe 与 chart_meta。"""
    def deco(f):
        meta = ChartMeta(name, engines or list(ENGINES), params, description, func=f)
        _CHART_REGISTRY[f.__name__] = meta
        f.recipe = lambda: inspect.getsource(f)
        f.chart_meta = meta
        return f
    return deco


def 图表注册表():
    return _CHART_REGISTRY


def 检查引擎(engine):
    if engine not in ENGINES:
        raise ValueError(f"不支持的引擎 {engine!r}，可选：{ENGINES}")


def _require(engine):
    """按需导入绘图引擎，缺失时给出版本/安装提示而不是一堆 traceback。"""
    检查引擎(engine)
    if engine == "plotly":
        import plotly.express as px
        import plotly.graph_objects as go
        return {"px": px, "go": go}
    if engine == "seaborn":
        import matplotlib.pyplot as plt
        import seaborn as sns
        return {"plt": plt, "sns": sns}
    if engine == "pyecharts":
        from pyecharts.charts import Bar, Line, Pie, Scatter, HeatMap, Boxplot
        from pyecharts import options as opts
        return {"Bar": Bar, "Line": Line, "Pie": Pie,
                "Scatter": Scatter, "HeatMap": HeatMap,
                "Boxplot": Boxplot, "opts": opts}


def 聚合填充(df, x, y, agg="sum", top_n=None, sort=True):
    """把明细按 x 聚合成 (x, y) 两列，得到可直接画图的数据。

    这是所有图表内部都会调用的「自动聚合填充」逻辑——你直接给明细行，
    它帮你按类别汇总好再画图。

    参数
    ----
    df    : 明细数据（一行一笔订单/一条记录）
    x     : 分类列（如 "地区"）—— 作为横轴/分组
    y     : 数值列（如 "销售额"）—— 作为纵轴/汇总值
    agg   : 汇总方式，决定「同类怎么合并」：
            · "sum"  (默认) 同类求和，最常用（销售额、成交量…）
            · "mean"         同类求平均（客单价、评分…）
            · "count"        同类计数（订单笔数…）
            · "max"/"min"    最大/最小
            · None           数据已经是一类一行，原样取两列，不聚合
    top_n : 只保留 y 最大的前 N 个类别，应对「类别太多/长尾」——
            比如客户有 200 个，只画成交额前 10 名：top_n=10
    sort  : 是否按 y 降序排（默认 True，柱子从高到低更好看）
    """
    if agg is None:
        data = df[[x, y]].copy()
    else:
        data = df.groupby(x, as_index=False)[y].agg(agg)
    if sort and agg is not None:
        data = data.sort_values(y, ascending=False)
    if top_n:
        data = data.head(int(top_n))
    return data.reset_index(drop=True)


# ============================ 样式预设 ============================
# 每套预设 = 三引擎各自的调优参数字典。
# plotly: template + colorway；seaborn: style + palette + font；pyecharts: 颜色列表。
#
# 💡 想「换黑底」怎么改？—— 不用动代码，调用时传 预设="暗夜" 即可：
#    da.图表.柱状图(df, x="地区", y="销售额", 预设="暗夜")
# 预设在内部做的事情（你一般不用管）：
#    · plotly  → template 由 plotly_white 变成 plotly_dark，配色换成高亮色
#    · seaborn → style 由 whitegrid 变成 darkgrid，调色板换成 viridis
#    · pyecharts → 整套颜色换成亮色系（深色底上才看得清）
# 默认预设是 "清爽白"（白底）。
预设库 = {
    "清爽白": {
        "plotly": dict(template="plotly_white",
                       colorway=["#5B8FB9", "#A7C4BC", "#F4A261", "#E76F51",
                                 "#2A9D8F", "#E9C46A", "#8D99AE"]),
        "seaborn": dict(style="whitegrid", palette="Set2", font="Microsoft YaHei"),
        "pyecharts": ["#5B8FB9", "#A7C4BC", "#F4A261", "#E76F51",
                      "#2A9D8F", "#E9C46A", "#8D99AE"],
    },
    "商务蓝": {
        "plotly": dict(template="plotly",
                       colorway=["#1F4E79", "#2E75B6", "#5B9BD5", "#9DC3E6",
                                 "#BDD7EE", "#DEEBF7", "#2F5496"]),
        "seaborn": dict(style="whitegrid", palette="Blues_r", font="Microsoft YaHei"),
        "pyecharts": ["#1F4E79", "#2E75B6", "#5B9BD5", "#9DC3E6",
                      "#BDD7EE", "#DEEBF7", "#2F5496"],
    },
    "活力橙": {
        "plotly": dict(template="plotly_white",
                       colorway=["#E76F51", "#F4A261", "#E9C46A", "#2A9D8F",
                                 "#264653", "#E76F51", "#F4A261"]),
        "seaborn": dict(style="whitegrid", palette="Oranges_r", font="Microsoft YaHei"),
        "pyecharts": ["#E76F51", "#F4A261", "#E9C46A", "#2A9D8F",
                      "#264653", "#E76F51", "#F4A261"],
    },
    "暗夜": {
        "plotly": dict(template="plotly_dark",
                       colorway=["#8ECAE6", "#219EBC", "#FFB703", "#FB8500",
                                 "#023047", "#8ECAE6", "#FFB703"]),
        "seaborn": dict(style="darkgrid", palette="viridis", font="Microsoft YaHei"),
        "pyecharts": ["#8ECAE6", "#219EBC", "#FFB703", "#FB8500",
                      "#023047", "#8ECAE6", "#FFB703"],
    },
}
默认预设 = "清爽白"
_全局 = {"默认引擎": "plotly", "默认预设": "清爽白"}


def 取预设(engine, name=默认预设):
    name = name or 默认预设
    return 预设库.get(name, 预设库[默认预设]).get(engine, {})


def 套用_plotly(fig, name=默认预设):
    p = 取预设("plotly", name)
    fig.update_layout(template=p.get("template", "plotly_white"),
                      title_font_size=18,
                      font=dict(family=p.get("font", "Microsoft YaHei, sans-serif")))
    if p.get("colorway"):
        fig.layout.colorway = p["colorway"]
    return fig


def 套用_seaborn(name=默认预设):
    """在画图前调用：设定主题与调色板（返回 palette 名供 pie 用）。"""
    import seaborn as sns
    p = 取预设("seaborn", name)
    sns.set_theme(style=p.get("style", "whitegrid"),
                  palette=p.get("palette", "Set2"),
                  font=p.get("font", "Microsoft YaHei"))
    return p.get("palette", "Set2")


def 套用_pyecharts(c, name=默认预设):
    cols = 取预设("pyecharts", name)
    if cols:
        c.set_colors(cols)
    return c


# ============================ 统一极简入口 ============================
def 画(df, 类型, x=None, y=None, *, engine=None, 预设=None, **kw):
    """一句话出图：只给中文图表类型名，不用记函数名。

        da.图表.画(df, 类型="柱状图", x="地区", y="销售额")
        da.图表.画(df, 类型="堆叠柱状图", x="地区", y="销售额", stack="品类")
        da.图表.画(df, 类型="气泡图", x="销量", y="销售额", size="销售额")

    参数
    ----
    df     : 明细数据（会自动按 x 聚合，见 聚合填充）
    x      : 分类/横轴列（必填，如 "地区"、"月份"）
    y      : 数值/纵轴列（柱状/折线/饼图必填，如 "销售额"）
    engine : "plotly"(默认·交互) / "seaborn"(静态) / "pyecharts"(HTML看板)
    agg    : 汇总方式，见 聚合填充（默认 "sum"）
    top_n  : 只画前 N 类（长尾友好，柱/条图常用）
    预设    : 样式主题，换黑底用 预设="暗夜"；可选 清爽白/商务蓝/活力橙/暗夜
    其它    : 各图专属参数走 **kw（如 stack / size / z / color / hole / bins）

    引擎/预设 省略时取全局设定（默认 plotly / 清爽白），可用 da.图表.设定() 改。
    """
    engine = engine or _全局["默认引擎"]
    预设 = 预设 or _全局["默认预设"]
    meta = _CHART_REGISTRY.get(类型)
    if meta is None:
        raise ValueError(f"未知图表类型 {类型!r}，可选：{list(_CHART_REGISTRY)}")
    return meta.func(df, x=x, y=y, engine=engine, 预设=预设, **kw)


def 设定(默认引擎=None, 默认预设=None):
    """配置一次全局默认，之后调用可省略 engine / 预设。"""
    if 默认引擎:
        检查引擎(默认引擎)
        _全局["默认引擎"] = 默认引擎
    if 默认预设:
        if 默认预设 not in 预设库:
            raise ValueError(f"未知预设 {默认预设!r}，可选：{list(预设库)}")
        _全局["默认预设"] = 默认预设
    print(f"已设定 → 默认引擎={_全局['默认引擎']}  默认预设={_全局['默认预设']}")


def 预设清单():
    print("可用样式预设：")
    for name in 预设库:
        print(f"  ├─ {name}")
    print(f"\n默认预设：{默认预设}   |   可用引擎：{', '.join(ENGINES)}")


def 预设示例():
    """直接打印每种预设的调用代码，抄着用即可。"""
    print("# 极简调用：先设定默认引擎/预设，再一句话出图")
    print('da.图表.设定(默认引擎="plotly", 默认预设="商务蓝")')
    print('da.图表.画(df, 类型="柱状图", x="地区", y="销售额")')
    print()
    print("# 或每次显式指定预设：")
    for name in 预设库:
        print(f'da.图表.画(df, 类型="柱状图", x="地区", y="销售额", 预设="{name}")')


def 图表清单():
    """打印所有图表（含支持引擎与说明）。"""
    for name, meta in _CHART_REGISTRY.items():
        print(f"├─ {meta.name}  ({name})")
        print(f"│     引擎 : {', '.join(meta.engines)}")
        print(f"│     参数 : {meta.params}")
        if meta.description:
            print(f"│     说明 : {meta.description}")
    return None


def 查看配方(func):
    """打印某个图表/看板的优调源码（同 da.show_recipe，按类型定制表头）。"""
    meta = getattr(func, "chart_meta", None) or getattr(func, "board_meta", None)
    if meta:
        if hasattr(meta, "engines"):          # 图表
            print(f"# 图表 : {meta.name}")
            print(f"# 引擎 : {', '.join(meta.engines)}")
            print(f"# 参数 : {meta.params}")
        else:                                  # 看板
            print(f"# 看板 : {meta.name}")
            print(f"# 所需列 : {meta.columns}")
        if meta.description:
            print(f"# 说明 : {meta.description}")
        print("-" * 48)
    print(func.recipe())
