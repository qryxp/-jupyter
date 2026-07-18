"""异常值检测单元测试：合成数据精确断言 + 真实数据冒烟。"""
import pandas as pd
import numpy as np
import da

ok = True
def check(name, cond):
    global ok
    print(("✅" if cond else "❌"), name)
    ok = ok and cond

# ===== 受控合成数据：注入极端值，确保落在 IQR 区间外 =====
syn = pd.DataFrame({
    "月薪": [5000, 6000, 5500, 6500, 5800, 100000, -100000],
    "评分": [1, 2, 3, 4, 5, 100, -100],
})
# sigma 单独用：只注入一个高离群，避免对称极端把 std 撑爆
syn_sig = pd.DataFrame({
    "月薪": [5000, 6000, 5500, 6500, 5800, 5300, 6200, 50000],
})

# 1) iqr 法：月薪 2 个极端值都应被抓（区间约 [3750, 7750]）
out = da.数据清洗.异常值检测(syn, 数值列=["月薪"], 方法="iqr", 静默=True)
check("iqr 月薪抓到 2 个异常", int(out["异常_月薪"].sum()) == 2)
check("iqr 月薪 100000 被标记", bool(out.loc[5, "异常_月薪"]))
check("iqr 月薪 -100000 被标记", bool(out.loc[6, "异常_月薪"]))

# 2) 多列 + 返回明细（月薪/评分 异常都在同一两行 → 异常_任一=2 行，明细=4 格）
out, detail = da.数据清洗.异常值检测(
    syn, 数值列=["月薪", "评分"], 方法="iqr", 系数=1.5, 返回明细=True)
check("多列 月薪 2 异常", int(out["异常_月薪"].sum()) == 2)
check("多列 评分 2 异常", int(out["异常_评分"].sum()) == 2)
check("异常_任一 按行汇总 = 2 行", int(out["异常_任一"].sum()) == 2)
check("返回明细 4 格（2列×2行）", len(detail) == 4)
check("明细列名正确", list(detail.columns) == ["行号", "列名", "取值", "下界", "上界"])

# 3) 系数放宽：异常数不增
out3 = da.数据清洗.异常值检测(syn, 数值列=["月薪"], 方法="iqr", 系数=3, 静默=True)
check("系数=3 异常数 <= 系数=1.5", int(out3["异常_月薪"].sum()) <= 2)

# 4) sigma 法（大量正态 + 1 个离群，符合真实场景）：抓到离群且正态主体不误判
rng = np.random.default_rng(0)
base = rng.normal(5000, 300, 500)          # 500 个正常值
syn_sig = pd.DataFrame({"月薪": np.append(base, 50000)})  # + 1 个离群
out4 = da.数据清洗.异常值检测(syn_sig, 数值列=["月薪"], 方法="sigma", 静默=True)
check("sigma 法抓到离群 50000", bool(out4.loc[500, "异常_月薪"]))
check("sigma 法 500 个正态主体无被误判", int(out4.loc[:499, "异常_月薪"].sum()) == 0)

# 5) 不新增标记列：不加列、行数不变
out5 = da.数据清洗.异常值检测(syn, 数值列=["月薪"], 新增标记列=False, 静默=True)
check("新增标记列=False 不加列", "异常_月薪" not in out5.columns)
check("新增标记列=False 行数不变", len(out5) == len(syn))

# 6) 默认自动检测所有数值列
out6 = da.数据清洗.异常值检测(syn, 方法="iqr", 静默=True)
check("默认自动检测 月薪+评分 两列",
      ("异常_月薪" in out6.columns) and ("异常_评分" in out6.columns))

# ===== 真实数据冒烟：Case6 当前月薪原始无离群 =====
XL = r"C:\Users\admin\Desktop\新建文件夹 (2)\数据分析案例模拟数据.xlsx"
real = pd.read_excel(XL, sheet_name="Case6_薪酬绩效")
real_out = da.数据清洗.异常值检测(real, 数值列=["当前月薪"], 方法="iqr", 静默=True)
check("真实数据 当前月薪 原始无离群", int(real_out["异常_当前月薪"].sum()) == 0)
n_score = int(da.数据清洗.异常值检测(real, 数值列=["年度绩效评分"], 静默=True)["异常_年度绩效评分"].sum())
print(f"\n真实数据 年度绩效评分 iqr 离群数：{n_score}（数据本身分布，非 bug，正好说明不能无脑删）")

print("\n" + ("ALL_OK" if ok else "HAS_FAIL"))
assert ok
