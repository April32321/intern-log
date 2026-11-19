> 位置说明：本文件由 `nsclc-cox/report.md` 迁入（原 v2.0，2026-11-17）。
> 内文中的 `code/`、`results/`、`journal/`、`logs/` 路径均相对迁移后的仓库根目录（即本目录的上一层）。
> 实习报告正文见仓库根 `report.md`（v3.0）。

---
title: NSCLC-Radiomics（Lung1）生存分析复现报告
author: WJQ
date: 2026-11-17
repo: https://github.com/April32321/nsclc-cox
env: conda radiomics (Python 3.10.22) + 镜像 intern-radiomics:1.0
kilo_version: 7.8.27
model: deepseek/deepseek-flash
---

# NSCLC-Radiomics（Lung1）生存分析复现报告

- 版本：v2.0（2026-11-17）｜v1.1：补图表与 binWidth 敏感性｜v1.0：初稿
- 数据：TCIA NSCLC-Radiomics，Lung1（n=422；主分析 n=399）
- 详细目标值、出处与逐项证据：`results/repro/target.md`（v1.11）

## 1. 摘要

1. **复现层级**：完成**方法级复现**——用公开数据 Lung1、PyRadiomics 3.0.1 与 Cox
   重建与原论文同类型的 radiomic signature 与风险分层，并量化差异来源；
   **不声称**数值逐位一致，也**不声称**复现了论文的外部验证。
2. **主结果**：固定 4 特征 signature 在 Lung1 内做 5 折 × 10 次重复的内部 CV，
   **C-index 0.581 ± 0.038**（50 折）；病人层面 bootstrap **95% CI 0.543–0.608**。
3. **对照模型**：LASSO 0.583 ± 0.035、临床+影像联合 0.581 ± 0.034、
   临床基线 0.530 ± 0.026。三条影像路线基本打平，联合模型没有带来增量。
4. **未达预期的地方**：临床基线 C-index 的 bootstrap CI 为 **0.495–0.558，包含 0.5**，
   不能声称优于随机。原因已核对为**本队列分期判别力弱**（stage_bin 单变量
   HR 0.93 [0.74–1.16]、log-rank p=0.53），不是编码错误。
5. **特征映射**：4 个 signature 特征的单变量方向与论文 Supplementary Fig. 1
   **4/4 一致**（每 1 SD）；Compactness2 为边界证据（HR 0.90，CI 上界 1.00）。
6. **量纲**：Energy 在统一 `HU+1024` 后中位数为论文的 **1.03×**（同数量级）；
   在 HU 口径下为 0.03×，该偏离已作为敏感性分析处理。
7. **稳健性**：binWidth = 10/25/50 HU 下，路线 1 的 C-index 为 0.580/0.581/0.581、
   路线 2 为 0.583/0.583/0.590，变化 ≤0.007（<0.25 SD）。
   但 **LASSO 特征选择随分箱重排且非单调**——性能稳健，不等于某个 signature 稳健。
8. **结论**：方法级复现成立；数值级复现与外部验证不成立，报告中不作此声称。

## 2. 目标与复现范围

### 2.1 目标文献与目标

- 目标文献：Aerts HJWL, et al. *Decoding tumour phenotype by noninvasive imaging
  using a quantitative radiomics approach*. Nature Communications 2014;5:4006。
- 复现对象：论文原 4 特征 radiomic signature（Energy、Compactness2、GLRLM GLN、
  wavelet-HLH GLRLM GLN）及其风险分层能力。
- 论文规模：总队列 1,019 例（Lung1 422 训练 + Lung2 225 / H&N1 136 / H&N2 95 验证）。
- 本项目可用数据：**仅 Lung1（422 例）**，且 Lung1 是论文的**训练集**，不是验证集。

### 2.2 范围：做什么、不做什么

| 项目 | 本项目 | 说明 |
|---|---|---|
| 特征复现 | 做 | PyRadiomics 3.0.1，537 特征；4 个 signature 特征按论文定义映射 |
| signature 权重 | 自拟合 | 论文未公开 4 个 Cox 系数（`target.md` §3.2） |
| 内部验证 | 做 | Lung1 内 5 折 × 10 次重复 CV，全部筛选在训练折内完成 |
| 外部验证 | **不做** | 无 Lung2 / H&N1 / H&N2；不计算与 0.65 / 0.69 / 0.69 的差值 |
| 数值级复现 | **不做** | 论文为自研 Matlab 实现，440 vs 537 特征，不可逐位对齐 |
| 临床可用性 | **不声称** | 单中心回顾性数据 + 内部 CV，不构成临床证据 |

### 2.3 验收判据（`target.md` §6.6）

| 判据 | 状态 | 证据 |
|---|---|---|
| 1. 4 个特征可提取且映射一致 | 满足 | §6.1 |
| 2. 量纲同数量级 | 满足 | Energy 统一 HU+1024 为 1.03× 论文（§5.3） |
| 3. 方向与 Supplementary Fig. 1 一致 | 满足（定性） | 单变量 4/4（§5.2） |
| 4. Track A 的 C-index 95% CI 不含 0.5 | 满足 | signature [0.543, 0.608]（§5.1） |
| 5. 与临床基线同分析集 | 满足 | 四模型统一 399；395 已核对为子集（§6.3） |
| 6. 差异按五类归因写入报告 | 满足 | §6.1–§6.5，汇总见 §6.6 |

