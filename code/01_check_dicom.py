#!/usr/bin/env python3
"""D12 步骤 2：只读 DICOM 头部，逐患者统计 CT / RTSTRUCT / SEG 概况。

Usage:
    python3 code/01_check_dicom.py                  # $TCIA_ROOT，未设置则 data/raw/full
    python3 code/01_check_dicom.py ~/tcia/full
    python3 code/01_check_dicom.py data/raw/full/LUNG1-001
    python3 code/01_check_dicom.py --limit 3
    python3 code/01_check_dicom.py --sample
"""

from __future__ import annotations

import argparse
import os
import re
import statistics
import sys
from pathlib import Path

import pydicom
from pydicom.errors import InvalidDicomError

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ROOT = Path(
    os.environ.get("TCIA_ROOT") or REPO_ROOT / "data" / "raw" / "full"
).expanduser()

MODALITY_DIRS = ("CT", "RTSTRUCT", "SEG")
THICK_TOL = 0.05


def norm_roi(name: str) -> str:
    return re.sub(r"[-_\s]", "", name.lower())


def gtv1_hit(names: list[str]) -> bool:
    return any(n == "gtv1" for n in map(norm_roi, names))


def gtv_alias(names: list[str]) -> str:
    normed = list(map(norm_roi, names))
    if "gtv1" in normed:
        return "gtv1"
    return next((n for n in normed if n.startswith("gtvpreop")), "")


def dicom_files(pdir: Path) -> list[Path]:
    return sorted(
        f for f in pdir.rglob("*") if f.is_file() and f.suffix.lower() == ".dcm"
    )


def scan_patient(pdir: Path) -> dict:
    ct: dict[str, list[tuple[str, float | None, float | None, Path]]] = {}
    rt_paths: list[Path] = []
    seg_paths: list[Path] = []
    patient_id = ""
    bad = 0

    for f in dicom_files(pdir):
        try:
            ds = pydicom.dcmread(f, stop_before_pixels=True)
        except (InvalidDicomError, OSError, ValueError):
            bad += 1
            continue

        modality = getattr(ds, "Modality", "")
        if modality == "CT":
            if not patient_id:
                patient_id = str(getattr(ds, "PatientID", ""))
            uid = str(getattr(ds, "SeriesInstanceUID", ""))
            pos = getattr(ds, "ImagePositionPatient", None)
            thick = getattr(ds, "SliceThickness", None)
            z = float(pos[2]) if pos else None
            ct.setdefault(uid, []).append(
                (
                    str(getattr(ds, "SOPInstanceUID", f.stem)),
                    z,
                    float(thick) if thick is not None else None,
                    f.parent,
                )
            )
        elif modality == "RTSTRUCT":
            rt_paths.append(f)
        elif modality == "SEG":
            seg_paths.append(f)

    roi_names: list[str] = []
    if rt_paths:
        try:
            rt = pydicom.dcmread(rt_paths[0], stop_before_pixels=True)
        except (InvalidDicomError, OSError, ValueError):
            bad += 1
        else:
            roi_names = [
                str(item.ROIName)
                for item in getattr(rt, "StructureSetROISequence", [])
            ]

    n_slices = len({sop for series in ct.values() for sop, _, _, _ in series})
    zs = sorted({z for series in ct.values() for _, z, _, _ in series if z is not None})
    gaps = [b - a for a, b in zip(zs, zs[1:]) if b - a > 1e-6]
    z_gap = round(statistics.median(gaps), 3) if gaps else None
    thicks = [t for series in ct.values() for _, _, t, _ in series if t is not None]
    thickness = round(statistics.median(thicks), 3) if thicks else None
    breaks = sum(1 for g in gaps if z_gap and g > z_gap * 1.5)

    main_uid = max(ct, key=lambda u: len(ct[u])) if ct else None
    series_dir = str(ct[main_uid][0][3]) if main_uid else ""

    warns: list[str] = []
    if not ct:
        warns.append("无CT")
    if len(ct) > 1:
        warns.append(f"CT拆成{len(ct)}个series")
    if not rt_paths:
        warns.append("无RTSTRUCT")
    if len(rt_paths) > 1:
        warns.append(f"RTSTRUCT有{len(rt_paths)}个")
    if not seg_paths:
        warns.append("无SEG")
    if thickness is None:
        warns.append("缺SliceThickness")
    if thickness is not None and z_gap is not None and abs(thickness - z_gap) > THICK_TOL:
        warns.append(f"层厚{thickness}≠z间距{z_gap}")
    if breaks:
        warns.append(f"层距断档{breaks}处")
    if patient_id and patient_id != pdir.name:
        warns.append(f"目录名{pdir.name}≠PatientID{patient_id}")
    if bad:
        warns.append(f"{bad}个文件无法解析")

    return {
        "patient": pdir.name,
        "patient_id": patient_id or pdir.name,
        "n_ct_series": len(ct),
        "n_slices": n_slices,
        "slice_thickness": thickness,
        "z_gap": z_gap,
        "has_rtstruct": bool(rt_paths),
        "has_seg": bool(seg_paths),
        "roi_names": roi_names,
        "gtv1_present": gtv1_hit(roi_names),
        "gtv_alias": gtv_alias(roi_names),
        "series_dir": series_dir,
        "rtstruct_path": str(rt_paths[0]) if rt_paths else "",
        "warns": warns,
    }


