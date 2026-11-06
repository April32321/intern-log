# Aerts et al. (2014) 论文精读笔记

> 论文：Decoding tumour phenotype by noninvasive imaging using a quantitative radiomics approach.
> *Nature Communications* 2014;5:4006. DOI `10.1038/ncomms5006`。
> 本笔记依据正文、图注与方法段整理；标「待核实」的内容需回原文或补充材料确认。

## 1. 论文基本信息

| 项 | 内容 |
|---|---|
| 标题 | Decoding tumour phenotype by noninvasive imaging using a quantitative radiomics approach |
| 作者 | Aerts HJWL, Rios Velazquez E, Leijenaar RTH, et al. |
| 期刊 | *Nature Communications* |
| 年份 / 卷号 | 2014；**5**:4006 |
| DOI | `10.1038/ncomms5006` |
| 更正 | Corrigendum：`10.1038/ncomms5644`（2014-08-07），引用数值前需核对 |
| 研究方向 | Radiomics、Survival Analysis、Radiogenomics |
| 本项目数据 | TCIA `NSCLC-Radiomics`（Lung1），422 例，DOI `10.7937/K9/TCIA.2015.PF0M9REI` |

## 2. 研究问题

1. 能否从常规 CT 图像中提取定量影像特征，用于预测癌症患者的生存？
2. 影像组学特征能否在独立的肺癌和头颈癌队列中保持预后能力？
3. 影像组学特征是否与肿瘤的基因表达模式相关？

核心思路：CT → 大量定量特征 → 稳定性筛选 → 特征降维 → Cox 生存模型 →
独立验证 → 基因表达关联。

## 3. 数据集与患者队列

论文报告 **7 个数据集、共 1,019 例**肺癌及头颈癌患者。

| 数据集 | 样本量 | 用途 |
|---|---:|---|
| RIDER | 31 | 重测稳定性（test–retest，约 15 分钟间隔） |
| Multiple delineation | 21 | 勾画者间稳定性（5 位肿瘤科医生） |
| Lung1 | **422** | **训练集**：特征选择 + signature 拟合 |
| Lung2 | 225 | 独立肺癌验证 |
| H&N1 | 136 | 头颈鳞癌验证 |
| H&N2 | 95 | 第二组头颈鳞癌验证 |
| Lung3 | 89 | 影像–基因表达关联 |
| 合计 | **1,019** | 31 + 21 + 422 + 225 + 136 + 95 + 89 |

重要说明：

- **Lung1 = 422 例是训练集，不是全部 1,019 例**，本项目用的就是它；
- 生存验证队列为 Lung2 + H&N1 + H&N2，共 **456 例**；
- Discussion 提到的 **545 例**独立验证 = 456 + 89（Lung3，基因关联），
  口径包含 Lung3，并非生存验证人数；
- 两个稳定性数据集只用于特征稳定性评估，不参与生存验证。

## 4. 影像组学特征

共 **440 个定量特征**，分为四类：

| 特征类别 | 中文名称 | 描述内容 |
|---|---|---|
| Intensity | 一阶强度特征 | 肿瘤体素灰度值及其统计分布 |
| Shape | 形状特征 | 几何形状、球形度、紧凑度 |
| Texture | 纹理特征 | 肿瘤内部灰度分布与空间异质性 |
| Wavelet | 小波特征 | 不同频率范围内的强度与纹理信息 |

其中纹理与小波特征用于刻画肿瘤内部异质性，是 signature 的核心信息来源。

## 5. Radiomic Signature

### 5.1 特征选择流程

1. 从 CT 提取 440 个特征；
2. 用 RIDER（ICC）和 Multiple delineation（Friedman 检验）评估稳定性；
3. 综合两类稳定性排名，取最稳定的 **100 个**特征；
4. 在 Lung1 训练集上计算这 100 个特征各自的 C-index；
5. 从四个特征类别中**各选预后最好的 1 个**；
6. 4 个特征组成多变量 Cox 比例风险模型，权重在 Lung1 拟合；
7. 在 Lung2、H&N1、H&N2 做独立验证。