## 3. 数据

### 3.1 来源、版本与许可

| 项 | 内容 |
|---|---|
| 数据集 | TCIA **NSCLC-Radiomics**（Lung1） |
| DOI | `10.7937/K9/TCIA.2015.PF0M9REI` |
| 版本 | v4（与本项目 `index.csv` 一致） |
| 许可 | **CC BY-NC 3.0**，仅限非商业研究使用 |
| 影像 | 计划 CT + RTSTRUCT（部分病例含 SEG），原始 DICOM 不进入本仓库 |
| 结局 | `Survival.time`（天）、`deadstatus.event`（1=死亡，0=删失） |

### 3.2 规模与分析集

| 用途 | n | 说明 |
|---|---:|---|
| 原始队列 | 422 | 索引表覆盖全部病例，且本地 DICOM 齐全 |
| 主分析集 | **399** | 排除 age 缺失 22 例、`Overall.Stage` 缺失 1 例 |
| 临床 v2 子集 | 395 | 399 中再排除 T 缺失 1 例、N=4 共 3 例（§6.3） |

主分析集事件数：**352 events / 47 censored**。跨模型比较一律在同一 399 例上进行。

**图 1　输入数据形态**：两例代表性病例的 CT 与 GTV-1 轮廓（红线）。
上：LUNG1-001（GTV-1 = 156.2 cm³）；下：LUNG1-003（34.8 cm³）。
左轴位、右冠状位；窗宽窗位 −1000…400 HU，坐标单位 mm，层厚 3.0 mm。
本图由 `code/13_report_figures.py` 直接读取 DICOM 生成，可复现。

![图1](results/figures/report/data_preview_ct_gtv.png)

### 3.3 队列画像与一致性核对

| 项 | 论文 Table 4 | 本数据集 | 结论 |
|---|---|---|---|
| 男 | 68.7%（290） | 290（68.7%） | 一致 |
| 女 | 31.3%（132） | 132（31.3%） | 一致 |
| I 期 | 22.0% | 93（22.0%） | 一致 |
| II 期 | 9.5% | 40（9.5%） | 一致 |
| IIIa | 26.5% | 112（26.5%） | 一致 |
| IIIb | 41.9% | 176（41.7%） | 差 0.2pp |

93+40+112+176 = 421，比 422 少 1 例，对应分析集中被排除的 stage 缺失病例；
IIIb 的 0.2pp 差异由此解释。**索引表与论文 Lung1 队列一致，不存在接错队列的风险。**

**图 2　生存时间分布（质控）**：n=399，events=352，censored=47。
A 为随访时间直方图（分箱 120 天，按结局分层）；B 为累积死亡曲线（1 − KM），
点线为中位 OS = 555 天。无误差线（A 为计数，B 为点估计）；时间单位：天。

![图2](results/figures/report/qc_survival_time.png)

### 3.4 已知缺陷

1. **无外部队列**：不能评估泛化，不能与论文的 0.65 / 0.69 / 0.69 比较。
2. **完整病例选择**：399 例为完整病例分析，排除的 23 例事件率 91.3%（vs 纳入 88.2%），
   可能带来轻微选择偏倚（`results/tables/analysis_set.md` §6）。
3. **T/N 编码缺失**：T=5（2 例）与 N=4（3 例）的含义已丢失，故 v1 临床模型不含 T/N。
4. **单中心、回顾性**：Lung1 为单一机构放疗队列，扫描协议与人群分布固定。
5. **H&N 队列内部不一致**（与本项目无关但影响引用）：论文正文写 H&N1 = 136，
   Supplementary Table 5 标题为 135；本项目无该队列，仅作引用说明。
6. **特征实现不可比**：论文 440 个特征的编号可复原约 431 个，差额 9 无法从公开材料解释
   （`target.md` §2.4），本项目不使用"440"作为预期特征数。

## 4. 方法

### 4.1 环境与镜像

| 项 | 值 |
|---|---|
| Python | 3.10.22（conda env `radiomics`） |
| 特征提取 | pyradiomics 3.0.1 |
| 影像 I/O | SimpleITK 2.5.6、pydicom 3.0.2、numpy 1.26.4 |
| 生存模型 | lifelines 0.30.0；scikit-survival 0.25.0（Coxnet、C-index） |
| 容器镜像 | `intern-radiomics:1.0`（ID `f7ee2f9daa9e`） |
| 随机性 | 特征提取无随机过程；CV 固定 `seed=42` |

完整环境见 `environment.yml` 与附录 C。

### 4.2 掩膜

- 从 RTSTRUCT 读取 ROI，按名称容错匹配 **GTV-1**（`gtv1` / `gtv` / 含 `pre` 的唯一候选）。
- 将轮廓按物理坐标变换到 CT 连续索引，用 even-odd 规则栅格化到 CT 网格；
  同一 ROI 的多轮廓用 XOR 合并，因此带孔洞的轮廓可正确处理。
- 提取前 `preCrop: true` 以控制内存峰值；已在 `LUNG1-111` 验证与全图提取等价
  （最大相对差 3.8e-14）。

### 4.3 特征

- 537 个特征/例：original 73（firstorder 18 + glcm 24 + glrlm 16 + shape 15）
  + wavelet 464（firstorder 144 + glcm 192 + glrlm 128）。
