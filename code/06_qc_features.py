"""Day 17：特征表质控（行数 / 缺失 / 零方差 / 一致性 / 分布）

输入：
  results/tables/features_all.csv          # 05 产出的全量特征表
  results/tables/features_all_timing.csv   # 每例耗时与掩膜几何
  results/tables/features_all_failures.csv # 失败清单（可能不存在）
  results/tables/index.csv                 # D12 索引，用于核对应有病例数
  results/tables/features_10.csv           # D16 基线（10 例），用于一致性比对

输出：
  results/tables/features_qc.md            # 质控报告
  results/tables/feature_missing_rate.csv  # 每列缺失率
  results/tables/feature_zero_variance.csv # 零方差 / 全缺失列
  results/tables/qc_missing_patients.csv   # 缺例清单（PatientID + 原因）
  results/figures/qc/hist_random6.png      # 随机 6 个特征的直方图

判据：
  - 行数 = 索引中 has_rtstruct=True 且本地存在目录的病例数；
  - 缺失率 > --missing-threshold（默认 0.2）标记，建议剔除；
  - 零方差（nunique <= 1）或全缺失列，建议剔除；
  - 与 D16 基线、与不同并行度的结果比对，最大相对差应在浮点误差量级；
  - 行数不符时以非零码退出，避免"少跑却显示通过"。
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

matplotlib.rcParams["font.sans-serif"] = [
    "PingFang SC", "Hiragino Sans GB", "Arial Unicode MS", "DejaVu Sans",
]
matplotlib.rcParams["axes.unicode_minus"] = False

# 一致性判据：超过该相对差就认为不是浮点误差
CONSISTENCY_TOL = 1e-6


# ---------------------------------------------------------------- 载入
def load_features(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise SystemExit(f"缺少特征表: {path}")
    df = pd.read_csv(path)
    if "PatientID" not in df.columns:
        raise SystemExit(f"{path} 没有 PatientID 列")
    return df


def load_optional(path: Path) -> pd.DataFrame | None:
    return pd.read_csv(path) if path.exists() else None


# ---------------------------------------------------------------- 行数核对
def expected_patients(index_path: Path, raw_root: Path) -> pd.DataFrame:
    index = pd.read_csv(index_path)
    index = index[index["has_rtstruct"].astype(str).str.lower() == "true"].copy()
    index = index[index["PatientID"].apply(
        lambda pid: (raw_root / str(pid)).is_dir())]
    return index


def missing_reasons(index: pd.DataFrame, have: set[str], raw_root: Path,
                    failures: pd.DataFrame | None) -> pd.DataFrame:
    fail_map = {}
    if failures is not None and {"PatientID", "error"}.issubset(failures.columns):
        fail_map = dict(zip(failures["PatientID"].astype(str), failures["error"].astype(str)))

    rows = []
    for _, row in index.iterrows():
        pid = str(row["PatientID"])
        if pid in have:
            continue
        if pid in fail_map:
            reason = f"提取失败：{fail_map[pid][:120]}"
        elif not (raw_root / str(row["rtstruct_path"])).exists():
            reason = "RTSTRUCT 文件不存在"
        else:
            reason = "未出现在特征表中（无失败记录）"
        rows.append({"PatientID": pid, "reason": reason})
    return pd.DataFrame(rows, columns=["PatientID", "reason"])


# ---------------------------------------------------------------- 数值检查
def numeric_block(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns=["PatientID"]).apply(pd.to_numeric, errors="coerce")


def missing_table(num: pd.DataFrame) -> pd.DataFrame:
    rate = num.isna().mean()
    out = pd.DataFrame({"feature": rate.index, "missing_rate": rate.values})
    return out.sort_values("missing_rate", ascending=False).reset_index(drop=True)


def zero_variance_table(num: pd.DataFrame) -> pd.DataFrame:
    nuniq = num.nunique(dropna=True)
    all_nan = num.isna().all()
    rows = [
        {"feature": col, "n_unique": int(nuniq[col]),
         "all_missing": bool(all_nan[col])}
        for col in num.columns
        if nuniq[col] <= 1
    ]
    return pd.DataFrame(rows, columns=["feature", "n_unique", "all_missing"])


def feature_breakdown(columns) -> dict[tuple[str, str], int]:
    counts: Counter[tuple[str, str]] = Counter()
    for col in columns:
        if col == "PatientID":
            continue
        tokens = col.split("_")
        image_type = tokens[0].split("-")[0]
        feature_class = tokens[1] if len(tokens) > 1 else "?"
        counts[(image_type, feature_class)] += 1
    return counts


# ---------------------------------------------------------------- 一致性比对
def compare_tables(left: pd.DataFrame, right: pd.DataFrame,
                   label: str) -> dict:
    """逐列比对两张特征表（按 PatientID 对齐），返回最大相对/绝对差。"""
    common_ids = sorted(set(left["PatientID"]) & set(right["PatientID"]))
    if not common_ids:
        return {"label": label, "n_cases": 0}

    cols = [c for c in left.columns
            if c in right.columns and c != "PatientID"]
    a = left.set_index("PatientID").loc[common_ids, cols].apply(pd.to_numeric, errors="coerce")
    b = right.set_index("PatientID").loc[common_ids, cols].apply(pd.to_numeric, errors="coerce")

    av, bv = a.to_numpy(dtype=float), b.to_numpy(dtype=float)
    valid = np.isfinite(av) & np.isfinite(bv)
    absdiff = np.where(valid, np.abs(av - bv), 0.0)
    rel = np.where(valid, absdiff / np.maximum(np.abs(bv), 1e-12), 0.0)

    per_col_rel = np.where(valid, rel, np.nan)
    with np.errstate(invalid="ignore"):
        col_max = np.nanmax(per_col_rel, axis=0) if len(common_ids) else np.zeros(len(cols))
    top = sorted(zip(cols, np.nan_to_num(col_max)), key=lambda kv: kv[1], reverse=True)[:5]
    return {
        "label": label,
        "n_cases": len(common_ids),
        "n_cols": len(cols),
        "max_rel": float(np.max(rel)) if rel.size else 0.0,
        "max_abs": float(np.max(absdiff)) if absdiff.size else 0.0,
        "n_cols_over_tol": int(np.sum(np.nan_to_num(col_max) > CONSISTENCY_TOL)),
        "top_cols": top,
    }


# ---------------------------------------------------------------- 作图
def plot_random_histograms(num: pd.DataFrame, out_png: Path,
                           n: int, seed: int) -> list[str]:
    usable = [c for c in num.columns if num[c].nunique(dropna=True) > 1]
    if not usable:
        return []
    rng = np.random.default_rng(seed)
    picked = list(rng.choice(usable, size=min(n, len(usable)), replace=False))

    ncols, nrows = 2, int(np.ceil(len(picked) / 2))
    fig, axes = plt.subplots(nrows, ncols, figsize=(11, 3.2 * nrows))
    axes = np.atleast_1d(axes).ravel()
    for ax, col in zip(axes, picked):
        values = pd.to_numeric(num[col], errors="coerce").dropna()
        ax.hist(values, bins=30, color="#4c72b0", alpha=0.85)
        ax.set_title(col, fontsize=8)
        ax.tick_params(labelsize=7)
    for ax in axes[len(picked):]:
        ax.axis("off")
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=150)
    plt.close(fig)
    return [str(c) for c in picked]


# ---------------------------------------------------------------- 报告
def fmt_rate(x: float) -> str:
    return f"{x:.2%}"


def build_report(args, feats: pd.DataFrame, num: pd.DataFrame, timing: pd.DataFrame | None,
                 failures: pd.DataFrame | None, expected: pd.DataFrame,
                 missing: pd.DataFrame, miss_tbl: pd.DataFrame,
                 zero_tbl: pd.DataFrame, baseline: dict | None,
                 parallel: dict | None, hist_cols: list[str],
                 breakdown: dict) -> str:
    n_rows, n_cols = feats.shape
    n_features = n_cols - 1
    nonfinite = int(np.sum(~np.isfinite(num.to_numpy(dtype=float))))
    high_missing = miss_tbl[miss_tbl["missing_rate"] > args.missing_threshold]

    lines: list[str] = []
    lines.append("# 特征质控报告（Day 17）")
    lines.append("")
    lines.append(f"- 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- 脚本：`code/06_qc_features.py`")
    lines.append(f"- 特征表：`{args.features}`")
    lines.append(f"- 索引：`{args.index}`；本地数据：`{args.raw_root}`")
    lines.append("")
    lines.append("## 1. 行数与缺例")
    lines.append("")
    lines.append(f"- 索引中应有病例（`has_rtstruct=True` 且本地存在目录）：**{len(expected)}**")
    lines.append(f"- 特征表实际行数：**{n_rows}**；列数 **{n_cols}**（`PatientID` + {n_features} 特征）")
    if len(missing):
        lines.append(f"- **缺例 {len(missing)} 例**（完整清单：`{args.missing_patients_out}`）：")
        lines.append("")
        lines.append("| PatientID | 原因 |")
        lines.append("|---|---|")
        for _, row in missing.head(30).iterrows():
            lines.append(f"| {row['PatientID']} | {row['reason']} |")
        if len(missing) > 30:
            lines.append(f"| …（其余 {len(missing) - 30} 例见 CSV） | |")
    else:
        lines.append("- 缺例：**0**（全部命中）")
    if failures is not None and len(failures):
        lines.append(f"- 失败清单：`{args.failures}` 共 {len(failures)} 条")
        if "error_type" in failures.columns:
            counts = failures["error_type"].value_counts()
            lines.append("- 失败类型：" + "；".join(f"`{k}` × {v}" for k, v in counts.items()))
    lines.append("")

    lines.append("## 2. 缺失率")
    lines.append("")
    lines.append(f"- 缺失率 > {fmt_rate(args.missing_threshold)} 的特征：**{len(high_missing)}** 个")
    if len(high_missing):
        lines.append("")
        lines.append("| feature | missing_rate |")
        lines.append("|---|---:|")
        for _, row in high_missing.head(30).iterrows():
            lines.append(f"| {row['feature']} | {fmt_rate(row['missing_rate'])} |")
        if len(high_missing) > 30:
            lines.append(f"| …（其余 {len(high_missing) - 30} 个见 CSV） | |")
    lines.append("")
    lines.append(f"- 明细：`{args.missing_out}`")
    lines.append("")

    lines.append("## 3. 零方差 / 全缺失")
    lines.append("")
    lines.append(f"- 零方差或全缺失列：**{len(zero_tbl)}** 个（建议剔除）")
    if len(zero_tbl):
        lines.append("")
        lines.append("| feature | n_unique | all_missing |")
        lines.append("|---|---:|---|")
        for _, row in zero_tbl.head(30).iterrows():
            lines.append(f"| {row['feature']} | {row['n_unique']} | {row['all_missing']} |")
        if len(zero_tbl) > 30:
            lines.append(f"| …（其余 {len(zero_tbl) - 30} 个见 CSV） | | |")
    lines.append("")
    lines.append(f"- 明细：`{args.zero_out}`")
    lines.append("")

    lines.append("## 4. 非有限值")
    lines.append("")
    lines.append(f"- NaN / inf 总数：**{nonfinite}**")
    lines.append("")

    lines.append("## 5. 与 D16 基线的一致性")
    lines.append("")
    if baseline is None or baseline.get("n_cases", 0) == 0:
        lines.append("- 未找到可比的基线（`features_10.csv` 缺失或无交集），跳过。")
    else:
        lines.append(f"- 比对病例：**{baseline['n_cases']}** 例（`features_all` ∩ `features_10`）；"
                     f"列数 {baseline['n_cols']}")
        lines.append(f"- 最大相对差：**{baseline['max_rel']:.3e}**；最大绝对差：{baseline['max_abs']:.3e}")
        lines.append(f"- 相对差 > {CONSISTENCY_TOL:g} 的列：**{baseline['n_cols_over_tol']}**")
        if baseline["top_cols"]:
            lines.append("")
            lines.append("| feature | max_rel |")
            lines.append("|---|---:|")
            for col, val in baseline["top_cols"]:
                lines.append(f"| {col} | {val:.3e} |")
    lines.append("")

    lines.append("## 6. 并行一致性")
    lines.append("")
    if parallel is None:
        lines.append("- 未找到 `speed_j1.csv` / `speed_j2.csv`，跳过。")
    elif parallel.get("n_cases", 0) == 0:
        lines.append("- 两份结果无共同病例，跳过。")
    else:
        lines.append(f"- 比对病例：**{parallel['n_cases']}** 例（`speed_j1` vs `speed_j2`）")
        lines.append(f"- 最大相对差：**{parallel['max_rel']:.3e}**；最大绝对差：{parallel['max_abs']:.3e}")
        lines.append(f"- 相对差 > {CONSISTENCY_TOL:g} 的列：**{parallel['n_cols_over_tol']}**")
    lines.append("")

    lines.append("## 7. 分布可视化")
    lines.append("")
    if hist_cols:
        lines.append(f"- 随机抽取 {len(hist_cols)} 个特征（seed={args.seed}）：")
        for col in hist_cols:
            lines.append(f"  - `{col}`")
        lines.append(f"- 图：`{args.hist_out}`")
    else:
        lines.append("- 所有列均无方差，未作图。")
    lines.append("")

    lines.append("## 8. 特征构成")
    lines.append("")
    lines.append("| 影像类型 | 特征类 | 数量 |")
    lines.append("|---|---|---:|")
    for (image_type, feature_class), n in sorted(breakdown.items()):
        lines.append(f"| {image_type} | {feature_class} | {n} |")
    lines.append("")
    if timing is not None and "n_features" in timing.columns:
        vals = timing["n_features"].dropna().unique()
        lines.append(f"- 每例特征数：{sorted(int(v) for v in vals)}（应与上表合计一致）")
        lines.append("")

    lines.append("## 9. 结论")
    lines.append("")
    problems = []
    if len(missing):
        problems.append(f"{len(missing)} 例缺失（见 §1）")
    if len(zero_tbl):
        problems.append(f"{len(zero_tbl)} 个零方差列建议剔除（见 §3）")
    if len(high_missing):
        problems.append(f"{len(high_missing)} 个列缺失率超过阈值（见 §2）")
    if baseline and baseline.get("max_rel", 0) > CONSISTENCY_TOL:
        problems.append(f"与 D16 基线最大相对差 {baseline['max_rel']:.2e} 超出浮点误差")
    if problems:
        lines.append("- 需要复核：" + "；".join(problems))
    else:
        lines.append("- 行数、缺失、零方差与一致性检查均通过。")
    lines.append("")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- 主流程
def main() -> None:
    ap = argparse.ArgumentParser(description="Day17 特征表质控")
    ap.add_argument("--features", default="results/tables/features_all.csv")
    ap.add_argument("--timing", default="results/tables/features_all_timing.csv")
    ap.add_argument("--failures", default="results/tables/features_all_failures.csv")
    ap.add_argument("--index", default="results/tables/index.csv")
    ap.add_argument("--raw-root", default="data/raw/full")
    ap.add_argument("--baseline", default="results/tables/features_10.csv")
    ap.add_argument("--parallel-a", default="results/tables/speedtest/speed_j1.csv")
    ap.add_argument("--parallel-b", default="results/tables/speedtest/speed_j2.csv")
    ap.add_argument("--missing-threshold", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=17)
    ap.add_argument("--n-hist", type=int, default=6)
    ap.add_argument("--missing-out", default="results/tables/feature_missing_rate.csv")
    ap.add_argument("--zero-out", default="results/tables/feature_zero_variance.csv")
    ap.add_argument("--missing-patients-out", default="results/tables/qc_missing_patients.csv")
    ap.add_argument("--hist-out", default="results/figures/qc/hist_random6.png")
    ap.add_argument("--out", default="results/tables/features_qc.md")
    args = ap.parse_args()

    feats = load_features(Path(args.features))
    timing = load_optional(Path(args.timing))
    failures = load_optional(Path(args.failures))
    baseline_df = load_optional(Path(args.baseline))
    par_a = load_optional(Path(args.parallel_a))
    par_b = load_optional(Path(args.parallel_b))

    expected = expected_patients(Path(args.index), Path(args.raw_root))
    have = set(feats["PatientID"].astype(str))
    missing = missing_reasons(expected, have, Path(args.raw_root), failures)

    num = numeric_block(feats)
    miss_tbl = missing_table(num)
    zero_tbl = zero_variance_table(num)
    breakdown = feature_breakdown(feats.columns)

    Path(args.missing_out).parent.mkdir(parents=True, exist_ok=True)
    miss_tbl.to_csv(args.missing_out, index=False)
    zero_tbl.to_csv(args.zero_out, index=False)
    missing.to_csv(args.missing_patients_out, index=False)

    baseline = compare_tables(feats, baseline_df, "features_all vs features_10") if baseline_df is not None else None
    parallel = compare_tables(par_a, par_b, "speed_j1 vs speed_j2") if (par_a is not None and par_b is not None) else None

    hist_cols = plot_random_histograms(num, Path(args.hist_out), args.n_hist, args.seed)

    report = build_report(
        args, feats, num, timing, failures, expected, missing, miss_tbl, zero_tbl,
        baseline, parallel, hist_cols, breakdown,
    )
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(report, encoding="utf-8")

    # ---------------- 控制台摘要 ----------------
    n_features = feats.shape[1] - 1
    nonfinite = int(np.sum(~np.isfinite(num.to_numpy(dtype=float))))
    high_missing = miss_tbl[miss_tbl["missing_rate"] > args.missing_threshold]
    print("==== QC ====")
    print(f"应有 {len(expected)} 例，实际 {len(feats)} 行；缺例 {len(missing)} 例")
    print(f"特征数/例: {n_features}；非有限值: {nonfinite}")
    print(f"缺失率 > {args.missing_threshold:.0%}: {len(high_missing)} 列；"
          f"零方差/全缺失: {len(zero_tbl)} 列")
    if baseline and baseline.get("n_cases"):
        print(f"与 features_10 比对 {baseline['n_cases']} 例，"
              f"最大相对差 {baseline['max_rel']:.3e}")
    if parallel and parallel.get("n_cases"):
        print(f"speed_j1 vs speed_j2 比对 {parallel['n_cases']} 例，"
              f"最大相对差 {parallel['max_rel']:.3e}")
    print(f"报告: {args.out}")
    print(f"缺例清单: {args.missing_patients_out}")
    print(f"缺失率明细: {args.missing_out}")
    print(f"零方差明细: {args.zero_out}")
    print(f"直方图: {args.hist_out}")

    if len(feats) != len(expected):
        raise SystemExit(f"行数不符：实际 {len(feats)} != 应有 {len(expected)}（见报告 §1）")


if __name__ == "__main__":
    main()
