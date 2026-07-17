"""域C 自媒体 · 互动与变现指标。"""
from .._registry import metric
from ..core.utils import 列存在, 聚合, 安全除法


@metric(name="互动率", domain="自媒体", category="互动指标",
        fields=["点赞", "收藏", "评论", "阅读播放"],
        formula="互动率 = (点赞 + 收藏 + 评论) / 阅读播放")
def 互动率(df, by=None):
    列存在(df, "点赞", "收藏", "评论", "阅读播放")

    def f(d):
        return 安全除法((d["点赞"] + d["收藏"] + d["评论"]).sum(), d["阅读播放"].sum())
    return 聚合(df, by, f)


@metric(name="千次曝光报价CPM", domain="自媒体", category="变现指标",
        fields=["商单收入", "阅读播放"],
        formula="CPM = 商单收入 / 阅读播放 × 1000")
def 千次曝光报价CPM(df, by=None):
    列存在(df, "商单收入", "阅读播放")

    def f(d):
        return 安全除法(d["商单收入"].sum(), d["阅读播放"].sum()) * 1000
    return 聚合(df, by, f)


@metric(name="粉丝净值", domain="自媒体", category="变现指标",
        fields=["商单收入", "粉丝数"],
        formula="粉丝净值 = 商单收入 / 粉丝数")
def 粉丝净值(df, by=None):
    列存在(df, "商单收入", "粉丝数")

    def f(d):
        return 安全除法(d["商单收入"].sum(), d["粉丝数"].sum())
    return 聚合(df, by, f)


@metric(name="商单承接率", domain="自媒体", category="变现指标",
        fields=["合作数", "询价"],
        formula="商单承接率 = 合作数 / 询价")
def 商单承接率(df, by=None):
    列存在(df, "合作数", "询价")

    def f(d):
        return 安全除法(d["合作数"].sum(), d["询价"].sum())
    return 聚合(df, by, f)
