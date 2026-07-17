"""折线图 / 面积图 —— 三引擎。

场景：销售额随月份变化、各渠道转化趋势、互动率走势……
支持 color 参数画多条系列（如不同地区的趋势线）。
预设：清爽白 / 商务蓝 / 活力橙 / 暗夜（默认 清爽白）。
"""
from .base import 图表, _require, 聚合填充, 套用_plotly, 套用_seaborn, 套用_pyecharts
import pandas as pd


def _准备序列数据(df, x, y, color, agg):
    """按 (x[, color]) 聚合，返回可直接画图的长表。"""
    if color:
        if agg is None:
            return df[[x, color, y]].copy()
        return df.groupby([x, color], as_index=False)[y].agg(agg)
    return 聚合填充(df, x, y, agg=agg, sort=False)


@图表(name="折线图", engines=["plotly", "seaborn", "pyecharts"],
      params="df, x, y, color=None, *, engine='plotly', agg='sum', 预设='清爽白', markers=True, **kw",
      description="随时间/顺序的数值走势，color 可画多条系列")
def 折线图(df, x=None, y=None, color=None, *, engine="plotly", agg="sum",
         预设="清爽白", markers=True, **kw):
    """随时间/顺序的数值走势（如销售额随月份变化）。color 可画多条系列。

    参数
    ----
    x      : 顺序/时间列（横轴），如 "月份"、"日期"
    y      : 数值列，如 "销售额"
    color  : 系列列（可选），如 "地区" → 同一图里画多条线对比趋势
    agg    : 汇总方式（默认 "sum"），按 (x[,color]) 聚合
    markers: 是否显示数据点（默认 True）
    预设    : 换黑底用 预设="暗夜"
    engine : plotly / seaborn / pyecharts（pyecharts 必须先 add_xaxis 再 add_yaxis）
    **kw   : 透传（title、line_dash 等）
    """
    data = _准备序列数据(df, x, y, color, agg)
    title = f"{y} · 按 {x}"

    if engine == "plotly":
        px = _require("plotly")["px"]
        fig = px.line(data, x=x, y=y, color=color, title=title,
                      markers=markers, template="plotly_white", **kw)
        fig.update_layout(font_size=14, title_font_size=18, margin=dict(t=50, b=40))
        return 套用_plotly(fig, 预设)

    if engine == "seaborn":
        plt = _require("seaborn")["plt"]
        sns = _require("seaborn")["sns"]
        套用_seaborn(预设)
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.lineplot(data=data, x=x, y=y, hue=color, marker="o" if markers else None,
                     ax=ax, **kw)
        ax.set_title(title, fontsize=15)
        ax.tick_params(axis="x", rotation=30)
        plt.tight_layout()
        return ax

    # pyecharts：必须先 add_xaxis 再 add_yaxis
    Line = _require("pyecharts")["Line"]
    opts = _require("pyecharts")["opts"]
    cats = [str(c) for c in sorted(data[x].unique())]
    c = Line().add_xaxis(cats)
    if color:
        for s in sorted(data[color].astype(str).unique()):
            sub = data[data[color].astype(str) == s]
            vals = [round(float(sub[sub[x].astype(str) == cat][y].sum()), 2) for cat in cats]
            c.add_yaxis(s, vals, is_smooth=False, symbol="circle", symbol_size=6)
    else:
        vals = [round(float(data[data[x].astype(str) == cat][y].sum()), 2) for cat in cats]
        c.add_yaxis("数值", vals, is_smooth=False, symbol="circle", symbol_size=6)
    c.set_global_opts(
        title_opts=opts.TitleOpts(title=title, pos_left="center"),
        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=30)),
        toolbox_opts=opts.ToolboxOpts(), tooltip_opts=opts.TooltipOpts(trigger="axis"))
    return 套用_pyecharts(c, 预设)


@图表(name="面积图", engines=["plotly", "seaborn", "pyecharts"],
      params="df, x, y, color=None, *, engine='plotly', agg='sum', 预设='清爽白', **kw",
      description="折线 + 填充，强调累计/体量（如累计收益）")
def 面积图(df, x=None, y=None, color=None, *, engine="plotly", agg="sum",
         预设="清爽白", **kw):
    """折线 + 下方填充，强调累计/体量（如累计收益走势）。

    参数与 折线图 基本一致：x=顺序列, y=数值列, color=多系列, agg=汇总方式。
    预设="暗夜" 换黑底；engine 支持 plotly / seaborn / pyecharts。
    """
    data = _准备序列数据(df, x, y, color, agg)
    title = f"{y} · 按 {x}（累计）"

    if engine == "plotly":
        px = _require("plotly")["px"]
        fig = px.area(data, x=x, y=y, color=color, title=title,
                      template="plotly_white", **kw)
        fig.update_layout(font_size=14, title_font_size=18, margin=dict(t=50, b=40))
        return 套用_plotly(fig, 预设)

    if engine == "seaborn":
        plt = _require("seaborn")["plt"]
        sns = _require("seaborn")["sns"]
        套用_seaborn(预设)
        fig, ax = plt.subplots(figsize=(8, 5))
        if color:
            for s, g in data.groupby(color):
                g = g.sort_values(x)
                ax.fill_between(g[x], g[y], alpha=0.35, label=str(s))
                ax.plot(g[x], g[y], marker="o")
            ax.legend()
        else:
            g = data.sort_values(x)
            ax.fill_between(g[x], g[y], alpha=0.35)
            ax.plot(g[x], g[y], marker="o")
        ax.set_title(title, fontsize=15)
        ax.tick_params(axis="x", rotation=30)
        plt.tight_layout()
        return ax

    # pyecharts
    Line = _require("pyecharts")["Line"]
    opts = _require("pyecharts")["opts"]
    cats = [str(c) for c in sorted(data[x].unique())]
    c = Line().add_xaxis(cats)
    if color:
        for s in sorted(data[color].astype(str).unique()):
            sub = data[data[color].astype(str) == s]
            vals = [round(float(sub[sub[x].astype(str) == cat][y].sum()), 2) for cat in cats]
            c.add_yaxis(s, vals, areastyle_opts=opts.AreaStyleOpts(opacity=0.35))
    else:
        vals = [round(float(data[data[x].astype(str) == cat][y].sum()), 2) for cat in cats]
        c.add_yaxis("数值", vals, areastyle_opts=opts.AreaStyleOpts(opacity=0.35))
    c.set_global_opts(
        title_opts=opts.TitleOpts(title=title, pos_left="center"),
        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=30)),
        toolbox_opts=opts.ToolboxOpts())
    return 套用_pyecharts(c, 预设)
