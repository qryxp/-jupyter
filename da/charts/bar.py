"""柱状图 / 堆叠柱状图 —— 三引擎（plotly / seaborn / pyecharts）。

最常用场景：各地区的销售额、各渠道成交量、各月收益……
调用即自动按类别聚合，参数已为你调好（白底、配色调色板、数值标签）。
预设：清爽白 / 商务蓝 / 活力橙 / 暗夜（默认 清爽白）。
"""
from .base import 图表, _require, 聚合填充, 套用_plotly, 套用_seaborn, 套用_pyecharts


@图表(name="柱状图", engines=["plotly", "seaborn", "pyecharts"],
      params="df, x, y, *, engine='plotly', agg='sum', 预设='清爽白', top_n=None, **kw",
      description="按类别汇总数值的柱状图，带数值标签，最长尾可选 top_n")
def 柱状图(df, x=None, y=None, *, engine="plotly", agg="sum", 预设="清爽白", top_n=None, **kw):
    """各分类的数值对比（如各地区销售额）。已为你调好：白底、配色、数值标签。

    参数
    ----
    x      : 分类列（必填），如 "地区"、"渠道来源"、"月份"
    y      : 数值列（必填），如 "销售额"、"成交量"
    agg    : 同类怎么汇总 → "sum"(默认)/"mean"/"count"/None(已汇总)
    top_n  : 只画 y 最大的前 N 个（长尾友好）            ← 类别太多时常用
    预设    : 样式主题，换黑底用 预设="暗夜"
    engine : plotly(默认,交互) / seaborn(静态) / pyecharts(HTML看板)
    **kw   : 透传给底层引擎（如 color、title、text_auto）
    """
    data = 聚合填充(df, x, y, agg=agg, top_n=top_n)
    title = f"{y} · 按 {x}"

    if engine == "plotly":
        px = _require("plotly")["px"]
        fig = px.bar(data, x=x, y=y, color=x, title=title,
                     template="plotly_white", text_auto=".2s", **kw)
        fig.update_layout(font_size=14, title_font_size=18, margin=dict(t=50, b=40))
        fig.update_traces(marker_line_width=0, textposition="outside",
                          selector=dict(type="bar"))
        return 套用_plotly(fig, 预设)

    if engine == "seaborn":
        plt = _require("seaborn")["plt"]
        sns = _require("seaborn")["sns"]
        palette = 套用_seaborn(预设)
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(data=data, x=x, y=y, ax=ax, palette=palette, **kw)
        ax.set_title(title, fontsize=15)
        ax.tick_params(axis="x", rotation=30)
        for c in ax.containers:
            ax.bar_label(c, fmt="%.1f", padding=2, fontsize=9)
        plt.tight_layout()
        return ax

    # pyecharts
    Bar = _require("pyecharts")["Bar"]
    opts = _require("pyecharts")["opts"]
    c = (Bar()
         .add_xaxis(data[x].astype(str).tolist())
         .add_yaxis("数值", [round(v, 2) for v in data[y].tolist()],
                    label_opts=opts.LabelOpts(position="top", formatter="{c}"),
                    itemstyle_opts=opts.ItemStyleOpts(border_width=0)))
    c.set_global_opts(
        title_opts=opts.TitleOpts(title=title, pos_left="center"),
        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=30)),
        toolbox_opts=opts.ToolboxOpts(),
        datazoom_opts=[opts.DataZoomOpts(type_="slider")] if len(data) > 8 else None)
    return 套用_pyecharts(c, 预设)


@图表(name="堆叠柱状图", engines=["plotly", "seaborn", "pyecharts"],
      params="df, x, y, stack, *, engine='plotly', agg='sum', 预设='清爽白', **kw",
      description="按 x 分组、用 stack 列堆叠，看构成结构（如各地区各品类销量）")
def 堆叠柱状图(df, x=None, y=None, stack=None, *, engine="plotly", agg="sum",
             预设="清爽白", **kw):
    """按 x 分组、用 stack 列堆叠，看构成结构（如各地区各品类销量）。

    参数
    ----
    x      : 主分类列（横轴），如 "地区"
    y      : 数值列，如 "销售额"
    stack  : 堆叠维度列（必填），如 "品类"、"渠道"——决定柱子怎么分层
    agg    : 汇总方式（默认 "sum"），详见 聚合填充
    预设    : 换黑底用 预设="暗夜"
    engine : plotly / seaborn / pyecharts
    **kw   : 透传（color、title 等）
    """
    if stack is None:
        raise ValueError("堆叠柱状图需要 stack 参数（用于堆叠的类别列）")
    if agg is None:
        data = df[[x, stack, y]].copy()
    else:
        data = df.groupby([x, stack], as_index=False)[y].agg(agg)
    title = f"{y} · 按 {x} 堆叠 {stack}"

    if engine == "plotly":
        px = _require("plotly")["px"]
        fig = px.bar(data, x=x, y=y, color=stack, title=title,
                     barmode="stack", template="plotly_white", **kw)
        fig.update_layout(font_size=14, title_font_size=18, margin=dict(t=50, b=40))
        return 套用_plotly(fig, 预设)

    if engine == "seaborn":
        plt = _require("seaborn")["plt"]
        sns = _require("seaborn")["sns"]
        palette = 套用_seaborn(预设)
        fig, ax = plt.subplots(figsize=(8, 5))
        piv = data.pivot(index=x, columns=stack, values=y).fillna(0)
        piv.plot(kind="bar", stacked=True, ax=ax, colormap=__cmap(palette), **kw)
        ax.set_title(title, fontsize=15)
        ax.tick_params(axis="x", rotation=30)
        plt.tight_layout()
        return ax

    # pyecharts
    Bar = _require("pyecharts")["Bar"]
    opts = _require("pyecharts")["opts"]
    cats = [str(c) for c in sorted(data[x].unique())]
    series = [str(s) for s in sorted(data[stack].unique())]
    c = Bar().add_xaxis(cats)
    for s in series:
        vals = [round(float(data[(data[x].astype(str) == cat) &
                               (data[stack].astype(str) == s)][y].sum()), 2)
                for cat in cats]
        c.add_yaxis(s, vals, stack="total",
                    label_opts=opts.LabelOpts(is_show=False))
    c.set_global_opts(
        title_opts=opts.TitleOpts(title=title, pos_left="center"),
        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=30)),
        toolbox_opts=opts.ToolboxOpts())
    return 套用_pyecharts(c, 预设)


def __cmap(palette):
    """把 seaborn palette 名转成 matplotlib colormap（用于 pivot 图）。"""
    import matplotlib.pyplot as plt
    try:
        return plt.get_cmap(palette)
    except Exception:
        return "Set2"