- `Compactness2` 在 PyRadiomics 3.x 已移除，按 `36π·V²/A³` 由 `MeshVolume`
  与 `SurfaceArea` 现算，列名后缀 `_derived`。
- signature 的 4 个特征映射：

| 论文名称 | 论文编号 | PyRadiomics 列名 |
|---|---|---|
| Statistics Energy | #1 | `original_firstorder_Energy` |
| Shape Compactness 2 | #16 | `original_shape_Compactness2_derived` |
| GLRLM GLN | #47（正文写 48，off-by-one） | `original_glrlm_GrayLevelNonUniformity` |
| wavelet GLN HLH | Group 4 | `wavelet-HLH_glrlm_GrayLevelNonUniformity` |

### 4.4 参数

| 参数 | 值 | 与论文关系 |
|---|---|---|
| `binWidth` | 25 HU | 论文 25 HU；起点规则论文未说明 |
| 重采样 | **不重采样**（原始体素，Lung1 层厚 3 mm） | 论文未重采样 |
| `normalize` | false | 论文未归一化 |
| 小波 | `wavelet`（coif1），8 分解，非降采样 | 论文 Coiflet 1 |
| 纹理方向 | 3D，默认 13 方向平均 | 论文 26 邻域 13 方向 |
| `label` | 1 | — |
| `geometryTolerance` | 1e-4 | — |

### 4.5 切分与折内流程

- 外层 CV：`RepeatedStratifiedKFold(n_splits=5, n_repeats=10, random_state=42)`，
  按 `deadstatus.event` 分层；50 个外层测试折，每例被测试 10 次。
- 每个外层折内依次执行：方差过滤 → 贪心相关过滤（`|r| > 0.9`）→ 单变量 Cox
  `p < 0.05` → 训练折 `StandardScaler` → 模型拟合。
- LASSO 的 alpha 由外层训练折内部再做 5 折选择（内层同样重做筛选与标准化）。
- 测试折只用于预测与打分，不参与任何拟合。

### 4.6 模型

| 代码名 | 输入 | 最终模型 |
|---|---|---|
| `clinical` | age、gender、stage_bin、4 个组织学哑变量 | 惩罚 Cox（7 项） |
| `signature` | 论文固定 4 特征 | 惩罚 Cox（4 项） |
| `lasso` | 537 个影像特征 | 折内 LASSO-Cox 选中特征上重拟合 Cox |
| `combined` | 7 项临床 + 1 个影像分数 | 惩罚 Cox（8 项） |

所有 Cox 使用 0.1 → 1 → 10 的惩罚阶梯，本批 50 折实际生效值均为 **0.1**
（论文未公开惩罚，属口径偏离，见 §6.4）。

### 4.7 指标

- 主指标：外层测试折 **Harrell's C-index**（`lifelines.utils.concordance_index`）。
- 辅助：50 折 `mean ± SD`、median、train−test gap；折内 log-rank p（阈值取该折
  训练集风险中位数）；LASSO 特征入选频率。
- 区间：病人层面 bootstrap（B=2000，seed=42，同一组重采样用于所有模型），
  每个模型取 10 个 repeat 的 C-index 均值作为一个复制，取 2.5/97.5 分位。
- 校准：1 年 / 2 年 OOF 校准（每折 Breslow 基线 + 十分位分组，见 §5.1 图 6）。

## 5. 结果

### 5.1 四个模型的内部 CV（399 例 / 352 events）

| model | C-index（50 折 mean ± SD） | median | train−test gap | log-rank p<0.05 折占比 |
|---|---:|---:|---:|---:|
| clinical | 0.530 ± 0.026 | 0.524 | 0.026 | 10% |
| signature | **0.581 ± 0.038** | 0.583 | 0.003 | 20% |
| lasso | 0.583 ± 0.035 | 0.589 | 0.049 | 18% |
| combined | 0.581 ± 0.034 | 0.585 | 0.057 | 28% |

病人层面 bootstrap（B=2000）：

| model | pooled OOF C-index | 95% CI | 排除 0.5 |
|---|---:|---|---|
| clinical | 0.527 | [0.495, 0.558] | **否** |
| signature | 0.576 | [0.543, 0.608] | 是 |
| lasso | 0.579 | [0.551, 0.608] | 是 |
| combined | 0.577 | [0.548, 0.605] | 是 |

三条影像路线 C-index 相差 ≤0.002、箱线图大幅重叠；联合模型 train−test gap 最大（0.057）。
按训练折风险中位数分高低危后，折外 KM 见图 3；50 折的 C-index 分布见图 4。

**图 3　折外 KM（含风险表）**：固定签名，repeat 0，按该折**训练集**风险中位数分组
（低危 199 / 高危 200），曲线下为 numbers-at-risk 风险表。标题中的 log-rank
p=0.060 是单 repeat 描述值，不是合并检验。
其余三个模型同格式（`km_risktable_{clinical,lasso,combined}.png`）；时间单位：天。

![图3](results/figures/report/km_risktable_signature.png)

**图 4　50 折 C-index 分布**：四个模型各 50 个外层测试折；箱体为 IQR，
红线为中位数，蓝色菱形为均值，散点为单折，虚线为 0.5。
SD 描述折间波动，**不是 95% CI**。

![图4](results/figures/cv/cindex_boxplot.png)

