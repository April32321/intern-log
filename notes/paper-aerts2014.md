# Aerts et al. (2014) 论文精读笔记

> 论文：Decoding tumour phenotype by noninvasive imaging using a quantitative radiomics approach.
> *Nature Communications* 2014;5:4006. DOI `10.1038/ncomms5006`。
> 本笔记依据正文、图注、方法段与 Supplementary Information（32 页，2026-11-10 核对）整理。
> **目标值与复现协议以 `results/repro/target.md`（当前 v1.2）为唯一权威**；
> 本笔记只记录文献理解与原文事实，两者冲突时以 target.md 为准。

## 1. 论文基本信息

| 项 | 内容 |
|---|---|
| 标题 | Decoding tumour phenotype by noninvasive imaging using a quantitative radiomics approach |
| 作者 | Aerts HJWL, Rios Velazquez E, Leijenaar RTH, et al. |
| 期刊 | *Nature Communications* |
| 年份 / 卷号 | 2014；**5**:4006 |
| DOI | `10.1038/ncomms5006` |
| 更正 | Corrigendum：`10.1038/ncomms5644`（2014-08-07）。**已核对：仅为作者姓名拼写更正（Sara Cavalho → Sara Carvalho），不影响任何数值或特征定义** |
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

共 **440 个定量特征**（论文口径），分为四类：

| 特征类别 | 中文名称 | 描述内容 | 补充材料编号 | 数量 |
|---|---|---|---|---|
| Intensity | 一阶强度特征 | 肿瘤体素灰度值及其统计分布 | #1–#14 | 14 |
| Shape | 形状特征 | 几何形状、球形度、紧凑度 | #15–#22 | 8 |
| Texture | 纹理特征 | GLCM #23–#44、GLRLM #45–#55 | #23–#55 | 22 + 11 |
| Wavelet | 小波特征 | Coiflet 1、非降采样、8 个分解，每分解含一阶 + 纹理 | Group 4 | 8 × 47 |

其中纹理与小波特征用于刻画肿瘤内部异质性，是 signature 的核心信息来源。

**关于 440 的可复原性**：按补充材料编号可数出 55 个原始特征，
加 8 个小波分解 × 47 = 376，合计 **431**，与正文 440 差 9。
差额来源无法从公开材料解释，本笔记不作推测；
440 只作为论文口径记录，不作为本项目的特征数预期
（PyRadiomics 的特征集与论文不同，数量天然不可比）。
详见 `results/repro/target.md` §2.4。

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

| 特征（正文名称） | 补充材料标注（已核对） | 补充材料编号 | PyRadiomics 名称 | 备注 |
|---|---|---|---|---|
| Statistics Energy | `Stats_energy` | **#1** Energy | `original_firstorder_Energy` | 是 Energy（ΣX²），**不是** Total Energy |
| Shape Compactness | `Shape_compactness2` | **#16** Compactness 2 | `original_shape_Compactness2` | 不是 Compactness 1（#15） |
| Grey Level Nonuniformity | `RLGL_grayLevelNonuniformity` | **#47** GLN（GLRLM） | `original_glrlm_GrayLevelNonUniformity` | 正文写 "Feature 48"，但 #48 是 Run Length Non-Uniformity |
| wavelet Grey Level Nonuniformity HLH | `Wavelet_HLH_rlgl_grayLevelNonuniformity` | Group 4 | `wavelet-HLH_glrlm-GrayLevelNonUniformity` | HLH 分解上的 GLRLM GLN |

说明：

- 以上标注与编号均取自 Supplementary Information（已核对）：
  - **Compactness 是 2 不是 1**：补充材料 #15 = Compactness 1、#16 = Compactness 2，
    Supplementary Fig. 1 图注亦为 `Shape_compactness2`；
  - **GLN 的编号存在 off-by-one**：正文 "Feature 48" 与补充材料编号对不上
    （#47 = GLN、#48 = RLN）；Fig. 1 图注写作 `RLGL_grayLevelNonuniformity`
    （RLGL = run-length gray level），故实际特征是 GLRLM 的 GLN；
  - 正文的 `Statistics Energy` 对应补充材料 #1 Energy，**不是** "Total Energy"；
    PyRadiomics 的 `TotalEnergy` 额外乘体素体积，量级会差一个体素体积因子。
- **4 个特征的 Cox 权重已查：补充材料只给 #1–#55 的数学定义，未公开系数**；
  复现时一律在训练折内用相同 4 特征重新拟合，并标注「自拟合」，
  不得写成"采用论文权重"。
