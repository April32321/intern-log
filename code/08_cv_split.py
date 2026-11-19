"""Day 18：外层交叉验证划分与审计（先定，后跑）

输入：
  results/tables/analysis_set.csv   # 07 固定的建模人群（399 例 / 352 events）

输出：
  results/tables/cv_assignment.csv  # 每个重复中每例所属的测试折
  results/tables/cv_audit.csv       # 每折训练/测试规模与事件数
  results/tables/cv_design.md       # 建模前预先指定的 CV 协议

判据：
  - 外层 RepeatedStratifiedKFold(5 × 10, seed=42)，按 deadstatus.event 分层；
  - 每个重复中，每例恰好进入测试折一次；
  - 每折训练/测试无交集，且训练、测试折均至少包含 1 个 event 与 1 个 censored；
  - 任何一项不满足即以非零码退出。
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import RepeatedStratifiedKFold

REQUIRED = ["PatientID", "deadstatus.event"]


def load_analysis(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise SystemExit(f"缺少分析集: {path}")
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise SystemExit(f"{path} 缺少列: {missing}")
    df["PatientID"] = df["PatientID"].astype(str)
    if not df["PatientID"].is_unique:
        raise SystemExit("分析集 PatientID 不唯一")
    if not set(df["deadstatus.event"].unique()) <= {0, 1}:
        raise SystemExit(
            f"deadstatus.event 取值异常: {df['deadstatus.event'].unique()}"
        )
    return df


def make_splits(df: pd.DataFrame, n_splits: int, n_repeats: int,
                seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    n = len(df)
    event = df["deadstatus.event"].to_numpy()
    X = np.zeros((n, 1), dtype=float)

    cv = RepeatedStratifiedKFold(
        n_splits=n_splits, n_repeats=n_repeats, random_state=seed
    )

    assignment_rows: list[dict] = []
    audit_rows: list[dict] = []

    for i, (train_idx, test_idx) in enumerate(cv.split(X, event)):
        repeat, fold = divmod(i, n_splits)

        train_ids = set(df.iloc[train_idx]["PatientID"])
        test_ids = set(df.iloc[test_idx]["PatientID"])
        if train_ids & test_ids:
            raise SystemExit(f"repeat={repeat} fold={fold}: 训练/测试有交集")
        if len(train_ids | test_ids) != n:
            raise SystemExit(f"repeat={repeat} fold={fold}: 未覆盖全部病例")

        tr_event = int(event[train_idx].sum())
        te_event = int(event[test_idx].sum())
        tr_cens = len(train_idx) - tr_event
        te_cens = len(test_idx) - te_event
        if min(tr_event, te_event, tr_cens, te_cens) <= 0:
            raise SystemExit(
                f"repeat={repeat} fold={fold}: 存在空事件/空删失折 "
                f"(train events={tr_event}, test events={te_event}, "
                f"train censored={tr_cens}, test censored={te_cens})"
            )

        audit_rows.append({
            "repeat": repeat,
            "fold": fold,
            "n_train": len(train_idx),
            "n_test": len(test_idx),
            "events_train": tr_event,
            "events_test": te_event,
            "censored_train": tr_cens,
            "censored_test": te_cens,
            "event_rate_test": te_event / len(test_idx),
        })
        for pid in df.iloc[test_idx]["PatientID"]:
            assignment_rows.append({
                "PatientID": pid, "repeat": repeat, "fold": fold,
            })

    assignment = (
        pd.DataFrame(assignment_rows)
        .sort_values(["repeat", "fold", "PatientID"])
        .reset_index(drop=True)
    )
    audit = (
        pd.DataFrame(audit_rows)
        .sort_values(["repeat", "fold"])
        .reset_index(drop=True)
    )

    # 每个重复中每例恰好被测试一次
    per_repeat = assignment.groupby(["repeat", "PatientID"]).size()
    if not (per_repeat == 1).all():
        raise SystemExit("存在同一重复内被测试多次或未被测试的病例")
    expected_rows = n * n_repeats
    if len(assignment) != expected_rows:
        raise SystemExit(
            f"测试分配行数异常: {len(assignment)} != {expected_rows}"
        )
    return assignment, audit


def build_report(args, df: pd.DataFrame, assignment: pd.DataFrame,
                 audit: pd.DataFrame) -> str:
    n = len(df)
    events = int(df["deadstatus.event"].sum())
    censored = n - events
    n_folds = args.n_splits * args.n_repeats

    def span(values: pd.Series) -> str:
        lo, hi = int(values.min()), int(values.max())
        return str(lo) if lo == hi else f"{lo}–{hi}"

    per_repeat = (
        audit.groupby("repeat")
        .agg(n_test=("n_test", "sum"),
             events_test=("events_test", "sum"),
             censored_test=("censored_test", "sum"),
             folds=("fold", "count"))
        .reset_index()
    )

    lines: list[str] = []
    lines.append("# 交叉验证设计（Day 18）")
    lines.append("")
    lines.append(f"- 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("- 脚本：`code/08_cv_split.py`")
    lines.append("- 状态：**建模前预先指定**（pre-specified）；后续模型不得更改切分")
    lines.append(f"- 分析集：`{args.analysis}`")
    lines.append("- 划分文件：`results/tables/cv_assignment.csv`")
    lines.append("- 审计文件：`results/tables/cv_audit.csv`")
    lines.append("")
    lines.append("## 1. 目标")
    lines.append("")
    lines.append("在没有独立外部验证集的前提下，用重复分层 K 折交叉验证估计"
                 "四个模型的折外性能，并给出带不确定性的性能数字。")
    lines.append("")
    lines.append("## 2. 分析集")
    lines.append("")
    lines.append(f"- n = **{n}**")
    lines.append(f"- events = **{events}**（{events / n:.1%}）")
    lines.append(f"- censored = **{censored}**（{censored / n:.1%}）")
    lines.append("- 特征数：537（列名锁定于 `feature_columns.txt`）")
    lines.append("- 分析集定义见 `analysis_set.md`；本设计不重新筛人")
    lines.append("")
    lines.append("## 3. 外层划分")
    lines.append("")
    lines.append("```python")
    lines.append("RepeatedStratifiedKFold(")
    lines.append(f"    n_splits={args.n_splits}, n_repeats={args.n_repeats}, "
                 f"random_state={args.seed}")
    lines.append(")")
    lines.append("```")
    lines.append("")
    lines.append(f"- 折数：{args.n_splits} × {args.n_repeats} = **{n_folds}** 个外层测试折")
    lines.append("- 分层变量：`deadstatus.event`（1=死亡，0=删失）")
    lines.append(f"- 随机种子：`SEED={args.seed}`")
    lines.append(f"- 每个病人被测试 **{args.n_repeats}** 次（每个重复一次）")
    lines.append(f"- 训练折大小：{span(audit['n_train'])} 例")
    lines.append(f"- 测试折大小：{span(audit['n_test'])} 例")
    lines.append(f"- 测试折 event 数：{span(audit['events_test'])}")
    lines.append(f"- 测试折 censored 数：{span(audit['censored_test'])}")
    lines.append("")
    lines.append("选择理由：5 折使每轮训练集约占 80%，10 次重复降低"
                 "“单次划分运气”带来的估计波动；50 个折外分数足以报告均值±SD。")
    lines.append("")
    lines.append("## 4. 内层划分")
    lines.append("")
    lines.append("每个外层训练折内部再做 5 折分层 CV，仅用于选择超参数"
                 "（LASSO-Cox 的 alpha）与完成折内特征筛选；"
                 "外层验证折不参与任何 fit 或选择。")
    lines.append("")
    lines.append("```python")
    lines.append("StratifiedKFold(")
    lines.append(f"    n_splits={args.n_splits}, shuffle=True,")
    lines.append("    random_state=SEED + 100 * repeat + fold")
    lines.append(")")
    lines.append("```")
    lines.append("")
    lines.append("## 5. 折内处理顺序（下游实现必须遵守）")
    lines.append("")
    lines.append("1. 缺失/方差过滤（只用训练折）")
    lines.append("2. 高度相关去冗余：`|r| > 0.9` 保留一个（只用训练折）")
    lines.append("3. 单变量 Cox 筛选：`p < 0.05`（只用训练折）")
    lines.append("4. 标准化：`StandardScaler.fit(训练折)`")
    lines.append("5. LASSO-Cox：`l1_ratio=1.0`，alpha 由内层 CV 选择")
    lines.append("6. 外层训练折拟合，外层验证折只 `predict`")
    lines.append("")
    lines.append("## 6. 指标与汇总")
    lines.append("")
    lines.append("- 主指标：每个外层测试折的 C-index")
    lines.append("  - `sksurv.metrics.concordance_index_censored(event, time, risk)`")
    lines.append("  - risk 越高表示风险越高，符号不得写反")
    lines.append("- 汇总：50 折的均值 ± 标准差")
    lines.append("- 辅助：中位数 [IQR]、事件分层 log-rank（训练折中位数阈值）")
    lines.append("- log-rank 汇总：中位 p、p<0.05 的折占比；不把 50 个相关 p 值"
                 "当作独立检验合并")
    lines.append("- 次级汇总：OOF（每例在每轮被预测一次，10 轮取平均）"
                 "C-index 与 log-rank")
    lines.append("")
    lines.append("## 7. 模型对照")
    lines.append("")
    lines.append("四个模型必须共用本文件的 50 个外层折：")
    lines.append("")
    lines.append("1. 仅临床")
    lines.append("2. 路线 1：先验 signature（4 特征）")
    lines.append("3. 路线 2：LASSO-Cox（全特征，折内筛选）")
    lines.append("4. 临床 + 影像")
    lines.append("")
    lines.append("## 8. 7:3 留出（可选，非主结果）")
    lines.append("")
    lines.append("如额外做一次固定 7:3 分层留出，仅作为稳定性补充：")
    lines.append("")
    lines.append("```python")
    lines.append("train_test_split(..., test_size=0.3, stratify=event, "
                 f"random_state={args.seed})")
    lines.append("```")
    lines.append("")
    lines.append("7:3 的结果不得替代 5×10 CV 的主结果，也不得用来反向挑选模型。")
    lines.append("")
    lines.append("## 9. 随机种子与复现")
    lines.append("")
    lines.append(f"- 外层：`RepeatedStratifiedKFold(random_state={args.seed})`")
    lines.append("- 内层：`SEED + 100 * repeat + fold`")
    lines.append("- 记录环境版本："
                 f"Python {sys.version.split()[0]}，scikit-learn {sklearn.__version__}")
    lines.append("- 禁止 seed shopping：不得因某个种子结果更好而更换种子")
    lines.append("- 完整测试折分配见 `cv_assignment.csv`；"
                 "训练折 = 该重复中除测试折外的其余病例")
    lines.append("")
    lines.append("## 10. 审计结果")
    lines.append("")
    lines.append(f"- 外层测试折：**{len(audit)}** 个")
    lines.append(f"- 每个重复测试例数：{span(per_repeat['n_test'])}")
    lines.append(f"- 每个重复 event 数：{span(per_repeat['events_test'])}")
    lines.append(f"- 每个重复 censored 数：{span(per_repeat['censored_test'])}")
    lines.append("- 训练/测试无交集、每例每轮恰好测试一次、每折事件与删失均非空：**通过**")
    lines.append("")
    lines.append("| repeat | folds | n_test | events_test | censored_test |")
    lines.append("|---:|---:|---:|---:|---:|")
    for _, row in per_repeat.iterrows():
        lines.append(f"| {int(row['repeat'])} | {int(row['folds'])} | "
                     f"{int(row['n_test'])} | {int(row['events_test'])} | "
                     f"{int(row['censored_test'])} |")
    lines.append("")
    lines.append("## 11. 防泄漏检查清单")
    lines.append("")
    lines.append("- [ ] 外层循环前没有全量 `fit/transform/corr/Coxnet`")
    lines.append("- [ ] 标准化、相关过滤、单变量 Cox、alpha 选择只使用训练折")
    lines.append("- [ ] 验证折只用于 `predict` 与打分")
    lines.append("- [ ] KM 阈值来自训练折中位数，不来自验证折")
    lines.append("- [ ] 四个模型使用同一份 `cv_assignment.csv`")
    lines.append("- [ ] C-index 的 risk 方向正确（越高越差）")
    lines.append("")
    lines.append("## 12. 限制")
    lines.append("")
    lines.append("- 内部 CV 只能说明“在同一队列内换划分”的稳定性，"
                 "不能替代外部验证，也不能证明跨人群可迁移。")
    lines.append("- 50 个折共享病人，折间分数不独立；SD 描述划分波动，"
                 "不能当作 95% 置信区间。")
    lines.append("- 事件率较高（88%），C-index 与 log-rank 的折间波动可能较小，"
                 "报告时仍需给出 SD。")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description="Day18 外层交叉验证划分")
    ap.add_argument("--analysis", default="results/tables/analysis_set.csv")
    ap.add_argument("--out-dir", default="results/tables")
    ap.add_argument("--out", default="results/tables/cv_design.md")
    ap.add_argument("--n-splits", type=int, default=5)
    ap.add_argument("--n-repeats", type=int, default=10)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    if args.n_splits < 2:
        raise SystemExit("n-splits 必须 >= 2")
    if args.n_repeats < 1:
        raise SystemExit("n-repeats 必须 >= 1")

    df = load_analysis(Path(args.analysis))
    assignment, audit = make_splits(
        df, args.n_splits, args.n_repeats, args.seed
    )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    assignment_path = out_dir / "cv_assignment.csv"
    audit_path = out_dir / "cv_audit.csv"
    assignment.to_csv(assignment_path, index=False)
    audit.to_csv(audit_path, index=False)

    report = build_report(args, df, assignment, audit)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(report, encoding="utf-8")

    print("==== CV split ====")
    print(f"分析集 {len(df)} 例；events {int(df['deadstatus.event'].sum())}；"
          f"censored {len(df) - int(df['deadstatus.event'].sum())}")
    print(f"外层: {args.n_splits} × {args.n_repeats} = "
          f"{args.n_splits * args.n_repeats} 折；seed={args.seed}")
    print(f"测试折大小 {audit['n_test'].min()}–{audit['n_test'].max()}；"
          f"events {audit['events_test'].min()}–{audit['events_test'].max()}；"
          f"censored {audit['censored_test'].min()}–{audit['censored_test'].max()}")
    print(f"分配: {assignment_path}")
    print(f"审计: {audit_path}")
    print(f"设计: {args.out}")


if __name__ == "__main__":
    main()