**临床模型为什么只有 0.530**：stage_bin 编码核对（399 例）显示映射正确
（I/II→0、IIIa/IIIb→1），但分期在本分析集中无显著预后效应：单变量 log-rank p=0.53、
HR 0.93 [0.74–1.16]；4 水平 Cox LRT p=0.57；多变量 pooled HR 1.04 [1.00–1.08]。
age（HR 1.20 / 10 岁，p=0.002）与男性（HR 1.29，p=0.032）方向正常，说明生存数据本身一致。
因此 clinical 的 0.530（CI 0.495–0.558）**不是编码错误**，而是本队列分期判别力弱；
报告不把它当作"临床基线应更高"的证据。

**图 5　联合模型森林图**：HR 为跨折逆方差合并，误差条为合并后的解析 95% CI。
50 折共享病人且 Cox 带 0.1 惩罚，该 CI 偏窄，不能替代病人层面 bootstrap；
`radiomics_score` 的 HR 是"每增加 1 个训练折标准差"，不是原始特征单位。

![图5](results/figures/cv/forest_combined.png)

**图 6　1 年 / 2 年校准图**：固定签名，按 `09` 折内流程重拟合后取 10 个 repeat
的平均预测（n=399），按预测生存率十分位分组（每组 39–40 例）。
横轴为组内平均预测，纵轴为该组 KM 观测值；误差线为 KM 的 95% CI（Greenwood），
灰虚线为理想校准。ICI = 0.076（1 年）/ 0.050（2 年）；预测值域较窄（1 年 0.49–0.71）
与 C-index≈0.58 一致，**不据此声称临床可用**。

![图6](results/figures/report/calibration_1y_2y.png)

### 5.2 四个 signature 特征的方向（单变量 Cox，每 1 SD，399 例）

| 特征 | 论文方向 | HR/SD [95% CI] | p |
|---|---|---|---|
| Energy | 高值更差（>1） | 1.13 [1.04–1.22] | 0.0025 |
| Compactness2 | 更紧凑/球形更好（<1） | 0.90 [0.81–1.00] | 0.047 |
| GLRLM GLN | 异质性高更差（>1） | 1.20 [1.09–1.32] | 1.3e-4 |
| wavelet-HLH GLN | 异质性高更差（>1） | 1.21 [1.10–1.33] | 8.5e-5 |

4/4 与论文 Supplementary Fig. 1 一致；Compactness2 为边界证据（CI 上界 1.00）。
方向判据用单变量而非多元系数，原因是多元 HR 会随 Energy 基准重分配（§5.3）。

### 5.3 Energy 量纲（全量 422 例）

| 口径 | 中位 Energy | 相对论文 1.2133×10¹⁰ |
|---|---:|---:|
| HU | 3.78×10⁸ | 0.03× |
| 按各例 DICOM intercept | 5.03×10⁹ | 0.41× |
| 统一 HU+1024 | **1.249×10¹⁰** | **1.03×** |

`LUNG1-001`：2.284×10⁹ → 5.291×10¹⁰，与论文口径一致。
intercept 分布：−1024 共 325 例、0 共 97 例（均为 CT，slope=1）；97 例拉低了按 intercept
的中位数。敏感性：signature C-index 0.5808 ± 0.0377（HU）vs 0.5813 ± 0.0390（stored），
无实质影响；但多元系数重分配（Energy 1.09→1.23、GLN 1.09→0.98、wavelet 1.06→1.00），
故**特征级多元 HR 不作稳健结论**。

### 5.4 binWidth 敏感性（10 / 25 / 50 HU）

固定分析集（399 例）、固定 5×10 折与 seed=42，只改 `binWidth` 重提特征后重跑两条路线。
**这是敏感性分析，不是与论文对齐的协议**（论文口径为 25 HU）；量纲锚点仍以 bw25 为准。

**路线 1：固定 4 特征签名**

| binWidth | C-index (mean ± SD) | median | train−test gap | log-rank p<0.05 | 相对 25 的差 |
|---:|---|---:|---:|---:|---:|
| 10 | 0.580 ± 0.037 | 0.584 | 0.003 | 20% | −0.0005 |
| 25（主结果） | 0.581 ± 0.038 | 0.583 | 0.003 | 20% | — |
| 50 | 0.581 ± 0.038 | 0.579 | 0.003 | 22% | +0.0004 |

四个特征的 pooled HR 方向在三档下完全一致，最大变动 0.033
（`wavelet-HLH GLN` 1.056 → 1.093）；Energy 与 wavelet GLN 间存在轻微系数重分配，
与 §6.2 的 Energy 基准敏感性同源，不影响 C-index。

**路线 2：折内 LASSO-Cox**

| binWidth | C-index (mean ± SD) | median | log-rank p<0.05 | 特征数 mean [min–max] |
|---:|---|---:|---:|---|
| 10 | 0.583 ± 0.033 | 0.582 | 24% | 11.6 [2–47] |
| 25（主结果） | 0.583 ± 0.035 | 0.589 | 18% | 11.3 [2–42] |
| 50 | 0.590 ± 0.033 | 0.592 | 30% | 11.5 [2–53] |

**解释与限制**

1. **判别力对 binWidth 不敏感**：路线 1 全距 0.0009；路线 2 落在 0.583–0.590，
   全距 0.007（约 0.2 个折间 SD，且非单调），均远小于折间 SD（0.033–0.038）。
