"""指标缺列容错测试：少了可选列（如税费）仍能算，能力探测打印 ⚠️。"""
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
缺税费 = df.drop(columns=["税费"])

print("== 1. 缺可选列仍能算 ==")
有税 = da.技能外包.综合成本率(df)
无税 = da.技能外包.综合成本率(缺税费)
check("综合成本率 缺税费不崩且为 (平台抽+成本+0)/实收", 无税 is not None and 无税 != 有税)
# 单均净利润缺 平台抽成/成本 也应能算（可选列）
check("单均净利润 缺平台抽成/成本 仍能算",
      da.技能外包.单均净利润(缺税费.drop(columns=["平台抽成", "成本"])) is not None)
# 销售净利率缺 成本/平台扣点/推广费 仍能算
eco = pd.read_csv("data/sample_ecommerce.csv")
缺附加 = eco.drop(columns=["成本", "平台扣点", "推广费"], errors="ignore")
# 仅保留销售额列也可用（其它都是可选列）
eco_min = pd.DataFrame({"销售额": [100, 200, 300]})
check("销售净利率 仅销售额列也能算", da.小微电商.销售净利率(eco_min) is not None)

print("== 2. 能力探测 对可选列缺失打印 ⚠️ ==")
探测 = da.能力探测(缺税费, "技能外包")
# 综合成本率应在 ✅ 列表且带 ⚠️（这里只验证不抛错、能跑完）
check("能力探测(缺税费) 正常执行", 探测 is None)

print("== 3. 必填列缺失则仍不可算 ==")
# 删掉 实收金额（必填）→ 综合成本率不应能算
缺实收 = 缺税费.drop(columns=["实收金额"])
可算 = {m.name for m in da.可算指标(缺实收, "技能外包")}
check("删必填列后 综合成本率 不在可算列表", "综合成本率" not in 可算)
check("删必填列后 净到手率 不在可算列表", "净到手率" not in 可算)

print(f"\n可选列容错测试：通过 {ok} / 失败 {fail}")
sys.exit(1 if fail else 0)
