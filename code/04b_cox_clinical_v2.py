"""Day 15 附加：临床 Cox v2 与交叉验证对比（探索性，不改 v1）

v1 = 04_cox_baseline.py 的 7 变量模型：
     age + gender + stage(二分) + histology
v2 = 扩展临床模型：
     age 限制性立方样条 + gender + T 分期(1-4) + N 分期(0-3)
     + stage 四水平(I/II/IIIa/IIIb) + histology

评估纪律：
- v1 与 v2 使用同一批病人、同一套 5-fold × 5 次重复划分；
- 只报告测试折 C-index，不用 apparent 值挑模型；
- 样条基函数在训练折内拟合，再应用到测试折（避免用测试集年龄分布定节点）；
- T=5、N=4 的含义在数据说明中已丢失，本脚本直接排除，不做臆测编码。

输入：results/tables/cohort.csv
输出：results/tables/cox_clinical_v2.csv          # v2 全量拟合的 HR 表
      results/tables/cox_clinical_v2_ph.csv       # v2 的 PH 检验
      results/tables/cox_cv_comparison.csv        # v1 vs v2 的 CV 汇总
      results/tables/cox_cv_folds.csv             # 每一折的分数（审计用）
"""

import numpy as np
import pandas as pd
import patsy
from lifelines import CoxPHFitter
from lifelines.statistics import proportional_hazard_test
from lifelines.utils import concordance_index
from sklearn.model_selection import StratifiedKFold

RANDOM_SEEDS = range(5)          # 5 次重复
N_SPLITS = 5                     # 每重复 5 折
PENALIZER = 0.1

df = pd.read_csv("results/tables/cohort.csv")
print(f"cohort: {len(df)} 例")

# ---------- 1. 结局与变量 ----------
df["T"] = df["Survival.time"].astype(float)
df["event"] = df["deadstatus.event"].astype(int)
df["gender_num"] = (df["gender"] == "male").astype(int)

df["stage_bin"] = df["Overall.Stage"].map(
    {"I": 0, "II": 0, "IIIa": 1, "IIIb": 1})

# T/N 只保留含义明确的编码；5 与 4 的含义已丢失，后续按缺失排除
df["t_ord"] = df["clinical.T.Stage"].where(
    df["clinical.T.Stage"].isin([1, 2, 3, 4]))
df["n_ord"] = df["Clinical.N.Stage"].where(
    df["Clinical.N.Stage"].isin([0, 1, 2, 3]))

hist_map = {
    "adenocarcinoma": "adeno",
    "squamous cell carcinoma": "squamous",
    "large cell": "large",
    "nos": "nos",
}
df["histology"] = df["Histology"].map(hist_map).fillna("unknown")
df["stage4"] = df["Overall.Stage"]

# ---------- 2. 共同分析集（v1/v2 必须同集比较） ----------
need = ["T", "event", "age", "gender_num", "stage_bin", "stage4",
        "histology", "t_ord", "n_ord"]
print("\n共同分析集的变量缺失数：")
print(df[need].isna().sum())

d = df.dropna(subset=need).copy()
print(f"\n共同分析集: n={len(d)}, events={int(d['event'].sum())}")
print(f"排除: age 缺失 22、stage 缺失 1、T 缺失/含义丢失、N=4（含义丢失）")

# 哑变量：histology 参考腺癌；stage4 参考 I 期
d = pd.get_dummies(d, columns=["histology", "stage4"], drop_first=True)

HIST_COLS = [c for c in d.columns if c.startswith("hist_")]
STAGE4_COLS = [c for c in d.columns if c.startswith("stage4_")]

V1_COLS = ["age", "gender_num", "stage_bin"] + HIST_COLS
V2_STATIC_COLS = ["gender_num", "t_ord", "n_ord"] + STAGE4_COLS + HIST_COLS

print(f"\nv1 协变量: {V1_COLS}")
print(f"v2 静态协变量: {V2_STATIC_COLS}")
print("v2 另加 4 个 age 样条项；参考组: female / I 期 / 腺癌；T、N 按有序数值")

# 显式给出年龄边界，保证测试折的年龄落在边界节点内；
# 边界只用到年龄范围，不使用结局信息。
AGE_MIN = float(d["age"].min())
AGE_MAX = float(d["age"].max())


def make_spline(train, test):
    """在训练折上确定样条节点，再应用到测试折，避免信息泄漏。"""
    formula = (
        "0 + bs(age, df=4, degree=3, include_intercept=False, "
        f"lower_bound={AGE_MIN}, upper_bound={AGE_MAX})"
    )
    tr = patsy.dmatrix(formula, train, return_type="dataframe")
    design_info = tr.design_info
    te = patsy.build_design_matrices([design_info], test)[0]

    cols = [f"age_s{i}" for i in range(tr.shape[1])]
    tr = pd.DataFrame(np.asarray(tr), index=train.index, columns=cols)
    te = pd.DataFrame(np.asarray(te), index=test.index, columns=cols)
    return tr, te


