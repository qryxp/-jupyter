"""分布类图表：热力图 / 箱线图 / 直方图。

- 热力图：三列 (x, y, 值) 透视成矩阵，看交叉强度（如地区×月份销量）。
- 箱线图：某数值按类别的分布（如各渠道接单金额分布，找异常单）。
- 直方图：单数值列的分布形态（如报价金额集中在哪段）。
  注：直方图在 pyecharts 下暂不支持，请用 plotly / seaborn。
预设：清爽白 / 商务蓝 / 活力橙 / 暗夜（默认 清爽白）。
"""
from .base import 图表, _require, 套用_plotly, 套用_seaborn, 套用_pyecharts


@图表(name="热力图", engines=["plotly", "seaborn", "pyecharts"],
      params="df, x, y, z, *, engine='plotly', 预设='清爽白', **kw",
      description="三列透视成矩阵，看交叉强度（地区×月份销量等）")
def 热力图(df, x=None, y=None, z=None, *, engine="plotly", 预设="清爽白", **kw):
    """三列透视成矩阵，看交叉强度（如 地区×月份 的销量热力）。

    参数（这是唯一需要 3 列的图）
    ----
    x      : 列方向分类（如 "月份"）
    y      : 行方向分类（如 "地区"）
    z      : 交叉处的数值列（如 "销售额"）—— 必填
    预设    : 换黑底用 预设="暗夜"（配色自动转亮）
    engine : plotly / seaborn / pyecharts 三引擎均支持
    **kw   : 透传（colorscale、annot 等）
    """
    if not (x and y and z):
        raise ValueError("热力图需要 x、y（行列）与 z（数值）三列")
    title = f"{z} · {y} × {x}"
    piv = df.pivot_table(index=y, columns=x, values=z, aggfunc="sum").fillna(0)
    xcats = [str(c) for c in piv.columns]
    ycats = [str(i) for i in piv.index]
    matrix = piv.values.tolist()

    if engine == "plotly":
        go = _require("plotly")["go"]
        fig = go.Figure(go.Heatmap(z=matrix, x=xcats, y=ycats,
                                   colorscale="YlGnBu",
                                   colorbar=dict(title=z), **kw))
        fig.update_layout(title=title, template="plotly_white",
                          font_size=14, title_font_size=18)
        return 套用_plotly(fig, 预设)

    if engine == "seaborn":
        plt = _require("seaborn")["plt"]
        sns = _require("seaborn")["sns"]
        套用_seaborn(预设)
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(piv, annot=True, fmt=".0f", cmap="YlGnBu",
                    linewidths=0.5, ax=ax, **kw)
        ax.set_title(title, fontsize=15)
        plt.tight_layout()
        return ax

    # pyecharts
    HeatMap = _require("pyecharts")["HeatMap"]
    opts = _require("pyecharts")["opts"]
    data_pts = []
    for j, yi in enumerate(piv.index):
        for i, xi in enumerate(piv.columns):
            data_pts.append([i, j, round(float(piv.iloc[j, i]), 2)])
    c = (HeatMap()
         .add_xaxis(xcats)
         .add_yaxis(z, ycats, data_pts,
                    label_opts=opts.LabelOpts(is_show=True, position="inside"), **kw))
    c.set_global_opts(
        title_opts=opts.TitleOpts(title=title, pos_left="center"),
        visualmap_opts=opts.VisualMapOpts(min_=float(piv.values.min()),
                                          max_=float(piv.values.max()),
                                          orient="horizontal", pos_bottom="5%"),
        toolbox_opts=opts.ToolboxOpts())
    return 套用_pyecharts(c, 预设)


@图表(name="箱线图", engines=["plotly", "seaborn", "pyecharts"],
      params="df, x, y, *, engine='plotly', 预设='清爽白', **kw",
      description="某数值按类别的分布，找离群/异常单")
def 箱线图(df, x=None, y=None, *, engine="plotly", 预设="清爽白", **kw):
    """某数值按类别的分布，找离群/异常单（如各渠道接单金额分布）。

    参数
    ----
    x      : 分类列（横轴分组），如 "渠道来源"
    y      : 数值列（必填），如 "实收金额"
    预设    : 换黑底用 预设="暗夜"
    engine : plotly / seaborn / pyecharts
    **kw   : 透传（points="all" 显示全部点、notched 缺口等）
    """
    title = f"{y} 分布 · 按 {x}"

    if engine == "plotly":
        px = _require("plotly")["px"]
        fig = px.box(df, x=x, y=y, title=title,
                     template="plotly_white", points="outliers", **kw)
        fig.update_layout(font_size=14, title_font_size=18, margin=dict(t=50, b=40))
        return 套用_plotly(fig, 预设)

    if engine == "seaborn":
        plt = _require("seaborn")["plt"]
        sns = _require("seaborn")["sns"]
        套用_seaborn(预设)
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.boxplot(data=df, x=x, y=y, ax=ax, palette=套用_seaborn(预设), **kw)
        ax.set_title(title, fontsize=15)
        ax.tick_params(axis="x", rotation=30)
        plt.tight_layout()
        return ax

    # pyecharts
    Boxplot = _require("pyecharts")["Boxplot"]
    opts = _require("pyecharts")["opts"]
    cats = [str(c) for c in sorted(df[x].unique())]
    groups = [df[df[x].astype(str) == c][y].tolist() for c in cats]
    prepared = Boxplot.prepare_data(groups)
    c = (Boxplot().add_xaxis(cats).add_yaxis("分布", prepared))
    c.set_global_opts(
        title_opts=opts.TitleOpts(title=title, pos_left="center"),
        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=30)),
        toolbox_opts=opts.ToolboxOpts())
    return 套用_pyecharts(c, 预设)


@图表(name="直方图", engines=["plotly", "seaborn"],
      params="df, x, *, engine='plotly', bins=20, 预设='清爽白', **kw",
      description="单数值列的分布形态（如报价金额集中在哪段）")
def 直方图(df, x=None, *, engine="plotly", bins=20, 预设="清爽白", **kw):
    """单数值列的分布形态（如报价金额集中在哪一段）。

    参数
    ----
    x      : 数值列（必填），如 "报价金额"
    bins   : 柱子数量（默认 20），调大更细、调小更粗
    预设    : 换黑底用 预设="暗夜"
    engine : plotly / seaborn（pyecharts 暂不支持直方图，传了会报错提示）
    **kw   : 透传（color、histnorm 等）
    """
    title = f"{x} 分布"
    if engine == "pyecharts":
        raise NotImplementedError("直方图在 pyecharts 下暂不支持，请改用 engine='plotly' 或 'seaborn'")

    if engine == "plotly":
        px = _require("plotly")["px"]
        fig = px.histogram(df, x=x, nbins=bins, title=title,
                           template="plotly_white", **kw)
        fig.update_layout(font_size=14, title_font_size=18, margin=dict(t=50, b=40))
        return 套用_plotly(fig, 预设)

    # seaborn
    plt = _require("seaborn")["plt"]
    sns = _require("seaborn")["sns"]
    套用_seaborn(预设)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(df, x=x, bins=bins, ax=ax, color="#5B8FB9", **kw)
    ax.set_title(title, fontsize=15)
    plt.tight_layout()
    return ax
