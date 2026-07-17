"""域D 零工平台 · 双边匹配指标。"""
import pandas as pd

from .._registry import metric
from ..core.utils import 列存在, 聚合, 安全除法


@metric(name="中标率", domain="零工平台", category="接单指标",
        fields=["中标数", "投标数"], formula="中标率 = 中标数 / 投标数")
def 中标率(df, by=None):
    列存在(df, "中标数", "投标数")

    def f(d):
        return 安全除法(d["中标数"].sum(), d["投标数"].sum())
    return 聚合(df, by, f)


@metric(name="纠纷率", domain="零工平台", category="接单指标",
        fields=["纠纷数", "中标数"], formula="纠纷率 = 纠纷数 / 中标数")
def 纠纷率(df, by=None):
    列存在(df, "纠纷数", "中标数")

    def f(d):
        return 安全除法(d["纠纷数"].sum(), d["中标数"].sum())
    return 聚合(df, by, f)


def 首标时效(df):
    """发单→首次有人接标 的平均时长（小时）。"""
    列存在(df, "发单时间", "首标时间")
    return (pd.to_datetime(df["首标时间"]) - pd.to_datetime(df["发单时间"])).dt.total_seconds().mean() / 3600


def 定标时效(df):
    """发单→确定接单方 的平均时长（小时）。"""
    列存在(df, "发单时间", "定标时间")
    return (pd.to_datetime(df["定标时间"]) - pd.to_datetime(df["发单时间"])).dt.total_seconds().mean() / 3600


def 等待时长(df):
    """发单→实际接单 的平均等待时长（小时）。"""
    列存在(df, "发单时间", "接单时间")
    return (pd.to_datetime(df["接单时间"]) - pd.to_datetime(df["发单时间"])).dt.total_seconds().mean() / 3600