def fit_predict(train, test, cols, use_spline):
    if use_spline:
        tr_s, te_s = make_spline(train, test)
        Xtr = pd.concat([train[cols].astype(float), tr_s], axis=1)
        Xte = pd.concat([test[cols].astype(float), te_s], axis=1)
    else:
        Xtr = train[cols].astype(float)
        Xte = test[cols].astype(float)

    fit_df = pd.concat([train[["T", "event"]], Xtr], axis=1)
    cph = CoxPHFitter(penalizer=PENALIZER)
    cph.fit(fit_df, duration_col="T", event_col="event")

    risk = cph.predict_partial_hazard(Xte)
    # lifelines 的 concordance_index 约定：分数越大 = 生存时间越长，
    # 所以要把“风险”取负；等价于 cph.concordance_index_ 的内部约定。
    return concordance_index(test["T"], -risk, test["event"])


def run_cv(cols, use_spline):
    scores, rows = [], []
    for rep in RANDOM_SEEDS:
        skf = StratifiedKFold(n_splits=N_SPLITS, shuffle=True,
                              random_state=rep)
        for fold, (tr_idx, te_idx) in enumerate(skf.split(d, d["event"])):
            train = d.iloc[tr_idx]
            test = d.iloc[te_idx]
            score = fit_predict(train, test, cols, use_spline)
            scores.append(score)
            rows.append({"repeat": rep, "fold": fold, "c_index": score})
    return np.asarray(scores), pd.DataFrame(rows)


print("\n交叉验证中（5-fold × 5 次重复）...")
v1_scores, v1_rows = run_cv(V1_COLS, use_spline=False)
v2_scores, v2_rows = run_cv(V2_STATIC_COLS, use_spline=True)

diff = v2_scores - v1_scores
print("\nCV C-index（测试折）：")
print(f"v1: {v1_scores.mean():.4f} ± {v1_scores.std(ddof=1):.4f} "
      f"(n={len(v1_scores)} 折)")
print(f"v2: {v2_scores.mean():.4f} ± {v2_scores.std(ddof=1):.4f} "
      f"(n={len(v2_scores)} 折)")
print(f"配对差 v2-v1: {diff.mean():+.4f} ± {diff.std(ddof=1):.4f}；"
      f"v2 更好的折占比: {(diff > 0).mean():.0%}")

summary = pd.DataFrame([
    {"model": "v1_clinical", "n": len(d), "events": int(d["event"].sum()),
     "cv_mean": v1_scores.mean(), "cv_sd": v1_scores.std(ddof=1)},
    {"model": "v2_clinical_extended", "n": len(d),
     "events": int(d["event"].sum()),
     "cv_mean": v2_scores.mean(), "cv_sd": v2_scores.std(ddof=1)},
])
summary.to_csv("results/tables/cox_cv_comparison.csv", index=False)

folds = v1_rows.rename(columns={"c_index": "v1"}).copy()
folds["v2"] = v2_rows["c_index"]
folds["diff"] = folds["v2"] - folds["v1"]
folds.to_csv("results/tables/cox_cv_folds.csv", index=False)

# ---------- 3. v2 全量拟合（仅用于描述 HR + PH 检验） ----------
tr_s, _ = make_spline(d, d)
X_full = pd.concat([d[V2_STATIC_COLS].astype(float), tr_s], axis=1)
fit_full = pd.concat([d[["T", "event"]], X_full], axis=1)

cph_v2 = CoxPHFitter(penalizer=PENALIZER)
cph_v2.fit(fit_full, duration_col="T", event_col="event")
cph_v2.print_summary(decimals=3)

tab = cph_v2.summary.copy()
tab.index.name = "variable"
tab = tab.reset_index().rename(columns={
    "coef": "beta",
    "exp(coef)": "HR",
    "exp(coef) lower 95%": "HR_lower95",
    "exp(coef) upper 95%": "HR_upper95",
})
tab = tab[["variable", "beta", "HR", "HR_lower95", "HR_upper95", "p"]]
tab.to_csv("results/tables/cox_clinical_v2.csv", index=False)
print("\nv2 全量拟合 HR 表（apparent，仅描述）：")
print(tab.round(4).to_string(index=False))
print(f"v2 apparent C-index = {cph_v2.concordance_index_:.4f}（不可用于选模型）")

# ---------- 4. v2 的 PH 检验（无惩罚副本） ----------
cph_v2_ph = CoxPHFitter()
cph_v2_ph.fit(fit_full, duration_col="T", event_col="event")
ph = proportional_hazard_test(cph_v2_ph, fit_full, time_transform="rank")
ph_tab = ph.summary.rename_axis("variable").reset_index()
ph_tab["violates_PH"] = ph_tab["p"] < 0.05
ph_tab.to_csv("results/tables/cox_clinical_v2_ph.csv", index=False)

print("\nv2 PH 检验（Schoenfeld, rank）：")
print(ph_tab.round(4).to_string(index=False))
if ph_tab["violates_PH"].any():
    bad = ph_tab.loc[ph_tab["violates_PH"], "variable"].tolist()
    print(f"\n⚠ 违反 PH 的变量: {bad} → 分层 / 时依项 / AFT")
else:
    print("\n✅ 未发现违反 PH 的证据（p ≥ 0.05 不等于证明成立）")
