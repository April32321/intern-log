"""Day 18：固定折上的 Cox 模型评估（临床 / 签名 / LASSO-Cox / 联合）

输入：
  results/tables/analysis_set.csv      # 07 固定的 399 例
  results/tables/features_all.csv      # 422 × 537 影像特征
  results/tables/feature_columns.txt   # 锁定的 537 个特征列
  results/tables/cv_assignment.csv     # 08 固定的 5×10 测试折

输出（默认 results/tables/）：
  cv_folds.csv             # 每折每模型的 C-index / log-rank / 特征数 / alpha
  oof_predictions.csv      # 每例每轮的折外 risk 与折内高低危标签
  selection_stability.csv  # LASSO 特征被选中的折数与平均系数
  cv_coefficients.csv      # 每折每模型的最终 Cox 系数、SE 与 95% CI（森林图数据源）
  coefficient_summary.csv  # 系数跨折汇总（分位 + 逆方差合并 HR / 95% CI）
  perf.csv                 # 每个模型的均值 ± SD 汇总
  perf.md                  # 人类可读的汇总、口径与限制

输出（默认 results/figures/cv/）：
  cindex_boxplot.png              # 四个模型 50 折 C-index 分布
  km_oof_<model>_repeat<N>.png    # 单个 repeat 的折外 KM
  forest_<model>.png              # 逐折 Cox 系数的森林图

原则：
  - 外层折固定，不重新切分；
  - 所有预处理、特征选择、alpha 选择只使用当前训练折；
  - 外层验证折只用于 predict 与打分；
  - 路线 2 的 alpha 由内层 5 折选择，内层同样重做特征筛选；
  - 跨折合并 KM 不使用原始 partial hazard，而使用折内训练集中位数定义的高低危标签，
    避免不同折的基线风险尺度混在一起。
"""

from __future__ import annotations

import argparse
import time
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter, KaplanMeierFitter
from lifelines.statistics import logrank_test
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sksurv.linear_model import CoxnetSurvivalAnalysis
from sksurv.metrics import concordance_index_censored
from sksurv.util import Surv

# 路线 1：论文 signature 的 4 个代表性特征
# Compactness2 在 PyRadiomics 3.0.1 中带 _derived 后缀
SIGNATURE_FEATURES = [
    "original_firstorder_Energy",
    "original_shape_Compactness2_derived",
    "original_glrlm_GrayLevelNonUniformity",
    "wavelet-HLH_glrlm_GrayLevelNonUniformity",
]

# 组织学 dummy：adeno 为参考组
HIST_DUMMIES = ["squamous", "large", "nos", "unknown"]

MODEL_CHOICES = ["clinical", "signature", "lasso", "combined"]


# ---------------------------------------------------------------- 数据
def load_data(args) -> tuple[pd.DataFrame, list[str], np.ndarray, pd.DataFrame]:
    analysis = pd.read_csv(args.analysis)
    features = pd.read_csv(args.features)
    feature_cols = pd.read_csv(args.feature_columns, header=None)[0].tolist()
    assignment = pd.read_csv(args.cv_assignment)

    if args.expect_features >= 0 and len(feature_cols) != args.expect_features:
        raise SystemExit(
            f"特征数不符: {len(feature_cols)} != {args.expect_features}"
        )
    missing = [c for c in feature_cols if c not in features.columns]
    if missing:
        raise SystemExit(f"feature_columns.txt 中的列不在特征表里: {missing[:10]}")

    analysis["PatientID"] = analysis["PatientID"].astype(str)
    features["PatientID"] = features["PatientID"].astype(str)
    if not analysis["PatientID"].is_unique:
        raise SystemExit("analysis_set PatientID 不唯一")

    df = analysis.merge(
        features[["PatientID"] + feature_cols],
        on="PatientID", how="inner", validate="one_to_one",
    )
    if len(df) != len(analysis):
        raise SystemExit(f"合并后行数异常: {len(df)} != {len(analysis)}")
    if args.expect_n >= 0 and len(df) != args.expect_n:
        raise SystemExit(f"分析集例数不符: {len(df)} != {args.expect_n}")

    df = df.sort_values("PatientID").reset_index(drop=True)
    if not set(df["deadstatus.event"].unique()) <= {0, 1}:
        raise SystemExit("deadstatus.event 取值异常")
    events = int(df["deadstatus.event"].sum())
    if args.expect_events >= 0 and events != args.expect_events:
        raise SystemExit(f"事件数不符: {events} != {args.expect_events}")

    y = Surv.from_arrays(
        df["deadstatus.event"].astype(bool),
        df["Survival.time"].astype(float),
    )

    assignment["PatientID"] = assignment["PatientID"].astype(str)
    if not set(assignment["PatientID"]) == set(df["PatientID"]):
        raise SystemExit("cv_assignment 与分析集病例集合不一致")
    return df, feature_cols, y, assignment


def iter_folds(df: pd.DataFrame, assignment: pd.DataFrame,
               repeats: int, n_splits: int):
    ids = df["PatientID"].to_numpy()
    pos = {pid: i for i, pid in enumerate(ids)}
    all_ids = set(ids)

    for repeat in range(repeats):
        sub = assignment[assignment["repeat"] == repeat]
        if sub.empty:
            raise SystemExit(f"cv_assignment 缺少 repeat={repeat}")

        counts = sub.groupby("PatientID").size()
        if not (counts == 1).all() or len(counts) != len(df):
            raise SystemExit(f"repeat={repeat} 的测试折未做到每例恰好一次")
        if sub["fold"].nunique() != n_splits:
            raise SystemExit(
                f"repeat={repeat} 的折数异常: "
                f"{sub['fold'].nunique()} != {n_splits}"
            )

        for fold in sorted(sub["fold"].unique()):
            test_ids = set(sub.loc[sub["fold"] == fold, "PatientID"])
            train_ids = all_ids - test_ids
            if train_ids & test_ids:
                raise SystemExit(f"repeat={repeat} fold={fold}: 训练/测试有交集")
            if len(train_ids | test_ids) != len(df):
                raise SystemExit(f"repeat={repeat} fold={fold}: 未覆盖全部病例")
            yield (
                int(repeat), int(fold),
                np.array([pos[p] for p in sorted(train_ids)], dtype=int),
                np.array([pos[p] for p in sorted(test_ids)], dtype=int),
            )


