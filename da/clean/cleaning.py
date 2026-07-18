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


def 按参照列填充(df, 目标列, 参考列, 方式="组内最常见值", 映射=None, 保留无法映射=True, 静默=False):
    """按参照列的取值，把目标列的空值「映射填充」。

    典型场景（你刚提的）：商品类型大量缺失，但商品名称几乎都有，
    且同一商品名称应当对应同一个商品类型 → 用「同名称下已有的类型」
    去填该名称下缺失的类型，而不是瞎填一个众数。

    参数
    ----
    df           : 原始 DataFrame（本函数不改原表，返回新表）
    目标列       : 要填充空值的列，如 "商品类型"
    参考列       : 用来分组的参照列，如 "商品名称"
    方式         : 当同一参考值对应多个非空目标值时怎么选——
                  "组内最常见值"（默认）：取该组出现最多的目标值
                  "组内首个"        ：取该组第一个非空目标值
    映射         : 可选的强制字典 {参考值: 目标值}，优先级最高，直接覆盖；
                  适合你已经有一份「名称→类型」对照表的情况
    保留无法映射 : 仅作语义提示——本函数拒绝无依据填充，参考列本身为空的
                  行一律保留空，绝不瞎猜
    静默         : True 时不打印歧义警告与填充统计

    返回
    ----
    填充后的新 DataFrame

    注意
    ----
    ⚠️ 歧义会被主动提示：如果某个商品名称对应了多个不同的商品类型
    （脏数据矛盾），函数会打印出来让你人工核对，而不是偷偷选一个。
    """
    df = df.copy()
    if 目标列 not in df.columns:
        raise KeyError(f"目标列不存在：{目标列!r}")
    if 参考列 not in df.columns:
        raise KeyError(f"参考列不存在：{参考列!r}")

    # 1) 用户给强制映射字典：直接按字典填（最高优先级）
    if 映射:
        miss = df[目标列].isna() & df[参考列].notna() & df[参考列].isin(映射)
        df.loc[miss, 目标列] = df.loc[miss, 参考列].map(映射)
        n = int(miss.sum())
        if not 静默:
            print(f"✅ 已用强制映射表填充 {n} 个「{目标列}」空值。")
        return df

    # 2) 由已知数据反推「参考值 → 目标值」映射表
    known = df[df[目标列].notna()]
    # 2a) 歧义检测：同一参考值对应多个不同目标值 → 提示人工核对
    if not 静默:
        amb = known.groupby(参考列)[目标列].nunique()
        amb = amb[amb > 1]
        if len(amb):
            print(f"⚠️ 发现歧义：以下 {len(amb)} 个「{参考列}」对应了多个不同的「{目标列}」，" +
                  f"已按「{方式}」自动选一个，请人工核对：")
            for k in amb.index:
                vals = known[known[参考列] == k][目标列].unique().tolist()
                print(f"   {参考列}={k!r}: {vals}")

    # 2b) 计算每组代表值
    if 方式 == "组内首个":
        rep = known.groupby(参考列)[目标列].first()
    else:  # 组内最常见值
        rep = known.groupby(参考列)[目标列].agg(lambda s: s.value_counts().idxmax())

    # 3) 只填「目标列空 + 参考列有值」的行；参考列空的行保留空
    need = df[目标列].isna() & df[参考列].notna()
    n_skip = int((df[目标列].isna() & df[参考列].isna()).sum())
    filled = df.loc[need, 参考列].map(rep)
    n_fill = int(filled.notna().sum())
    n_noref = int((filled.isna() & need).sum())
    df.loc[need, 目标列] = filled
    if not 静默:
        msg = f"✅ 已用「{参考列}」映射填充 {n_fill} 个「{目标列}」空值"
        extra = []
        if n_skip:
            extra.append(f"{n_skip} 行因「{参考列}」本身为空无法映射")
        if n_noref:
            extra.append(f"{n_noref} 行「{参考列}」有值但无已知「{目标列}」")
        msg += ("；" + "，".join(extra) + "，已保留空。") if extra else "。"
        print(msg)
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
