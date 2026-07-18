"""按参照列填充 单元测试。"""
import contextlib
import io

import pandas as pd

from da.clean import 按参照列填充


def _base():
    return pd.DataFrame({
        "商品名称": ["A", "A", "B", "B", "C", "C"],
        "商品类型": ["电子", None, "食品", "食品", None, None],
    })


def test_基本映射填充():
    df = 按参照列填充(_base(), "商品类型", "商品名称", 静默=True)
    # A 组缺失填「电子」；B 组无缺失；C 组全空无法映射，保留空
    assert df.loc[1, "商品类型"] == "电子"
    assert pd.isna(df.loc[4, "商品类型"])
    assert pd.isna(df.loc[5, "商品类型"])
    # 原表未被改动
    assert pd.isna(_base().loc[1, "商品类型"])


def test_组内首个与最常见值():
    df = pd.DataFrame({
        "名称": ["X", "X", "X"],
        "类型": ["甲", "乙", "甲"],  # 最常见=甲，首个=甲
    })
    r1 = 按参照列填充(df, "类型", "名称", 方式="组内最常见值", 静默=True)
    r2 = 按参照列填充(df, "类型", "名称", 方式="组内首个", 静默=True)
    assert r1.equals(r2)


def test_歧义提示():
    df = pd.DataFrame({
        "名称": ["X", "X"],
        "类型": ["甲", "乙"],  # 同一名称对应两个不同值 → 歧义
    })
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        按参照列填充(df, "类型", "名称", 静默=False)
    out = buf.getvalue()
    assert "歧义" in out and "X" in out


def test_强制映射字典():
    df = pd.DataFrame({
        "名称": ["X", "X", "Y"],
        "类型": [None, "甲", None],
    })
    r = 按参照列填充(df, "类型", "名称", 映射={"X": "电子", "Y": "食品"}, 静默=True)
    assert r.loc[0, "类型"] == "电子"
    assert r.loc[2, "类型"] == "食品"
    assert r.loc[1, "类型"] == "甲"  # 原有值不被覆盖


def test_参考列空值保留空():
    df = pd.DataFrame({
        "名称": ["X", None, "Y"],
        "类型": [None, None, None],
    })
    r = 按参照列填充(df, "类型", "名称", 静默=True)
    assert pd.isna(r.loc[1, "类型"])  # 名称空 → 保留空
    assert pd.isna(r.loc[0, "类型"])  # X 组无已知类型 → 保留空


if __name__ == "__main__":
    test_基本映射填充()
    test_组内首个与最常见值()
    test_歧义提示()
    test_强制映射字典()
    test_参考列空值保留空()
    print("ALL_OK")