def clinical_matrix(frame: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=frame.index)
    out["age"] = frame["age"].astype(float)
    out["gender_num"] = frame["gender_num"].astype(int)
    out["stage_bin"] = frame["stage_bin"].astype(int)
    for level in HIST_DUMMIES:
        out[f"hist_{level}"] = (frame["histology"] == level).astype(int)
    return out


# ---------------------------------------------------------------- Cox
def fit_cox(X: pd.DataFrame, y: np.ndarray) -> CoxPHFitter:
    data = X.astype(float).copy()
    data["T"] = y["time"]
    data["event"] = y["event"].astype(int)

    last_exc: Exception | None = None
    for penalizer in (0.1, 1.0, 10.0):
        try:
            cph = CoxPHFitter(penalizer=penalizer)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                cph.fit(data, duration_col="T", event_col="event")
            return cph
        except Exception as exc:  # noqa: BLE001 - 保留最后一次异常
            last_exc = exc
    raise RuntimeError(f"Cox 拟合失败: {last_exc}")


def predict_cox(cph: CoxPHFitter, X: pd.DataFrame) -> np.ndarray:
    risk = cph.predict_partial_hazard(X.astype(float)).to_numpy(dtype=float)
    if not np.isfinite(risk).all():
        raise RuntimeError("Cox 预测出现 NaN/inf")
    return risk


# ---------------------------------------------------------------- 折内筛选
def correlation_filter(X: pd.DataFrame, threshold: float) -> list[str]:
    order = X.var().sort_values(ascending=False).index.tolist()
    corr = X[order].corr().abs()
    keep: list[str] = []
    for col in order:
        if all(corr.loc[col, kept] <= threshold for kept in keep):
            keep.append(col)
    return keep


def univariate_pvalues(X: pd.DataFrame, y: np.ndarray) -> dict[str, float]:
    pvals: dict[str, float] = {}
    for col in X.columns:
        data = pd.DataFrame({
            "T": y["time"],
            "event": y["event"].astype(int),
            "x": X[col].to_numpy(dtype=float),
        })
        try:
            cph = CoxPHFitter(penalizer=0.01)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                cph.fit(data, duration_col="T", event_col="event")
            pvals[col] = float(cph.summary.loc["x", "p"])
        except Exception:  # noqa: BLE001 - 单变量失败按不显著处理
            pvals[col] = 1.0
    return pvals


def feature_pipeline(Xtr: pd.DataFrame, ytr: np.ndarray, args) \
        -> tuple[pd.DataFrame, StandardScaler, list[str], dict[str, float], dict]:
    """在训练折上完成：方差 → 相关 → 单变量 Cox → 标准化。"""
    n_start = Xtr.shape[1]

    std = Xtr.std(axis=0)
    var_keep = std[std > 0].index.tolist()
    if not var_keep:
        raise RuntimeError("训练折所有特征均为常数")
    Xtr = Xtr[var_keep]
    n_var = Xtr.shape[1]

    corr_keep = correlation_filter(Xtr, args.corr_threshold)
    if not corr_keep:
        raise RuntimeError("相关过滤后没有剩余特征")
    Xtr = Xtr[corr_keep]
    n_corr = Xtr.shape[1]

    pvals = univariate_pvalues(Xtr, ytr)
    selected = [c for c in Xtr.columns if pvals[c] < args.p_threshold]
    if not selected:
        selected = sorted(pvals, key=pvals.get)[:min(args.fallback_k, len(pvals))]
    Xtr = Xtr[selected]
    n_univ = Xtr.shape[1]

    scaler = StandardScaler().fit(Xtr.to_numpy(dtype=float))
    Xtr_s = pd.DataFrame(
        scaler.transform(Xtr.to_numpy(dtype=float)),
        columns=Xtr.columns, index=Xtr.index,
    )
    diag = {
        "n_start": n_start,
        "n_var": n_var,
        "n_corr": n_corr,
        "n_univ": n_univ,
    }
    return Xtr_s, scaler, selected, pvals, diag


def alpha_grid(Xtr_s: pd.DataFrame, ytr: np.ndarray) -> np.ndarray:
    ref = CoxnetSurvivalAnalysis(
        l1_ratio=1.0, n_alphas=50, alpha_min_ratio=0.01, max_iter=100000,
    ).fit(Xtr_s.to_numpy(dtype=float), ytr)
    amax = float(np.max(ref.alphas_))
    if not np.isfinite(amax) or amax <= 0:
        raise RuntimeError(f"alpha_max 异常: {amax}")
    return np.logspace(
        np.log10(amax), np.log10(max(amax * 1e-3, 1e-12)), 30,
    )


def choose_alpha(Xtr_raw: pd.DataFrame, ytr: np.ndarray,
                 alphas: np.ndarray, seed: int, args) -> float:
    """内层 5 折选 alpha；每折重新做特征筛选与标准化，避免内层泄漏。

    候选网格由外层训练折的 alpha_max 生成，只决定候选范围，不参与打分。
    """
    inner = StratifiedKFold(
        n_splits=args.inner_splits, shuffle=True, random_state=seed,
    )
    scores = np.full((args.inner_splits, len(alphas)), np.nan)

    for j, (itr, iva) in enumerate(inner.split(Xtr_raw, ytr["event"])):
        X_in_raw = Xtr_raw.iloc[itr]
        X_val_raw = Xtr_raw.iloc[iva]
        y_in = ytr[itr]
        try:
            X_in_s, scaler, sel, _, _ = feature_pipeline(X_in_raw, y_in, args)
        except Exception:  # noqa: BLE001 - 内层失败则该折跳过
            continue
        if not sel:
            continue
        X_val_s = pd.DataFrame(
            scaler.transform(X_val_raw[sel].to_numpy(dtype=float)),
            columns=sel, index=X_val_raw.index,
        )
        try:
            model = CoxnetSurvivalAnalysis(
                l1_ratio=1.0, alphas=alphas, max_iter=100000,
            ).fit(X_in_s.to_numpy(dtype=float), y_in)
        except Exception:  # noqa: BLE001
            continue

        for k, alpha in enumerate(alphas):
            try:
                risk = model.predict(X_val_s.to_numpy(dtype=float), alpha=float(alpha))
                scores[j, k] = concordance_index_censored(
                    ytr["event"][iva], ytr["time"][iva], risk,
                )[0]
            except Exception:  # noqa: BLE001
                scores[j, k] = np.nan

    mean_scores = np.nanmean(scores, axis=0)
    if np.all(np.isnan(mean_scores)):
        return float(alphas[-1])
    return float(alphas[int(np.nanargmax(mean_scores))])


