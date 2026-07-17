"""通用工具：列校验、分组聚合封装、空值处理。"""
import pandas as pd


def 列存在(df, *cols):
    """校验 df 是否包含指定列，缺列时给出友好报错。"""
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"缺少列: {missing}\n当前可用列: {list(df.columns)}")


def 聚合(df, by, func, **kwargs):
    """指标聚合封装。

    - by=None：对整张表算一个标量
    - by='某列'：按该列分组，返回 Series（索引为分组值）
    """
    if by is None:
        return func(df, **kwargs)
    return df.groupby(by, group_keys=False).apply(lambda g: func(g, **kwargs))


def 安全除法(分子, 分母, 默认=0.0):
    """避免除以 0 的除法。"""
    分母 = float(分母)
    if 分母 == 0:
        return 默认
    return 分子 / 分母