2. **特征选择不稳定，且不随分箱单调变化**：`wavelet-LHL_glcm_MCC` 的入选率
   在 10/25/50 下为 0.08 / 0.60 / 0.76，`wavelet-LHH_glcm_Correlation` 为
   0.44 / 0.56 / 0.76，`wavelet-HHH_glcm_Idn` 为 0 / 0.32 / 0.04。
   "掉下去又跳回来"说明中频 GLCM 特征的选择接近随机，不是分箱的单调函数。
   稳定的是三个小波一阶特征：`HHL_TotalEnergy`（0.90/0.86/0.84）、
   `LHL_Skewness`（0.82/0.78/0.88）、`LLH_Variance`（0.74/0.68/0.60）。
   **性能稳健 ≠ 某个 signature 稳健**，与 §5.1（三条影像路线打平）及 `day19.md` §3.4 一致。
3. **量纲只看 bw25**：GLN 中位数 bw10 499 / bw25 954 / bw50 1225（论文 984.7）。
   GLN 是计数类量且随灰度级数减少而升高，**不得**用"bw50 偏离论文几倍"评价实现正确性。

**图 7　binWidth 敏感性**：`binWidth` = 10 / 25 / 50 HU 下两条路线的外层测试折 C-index。
固定分析集（n=399）与固定 5×10 折；左为路线 1，右为路线 2；点与折线为 50 折均值，
误差线为折间 SD（**不是 95% CI**），淡色散点为各折，虚线为 C-index = 0.5。

![图7](results/figures/report/binwidth_sensitivity.png)

## 6. 与原文/文献的差异分析

### 6.1 特征实现

- 论文为 Matlab 自研实现，共 440 个特征；本项目为 PyRadiomics 3.0.1，537 个特征
  （original 73 + wavelet 464）。按论文编号复原约 431 个，仍与 440 不可比。
- 4 个 signature 特征的对应关系：
  - `Energy`：同名，`ΣX²`；
  - `Compactness2`：PyRadiomics 3.x 已移除，按 `36πV²/A³` 现算（列名 `_derived`）；
  - `GLN`：对应 GLRLM 的 `GrayLevelNonUniformity`（正文编号 48 / 补充 #47，off-by-one 已记录）；
  - `wavelet-HLH GLN`：列名修正为 `wavelet-HLH_glrlm_GrayLevelNonUniformity`。
- 影响：同名特征不保证数值等价，尤其 Compactness2 的曲面重建（marching cubes vs
  三角化表面积）会带来差异。**但单变量方向 4/4 一致**（§5.2），说明特征映射与方向没有接错。
- 处理：只做方法级复现，不声称特征值逐位一致。

### 6.2 预处理参数

- `binWidth = 25 HU`、不重采样：与论文一致。
- 离散化起点：论文未说明；PyRadiomics 从 ROI 内最小值起算，可能影响纹理类特征
  （GLN、wavelet GLN）的数值，但不改变其方向。
- **Energy 基准**：论文在 `HU+1024`（未转 HU 的存储值）上计算，本项目 `features_all`
  为 HU 口径。
  - 全量 422 例：按各例 DICOM intercept 时中位数 5.03×10⁹（0.41× 论文）；
    统一 HU+1024 时 1.249×10¹⁰（**1.03× 论文**）。
  - intercept：−1024 共 325 例、0 共 97 例（均为 CT，slope=1）；97 例拉低了按 intercept 的中位数。
  - 敏感性：signature C-index 0.5808 ± 0.0377（HU）vs 0.5813 ± 0.0390（stored），
    **无实质影响**；但多元系数重分配（Energy 1.09→1.23、GLN 1.09→0.98、
    wavelet 1.06→1.00），故特征级多元 HR 不稳。
- 处理：主结果保持 HU 口径，stored 作为敏感性；方法节声明该偏离。

### 6.3 队列版本

- 论文 Lung1 为 422 例；本项目主分析为 399 例（age 缺失 22 + stage 缺失 1）。
- 临床 v2 的 395 例子集**已核对**：395 ⊂ 399，差异为 4 例——
  `LUNG1-085`（T 缺失）、`LUNG1-167` / `LUNG1-232` / `LUNG1-292`（N=4，含义丢失）。
  事件数 352 → 348。
- 本项目没有 Lung2 / H&N1 / H&N2，**无法**复现论文的 0.65 / 0.69 / 0.69。
- 422 例 signature-only 尚未运行，列为待补敏感性。
- 处理：所有跨模型比较统一用 399 例；任何 395 的数值都单独标 n 与 CV。

### 6.4 切分方式

- 论文为 5 折 × 5 次重复；本项目为 5 折 × 10 次重复（建模前改，避免事后挑选）。
  主结果为 5×10；5×5 未运行。
- 论文是"Lung1 训练 + 外部队列验证"；本项目是 **Lung1 内部 CV**，每折重新拟合，
  没有锁定阈值或外部队列。
- 50 折共享病人，`mean ± SD` 描述折间波动，**不是 95% CI**；bootstrap CI 只反映
  病人抽样，不含折划分/模型拟合变异。
- 论文未公开 Cox 惩罚；本项目统一 0.1（阶梯 0.1/1/10 实际均停在 0.1）。
- 影响：内部 CV 的 C-index 与论文的外部验证 C-index **不可直接相减**。