def fit_signature_fold(Xtr_raw: pd.DataFrame, Xte_raw: pd.DataFrame,
                       ytr: np.ndarray) -> dict:
    scaler = StandardScaler().fit(Xtr_raw.to_numpy(dtype=float))
    Xtr_s = pd.DataFrame(
        scaler.transform(Xtr_raw.to_numpy(dtype=float)),
        columns=Xtr_raw.columns, index=Xtr_raw.index,
    )
    Xte_s = pd.DataFrame(
        scaler.transform(Xte_raw.to_numpy(dtype=float)),
        columns=Xte_raw.columns, index=Xte_raw.index,
    )
    cph = fit_cox(Xtr_s, ytr)
    return {
        "risk_train": predict_cox(cph, Xtr_s),
        "risk_test": predict_cox(cph, Xte_s),
        "n_features": len(Xtr_s.columns),
        "coef_map": {k: float(v) for k, v in cph.params_.items()},
        "cox_summary": cph.summary.copy(),
        "cox_penalizer": float(cph.penalizer),
    }


def fit_lasso_fold(Xtr_raw: pd.DataFrame, Xte_raw: pd.DataFrame,
                   ytr: np.ndarray, seed: int, args) -> dict:
    Xtr_s, scaler, selected, pvals, diag = feature_pipeline(Xtr_raw, ytr, args)
    alphas = alpha_grid(Xtr_s, ytr)
    alpha = choose_alpha(Xtr_raw, ytr, alphas, seed, args)

    lasso = CoxnetSurvivalAnalysis(
        l1_ratio=1.0, alphas=[alpha], max_iter=100000,
    ).fit(Xtr_s.to_numpy(dtype=float), ytr)
    coef = np.asarray(lasso.coef_)
    if coef.ndim == 1:
        coef = coef[:, None]
    coef = coef[:, 0]
    coef_map = {c: float(b) for c, b in zip(selected, coef)}
    picked = [c for c, b in zip(selected, coef) if abs(b) > 1e-8]

    notes = "lasso_cv"
    fallback = False
    if not picked:
        picked = sorted(selected, key=pvals.get)[
            :min(args.fallback_k, len(selected))
        ]
        notes = "lasso_empty_fallback_topk"
        fallback = True

    cph = fit_cox(Xtr_s[picked], ytr)
    risk_tr = predict_cox(cph, Xtr_s[picked])

    Xte_s = pd.DataFrame(
        scaler.transform(Xte_raw[selected].to_numpy(dtype=float)),
        columns=selected, index=Xte_raw.index,
    )
    risk_te = predict_cox(cph, Xte_s[picked])

    picked_coef = {} if fallback else {c: coef_map[c] for c in picked}
    return {
        "risk_train": risk_tr,
        "risk_test": risk_te,
        "n_features": len(picked),
        "alpha": alpha,
        "notes": notes,
        "selected": picked,
        "coef_map": coef_map,
        "picked_coef": picked_coef,
        "fallback": fallback,
        "diag": diag,
        "cox_coef": {k: float(v) for k, v in cph.params_.items()},
        "cox_summary": cph.summary.copy(),
        "cox_penalizer": float(cph.penalizer),
    }


def fit_combined_fold(Xc_tr: pd.DataFrame, Xc_te: pd.DataFrame,
                      risk_tr: np.ndarray, risk_te: np.ndarray,
                      ytr: np.ndarray) -> dict:
    score_tr = np.log(np.clip(risk_tr, 1e-12, None))
    score_te = np.log(np.clip(risk_te, 1e-12, None))
    mu = float(score_tr.mean())
    sd = float(score_tr.std(ddof=0))
    if not np.isfinite(sd) or sd <= 0:
        sd = 1.0

    Xtr = Xc_tr.copy()
    Xte = Xc_te.copy()
    Xtr["radiomics_score"] = (score_tr - mu) / sd
    Xte["radiomics_score"] = (score_te - mu) / sd

    cph = fit_cox(Xtr, ytr)
    return {
        "risk_train": predict_cox(cph, Xtr),
        "risk_test": predict_cox(cph, Xte),
        "n_features": Xtr.shape[1],
        "coef_map": {k: float(v) for k, v in cph.params_.items()},
        "cox_summary": cph.summary.copy(),
        "cox_penalizer": float(cph.penalizer),
    }


# ---------------------------------------------------------------- 评估
def evaluate_fold(risk_train: np.ndarray, risk_test: np.ndarray,
                  y_train: np.ndarray, y_test: np.ndarray) -> tuple:
    cindex_train = float(concordance_index_censored(
        y_train["event"], y_train["time"], risk_train,
    )[0])
    cindex = float(concordance_index_censored(
        y_test["event"], y_test["time"], risk_test,
    )[0])

    threshold = float(np.median(risk_train))
    high = risk_test > threshold
    if high.all() or (~high).all():
        return cindex, cindex_train, np.nan, high, threshold
    p_value = float(logrank_test(
        y_test["time"][high], y_test["time"][~high],
        y_test["event"][high], y_test["event"][~high],
    ).p_value)
    return cindex, cindex_train, p_value, high, threshold


def add_row(rows: list[dict], model: str, repeat: int, fold: int,
            n_train: int, n_test: int, n_features: int,
            cindex: float, cindex_train: float, p_value: float,
            alpha: float | None, cox_penalizer: float | None,
            diag: dict | None, notes: str) -> None:
    diag = diag or {}
    rows.append({
        "model": model,
        "repeat": repeat,
        "fold": fold,
        "n_train": n_train,
        "n_test": n_test,
        "n_features": n_features,
        "n_after_variance": diag.get("n_var", np.nan),
        "n_after_corr": diag.get("n_corr", np.nan),
        "n_after_univariate": diag.get("n_univ", np.nan),
        "alpha": np.nan if alpha is None else float(alpha),
        "cox_penalizer": (
            np.nan if cox_penalizer is None else float(cox_penalizer)
        ),
        "cindex_train": cindex_train,
        "cindex": cindex,
        "cindex_gap": cindex_train - cindex,
        "logrank_p": p_value,
        "notes": notes,
    })


