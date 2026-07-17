"""域D 零工平台视角。"""
from .fields import 零工平台字段, 英文名映射, 规范列名
from .matching import 中标率, 纠纷率, 首标时效, 定标时效, 等待时长
from .multi import 综合履约分, 复购加权中标率, 任务接标时效
from .deliverables import 评价分布
from . import _自定义  # noqa: F401  自定义指标（da.更新.加指标 写入）

__all__ = [
    "零工平台字段", "英文名映射", "规范列名",
    "中标率", "纠纷率", "首标时效", "定标时效", "等待时长",
    "综合履约分", "复购加权中标率", "任务接标时效",
    "评价分布",
]
