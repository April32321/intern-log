"""13_report_figures.py

报告用图（只读现有产物，不重跑 09 的主流程）：

  1. results/figures/report/qc_survival_time.png
     生存时间分布质控图（事件/删失分层 + 累积事件曲线）。
  2. results/figures/report/km_risktable_<model>.png
     折外 KM（repeat 0）重绘，带 at-risk 风险表。读 oof_predictions.csv，
     不重新拟合模型；图形内容与 09 的 km_oof_* 一致，只多一张风险表。
  3. results/figures/report/calibration_1y_2y.png
     1 年 / 2 年生存率的折外校准图。按 09 的 signature 折内流程
     （训练折 StandardScaler + penalizer 0.1 Cox）在固定 5×10 折上重新拟合，
     得到每折基线生存函数；每例取 10 个 repeat 的平均预测，按十分位分组，
     与该组 KM 观测值比较。
  4. results/figures/report/binwidth_sensitivity.png
     binWidth 10 / 25 / 50 的 C-index 三点图（路线 1 与路线 2）。
     数据来自各次运行的 perf.csv / cv_folds.csv；缺失的口径自动跳过并标注。

约定：
  - 全英文标签，避免中文字体缺失导致的乱码；
  - mean ± SD 的误差线在图中写明是折间 SD，不是 95% CI；
  - 不写死任何结论数字，所有数值从产物读取。
"""
from __future__ import annotations

import argparse
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter, KaplanMeierFitter
from lifelines.plotting import add_at_risk_counts
from lifelines.statistics import logrank_test
from sklearn.preprocessing import StandardScaler

ROOT = Path("/home/jiaqiwang/nsclc-cox")
ANALYSIS = ROOT / "results/tables/analysis_set.csv"
FEATURES = ROOT / "results/tables/features_all.csv"
ASSIGNMENT = ROOT / "results/tables/cv_assignment.csv"
OOF = ROOT / "results/tables/oof_predictions.csv"

SIGNATURE_FEATURES = [
    "original_firstorder_Energy",
    "original_shape_Compactness2_derived",
    "original_glrlm_GrayLevelNonUniformity",
    "wavelet-HLH_glrlm_GrayLevelNonUniformity",
]

MODELS = ["clinical", "signature", "lasso", "combined"]
COLORS = {"clinical": "#4a5568", "signature": "#2b6cb0",
          "lasso": "#c53030", "combined": "#2f855a"}

# (label, binWidth, perf.csv, cv_folds.csv or None)
BINWIDTH_RUNS = {
    "signature": [
        ("10", 10, ROOT / "results/cache/sens_bw10_sig/perf.csv", None),
        ("25", 25, ROOT / "results/tables/perf.csv", None),
        ("50", 50, ROOT / "results/cache/sens_bw50_sig/perf.csv", None),
    ],
    "lasso": [
        ("10", 10, ROOT / "results/cache/sens_bw10/perf.csv",
         ROOT / "results/cache/sens_bw10/cv_folds.csv"),
        ("25", 25, ROOT / "results/tables/perf.csv",
         ROOT / "results/tables/cv_folds.csv"),
        ("50", 50, ROOT / "results/cache/sens_bw50/perf.csv",
         ROOT / "results/cache/sens_bw50/cv_folds.csv"),
    ],
}


def load_base() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    analysis = pd.read_csv(ANALYSIS)
    features = pd.read_csv(FEATURES)
    assignment = pd.read_csv(ASSIGNMENT)
    for frame in (analysis, features, assignment):
        frame["PatientID"] = frame["PatientID"].astype(str)
    missing = [c for c in SIGNATURE_FEATURES if c not in features.columns]
    if missing:
        raise SystemExit(f"特征表缺少 signature 列: {missing}")
    df = analysis.merge(
        features[["PatientID"] + SIGNATURE_FEATURES],
        on="PatientID", how="inner", validate="one_to_one",
    ).sort_values("PatientID").reset_index(drop=True)
    if len(df) != len(analysis):
        raise SystemExit(f"合并后行数异常: {len(df)} != {len(analysis)}")
    return df, features, assignment


