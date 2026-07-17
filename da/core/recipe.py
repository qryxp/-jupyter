"""配方（recipe）查看：把指标的公式、依赖字段和源码打印出来，方便学习/复制。"""
from .._registry import metrics_in


def list_metrics(domain=None, category=None, as_tree=True):
    """打印多层级清单：域 → 子类 → 指标(公式)。

    as_tree=True  以树状文本打印（默认）
    as_tree=False 返回 Metric 列表
    """
    rows = metrics_in(domain, category)
    if not as_tree:
        return rows
    tree = {}
    for m in rows:
        tree.setdefault(m.domain, {}).setdefault(m.category, []).append(m)
    for d, cats in tree.items():
        print(f"【{d}】")
        for c, ms in cats.items():
            print(f"  └─ {c}")
            for m in ms:
                print(f"       ├─ {m.name}  =  {m.formula}")
    return None


def show_recipe(func):
    """打印某个指标/图表/看板的：公式或参数 + 依赖字段 + 可复制源码。

    同时兼容指标（metric_meta）、图表（chart_meta）、看板（board_meta）。
    """
    meta = (getattr(func, "metric_meta", None)
            or getattr(func, "chart_meta", None)
            or getattr(func, "board_meta", None))
    if meta:
        if hasattr(meta, "fields"):           # 指标
            print(f"# 指标 : {meta.name}")
            print(f"# 域   : {meta.domain}  |  子类: {meta.category}")
            print(f"# 字段 : {', '.join(meta.fields)}")
            print(f"# 公式 : {meta.formula}")
            if meta.description:
                print(f"# 说明 : {meta.description}")
        elif hasattr(meta, "engines"):        # 图表
            print(f"# 图表 : {meta.name}")
            print(f"# 引擎 : {', '.join(meta.engines)}")
            print(f"# 参数 : {meta.params}")
            if meta.description:
                print(f"# 说明 : {meta.description}")
        else:                                  # 看板
            print(f"# 看板 : {meta.name}")
            print(f"# 所需列 : {meta.columns}")
            if meta.description:
                print(f"# 说明 : {meta.description}")
        print("-" * 48)
    print(func.recipe())