### 5.2 最终四个特征

| 特征（正文名称） | Figure 4b / 补充材料标注（待核对） | 类别 | 原文编号 |
|---|---|---|---|
| Statistics Energy | Statistics (Total) Energy | 一阶强度 | Feature 1 |
| Shape Compactness | Shape Compactness | 形状 | Feature 16 |
| Grey Level Nonuniformity | RLGL Grey Level Nonuniformity | 纹理 | Feature 48 |
| wavelet Grey Level Nonuniformity HLH | Wavelet HLH RLGL GLNU | 小波 | Feature Group 4 |

说明：

- 正文使用的是 `Statistics Energy` 和 `Grey Level Nonuniformity`；
  Figure 4b 可能使用 `Statistics Total Energy`、`RLGL Grey Level Nonuniformity`
  等标注，**属于命名差异，精确数学定义必须查 Supplementary Methods**；
- **4 个特征的 Cox 权重（系数）未在正文给出**，需查补充材料；
  若无法获得，复现时用相同 4 特征在 Lung1 重新拟合，并注明权重来源；
- 特征算法为作者自研 Matlab 实现，PyRadiomics 中同名特征不保证等价。

## 6. 特征提取软件与参数

### 6.1 原论文使用的软件

原文 Methods 明确写道：

> All feature algorithms were implemented in Matlab.

- 原论文采用研究团队**自行实现**的特征算法；
- 论文发表于 2014 年，PyRadiomics 尚未发布（2016 年后才出现），
  因此不存在"作者选择不用 PyRadiomics"的问题，而是当时**只能自研**；
- 特征算法的详细定义在 Supplementary Methods，正文未完整给出。

### 6.2 复现时需要核实的参数

| 参数 | 需要核实的内容 |
|---|---|
| Feature definitions | 数学定义是否一致（Feature 1/16/48/Group 4） |
| Image preprocessing | 是否重采样、滤波、插值 |
| Gray-level discretization | bin width / bin count 的定义 |
| Texture matrix | 三维计算方式、方向合并方式 |
| Wavelet decomposition | 小波类型、滤波与边界处理 |
| Segmentation / ROI | 肿瘤掩膜来源与勾画规则是否一致 |

原论文明确说明：影像组学特征**未在任何数据集上归一化**，
只使用直接从 DICOM 图像计算出的原始数值。但这不等于所有预处理和
特征参数都已完整公开。

### 6.3 复现级别

**方法级复现（Methodological Reproduction）**

用 PyRadiomics 实现类似的特征提取与 Cox 生存建模流程，检验是否得到
方向一致、量级接近的预测表现。

**数值级复现（Numerical Reproduction）**

要求输入影像、ROI、特征定义、预处理、算法实现和模型参数尽可能一致。
在缺少原始 Matlab 实现或必要参数时，**不得声称完成数值级复现**。

本项目只做方法级复现。

## 7. 生存分析与统计方法

| 方法 | 作用 |
|---|---|
| Unsupervised Clustering | 识别影像特征模式相似的患者群组（Fig. 3） |
| ICC | 评估重测（test–retest）特征稳定性 |
| Friedman Test | 评估不同医生勾画导致的特征变化 |
| Kaplan–Meier | 比较不同特征组的生存概率 |
| G-rho Test | KM 两组曲线差异检验（删失数据） |
| FDR 10% | 多重检验校正 |
| Cox Proportional Hazards | 构建多变量生存预测模型 |
| Concordance Index | 评价模型区分能力（Harrell's C） |
| Bootstrap + Wilcoxon | 比较两个模型 / 与随机 C-index=0.5 的差异 |
| GSEA | 分析影像特征相关的基因集 |
| 相关性分析 | 影像特征与基因表达关联（具体方法待核实，正文方法段未见 Spearman 的明确表述） |