# ---------------------------------------------------------------- 1. QC
def fig_survival_qc(df: pd.DataFrame, out: Path) -> Path:
    time = df["Survival.time"].astype(float)
    event = df["deadstatus.event"].astype(int)
    n, n_ev = len(df), int(event.sum())

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.2))

    ax = axes[0]
    upper = float(np.ceil(time.max() / 120.0) * 120.0)
    bins = np.arange(0, upper + 120, 120)
    ax.hist([time[event == 1], time[event == 0]], bins=bins, stacked=True,
            color=["#c53030", "#a0aec0"],
            label=[f"death (n={n_ev})", f"censored (n={n - n_ev})"])
    ax.set_xlabel("Follow-up time (days)")
    ax.set_ylabel("Number of patients")
    ax.set_title("A. Follow-up distribution")
    ax.legend(frameon=False, fontsize=9)
    ax.grid(axis="y", alpha=0.25)

    ax = axes[1]
    kmf = KaplanMeierFitter().fit(time, event, label="all patients")
    ax.step(kmf.survival_function_.index,
            1.0 - kmf.survival_function_.iloc[:, 0],
            where="post", color="#2b6cb0", linewidth=1.6)
    ax.set_xlabel("Time since treatment (days)")
    ax.set_ylabel("Cumulative incidence of death")
    ax.set_title("B. 1 - KM (events accumulate)")
    ax.set_ylim(0, 1.02)
    ax.grid(alpha=0.25)
    median_ev = float(kmf.median_survival_time_)
    ax.axhline(0.5, color="grey", linestyle="--", linewidth=1)
    if np.isfinite(median_ev):
        ax.axvline(median_ev, color="grey", linestyle=":", linewidth=1)
        ax.annotate(f"median OS = {median_ev:.0f} d",
                    xy=(median_ev, 0.52), xytext=(median_ev + 80, 0.62),
                    fontsize=9,
                    arrowprops={"arrowstyle": "-", "color": "grey"})

    fig.suptitle(
        f"Survival time distribution (n={n}, events={n_ev}, "
        f"censored={n - n_ev})", fontsize=10,
    )
    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------------------------------------------------------------- 2. KM + risk table
def fig_km_risktable(oof: pd.DataFrame, model: str, repeat: int,
                     out: Path) -> Path | None:
    sub = oof[(oof["model"] == model) & (oof["repeat"] == repeat)].copy()
    if sub.empty:
        return None
    sub["high_risk"] = sub["high_risk"].astype(bool)
    if sub["high_risk"].all() or (~sub["high_risk"]).all():
        return None

    fig, ax = plt.subplots(figsize=(7.0, 5.4))
    fitted = []
    for flag, label, color in ((False, "Low risk", "#2b6cb0"),
                               (True, "High risk", "#c53030")):
        group = sub[sub["high_risk"] == flag]
        kmf = KaplanMeierFitter().fit(
            group["time"], group["event"],
            label=f"{label} (n={len(group)})",
        )
        kmf.plot_survival_function(ax=ax, ci_show=False, color=color,
                                   linewidth=1.6)
        fitted.append(kmf)

    p_value = float(logrank_test(
        sub.loc[sub["high_risk"], "time"],
        sub.loc[~sub["high_risk"], "time"],
        sub.loc[sub["high_risk"], "event"],
        sub.loc[~sub["high_risk"], "event"],
    ).p_value)

    add_at_risk_counts(*fitted, ax=ax, fontsize=8)
    ax.set_xlabel("Time (days)")
    ax.set_ylabel("Overall survival")
    ax.set_ylim(0, 1.02)
    ax.set_xlim(0, float(sub["time"].max()) * 1.02)
    ax.set_title(
        f"{model}: out-of-fold KM with numbers at risk "
        f"(repeat {repeat}, log-rank p={p_value:.3g})", fontsize=10,
    )
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------------------------------------------------------------- 3. 校准
def fit_fold_survival(train: pd.DataFrame, test: pd.DataFrame,
                      times: list[float]) -> pd.DataFrame:
    scaler = StandardScaler().fit(train[SIGNATURE_FEATURES].to_numpy(float))
    cols = SIGNATURE_FEATURES
    tr = pd.DataFrame(
        scaler.transform(train[cols].to_numpy(float)),
        columns=cols, index=train.index,
    )
    te = pd.DataFrame(
        scaler.transform(test[cols].to_numpy(float)),
        columns=cols, index=test.index,
    )
    tr["T"] = train["Survival.time"].astype(float).to_numpy()
    tr["event"] = train["deadstatus.event"].astype(int).to_numpy()

    last_exc: Exception | None = None
    for penalizer in (0.1, 1.0, 10.0):
        try:
            cph = CoxPHFitter(penalizer=penalizer)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                cph.fit(tr, duration_col="T", event_col="event")
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                surv = cph.predict_survival_function(
                    te[cols], times=times,
                )
            return surv
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
    raise RuntimeError(f"Cox 拟合失败: {last_exc}")


