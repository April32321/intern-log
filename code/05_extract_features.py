"""Day 17：特征提取管线（全量 / 并行 / 幂等续跑）

输入：
  results/tables/index.csv                 # D12 生成的病例索引
  data/raw/full/{series_dir}/              # CT 序列
  data/raw/full/{rtstruct_path}            # RTSTRUCT
  code/params.yaml                         # 与论文对齐的参数

输出（前缀默认 --all 用 features_all，否则 features_10）：
  results/tables/{prefix}.csv              # 每例一行，全部特征
  results/tables/{prefix}_timing.csv       # 每例耗时 + 掩膜体积（QC 用）
  results/tables/{prefix}_failures.csv     # 失败病例及原因（有失败才写）
  results/tables/{prefix}_unmatched_roi.csv# 未匹配到 GTV 的病例与候选 ROI 名
  results/cache/features/{PatientID}.json  # 逐例缓存，续跑依据

设计要点：
  - 掩膜来源：RTSTRUCT 轮廓 → 用 even-odd 规则栅格化到 CT 网格；
  - ROI 名容错：normalize_roi() 去掉大小写/连字符/下划线差异；
  - 单例失败不中断整批，记 case_id 与原因；
  - 幂等：成功即写逐例缓存，重跑跳过；缓存带 params 与脚本哈希，改任一项自动重算；
  - 并行：--jobs N 起 N 个进程，每进程只建一个 extractor 且 ITK 只用单线程；
  - 打印 4 个 signature 特征与论文 Supplementary Fig. 1 的 Lung1 中位数对照。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import math
import re
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
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


# ---------------------------------------------------------------- 逐例缓存
def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_cache(path: Path, params_sha: str, script_sha: str) -> tuple[dict, dict] | None:
    """读取并校验逐例缓存；文件缺失、损坏、参数或代码已变都返回 None。"""
    try:
        with path.open(encoding="utf-8") as f:
            payload = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
    if payload.get("params_sha256") != params_sha:
        return None
    if payload.get("script_sha256") != script_sha:
        return None
    features, qc = payload.get("features"), payload.get("qc")
    if not isinstance(features, dict) or not isinstance(qc, dict):
        return None
    return features, qc


def save_cache(path: Path, case_id: str, features: dict, qc: dict,
               params_sha: str, script_sha: str) -> None:
    """原子写入：先写 .tmp 再 replace，避免中断留下半个 JSON。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "PatientID": case_id,
        "params_sha256": params_sha,
        "script_sha256": script_sha,
        "features": features,
        "qc": qc,
    }
    tmp = path.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    tmp.replace(path)


# ---------------------------------------------------------------- 并行 worker
_WORKER: dict = {}


def init_worker(params: str, raw_root: str, cache_dir: str,
                params_sha: str, script_sha: str) -> None:
    """每个子进程只做一次：建 extractor、关多线程、准备路径。"""
    sitk.ProcessObject_SetGlobalDefaultNumberOfThreads(1)
    radiomics.setVerbosity(logging.ERROR)
    _WORKER.update({
        "extractor": featureextractor.RadiomicsFeatureExtractor(params),
        "raw_root": Path(raw_root),
        "cache_dir": Path(cache_dir),
        "params_sha": params_sha,
        "script_sha": script_sha,
    })


