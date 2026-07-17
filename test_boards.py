"""业务看板测试：6 个固化模板 + 自定义看板 + 缺列跳过 + 组合形态（plotly/pyecharts）。"""
import sys
import pandas as pd
import da
from da.charts.boards import _BOARD_REGISTRY

ok = 0
fail = 0


def check(名称, 条件):
    global ok, fail
    if 条件:
        ok += 1
        print(f"  ✅ {名称}")
    else:
        fail += 1
        print(f"  ❌ {名称}")


# 一份覆盖四域所需列的样例
df = pd.DataFrame({
    "地区": ["华东", "华北", "华南", "华东", "华北"],
    "销售额": [120, 90, 75, 60, 40],
    "月份": ["1月", "1月", "2月", "2月", "3月"],
    "品类": ["A", "B", "A", "C", "B"],
    "渠道来源": ["某宝", "某鱼", "朋友圈", "某宝", "某鱼"],
    "实收金额": [120, 90, 75, 60, 40],
    "净到手率": [0.6, 0.55, 0.62, 0.58, 0.5],
    "粉丝数": [1000, 1100, 1200, 1300, 1400],
    "互动率": [0.05, 0.06, 0.07, 0.08, 0.09],
    "内容类型": ["图文", "视频", "图文", "视频", "图文"],
    "阅读播放": [500, 800, 600, 900, 700],
    "中标率": [0.3, 0.4, 0.5, 0.35, 0.45],
    "日期": ["d1", "d2", "d3", "d4", "d5"],
    "首标时长h": [2, 3, 4, 2, 3],
})

print("== 1. 6 个固化模板存在 ==")
for 名称 in ["地区销售看板", "渠道对比看板", "收益趋势看板",
            "品类销售看板", "账号表现看板", "接单效率看板"]:
    check(f"模板 {名称} 已注册", 名称 in _BOARD_REGISTRY)

print("== 2. 默认(组合=False) 返回 dict ==")
for 名称 in ["地区销售看板", "渠道对比看板", "收益趋势看板",
            "品类销售看板", "账号表现看板", "接单效率看板"]:
    res = da.图表.看板(df, 名称=名称)
    check(f"{名称} 返回 dict 且至少1张图", isinstance(res, dict) and len(res) >= 1)

print("== 3. 组合=True plotly 返回单张图 ==")
r = da.图表.看板(df, 名称="地区销售看板", engine="plotly", 组合=True)
check("plotly 组合返回 Figure", type(r).__name__ == "Figure")

print("== 4. 组合=True pyecharts 返回 Page ==")
r = da.图表.看板(df, 名称="地区销售看板", engine="pyecharts", 组合=True)
check("pyecharts 组合返回 Page", type(r).__name__ == "Page")

print("== 5. 自定义看板 ==")
res = da.图表.自定义看板(df, 图表=[
    ("柱状图", "地区", "销售额"),
    ("饼图", "地区", "销售额"),
    ("折线图", "月份", "销售额"),
])
check("自定义看板 返回 dict 含3张图", isinstance(res, dict) and len(res) == 3)

print("== 6. 缺列跳过不崩 ==")
缺 = df.drop(columns=["地区", "销售额"])
res = da.图表.看板(缺, 名称="地区销售看板")
check("缺列时返回空 dict(不崩)", isinstance(res, dict))

print(f"\n看板测试：通过 {ok} / 失败 {fail}")
sys.exit(1 if fail else 0)