def fig_calibration(df: pd.DataFrame, assignment: pd.DataFrame,
                    times: list[float], repeats: int,
                    n_bins: int, out: Path) -> tuple[Path, pd.DataFrame]:
    preds: dict[str, dict[float, list[float]]] = {
        pid: {t: [] for t in times} for pid in df["PatientID"]
    }

    for repeat in range(repeats):
        sub = assignment[assignment["repeat"] == repeat]
        if sub.empty:
            raise SystemExit(f"cv_assignment 缺少 repeat={repeat}")
        for fold in sorted(sub["fold"].unique()):
            test_ids = set(sub.loc[sub["fold"] == fold, "PatientID"])
            test = df[df["PatientID"].isin(test_ids)]
            train = df[~df["PatientID"].isin(test_ids)]
            if len(train) + len(test) != len(df):
                raise SystemExit(f"repeat={repeat} fold={fold} 覆盖异常")
            surv = fit_fold_survival(train, test, times)
            for idx, pid in zip(test.index, test["PatientID"]):
                for t in times:
                    preds[pid][t].append(float(surv.loc[t, idx]))
        print(f"  calibration repeat {repeat + 1}/{repeats} 完成", flush=True)

    rows = []
    for pid in df["PatientID"]:
        row = {"PatientID": pid}
        for t in times:
            row[f"pred_{int(t)}"] = float(np.mean(preds[pid][t]))
        rows.append(row)
    pred_df = pd.DataFrame(rows)
    merged = df.merge(pred_df, on="PatientID", how="left",
                      validate="one_to_one")

    # 自检：用平均预测生存率反推的风险排序，C-index 应接近 09 的 signature 结果
    from sksurv.metrics import concordance_index_censored
    for t in times:
        ci = concordance_index_censored(
            merged["deadstatus.event"].astype(bool),
            merged["Survival.time"].astype(float),
            -merged[f"pred_{int(t)}"].to_numpy(float),
        )[0]
        print(f"  自检：{int(t)} 天平均预测的 C-index = {ci:.3f}", flush=True)

    fig, axes = plt.subplots(1, len(times), figsize=(5.4 * len(times), 4.8))
    if len(times) == 1:
        axes = [axes]
    summary_rows = []

    for ax, t in zip(axes, times):
        col = f"pred_{int(t)}"
        merged["_bin"] = pd.qcut(
            merged[col].rank(method="first"), n_bins, labels=False,
        )
        xs, ys, los, his, ns = [], [], [], [], []
        for b in range(n_bins):
            group = merged[merged["_bin"] == b]
            if group.empty:
                continue
            kmf = KaplanMeierFitter().fit(
                group["Survival.time"].astype(float),
                group["deadstatus.event"].astype(int),
            )
            obs = float(kmf.predict(t))
            ci = kmf.confidence_interval_survival_function_
            lo = float(ci.iloc[:, 0].loc[ci.index <= t].iloc[-1])
            hi = float(ci.iloc[:, 1].loc[ci.index <= t].iloc[-1])
            xs.append(float(group[col].mean()))
            ys.append(obs)
            los.append(obs - lo)
            his.append(hi - obs)
            ns.append(len(group))
            summary_rows.append({
                "horizon_days": int(t), "bin": b + 1, "n": len(group),
                "predicted_mean": float(group[col].mean()),
                "observed_km": obs, "ci_lower": lo, "ci_upper": hi,
            })

        ax.errorbar(xs, ys, yerr=[los, his], fmt="o", color="#2b6cb0",
                    ecolor="#4a5568", elinewidth=1.0, capsize=3,
                    markersize=5, label="decile (KM ± 95% CI)")
        ax.plot([0, 1], [0, 1], linestyle="--", color="grey", linewidth=1,
                label="perfect calibration")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xlabel(f"Predicted {int(t / 365)}-year survival")
        ax.set_ylabel(f"Observed {int(t / 365)}-year survival (KM)")
        ax.set_title(f"{int(t / 365)}-year calibration")
        ax.legend(frameon=False, fontsize=8, loc="upper left")
        ax.grid(alpha=0.25)

    fig.suptitle(
        f"Out-of-fold calibration, fixed 4-feature signature "
        f"(n={len(merged)}, {repeats} repeats averaged, {n_bins} deciles)",
        fontsize=10,
    )
    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    pts = pd.DataFrame(summary_rows)
    for t, grp in pts.groupby("horizon_days"):
        ici = float(np.average(np.abs(grp["observed_km"] -
                                      grp["predicted_mean"]),
                               weights=grp["n"]))
        print(f"  校准自检：{int(t)} 天 ICI（|观测-预测| 加权均值）= {ici:.3f}",
              flush=True)
    return out, pts


