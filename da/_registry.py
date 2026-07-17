"""指标注册表 + @metric 装饰器。

所有指标通过 @metric 注册，元数据（名称/域/子类/依赖字段/公式）集中存放，
并自动附带 `recipe`（源码配方）和 `metric_meta`，方便一键查看与学习。

【指标缺列容错】
@metric 支持 `可选列` 参数：当数据里少了某些「附加成本/费用」类字段时，
装饰器在调用前自动把缺失的可选列补成全 0 再算（视为"没发生"），
不让整段崩。分母类必填列缺失则照常不可算。
"""
import inspect
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from .core.utils import 聚合, 列存在  # noqa: F401  (供指标函数复用)


@dataclass
class Metric:
    name: str
    func: Callable
    domain: str
    category: str
    fields: List[str]
    formula: str
    description: str = ""
    可选列: List[str] = field(default_factory=list)

    @property
    def 必填列(self):
        """算这个指标「最少需要」的列（fields 中去掉可选列）。"""
        opt = set(self.可选列)
        return [c for c in self.fields if c not in opt]


_REGISTRY: dict = {}


def metric(name, domain, category, fields, formula, description="", 可选列=None):
    """装饰器：把一个函数登记为可调用指标。

    参数
    ----
    name       : 中文显示名（也是检索名）
    domain     : 业务域，如 "技能外包"
    category   : 子类，如 "收益指标"
    fields     : 依赖的原始字段列表（含必填 + 可选）
    formula    : 人类可读的公式
    description: 补充说明
    可选列     : 缺失时自动补 0 的列（一般是附加成本/费用/损耗，如 税费、平台抽成、成本）；
                分母类列（实收金额/销售额/报价金额…）绝不能放进这里
    """
    def deco(f):
        opt = list(可选列 or [])

        def wrapper(df, *a, **kw):
            # 缺的可选列自动补成全 0（视为未发生），不让整段崩
            cols = set(df.columns)
            inj = [c for c in opt if c not in cols]
            if inj:
                df = df.copy()
                for c in inj:
                    df[c] = 0
            wrapper._补0列 = inj
            return f(df, *a, **kw)

        wrapper.__name__ = f.__name__
        wrapper.__doc__ = f.__doc__
        wrapper.recipe = lambda: inspect.getsource(f)
        wrapper.metric_meta = None
        _REGISTRY[f.__name__] = Metric(
            name, wrapper, domain, category,
            list(fields), formula, description, 可选列=opt)
        wrapper.metric_meta = _REGISTRY[f.__name__]
        return wrapper
    return deco


def get_registry():
    return _REGISTRY


def 可算指标(df, domain=None):
    """返回所有『必填字段都能在 df 列中找到』的指标（即当前这份数据能直接算的）。

    注意：可选列缺失也算可算（会自动按 0 处理）。

    用法：
        da.可算指标(df)                  # 全部域里当前数据能算的
        da.可算指标(df, "技能外包")      # 只看技能外包域里能算的
    """
    out = []
    for m in _REGISTRY.values():
        if domain and m.domain != domain:
            continue
        if set(m.必填列).issubset(set(df.columns)):
            out.append(m)
    return out


def 能力探测(df, domain=None):
    """给定一份数据，自动告诉你：

    1) ✅ 当前列能直接算出哪些指标（含公式）
    2) 🔧 再补 **1 个必填字段** 就能多解锁哪些指标（升级提示）
    3) ❌ 完全算不了、缺多个必填字段的指标（仅统计数量）

    这正是「把三种、四种列名同时考虑，尽量榨出可得数据」的核心入口——
    你不必记每个指标要哪几列，丢份数据进来它替你盘清楚。

    可选列缺失时，✅ 列表里会额外打印 ⚠️ 提示（该列按 0 算）。

    用法：
        da.能力探测(df)
        da.能力探测(df, "小微电商")
    """
    cols = set(df.columns)
    全部 = [m for m in _REGISTRY.values() if (not domain or m.domain == domain)]
    ok = [m for m in 全部 if set(m.必填列).issubset(cols)]
    near = [m for m in 全部
            if not set(m.必填列).issubset(cols)
            and len(set(m.必填列) - cols) == 1]
    far = [m for m in 全部
           if not set(m.必填列).issubset(cols)
           and len(set(m.必填列) - cols) > 1]

    print(f"📊 当前数据共 {len(cols)} 列：{sorted(cols)}\n")
    print(f"✅ 可直接计算的指标（{len(ok)} 个）：")
    for m in ok:
        lack_opt = sorted(set(m.可选列) - cols)
        extra = f"   ⚠️ 可选列 {lack_opt} 缺失 → 按0算" if lack_opt else ""
        print(f"   ├─ [{m.domain}·{m.category}] {m.formula}{extra}")
    print(f"\n🔧 再补 「1 个字段」 就能解锁的指标（{len(near)} 个）：")
    for m in near:
        lack = sorted(set(m.必填列) - cols)
        print(f"   ├─ 缺 {lack} → {m.formula}")
    if not near:
        print("   （已无此类，或已全部可算）")
    print(f"\n❌ 还差多个字段才能算的指标（{len(far)} 个，暂不展开）")
    return None


def 一键计算(df, domain=None):
    """把当前数据**能算的所有指标一次性算出来**，返回 {指标中文名: 结果} 字典。

    适合「拿到一份新数据，先无脑扫一遍能出哪些数」的场景。
    标量指标返回数值；带分组(by)的指标返回 Series（索引=分组值）。
    某个指标算出错会被跳过（结果置 None），不影响其它指标。

    注意：必填列齐全、但可选列缺失的指标也会算（可选列按 0）。

    用法：
        res = da.一键计算(df)
        res = da.一键计算(df, "技能外包")
        pd.Series(res).sort_values(ascending=False)   # 当标量时可直接排序看
    """
    out = {}
    for m in 可算指标(df, domain=domain):
        try:
            out[m.name] = m.func(df)
        except Exception:
            out[m.name] = None
    return out


def metrics_in(domain=None, category=None):
    """返回符合条件的 Metric 列表（可按域/子类过滤）。"""
    out = []
    for m in _REGISTRY.values():
        if domain and m.domain != domain:
            continue
        if category and m.category != category:
            continue
        out.append(m)
    return out
