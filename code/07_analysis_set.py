"""Day 18：固定建模分析集（合并 / 缺失审计 / 编码锁定）

输入：
  results/tables/cohort.csv        # 临床与生存结局
  results/tables/features_all.csv  # 422 × 537 影像特征

输出：
  results/tables/analysis_set.csv      # 唯一建模人群（ID + 结局 + 已编码临床变量）
  results/tables/excluded_patients.csv # 逐例排除清单与原因
  results/tables/feature_columns.txt   # 锁定的 537 个特征列名与顺序
  results/tables/analysis_set.md       # 分析集报告（流转 / 基线 / 局限）

判据：
  - cohort 与 features 的 PatientID 一一对应，合并后不得膨胀；
  - 只对预先声明的建模变量做完整病例筛选，禁止全表 dropna；
  - 分期、组织学、性别编码在固定分析集后一次性锁定；
  - 最终行数或事件数与 --expect-n / --expect-events 不符时以非零码退出。
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

# 建模变量：任一缺失即排除（Histology 例外，缺失编码为 unknown）
EXCLUSION_VARS = ["age", "gender", "Overall.Stage", "Survival.time", "deadstatus.event"]
REQUIRED_COHORT = ["PatientID", *EXCLUSION_VARS, "Histology"]

STAGE_MAP = {"I": 0, "II": 0, "IIIa": 1, "IIIb": 1}
HIST_MAP = {
    "adenocarcinoma": "adeno",
    "squamous cell carcinoma": "squamous",
    "large cell": "large",
    "nos": "nos",
}
HIST_LEVELS = ["adeno", "squamous", "large", "nos", "unknown"]

ANALYSIS_COLS = [
    "PatientID", "Survival.time", "deadstatus.event",
    "age", "gender", "gender_num",
    "Overall.Stage", "stage_bin",
    "Histology", "histology",
]


# ---------------------------------------------------------------- 载入与合并
def load_table(path: Path, required: list[str], label: str) -> pd.DataFrame:
    if not path.exists():
        raise SystemExit(f"缺少{label}: {path}")
    df = pd.read_csv(path)
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise SystemExit(f"{path} 缺少列: {missing}")
    df["PatientID"] = df["PatientID"].astype(str)
    return df


def merge_tables(cohort: pd.DataFrame, feats: pd.DataFrame) -> pd.DataFrame:
    if not cohort["PatientID"].is_unique:
        dup = cohort.loc[cohort["PatientID"].duplicated(), "PatientID"].tolist()
        raise SystemExit(f"cohort 存在重复 PatientID: {dup[:10]}")
    if not feats["PatientID"].is_unique:
        dup = feats.loc[feats["PatientID"].duplicated(), "PatientID"].tolist()
        raise SystemExit(f"features 存在重复 PatientID: {dup[:10]}")

    only_cohort = sorted(set(cohort["PatientID"]) - set(feats["PatientID"]))
    only_feats = sorted(set(feats["PatientID"]) - set(cohort["PatientID"]))
    if only_cohort or only_feats:
        raise SystemExit(
            f"两表病例集合不一致：仅 cohort {len(only_cohort)} 例，"
            f"仅 features {len(only_feats)} 例"
        )

    df = cohort.merge(
        feats, on="PatientID", how="inner",
        validate="one_to_one", suffixes=("", "_feature"),
    )
    if len(df) != len(cohort):
        raise SystemExit(f"合并后行数异常: {len(df)} != {len(cohort)}")
    if not df["PatientID"].is_unique:
        raise SystemExit("合并后 PatientID 不唯一")

    collision = [c for c in df.columns if c.endswith("_feature")]
    if collision:
        raise SystemExit(f"临床表与特征表存在同名列: {collision}")
    return df


# ---------------------------------------------------------------- 排除审计
def add_exclusion_flags(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    flags = []
    for var in EXCLUSION_VARS:
        flag = f"excl_{var}"
        df[flag] = df[var].isna()
        flags.append(flag)

    df["excluded"] = df[flags].any(axis=1)
    df["exclude_reason"] = df[flags].apply(
        lambda row: "+".join(f.replace("excl_", "") for f in flags if row[f]),
        axis=1,
    )
    return df, flags


def sequential_flow(df: pd.DataFrame) -> tuple[list[dict], pd.DataFrame]:
    remaining = df
    rows = [{"step": "原始队列（cohort ∩ features）", "excluded": 0,
             "remaining": len(df)}]
    for var in EXCLUSION_VARS:
        mask = remaining[var].isna()
        n_excl = int(mask.sum())
        remaining = remaining.loc[~mask]
        rows.append({"step": f"缺 `{var}`", "excluded": n_excl,
                     "remaining": len(remaining)})
    return rows, remaining


# ---------------------------------------------------------------- 编码
def encode_analysis(analysis: pd.DataFrame) -> pd.DataFrame:
    out = analysis.copy()

    bad_gender = ~out["gender"].isin(["male", "female"])
    if bad_gender.any():
        raise SystemExit(
            f"未识别的 gender 取值: {out.loc[bad_gender, 'gender'].unique()}"
        )
    out["gender_num"] = (out["gender"] == "male").astype(int)

    out["stage_bin"] = out["Overall.Stage"].map(STAGE_MAP)
    bad_stage = out["stage_bin"].isna()
    if bad_stage.any():
        raise SystemExit(
            f"未映射的 Overall.Stage 取值: "
            f"{out.loc[bad_stage, 'Overall.Stage'].unique()}"
        )
    out["stage_bin"] = out["stage_bin"].astype(int)

    mapped = out["Histology"].map(HIST_MAP)
    unmapped = out["Histology"].notna() & mapped.isna()
    if unmapped.any():
        raise SystemExit(
            f"未映射的 Histology 取值: {out.loc[unmapped, 'Histology'].unique()}"
        )
    out["histology"] = mapped.fillna("unknown")
    if not out["histology"].isin(HIST_LEVELS).all():
        raise SystemExit("histology 编码出现未知取值")

    return out


# ---------------------------------------------------------------- 统计
def pct(count: int, total: int) -> str:
    return f"{count}（{count / total:.1%}）" if total else f"{count}（—）"


def count_value(series: pd.Series, value: str) -> int:
    return int((series == value).sum())


def baseline_rows(included: pd.DataFrame, excluded: pd.DataFrame) -> list[tuple[str, str, str]]:
    n_in, n_ex = len(included), len(excluded)

    def stage_group(frame: pd.DataFrame, label: str) -> int:
        if label == "III":
            return int(frame["Overall.Stage"].isin(["IIIa", "IIIb"]).sum())
        if label == "I-II":
            return int(frame["Overall.Stage"].isin(["I", "II"]).sum())
        return int(frame["Overall.Stage"].isna().sum())

    def hist_group(frame: pd.DataFrame, label: str) -> int:
        mapped = frame["Histology"].map(HIST_MAP)
        if label == "unknown":
            return int(mapped.isna().sum())
        return int((mapped == label).sum())

    rows = [
        ("events", pct(count_value(included["deadstatus.event"], 1), n_in),
         pct(count_value(excluded["deadstatus.event"], 1), n_ex)),
        ("male", pct(count_value(included["gender"], "male"), n_in),
         pct(count_value(excluded["gender"], "male"), n_ex)),
        ("female", pct(count_value(included["gender"], "female"), n_in),
         pct(count_value(excluded["gender"], "female"), n_ex)),
        ("Stage III", pct(stage_group(included, "III"), n_in),
         pct(stage_group(excluded, "III"), n_ex)),
        ("Stage I–II", pct(stage_group(included, "I-II"), n_in),
         pct(stage_group(excluded, "I-II"), n_ex)),
        ("Stage 缺失", pct(stage_group(included, "missing"), n_in),
         pct(stage_group(excluded, "missing"), n_ex)),
    ]
    for level in HIST_LEVELS:
        rows.append((
            f"Histology: {level}",
            pct(hist_group(included, level), n_in),
            pct(hist_group(excluded, level), n_ex),
        ))
    return rows


# ---------------------------------------------------------------- 报告
def build_report(args, df: pd.DataFrame, analysis: pd.DataFrame,
                 excluded: pd.DataFrame, flow: list[dict],
                 feature_cols: list[str]) -> str:
    n_raw, n_in, n_ex = len(df), len(analysis), len(excluded)
    events = int(analysis["deadstatus.event"].sum())
    censored = n_in - events

    age = analysis["age"]
    age_txt = (f"{age.median():.1f}（IQR {age.quantile(0.25):.1f}–"
               f"{age.quantile(0.75):.1f}；范围 {age.min():.1f}–{age.max():.1f}）")

    stage_missing = int(excluded["Overall.Stage"].isna().sum())
    stage_known = n_ex - stage_missing
    ex_iii = int(excluded["Overall.Stage"].isin(["IIIa", "IIIb"]).sum())
    in_iii = int(analysis["Overall.Stage"].isin(["IIIa", "IIIb"]).sum())
    ex_unknown_hist = int(excluded["Histology"].map(HIST_MAP).isna().sum())
    in_unknown_hist = int(analysis["Histology"].map(HIST_MAP).isna().sum())

    lines: list[str] = []
    lines.append("# 分析集定义与固定（Day 18）")
    lines.append("")
    lines.append(f"- 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("- 脚本：`code/07_analysis_set.py`")
    lines.append(f"- 临床表：`{args.cohort}`")
    lines.append(f"- 特征表：`{args.features}`")
    lines.append("- 输出：`results/tables/analysis_set.csv`、"
                 "`results/tables/excluded_patients.csv`、"
                 "`results/tables/feature_columns.txt`")
    lines.append("")

    lines.append("## 1. 目的")
    lines.append("")
    lines.append("为 Day 18 的四个模型（仅临床、路线 1 签名模型、路线 2 LASSO-Cox、"
                 "临床+影像）提供**唯一、固定、可复现**的建模人群，确保所有模型使用"
                 "同一批病人、同一套外层交叉验证折。")
    lines.append("")

    lines.append("## 2. 原则")
    lines.append("")
    lines.append("1. 先声明建模变量与缺失规则，再做排除；禁止对合并表直接 `dropna()`。")
    lines.append("2. 只对预先声明的建模变量做完整病例筛选。")
    lines.append("3. 分析集一旦固定，下游脚本不得再次筛人、不得重新编码变量。")
    lines.append("4. 所有排除逐例记录原因，保留审计清单。")
    lines.append("")

    lines.append("## 3. 病例流转")
    lines.append("")
    lines.append("| 步骤 | 排除 | 剩余 |")
    lines.append("|---|---:|---:|")
    for row in flow:
        lines.append(f"| {row['step']} | {row['excluded']} | {row['remaining']} |")
    lines.append(f"| **固定分析集** | | **{n_in}** |")
    lines.append(f"| 其中 events / censored | | **{events} / {censored}** |")
    lines.append("")
    lines.append("排除按 `EXCLUSION_VARS` 顺序依次进行；同一病例若存在多项缺失，"
                 "计入首个命中变量。")
    lines.append("")

    lines.append("## 4. 排除清单")
    lines.append("")
    if n_ex == 0:
        lines.append("- 无排除病例。")
    else:
        reasons = excluded["exclude_reason"].value_counts()
        for reason, count in reasons.items():
            lines.append(f"### 4.{list(reasons.index).index(reason) + 1} "
                         f"`{reason}`（{count} 例）")
            lines.append("")
            ids = excluded.loc[excluded["exclude_reason"] == reason, "PatientID"].tolist()
            lines.append("、".join(ids) + "。")
            lines.append("")
        lines.append("完整清单（含 age、gender、stage、Histology、time、event）见 "
                     "`results/tables/excluded_patients.csv`。")
    lines.append("")

    lines.append("## 5. 变量定义与编码")
    lines.append("")
    lines.append("| 变量 | 来源列 | 类型 | 编码/处理 |")
    lines.append("|---|---|---|---|")
    lines.append("| 生存时间 | `Survival.time` | 连续 | 天，要求 > 0 |")
    lines.append("| 事件 | `deadstatus.event` | 二值 | 1=死亡，0=删失 |")
    lines.append("| 年龄 | `age` | 连续 | 年，不缩放、不插补 |")
    lines.append("| 性别 | `gender` | 二分类 | male=1，female=0 |")
    lines.append("| 分期 | `Overall.Stage` | 二分类 | I/II=0，IIIa/IIIb=1 |")
    lines.append("| 组织学 | `Histology` | 多分类 | adeno/squamous/large/nos/unknown；"
                 "原始缺失→unknown |")
    lines.append("")
    lines.append("下游建模使用编码后的 `gender_num`、`stage_bin`、`histology`；"
                 "原始 `Histology` 保留用于审计，其中 "
                 f"{int(analysis['Histology'].isna().sum())} 例为空。")
    lines.append("")
    lines.append("不纳入 `clinical.T.Stage`、`Clinical.N.Stage`、`Clinical.M.Stage`，"
                 "原因：T=5（2 例）与 N=4（3 例）的编码含义已丢失；"
                 "`clinical.T.Stage` 另缺 1 例（`LUNG1-085`，event=1）；"
                 "纳入会使分析集进一步缩小，并与 Day 15 的 v1 不可比。")
    lines.append("")

    lines.append("## 6. 纳入 vs 排除基线")
    lines.append("")
    lines.append(f"| 变量 | 纳入（n={n_in}） | 排除（n={n_ex}） |")
    lines.append("|---|---:|---:|")
    for name, inc, exc in baseline_rows(analysis, excluded):
        lines.append(f"| {name} | {inc} | {exc} |")
    lines.append("")
    if stage_missing:
        lines.append(f"\\* 排除组 {n_ex} 例中 {stage_missing} 例分期缺失；"
                     f"在 {stage_known} 例分期可查者中 Stage III 为 "
                     f"{ex_iii}/{stage_known} = {ex_iii / stage_known:.1%}。")
        lines.append("")
    lines.append(f"年龄：纳入者中位数 {age_txt}。"
                 f"排除组中 {int(excluded['age'].isna().sum())}/{n_ex} 例年龄缺失，"
                 "无法做组间年龄比较。")
    lines.append("")

    lines.append("## 7. 分析集特征")
    lines.append("")
    lines.append(f"- n={n_in}；events={events}（{events / n_in:.1%}）；"
                 f"censored={censored}（{censored / n_in:.1%}）")
    lines.append(f"- male {count_value(analysis['gender'], 'male')}"
                 f"（{count_value(analysis['gender'], 'male') / n_in:.1%}）/ "
                 f"female {count_value(analysis['gender'], 'female')}"
                 f"（{count_value(analysis['gender'], 'female') / n_in:.1%}）")
    lines.append(f"- Stage III {in_iii}（{in_iii / n_in:.1%}）/ "
                 f"Stage I–II {n_in - in_iii}（{(n_in - in_iii) / n_in:.1%}）")
    hist_parts = []
    for level in HIST_LEVELS:
        mapped = analysis["Histology"].map(HIST_MAP)
        count = int(mapped.isna().sum()) if level == "unknown" else int((mapped == level).sum())
        hist_parts.append(f"{level} {count}（{count / n_in:.1%}）")
    lines.append("- 组织学：" + "、".join(hist_parts))
    lines.append(f"- 影像特征：{len(feature_cols)} 个，全部有限；"
                 "列名与顺序锁定于 `feature_columns.txt`")
    lines.append("")

    lines.append("## 8. 下游使用约定")
    lines.append("")
    lines.append("```python")
    lines.append('analysis = pd.read_csv("results/tables/analysis_set.csv")')
    lines.append('feats = pd.read_csv("results/tables/features_all.csv")')
    lines.append('feature_cols = pd.read_csv(')
    lines.append('    "results/tables/feature_columns.txt", header=None')
    lines.append(")[0].tolist()")
    lines.append("")
    lines.append("model = analysis.merge(")
    lines.append('    feats[["PatientID"] + feature_cols],')
    lines.append('    on="PatientID", validate="one_to_one",')
    lines.append(")")
    lines.append(f"assert len(model) == {n_in}")
    lines.append("```")
    lines.append("")
    lines.append("- 所有模型必须从 `analysis_set.csv` 读取病人；")
    lines.append("- 不得再次 `dropna()` 或按其他变量筛人；")
    lines.append("- 外层折划分只基于这 "
                 f"{n_in} 例，见 `cv_assignment.csv`。")
    lines.append("")

    lines.append("## 9. 局限")
    lines.append("")
    lines.append(f"- 完整病例分析排除 {n_ex} 例（{n_ex / n_raw:.1%}），"
                 f"其中 {int(excluded['age'].isna().sum())} 例因 `age` 缺失。")
    lines.append(f"- 排除组事件率 {count_value(excluded['deadstatus.event'], 1) / n_ex:.1%}"
                 f"（纳入 {events / n_in:.1%}）、Stage III 比例 "
                 f"{ex_iii / stage_known:.1%}（纳入 {in_iii / n_in:.1%}）、"
                 f"组织学 unknown 比例 {ex_unknown_hist / n_ex:.1%}"
                 f"（纳入 {in_unknown_hist / n_in:.1%}），"
                 "提示缺失并非完全随机，结果外推需谨慎。")
    lines.append("- 未使用多重插补。若后续做敏感性分析，可在 CV 折内对 `age` 做中位数插补"
                 "并保留 422 例，但不得与主分析混用。")
    lines.append("")

    lines.append("## 10. 结论")
    lines.append("")
    lines.append(f"- 固定分析集：**{n_in} 例，{events} events，{censored} censored**。")
    lines.append("- 临床变量编码、缺失规则、特征列均已锁定。")
    lines.append("- 本文件与 `excluded_patients.csv` 共同作为 Day 18 的数据审计证据。")
    lines.append("")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- 主流程
def main() -> None:
    ap = argparse.ArgumentParser(description="Day18 固定建模分析集")
    ap.add_argument("--cohort", default="results/tables/cohort.csv")
    ap.add_argument("--features", default="results/tables/features_all.csv")
    ap.add_argument("--out-dir", default="results/tables")
    ap.add_argument("--out", default="results/tables/analysis_set.md")
    ap.add_argument("--expect-n", type=int, default=399,
                    help="固定分析集例数；<0 表示不检查")
    ap.add_argument("--expect-events", type=int, default=352,
                    help="固定分析集事件数；<0 表示不检查")
    ap.add_argument("--expect-features", type=int, default=537,
                    help="特征列数；<0 表示不检查")
    args = ap.parse_args()

    cohort = load_table(Path(args.cohort), REQUIRED_COHORT, "临床表")
    feats = load_table(Path(args.features), ["PatientID"], "特征表")
    if not feats.columns.is_unique:
        dup = feats.columns[feats.columns.duplicated()].tolist()
        raise SystemExit(f"特征表存在重复列名: {dup[:10]}")

    df = merge_tables(cohort, feats)
    df, _ = add_exclusion_flags(df)
    flow, sequential_remaining = sequential_flow(df)

    excluded = (
        df.loc[df["excluded"],
               ["PatientID", "age", "gender", "Overall.Stage", "Histology",
                "Survival.time", "deadstatus.event", "exclude_reason"]]
        .sort_values("PatientID")
        .reset_index(drop=True)
    )

    analysis = (
        df.loc[~df["excluded"]]
        .sort_values("PatientID")
        .reset_index(drop=True)
    )
    if set(analysis["PatientID"]) != set(sequential_remaining["PatientID"]):
        raise SystemExit("逐项筛选结果与 excluded 标记不一致")

    analysis = encode_analysis(analysis)

    if not set(analysis["deadstatus.event"].unique()) <= {0, 1}:
        raise SystemExit(
            f"deadstatus.event 取值异常: {analysis['deadstatus.event'].unique()}"
        )
    if (analysis["Survival.time"] <= 0).any():
        bad = analysis.loc[analysis["Survival.time"] <= 0, "PatientID"].tolist()
        raise SystemExit(f"Survival.time <= 0: {bad[:10]}")
    if analysis["age"].isna().any():
        raise SystemExit("固定分析集仍存在 age 缺失")

    feature_cols = [c for c in feats.columns if c != "PatientID"]
    if args.expect_features >= 0 and len(feature_cols) != args.expect_features:
        raise SystemExit(
            f"特征数不符：{len(feature_cols)} != {args.expect_features}"
        )
    feature_matrix = analysis[feature_cols].apply(pd.to_numeric, errors="coerce")
    bad_cols = feature_matrix.columns[feature_matrix.isna().any()].tolist()
    if bad_cols:
        raise SystemExit(f"特征表存在缺失或非数值列: {bad_cols[:10]}")
    if not np.isfinite(feature_matrix.to_numpy(dtype=float)).all():
        raise SystemExit("特征表存在 NaN/inf")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    analysis_path = out_dir / "analysis_set.csv"
    excluded_path = out_dir / "excluded_patients.csv"
    features_path = out_dir / "feature_columns.txt"

    analysis[ANALYSIS_COLS].to_csv(analysis_path, index=False)
    excluded.to_csv(excluded_path, index=False)
    pd.Series(feature_cols).to_csv(features_path, index=False, header=False)

    report = build_report(args, df, analysis, excluded, flow, feature_cols)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(report, encoding="utf-8")

    events = int(analysis["deadstatus.event"].sum())
    print("==== analysis set ====")
    print(f"原始 {len(df)} 例；排除 {len(excluded)} 例；分析集 {len(analysis)} 例")
    print(f"events: {events}；censored: {len(analysis) - events}；"
          f"特征: {len(feature_cols)}")
    print(f"年龄: 中位 {analysis['age'].median():.1f} "
          f"(IQR {analysis['age'].quantile(0.25):.1f}–"
          f"{analysis['age'].quantile(0.75):.1f})")
    if len(excluded):
        print("排除原因：")
        for reason, count in excluded["exclude_reason"].value_counts().items():
            print(f"  - {reason}: {count}")
    print(f"分析集: {analysis_path}")
    print(f"排除清单: {excluded_path}")
    print(f"特征列: {features_path}")
    print(f"报告: {args.out}")

    if args.expect_n >= 0 and len(analysis) != args.expect_n:
        raise SystemExit(
            f"分析集例数不符：{len(analysis)} != {args.expect_n}（见报告 §3）"
        )
    if args.expect_events >= 0 and events != args.expect_events:
        raise SystemExit(
            f"事件数不符：{events} != {args.expect_events}（见报告 §3）"
        )


if __name__ == "__main__":
    main()
