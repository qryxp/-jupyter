"""库更新脚手架 🛠️ —— 不想记代码模板长啥样？命令直接吐可粘贴源码。

    da.脚手架.生成指标代码(域名, 名称, 字段, 公式, 可选列=[...])
    da.脚手架.生成看板代码(名称, 图表列表, 列=[...])

返回的就是一段带 @metric / @看板模板 的完整函数源码，粘到对应 _自定义.py 即可；
或直接用 da.更新.加指标 / da.更新.加看板 让它帮你写文件 + 热加载。
"""
from typing import List, Optional


def 生成指标代码(域名: str, 名称: str, 字段: List[str], 公式: str,
               类别: str = "自定义指标", 可选列: Optional[List[str]] = None,
               计算体: Optional[str] = None) -> str:
    """生成一段带 @metric 的指标函数源码（字符串）。

    参数
    ----
    域名    : 业务域中文名，如 "技能外包"
    名称    : 指标中文名（同时作为函数名）
    字段    : 依赖的原始字段列表（含可选列）
    公式    : 人类可读公式
    可选列  : 缺失时自动补 0 的列（附加成本/费用类）
    计算体  : f(d) 函数体的 Python 代码字符串；留空则给占位 TODO
    """
    opt = list(可选列 or [])
    opt_repr = "[" + ", ".join(f'"{c}"' for c in opt) + "]" if opt else "None"
    校验行 = "\n    ".join(f'列存在(df, "{c}")' for c in 字段)
    if 计算体:
        # 计算体是 f(d) 的函数体，需缩进到 def f(d): 内部（8 空格）
        body = "\n".join("        " + line for line in 计算体.strip().splitlines())
    else:
        body = f'        return d["{字段[0]}"].sum()   # TODO: 替换为真实计算公式'

    src = f'''@metric(name="{名称}", domain="{域名}", category="{类别}",
        fields={字段!r},
        formula="{公式}",
        可选列={opt_repr})
def {名称}(df, by=None):
    {校验行}
    def f(d):
{body}
    return 聚合(df, by, f)
'''
    print(src)
    return src


def 生成看板代码(名称: str, 图表列表: List[dict],
               列: Optional[List[str]] = None, 说明: str = "") -> str:
    """生成一段带 @看板模板 的看板函数源码（字符串）。

    图表列表 中每个元素形如：
        {"标题":"各地区销售额", "类型":"柱状图", "x":"地区", "y":"销售额", "kw":{}}
    """
    spec_lines = ",\n".join(
        '        {"标题": %r, "类型": %r, "x": %r, "y": %r, "kw": %r}'
        % (s["标题"], s["类型"], s["x"], s["y"], s.get("kw", {}))
        for s in 图表列表
    )
    cols_repr = 列 if 列 is not None else []
    src = f'''@看板模板(name="{名称}", 列={cols_repr!r}, 说明="{说明}")
def {名称}():
    return [
{spec_lines}
    ]
'''
    print(src)
    return src
