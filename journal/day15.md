---
day: 15
date: 2026-11-06
theme: 生存分析原理二：Cox、HR、PH 假设 + 临床基线模型
gate: G3
status: 进行中
---

# Day 15｜生存分析原理二：Cox、HR、PH 假设 + 临床基线模型（进行中）

> 今日完成 Cox 概念笔记、临床变量基线 Cox、PH 假设检验与分层敏感性分析。
> 待办：论文精读、`results/repro/target.md`、G3 对照、周复盘、INDEX 回填。

## 今日目标

- 理解 Cox 模型、HR、PH 假设的含义与适用边界；
- 只用临床变量（age、Gender、Histology、Stage）拟合基线 Cox；
- 用 Schoenfeld 残差检验 PH，违规时有补救方案；
- 产出 `results/tables/cox_baseline.csv`，作为 D18 影像模型的对照基准；
- 能区分 C-index、log-rank、校准、IBS 各自回答的问题。

## 进度快照

| 步骤 | 状态 | 说明 |
|---|---|---|
| 1. Cox 概念笔记 | ✅ | `notes/survival-analysis.md` 第 11 节（11.1–11.10），commit `f4ba870` |
| 2. `code/04_cox_baseline.py` | ✅ | 临床变量 Cox + PH 检验 + 分层敏感性分析 |
| 3. `results/tables/cox_baseline.csv` | ✅ | 7 个协变量的 β、HR、95%CI、p |
| 4. `results/tables/cox_ph_test.csv` | ✅ | Schoenfeld 残差检验，stage 违反 PH |
| 5. `results/tables/cox_baseline_stratified.csv` | ✅ | 按 stage 分层的敏感性分析 |
| 6. 论文精读 `notes/paper-aerts2014.md` | ❌ | 未开始 |
| 7. `results/repro/target.md` | ❌ | 未开始，D16 依赖 |
| 8. G3 五项自查 | 🟡 | 前四项已有证据，待汇总 |
| 9. `journal/week3-review.md` | ❌ | 未开始 |
| 10. INDEX 回填 + 收尾 commit | 🟡 | 等论文与 G3 完成后一起做 |

## 今日完成

1. 在 `notes/survival-analysis.md` 新增第 11 节 Cox 专题：
   Cox 公式、Baseline Hazard、HR、PH 假设、Schoenfeld 残差、
   违反 PH 的三种补救（分层 Cox / 时依效应 / AFT）、与 KM 的关系、影像组学应用；
2. 新建 `code/04_cox_baseline.py`，只用 4 类临床变量（age、gender、histology、stage），
   不读取任何影像特征；
3. 完成缺失处理与分析集定义：422 例 → 399 例（排除 age 缺失 22 例、Stage 缺失 1 例），
   Histology 缺失 42 例编码为 `unknown` 保留；
4. 拟合 `CoxPHFitter(penalizer=0.1)`，导出基线表；
5. 用无惩罚副本做 Schoenfeld 残差 PH 检验，发现 stage 违反 PH；
6. 补做按 stage 分层的 Cox，验证其余协变量稳健；
7. 记录表观 C-index，并明确它不能作为验证性能。

## 研究设计与编码

- 数据：`results/tables/cohort.csv`（Lung1，422 例）；
- 结局：`T = Survival.time`（天），`event = deadstatus.event`（1 死亡，0 右删失）；
- 分析集：**399 例，352 事件，47 删失（11.8%）**；
- 排除：`age` 缺失 22 例（5.21%）、`Overall.Stage` 缺失 1 例（0.24%）；
- 缺失值处理：`Histology` 缺失 42 例（9.95%）编码为 `unknown`，未做插补；
- 变量编码：
  - `age`：连续，单位岁；
  - `gender_num`：male=1，female=0；
  - `stage_num`：IIIa/IIIb=1，I/II=0；
  - Histology：腺癌为参考组，其余为 `large`、`nos`、`squamous`、`unknown`；
- 模型：`CoxPHFitter(penalizer=0.1)`，Breslow 基线，7 个协变量。

## Cox 基线结果（n=399，events=352）