### 6.5 指标定义

- C-index 定义一致（Harrell's C）。
- 论文只报告外部队列的 C-index（Lung2 0.65、H&N1 0.69、H&N2 0.69），
  **未报告 Lung1 训练集 C-index**，因此 `Difference = 本项目 − 论文` 没有可对齐的单元格，
  `target.md` §5 标为 N/A。
- 本项目补充了论文没有的口径：50 折 mean ± SD、pooled OOF bootstrap CI、
  log-rank 显著折占比、OOF 校准；并列时必须标清口径。
- 论文用 100 次 bootstrap + Wilcoxon 比较模型；本项目用 2000 次病人层面 bootstrap
  给 CI，方法不同，不直接比较显著性。

### 6.6 差异来源汇总表

| 差异来源 | 我们的设置 | 论文/文献设置 | 预期影响方向 | 是否验证 |
|---|---|---|---|---|
| 特征实现 | PyRadiomics 3.0.1，537 特征 | 自研 Matlab，440 特征 | 数值不可比 | 不可逐位验证；**方向 4/4 一致**（§5.2） |
| 重采样 spacing | **不重采样**，原始体素（Lung1 层厚 3 mm） | 未重采样（Suppl. Methods 无 resampling） | 无 | 已对齐；本项**未使用** 1×1×1 mm |
| binWidth | 25 HU，起点为 ROI 内最小值 | 25 HU，起点未说明 | 纹理数值（GLN 等） | 已做 **10/25/50 敏感性**（§5.4）；起点不可验证 |
| ROI 定义 | RTSTRUCT 的 GTV-1 栅格化到 CT 网格，全量 3D | 医生在融合 PET-CT 勾画的 GTV；TCIA 发布同批 delineation | 边界 → 形状类（Compactness2） | 同源可对齐；形状实现差异见 §6.1 |
| 队列版本 | 399 例（422 排除 age 缺失 22、stage 缺失 1） | 422 例（Lung1 训练集） | 病例集合不同 | 395⊂399 已核对（§6.3）；无外部队列 |
| 事件/随访定义 | `deadstatus.event`（1=死亡）、`Survival.time`（天） | 同源 TCIA 结局字段 | 删失处理 | 已对齐（同一数据源）；删失 47/399 |
| 指标定义 | Harrell's C；50 折 mean ± SD；病人层面 bootstrap CI | 仅报告外部验证 C-index | 口径不同 | 已记录；不计算 `Difference`（§6.5） |

上表 7 项中，重采样、ROI 来源、事件定义三项已对齐；binWidth 与指标口径已量化；
特征实现与队列版本不可逐位对齐。**没有任何一项需要靠调参掩盖。**

### 6.7 结论

- 上述五类差异可以解释"为什么不能数值级复现"，但没有一条改变主要方向性结论：
  - 4 特征方向 4/4 与论文一致；
  - Energy 量纲在论文口径下为 1.03×；
  - signature 的 C-index 显著高于 0.5（95% CI 0.543–0.608）；
  - binWidth 10–50 HU 内判别力稳定。
- **方法级复现成立**；数值级复现与外部验证**不成立**，报告中不得声称。

## 7. 局限

1. **单中心、回顾性**：Lung1 为单一机构放疗队列，扫描协议、勾画习惯与人群分布固定，
   结论不能外推到其他中心。
2. **样本量有限且为完整病例**：399 例 / 352 events；排除的 23 例事件率更高（91.3%），
   存在轻度选择偏倚。所辖事件数虽足以拟合 4 特征模型，但对高维 LASSO 而言仍偏小，
   这也是特征选择不稳定的根本原因。
3. **无外部验证**：不具备 Lung2 / H&N1 / H&N2，无法评估泛化，也无法与论文
   0.65 / 0.69 / 0.69 对比。
4. **特征实现不同**：Matlab 自研 vs PyRadiomics，440 vs 537，同名特征不保证数值等价；
   Compactness2 的曲面重建差异无法消除。
5. **临床基线弱且 CI 含 0.5**：不能声称临床模型优于随机；原因是本队列分期判别力弱。
6. **区间口径有限**：50 折 `mean ± SD` 不是 95% CI；bootstrap CI 只反映病人抽样，
   不含模型拟合与折划分变异。
7. **校准为内部 OOF**：预测值域窄（1 年 0.49–0.71），不能替代外部校准。
8. **未完成项**：422 例 signature-only、5×5 重复敏感性、apparent C-index；
   其中前两项属可选稳健性检查，不影响主结论。

## 8. 可复现性声明

### 8.1 一键重跑（在项目根目录、`radiomics` 环境下）

```bash
cd <PROJECT_ROOT>
conda activate radiomics

RAW=<TCIA_ROOT>     # 本地 DICOM 根目录，目录结构为 <PatientID>/{CT,RTSTRUCT}
PY=python           # 已激活 radiomics 环境

$PY code/02_build_index.py --root "$RAW" --expect 422          # 索引
$PY code/05_extract_features.py --all --raw-root "$RAW" \
    --params code/params.yaml --jobs 4 --chunk 80 --expect 422  # 537 特征
$PY code/07_analysis_set.py --expect-n 399 --expect-events 352  # 固定分析集
$PY code/08_cv_split.py --n-splits 5 --n-repeats 10 --seed 42   # 固定 5×10 折
$PY code/09_cv_models.py                                        # 四模型 CV
$PY code/11_cindex_bootstrap.py                                 # bootstrap CI
$PY code/10_energy_scale_check.py                               # Energy 三口径
$PY code/12_stage_bin_audit.py                                  # stage 编码核对
$PY code/13_report_figures.py                                   # 图 1–7
```

