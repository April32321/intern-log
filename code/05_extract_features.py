"""Day 16：特征提取管线（先跑 10 例）

输入：
  results/tables/index.csv                 # D12 生成的病例索引
  data/raw/full/{series_dir}/              # CT 序列
  data/raw/full/{rtstruct_path}            # RTSTRUCT
  code/params.yaml                         # 与论文对齐的参数

输出：
  results/tables/features_10.csv           # 每例一行，全部特征
  results/tables/features_10_timing.csv    # 每例耗时 + 掩膜体积（QC 用）
  results/tables/features_10_failures.csv  # 失败病例及原因（有失败才写）
  results/tables/unmatched_roi.csv         # 未匹配到 GTV 的病例与候选 ROI 名

设计要点：
  - 掩膜来源：RTSTRUCT 轮廓 → 用 even-odd 规则栅格化到 CT 网格；
  - ROI 名容错：normalize_roi() 去掉大小写/连字符/下划线差异；
  - 单例失败不中断整批，记 case_id 与原因；
  - 打印 4 个 signature 特征与论文 Supplementary Fig. 1 的 Lung1 中位数对照。
"""

from __future__ import annotations

import argparse
import logging
import math
import re
import time
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import pydicom
import radiomics
import SimpleITK as sitk
from radiomics import featureextractor

radiomics.setVerbosity(logging.ERROR)

# 论文 Supplementary Fig. 1 的 Lung1 中位数，仅用于量纲校验，不可当分组阈值
# 注意：PyRadiomics 3.x 已移除 Compactness1/2，改由 MeshVolume 与 SurfaceArea 现算
PAPER_MEDIANS = {
    "original_firstorder_Energy": 12_133_187_584.0,
    "original_shape_Compactness2_derived": 0.24,
    "original_glrlm_GrayLevelNonUniformity": 984.67,
    "wavelet-HLH_glrlm_GrayLevelNonUniformity": 1110.68,
}


# ---------------------------------------------------------------- ROI 名称匹配
def normalize_roi(name: str) -> str:
    """把 GTV-1 / GTV1 / gtv_1 / GTV 1 统一成 'gtv1' 这类形式。"""
    return re.sub(r"[^a-z0-9]+", "", str(name).lower())


def pick_gtv(roi_names: dict[int, str], has_contour: set[int]) -> tuple[int | None, list[str]]:
    """返回 (选中的 ROI number, 全部 GTV 候选名)。

    优先级：gtv1/gtv/gtvprimary > 含 pre 的 gtv* > 唯一的 gtv*。
    """
    cands = [(num, name, normalize_roi(name)) for num, name in roi_names.items()
             if num in has_contour]
    gtv_cands = [c for c in cands if c[2].startswith("gtv")]

    exact = [c for c in gtv_cands if c[2] in {"gtv1", "gtv", "gtvprimary"}]
    if exact:
        return exact[0][0], [c[1] for c in gtv_cands]

    pre = [c for c in gtv_cands if "pre" in c[2]]
    if pre:
        return pre[0][0], [c[1] for c in gtv_cands]

    if len(gtv_cands) == 1:
        return gtv_cands[0][0], [c[1] for c in gtv_cands]

    return None, [c[1] for c in gtv_cands]


# ---------------------------------------------------------------- 读取影像与轮廓
def read_series(series_dir: Path) -> sitk.Image:
    reader = sitk.ImageSeriesReader()
    series_ids = list(reader.GetGDCMSeriesIDs(str(series_dir)) or [])
    if not series_ids:
        raise RuntimeError(f"目录内没有 DICOM 序列: {series_dir}")

    if len(series_ids) > 1:
        best = max(series_ids,
                   key=lambda sid: len(reader.GetGDCMSeriesFileNames(str(series_dir), sid)))
    else:
        best = series_ids[0]

    files = reader.GetGDCMSeriesFileNames(str(series_dir), best)
    reader.SetFileNames(files)
    return reader.Execute()


