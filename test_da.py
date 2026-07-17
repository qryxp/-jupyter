import da
import pandas as pd

print("== 清洗 ==")
原始 = pd.read_csv("data/sample_skills.csv")
干净 = da.数据清洗.清洗管道(原始)
print("日期 dtype:", 干净["日期"].dtype, "| 评价分:", list(干净["评价分"]))

df = 干净
print("\n== 域A 技能外包 ==")
print("净到手率", round(da.技能外包.净到手率(df), 4))
print("客单价", round(da.技能外包.客单价(df), 2))
print("时薪", round(da.技能外包.时薪(df), 2))
print("返工率", round(da.技能外包.返工率(df), 4))
print("毛利率", round(da.技能外包.毛利率(df), 4))
print("单渠道转化率\n", da.技能外包.单渠道转化率(df))
print("老客复购率", round(da.技能外包.老客复购率(df), 4))
print("净到手率 by 渠道\n", da.技能外包.净到手率(df, by="渠道来源"))

print("\n== 域B 小微电商 ==")
ec = pd.read_csv("data/sample_ecommerce.csv")
print("销售额", da.小微电商.销售额(ec))
print("净销售额", da.小微电商.净销售额(ec))
print("客单价ATV", round(da.小微电商.客单价ATV(ec), 2))
print("销售毛利率", round(da.小微电商.销售毛利率(ec), 4))
print("整体转化率", round(da.小微电商.整体转化率(ec), 4))
print("动销率", round(da.小微电商.动销率(ec), 4))

print("\n== 域C 自媒体 ==")
md = pd.read_csv("data/sample_media.csv")
print("互动率", round(da.自媒体.互动率(md), 4))
print("粉丝净值", round(da.自媒体.粉丝净值(md), 4))
print("商单承接率", round(da.自媒体.商单承接率(md), 4))
print("账号估值", da.自媒体.账号估值模型(md))

print("\n== 域D 零工平台 ==")
gg = pd.read_csv("data/sample_gig.csv")
print("中标率", round(da.零工平台.中标率(gg), 4))
print("纠纷率", round(da.零工平台.纠纷率(gg), 4))
print("首标时效(h)", round(da.零工平台.首标时效(gg), 2))
print("评价分布\n", da.零工平台.评价分布(gg))

print("\n== 可交付项目 ==")
print(da.技能外包.收益复盘表(df))
print(da.技能外包.渠道ROI对比(df))
print(da.技能外包.报价模拟器(需求复杂度="高", 预计时长h=12, 目标时薪=90))
print(da.小微电商.爆款滞销分层(ec))
print(da.小微电商.利润敏感度分析(ec, 涨价=1))
print(da.自媒体.内容类型AB对比(md))

print("\n== 清单(域A) ==")
da.list_metrics("技能外包")

print("\n== 配方 ==")
da.show_recipe(da.技能外包.净到手率)

print("\nALL_OK")