# ---------------------------------------------------------------- 4. binWidth
def _perf_row(path: Path, model: str) -> pd.Series | None:
    if not path.exists():
        return None
    perf = pd.read_csv(path)
    hit = perf[perf["model"] == model]
    return None if hit.empty else hit.iloc[0]


def fig_binwidth(out: Path) -> tuple[Path, list[str]]:
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.4), sharey=True)
    notes: list[str] = []

    for ax, model in zip(axes, ("signature", "lasso")):
        xs, values, sds = [], [], []
        for label, bw, perf_path, folds_path in BINWIDTH_RUNS[model]:
            row = _perf_row(perf_path, model)
            if row is None:
                notes.append(f"{model} bw{bw}: 缺少 {perf_path}")
                ax.annotate("bw=50: pending", xy=(50, 0.5),
                            ha="center", fontsize=8, color="grey",
                            rotation=90)
                continue
            xs.append(bw)
            values.append(float(row["cindex_mean"]))
            sds.append(float(row["cindex_sd"]))

            if folds_path is not None and folds_path.exists():
                folds = pd.read_csv(folds_path)
                vals = folds.loc[folds["model"] == model, "cindex"].to_numpy(float)
                jitter = np.linspace(-1.6, 1.6, len(vals))
                ax.scatter(np.full(len(vals), bw) + jitter, vals,
                           s=7, alpha=0.35, color=COLORS[model],
                           linewidths=0)

        if not xs:
            ax.set_title(f"{model}: no data")
            continue

        ax.errorbar(xs, values, yerr=sds, fmt="o-", color=COLORS[model],
                    ecolor="#4a5568", elinewidth=1.1, capsize=4,
                    markersize=6, linewidth=1.4)
        for x, y in zip(xs, values):
            ax.annotate(f"{y:.3f}", xy=(x, y), xytext=(0, 8),
                        textcoords="offset points", ha="center", fontsize=8)
        ax.axhline(0.5, color="grey", linestyle="--", linewidth=1)
        ax.set_xticks([10, 25, 50])
        ax.set_xlim(2, 58)
        ax.set_title(f"{model}: C-index vs binWidth")
        ax.set_xlabel("Grey-level bin width (HU)")
        ax.grid(axis="y", alpha=0.25)

    axes[0].set_ylabel("C-index (outer test folds, mean ± SD)")
    fig.suptitle(
        "binWidth sensitivity, fixed 5×10 folds "
        "(error bars = fold-to-fold SD, not 95% CI)", fontsize=10,
    )
    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out, notes