### 7.1 Kaplan–Meier

作者在 Lung1 训练集上计算每个特征的中位数，并**将该阈值锁定**，
直接用于 Lung2、H&N1、H&N2 的分组，不重新选择阈值；
用 G-rho 检验比较两组曲线，并以 FDR 10% 控制多重检验。

### 7.2 Cox 回归

```text
h(t|X) = h0(t) × exp(β1X1 + β2X2 + ... + βpXp)
```

- `h(t|X)`：给定特征时的风险函数；
- `h0(t)`：基线风险函数；
- `Xi`：影像组学特征；
- `βi`：模型系数。

4 特征 signature 的权重在 Lung1 上拟合，然后固定应用到验证集。

### 7.3 C-index

- C-index = 0.5：相当于随机预测；
- C-index 越高，区分能力越好；
- C-index = 1：可比较患者对的排序完全正确；
- 论文使用 Harrell's C，并说明它是 AUC 在生存数据上的推广；
- C-index 只反映排序，不反映绝对生存率的准确性。

## 8. 原论文报告的 C-index

| 数据集 | 角色 | 样本量 | C-index | 原文逐字 | 出处 |
|---|---|---:|---:|---|---|
| Lung1 | 训练集 | 422 | **主文未报告** | — | Results「Prognostic validation of radiomic signature」；待查 Supplementary Table 1 |
| Lung2 | 验证集 | 225 | 0.65 | "CI=0.65, *P*=2.91 × 10−09, Wilcoxon test" | 同上 + Fig. 4a |
| H&N1 | 验证集 | 136 | 0.69 | "CI=0.69, *P*=7.99 × 10−07, Wilcoxon test" | 同上 + Fig. 4a |
| H&N2 | 验证集 | 95 | 0.69 | "CI=0.69, *P*=3.53 × 10−06, Wilcoxon test" | 同上 + Fig. 4a |

**注意：**

1. 正文只报告三个验证集的 C-index，**没有报告 4 特征 signature 在 Lung1 的 C-index**；
   训练集数值可能在 Supplementary Table 1（signature vs volume vs TNM 对比表）中；
2. 不能把验证集结果误写为训练集结果；
3. **本项目只有 Lung1（论文训练集），没有 Lung2/H&N1/H&N2**，
   因此无法复现 0.65/0.69/0.69，只能做 Lung1 内部交叉验证；
4. 545 与 456 的口径：225 + 136 + 95 = 456（生存验证），
   456 + 89（Lung3）= 545（Discussion 口径）。

## 9. 核心研究结果

### 9.1 大量特征具有预后价值

以 Lung1 中位数阈值锁定后：

- Lung2：**238 个特征**（54% of 440）显著，FDR 10%；
- H&N1：**135 个**（31%）；
- H&N2：**186 个**（42%）；
- 三个验证集均显著的共有 **66 个**（15%）。

### 9.2 四特征模型具有预测能力

- Lung2：C-index = 0.65；
- H&N1：C-index = 0.69；
- H&N2：C-index = 0.69；
- signature 优于单纯 tumor volume，signature + volume 优于 volume；
- signature 在 Lung2、H&N2 优于 TNM，在 H&N1 与 TNM 相当；
  signature + TNM 在所有验证集均优于单独 TNM（Supplementary Table 1）；
- HPV 阴性亚组（n=130，占 76%）C-index = 0.66。

### 9.3 肿瘤异质性与基因表达相关

- 两个异质性特征（Feature III、IV）与细胞周期/增殖通路强相关；
- 说明影像特征可能反映潜在生物学过程，但**不能直接证明因果关系**。

## 10. 研究局限性

### 10.1 训练集单中心

论文整体是多中心研究，但 **Lung1 训练集来自单一中心（MAASTRO）**，
模型可能受训练中心患者构成与扫描条件影响。

