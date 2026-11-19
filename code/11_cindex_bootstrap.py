"""11_cindex_bootstrap.py
患者层面 bootstrap：给 5×10 折外预测的 C-index 提供 95% CI，
并检查下限是否 > 0.5（§6.6-4）。

方法：病人层面有放回重采样（B 次），同一组重采样用于所有 model/repeat；
每个 model 取 10 个 repeat 的 C-index 均值作为一个 bootstrap 复制。
"""
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sksurv.metrics import concordance_index_censored

ROOT = Path("/home/jiaqiwang/nsclc-cox")
IN = ROOT / "results/tables/oof_predictions.csv"
OUT = ROOT / "results/repro/cindex_bootstrap.csv"
MODELS = ["clinical", "signature", "lasso", "combined"]
B, SEED = 2000, 42

oof = pd.read_csv(IN)
rng = np.random.default_rng(SEED)

wide = {m: {r: g.set_index("PatientID")
            for r, g in oof[oof.model == m].groupby("repeat")}
        for m in MODELS}
ids = sorted(oof.PatientID.unique())


def ci(g):
    return concordance_index_censored(g.event.astype(bool), g.time, g.risk)[0]


obs = {m: float(np.mean([ci(g) for g in wide[m].values()]))
       for m in MODELS}
print("observed pooled OOF C-index:", obs, flush=True)

boot = {m: [] for m in MODELS}
t0 = time.time()
for b in range(B):
    samp = rng.choice(ids, size=len(ids), replace=True)
    for m in MODELS:
        boot[m].append(np.mean([ci(g.loc[samp]) for g in wide[m].values()]))
    if (b + 1) % 100 == 0:
        print(f"{b + 1}/{B}  {time.time() - t0:.1f}s", flush=True)

rows = []
for m in MODELS:
    arr = np.array(boot[m])
    lo, hi = np.percentile(arr, [2.5, 97.5])
    rows.append({"model": m, "cindex_obs": obs[m],
                 "ci_lower": lo, "ci_upper": hi,
                 "excludes_0.5": bool(lo > 0.5)})

res = pd.DataFrame(rows)
res.to_csv(OUT, index=False)
print(res.to_string(index=False))