def add_oof(oof_rows: list[dict], model: str, repeat: int, fold: int,
            test_df: pd.DataFrame, risk: np.ndarray,
            high_risk: np.ndarray, threshold: float) -> None:
    for pid, time, event, r, high in zip(
        test_df["PatientID"], test_df["Survival.time"],
        test_df["deadstatus.event"], risk, high_risk,
    ):
        oof_rows.append({
            "model": model,
            "repeat": repeat,
            "fold": fold,
            "PatientID": pid,
            "time": float(time),
            "event": int(event),
            "risk": float(r),
            "high_risk": bool(high),
            "risk_threshold": float(threshold),
        })


def add_coefficients(coef_rows: list[dict], model: str, repeat: int, fold: int,
                     summary: pd.DataFrame, cox_penalizer: float) -> None:
    """把单折最终 Cox 的系数、SE 与 95% CI 写入逐折系数表。

    summary 为 lifelines CoxPHFitter.summary，索引是 term，
    含 coef / se(coef) / exp(coef) lower 95% / exp(coef) upper 95%。
    """
    for term, row in summary.iterrows():
        coef = float(row["coef"])
        coef_rows.append({
            "model": model,
            "repeat": repeat,
            "fold": fold,
            "term": term,
            "coef": coef,
            "se": float(row["se(coef)"]),
            "hr": float(np.exp(coef)),
            "hr_lower95": float(row["exp(coef) lower 95%"]),
            "hr_upper95": float(row["exp(coef) upper 95%"]),
            "cox_penalizer": float(cox_penalizer),
        })


# ---------------------------------------------------------------- 汇总
def summarise(folds: pd.DataFrame, repeats: int, seed: int) -> pd.DataFrame:
    if folds.empty:
        return pd.DataFrame()
    perf = (
        folds.groupby("model")
        .agg(
            n_folds=("cindex", "count"),
            cindex_mean=("cindex", "mean"),
            cindex_sd=("cindex", "std"),
            cindex_median=("cindex", "median"),
            cindex_train_mean=("cindex_train", "mean"),
            cindex_gap_mean=("cindex_gap", "mean"),
            logrank_p_median=("logrank_p", "median"),
            logrank_pct_sig=("logrank_p", lambda s: (
                float((s.dropna() < 0.05).mean()) if s.notna().any() else np.nan
            )),
            n_features_mean=("n_features", "mean"),
            n_features_min=("n_features", "min"),
            n_features_max=("n_features", "max"),
            alpha_median=("alpha", "median"),
            alpha_min=("alpha", "min"),
            alpha_max=("alpha", "max"),
            cox_penalizer_median=("cox_penalizer", "median"),
        )
        .reset_index()
    )
    fallback = (
        folds.assign(_fb=folds["notes"].astype(str).str.contains("fallback"))
        .groupby("model")["_fb"].sum()
    )
    perf["n_fallback_folds"] = perf["model"].map(fallback).fillna(0).astype(int)
    perf["cv_scheme"] = f"5x{repeats}"
    perf["seed"] = seed
    order = [m for m in MODEL_CHOICES if m in set(perf["model"])]
    perf["model"] = pd.Categorical(perf["model"], categories=order, ordered=True)
    return perf.sort_values("model").reset_index(drop=True)


def stability_table(stability_rows: list[dict], n_folds: int) -> pd.DataFrame:
    if not stability_rows:
        return pd.DataFrame(
            columns=["feature", "n_selected", "freq", "mean_coef"]
        )
    raw = pd.DataFrame(stability_rows)
    out = (
        raw.groupby("feature")
        .agg(
            n_selected=("coef", "count"),
            mean_coef=("coef", "mean"),
        )
        .reset_index()
    )
    out["freq"] = out["n_selected"] / max(n_folds, 1)
    return out.sort_values(
        ["n_selected", "feature"], ascending=[False, True]
    ).reset_index(drop=True)


def _add_pooled_ci(summary: pd.DataFrame, raw: pd.DataFrame) -> pd.DataFrame:
    """按 model + term 做逆方差合并，返回带 pooled HR 与解析 95% CI 的表。

    每折的 log-HR 记为 beta_i、标准误为 se_i，权重 w_i = 1 / se_i^2：
        beta_pooled = Σ w_i beta_i / Σ w_i
        var_pooled  = 1 / Σ w_i
    95% CI 在 log-HR 尺度上取 beta_pooled ± 1.96 * sqrt(var_pooled) 再 exp。

    注意：50 折共享病人、且 Cox 带惩罚，该 CI 是近似值，可能偏窄，
    不能替代病人层面 bootstrap。
    """
    z = 1.959963984540054
    rows: list[dict] = []
    for (model, term), grp in raw.groupby(["model", "term"]):
        beta = grp["coef"].to_numpy(dtype=float)
        se = grp["se"].to_numpy(dtype=float)
        w = 1.0 / np.maximum(se ** 2, 1e-12)
        b = float(np.sum(w * beta) / np.sum(w))
        se_p = float(np.sqrt(1.0 / np.sum(w)))
        lo_b, hi_b = b - z * se_p, b + z * se_p
        rows.append({
            "model": model,
            "term": term,
            "coef_pooled": b,
            "coef_pooled_lo": lo_b,
            "coef_pooled_hi": hi_b,
            "hr_pooled": float(np.exp(b)),
            "hr_pooled_lo": float(np.exp(lo_b)),
            "hr_pooled_hi": float(np.exp(hi_b)),
        })
    if not rows:
        return summary
    return summary.merge(pd.DataFrame(rows), on=["model", "term"], how="left")