### 10.2 回顾性设计

各队列基于既有临床影像与随访资料构建，通常被视为回顾性分析，
可能存在选择偏倚；但论文未逐队列声明研究设计类型，
引用时需注明"以各队列原始资料为准"。

### 10.3 外部验证规模

三个生存验证集分别为 225、136、95 例，部分队列规模较小，
泛化能力仍需更大规模、前瞻性研究验证。

### 10.4 分割依赖

影像组学特征依赖肿瘤 ROI 定义，不同医生的勾画会影响特征数值。
论文用多次勾画数据评估稳定性，但不能保证所有特征都不受分割差异影响。

### 10.5 扫描协议与标准化

不同医院、扫描仪和采集协议会影响特征一致性。
原论文未做特征归一化，也未按队列/扫描仪校正；
未来需要进一步标准化与跨平台验证。

### 10.6 权重与实现未完全公开

4 个特征的 Cox 系数未在正文给出，特征算法为自研 Matlab 实现，
外部团队难以逐位复现。

## 11. 复现项目建议

### 11.1 明确区分三类结果

1. **Original Paper Results**：论文原始结果；
2. **Our Reproduction Results**：本项目实际运行结果；
3. **Differences and Explanations**：差异及可能原因。

### 11.2 本项目的能力边界

- 只有 Lung1（论文训练集），**没有外部验证队列**；
- 只能做 Lung1 内部交叉验证，不能声称复现论文的 0.65/0.69/0.69；
- 影像主分析用 422 例；与临床基线（399 例）对比时必须使用同一分析集；
- 论文训练集 C-index 未报告，需查补充材料后才能判断是否可对照。

### 11.3 待核实清单

- [ ] 获取并阅读 Supplementary Methods；
- [ ] 核对 4 个最终特征的数学定义与编号（Feature 1/16/48/Group 4）；
- [ ] 核对原始 Matlab 实现与 PyRadiomics 的差异；
- [ ] 确认 Lung1 训练集 C-index（Supplementary Table 1）；
- [ ] 确认 signature 的 4 个 Cox 权重是否公开；
- [ ] 核对 Corrigendum `10.1038/ncomms5644` 是否影响数值；
- [x] 核对 545 与 456 两种样本量口径：225 + 136 + 95 = 456；
      456 + 89（Lung3）= 545（Discussion 口径）；
- [ ] 确认本数据集患者数量、分割文件与索引表一致（422 例）；
- [ ] 记录实际使用的软件版本与特征提取参数；
- [ ] 将复现 C-index 与论文报告值按「同口径/不同口径」分别对照。

## 12. 总结

Aerts et al. (2014) 证明，常规 CT 中的定量影像特征可为肺癌和头颈癌患者
提供具有预后价值的信息。研究从 440 个特征中筛选出 4 个，构建 Cox
signature，并在三个独立队列中验证（C-index 0.65 / 0.69 / 0.69）。

核心流程：

```text
CT 图像 → 440 特征提取 → 稳定性评估 → 选 100 → 四类各选 1
→ 4 特征 Cox → 独立验证 → 基因表达关联
```

对本项目而言，它的价值是提供**方法模板与目标量级**，而不是一套可直接
逐位复现的代码；由于只有 Lung1，复现定位为「论文训练集上的内部验证」。

## 参考

Aerts HJWL, Rios Velazquez E, Leijenaar RTH, et al.
Decoding tumour phenotype by noninvasive imaging using a quantitative radiomics approach.
*Nature Communications*. 2014;5:4006. DOI: `10.1038/ncomms5006`.

Corrigendum. *Nature Communications*. 2014. DOI: `10.1038/ncomms5644`
（页码/文章号以出版页为准）。

Dataset: TCIA NSCLC-Radiomics (Lung1). DOI: `10.7937/K9/TCIA.2015.PF0M9REI`.