| 变量 | β | HR | 95% CI | p |
|---|---:|---:|---|---:|
| age（每 1 岁） | 0.0135 | 1.014 | 1.002–1.026 | 0.024 |
| gender（男 vs 女） | 0.153 | 1.166 | 0.932–1.458 | 0.180 |
| stage（III vs I–II） | 0.036 | 1.036 | 0.821–1.308 | 0.765 |
| hist_large vs 腺癌 | −0.082 | 0.921 | 0.685–1.239 | 0.587 |
| hist_nos vs 腺癌 | −0.063 | 0.939 | 0.665–1.326 | 0.720 |
| hist_squamous vs 腺癌 | 0.110 | 1.116 | 0.843–1.477 | 0.443 |
| hist_unknown vs 腺癌 | 0.082 | 1.085 | 0.714–1.650 | 0.701 |

补充：

- age 每增加 10 岁：HR = exp(10 × 0.0135) ≈ **1.144（1.018–1.290）**，即风险增加约 14%；
- 表观 C-index = **0.553**（训练集内，偏乐观）；
- 全局似然比检验：13.300 on 7 df，p ≈ 0.065；
- 仅 age 达到统计学显著，其余变量 95%CI 均跨 1。

## PH 假设检验（Schoenfeld 残差）

方法：对**无惩罚**的 Cox 副本调用
`proportional_hazard_test(cph, d, time_transform="rank")`；
检验水平 α=0.05，H0 为满足 PH。

| 变量 | 检验统计量 | p | 是否违反 PH |
|---|---:|---:|---|
| age | 0.204 | 0.651 | 否 |
| gender_num | 0.045 | 0.833 | 否 |
| hist_large | 1.735 | 0.188 | 否 |
| hist_nos | 1.171 | 0.279 | 否 |
| hist_squamous | 2.124 | 0.145 | 否 |
| hist_unknown | 0.250 | 0.617 | 否 |
| **stage_num** | **7.544** | **0.006** | **是** |

结论：只有 `stage_num` 违反 PH（p=0.006），其余 6 个变量 p=0.145–0.833，不拒绝 PH。
注意：p≥0.05 只表示"未发现证据"，不等于 PH 一定成立。

## 敏感性分析：按 stage 分层 Cox

- 分层人数：I–II 期 121 例（113 事件），III 期 278 例（239 事件）；
- stage 作为 `strata` 后不再估计统一 HR，各层拥有独立基准风险；
- 分层结果：

| 变量 | HR | 95% CI | p |
|---|---:|---|---:|
| age（每 1 岁） | 1.015 | 1.003–1.027 | 0.016 |
| gender（男 vs 女） | 1.156 | 0.924–1.445 | 0.204 |
| hist_large vs 腺癌 | 0.911 | 0.677–1.225 | 0.536 |
| hist_nos vs 腺癌 | 0.927 | 0.655–1.310 | 0.666 |
| hist_squamous vs 腺癌 | 1.107 | 0.836–1.466 | 0.476 |
| hist_unknown vs 腺癌 | 1.056 | 0.692–1.611 | 0.802 |

对比主模型：age 1.014→1.015、gender 1.166→1.156、histology 0.921–1.116→0.911–1.108，
变化均小于 0.02，说明 **PH 违反主要影响 stage 的平均 HR 解释，其余协变量结论稳健**。

注意：分层模型的 log-likelihood（−1609.8）和 AIC（3231.6）与主模型
（−1831.9 / 3677.8）**不可直接比较**，因为分层似然按层求和，基准不同。

## 结果解释

- age 是唯一显著的临床协变量：年龄越大，瞬时死亡风险越高，效应量温和（每 10 岁约 +14%）；
- gender、histology 在控制其他变量后均无统计学差异；
- stage 的 HR 接近 1 且违反 PH。结合 D14 的 KM 结果（两条曲线在约 1000–1500 天交叉，
  log-rank p=0.532），可以解释为：早期与晚期的风险比随时间变化，单一半参数
  Cox 只能给出被平均掉的 HR，因此 stage 的时变效应不能忽略；
- 表观 C-index=0.553 接近随机，说明"只靠基础临床变量"区分能力很弱，
  这正是 D18 引入影像组学特征、做增量比较的出发点；但该数值不能当作验证性能。

