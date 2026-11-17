# 简历「Research Experience」已填写版

> 基于 2026-11-17 report v2.0 的仓库数据；数字均可在 `results/` 与 `logs/` 中找到出处。
> 仅剩两处待确认且无法从仓库信息补齐：实习单位、导师姓名（保留占位符，填好再投）。
> 空白模板仍保留在 `notes/resume-experience-template.md`，未改动。

## 1. 英文版（当前可投）

```text
Research Experience

Method-Level Reproduction of a CT Radiomics Survival Model (Aerts et al., 2014)       10/2026–Present
Research Internship Project, [Company / Lab]                                Mentor: [Name]

Objective: Test whether an open-source PyRadiomics pipeline can reproduce the CT-radiomics → Cox
survival workflow of Aerts et al. (Nature Communications, 2014) on the Lung1 cohort (422 patients;
399 analyzed), and quantify the signature's prognostic signal relative to routine clinical variables.

Workloads:
1. Built a reproducible Docker + Conda environment (PyRadiomics 3.0.1 compiled from source, NumPy
   1.26.4, build-time import checks); ingested the full 422-patient TCIA DICOM CT/RTSTRUCT dataset
   and reconstructed GTV-1 masks from RTSTRUCT contours via even-odd rasterization with ROI-name
   normalization.
2. Implemented an idempotent, chunked multiprocessing pipeline (per-case cache keyed by parameter and
   script SHA-256, pool recycling) that extracts 537 features per case under paper-aligned settings
   (25 HU bin width, no resampling, Coif1 wavelet) at ~26 s/case (cold cache); diagnosed repeated OOM
   failures and isolated a 297-slice scan exceeding the 8 GB container limit.
3. Built a leakage-free evaluation pipeline on a pre-specified 399-patient / 352-event analysis set with
   5-fold × 10-repeat stratified CV (seed 42, 50 held-out folds, ~49 min); variance/correlation
   filtering, univariate Cox screening and LASSO-Cox were all fitted inside each training fold, and
   Harrell's C-index, train−test optimism gap and per-feature selection frequency were reported.

Results: Extracted 537 features for all 422 patients with zero non-finite values. Compactness 2 and
GLRLM GLN matched the paper's Lung1 medians (×1.01, ×0.97); Energy matched at ×1.03 once expressed on
the paper's HU+1024 convention (raw-HU ×0.03 is a sensitivity), while wavelet-HLH GLN remained ×1.88,
reflecting implementation differences. On the fixed 399-patient set, the reconstructed 4-feature
signature (weights self-fitted) reached a 5×10 CV C-index of 0.581 ± 0.038, versus 0.530 ± 0.026 for
clinical variables alone, 0.583 ± 0.035 for in-fold LASSO-Cox, and 0.581 ± 0.034 for the combined
model — no gain over imaging alone. All four features showed the paper-consistent univariate direction
(HR/SD: Energy 1.13, GLN 1.20, Compactness 2 0.90 (borderline), wavelet GLN 1.21), a qualitative check
only. LASSO kept 11.3 features per fold (range 2–42; 99 features selected at least once, only one above
80%) and selected only one of the 4 signature features (8% of folds) yet matched its performance, so
the work is scoped as a method-level reproduction — the paper reported no Lung1 training C-index and
did not publish the Cox weights — and supports "radiomics carries signal", not "this signature is
stable".
```

## 2. 中文版（投国内岗位）

