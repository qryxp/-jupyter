"""数据清洗实现。

接单数据往往来自 Excel / 平台导出 / 手工台账，常见两大脏点：
1. 日期格式乱（2026-07-16、2026/7/16、16/07/2026、2026年7月16日、Excel 序列号…）
2. 空值表示乱（空串、"无"、"暂无"、"NULL"、"NA"、"-"、None…）

本模块统一处理这两类，并把清洗做成可复用的管道。
"""
import numpy as np
import pandas as pd

# 常见日期格式（按顺序逐个尝试，剩下的再交给 pandas 自动识别）
默认日期格式 = [
    "%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d",
    "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y", "%m-%d-%Y",
    "%Y年%m月%d日", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S",
]

# 各种"看起来像空"的写法 → 统一成 NaN
默认空值映射 = {
    "": np.nan, " ": np.nan, "  ": np.nan,
    "无": np.nan, "暂无": np.nan, "未知": np.nan, "待定": np.nan, "无数据": np.nan,
    "NULL": np.nan, "null": np.nan, "Null": np.nan,
    "NA": np.nan, "na": np.nan, "N/A": np.nan, "n/a": np.nan,
    "None": np.nan, "none": np.nan, "NaN": np.nan, "nan": np.nan,
    "-": np.nan, "—": np.nan, "--": np.nan, "/": np.nan, "无记录": np.nan,
}


def 强制日期转换(df, 列=None, 格式=None):
    """把指定列强制转成 datetime。

    参数
    ----
    df   : 原始 DataFrame
    列   : 列名或列名列表；默认自动识别含「日期/时间/date/time」的列
    格式 : 自定义格式列表；默认用 默认日期格式

    返回
    ----
    转换后的新 DataFrame（原表不变）。转换不了的变成 NaT，不报错。
    """
    df = df.copy()
    if 列 is None:
        列 = [c for c in df.columns if any(k in str(c) for k in ["日期", "时间", "date", "Date", "time", "Time", "结算"])]
    elif isinstance(列, str):
        列 = [列]
    if 格式 is None:
        格式 = 默认日期格式

    for col in 列:
        if col not in df.columns:
            continue
        s = df[col].astype(str).str.strip()
        out = pd.Series(pd.NaT, index=df.index)
        remaining = s.copy()
        for fmt in 格式:
            mask = out.isna() & remaining.notna() & (remaining.str.lower() != "nan")
            if not mask.any():
                continue
            parsed = pd.to_datetime(remaining.where(mask), format=fmt, errors="coerce")
            out = out.fillna(parsed)
            remaining = remaining.where(out.isna())
        # 兜底：让 pandas 自行猜测剩余部分
        mask = out.isna() & remaining.notna() & (remaining.str.lower() != "nan")
        if mask.any():
            parsed = pd.to_datetime(remaining.where(mask), errors="coerce")
            out = out.fillna(parsed)
        df[col] = out
    return df


def 空值映射填充(df, 映射=None, 填充=None, 数值列默认填充=0, 文本列默认填充=""):
    """把"伪空值"统一成 NaN，再按类型填充。

    参数
    ----
    映射             : 自定义「伪空值 → NaN」字典；默认用 默认空值映射
    填充             : 给一个标量（如 0 或 ""）统一填充所有空值
    数值列默认填充   : 不指定 填充 时，数值列填这个（默认 0）
    文本列默认填充   : 不指定 填充 时，文本列填这个（默认 ""）
    """
    df = df.copy()
    if 映射 is None:
        映射 = 默认空值映射
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].replace(映射)
    if 填充 is not None:
        df = df.fillna(填充)
    else:
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(数值列默认填充)
            else:
                df[col] = df[col].fillna(文本列默认填充)
    return df


def 清洗管道(df, 日期列=None, 日期格式=None, 空值映射=None, 去重=True, 去空格=True):
    """一键清洗：去空格 → 日期转换 → 空值填充 → 去重。

    顺序很重要：先去空格，映射才能命中；先转日期，再填充才安全。
    """
    df = df.copy()
    if 去空格:
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].replace({"nan": np.nan, "None": np.nan, "NaT": np.nan})
    df = 强制日期转换(df, 列=日期列, 格式=日期格式)
    df = 空值映射填充(df, 映射=空值映射)
    if 去重:
        df = df.drop_duplicates().reset_index(drop=True)
    return df
