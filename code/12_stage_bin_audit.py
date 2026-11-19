"""12_stage_bin_audit.py
临床模型 stage_bin 编码核对（day19 §7-1 / §8-2）。

检查：
1. stage_bin 与 Overall.Stage 的映射一致性；
2. 分期分布与事件率（对比论文 Lung1）；
3. stage_bin 单变量 log-rank / Cox；
4. 与 09 的多变量 clinical pooled HR 对照。
"""
from pathlib import Path

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from lifelines.statistics import logrank_test

ROOT = Path("/home/jiaqiwang/nsclc-cox")
OUT = ROOT / "results/repro/stage_bin_audit.csv"

df = pd.read_csv(ROOT / "results/tables/analysis_set.csv")
df["T"] = df["Survival.time"].astype(float)
df["event"] = df["deadstatus.event"].astype(int)

print(f"n = {len(df)}, events = {int(df.event.sum())}")

# 0) 映射一致性
nuniq = df.groupby("Overall.Stage")["stage_bin"].nunique()
assert (nuniq == 1).all(), "同一 Overall.Stage 对应多个 stage_bin"
mapping = df.groupby("Overall.Stage")["stage_bin"].first().to_dict()
print("\nstage_bin 映射:", mapping)
assert mapping == {"I": 0, "II": 0, "IIIa": 1, "IIIb": 1}, \
    f"stage_bin 映射不符预期: {mapping}"

# 1) 分期分布与事件率（399 例）
order = ["I", "II", "IIIa", "IIIb"]
paper_n = {"I": 93, "II": 40, "IIIa": 112, "IIIb": 176}
dist = (df.groupby("Overall.Stage")
          .agg(n=("PatientID", "size"), events=("event", "sum"))
          .reindex(order))
dist["event_rate"] = dist["events"] / dist["n"]
dist["pct"] = dist["n"] / len(df)
dist["paper_n"] = [paper_n[s] for s in order]
dist["paper_pct"] = dist["paper_n"] / sum(paper_n.values())
print("\n分期分布/事件率（399 例）:")
print(dist.to_string())

# 2) stage_bin 分布
sb = df.groupby("stage_bin").agg(n=("PatientID", "size"),
                                 events=("event", "sum"))
sb["event_rate"] = sb["events"] / sb["n"]
print("\nstage_bin 分布/事件率:")
print(sb.to_string())

# 3) log-rank
g0, g1 = df[df.stage_bin == 0], df[df.stage_bin == 1]
lr = logrank_test(g0["T"], g1["T"],
                  event_observed_A=g0.event, event_observed_B=g1.event)
print(f"\nlog-rank stage_bin: chi2={lr.test_statistic:.3f}, "
      f"p={lr.p_value:.4g}")

# 4) 单变量 Cox：stage_bin（0/1）与 stage 有序
for col, vals in [
    ("stage_bin", df["stage_bin"].astype(float)),
    ("stage_ord",
     df["Overall.Stage"].map({"I": 0, "II": 1, "IIIa": 2, "IIIb": 3}).astype(float)),
]:
    x = pd.DataFrame({col: vals, "T": df["T"], "event": df["event"]})
    s = CoxPHFitter().fit(x, "T", "event").summary.loc[col]
    print(f"单变量 Cox {col}: HR={np.exp(s['coef']):.3f} "
          f"[{np.exp(s['coef lower 95%']):.3f}-"
          f"{np.exp(s['coef upper 95%']):.3f}], p={s['p']:.4g}")

# 5) 多变量 clinical 模型的 pooled HR（来自 09）
cs = pd.read_csv(ROOT / "results/tables/coefficient_summary.csv")
row = cs[(cs.model == "clinical") & (cs.term == "stage_bin")].iloc[0]
print(f"\nclinical 多变量 pooled stage_bin: HR={row.hr_pooled:.3f} "
      f"[{row.hr_pooled_lo:.3f}-{row.hr_pooled_hi:.3f}] "
      f"(n_folds={int(row.n_folds)}, freq={row.freq:.2f})")

# 6) 分期 4 水平的 KM 中位生存 + 4 水平 Cox LRT
from lifelines import KaplanMeierFitter

print("\n各分期中位 OS（Kaplan–Meier）：")
km = KaplanMeierFitter()
for st in order:
    sub = df[df["Overall.Stage"] == st]
    km.fit(sub["T"], sub["event"])
    print(f"  {st:4s}: n={len(sub):3d}, median={km.median_survival_time_:.0f} 天")

d4 = df.copy()
for st in ["II", "IIIa", "IIIb"]:
    d4[f"stage_{st}"] = (d4["Overall.Stage"] == st).astype(float)
cols4 = ["stage_II", "stage_IIIa", "stage_IIIb"]
x4 = pd.concat([d4[cols4], d4[["T", "event"]]], axis=1)
cph4 = CoxPHFitter().fit(x4, "T", "event")
lrt = cph4.log_likelihood_ratio_test()
print(f"\n4 水平 Cox（参考 I 期）LRT: chi2={lrt.test_statistic:.3f}, "
      f"p={lrt.p_value:.4g}")

# 7)  sanity check：年龄/性别是否按常理方向
print("\n sanity check（年龄/性别，单变量 Cox）：")
for col, vals, name in [
    ("age_per10", df["age"].astype(float) / 10.0, "age per 10 years"),
    ("gender_num", df["gender_num"].astype(float), "male vs female"),
]:
    x = pd.DataFrame({col: vals, "T": df["T"], "event": df["event"]})
    s = CoxPHFitter().fit(x, "T", "event").summary.loc[col]
    print(f"  {name:18s}: HR={np.exp(s['coef']):.3f} "
          f"[{np.exp(s['coef lower 95%']):.3f}-"
          f"{np.exp(s['coef upper 95%']):.3f}], p={s['p']:.4g}")

# 8) 输出
out = dist.reset_index().rename(columns={"Overall.Stage": "stage"})
out.to_csv(OUT, index=False)
print(f"\nwrote {OUT}")
