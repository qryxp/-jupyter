"""库命令自更新 🔧 —— 一行命令给库永久追加指标 / 看板，写文件 + 热加载。

    da.更新.加指标(域, 名称, 字段, 公式, 可选列=[...], 计算体="...")
    da.更新.加看板(名称, 图表列表, 列=[...], 说明="...")

写入位置（库启动时已被对应 __init__ 导入，所以重载后立即可用）：
    da/<域>/_自定义.py          ← 指标
    da/charts/_自定义看板.py     ← 看板

重载后无需重启 kernel，当前 Jupyter 会话里就能用：
    da.技能外包.你的指标(df)
    da.图表.看板(df, 名称="你的看板")

想看生成的源码长啥样、或手动粘到文件，用 da.脚手架.生成指标代码 / 生成看板代码。
"""
import importlib
from pathlib import Path
from typing import List, Optional

from .脚手架 import 生成指标代码, 生成看板代码

_域到模块 = {
    "技能外包": "skills",
    "小微电商": "ecommerce",
    "自媒体": "media",
    "零工平台": "gig",
}


def 加指标(域: str, 名称: str, 字段: List[str], 公式: str,
          类别: str = "自定义指标", 可选列: Optional[List[str]] = None,
          计算体: Optional[str] = None):
    """一行命令给库追加一个指标，写文件 + 热加载后立即可用。

    参数
    ----
    域      : "技能外包" / "小微电商" / "自媒体" / "零工平台"
    名称    : 指标中文名（同时是函数名、也是 da.能力探测 里显示的名字）
    字段    : 依赖的原始字段列表（含可选列）
    公式    : 人类可读公式
    可选列  : 缺失时自动补 0 的列（附加成本/费用类，如 税费/平台抽成/成本）
    计算体  : f(d) 函数体的 Python 代码（字符串）；留空则生成占位 TODO，你之后手动补

    示例
    ----
        da.更新.加指标(
            "技能外包", "私单净收率",
            ["实收金额", "平台抽成", "税费"],
            "私单净收率 = (实收金额 − 平台抽成 − 税费) / 实收金额",
            可选列=["税费"],
            计算体='return 安全除法(d["实收金额"].sum() - d["平台抽成"].sum() - d["税费"].sum(), d["实收金额"].sum())',
        )
        # 之后直接：
        da.技能外包.私单净收率(df)
    """
    英文名 = _域到模块.get(域)
    if 英文名 is None:
        raise ValueError(f"未知域 {域!r}，可选：{list(_域到模块)}")

    代码 = 生成指标代码(域, 名称, 字段, 公式, 类别=类别, 可选列=可选列, 计算体=计算体)
    文件 = Path(__file__).parent / 英文名 / "_自定义.py"
    if not 文件.exists():
        raise FileNotFoundError(f"找不到 {文件}，请确认域 {域} 正确")

    try:
        with open(文件, "a", encoding="utf-8") as f:
            f.write("\n\n" + 代码)
    except OSError as e:
        raise OSError(f"写入 {文件} 失败：{e}（检查文件权限）")

    # 热加载：重载 _自定义 子模块，让新 @metric 重新注册
    子模块 = importlib.import_module(f"da.{英文名}._自定义")
    importlib.reload(子模块)
    func = getattr(子模块, 名称, None)
    if func is None:
        raise RuntimeError(f"写入后未找到函数 {名称}，请检查生成代码是否有语法错误")

    # 暴露到域命名空间，方便 da.{域}.{名称} 直接调用
    domain_pkg = importlib.import_module(f"da.{英文名}")
    setattr(domain_pkg, 名称, func)
    print(f"✅ 已添加指标【{名称}】到域【{域}】，现在可用 da.{域}.{名称}(df) 调用")
    return func


def 加看板(名称: str, 图表列表: List[dict],
          列: Optional[List[str]] = None, 说明: str = ""):
    """一行命令给库追加一个看板模板，写文件 + 热加载后立即可用。

    图表列表 中每个元素形如：
        {"标题":"各地区销售额", "类型":"柱状图", "x":"地区", "y":"销售额", "kw":{}}

    示例
    ----
        da.更新.加看板(
            "我的看板",
            [{"标题":"各地区销售额","类型":"柱状图","x":"地区","y":"销售额","kw":{}},
             {"标题":"各月趋势","类型":"折线图","x":"月份","y":"销售额","kw":{}}],
            列=["地区","销售额","月份"],
            说明="自定义看板示例",
        )
        # 之后直接：
        da.图表.看板(df, 名称="我的看板")
    """
    代码 = 生成看板代码(名称, 图表列表, 列=列, 说明=说明)
    文件 = Path(__file__).parent / "charts" / "_自定义看板.py"
    if not 文件.exists():
        raise FileNotFoundError(f"找不到 {文件}")

    try:
        with open(文件, "a", encoding="utf-8") as f:
            f.write("\n\n" + 代码)
    except OSError as e:
        raise OSError(f"写入 {文件} 失败：{e}（检查文件权限）")

    子模块 = importlib.import_module("da.charts._自定义看板")
    importlib.reload(子模块)
    func = getattr(子模块, 名称, None)
    if func is None:
        raise RuntimeError(f"写入后未找到函数 {名称}，请检查生成代码是否有语法错误")

    charts_pkg = importlib.import_module("da.charts")
    setattr(charts_pkg, 名称, func)
    print(f"✅ 已添加看板【{名称}】，现在可用 da.图表.看板(df, 名称={名称!r}) 调用")
    return func