def read_rtstruct(path: Path) -> tuple[dict[int, str], dict[int, list[np.ndarray]]]:
    ds = pydicom.dcmread(str(path))
    roi_names = {int(item.ROINumber): str(item.ROIName)
                 for item in ds.StructureSetROISequence}

    contours: dict[int, list[np.ndarray]] = {}
    for roi_contour in getattr(ds, "ROIContourSequence", []):
        num = getattr(roi_contour, "ReferencedROINumber", None)
        if num is None:
            continue
        num = int(num)
        seq = getattr(roi_contour, "ContourSequence", None)
        if not seq:
            continue
        polys = []
        for c in seq:
            pts = np.asarray(c.ContourData, dtype=float).reshape(-1, 3)
            if len(pts) >= 3:
                polys.append(pts)
        if polys:
            contours[num] = polys
    return roi_names, contours


# ---------------------------------------------------------------- 栅格化
def rasterize_polygon(xs: np.ndarray, ys: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    """把单个闭合多边形填成布尔掩膜。

    xs / ys 是**连续索引坐标**（像素 i 覆盖 [i, i+1)，中心 i+0.5）。
    shape = (rows, cols)。用 even-odd 规则（同一层的多个轮廓用 XOR 合并，
    因此带孔洞的轮廓也能正确处理）。
    """
    n_rows, n_cols = shape
    out = np.zeros(shape, dtype=bool)
    if len(xs) < 3:
        return out

    row_lo = max(int(np.floor(ys.min())), 0)
    row_hi = min(int(np.ceil(ys.max())), n_rows - 1)
    if row_hi < row_lo:
        return out

    x1, y1 = xs, ys
    x2, y2 = np.roll(xs, -1), np.roll(ys, -1)
    rows = np.arange(row_lo, row_hi + 1)
    yc = (rows + 0.5)[:, None]                      # (R,1)

    crosses = ((y1 <= yc) & (yc < y2)) | ((y2 <= yc) & (yc < y1))
    dy = np.where(y2 != y1, y2 - y1, np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        inter = x1 + (yc - y1) * (x2 - x1) / dy     # (R,E)，无效处为 nan
    inter = np.where(crosses, inter, np.inf)
    inter.sort(axis=1)

    left, right = inter[:, 0::2], inter[:, 1::2]    # even-odd 配对
    n_pairs = min(left.shape[1], right.shape[1])    # 边数为奇数时对齐
    left, right = left[:, :n_pairs], right[:, :n_pairs]
    valid = np.isfinite(left) & np.isfinite(right)

    col_lo = np.ceil(np.where(valid, left, 0) - 0.5).astype(int)
    col_hi = np.floor(np.where(valid, right, -1) - 0.5).astype(int)
    col_lo = np.clip(col_lo, 0, n_cols)
    col_hi = np.clip(col_hi, -1, n_cols - 1)
    valid &= col_hi >= col_lo

    if not valid.any():
        return out

    diff = np.zeros((len(rows), n_cols + 1), dtype=np.int32)
    rr = np.broadcast_to(rows[:, None], col_lo.shape)
    np.add.at(diff, (rr[valid] - row_lo, col_lo[valid]), 1)
    np.add.at(diff, (rr[valid] - row_lo, col_hi[valid] + 1), -1)
    out[row_lo:row_hi + 1] = np.cumsum(diff[:, :n_cols], axis=1) > 0
    return out


def build_mask(polys: list[np.ndarray], image: sitk.Image) -> np.ndarray:
    """把某 ROI 的所有轮廓栅格化到 CT 网格，返回 (z, y, x) uint8 掩膜。"""
    nx, ny, nz = image.GetSize()
    mask = np.zeros((nz, ny, nx), dtype=np.uint8)

    for poly in polys:
        idx = np.asarray([image.TransformPhysicalPointToContinuousIndex(tuple(p))
                          for p in poly], dtype=float)
        k = int(round(float(np.median(idx[:, 2]))))
        if k < 0 or k >= nz:
            continue
        layer = rasterize_polygon(idx[:, 0], idx[:, 1], (ny, nx))
        mask[k] ^= layer.astype(np.uint8)   # XOR：支持一个 ROI 内部有孔洞
    return mask


# ---------------------------------------------------------------- 单例提取
def extract_one(row, extractor, raw_root: Path) -> tuple[dict, dict]:
    case_id = str(row["PatientID"])

    image = read_series(raw_root / str(row["series_dir"]))
    roi_names, contours = read_rtstruct(raw_root / str(row["rtstruct_path"]))

    roi_num, gtv_names = pick_gtv(roi_names, set(contours))
    if roi_num is None:
        raise LookupError(f"未匹配到 GTV；候选 ROI: {roi_names}")

    mask = build_mask(contours[roi_num], image)
    voxels = int(mask.sum())
    if voxels == 0:
        raise ValueError(f"掩膜为空（ROI={roi_names[roi_num]}）")

    mask_img = sitk.GetImageFromArray(mask)
    mask_img.CopyInformation(image)

    t0 = time.perf_counter()
    feats = extractor.execute(image, mask_img, label=1)
    elapsed = time.perf_counter() - t0

    values = {k: float(v) for k, v in feats.items() if not k.startswith("diagnostics_")}
    values["PatientID"] = case_id

    # PyRadiomics 3.x 移除了 Compactness1/2 与 SphericalDisproportion，
    # 按原定义补算 Compactness2 = 36π·V² / A³，保证论文第 2 个特征可用。
    vol = values.get("original_shape_MeshVolume")
    area = values.get("original_shape_SurfaceArea")
    if vol and area:
        values["original_shape_Compactness2_derived"] = 36.0 * math.pi * vol ** 2 / area ** 3

    spacing = image.GetSpacing()
    qc = {
        "PatientID": case_id,
        "roi_name": roi_names[roi_num],
        "roi_candidates": "|".join(gtv_names),
        "mask_voxels": voxels,
        "mask_volume_mm3": voxels * spacing[0] * spacing[1] * spacing[2],
        "seconds": round(elapsed, 2),
        "n_features": len(values) - 1,
    }
    return values, qc


# ---------------------------------------------------------------- 汇总打印
def report_feature_breakdown(columns) -> None:
    """按 (影像类型, 特征类) 统计特征数，用于核对特征数量是否合理。"""
    counts: Counter[tuple[str, str]] = Counter()
    for col in columns:
        if col == "PatientID":
            continue
        tokens = col.split("_")
        image_type = tokens[0].split("-")[0]
        feature_class = tokens[1] if len(tokens) > 1 else "?"
        counts[(image_type, feature_class)] += 1
    for (image_type, feature_class), n in sorted(counts.items()):
        print(f"  {image_type:10s} {feature_class:12s} {n:4d}")


def report_signature(df: pd.DataFrame) -> None:
    print("\n4 个 signature 特征（与论文 Lung1 中位数对照，仅量纲校验）：")
    print(f"{'特征':52s} {'本批中位数':>16s} {'论文中位数':>16s}")
    for key, paper in PAPER_MEDIANS.items():
        if key in df.columns:
            ours = float(pd.to_numeric(df[key], errors='coerce').median())
            ratio = ours / paper if paper else float('nan')
            print(f"{key:52s} {ours:16.4g} {paper:16.4g}  (×{ratio:.2f})")
        else:
            print(f"{key:52s} {'缺失':>16s} {paper:16.4g}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Day16 特征提取（先 10 例）")
    ap.add_argument("--index", default="results/tables/index.csv")
    ap.add_argument("--raw-root", default="data/raw/full")
    ap.add_argument("--params", default="code/params.yaml")
    ap.add_argument("--out-dir", default="results/tables")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--patients", nargs="*", default=None,
                    help="指定病例（默认按 index 顺序取前 limit 例）")
    args = ap.parse_args()

    raw_root = Path(args.raw_root)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    index = pd.read_csv(args.index)
    index = index[index["has_rtstruct"].astype(str).str.lower() == "true"].copy()

    # index.csv 覆盖全部 422 例，但本地可能只下载了子集：只保留磁盘上存在的病例
    if raw_root.is_dir():
        existed = {p.name for p in raw_root.iterdir() if p.is_dir()}
        before = len(index)
        index = index[index["PatientID"].isin(existed)]
        if len(index) != before:
            print(f"本地仅有 {len(index)}/{before} 例的数据，按磁盘存在的病例处理")

    if args.patients:
        index = index[index["PatientID"].isin(args.patients)]
    index = index.head(args.limit)
    if index.empty:
        raise SystemExit(f"{raw_root} 下没有可处理的病例")
    print(f"待处理病例: {len(index)} 例（{index['PatientID'].iloc[0]} … "
          f"{index['PatientID'].iloc[-1]}）")

    extractor = featureextractor.RadiomicsFeatureExtractor(args.params)
    print(f"启用特征类: {sorted(extractor.enabledFeatures)}")
    print(f"参数: {args.params}")

    rows, qc_rows, failures = [], [], []
    total_cases = len(index)
    for pos, (_, row) in enumerate(index.iterrows(), start=1):
        case_id = str(row["PatientID"])
        t0 = time.perf_counter()
        try:
            values, qc = extract_one(row, extractor, raw_root)
        except Exception as exc:                      # 单例失败不中断整批
            failures.append({"PatientID": case_id,
                             "error_type": type(exc).__name__,
                             "error": str(exc)[:300]})
            print(f"[{pos}/{total_cases}] {case_id} 失败: {type(exc).__name__}: {exc}")
            continue
        total = time.perf_counter() - t0
        rows.append(values)
        qc["total_seconds"] = round(total, 2)
        qc_rows.append(qc)
        print(f"[{pos}/{total_cases}] {case_id} 完成 "
              f"（{qc['roi_name']}，{qc['n_features']} 特征，"
              f"掩膜 {qc['mask_volume_mm3'] / 1000:.1f} cm³，"
              f"提取 {qc['seconds']:.1f}s，合计 {total:.1f}s）")

    if not rows:
        raise SystemExit("没有任何病例提取成功，终止。")

    feats_df = pd.DataFrame(rows)
    cols = ["PatientID"] + [c for c in feats_df.columns if c != "PatientID"]
    feats_df = feats_df[cols]
    feats_df.to_csv(out_dir / "features_10.csv", index=False)

    qc_df = pd.DataFrame(qc_rows)
    qc_df.to_csv(out_dir / "features_10_timing.csv", index=False)

    if failures:
        pd.DataFrame(failures).to_csv(out_dir / "features_10_failures.csv", index=False)

    unmatched = [{"PatientID": f["PatientID"], "error": f["error"]}
                 for f in failures if f["error_type"] == "LookupError"]
    pd.DataFrame(unmatched, columns=["PatientID", "error"]).to_csv(
        out_dir / "unmatched_roi.csv", index=False)

    # ---------------- QC 汇总 ----------------
    numeric = feats_df.drop(columns=["PatientID"]).apply(pd.to_numeric, errors="coerce")
    n_bad = int((~np.isfinite(numeric.to_numpy())).sum())
    print("\n==== QC ====")
    print(f"成功 {len(feats_df)} 例，失败 {len(failures)} 例")
    print(f"特征数/例: {numeric.shape[1]}"
          "（论文口径 440；本项目按 PyRadiomics 实际计数，含 1 个补算的 Compactness2）")
    print("特征构成：")
    report_feature_breakdown(feats_df.columns)
    print(f"非有限值（NaN/inf）总数: {n_bad}")
    print(f"总耗时: {qc_df['total_seconds'].sum():.1f}s，"
          f"单例均值 {qc_df['total_seconds'].mean():.1f}s"
          f"（外推 422 例约 {qc_df['total_seconds'].mean() * 422 / 60:.0f} 分钟）")
    report_signature(feats_df)
    print("\n输出：")
    for name in ["features_10.csv", "features_10_timing.csv",
                 "features_10_failures.csv", "unmatched_roi.csv"]:
        p = out_dir / name
        if p.exists():
            print(f"  {p}")


if __name__ == "__main__":
    main()