### 8.2 幂等与缓存

- `05` 按 `params_sha256` + `script_sha256` 双校验逐例缓存，中断后重跑自动续算；
  改参数或改脚本会触发重算，**不要在中途编辑 `05_extract_features.py`**。
- `09` 无逐折落盘：50 折全部结束后才写表，中途中断需从头重跑。
- 子集运行（`--models` 不完整或 `--repeats < 10`）强制要求自定义 `--out-dir`，
  避免覆盖主结果。

### 8.3 binWidth 敏感性重跑

先沿用 8.1 中的 `$PY` 与 `$RAW` 两个变量。

```bash
$PY code/05_extract_features.py --all --raw-root "$RAW" \
    --params code/params_bw10.yaml --cache-dir results/cache/features_bw10 \
    --out-name features_all_bw10 --jobs 4 --chunk 80 --expect 422
$PY code/09_cv_models.py --features results/tables/features_all_bw10.csv \
    --models lasso --out-dir results/cache/sens_bw10 --no-figures
$PY code/09_cv_models.py --features results/tables/features_all_bw10.csv \
    --models signature --out-dir results/cache/sens_bw10_sig --no-figures
# bw50 同理，替换 params_bw50.yaml 与两个输出目录
```

### 8.4 关键随机性

| 环节 | 种子 | 说明 |
|---|---|---|
| 外层 CV | 42 | `RepeatedStratifiedKFold`，折分配已固化为 `cv_assignment.csv` |
| LASSO 内层 alpha 选择 | 42（继承） | 内层 5 折 |
| bootstrap | 42 | 2000 次，同一组重采样用于所有模型 |
| 特征提取 | 无 | 无采样、无随机划分 |

## 9. 合规声明

1. **数据许可**：TCIA NSCLC-Radiomics 采用 **CC BY-NC 3.0**，仅限非商业研究使用；
   使用需引用数据集 DOI `10.7937/K9/TCIA.2015.PF0M9REI`。
2. **数据分发**：原始 DICOM（`data/`）、逐例缓存（`results/cache/`）与运行日志
   （`logs/*.log`）均不进入代码仓库，符合数据集再分发限制。
3. **临床用途**：本报告为方法学复现，**不构成医疗器械、诊断或治疗建议**，
   **不得用于临床决策**；所有 C-index 均为内部交叉验证结果。
4. **隐私**：TCIA 数据已去标识；本报告不含任何患者身份信息。
5. **工具许可**：PyRadiomics（BSD-3）、lifelines（MIT）、scikit-survival（GPL-3）
   按其各自许可使用；本仓库代码不包含上述项目的源码。

## 10. 参考文献

1. Aerts HJWL, Rios Velazquez E, Leijenaar RTH, et al. Decoding tumour phenotype by
   noninvasive imaging using a quantitative radiomics approach. *Nature Communications*.
   2014;5:4006. DOI: 10.1038/ncomms5006.
2. Corrigendum to ref. 1. *Nature Communications*. 2014;5:4644.
   DOI: 10.1038/ncomms5644（仅作者姓名拼写更正，不影响数值与特征定义）。
3. TCIA NSCLC-Radiomics (Lung1), v4. DOI: 10.7937/K9/TCIA.2015.PF0M9REI.
4. van Griethuysen JJM, Fedorov A, Parmar C, et al. Computational Radiomics System to
   Decode the Radiographic Phenotype. *Cancer Research*. 2017;77(21):e104–e107.
   DOI: 10.1158/0008-5472.CAN-17-0339.
5. Davidson-Pilon C. lifelines: survival analysis in Python. *Journal of Open Source
   Software*. 2019;4(40):1317. DOI: 10.21105/joss.01317.

## 附录 A 术语表

| 术语 | 含义 |
|---|---|
| **C-index** | 一致性指数，随机取一对可比病人、模型风险排序与真实生存顺序一致的概率；0.5 等于随机 |
| **Harrell's C** | 处理右删失的 C-index 版本，仅在可比对上计算 |
| **OOF** | Out-of-fold，折外预测：每例的预测来自未见过该例的模型 |
| **Cox 比例风险模型** | 半参数生存模型，风险 ∝ exp(βᵀx)，不假定基线风险分布 |
| **Breslow 估计** | 由 Cox 模型估计基线累积风险的常用方法；本报告用它把风险转成 1y/2y 生存率 |
| **惩罚 Cox** | 在 Cox 似然上加 L2 惩罚；本报告 `penalizer=0.1`，用于稳定小样本拟合 |
| **LASSO-Cox** | L1 惩罚的 Cox，可把系数压到 0，从而在折内做特征选择 |
| **alpha** | LASSO 的正则化强度；越大越稀疏。本报告用内层 5 折 CV 选择 |
| **binWidth** | 影像灰度离散化箱宽（HU）；越小级数越多，纹理矩阵越稀疏 |
| **GLCM** | 灰度共生矩阵，描述二阶纹理（本报告含 24 个 original 特征） |
| **GLRLM** | 灰度游程矩阵，描述同灰度连续游程（含 16 个 original 特征） |
| **GLN** | Gray Level Non-Uniformity，灰度分布不均匀性；本 signature 的 2 个纹理特征用它 |
| **Compactness2** | 形状紧致度 `36πV²/A³`；球体为 1，越不规则越小 |
| **wavelet-HLH** | Coiflet 1 小波在 H-L-H 三个方向的分解子带 |
| **ICI** | Integrated Calibration Index，|观测−预测| 按样本量加权平均；越小校准越好 |
| **train−test gap** | 训练折 C-index 减测试折 C-index，描述乐观偏差 |
| **bootstrap CI** | 病人有放回重采样得到的区间；本报告 B=2000，反映抽样不确定性 |