- 特征算法为作者自研 Matlab 实现，PyRadiomics 中同名特征不保证等价。

Supplementary Fig. 1 给出 4 个特征在 Lung1 上的中位数（即论文锁定的分组阈值），
可作量纲校验锚点：

| 特征 | Lung1 中位数 |
|---|---:|
| `Stats_energy` | 12,133,187,584（≈1.21×10¹⁰） |
| `Shape_compactness2` | 0.24 |
| `RLGL_grayLevelNonuniformity` | 984.67 |
| `Wavelet_HLH_rlgl_grayLevelNonuniformity` | 1110.68 |

这些值只能用于**量纲校验**，不可直接当作 PyRadiomics 特征的分组阈值
（实现不同，数值分布不可假定一致）。

## 6. 特征提取软件与参数

### 6.1 原论文使用的软件

原文 Methods 明确写道：

> All feature algorithms were implemented in Matlab.

- 原论文采用研究团队**自行实现**的特征算法；
- 论文发表于 2014 年，PyRadiomics 尚未发布（2016 年后才出现），
  因此不存在"作者选择不用 PyRadiomics"的问题，而是当时**只能自研**；
- 特征算法的详细定义在 Supplementary Methods，正文未完整给出。

### 6.2 复现参数（已核实）

| 参数 | 原文结论 | 出处 |
|---|---|---|
| Feature definitions | 见 §5.2：Energy、Compactness 2、GLRLM GLN、wavelet HLH GLN | Supplementary Methods 编号 #1–#55 |
| Image preprocessing | **未重采样**，直接用原始体素（Lung1 层厚 3 mm）；无滤波、无插值 | Supplementary Methods；Lung1 数据集段 |
| Gray-level discretization | 等宽分箱，**binWidth = 25 HU** | Group 3 第 1 段 |
| Texture matrix | 3D、26 邻域、13 方向；每个 3D 特征取 13 方向的均值；distance = 1 | Group 3 |
| Wavelet decomposition | **Coiflet 1**，离散、一层、**非降采样**，8 个分解；每个分解计算一阶 + 纹理特征 | Group 4 |
| Segmentation / ROI | GTV，放疗医生在融合 PET-CT 上按固定窗宽勾画；TCIA 发布的是同一批 delineation | Lung1 数据集段；TCIA |
| Normalization | **未做任何归一化**，直接使用 DICOM 原始数值 | Methods |

仍未知的细节：等宽分箱的**起点规则**（全局最小值还是 ROI 最小值）原文未说明；
PyRadiomics 从 ROI 内最小值起算，这一条留作残余差异。

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
| 相关性分析 | 影像特征与基因表达关联（正文与补充材料均未明确方法名；**与复现无关**，仅影响 radiogenomics 部分的解读） |

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
| Lung1 | 训练集 | 422 | **主文未报告** | — | Supplementary Table 1 亦无（该表仅含验证集） |
| Lung2 | 验证集 | 225 | 0.65 | "CI=0.65, *P*=2.91 × 10−09, Wilcoxon test" | 同上 + Fig. 4a |
| H&N1 | 验证集 | 136 | 0.69 | "CI=0.69, *P*=7.99 × 10−07, Wilcoxon test" | 同上 + Fig. 4a |
| H&N2 | 验证集 | 95 | 0.69 | "CI=0.69, *P*=3.53 × 10−06, Wilcoxon test" | 同上 + Fig. 4a |

**注意：**

1. 正文只报告三个验证集的 C-index，**没有报告 4 特征 signature 在 Lung1 的 C-index**；
   已核对 Supplementary Table 1（标题即 "Prognostic performance in validation datasets"），
   该表只有 Lung2 / H&N1 / H&N2 三行，**不含训练集值**——「Lung1 训练集 C-index」
   在本项目中判定为**不可对照**，不得用其他模型的数字顶替；
2. 不能把验证集结果误写为训练集结果；
3. **本项目只有 Lung1（论文训练集），没有 Lung2/H&N1/H&N2**，
   因此无法复现 0.65/0.69/0.69，只能做 Lung1 内部交叉验证；
4. 545 与 456 的口径：225 + 136 + 95 = 456（生存验证），
   456 + 89（Lung3）= 545（Discussion 口径）。

### 8.1 Supplementary Table 1（仅验证集）

