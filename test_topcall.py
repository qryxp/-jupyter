import numbers
import pandas as pd
import da

ok = 0
def check(label, cond):
    global ok
    if cond:
        ok += 1
        print(f"  ✅ {label}")
    else:
        print(f"  ❌ {label}")

# 1) 顶层直呼 == 域级调用
df_s = pd.read_csv(r"E:\接单库\data\sample_skills.csv")
top = da.净到手率(df_s)
dom = da.技能外包.净到手率(df_s)
check("da.净到手率(df) 存在且可调用", callable(da.净到手率))
check("顶层结果 == da.技能外包.净到手率(df)", top == dom)
check("带分组也通：da.净到手率(df, by='渠道来源')", da.净到手率(df_s, by="渠道来源").notna().any())

# 2) 跨域顶层直呼
df_e = pd.read_csv(r"E:\接单库\data\sample_ecommerce.csv")
df_m = pd.read_csv(r"E:\接单库\data\sample_media.csv")
df_g = pd.read_csv(r"E:\接单库\data\sample_gig.csv")
check("da.销售额(df) 小微电商", isinstance(da.销售额(df_e), numbers.Number))
check("da.互动率(df) 自媒体", isinstance(da.互动率(df_m), (int, float)))
check("da.中标率(df) 零工平台", isinstance(da.中标率(df_g), (int, float)))

# 3) 未知名报错友好（AttributeError，非其它异常）
try:
    da.这个指标不存在(df_s)
    check("未知指标应抛 AttributeError", False)
except AttributeError as e:
    msg = str(e)
    check("未知指标抛 AttributeError 且给提示", ("da.list_metrics" in msg) and ("da.能力探测" in msg))
except Exception as e:
    check(f"未知指标抛错类型正确(实际={type(e).__name__})", False)

# 4) 自动补全：dir(da) 含指标名
names = dir(da)
check("'净到手率' 出现在 dir(da)", "净到手率" in names)
check("'销售额' 出现在 dir(da)", "销售额" in names)

# 5) 看配方（show_recipe 是打印型，捕获 stdout 验证）
import io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    da.show_recipe(da.净到手率)
recipe = buf.getvalue()
check("da.show_recipe(da.净到手率) 打印出配方源码", isinstance(recipe, str) and "净到手率" in recipe and "def" in recipe)

# 6) 既有 能力探测 / 一键计算 不受影响
det = da.能力探测(df_s)
check("da.能力探测 仍正常", det is None)
res = da.一键计算(df_s)
check("da.一键计算 含 '净到手率' 键", "净到手率" in res)

print(f"\n结果：{ok}/12 通过")
assert ok == 12, "有失败项"
print("ALL_OK")
