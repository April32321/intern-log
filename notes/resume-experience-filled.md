# 简历「Research Experience」已填写版

> 基于 2026-11-16（D19）的仓库数据；数字均可在 `results/` 与 `logs/` 中找到出处。
> 仅剩两处待确认且无法从仓库信息补齐：实习单位、导师姓名（保留占位符，填好再投）。
> 空白模板仍保留在 `notes/resume-experience-template.md`，未改动。

## 1. 英文版（当前可投）

```text
Research Experience

Method-Level Reproduction of a CT Radiomics Survival Model (Aerts et al., 2014)       10/2026–Present
Research Internship Project, [Company / Lab]                                Mentor: [Name]

Objective: Test whether an open-source PyRadiomics pipeline can reproduce the CT-radiomics → Cox
survival workflow of Aerts et al. (Nature Communications, 2014) on the 422-patient Lung1 cohort, and
quantify how much prognostic signal the radiomic signature adds over routine clinical variables.

Workloads:
1. Built a reproducible Docker + Conda environment (PyRadiomics 3.0.1 compiled from source, NumPy
   1.26.4, build-time import checks); ingested 26 GB of TCIA DICOM CT/RTSTRUCT data and reconstructed
   GTV-1 masks from RTSTRUCT contours via even-odd rasterization with ROI-name normalization.
2. Implemented an idempotent, chunked multiprocessing pipeline (per-case cache keyed by parameter and
   script SHA-256, pool recycling) that extracts 537 features per case under paper-aligned settings
   (25 HU bin width, no resampling, Coif1 wavelet) at ~25 s/case; diagnosed repeated OOM failures and
   isolated a 297-slice scan exceeding the 8 GB container limit.
3. Built a leakage-free evaluation pipeline on a pre-specified 399-patient / 352-event analysis set with
   5-fold × 10-repeat stratified CV (seed 42, 50 held-out folds, ~49 min); variance/correlation
   filtering, univariate Cox screening and LASSO-Cox were all fitted inside each training fold, and
   Harrell's C-index, train−test optimism gap and per-feature selection frequency were reported.

Results: Extracted 537 features for all 422 patients with zero non-finite values; Compactness 2 and
GLRLM GLN matched the paper's reported Lung1 medians in scale (×1.00, ×0.97), while Energy (×0.03) and
wavelet HLH GLN (×1.88) exposed pixel-value and implementation differences. On the fixed 399-patient
set, the paper's 4-feature signature reached a 5×10 CV C-index of 0.581 ± 0.038, versus 0.530 ± 0.026
for clinical variables alone and 0.583 ± 0.035 for in-fold LASSO-Cox. LASSO kept 11.3 features per
fold (range 2–42; 99 features selected at least once, only one above 80%) and barely overlapped the
4 signature features yet matched its performance, so the work is scoped as a method-level reproduction
— Lung1 C-index and Cox weights are unpublished — and supports "radiomics carries signal", not
"this signature is stable".
```

## 2. 中文版（投国内岗位）

```text
研究经历

CT 影像组学生存模型的方法级复现                                              2026.10–至今
研究实习项目，[单位]                                                     导师：[姓名]

研究问题：用开源 PyRadiomics 管线复现 Aerts et al.（Nature Communications, 2014）的
CT 影像组学 → Cox 生存分析流程，在 422 例 Lung1 队列上量化其与原始 Matlab 实现的异同，
并估计影像签名相对常规临床变量的增量判别力。

主要工作：
  1. 搭建可重建的 Docker + Conda 环境（源码编译 PyRadiomics 3.0.1、固定 NumPy 1.26.4、
     构建期自检）；处理 26 GB TCIA DICOM CT/RTSTRUCT 数据，用 even-odd 栅格化从 RTSTRUCT
     重建 GTV-1 掩膜，并对 ROI 名称做容错归一化。
  2. 实现幂等、分块的并行特征提取管线（按参数与脚本 SHA-256 逐例缓存、进程池分块回收），
     在 25 HU 分箱、不重采样、Coif1 小波设置下每例提取 537 个特征，约 25 s/例；
     定位并隔离超过 8 GB 容器内存上限的 297 层病例。
  3. 在预先固定的 399 例 / 352 events 分析集上搭建无泄漏评估管线：5 折 × 10 次重复分层
     交叉验证（seed 42，50 个测试折，约 49 分钟），方差/相关过滤、单变量 Cox 筛选与
     LASSO-Cox 全部在训练折内完成；逐折报告 Harrell C-index、训练−测试乐观偏差与特征入选频率。

结果：422 例全部完成 537 维特征提取，非有限值为 0；Compactness 2 与 GLRLM GLN 的中位数与论文
报告的 Lung1 中位数同量级（×1.00、×0.97），Energy（×0.03）与小波 HLH GLN（×1.88）则反映
像素值口径与实现差异。在固定 399 例分析集上，论文 4 特征签名的 5×10 CV C-index 为
0.581 ± 0.038，仅临床变量为 0.530 ± 0.026，折内 LASSO-Cox 为 0.583 ± 0.035。LASSO 每折
平均选 11.3 个特征（范围 2–42；99 个特征至少入选一次，仅 1 个超过 80%），与 4 个签名特征
几乎不重叠却性能相当；因此工作定位为方法级复现（论文未报告 Lung1 C-index、未公开 Cox 权重），
结论只支持"影像携带预后信号"，不支持"某个签名稳定"。
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
| 422 例、26 GB | `data/raw/full` 目录数；`journal/day08.md` |
| 422 例全部成功、537 特征/例、0 非有限值 | `logs/extract_2026-11-13_1133.log` 末尾 |
| 25 HU、不重采样、Coif1 | `code/params.yaml` |
| ~25 s/例（容器内 20–30 s，实测 23.9 s） | `journal/day17.md` §二.4、§二.7 |
| 297 层 / 151 MB / 8 GB OOM | `journal/day17.md` §二.7 |
| 422 → 399 例 / 352 events / 47 censored | `results/tables/analysis_set.md` §3 |
| 5 折 × 10 次、seed 42、50 测试折 | `results/tables/cv_design.md`、`cv_audit.csv` |
| 四模型 0.530 / 0.581 / 0.583 / 0.581 ± SD | `results/tables/perf.csv`、`journal/day19.md` §3.1 |
| LASSO 11.3 [2–42]、99 特征、1 个 >80% | `results/tables/selection_stability.csv`、`journal/day19.md` §3.3 |
| 2936 s（约 49 分钟） | `journal/day19.md` §2 |
| signature 中位数 ×1.00 / ×0.97 / ×0.03 / ×1.88 | `logs/extract_2026-11-13_1133.log` 末尾 |
| 三个特征定义陷阱（Compactness 2、GLN off-by-one、Energy） | `target.md` §3 |

## 5. 提交前提醒

- 单位、导师占位符填好再投；没有导师就整段删掉右半边，不要留空括号。
- 中英文两版数字必须同步，面试时两种语言的口径要能对上。
- 不要把论文在 Lung2 / H&N1 / H&N2 上的外部验证 C-index（本项目无这些队列，数值见 `target.md`
  §2.1）、`improved` / `outperformed`、`numerical reproduction` 写进去。
- 四个模型是同一 399 例分析集上的内部 5×10 CV 描述性对比，没有配对统计检验；`±` 是折间
  SD，不是 95% CI（50 折共享病人，每例被测试 10 次）。
- 4 个签名特征是论文先验指定，不是在本队列上选出来的，限制句不能删。
- 一页简历里这段控制在 12–14 行；超长时优先删掉 26 GB。