def process_case(task: tuple[int, dict]) -> dict:
    """子进程入口：算一例，成功即写缓存（缓存与计算同一进程，崩溃只丢这一例）。"""
    pos, row = task
    case_id = str(row["PatientID"])
    t0 = time.perf_counter()
    try:
        values, qc = extract_one(row, _WORKER["extractor"], _WORKER["raw_root"])
    except Exception as exc:                      # 单例失败不中断整批
        return {"pos": pos, "status": "failed", "PatientID": case_id,
                "error_type": type(exc).__name__, "error": str(exc)[:300]}
    qc["total_seconds"] = round(time.perf_counter() - t0, 2)
    save_cache(_WORKER["cache_dir"] / f"{case_id}.json",
               case_id, values, qc, _WORKER["params_sha"], _WORKER["script_sha"])
    return {"pos": pos, "status": "ok", "PatientID": case_id,
            "values": values, "qc": qc}


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
    ap = argparse.ArgumentParser(description="Day17 特征提取（全量 / 并行 / 幂等续跑）")
    ap.add_argument("--index", default="results/tables/index.csv")
    ap.add_argument("--raw-root", default="data/raw/full")
    ap.add_argument("--params", default="code/params.yaml")
    ap.add_argument("--out-dir", default="results/tables")
    ap.add_argument("--limit", type=int, default=10,
                    help="只取前 N 例（--all 时忽略）")
    ap.add_argument("--all", action="store_true", help="处理索引中全部本地存在的病例")
    ap.add_argument("--patients", nargs="*", default=None,
                    help="指定病例（默认按 index 顺序取前 limit 例）")
    ap.add_argument("--jobs", type=int, default=1,
                    help="并行进程数（经验值：核数一半，内存吃紧再降）")
    ap.add_argument("--cache-dir", default="results/cache/features",
                    help="逐例缓存目录；复算时换一个目录即可强制重算")
    ap.add_argument("--force", action="store_true", help="忽略已有缓存，全部重算")
    ap.add_argument("--out-name", default=None,
                    help="输出前缀（默认 --all 时 features_all，否则 features_10）")
    ap.add_argument("--expect", type=int, default=None,
                    help="期望成功例数；不符则记录后以非零码退出")
    args = ap.parse_args()

    raw_root = Path(args.raw_root)
    out_dir = Path(args.out_dir)
    cache_dir = Path(args.cache_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = args.out_name or ("features_all" if args.all else "features_10")

    params_sha = sha256_file(Path(args.params))
    script_sha = sha256_file(Path(__file__).resolve())

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
    if not args.all:
        index = index.head(args.limit)
    if index.empty:
        raise SystemExit(f"{raw_root} 下没有可处理的病例")
    print(f"待处理病例: {len(index)} 例（{index['PatientID'].iloc[0]} … "
          f"{index['PatientID'].iloc[-1]}）")
    print(f"参数: {args.params}（sha256 {params_sha[:12]}）；"
          f"脚本: {script_sha[:12]}；缓存: {cache_dir}；并行进程: {args.jobs}")

    rows: list[tuple[int, dict]] = []
    qc_rows: list[tuple[int, dict]] = []
    failures: list[dict] = []
    tasks: list[tuple[int, dict]] = []

    for pos, (_, row) in enumerate(index.iterrows(), start=1):
        case_id = str(row["PatientID"])
        hit = (None if args.force
               else load_cache(cache_dir / f"{case_id}.json", params_sha, script_sha))
        if hit is not None:
            values, qc = hit
            rows.append((pos, values))
            qc_rows.append((pos, qc))
            print(f"[{pos}/{len(index)}] {case_id} 缓存命中，跳过")
            continue
        tasks.append((pos, row.to_dict()))

    cached_hits = len(index) - len(tasks)
    print(f"缓存命中 {cached_hits} 例，待计算 {len(tasks)} 例")

    t_start = time.perf_counter()
    if tasks:
        with ProcessPoolExecutor(
            max_workers=max(1, args.jobs),
            initializer=init_worker,
            initargs=(args.params, str(raw_root), str(cache_dir), params_sha, script_sha),
        ) as pool:
            futures = {pool.submit(process_case, task): task for task in tasks}
            for done, future in enumerate(as_completed(futures), start=1):
                task = futures[future]
                try:
                    res = future.result()
                except Exception as exc:          # worker 崩溃也只记一例失败
                    res = {"pos": task[0], "status": "failed",
                           "PatientID": str(task[1]["PatientID"]),
                           "error_type": type(exc).__name__, "error": str(exc)[:300]}
                if res["status"] == "failed":
                    failures.append({"PatientID": res["PatientID"],
                                     "error_type": res["error_type"],
                                     "error": res["error"]})
                    print(f"[{done}/{len(tasks)}] {res['PatientID']} 失败: "
                          f"{res['error_type']}: {res['error']}", flush=True)
                    continue
                rows.append((res["pos"], res["values"]))
                qc_rows.append((res["pos"], res["qc"]))
                qc = res["qc"]
                print(f"[{done}/{len(tasks)}] {res['PatientID']} 完成 "
                      f"（{qc['roi_name']}，{qc['n_features']} 特征，"
                      f"掩膜 {qc['mask_volume_mm3'] / 1000:.1f} cm³，"
                      f"提取 {qc['seconds']:.1f}s，合计 {qc['total_seconds']:.1f}s）",
                      flush=True)

    elapsed = time.perf_counter() - t_start
    if not rows:
        raise SystemExit("没有任何病例提取成功，终止。")

    rows.sort(key=lambda item: item[0])
    qc_rows.sort(key=lambda item: item[0])
    key_sets = {frozenset(values) for _, values in rows}
    if len(key_sets) > 1:
        print(f"\n警告：{len(key_sets)} 种特征集合，表按并集对齐，缺失处为 NaN")

    feats_df = pd.DataFrame([values for _, values in rows])
    cols = ["PatientID"] + [c for c in feats_df.columns if c != "PatientID"]
    feats_df = feats_df[cols]
    feats_df.to_csv(out_dir / f"{prefix}.csv", index=False)

    qc_df = pd.DataFrame([qc for _, qc in qc_rows])
    qc_df.to_csv(out_dir / f"{prefix}_timing.csv", index=False)

    if failures:
        pd.DataFrame(failures).to_csv(out_dir / f"{prefix}_failures.csv", index=False)

    unmatched = [{"PatientID": f["PatientID"], "error": f["error"]}
                 for f in failures if f["error_type"] == "LookupError"]
    pd.DataFrame(unmatched, columns=["PatientID", "error"]).to_csv(
        out_dir / f"{prefix}_unmatched_roi.csv", index=False)

    # ---------------- QC 汇总 ----------------
    numeric = feats_df.drop(columns=["PatientID"]).apply(pd.to_numeric, errors="coerce")
    n_bad = int((~np.isfinite(numeric.to_numpy())).sum())
    print("\n==== QC ====")
    print(f"成功 {len(feats_df)} 例（缓存 {cached_hits}，新算 {len(tasks) - len(failures)}），"
          f"失败 {len(failures)} 例")
    print(f"特征数/例: {numeric.shape[1]}"
          "（论文口径 440；本项目按 PyRadiomics 实际计数，含 1 个补算的 Compactness2）")
    print("特征构成：")
    report_feature_breakdown(feats_df.columns)
    print(f"非有限值（NaN/inf）总数: {n_bad}")
    print(f"本批计算耗时: {elapsed:.1f}s，"
          f"单例均值 {qc_df['total_seconds'].mean():.1f}s"
          f"（外推 422 例约 {qc_df['total_seconds'].mean() * 422 / 60:.0f} 分钟）")
    report_signature(feats_df)
    print("\n输出：")
    for name in [f"{prefix}.csv", f"{prefix}_timing.csv",
                 f"{prefix}_failures.csv", f"{prefix}_unmatched_roi.csv"]:
        p = out_dir / name
        if p.exists():
            print(f"  {p}")

    if args.expect is not None and len(feats_df) != args.expect:
        raise SystemExit(f"成功例数 {len(feats_df)} != --expect {args.expect}")


if __name__ == "__main__":
    main()
