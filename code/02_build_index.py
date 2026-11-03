#!/usr/bin/env python3
"""D12 步骤 3：生成 422 行、每行一个患者的 results/tables/index.csv。

Usage:
    python3 code/02_build_index.py                    # 默认 --expect 422
    python3 code/02_build_index.py --expect 6         # 本机 6 例样本
    python3 code/02_build_index.py --root ~/tcia/full --out ~/tcia/results
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ROOT = Path(
    os.environ.get("TCIA_ROOT") or REPO_ROOT / "data" / "raw" / "full"
).expanduser()
DEFAULT_OUT = Path(os.environ.get("TCIA_OUT") or REPO_ROOT / "results").expanduser()

COLUMNS = [
    "PatientID",
    "n_ct_series",
    "n_slices",
    "slice_thickness",
    "has_rtstruct",
    "has_seg",
    "roi_names",
    "gtv1_present",
    "series_dir",
    "rtstruct_path",
]


def load_scanner():
    path = Path(__file__).with_name("01_check_dicom.py")
    spec = importlib.util.spec_from_file_location("check_dicom", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def relative(path_str: str, root: Path) -> str:
    if not path_str:
        return ""
    try:
        return str(Path(path_str).resolve().relative_to(root))
    except ValueError:
        return path_str


def build_rows(scanner, root: Path) -> list[dict]:
    rows = []
    for pdir in scanner.discover(root):
        stats = scanner.scan_patient(pdir)
        rows.append(
            {
                "PatientID": stats["patient_id"],
                "n_ct_series": stats["n_ct_series"],
                "n_slices": stats["n_slices"],
                "slice_thickness": stats["slice_thickness"],
                "has_rtstruct": stats["has_rtstruct"],
                "has_seg": stats["has_seg"],
                "roi_names": "|".join(stats["roi_names"]),
                "gtv1_present": stats["gtv1_present"],
                "series_dir": relative(stats["series_dir"], root),
                "rtstruct_path": relative(stats["rtstruct_path"], root),
            }
        )
    return rows


def describe(df: pd.DataFrame) -> None:
    no_rt = df.loc[~df.has_rtstruct, "PatientID"].tolist()
    no_seg = df.loc[~df.has_seg, "PatientID"].tolist()
    no_gtv = df.loc[~df.gtv1_present, "PatientID"].tolist()
    multi = df.loc[df.n_ct_series > 1, "PatientID"].tolist()
    thin = df["slice_thickness"].value_counts(dropna=False).to_dict()

    print(f"患者: {len(df)}")
    print(f"CT series: {int(df.n_ct_series.sum())}（多 series: {multi or '-'}）")
    print(f"CT 层数合计: {int(df.n_slices.sum())}")
    print(f"层厚分布: {thin}")
    print(f"无 RTSTRUCT: {no_rt or '-'}")
    print(f"无 SEG: {no_seg or '-'}")
    print(f"无 GTV-1: {no_gtv or '-'}")


def check(df: pd.DataFrame, expect: int) -> None:
    errors = []
    if len(df) != expect:
        errors.append(f"行数 {len(df)} != {expect}")
    if df.PatientID.duplicated().any():
        errors.append(f"PatientID 重复: {df.loc[df.PatientID.duplicated(), 'PatientID'].tolist()}")
    if df.PatientID.isna().any() or (df.PatientID == "").any():
        errors.append("存在空 PatientID")
    if expect == 422:
        no_gtv = sorted(df.loc[~df.gtv1_present, "PatientID"].tolist())
        if no_gtv != ["LUNG1-128"]:
            errors.append(f"无 GTV-1 的患者应为 ['LUNG1-128']，实际 {no_gtv}")
        no_seg = sorted(df.loc[~df.has_seg, "PatientID"].tolist())
        if no_seg != ["LUNG1-128"]:
            errors.append(f"无 SEG 的患者应为 ['LUNG1-128']，实际 {no_seg}")
        if not df.has_rtstruct.all():
            errors.append("存在无 RTSTRUCT 的患者")
    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        raise SystemExit(1)


def main() -> int:
    ap = argparse.ArgumentParser(description="生成每行一个患者的 DICOM 索引表")
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--expect", type=int, default=422, help="期望的患者行数")
    args = ap.parse_args()

    root = args.root.expanduser().resolve()
    out_dir = args.out.expanduser().resolve() / "tables"
    if not root.exists():
        print(f"路径不存在: {root}", file=sys.stderr)
        return 2

    scanner = load_scanner()
    rows = build_rows(scanner, root)
    if not rows:
        print(f"未在 {root} 找到患者目录", file=sys.stderr)
        return 2

    df = pd.DataFrame(rows, columns=COLUMNS).sort_values("PatientID").reset_index(drop=True)
    check(df, args.expect)

    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "index.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8")

    describe(df)
    print(f"写出: {csv_path}（{len(df)} 行 × {df.shape[1]} 列）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