## 指标辨析

| 指标 | 回答什么问题 | 本项目怎么算 |
|---|---|---|
| C-index | 预测风险排序对不对 | 0.5=随机；本日只报表观值，正式值留给 D18 交叉验证 |
| log-rank p | 两组曲线有无差异 | `lifelines.statistics.logrank_test`，D14 已用于 stage 分组 |
| 校准 | 预测的绝对生存率准不准 | KM 分层 vs 预测生存率（后续绘制校准图） |
| IBS | 综合校准 + 区分度 | `sksurv.metrics.integrated_brier_score`，D18 后再用 |

纪律：C-index 必须在**未参与训练的样本**上报告；本日的 0.553 是训练集表观值，
只能作内部参考。

## 产出文件

| 文件 | 内容 |
|---|---|
| `code/04_cox_baseline.py` | 建模、PH 检验、分层敏感性分析 |
| `results/tables/cox_baseline.csv` | 主模型 β、HR、95%CI、p |
| `results/tables/cox_ph_test.csv` | Schoenfeld 残差 PH 检验结果 |
| `results/tables/cox_baseline_stratified.csv` | 按 stage 分层的敏感性分析 |

## 环境与运行

- 环境：`radiomics`（`lifelines 0.30.0`），base 环境未装；
- 必须在项目根目录运行（脚本使用相对路径）：

```bash
/Users/wangjiaqi/miniconda3/envs/radiomics/bin/python code/04_cox_baseline.py
```

- 关键输出：

```text
分析集: n=399, events=352
Concordance = 0.553
PH 检验: stage_num p=0.006（违反），其余 p=0.145–0.833
分层: I–II 121 例（113 事件），III 278 例（239 事件）
```

## 待办（收尾前）

1. 下载 Aerts et al. 2014（DOI `10.1038/ncomms5006`），写 `notes/paper-aerts2014.md`；
2. 把论文报告的 C-index（训练集 / 验证集）逐字抄进 `results/repro/target.md`，
   标注表号/图号；注意 **Lung1 422 例 ≠ 论文队列 1,019 例**；
3. 汇总 G3 五项证据：数据清点、422 例索引表、viewer 定位 GTV-1、
   KM/Cox/HR/C-index 概念、基线 Cox 表；
4. 写 `journal/week3-review.md`（交付 / 卡点及根因 / W4 最该提前准备的一件事）；
5. 回填 `journal/INDEX.md` 的 D15 行并做收尾 commit。

## 验收对照（Day 15）

| 验收标准 | 状态 | 证据 |
|---|---|---|
| Cox 基线表生成，能解释每个 HR | ✅ | `results/tables/cox_baseline.csv`；本日「Cox 基线结果」表 |
| 做了 PH 假设检验并记录结论 | ✅ | `results/tables/cox_ph_test.csv`；stage p=0.006，已补分层 Cox |
| `results/repro/target.md` 有目标指标 + 出处 | ❌ | 待论文精读后填写 |
| 能区分 C-index、log-rank、校准、IBS | ✅ | 本日「指标辨析」表 + 笔记第 11 节 |
| 细节不混淆（2014 / Nat Commun / DOI / 422≠1019） | 🟡 | 待论文笔记落盘后核对 |

## 今日结论

- Cox 模型用 `h(t|X)=h0(t)·exp(βᵀX)` 把协变量效应写成相对风险，
  HR=exp(β) 是核心解释指标，HR>1 为危险因素、HR<1 为保护因素；
- HR 是瞬时风险比，不是死亡概率，也不直接等于生存时间的变化比例；
- PH 假设要求风险比不随时间变化，而不要求风险率恒定；
  本项目用 Schoenfeld 残差检验，stage 违反（p=0.006）；
- 违反 PH 时用分层 Cox、时依项或 AFT；本日以分层 Cox 作敏感性分析，
  其余协变量 HR 变化 <0.02，结论稳健；
- 临床基线模型仅 age 显著（每 10 岁 HR≈1.145），表观 C-index=0.553，
  区分能力有限，为 D18 影像特征增量价值提供对照；
- C-index 必须在未参与训练的样本上报告，本日数值仅为表观值。
