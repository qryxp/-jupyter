"""业务看板模板 📊 —— 把常用「多图组合」固化成一条命令。

两种玩法（都满足你说的"后面类似的也能加上"）：

① 固化看板（直接套，首版 6 个覆盖四域）：
        da.图表.看板(df, 名称="地区销售")
        da.图表.看板(df, 名称="地区销售", 预设="商务蓝")
   名称可选：地区销售 / 渠道对比 / 收益趋势 / 品类销售 / 账号表现 / 接单效率

② 自定义看板（不写函数，临时拼任意组合）：
        da.图表.自定义看板(df, 图表=[
            ("柱状图","地区","销售额"),
            ("饼图","地区","销售额"),
        ])

看板清单 / 查看配方：
        da.图表.看板清单()
        da.图表.查看配方(da.图表.地区销售看板)

返回形态（跨引擎一致最稳）：
    · 默认 组合=False → 返回 dict {子图标题: 图对象}，Jupyter 里多张图依次渲染
    · 组合=True      → plotly/pyecharts 拼成单张看板；seaborn 自动退回 dict（已知限制）
    · 数据缺某子图所需列时，自动跳过该子图并提示，不让看板崩
"""
import inspect
from dataclasses import dataclass
from typing import Callable, List

import pandas as pd

from .base import 画, _全局


_BOARD_REGISTRY: dict = {}


@dataclass
class BoardMeta:
    name: str
    columns: List[str]
    description: str
    func: Callable = None


def 看板模板(name, 列=None, 说明=""):
    """装饰器：把一个返回「图规格列表」的函数登记为看板模板。

    被装饰的函数返回形如：
        [{"标题": "...", "类型": "柱状图", "x": "地区", "y": "销售额",
          "kw": {"top_n": 10}}, ...]
    图规格里用到的列都在 列= 里登记，供 da.图表.看板清单() 展示。
    """
    def deco(f):
        _BOARD_REGISTRY[f.__name__] = BoardMeta(name, 列 or [], 说明, func=f)
        f.recipe = lambda: inspect.getsource(f)
        f.board_meta = _BOARD_REGISTRY[f.__name__]
        return f
    return deco


# ===================== 缺列解析辅助 =====================
def _所需列(x, y, kw):
    cols = []
    for c in (x, y, kw.get("stack"), kw.get("size"), kw.get("color"), kw.get("z")):
        if c:
            cols.append(c)
    return cols


def _组装(图组, engine, 组合):
    """把 [(标题, 图对象), ...] 组装成最终返回。"""
    if not 图组:
        print("⚠️ 没有任何子图可画（所需列可能都缺失）。")
        return {}
    if not 组合:
        return {标题: 图 for 标题, 图 in 图组}

    # —— 组合成单张 ——
    if engine == "plotly":
        from plotly.subplots import make_subplots
        n = len(图组)
        cols_n = 2 if n > 1 else 1
        rows = (n + cols_n - 1) // cols_n
        # 饼图/环形图 是 domain 类型，不能与 xy 子图混在同一网格，
        # 必须给对应格子标 type="domain"，否则报错。
        域类型 = {"pie"}
        specs = []
        for i in range(rows):
            row_specs = []
            for j in range(cols_n):
                idx = i * cols_n + j
                if idx < n:
                    t = 图组[idx][1].data[0].type if 图组[idx][1].data else "xy"
                    row_specs.append({"type": "domain" if t in 域类型 else "xy"})
                else:
                    row_specs.append({"type": "xy"})
            specs.append(row_specs)
        fig = make_subplots(rows=rows, cols=cols_n, specs=specs,
                            subplot_titles=[t for t, _ in 图组])
        for i, (_, sub) in enumerate(图组):
            r = i // cols_n + 1
            c = i % cols_n + 1
            for trace in sub.data:
                fig.add_trace(trace, row=r, col=c)
        return fig
    if engine == "pyecharts":
        from pyecharts.charts import Page
        page = Page()
        for _, 图 in 图组:
            page.add(图)
        return page
    # seaborn 不支持多图拼合，退回 dict 并提示
    print("⚠️ seaborn 暂不支持多图拼合成单张，已逐张返回（dict）。")
    return {标题: 图 for 标题, 图 in 图组}


def _按规格画图(df, spec, engine, 预设):
    """按单个图规格画图（含缺列跳过）。"""
    类型 = spec["类型"]
    x = spec.get("x")
    y = spec.get("y")
    kw = dict(spec.get("kw", {}))
    need = _所需列(x, y, kw)
    missing = [c for c in need if c not in df.columns]
    if missing:
        print(f"⚠️ 缺列 {missing}（{spec['标题']}），已跳过该子图")
        return None
    try:
        图 = 画(df, 类型=类型, x=x, y=y, engine=engine, 预设=预设, **kw)
    except Exception as e:  # noqa: BLE001  某图出错不应拖垮整块看板
        print(f"⚠️ 子图「{spec['标题']}」绘制失败：{e}")
        return None
    return 图


