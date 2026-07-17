"""命令自更新测试：da.更新.加指标 / 加看板 写文件 + 热加载后立即可用。"""
import sys
import pandas as pd
import da

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


df = pd.read_csv("data/sample_skills.csv")

print("== 1. 加指标 → 重载 → 可调用 ==")
da.更新.加指标(
    "技能外包", "私单净收率",
    ["实收金额", "平台抽成", "税费"],
    "私单净收率 = (实收金额 − 平台抽成 − 税费) / 实收金额",
    可选列=["税费"],
    计算体='return 安全除法(d["实收金额"].sum() - d["平台抽成"].sum() - d["税费"].sum(), d["实收金额"].sum())',
)
check("da.技能外包.私单净收率 存在且可算",
      hasattr(da.技能外包, "私单净收率")
      and da.技能外包.私单净收率(df) is not None)
check("已进 能力探测 可算列表",
      "私单净收率" in {m.name for m in da.可算指标(df, "技能外包")})

print("== 2. 加看板 → 重载 → 可调用 ==")
da.更新.加看板(
    "我的测试看板",
    [{"标题": "各地区销售额", "类型": "柱状图", "x": "地区", "y": "销售额", "kw": {}},
     {"标题": "各月趋势", "类型": "折线图", "x": "月份", "y": "销售额", "kw": {}}],
    列=["地区", "销售额", "月份"],
    说明="测试看板",
)
check("da.图表.看板 能调自定义看板",
      isinstance(da.图表.看板(df, 名称="我的测试看板"), dict))

print(f"\n命令自更新测试：通过 {ok} / 失败 {fail}")
sys.exit(1 if fail else 0)
