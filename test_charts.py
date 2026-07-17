"""图表模块自测：三引擎跑通全部图表，校验返回对象类型与入口函数。"""
import warnings
warnings.filterwarnings("ignore")

import da
import pandas as pd
C = da.图表
import matplotlib

matplotlib.use("Agg")  # 无界面环境也能跑 seaborn 分支

df = pd.read_csv("data/sample_region_sales.csv")

ok = 0
fail = 0


def 检查(名称, 图):
    global ok, fail
    try:
        mod = type(图).__module__
        if "plotly" in mod:
            assert hasattr(图, "to_plotly_json")
        elif "pyecharts" in mod:
            assert hasattr(图, "render")
        else:  # matplotlib / seaborn → Axes
            from matplotlib.axes import Axes
            assert isinstance(图, Axes)
        print(f"  ✅ {名称}  [{mod.split('.')[0]}]")
        ok += 1
    except Exception as e:
        print(f"  ❌ {名称}: {e!r}")
        fail += 1


print("== 柱状图 / 堆叠 / 折线 / 面积 / 饼 / 环形 ==")
检查("柱状图-plotly", C.柱状图(df, x="地区", y="销售额", engine="plotly"))
检查("柱状图-seaborn", C.柱状图(df, x="地区", y="销售额", engine="seaborn"))
检查("柱状图-pyecharts", C.柱状图(df, x="地区", y="销售额", engine="pyecharts"))
检查("堆叠柱-plotly", C.堆叠柱状图(df, x="地区", y="销售额", stack="品类", engine="plotly"))
检查("堆叠柱-seaborn", C.堆叠柱状图(df, x="地区", y="销售额", stack="品类", engine="seaborn"))
检查("堆叠柱-pyecharts", C.堆叠柱状图(df, x="地区", y="销售额", stack="品类", engine="pyecharts"))
检查("折线-plotly", C.折线图(df, x="月份", y="销售额", color="地区", engine="plotly"))
检查("折线-pyecharts", C.折线图(df, x="月份", y="销售额", color="地区", engine="pyecharts"))
检查("面积-plotly", C.面积图(df, x="月份", y="销售额", color="地区", engine="plotly"))
检查("饼-pyecharts", C.饼图(df, x="地区", y="销售额", engine="pyecharts"))
检查("环形-plotly", C.环形图(df, x="地区", y="销售额", engine="plotly"))

print("== 散点 / 气泡 / 热力 / 箱线 / 直方 ==")
检查("散点-plotly", C.散点图(df, x="销量", y="销售额", engine="plotly"))
检查("气泡-plotly", C.气泡图(df, x="销量", y="销售额", size="销售额", engine="plotly"))
检查("热力-plotly", C.热力图(df, x="月份", y="地区", z="销售额", engine="plotly"))
检查("热力-pyecharts", C.热力图(df, x="月份", y="地区", z="销售额", engine="pyecharts"))
检查("箱线-plotly", C.箱线图(df, x="地区", y="销售额", engine="plotly"))
检查("箱线-pyecharts", C.箱线图(df, x="地区", y="销售额", engine="pyecharts"))
检查("直方-seaborn", C.直方图(df, x="销售额", engine="seaborn"))

# 直方图在 pyecharts 应明确不支持
try:
    C.直方图(df, x="销售额", engine="pyecharts")
    print("  ❌ 直方图-pyecharts 应抛 NotImplementedError")
    fail += 1
except NotImplementedError:
    print("  ✅ 直方图-pyecharts 正确拒绝（NotImplementedError）")
    ok += 1

print("== 预设 / 统一入口 画 ==")
# 统一入口 + 预设
检查("画-柱状图(商务蓝)", C.画(df, 类型="柱状图", x="地区", y="销售额", 预设="商务蓝"))
检查("画-堆叠(活力橙)", C.画(df, 类型="堆叠柱状图", x="地区", y="销售额", stack="品类", 预设="活力橙"))
检查("画-折线(seaborn暗夜)", C.画(df, 类型="折线图", x="月份", y="销售额", color="地区",
                              engine="seaborn", 预设="暗夜"))
# 遍历所有预设，确保每种都不崩
for _名 in C.预设库:
    检查(f"柱状图-预设[{_名}]", C.柱状图(df, x="地区", y="销售额", engine="plotly", 预设=_名))
# 全局设定后省略 engine/预设
C.设定(默认引擎="plotly", 默认预设="清爽白")
检查("画-默认设定", C.画(df, 类型="饼图", x="地区", y="销售额"))
C.预设示例()

print("== 入口：查看配方 / 清单 ==")
try:
    C.查看配方(C.柱状图)
    da.show_recipe(C.折线图)
    C.图表清单()
    print("  ✅ 查看配方 / show_recipe / 图表清单 正常")
    ok += 1
except Exception as e:
    print(f"  ❌ 入口函数异常: {e!r}")
    fail += 1

print(f"\n图表自测: 通过 {ok} / 失败 {fail}")
assert fail == 0, "存在失败项"
print("CHARTS_OK")