# ===================== 对外入口 =====================
def 看板(df, 名称, *, engine=None, 预设=None, 组合=False):
    """一键出预置多图组合。

    名称可选（见 da.图表.看板清单()）：
        地区销售 / 渠道对比 / 收益趋势 / 品类销售 / 账号表现 / 接单效率
    engine : "plotly"(默认) / "seaborn" / "pyecharts"
    预设   : 清爽白(默认) / 商务蓝 / 活力橙 / 暗夜（换黑底用 预设="暗夜"）
    组合   : True=拼成单张看板；False(默认)=返回 dict，多张图依次渲染
    """
    engine = engine or _全局["默认引擎"]
    预设 = 预设 or _全局["默认预设"]
    meta = _BOARD_REGISTRY.get(名称)
    if meta is None:
        # 同时支持 @看板模板(name="...") 里的中文友好名查找
        for m in _BOARD_REGISTRY.values():
            if m.name == 名称:
                meta = m
                break
    if meta is None:
        raise ValueError(f"未知看板 {名称!r}，可选：{list(_BOARD_REGISTRY)}（或其友好名："
                         f"{[m.name for m in _BOARD_REGISTRY.values()]}）")
    spec = meta.func()                      # 模板函数返回图规格列表（与数据无关）
    图组 = []
    for s in spec:
        图 = _按规格画图(df, s, engine, 预设)
        if 图 is not None:
            图组.append((s["标题"], 图))
    return _组装(图组, engine, 组合)


def 自定义看板(df, 图表=None, *, engine=None, 预设=None, 组合=False):
    """临时拼任意图组合，不写函数。

    图表=[("柱状图","地区","销售额"),
          ("饼图","地区","销售额"),
          ("折线图","月份","销售额", {"color":"品类"})]

    每个图是 (类型, x, y) 或 (类型, x, y, kw字典)。
    """
    engine = engine or _全局["默认引擎"]
    预设 = 预设 or _全局["默认预设"]
    图组 = []
    for item in (图表 or []):
        if len(item) == 3:
            类型, x, y, kw = item[0], item[1], item[2], {}
        elif len(item) >= 4:
            类型, x, y, kw = item[0], item[1], item[2], item[3]
        else:
            raise ValueError("每个图需 (类型, x, y) 或 (类型, x, y, kw字典)")
        spec = {"标题": f"{类型} · {x}", "类型": 类型, "x": x, "y": y, "kw": kw}
        图 = _按规格画图(df, spec, engine, 预设)
        if 图 is not None:
            图组.append((spec["标题"], 图))
    return _组装(图组, engine, 组合)


def 看板清单():
    """列出所有固化看板模板。"""
    for name, meta in _BOARD_REGISTRY.items():
        print(f"├─ {meta.name}  ({name})")
        print(f"│     所需列 : {meta.columns}")
        if meta.description:
            print(f"│     说明 : {meta.description}")
    return None


# ===================== 6 个固化模板（覆盖四域） =====================
@看板模板(name="地区销售", 列=["地区", "销售额", "月份"],
          说明="柱状(地区×销售额)+饼(占比)+折线(月份趋势)")
def 地区销售看板():
    return [
        {"标题": "各地区销售额", "类型": "柱状图", "x": "地区", "y": "销售额", "kw": {}},
        {"标题": "各地区销售额占比", "类型": "饼图", "x": "地区", "y": "销售额", "kw": {}},
        {"标题": "月度销售趋势", "类型": "折线图", "x": "月份", "y": "销售额", "kw": {}},
    ]


@看板模板(name="渠道对比", 列=["渠道来源", "实收金额"],
          说明="柱状(渠道×实收)+饼(渠道占比)")
def 渠道对比看板():
    return [
        {"标题": "各渠道实收金额", "类型": "柱状图", "x": "渠道来源", "y": "实收金额", "kw": {}},
        {"标题": "各渠道实收占比", "类型": "饼图", "x": "渠道来源", "y": "实收金额", "kw": {}},
    ]


@看板模板(name="收益趋势", 列=["月份", "净到手率", "实收金额"],
          说明="折线(月份×净到手率)+柱状(月份×实收)")
def 收益趋势看板():
    return [
        {"标题": "净到手率趋势", "类型": "折线图", "x": "月份", "y": "净到手率", "kw": {}},
        {"标题": "实收金额趋势", "类型": "柱状图", "x": "月份", "y": "实收金额", "kw": {}},
    ]


@看板模板(name="品类销售", 列=["地区", "销售额", "品类"],
          说明="堆叠(地区×销售额,stack=品类)+柱状(品类×销售额,top_n=10)")
def 品类销售看板():
    return [
        {"标题": "地区×品类销售额(堆叠)", "类型": "堆叠柱状图", "x": "地区", "y": "销售额",
         "kw": {"stack": "品类"}},
        {"标题": "各类目销售额Top10", "类型": "柱状图", "x": "品类", "y": "销售额",
         "kw": {"top_n": 10}},
    ]


@看板模板(name="账号表现", 列=["日期", "粉丝数", "互动率", "内容类型", "阅读播放"],
          说明="折线(日期×粉丝数)+折线(日期×互动率)+饼(内容类型×阅读)")
def 账号表现看板():
    return [
        {"标题": "粉丝增长", "类型": "折线图", "x": "日期", "y": "粉丝数", "kw": {}},
        {"标题": "互动率走势", "类型": "折线图", "x": "日期", "y": "互动率", "kw": {}},
        {"标题": "内容类型阅读分布", "类型": "饼图", "x": "内容类型", "y": "阅读播放", "kw": {}},
    ]


@看板模板(name="接单效率", 列=["渠道来源", "中标率", "日期", "首标时长h"],
          说明="柱状(渠道×中标率)+折线(日期×首标时效)")
def 接单效率看板():
    return [
        {"标题": "各渠道中标率", "类型": "柱状图", "x": "渠道来源", "y": "中标率", "kw": {}},
        {"标题": "首标时效走势", "类型": "折线图", "x": "日期", "y": "首标时长h", "kw": {}},
    ]