# ---------------------------------------------------------------- 5. 数据预览
def fig_data_preview(patients: list[str], raw_root: Path, out: Path) -> Path:
    """CT 切片 + GTV-1 轮廓预览，替代人工 viewer 截图（可复现）。"""
    import importlib.util

    import SimpleITK as sitk

    spec = importlib.util.spec_from_file_location(
        "extract05", ROOT / "code/05_extract_features.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    index = pd.read_csv(ROOT / "results/tables/index.csv")
    index["PatientID"] = index["PatientID"].astype(str)

    n_rows = len(patients)
    fig, axes = plt.subplots(n_rows, 2, figsize=(10.5, 3.6 * n_rows),
                             squeeze=False)

    for row_i, pid in enumerate(patients):
        hit = index[index["PatientID"] == pid]
        if hit.empty:
            axes[row_i, 0].set_axis_off()
            axes[row_i, 0].set_title(f"{pid}: not in index")
            axes[row_i, 1].set_axis_off()
            continue
        row = hit.iloc[0]
        image = mod.read_series(raw_root / str(row["series_dir"]))
        roi_names, contours = mod.read_rtstruct(
            raw_root / str(row["rtstruct_path"]))
        roi_num, _ = mod.pick_gtv(roi_names, set(contours))
        if roi_num is None:
            raise SystemExit(f"{pid}: 未匹配到 GTV")
        mask = mod.build_mask(contours[roi_num], image)
        arr = sitk.GetArrayFromImage(image).astype(float)
        sx, sy, sz = image.GetSpacing()

        k = int(mask.sum(axis=(1, 2)).argmax())
        j = int(mask.sum(axis=(0, 2)).argmax())

        def mm_ticks(ax, n, spacing, axis):
            ticks = np.linspace(0, n - 1, 5).round().astype(int)
            labels = [f"{t * spacing:.0f}" for t in ticks]
            if axis == "x":
                ax.set_xticks(ticks)
                ax.set_xticklabels(labels)
            else:
                ax.set_yticks(ticks)
                ax.set_yticklabels(labels)

        ax = axes[row_i, 0]
        ax.imshow(arr[k], cmap="gray", vmin=-1000, vmax=400,
                  aspect=sy / sx)
        ax.contour(mask[k], levels=[0.5], colors="#ff3b30", linewidths=1.2)
        mm_ticks(ax, arr.shape[2], sx, "x")
        mm_ticks(ax, arr.shape[1], sy, "y")
        ax.set_title(
            f"{pid} - axial (z={k}, thickness={sz:.1f} mm)\n"
            f"GTV-1 volume = {mask.sum() * sx * sy * sz / 1000:.1f} cm3",
            fontsize=8,
        )
        ax.set_xlabel("x (mm)")
        ax.set_ylabel("y (mm)")

        ax = axes[row_i, 1]
        ax.imshow(arr[:, j, :], cmap="gray", vmin=-1000, vmax=400,
                  aspect=sz / sx)
        ax.contour(mask[:, j, :], levels=[0.5], colors="#ff3b30",
                   linewidths=1.2)
        mm_ticks(ax, arr.shape[2], sx, "x")
        mm_ticks(ax, arr.shape[0], sz, "y")
        ax.set_title(f"{pid} - coronal (y={j})", fontsize=8)
        ax.set_xlabel("x (mm)")
        ax.set_ylabel("z (mm)")

    fig.suptitle(
        "Input data preview: CT with GTV-1 contour (window: -1000..400 HU)",
        fontsize=10,
    )
    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------------------------------------------------------------- main
def main() -> None:
    ap = argparse.ArgumentParser(description="报告用图（只读现有产物）")
    ap.add_argument("--out-dir", default="results/figures/report")
    ap.add_argument("--repeats", type=int, default=10)
    ap.add_argument("--calibration-bins", type=int, default=10)
    ap.add_argument("--skip-calibration", action="store_true")
    ap.add_argument("--km-repeat", type=int, default=0)
    ap.add_argument("--skip-preview", action="store_true")
    ap.add_argument("--preview-patients", nargs="*",
                    default=["LUNG1-001", "LUNG1-003"])
    ap.add_argument("--raw-root", default="/home/jiaqiwang/tcia/full")
    args = ap.parse_args()

    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    print("[1/5] 生存时间分布")
    df, _, assignment = load_base()
    print("  ", fig_survival_qc(df, out_dir / "qc_survival_time.png"))

    print("[2/5] KM + 风险表")
    oof = pd.read_csv(OOF)
    oof["PatientID"] = oof["PatientID"].astype(str)
    for model in MODELS:
        path = out_dir / f"km_risktable_{model}.png"
        made = fig_km_risktable(oof, model, args.km_repeat, path)
        if made is not None:
            print("  ", made)

    if not args.skip_calibration:
        print("[3/5] 1y/2y 校准图（按 09 的 signature 流程重拟合）")
        path, summary = fig_calibration(
            df, assignment, [365.0, 730.0], args.repeats,
            args.calibration_bins, out_dir / "calibration_1y_2y.png",
        )
        print("  ", path)
        summary.to_csv(out_dir / "calibration_points.csv", index=False)
        print("  ", out_dir / "calibration_points.csv")

    print("[4/5] binWidth 敏感性")
    path, notes = fig_binwidth(out_dir / "binwidth_sensitivity.png")
    print("  ", path)
    for note in notes:
        print("   [skip]", note)

    if not args.skip_preview:
        print("[5/5] 数据预览（CT + GTV-1 轮廓）")
        print("  ", fig_data_preview(
            args.preview_patients, Path(args.raw_root),
            out_dir / "data_preview_ct_gtv.png",
        ))


if __name__ == "__main__":
    main()
