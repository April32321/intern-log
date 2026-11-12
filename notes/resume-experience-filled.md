# 简历「Research Experience」已填写版

> 基于 2026-11-12（D17）的仓库数据；数字均可在 `results/` 与 `logs/` 中找到出处。
> 三处仍待确认：实习单位、导师姓名、D18 影像模型 C-index。
> 空白模板仍保留在 `notes/resume-experience-template.md`，未改动。

## 1. 英文版（当前可投）

```text
Research Experience

Method-Level Reproduction of a CT Radiomics Survival Model (Aerts et al., 2014)   10/2026–Present
Research Internship Project, [Company / Lab]                    Mentor: [Name]

Objective: Test whether an open-source PyRadiomics pipeline can reproduce the CT-radiomics → Cox
survival workflow of Aerts et al. (Nature Communications, 2014) on the 422-patient Lung1 cohort,
and quantify where it aligns with or departs from the original, unpublished Matlab implementation.

Workloads:
1. Built a reproducible Docker + Conda environment (PyRadiomics 3.0.1 compiled from source, NumPy
   1.26.4, build-time import checks); ingested 26 GB of TCIA DICOM CT/RTSTRUCT data and reconstructed
   GTV-1 masks from RTSTRUCT contours via even-odd rasterization with ROI-name normalization.
2. Implemented an idempotent, chunked multiprocessing pipeline (per-case cache keyed by parameter
   and script SHA-256, pool recycling) that extracts 537 features per case under paper-aligned
   settings (25 HU bin width, no resampling, Coif1 wavelet) at ~25 s/case; diagnosed repeated OOM
   failures and isolated a 297-slice scan exceeding the 8 GB container limit.
3. Rebuilt Kaplan–Meier/log-rank and Cox proportional-hazards baselines with Harrell's C-index,
   5-fold × 5-repeat cross-validation, and Schoenfeld residual checks; cross-checked mask volumes
   against 3D Slicer on a five-case audit and verified serial-vs-parallel outputs agree to
   floating-point precision.

Results: Processed 412 of 422 patients into a 412 × 537 radiomics matrix with zero non-finite
values; Compactness 2 and GLRLM GLN matched the paper's reported Lung1 medians in scale (×1.00,
×0.97), while Energy (×0.03) and wavelet HLH GLN (×1.88) exposed pixel-value and implementation
differences. Clinical baselines reached a 5×5 CV C-index of 0.546 ± 0.030 (n = 395). Audited the
paper's feature definitions, identified three reproducibility pitfalls — Compactness 2 vs. 1, a
GLRLM GLN off-by-one, and Energy vs. TotalEnergy — and scoped the work as a method-level
reproduction, since the paper does not report a Lung1 C-index and does not publish its Cox weights.
```

## 2. 中文版（投国内岗位）

```text
研究经历

CT 影像组学生存模型的方法级复现                                     2026.10–至今
研究实习项目，[单位]                                            导师：[姓名]

研究问题：用开源 PyRadiomics 管线复现 Aerts et al.（Nature Communications, 2014）的
CT 影像组学 → Cox 生存分析流程，并在 422 例 Lung1 队列上量化其与原始 Matlab 实现的异同。

主要工作：
  1. 搭建可重建的 Docker + Conda 环境（源码编译 PyRadiomics 3.0.1、固定 NumPy 1.26.4、
     构建期自检）；处理 26 GB TCIA DICOM CT/RTSTRUCT 数据，用 even-odd 栅格化从 RTSTRUCT
     重建 GTV-1 掩膜，并对 ROI 名称做容错归一化。
  2. 实现幂等、分块的并行特征提取管线（按参数与脚本 SHA-256 逐例缓存、进程池分块回收），
     在 25 HU 分箱、不重采样、Coif1 小波设置下每例提取 537 个特征，约 25 s/例；
     定位并隔离超过 8 GB 容器内存上限的 297 层病例。
  3. 复现 KM/log-rank 与 Cox 比例风险基线，使用 Harrell C-index、5 折 × 5 次重复交叉验证
     与 Schoenfeld 残差检验；对 5 例做 3D Slicer 掩膜体积对照，并验证串行/并行输出在
     浮点精度内一致。

结果：已完成 422 例中的 412 例，构建 412 × 537 特征矩阵，非有限值为 0；Compactness 2 与
GLRLM GLN 的中位数与论文报告的 Lung1 中位数同量级（×1.00、×0.97），Energy（×0.03）与
小波 HLH GLN（×1.88）则反映像素值口径与实现差异。临床基线 5×5 CV C-index 为
0.546 ± 0.030（n = 395）。核对论文特征定义时发现三处复现陷阱——Compactness 2 与 1、
GLRLM GLN 编号 off-by-one、Energy 与 TotalEnergy——并将工作定位为方法级（非数值级）复现，
因为论文未报告 Lung1 C-index，也未公开 Cox 权重。
```

## 3. 三处待确认

| 位置 | 当前写法 | 怎么处理 |
|---|---|---|
| 单位 | `[Company / Lab]` / `[单位]` | 换成实习单位；没有导师就把 `Mentor` 或 `导师` 半边删掉 |
| 导师 | `[Name]` / `[姓名]` | 有则填，无则删 |
| 影像 C-index | 未写入 Results | D18 出结果后按下方替换段补入 |

## 4. D18 后的 Results 替换段

```text
Results: Processed all 422 patients into a 422 × 537 radiomics matrix with zero non-finite values.
The 4-feature Cox signature reached a 5-fold × 5-repeat CV C-index of X.XX ± 0.0X on the same
[395/422]-patient analysis set as the clinical baseline (0.546 ± 0.030). Audited the paper's feature
definitions and identified three reproducibility pitfalls — Compactness 2 vs. 1, a GLRLM GLN
off-by-one, and Energy vs. TotalEnergy — and scoped the work as a method-level reproduction, since
the paper does not report a Lung1 C-index and does not publish its Cox weights.
```

## 5. 数字出处（面试前自查）

| 数字 | 出处 |
|---|---|
| 422 例、26 GB | `data/raw/full` 目录数 + `du -sh` |
| 537 特征/例、24.6 s/例、0 非有限值 | `logs/extract-no058.log` 末尾 |
| 25 HU、不重采样、Coif1 | `code/params.yaml` |
| 412/422；9 例失败 + LUNG1-058 待补算 | `features_all.csv`、`features_all_failures.csv` |
| CV 0.546 ± 0.030 / 0.571 ± 0.024（n = 395） | `results/tables/cox_cv_comparison.csv` |
| signature 中位数 ×1.00 / ×0.97 / ×0.03 / ×1.88 | `logs/extract-no058.log` 末尾 |
| 三个特征定义陷阱 | `results/repro/target.md` §3 |
| Slicer 体积对照 | `results/tables/gtv_volume_check.csv` |
| 297 层 / 151 MB / 8 GB OOM | `journal/day17.md` §二.7 |

## 6. 提交前提醒

- 如果能在投递前补完 10 例并跑 `06_qc_features.py`，把 `412 of 422` 改成 `all 422`，
  再把 `zero non-finite` 升级为 06 报告中的实际缺失率 / 零方差 / 非有限值结果。
- 不要把 `0.65 / 0.69 / 0.69`、`improved`、`numerical reproduction` 写进去。
- 一页简历里这段控制在 12–14 行；超长时优先删掉 Slicer 对照与 26 GB。
