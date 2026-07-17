"""域C 自媒体/内容接单。"""
from .fields import 自媒体字段, 英文名映射, 规范列名
from .engagement import 互动率, 千次曝光报价CPM, 粉丝净值, 商单承接率
from .multi import 内容投产比, 掉粉率, 千粉月收益
from .deliverables import 账号估值模型, 内容类型AB对比
from . import _自定义  # noqa: F401  自定义指标（da.更新.加指标 写入）

__all__ = [
    "自媒体字段", "英文名映射", "规范列名",
    "互动率", "千次曝光报价CPM", "粉丝净值", "商单承接率",
    "内容投产比", "掉粉率", "千粉月收益",
    "账号估值模型", "内容类型AB对比",
]
