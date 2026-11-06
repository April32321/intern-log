# 复现目标（Aerts et al. 2014）

> 本文件只记录**论文原始目标值 + 出处 + 复现协议**。
> 复现结果由 D18 填写；未核实的数字一律标「待核实」，不使用推测值。

## 0. 范围

- 论文总队列：**1,019 例**，来自 7 个数据集（肺癌 + 头颈癌），
  即 31 + 21 + 422 + 225 + 136 + 95 + 89。
- 本项目可用数据：**Lung1，422 例**（TCIA `NSCLC-Radiomics`，
  数据集 DOI `10.7937/K9/TCIA.2015.PF0M9REI`）。
- **Lung1 是论文的训练集，不是验证集。**
- 本项目无 Lung2 / H&N1 / H&N2，**不做外部验证**，也不声称复现
  论文的 0.65 / 0.69 / 0.69。
- 复现级别：**方法级复现**（PyRadiomics + Cox），不是数值级复现。

## 1. 论文基本信息

| 项 | 内容 |
|---|---|
| 标题 | Decoding tumour phenotype by noninvasive imaging using a quantitative radiomics approach |
| 作者 | Aerts HJWL, et al. |
| 期刊 | *Nature Communications* |
| 年份 / 卷号 | 2014；**5**:4006 |
| DOI | `10.1038/ncomms5006` |
| 更正 | Corrigendum：`10.1038/ncomms5644`（2014-08-07），引用数值前需核对 |
| 数据来源 | TCIA `NSCLC-Radiomics`（Lung1），DOI `10.7937/K9/TCIA.2015.PF0M9REI` |

## 2. 原论文报告结果（逐字抄录 + 出处）

| Dataset | Role | N | C-index | 原文逐字 | 出处 |
|---|---|---:|---:|---|---|
| Lung1 | Training | 422 | **主文未报告** | — | Results「Prognostic validation of radiomic signature」；待查 Supplementary Table 1 |
| Lung2 | Validation | 225 | 0.65 | "CI=0.65, *P*=2.91 × 10−09, Wilcoxon test" | Results「Prognostic validation of radiomic signature」+ Fig. 4a |
| H&N1 | Validation | 136 | 0.69 | "CI=0.69, *P*=7.99 × 10−07, Wilcoxon test" | 同上 |
| H&N2 | Validation | 95 | 0.69 | "CI=0.69, *P*=3.53 × 10−06, Wilcoxon test" | 同上 |

补充事实（同段）：

- 论文只在三个独立验证集报告 signature 的 C-index；
- 训练集 Lung1 上，作者计算过 100 个候选特征各自的 C-index 用于选特征，
  但**没有在正文报告 4 特征 signature 在 Lung1 的 C-index**；
- 训练集数值可能在 Supplementary Table 1（signature / volume / TNM 对比表）中，
  需查补充材料后补填。

## 3. 目标 signature（4 个特征）

| 特征（正文名称） | 类别 | 原文编号 | 说明 |
|---|---|---|---|
| Statistics Energy | 一阶强度 | Feature 1 | 反映肿瘤整体密度 |
| Shape Compactness | 形状 | Feature 16 | 肿瘤形状紧凑度 |
| Grey Level Nonuniformity | 纹理 | Feature 48 | 肿瘤内灰度异质性 |
| wavelet Grey Level Nonuniformity HLH | 小波 | Feature Group 4 | HLH 小波分解后的异质性 |

注意：

1. 正文与 Figure 4b / 补充材料的命名可能不同
   （例如 `Statistics Total Energy`、`RLGL Grey Level Nonuniformity` 等），
   映射到 PyRadiomics 前必须逐项核对 Supplementary Methods。
2. **4 个特征的 Cox 权重未在正文给出**，需查补充材料；
   若无法获得，复现时用相同 4 个特征在 Lung1 重新拟合 Cox，并注明权重来源。
3. 论文的特征算法为**自研 Matlab 实现**，PyRadiomics 中同名特征不保证等价。

## 4. 复现范围与可比性

| Dataset | 论文 C-index | 本项目结果 | 可比性 |
|---|---:|---|---|
| Lung1 | 主文未报告（待查 Supplementary Table 1） | apparent（全量拟合）+ 5-fold 交叉验证均值 ± SD | 仅 apparent 与论文训练集值同口径；交叉验证值**不可直接相减** |
| Lung2 | 0.65 | **N/A（无数据）** | 否 |
| H&N1 | 0.69 | **N/A（无数据）** | 否 |
| H&N2 | 0.69 | **N/A（无数据）** | 否 |

`Difference = Reproduced − Paper` 只在上表「可比性 = 是/部分」的格子计算；
其余写 `N/A`，不得用 `TBD` 暗示以后能补。

## 5. D18 评估协议（先定后跑）

- **内部验证**：Lung1 上 5-fold 交叉验证 × 5 次重复，按事件分层；
- **特征选择只在训练折内进行**，测试折不参与任何筛选或调参；
- **主指标**：测试折 C-index 的均值 ± SD（保留 3 位小数）；
- **另报表观 C-index**：全量拟合后在 Lung1 上计算，明确标注 `apparent`；
- 校准图与 IBS 作为次要指标，具体时间点在 D18 再定；
- 不因结果好坏更换划分、指标或特征集；任何偏离都要在日志中写明理由。

## 6. 待核实事项

- [ ] 查 Supplementary Table 1：Lung1 训练集 C-index 及 signature vs volume / TNM 对比；
- [ ] 查 Supplementary Methods：4 个特征的数学定义与 Feature 1/16/48/Group 4 编号；
- [ ] 查补充材料：signature 的 4 个 Cox 系数（权重）是否公开；
- [ ] 核对 Corrigendum（`10.1038/ncomms5644`）是否影响 C-index 数值；
- [ ] 核对 Figure 4b 的特征标注与正文命名差异；
- [ ] 确认 PyRadiomics 与原文 Matlab 实现的参数差异（重采样、离散化、小波）；
- [ ] 记录 D18 实际使用的软件版本、特征提取参数与随机种子；
- [ ] 确认 545 的口径：225 + 136 + 95 = 456（生存验证），
      456 + 89（Lung3，基因关联）= 545（Discussion 口径）。

## 7. 复现说明

- 原论文：`All feature algorithms were implemented in Matlab.`
  即自研实现；论文发表于 2014 年，PyRadiomics 尚未发布（2016 年后才出现），
  因此不存在"论文不用 PyRadiomics"的选择问题，而是**只能方法级复现**。
- 原论文特征直接从 DICOM 原始值计算，**未做归一化**，也未按队列/扫描仪校正。
- 数值级复现要求输入影像、ROI、特征定义、预处理、算法实现和模型参数一致；
  缺少原始 Matlab 实现或必要参数时，不得声称完成数值级复现。
- 本项目只在 Lung1 内做内部验证，结论表述为
  「在论文训练集上的内部验证结果」，不得表述为「复现了论文的外部验证」。

## 8. 参考

Aerts HJWL, Rios Velazquez E, Leijenaar RTH, et al.
Decoding tumour phenotype by noninvasive imaging using a quantitative radiomics approach.
*Nature Communications*. 2014;5:4006. DOI: `10.1038/ncomms5006`.

Corrigendum: *Nature Communications*. 2014. DOI: `10.1038/ncomms5644`
（页码/文章号以出版页为准，引用前核对）。

Dataset: TCIA NSCLC-Radiomics (Lung1). DOI: `10.7937/K9/TCIA.2015.PF0M9REI`.
