"""全量 422 例 Energy 量纲核对：HU 口径 vs 存储像素值口径。"""
from pathlib import Path

import pandas as pd
import pydicom

ROOT = Path("/home/jiaqiwang/nsclc-cox")
RAW = Path("/home/jiaqiwang/tcia/full")          # index.csv 的 series_dir 相对这里
PAPER = 12_133_187_584.0                          # 论文 Lung1 中位数

feat = pd.read_csv(ROOT / "results/tables/features_all.csv",
                   usecols=["PatientID", "original_firstorder_Energy",
                            "original_firstorder_Mean"])
timing = pd.read_csv(ROOT / "results/tables/features_all_timing.csv",
                     usecols=["PatientID", "mask_voxels"])
idx = pd.read_csv(ROOT / "results/tables/index.csv",
                  usecols=["PatientID", "series_dir"])

df = (feat.merge(timing, on="PatientID", validate="one_to_one")
          .merge(idx, on="PatientID", validate="one_to_one"))
assert len(df) == 422, len(df)


def rescale(series_dir: Path):
    for p in sorted(series_dir.iterdir()):
        if not p.is_file():
            continue
        try:
            ds = pydicom.dcmread(str(p), stop_before_pixels=True, force=True)
        except Exception:
            continue
        return (float(getattr(ds, "RescaleSlope", 1.0)),
                float(getattr(ds, "RescaleIntercept", 0.0)))
    raise RuntimeError(f"读不到 DICOM header: {series_dir}")


rows = []
for r in df.itertuples():
    slope, intercept = rescale(RAW / r.series_dir)
    n = float(r.mask_voxels)
    e_hu = float(r.original_firstorder_Energy)
    mean = float(r.original_firstorder_Mean)
    e_stored = (e_hu - 2.0 * intercept * mean * n + n * intercept ** 2) / slope ** 2
    rows.append({
        "PatientID": r.PatientID, "mask_voxels": n,
        "rescale_slope": slope, "rescale_intercept": intercept,
        "Energy_hu": e_hu, "Mean_hu": mean, "Energy_stored": e_stored,
    })

out = pd.DataFrame(rows)
# 论文口径：统一 HU+1024（不按各例 intercept 分支）
out["Energy_uniform1024"] = (
    out["Energy_hu"]
    + 2 * 1024 * out["Mean_hu"] * out["mask_voxels"]
    + out["mask_voxels"] * 1024 ** 2
)
for col, name in [("Energy_hu", "ratio_hu"),
                  ("Energy_stored", "ratio_stored"),
                  ("Energy_uniform1024", "ratio_uniform1024")]:
    out[name] = out[col] / PAPER
out.to_csv(ROOT / "results/repro/energy_scale_check.csv", index=False)

print("n =", len(out))
print("slope:", sorted(out.rescale_slope.unique()))
print("intercept:", sorted(out.rescale_intercept.unique()))
print(f"median Energy_HU          : {out.Energy_hu.median():.4e}")
print(f"median Energy_stored      : {out.Energy_stored.median():.4e}")
print(f"median Energy_uniform1024 : {out.Energy_uniform1024.median():.4e}")
print(f"paper median              : {PAPER:.4e}")
for col in ["ratio_hu", "ratio_stored", "ratio_uniform1024"]:
    r = out[col]
    print(f"{col:20s} median={r.median():.2f}  "
          f"0.5-2x={r.between(0.5, 2).mean():.1%}  "
          f"0.1-10x={r.between(0.1, 10).mean():.1%}")
print("LUNG1-001:", out.loc[out.PatientID == "LUNG1-001",
                            ["Energy_hu", "Energy_stored",
                             "Energy_uniform1024"]].to_dict("records"))