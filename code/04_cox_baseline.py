"""Day 15：临床变量 Cox 基线模型（只用 age/Gender/Histology/Stage，不碰影像）

输入：results/tables/cohort.csv
输出：results/tables/cox_baseline.csv   # beta、HR、95% CI、p
      results/tables/cox_ph_test.csv   # Schoenfeld 残差 PH 检验
"""

import pandas as pd
from lifelines import CoxPHFitter
from lifelines.statistics import proportional_hazard_test

df = pd.read_csv("results/tables/cohort.csv")
print(f"cohort: {len(df)} 例")

# ---------- 1. 生存结局 ----------
df["T"] = df["Survival.time"].astype(float)
df["event"] = df["deadstatus.event"].astype(int)

# ---------- 2. 临床协变量编码 ----------
df["gender_num"] = (df["gender"] == "male").astype(int)

stage_map = {"I": 0, "II": 0, "IIIa": 1, "IIIb": 1}
df["stage_num"] = df["Overall.Stage"].map(stage_map)
unmapped = df.loc[df["stage_num"].isna() & df["Overall.Stage"].notna(),
                  "Overall.Stage"].unique()
assert len(unmapped) == 0, f"未映射的分期取值: {unmapped}"

hist_map = {
    "adenocarcinoma": "adeno",
    "squamous cell carcinoma": "squamous",
    "large cell": "large",
    "nos": "nos",
}
df["histology"] = df["Histology"].map(hist_map).fillna("unknown")

# ---------- 3. 缺失处理 ----------
print("\n建模变量缺失数：")
print(df[["T", "event", "age", "gender_num", "stage_num", "histology"]]
      .isna().sum())

d = df.dropna(subset=["T", "event", "age", "gender_num", "stage_num"]).copy()
print(f"\n分析集: n={len(d)}, events={int(d['event'].sum())}")

# ---------- 4. 设计矩阵 ----------
d = pd.get_dummies(d, columns=["histology"], prefix="hist", drop_first=True)
hist_cols = [c for c in d.columns if c.startswith("hist_")]
fit_cols = ["T", "event", "age", "gender_num", "stage_num"] + hist_cols
d = d[fit_cols].astype(float)

print(f"协变量: {fit_cols[2:]}")
print(f"参考组: female / 早期(I-II) / adenocarcinoma")

# ---------- 5. 拟合 Cox（小样本加轻惩罚） ----------
cph = CoxPHFitter(penalizer=0.1)
cph.fit(d, duration_col="T", event_col="event")
cph.print_summary(decimals=3)

# ---------- 6. 导出基线表 ----------
tab = cph.summary.copy()
tab.index.name = "variable"
tab = tab.reset_index().rename(columns={
    "coef": "beta",
    "exp(coef)": "HR",
    "exp(coef) lower 95%": "HR_lower95",
    "exp(coef) upper 95%": "HR_upper95",
})
tab = tab[["variable", "beta", "HR", "HR_lower95", "HR_upper95", "p"]]
tab.to_csv("results/tables/cox_baseline.csv", index=False)
print("\nCox 基线表：")
print(tab.round(4).to_string(index=False))

# 表观 C-index：训练集，仅作参考，正式性能留给 D18 的交叉验证
print(f"\napparent C-index = {cph.concordance_index_:.4f}")

# ---------- 7. PH 检验（用无惩罚副本，结论才可靠） ----------
cph_ph = CoxPHFitter()
cph_ph.fit(d, duration_col="T", event_col="event")

ph = proportional_hazard_test(cph_ph, d, time_transform="rank")
ph_tab = ph.summary.rename_axis("variable").reset_index()
ph_tab["violates_PH"] = ph_tab["p"] < 0.05
ph_tab.to_csv("results/tables/cox_ph_test.csv", index=False)
print("\nPH 检验（Schoenfeld, rank 时间变换）：")
print(ph_tab.round(4).to_string(index=False))

if ph_tab["violates_PH"].any():
    bad = ph_tab.loc[ph_tab["violates_PH"], "variable"].tolist()
    print(f"\n⚠ 违反 PH 的变量: {bad} → 分层 Cox / 时依项 / AFT")
else:
    print("\n✅ 未发现违反 PH 的证据（p ≥ 0.05，不等于证明成立）")

# 可选：画诊断图（IDE 里运行才看得见）
# cph_ph.check_assumptions(d, p_value_threshold=0.05, show_plots=True)

# ---------- 8. 敏感性分析：按 stage 分层 ----------
print("\n分层情况：")
print(d.groupby("stage_num")["event"].agg(["count", "sum"]))

cph_strat = CoxPHFitter(penalizer=0.1)
cph_strat.fit(d, duration_col="T", event_col="event",
              strata=["stage_num"])          # strata 列不进协变量
cph_strat.print_summary(decimals=3)

s2 = cph_strat.summary.copy()
s2.index.name = "variable"
s2 = s2.reset_index().rename(columns={
    "coef": "beta",
    "exp(coef)": "HR",
    "exp(coef) lower 95%": "HR_lower95",
    "exp(coef) upper 95%": "HR_upper95",
})
s2 = s2[["variable", "beta", "HR", "HR_lower95", "HR_upper95", "p"]]
s2.to_csv("results/tables/cox_baseline_stratified.csv", index=False)
print("\n分层 Cox（按 stage）：")
print(s2.round(4).to_string(index=False))