| Dataset | TNM | Volume | Radiomics | TNM + Radiomics | Volume + Radiomics |
|---|---:|---:|---:|---:|---:|
| Lung2 | 0.60 | 0.63 | 0.65 | 0.64 | 0.65 |
| H&N1 | 0.69 | 0.68 | 0.69 | 0.70 | 0.69 |
| H&N2 | 0.66 | 0.65 | 0.69 | 0.69 | 0.68 |

可用于「量级参照」：signature 在三个验证集均不低于 volume；
加 TNM 后在三个验证集都优于单独 TNM。本项目没有这三个队列，不进入差异计算。

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

补充（Supplementary Tables 2–3）：

- 按治疗分组的 C-index——单纯放疗：Lung2 0.66、H&N1 0.72、H&N2 0.78；
  放化疗：Lung2 0.64、H&N1 0.65、H&N2 0.58；
- HPV 状态：H&N1 为 HPV− 53 / HPV+ 22 例，H&N2 为 77 / 18，合并 130 / 40（HPV− 占 76%）；
  组内 C-index：HPV− 0.66、HPV+ 0.53；
  单独用 HPV 状态预测的 C-index：H&N1 0.84、H&N2 0.81、合并 0.83。

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
原论文未做特征归一化、未按队列/扫描仪校正，也**未做体素重采样**；
未来需要进一步标准化与跨平台验证。

### 10.6 权重与实现未完全公开

4 个特征的 Cox 系数正文与 Supplementary Information 均未给出，
特征算法为自研 Matlab 实现，外部团队难以逐位复现。

## 11. 复现项目建议

### 11.1 明确区分三类结果

1. **Original Paper Results**：论文原始结果；
2. **Our Reproduction Results**：本项目实际运行结果；
3. **Differences and Explanations**：差异及可能原因。

### 11.2 本项目的能力边界

- 只有 Lung1（论文训练集），**没有外部验证队列**；
- 只能做 Lung1 内部交叉验证，不能声称复现论文的 0.65/0.69/0.69；
- 影像主分析用 422 例；与临床基线对比时必须使用同一分析集
  （临床 v1 399 例 / v2 395 例）；
- 论文训练集 C-index 未报告（正文与 Supplementary Table 1 均无），**已判定为不可对照**；
- apparent 与 CV 不得并列比较（详见 target.md §6.1–6.2）。

### 11.3 待核实清单

- [x] 获取并阅读 Supplementary Methods：已获取（32 页，Open access，2026-11-10）；
- [x] 核对 4 个最终特征的数学定义与编号：见 §5.2
      （Compactness 2；GLRLM GLN，正文 #48 与补充材料 #47 差一位）；
- [ ] 核对原始 Matlab 实现与 PyRadiomics 的差异（D16/D19 实测后补）；
- [x] 确认 Lung1 训练集 C-index：**正文与 Supplementary Table 1 均无，判定为未报告**；
- [x] 确认 signature 的 4 个 Cox 权重是否公开：**未公开**，一律自拟合；
- [x] 核对 Corrigendum `10.1038/ncomms5644`：仅为作者姓名拼写更正，不影响数值；
- [x] 核对 545 与 456 两种样本量口径：225 + 136 + 95 = 456；
      456 + 89（Lung3）= 545（Discussion 口径）；
- [x] 确认本数据集患者数量、分割文件与索引表一致：422 例；
      性别（290 男 / 132 女）与分期（I 93、II 40、IIIa 112、IIIb 176）与论文 Table 4 一致，
      缺 1 例 stage 与排除数吻合；
- [ ] 记录实际使用的软件版本与特征提取参数（D16）；
- [ ] 将复现 C-index 与论文报告值按「同口径/不同口径」分别对照（D18）。

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

Corrigendum: *Nature Communications*. 2014;5:4644. DOI: `10.1038/ncomms5644`
（2014-08-07）。已核对：仅为作者姓名拼写更正（Sara Cavalho → Sara Carvalho），
不影响任何数值或特征定义。

Supplementary Information（32 页，含 Supplementary Methods #1–#55、
Figs 1–4、Tables 1–7）：`https://www.nature.com/articles/ncomms5006#MOESM716`
（Open access；2026-11-10 获取，1,252,817 B；本地 `data/paper/` 不入库）。

Dataset: TCIA NSCLC-Radiomics (Lung1). DOI: `10.7937/K9/TCIA.2015.PF0M9REI`.