```text
研究经历

CT 影像组学生存模型的方法级复现                                              2026.10–至今
研究实习项目，[单位]                                                     导师：[姓名]

研究问题：用开源 PyRadiomics 管线复现 Aerts et al.（Nature Communications, 2014）的
CT 影像组学 → Cox 生存分析流程，在 Lung1 队列（422 例，主分析 399 例）上量化其与原始
Matlab 实现的异同，并估计影像签名相对常规临床变量的判别力。

主要工作：
  1. 搭建可重建的 Docker + Conda 环境（源码编译 PyRadiomics 3.0.1、固定 NumPy 1.26.4、
     构建期自检）；处理完整 422 例 TCIA DICOM CT/RTSTRUCT 数据，用 even-odd 栅格化从 RTSTRUCT
     重建 GTV-1 掩膜，并对 ROI 名称做容错归一化。
  2. 实现幂等、分块的并行特征提取管线（按参数与脚本 SHA-256 逐例缓存、进程池分块回收），
     在 25 HU 分箱、不重采样、Coif1 小波设置下每例提取 537 个特征，约 26 s/例（冷缓存）；
     定位并隔离超过 8 GB 容器内存上限的 297 层病例。
  3. 在预先固定的 399 例 / 352 events 分析集上搭建无泄漏评估管线：5 折 × 10 次重复分层
     交叉验证（seed 42，50 个测试折，约 49 分钟），方差/相关过滤、单变量 Cox 筛选与
     LASSO-Cox 全部在训练折内完成；逐折报告 Harrell C-index、训练−测试乐观偏差与特征入选频率。

结果：422 例全部完成 537 维特征提取，非有限值为 0；Compactness 2 与 GLRLM GLN 的中位数与论文
报告的 Lung1 中位数同量级（×1.01、×0.97）；Energy 在论文的 HU+1024 口径下为 ×1.03（原始 HU
口径 ×0.03 为敏感性），小波 HLH GLN 为 ×1.88，反映实现差异。在固定 399 例分析集上，重建的
4 特征签名（权重自拟合）的 5×10 CV C-index 为 0.581 ± 0.038，仅临床变量为 0.530 ± 0.026，
折内 LASSO-Cox 为 0.583 ± 0.035，临床+影像联合为 0.581 ± 0.034（相对单独影像无增量）。4 个
签名特征的单变量风险方向均与论文 Supplementary Fig. 1 一致（HR/SD：Energy 1.13、GLN 1.20、
Compactness 2 0.90（边界）、小波 GLN 1.21），但仅为定性核对。LASSO 每折平均选 11.3 个特征
（范围 2–42；99 个特征至少入选一次，仅 1 个超过 80%），4 个签名特征中只有 1 个被选中
（8% 的折）却性能相当；因此工作定位为方法级复现（论文未报告 Lung1 训练集 C-index、未公开
Cox 权重），结论只支持"影像携带预后信号"，不支持"某个签名稳定"。
```

## 3. 待确认

| 位置 | 当前写法 | 怎么处理 |
|---|---|---|
| 单位 | `[Company / Lab]` / `[单位]` | 换成实习单位；仓库里没有该信息，不要编造 |
| 导师 | `[Name]` / `[姓名]` | 有则填；没有导师就把 `Mentor: [Name]` 与 `导师：[姓名]` 整段删掉，不留空括号 |
| 时间 | `10/2026–Present` / `2026.10–至今` | 实习结束时改成具体结束月，中英同步 |

## 4. 数字出处（面试前自查）

| 数字 | 出处 |
|---|---|
| 422 例；完整发布 35.78 GB（含 SEG） | `data/raw/full` 目录数；`data/README.md` |
| 422 例全部成功、537 特征/例、0 非有限值 | `logs/extract_2026-11-13_1133.log` 末尾 |
| 25 HU、不重采样、Coif1 | `code/params.yaml` |
| ~26 s/例（冷缓存 26.3 s；暖缓存 12.3 s） | report 附录 B/C；`journal/day17.md` §二.4 |
| 297 层 / 151 MB / 8 GB OOM | `journal/day17.md` §二.7 |
| 422 → 399 例 / 352 events / 47 censored | `results/tables/analysis_set.md` §3 |
| 5 折 × 10 次、seed 42、50 测试折 | `results/tables/cv_design.md`、`cv_audit.csv` |
| 四模型 0.530 / 0.581 / 0.583 / 0.581 ± SD | `results/tables/perf.csv`、`journal/day19.md` §3.1 |
| LASSO 11.3 [2–42]、99 特征、1 个 >80% | `results/tables/selection_stability.csv`、`journal/day19.md` §3.3 |
| 4 签名特征中仅 1 个被 LASSO 选中（4/50 折 = 8%） | `results/tables/selection_stability.csv` |
| 4 特征单变量方向 4/4 一致、HR/SD 1.13 / 1.20 / 0.90 / 1.21 | report §5.2、`results/repro/target.md` §5.4 |
| 2936 s（约 49 分钟）；系数口径重跑 2917.6 s | `journal/day19.md` §2、§11；`results/tables/perf.md` §1 |
| signature 中位数 ×1.01 / ×0.97；Energy ×1.03（HU+1024）/ ×0.03（HU）；小波 ×1.88 | `logs/extract_2026-11-13_1133.log` 末尾；report §5.3 |
| 三个特征定义陷阱（Compactness 2、GLN off-by-one、Energy） | `results/repro/target.md` §3 |

## 5. 提交前提醒

- 单位、导师占位符填好再投；没有导师就整段删掉右半边，不要留空括号。
- 中英文两版数字必须同步，面试时两种语言的口径要能对上。
- 不要把论文在 Lung2 / H&N1 / H&N2 上的外部验证 C-index（本项目无这些队列，数值见 `target.md`
  §2.1）、`improved` / `outperformed`、`numerical reproduction` 写进去。
- 四个模型是同一 399 例分析集上的内部 5×10 CV 描述性对比，没有配对统计检验；`±` 是折间
  SD，不是 95% CI（50 折共享病人，每例被测试 10 次）。
- 4 个签名特征是论文先验指定，不是在本队列上选出来的，限制句不能删。
- 一页简历里这段控制在 12–14 行；超长时优先压缩数据规模描述。
