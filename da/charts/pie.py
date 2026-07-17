"""饼图 / 环形图 —— 三引擎。

场景：渠道占比、品类占比、客户来源构成……
数值默认按类别求和（agg），适合"各部分占整体多少"。
预设：清爽白 / 商务蓝 / 活力橙 / 暗夜（默认 清爽白）。
"""
from .base import 图表, _require, 聚合填充, 套用_plotly, 套用_seaborn, 套用_pyecharts
import matplotlib.pyplot as plt


@图表(name="饼图", engines=["plotly", "seaborn", "pyecharts"],
      params="df, x, y, *, engine='plotly', agg='sum', 预设='清爽白', **kw",
      description="各部分占整体的比例（如各渠道成交额占比）")
def 饼图(df, x=None, y=None, *, engine="plotly", agg="sum", 预设="清爽白", **kw):
    """各部分占整体的比例（如各渠道成交额占比）。默认显示百分比+标签。

    参数
    ----
    x      : 分类列（必填），如 "渠道来源"、"品类"
    y      : 数值列（必填），如 "销售额"
    agg    : 同类汇总（默认 "sum"），详见 聚合填充
    预设    : 换黑底用 预设="暗夜"（饼图在暗夜下配色自动转亮）
    engine : plotly / seaborn / pyecharts
    **kw   : 透传（如 hole 改环形、pull 某块突出）
    """
    data = 聚合填充(df, x, y, agg=agg)
    title = f"{y} 占比 · 按 {x}"

    if engine == "plotly":
        px = _require("plotly")["px"]
        fig = px.pie(data, names=x, values=y, title=title,
                     template="plotly_white", hole=0, **kw)
        fig.update_traces(textinfo="percent+label",
                          pull=[0.05 if i == 0 else 0 for i in range(len(data))])
        fig.update_layout(font_size=14, title_font_size=18, margin=dict(t=50, b=20))
        return 套用_plotly(fig, 预设)

    if engine == "seaborn":
        palette = 套用_seaborn(预设)
        fig, ax = plt.subplots(figsize=(7, 7))
        try:
            colors = plt.get_cmap(palette).colors
        except Exception:
            colors = plt.cm.Set2.colors
        ax.pie(data[y], labels=data[x].astype(str), autopct="%1.1f%%",
               startangle=90, counterclock=False, colors=colors, **kw)
        ax.set_title(title, fontsize=15)
        ax.axis("equal")
        plt.tight_layout()
        return ax

    # pyecharts
    Pie = _require("pyecharts")["Pie"]
    opts = _require("pyecharts")["opts"]
    pairs = list(zip(data[x].astype(str).tolist(),
                     [round(float(v), 2) for v in data[y].tolist()]))
    c = (Pie()
         .add("", pairs, radius=["0%", "70%"],
              label_opts=opts.LabelOpts(formatter="{b}: {d}%")))
    c.set_global_opts(title_opts=opts.TitleOpts(title=title, pos_left="center"),
                      toolbox_opts=opts.ToolboxOpts(),
                      legend_opts=opts.LegendOpts(orient="vertical", pos_left="left"))
    return 套用_pyecharts(c, 预设)


@图表(name="环形图", engines=["plotly", "seaborn", "pyecharts"],
      params="df, x, y, *, engine='plotly', agg='sum', 预设='清爽白', hole=0.45, **kw",
      description="中间留空的饼图，更现代，适合仪表盘/看板")
def 环形图(df, x=None, y=None, *, engine="plotly", agg="sum", 预设="清爽白", hole=0.45, **kw):
    """中间留空的饼图，更现代，适合仪表盘/看板。比饼图多一个 hole 参数。

    参数
    ----
    x, y, agg, 预设, engine : 同 饼图（hole 默认 0.45，调大中间越空）
    hole   : 中间空洞比例（0=普通饼图，0.6=细环），可改成 0.6 等
    预设="暗夜" 换黑底。
    """
    data = 聚合填充(df, x, y, agg=agg)
    title = f"{y} 占比 · 按 {x}"

    if engine == "plotly":
        px = _require("plotly")["px"]
        fig = px.pie(data, names=x, values=y, title=title,
                     template="plotly_white", hole=hole, **kw)
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(font_size=14, title_font_size=18, margin=dict(t=50, b=20))
        return 套用_plotly(fig, 预设)

    if engine == "seaborn":
        palette = 套用_seaborn(预设)
        fig, ax = plt.subplots(figsize=(7, 7))
        try:
            colors = plt.get_cmap(palette).colors
        except Exception:
            colors = plt.cm.Set2.colors
        ax.pie(data[y], labels=data[x].astype(str), autopct="%1.1f%%",
               startangle=90, counterclock=False, wedgeprops=dict(width=hole),
               colors=colors, **kw)
        ax.set_title(title, fontsize=15)
        ax.axis("equal")
        plt.tight_layout()
        return ax

    # pyecharts
    Pie = _require("pyecharts")["Pie"]
    opts = _require("pyecharts")["opts"]
    pairs = list(zip(data[x].astype(str).tolist(),
                     [round(float(v), 2) for v in data[y].tolist()]))
    c = (Pie()
         .add("", pairs, radius=["45%", "70%"],
              label_opts=opts.LabelOpts(formatter="{b}: {d}%")))
    c.set_global_opts(title_opts=opts.TitleOpts(title=title, pos_left="center"),
                      toolbox_opts=opts.ToolboxOpts(),
                      legend_opts=opts.LegendOpts(orient="vertical", pos_left="left"))
    return 套用_pyecharts(c, 预设)