## 附录 B 关键数字—来源对照表

`mean ± SD` 均为 50 折折间波动；`[a, b]` 为 bootstrap 95% CI。

| # | 数字 | 含义 | 来源（文件 / 列） |
|---:|---|---|---|
| 1 | 0.581 ± 0.038 | signature 5×10 折测试 C-index | `results/tables/perf.csv` `cindex_mean/sd`（model=signature） |
| 2 | 0.576 [0.543, 0.608] | signature pooled OOF C-index 及其 CI | `results/repro/cindex_bootstrap.csv` `cindex_obs/ci_lower/ci_upper` |
| 3 | 0.583 ± 0.035 | LASSO 路线 C-index | `results/tables/perf.csv`（model=lasso） |
| 4 | 0.530 ± 0.026 | 临床基线 C-index | `results/tables/perf.csv`（model=clinical） |
| 5 | 0.527 [0.495, 0.558] | 临床基线 CI（含 0.5） | `results/repro/cindex_bootstrap.csv`（model=clinical） |
| 6 | 1.03× | Energy 中位数 / 论文中位数（HU+1024） | `results/repro/energy_scale_check.csv`；论文值见 `target.md` §3.1 |
| 7 | 4/4 | 四特征单变量方向一致数 | `results/repro/target.md` §5.4；复算见 `journal/day19.md` §12 |
| 8 | 395 ⊂ 399（差 4 例） | 临床 v2 子集核对 | `journal/day19.md` §15；`results/tables/excluded_patients.csv` |
| 9 | 352 / 47 | 事件数 / 删失数（399 例） | `results/tables/analysis_set.md` §3 |
| 10 | 0.580/0.581/0.581 | 路线 1 在 bw10/25/50 的 C-index | `results/cache/sens_bw10_sig/perf.csv`、`sens_bw50_sig/perf.csv`、`results/tables/perf.csv` |
| 11 | 0.583/0.583/0.590 | 路线 2 在 bw10/25/50 的 C-index | `results/cache/sens_bw10/perf.csv`、`sens_bw50/perf.csv`、`results/tables/perf.csv` |
| 12 | 0.076 / 0.050 | 1y / 2y 校准 ICI | `results/figures/report/calibration_points.csv` |
| 13 | 555 天 | 中位总生存（KM） | `results/tables/analysis_set.csv`；由 `code/13_report_figures.py` 计算 |
| 14 | 537 | 每例特征数（73 original + 464 wavelet） | `results/tables/feature_columns.txt`；`logs/extract_*.log` 的 QC |
| 15 | 0.93 [0.74–1.16], p=0.53 | stage_bin 单变量 HR / log-rank | `results/repro/stage_bin_audit.csv` |
| 16 | 12.3 s/例 | 特征提取单例耗时（暖缓存） | `results/tables/features_all_timing.csv` |

## 附录 C 环境清单与版本

### C.1 软件版本

| 组件 | 版本 | 用途 |
|---|---|---|
| Python | 3.10.22 | 运行时 |
| pyradiomics | 3.0.1 | 特征提取 |
| SimpleITK | 2.5.6 | 影像读写/重采样 |
| pydicom | 3.0.2 | RTSTRUCT 解析 |
| numpy | 1.26.4 | 数值计算 |
| pandas | 见 `environment.yml` | 表格 |
| lifelines | 0.30.0 | Cox、KM、log-rank |
| scikit-survival | 0.25.0 | Coxnet、C-index、校准所需工具 |
| matplotlib | 见 `environment.yml` | 作图 |

### C.2 镜像与环境重建

- 提取阶段镜像：`intern-radiomics:1.0`（镜像 ID `f7ee2f9daa9e`）。
- 环境重建：`conda env create -f environment.yml`（环境名 `radiomics`）。
- 完整依赖锁定见 `environment.yml`；本报告只列直接相关组件。

### C.3 硬件与耗时（参考）

| 环节 | 规模 | 耗时 |
|---|---|---|
| 特征提取（bw25，冷缓存） | 422 例 | 约 47 min（26.3 s/例） |
| 特征提取（bw50，暖缓存） | 422 例 | 约 14 min（7.5 s/例） |
| 四模型 5×10 CV | 200 条模型-折记录 | 2917.6 s（约 49 min） |
| 单模型 LASSO 5×10 CV | 50 折 | 2590.9–3166.1 s |
| signature 5×10 CV | 50 折 | 约 20 s |
| bootstrap（B=2000） | 4 模型 × 10 repeat | 见 `journal/day19.md` §14 |
| 报告用图生成（含校准重拟合） | 7 张 | 约 40 s |