def discover(root: Path) -> list[Path]:
    if any((root / name).is_dir() for name in MODALITY_DIRS):
        return [root]
    return sorted(
        d
        for d in root.iterdir()
        if d.is_dir() and any((d / name).is_dir() for name in MODALITY_DIRS)
    )


def print_sample(root: Path) -> None:
    patients = discover(root)
    if not patients:
        return
    print(f"抽样（{patients[0].name} 前 3 个 .dcm）:")
    for f in dicom_files(patients[0])[:3]:
        ds = pydicom.dcmread(f, stop_before_pixels=True)
        print(
            f"  {f.name}  {getattr(ds, 'Modality', '')}  "
            f"{str(getattr(ds, 'SeriesInstanceUID', ''))[:20]}"
        )


def print_patient(r: dict) -> None:
    thick = "-" if r["slice_thickness"] is None else f'{r["slice_thickness"]:g}'
    zgap = "-" if r["z_gap"] is None else f'{r["z_gap"]:g}'
    print(
        f'{r["patient"]:<12} CT_series={r["n_ct_series"]} '
        f'slices={r["n_slices"]} thick={thick}mm z_gap={zgap} '
        f'RTSTRUCT={"Y" if r["has_rtstruct"] else "N"} '
        f'SEG={"Y" if r["has_seg"] else "N"} '
        f'GTV1={"Y" if r["gtv1_present"] else "N"} '
        f'ROI={len(r["roi_names"])}'
        + (f' alias={r["gtv_alias"]}' if r["gtv_alias"] and not r["gtv1_present"] else "")
    )
    if r["roi_names"]:
        print(f'    ROIs: {", ".join(r["roi_names"])}')
    for w in r["warns"]:
        print(f"    WARN: {w}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="逐患者统计 DICOM 的 CT / RTSTRUCT / SEG 概况（只读头部）"
    )
    ap.add_argument("path", nargs="?", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--limit", type=int, default=0, help="只处理前 N 个患者")
    ap.add_argument("--sample", action="store_true", help="额外打印首个患者的前 3 个文件")
    args = ap.parse_args()

    root = args.path.expanduser().resolve()
    if not root.exists():
        print(f"路径不存在: {root}", file=sys.stderr)
        return 2

    patients = discover(root)
    if not patients:
        print(f"未在 {root} 找到患者目录（需含 CT/RTSTRUCT/SEG）", file=sys.stderr)
        return 2
    if args.limit:
        patients = patients[: args.limit]

    print(f"根目录: {root}")
    print(f"患者数: {len(patients)}")
    if args.sample:
        print_sample(root)
    print()

    results = [scan_patient(p) for p in patients]
    for r in results:
        print_patient(r)

    no_rt = [r["patient"] for r in results if not r["has_rtstruct"]]
    no_seg = [r["patient"] for r in results if not r["has_seg"]]
    no_gtv = [r["patient"] for r in results if not r["gtv1_present"]]
    warned = [r["patient"] for r in results if r["warns"]]
    multi = [r["patient"] for r in results if r["n_ct_series"] > 1]

    print()
    print(
        f"汇总: 患者={len(results)} CT_series={sum(r['n_ct_series'] for r in results)} "
        f"slices={sum(r['n_slices'] for r in results)} "
        f"无RTSTRUCT={no_rt or '-'} 无SEG={no_seg or '-'} "
        f"无GTV1={no_gtv or '-'} 多series={multi or '-'} 有警告={len(warned)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
