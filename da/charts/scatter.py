"""散点图 / 气泡图 —— 三引擎（气泡图 pyecharts 暂不支持，请用 plotly/seaborn）。

场景：单价 vs 销量、工时 vs 收入（找离群高价值单）、互动率 vs 粉丝数……
size 参数把第三维画成气泡大小；color 按类别上色。
预设：清爽白 / 商务蓝 / 活力橙 / 暗夜（默认 清爽白）。
"""
from .base import 图表, _require, 套用_plotly, 套用_seaborn, 套用_pyecharts
import pandas as pd


@图表(name="散点图", engines=["plotly", "seaborn", "pyecharts"],
      params="df, x, y, color=None, *, engine='plotly', 预设='清爽白', **kw",
      description="两数值变量的相关性/分布（如单价 vs 销量）")
def 散点图(df, x=None, y=None, color=None, *, engine="plotly", 预设="清爽白", **kw):
    """两数值变量的相关性/分布（如单价 vs 销量，找离群高价值单）。

    参数
    ----
    x      : 横轴数值列，如 "单价"
    y      : 纵轴数值列，如 "销量"
    color  : 按类别上色（可选），如 "品类"——不同类不同颜色
    预设    : 换黑底用 预设="暗夜"
    engine : plotly / seaborn / pyecharts 三引擎均支持
    **kw   : 透传（size、symbol、title 等）
    """
    列 = [c for c in [x, y, color] if c]
    data = df[列].copy()
    title = f"{y} vs {x}"

    if engine == "plotly":
        px = _require("plotly")["px"]
        fig = px.scatter(data, x=x, y=y, color=color, title=title,
                         template="plotly_white", **kw)
        fig.update_layout(font_size=14, title_font_size=18, margin=dict(t=50, b=40))
        return 套用_plotly(fig, 预设)

    if engine == "seaborn":
        plt = _require("seaborn")["plt"]
        sns = _require("seaborn")["sns"]
        套用_seaborn(预设)
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.scatterplot(data=data, x=x, y=y, hue=color, ax=ax, alpha=0.8, **kw)
        ax.set_title(title, fontsize=15)
        plt.tight_layout()
        return ax

    # pyecharts：先 add_xaxis 再 add_yaxis
    Scatter = _require("pyecharts")["Scatter"]
    opts = _require("pyecharts")["opts"]
    cats = [str(v) for v in sorted(data[x].unique())]
    c = Scatter().add_xaxis(cats)
    if color:
        for s in sorted(data[color].astype(str).unique()):
            sub = data[data[color].astype(str) == s]
            pts = [[float(r[x]), float(r[y])] for _, r in sub.iterrows()]
            c.add_yaxis(str(s), pts, symbol_size=10)
    else:
        pts = [[float(r[x]), float(r[y])] for _, r in data.iterrows()]
        c.add_yaxis("数值", pts, symbol_size=10)
    c.set_global_opts(
        title_opts=opts.TitleOpts(title=title, pos_left="center"),
        xaxis_opts=opts.AxisOpts(name=x), yaxis_opts=opts.AxisOpts(name=y),
        toolbox_opts=opts.ToolboxOpts(), tooltip_opts=opts.TooltipOpts())
    return 套用_pyecharts(c, 预设)


@图表(name="气泡图", engines=["plotly", "seaborn"],
      params="df, x, y, size, color=None, *, engine='plotly', 预设='清爽白', **kw",
      description="在散点基础上用 size 列表示第三维（如销量气泡大小）")
def 气泡图(df, x=None, y=None, size=None, color=None, *, engine="plotly", 预设="清爽白", **kw):
    """在散点基础上用 size 列表示第三维（如销量作为气泡大小）。

    参数
    ----
    x      : 横轴数值列，如 "单价"
    y      : 纵轴数值列，如 "销售额"
    size   : 气泡大小列（必填），如 "销量"、"收藏数"
    color  : 按类别上色（可选）
    预设    : 换黑底用 预设="暗夜"
    engine : plotly / seaborn（pyecharts 暂不支持气泡图，传了会报错提示）
    **kw   : 透传（size_max、sizes 范围等）
    """
    if size is None:
        raise ValueError("气泡图需要 size 参数（决定气泡大小的列）")
    if engine == "pyecharts":
        raise NotImplementedError("气泡图在 pyecharts 下暂不支持，请改用 engine='plotly' 或 'seaborn'")
    列 = list(dict.fromkeys([c for c in [x, y, size, color] if c]))
    data = df[列].copy()
    title = f"{y} vs {x}（气泡={size}）"

    if engine == "plotly":
        px = _require("plotly")["px"]
        fig = px.scatter(data, x=x, y=y, size=size, color=color, title=title,
                         template="plotly_white", size_max=60, **kw)
        fig.update_layout(font_size=14, title_font_size=18, margin=dict(t=50, b=40))
        return 套用_plotly(fig, 预设)

    # seaborn
    plt = _require("seaborn")["plt"]
    sns = _require("seaborn")["sns"]
    套用_seaborn(预设)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(data=data, x=x, y=y, size=size, hue=color, ax=ax,
                    sizes=(30, 400), alpha=0.8, **kw)
    ax.set_title(title, fontsize=15)
    plt.tight_layout()
    return ax
