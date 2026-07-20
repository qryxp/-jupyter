import sys, traceback
sys.path.insert(0, r"E:\接单库")
ok = 0; tot = 0
def check(name, cond):
    global ok, tot; tot += 1
    print(("✅ " if cond else "❌ ") + name); ok += 1 if cond else 0

try:
    import da, pandas as pd
    df = pd.read_csv(r"E:\接单库\data\sample_skills.csv")

    # 饼图 y=None 三引擎都能跑
    for eng in ["plotly", "seaborn", "pyecharts"]:
        fig = da.图表.画(df, 类型="饼图", x="渠道来源", 预设="活力橙", engine=eng)
        check(f"饼图 y=None 引擎={eng} 可跑", fig is not None)

    # 环形图 y=None
    for eng in ["plotly", "seaborn", "pyecharts"]:
        fig = da.图表.画(df, 类型="环形图", x="渠道来源", engine=eng)
        check(f"环形图 y=None 引擎={eng} 可跑", fig is not None)

    # y 传值时仍正常（回归）
    fig = da.图表.画(df, 类型="饼图", x="渠道来源", y="实收金额", 预设="商务蓝")
    check("饼图 带y 可跑", fig is not None)

    print(f"\n{tot} 项断言, 通过 {ok}")
    print("ALL_OK" if ok == tot else "HAS_FAIL")
except Exception:
    traceback.print_exc()
    print("TEST_FAIL")