def coefficient_summary(coef_rows: list[dict],
                        fold_counts: dict[str, int]) -> pd.DataFrame:
    if not coef_rows:
        return pd.DataFrame(columns=[
            "model", "term", "n_folds", "freq", "coef_median",
            "coef_q10", "coef_q90", "hr_median", "hr_q10", "hr_q90",
            "cox_penalizer_median", "coef_pooled", "coef_pooled_lo",
            "coef_pooled_hi", "hr_pooled", "hr_pooled_lo", "hr_pooled_hi",
        ])
    raw = pd.DataFrame(coef_rows)
    out = (
        raw.groupby(["model", "term"])
        .agg(
            n_folds=("coef", "count"),
            coef_median=("coef", "median"),
            coef_q10=("coef", lambda s: float(s.quantile(0.10))),
            coef_q90=("coef", lambda s: float(s.quantile(0.90))),
            hr_median=("hr", "median"),
            hr_q10=("hr", lambda s: float(s.quantile(0.10))),
            hr_q90=("hr", lambda s: float(s.quantile(0.90))),
            cox_penalizer_median=("cox_penalizer", "median"),
        )
        .reset_index()
    )
    out["freq"] = [
        row.n_folds / max(fold_counts.get(row.model, 0), 1)
        for row in out.itertuples()
    ]
    out = _add_pooled_ci(out, raw)
    order = {m: i for i, m in enumerate(MODEL_CHOICES)}
    out["_order"] = out["model"].map(order).fillna(99)
    return (
        out.sort_values(["_order", "term"])
        .drop(columns="_order")
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------- 报告
def _fmt(value, nd: int = 3, dash: str = "–") -> str:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return dash
    if not np.isfinite(value):
        return dash
    return f"{value:.{nd}f}"


def write_markdown(path: Path, perf: pd.DataFrame, folds: pd.DataFrame,
                   stability: pd.DataFrame, coef_sum: pd.DataFrame,
                   fold_counts: dict[str, int],
                   args, elapsed: float, n_patients: int, n_events: int,
                   figure_paths: list[Path]) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    n_outer = 5 * args.repeats
    lines: list[str] = []
    lines.append("# 固定折 Cox 模型性能汇总")
    lines.append("")
    lines.append(f"- 生成时间：{now}")
    lines.append(f"- 分析集：{n_patients} 例 / {n_events} events")
    lines.append(
        f"- CV：5×{args.repeats} 重复分层 K 折，seed={args.seed}，"
        f"共 {len(folds)} 个模型-折记录"
    )
    lines.append(
        f"- 折内流程：方差过滤 → |r|>{args.corr_threshold} 去冗余 → "
        f"单变量 Cox p<{args.p_threshold} → 标准化 → "
        f"（LASSO 内层 {args.inner_splits} 折选 alpha）→ 最终 Cox"
    )
    lines.append(f"- 运行耗时：{elapsed:.1f}s")
    lines.append("")
    lines.append("## 1. 性能")
    lines.append("")
    lines.append(
        "| model | folds | C-index (mean ± SD) | median | "
        "train−test gap | log-rank p<0.05 | features mean [min–max] | "
        "alpha median [min–max] | Cox penalizer | fallback folds |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for row in perf.itertuples():
        feats = "–"
        if np.isfinite(row.n_features_mean):
            feats = (
                f"{row.n_features_mean:.1f} "
                f"[{int(row.n_features_min)}–{int(row.n_features_max)}]"
            )
        alpha = "–"
        if np.isfinite(row.alpha_median):
            alpha = (
                f"{row.alpha_median:.3e} "
                f"[{row.alpha_min:.3e}–{row.alpha_max:.3e}]"
            )
        lines.append(
            f"| {row.model} | {row.n_folds} | "
            f"{_fmt(row.cindex_mean)} ± {_fmt(row.cindex_sd)} | "
            f"{_fmt(row.cindex_median)} | {_fmt(row.cindex_gap_mean)} | "
            f"{_fmt(row.logrank_pct_sig)} | {feats} | {alpha} | "
            f"{_fmt(row.cox_penalizer_median, 2)} | "
            f"{row.n_fallback_folds} |"
        )
    lines.append("")
    lines.append("## 2. LASSO 特征稳定性（前 10）")
    lines.append("")
    if stability.empty:
        lines.append("本次运行未包含 LASSO 模型。")
    else:
        lines.append("| feature | 被选折数 | 频率 | 平均 LASSO 系数 |")
        lines.append("|---|---|---|---|")
        for row in stability.head(10).itertuples():
            lines.append(
                f"| {row.feature} | {row.n_selected} | "
                f"{_fmt(row.freq)} | {_fmt(row.mean_coef, 4)} |"
            )
    lines.append("")
    lines.append("## 3. 主要系数（跨折入选频率 ≥ 0.99）")
    lines.append("")
    stable = coef_sum[
        (coef_sum["freq"] >= 0.99) & (coef_sum["model"].astype(str) != "lasso")
    ] if not coef_sum.empty else coef_sum
    if stable.empty:
        lines.append("本次运行没有跨折稳定的非 LASSO 系数。")
    else:
        lines.append("| model | term | folds | HR (pooled 95% CI) |")
        lines.append("|---|---|---|---|")
        for row in stable.itertuples():
            lines.append(
                f"| {row.model} | {row.term} | {row.n_folds}/{fold_counts.get(row.model, 0)} | "
                f"{_fmt(row.hr_pooled, 2)} "
                f"[{_fmt(row.hr_pooled_lo, 2)}–{_fmt(row.hr_pooled_hi, 2)}] |"
            )
    lines.append("")
    lines.append("## 4. 口径与限制")
    lines.append("")
    lines.append(
        f"1. C-index 在外层测试折上计算；主结果是 {n_outer} 折的均值 ± SD。"
        f"这些折共享病人（每例被测试 {args.repeats} 次），"
        "**SD 不是 95% CI**。"
    )
    lines.append(
        "2. 方差过滤、相关性去冗余、单变量 Cox、标准化和 alpha 选择"
        "全部只在当前外层训练折内完成；测试折不参与任何拟合。"
    )
    lines.append(
        "3. log-rank 的高低危阈值取该折**训练集**风险的中位数，"
        f"在测试折上分组；`log-rank p<0.05` 是 {n_outer} 折中显著的比例。"
    )
    lines.append(
        "4. train−test gap = 训练折 C-index − 测试折 C-index 的均值，"
        "用于描述乐观偏差；正值越大，过拟合越明显。"
    )
    lines.append(
        "5. KM 图只使用**单个 repeat** 的折外预测，每组 399 例各出现一次；"
        "不把 10 个 repeat 的 3990 条记录合并，避免同一病人重复计入。"
    )
    lines.append(
        "6. 森林图的 HR 为跨折逆方差合并（每折最终 Cox 的 `coef` 与 "
        "`se(coef)`），误差条是合并后的解析 95% CI。50 折共享病人、"
        "且 Cox 带惩罚，该 CI 为近似值、可能偏窄，不能替代病人层面 "
        f"bootstrap；LASSO 模型只展示入选频率≥ {args.forest_min_freq:.2f} 的特征。"
    )
    lines.append(
        "7. 所有 Cox 拟合使用 0.1 / 1 / 10 的惩罚阶梯，表中记录实际生效的"
        "惩罚值中位数；若与论文的无惩罚 Cox 并排比较，需在方法中声明。"
    )
    lines.append(
        "8. LASSO 在某折选中 0 个特征时，回退到单变量 p 值最小的前 "
        f"{args.fallback_k} 个特征，并在 `notes` 中标记；"
        "回退折仍计入稳定性分母，但不贡献入选次数，"
        "也不写入 LASSO 的逐折系数表与森林图。"
    )
    lines.append("")
    lines.append("## 5. 产物")
    lines.append("")
    out_dir = Path(args.out_dir)
    table = [
        (out_dir / "cv_folds.csv", "逐折指标"),
        (out_dir / "oof_predictions.csv", "折外风险与高低危标签"),
        (out_dir / "selection_stability.csv", "LASSO 特征稳定性"),
        (out_dir / "cv_coefficients.csv", "逐折 Cox 系数"),
        (out_dir / "coefficient_summary.csv", "系数跨折汇总"),
        (out_dir / "perf.csv", "性能汇总（机器可读）"),
        (out_dir / "perf.md", "本报告"),
    ]
    for item in table:
        lines.append(f"- `{item[0]}`：{item[1]}")
    for fig in figure_paths:
        lines.append(f"- `{fig}`：图形")
    lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- 图形
def make_figures(folds: pd.DataFrame, oof: pd.DataFrame,
                 coef_sum: pd.DataFrame, args) -> list[Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter, MaxNLocator, NullLocator

    out_dir = Path(args.figures_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    present = set(folds["model"].astype(str))
    models = [m for m in MODEL_CHOICES if m in present]
    made: list[Path] = []

    # 1) C-index 箱线图
    data = [
        folds.loc[folds["model"].astype(str) == m, "cindex"].to_numpy(float)
        for m in models
    ]
    pos = np.arange(len(models))
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.boxplot(
        data, positions=pos, widths=0.55,
        showmeans=True, patch_artist=True,
        boxprops={"facecolor": "#e2e8f0", "edgecolor": "#4a5568"},
        medianprops={"color": "#c53030"},
        meanprops={"marker": "D", "markerfacecolor": "#2b6cb0",
                   "markeredgecolor": "#2b6cb0", "markersize": 5},
    )
    rng = np.random.default_rng(0)
    for i, values in enumerate(data):
        ax.scatter(
            pos[i] + rng.uniform(-0.12, 0.12, len(values)),
            values, s=8, alpha=0.45, color="#2b6cb0", linewidths=0,
        )
    ax.axhline(0.5, color="grey", linestyle="--", linewidth=1)
    ax.set_xticks(pos)
    ax.set_xticklabels(models)
    ax.set_ylabel("C-index (outer test folds)")
    ax.set_title(
        f"C-index across 5×{args.repeats} folds (seed={args.seed})"
    )
    fig.tight_layout()
    path = out_dir / "cindex_boxplot.png"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    made.append(path)

    # 2) 折外 KM（单个 repeat）
    repeat = min(max(args.km_repeat, 0), max(args.repeats - 1, 0))
    for model in models:
        sub = oof[(oof["model"] == model) & (oof["repeat"] == repeat)]
        if sub.empty:
            continue
        sub = sub.copy()
        sub["high_risk"] = sub["high_risk"].astype(bool)
        if sub["high_risk"].all() or (~sub["high_risk"]).all():
            continue
        fig, ax = plt.subplots(figsize=(6.4, 4.6))
        for flag, label, color in (
            (False, "low risk", "#2b6cb0"),
            (True, "high risk", "#c53030"),
        ):
            group = sub[sub["high_risk"] == flag]
            if group.empty:
                continue
            kmf = KaplanMeierFitter()
            kmf.fit(group["time"], group["event"],
                    label=f"{label} (n={len(group)})")
            kmf.plot_survival_function(ax=ax, ci_show=False, color=color)
        p_value = float(logrank_test(
            sub.loc[sub["high_risk"], "time"],
            sub.loc[~sub["high_risk"], "time"],
            sub.loc[sub["high_risk"], "event"],
            sub.loc[~sub["high_risk"], "event"],
        ).p_value)
        ax.set_xlabel("Time (days)")
        ax.set_ylabel("Overall survival")
        ax.set_title(
            f"{model}: out-of-fold KM (repeat {repeat}), "
            f"log-rank p={p_value:.3g}"
        )
        fig.tight_layout()
        path = out_dir / f"km_oof_{model}_repeat{repeat}.png"
        fig.savefig(path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        made.append(path)

    # 3) 森林图
    if coef_sum.empty:
        return made
    for model in models:
        sub = coef_sum[coef_sum["model"] == model].copy()
        if sub.empty:
            continue
        if model == "lasso":
            sub = sub[sub["freq"] >= args.forest_min_freq]
            sub = sub.sort_values(
                ["n_folds", "hr_pooled"], ascending=[False, True],
            ).head(args.forest_top_terms)
        else:
            sub = sub.sort_values("hr_pooled")
        if sub.empty:
            continue
        sub = sub.iloc[::-1].reset_index(drop=True)

        hr = sub["hr_pooled"].to_numpy(float)
        lo = np.clip(sub["hr_pooled_lo"].to_numpy(float), 1e-8, None)
        hi = np.clip(sub["hr_pooled_hi"].to_numpy(float), 1e-8, None)
        xerr = np.clip(np.vstack([hr - lo, hi - hr]), 0, None)
        y = np.arange(len(sub))

        fig, ax = plt.subplots(
            figsize=(7.0, max(3.0, 0.42 * len(sub) + 1.2))
        )
        ax.errorbar(
            hr, y, xerr=xerr, fmt="o", color="#2b6cb0",
            ecolor="#4a5568", elinewidth=1.2, capsize=3, markersize=5,
        )
        ax.axvline(1.0, color="grey", linestyle="--", linewidth=1)
        lo_all = min(float(np.min(lo)), 1.0)
        hi_all = max(float(np.max(hi)), 1.0)
        if hi_all / max(lo_all, 1e-12) > 2.0:
            ax.set_xscale("log")
            candidates = [
                0.1, 0.2, 0.25, 0.33, 0.5, 0.67, 0.75, 1.0,
                1.25, 1.5, 2.0, 3.0, 4.0, 5.0, 10.0,
            ]
            ticks = [
                t for t in candidates
                if lo_all * 0.95 <= t <= hi_all * 1.05
            ]
            if len(ticks) > 5:
                idx = np.unique(
                    np.linspace(0, len(ticks) - 1, 5).round().astype(int)
                )
                ticks = [ticks[i] for i in idx]
            if len(ticks) >= 2:
                ax.set_xticks(ticks)
                ax.xaxis.set_major_formatter(
                    FuncFormatter(lambda value, _pos: f"{value:g}")
                )
                ax.xaxis.set_minor_locator(NullLocator())
        else:
            ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
        ax.set_yticks(y)
        ax.set_yticklabels(
            [
                f"{term}  ({int(n)} folds)"
                for term, n in zip(sub["term"], sub["n_folds"])
            ],
            fontsize=8,
        )
        ax.set_xlabel(
            "Hazard ratio (pooled; bars = 95% CI)"
        )
        ax.set_title(f"{model}: fold-wise Cox coefficients (inverse-variance pooled)")
        fig.tight_layout()
        path = out_dir / f"forest_{model}.png"
        fig.savefig(path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        made.append(path)
    return made


# ---------------------------------------------------------------- 主流程
def main() -> None:
    ap = argparse.ArgumentParser(description="Day18 固定折 Cox 模型评估")
    ap.add_argument("--analysis", default="results/tables/analysis_set.csv")
    ap.add_argument("--features", default="results/tables/features_all.csv")
    ap.add_argument("--feature-columns", default="results/tables/feature_columns.txt")
    ap.add_argument("--cv-assignment", default="results/tables/cv_assignment.csv")
    ap.add_argument("--out-dir", default="results/tables")
    ap.add_argument("--figures-dir", default="results/figures/cv")
    ap.add_argument("--models", nargs="+", choices=MODEL_CHOICES,
                    default=MODEL_CHOICES)
    ap.add_argument("--repeats", type=int, default=10,
                    help="只跑前 N 个 repeat；用于冒烟测试")
    ap.add_argument("--inner-splits", type=int, default=5)
    ap.add_argument("--corr-threshold", type=float, default=0.9)
    ap.add_argument("--p-threshold", type=float, default=0.05)
    ap.add_argument("--fallback-k", type=int, default=10)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--expect-n", type=int, default=399)
    ap.add_argument("--expect-events", type=int, default=352)
    ap.add_argument("--expect-features", type=int, default=537)
    ap.add_argument("--no-figures", action="store_true",
                    help="跳过图形生成")
    ap.add_argument("--km-repeat", type=int, default=0,
                    help="KM 图使用哪一个 repeat 的折外预测")
    ap.add_argument("--forest-min-freq", type=float, default=0.5,
                    help="LASSO 森林图只展示入选频率不低于该值的特征")
    ap.add_argument("--forest-top-terms", type=int, default=20,
                    help="LASSO 森林图最多展示多少个特征")
    args = ap.parse_args()

    if not (1 <= args.repeats <= 10):
        raise SystemExit("--repeats 必须在 1..10 之间")
    if not (0 <= args.forest_min_freq <= 1):
        raise SystemExit("--forest-min-freq 必须在 0..1 之间")
    if args.forest_top_terms < 1:
        raise SystemExit("--forest-top-terms 必须 >= 1")

    is_partial = (
        args.repeats != 10 or set(args.models) != set(MODEL_CHOICES)
    )
    if is_partial:
        if Path(args.out_dir).resolve() == Path("results/tables").resolve():
            raise SystemExit(
                "子集运行（--repeats<10 或 --models 不完整）不能写入默认 "
                "results/tables；请显式指定 --out-dir（例如 "
                "--out-dir results/tables/smoke）。"
            )
        if (not args.no_figures
                and Path(args.figures_dir).resolve()
                == Path("results/figures/cv").resolve()):
            raise SystemExit(
                "子集运行不能写入默认 results/figures/cv；请指定 "
                "--figures-dir，或加 --no-figures。"
            )

    df, feature_cols, y, assignment = load_data(args)
    missing_sig = [c for c in SIGNATURE_FEATURES if c not in feature_cols]
    if missing_sig:
        raise SystemExit(f"路线 1 特征不在特征列中: {missing_sig}")

    X_clinical = clinical_matrix(df)
    X_signature = df[SIGNATURE_FEATURES].astype(float)
    X_image = df[feature_cols].astype(float)

    folds_rows: list[dict] = []
    oof_rows: list[dict] = []
    stability_rows: list[dict] = []
    coef_rows: list[dict] = []

    started = time.time()
    # 只统计实际跑了 lasso 的折数，作为稳定性分母
    lasso_fold_count = 0

    for repeat, fold, tr, te in iter_folds(
        df, assignment, args.repeats, n_splits=5,
    ):
        test_df = df.iloc[te]
        ytr, yte = y[tr], y[te]
        n_train, n_test = len(tr), len(te)
        line = [f"[repeat {repeat} fold {fold}] train={n_train} test={n_test}"]

        # 仅临床
        if "clinical" in args.models:
            Xtr = X_clinical.iloc[tr]
            Xte = X_clinical.iloc[te]
            cph = fit_cox(Xtr, ytr)
            risk_tr = predict_cox(cph, Xtr)
            risk_te = predict_cox(cph, Xte)
            ci, ci_tr, p, high, thr = evaluate_fold(
                risk_tr, risk_te, ytr, yte,
            )
            penalizer = float(cph.penalizer)
            add_row(folds_rows, "clinical", repeat, fold, n_train, n_test,
                    Xtr.shape[1], ci, ci_tr, p, None, penalizer, None,
                    "age+gender+stage+histology")
            add_oof(oof_rows, "clinical", repeat, fold, test_df, risk_te,
                    high, thr)
            add_coefficients(coef_rows, "clinical", repeat, fold,
                             cph.summary, penalizer)
            line.append(f"clinical={ci:.3f}")

        # 路线 1
        if "signature" in args.models:
            Xtr = X_signature.iloc[tr]
            Xte = X_signature.iloc[te]
            sig = fit_signature_fold(Xtr, Xte, ytr)
            ci, ci_tr, p, high, thr = evaluate_fold(
                sig["risk_train"], sig["risk_test"], ytr, yte,
            )
            add_row(folds_rows, "signature", repeat, fold, n_train, n_test,
                    sig["n_features"], ci, ci_tr, p, None,
                    sig["cox_penalizer"], None,
                    "4-feature a priori signature")
            add_oof(oof_rows, "signature", repeat, fold, test_df,
                    sig["risk_test"], high, thr)
            add_coefficients(coef_rows, "signature", repeat, fold,
                             sig["cox_summary"], sig["cox_penalizer"])
            line.append(f"signature={ci:.3f}")

        # 路线 2 与联合模型复用同一次 LASSO 拟合
        lasso_result = None
        if ("lasso" in args.models) or ("combined" in args.models):
            lasso_result = fit_lasso_fold(
                X_image.iloc[tr], X_image.iloc[te], ytr,
                seed=args.seed + 100 * repeat + fold, args=args,
            )
            lasso_fold_count += 1
            if not lasso_result["fallback"]:
                for feature, coef in lasso_result["picked_coef"].items():
                    stability_rows.append({
                        "feature": feature, "coef": coef,
                        "repeat": repeat, "fold": fold,
                    })

        if "lasso" in args.models and lasso_result is not None:
            ci, ci_tr, p, high, thr = evaluate_fold(
                lasso_result["risk_train"], lasso_result["risk_test"], ytr, yte,
            )
            add_row(folds_rows, "lasso", repeat, fold, n_train, n_test,
                    lasso_result["n_features"], ci, ci_tr, p,
                    lasso_result["alpha"], lasso_result["cox_penalizer"],
                    lasso_result["diag"], lasso_result["notes"])
            add_oof(oof_rows, "lasso", repeat, fold, test_df,
                    lasso_result["risk_test"], high, thr)
            if not lasso_result["fallback"]:
                add_coefficients(coef_rows, "lasso", repeat, fold,
                                 lasso_result["cox_summary"],
                                 lasso_result["cox_penalizer"])
            line.append(f"lasso={ci:.3f}")

        if "combined" in args.models and lasso_result is not None:
            comb = fit_combined_fold(
                X_clinical.iloc[tr], X_clinical.iloc[te],
                lasso_result["risk_train"], lasso_result["risk_test"], ytr,
            )
            ci, ci_tr, p, high, thr = evaluate_fold(
                comb["risk_train"], comb["risk_test"], ytr, yte,
            )
            notes = "clinical+radiomics_score; " + lasso_result["notes"]
            add_row(folds_rows, "combined", repeat, fold, n_train, n_test,
                    comb["n_features"], ci, ci_tr, p, lasso_result["alpha"],
                    comb["cox_penalizer"], lasso_result["diag"], notes)
            add_oof(oof_rows, "combined", repeat, fold, test_df,
                    comb["risk_test"], high, thr)
            add_coefficients(coef_rows, "combined", repeat, fold,
                             comb["cox_summary"], comb["cox_penalizer"])
            line.append(f"combined={ci:.3f}")

        print(" | ".join(line), flush=True)

    folds = pd.DataFrame(folds_rows)
    oof = pd.DataFrame(oof_rows)
    perf = summarise(folds, args.repeats, args.seed)
    stability = stability_table(stability_rows, lasso_fold_count)
    fold_counts = (
        folds.groupby("model")["cindex"].count().to_dict()
        if not folds.empty else {}
    )
    coef_sum = coefficient_summary(coef_rows, fold_counts)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    folds_path = out_dir / "cv_folds.csv"
    oof_path = out_dir / "oof_predictions.csv"
    perf_path = out_dir / "perf.csv"
    stability_path = out_dir / "selection_stability.csv"
    coef_path = out_dir / "cv_coefficients.csv"
    coef_sum_path = out_dir / "coefficient_summary.csv"
    md_path = out_dir / "perf.md"

    folds.to_csv(folds_path, index=False)
    oof.to_csv(oof_path, index=False)
    perf.to_csv(perf_path, index=False)
    stability.to_csv(stability_path, index=False)
    pd.DataFrame(coef_rows).to_csv(coef_path, index=False)
    coef_sum.to_csv(coef_sum_path, index=False)

    elapsed = time.time() - started
    figure_paths: list[Path] = []
    if not args.no_figures and not folds.empty:
        try:
            figure_paths = make_figures(folds, oof, coef_sum, args)
        except Exception as exc:  # noqa: BLE001 - 图形失败不丢表格
            print(f"[warn] 图形生成失败: {exc}", flush=True)

    write_markdown(
        md_path, perf, folds, stability, coef_sum, fold_counts, args,
        elapsed, len(df), int(df["deadstatus.event"].sum()), figure_paths,
    )

    print("\n==== CV models ====")
    print(f"分析集 {len(df)} 例；events {int(df['deadstatus.event'].sum())}")
    print(f"repeats: {args.repeats}；models: {', '.join(args.models)}")
    if not perf.empty:
        show = perf[[
            "model", "n_folds", "n_features_mean",
            "cindex_mean", "cindex_sd", "cindex_gap_mean",
            "logrank_pct_sig", "n_fallback_folds",
        ]].copy()
        print(show.to_string(index=False))
    print(f"耗时: {elapsed:.1f}s")
    print(f"逐折结果: {folds_path}")
    print(f"OOF 预测: {oof_path}")
    print(f"性能汇总: {perf_path}")
    print(f"特征稳定性: {stability_path}")
    print(f"逐折系数: {coef_path}")
    print(f"系数汇总: {coef_sum_path}")
    print(f"文字报告: {md_path}")
    for fig in figure_paths:
        print(f"图形: {fig}")


if __name__ == "__main__":
    main()
