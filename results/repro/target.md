# 复现目标（Aerts et al. 2014）

> 版本 **v1.11**（2026-11-17）｜初版 v1.0（2026-11-06）｜上版 v1.10（2026-11-17）
> 本文件记录**论文原始目标值 + 出处 + 复现协议 + D19 实际执行状态**。
> 复现结果由 D18/D19 填写；未核实的数字一律标「未报告」，**不使用推测值**。
>
> 对应附录 B 模板：§1 ↔ 模板§1；§2.1/§2.2 ↔ 模板§2；§4 ↔ 模板§3；§8 ↔ 模板§4。
> 其余章节（§0/§3/§5/§6/§7/§9）是复现协议与证据，属模板之外的自愿补充。
>
> 变更记录：
> - v1.1：补入 Supplementary Information（32 页）核对结果；目标数值表补齐 7 项；
>   修正 signature 特征定义（Compactness 2 / GLRLM GLN）；明确论文未做重采样、
>   binWidth = 25 HU；关闭「Lung1 训练集 C-index」一项。
> - v1.2：关闭 Corrigendum 核对（仅作者姓名拼写更正）；§3.1 限定中位数用途；
>   §6.2 补临床基线三口径对照；§4 补指标定义；补 signature 风险评分公式；
>   §6.1 补队列画像核对；§2.4 删除无法证实的推测解释。
> - v1.3：按附录 B 模板补齐——§2.2 增加「队列规模」行；§1 说明页码缺失原因；
>   §7 回填版本与实测特征数（两条 D16 项已关闭）；§8 补「差异在报告第 6 章归因」。
> - v1.4（D19）：回填四模型 5×10 实测结果（§5.1）与协议对齐表（§5.2）；
>   §6.2 增加 D19 临床基线口径；修正 wavelet 列名（`glrlm-GrayLevel` →
>   `glrlm_GrayLevel`）；记录 5×5→5×10、422/399、signature 标准化/惩罚三项偏离。
> - v1.5（D19）：森林图 HR 改为跨折逆方差合并 + 解析 95% CI（§5.3）；
>   说明该 CI 偏窄且不等于 §6.6-4 的 C-index CI 判据；主结果（C-index）逐字节复现。
> - v1.6（D19）：四特征方向核对完成（Supplementary Fig. 1，4/4 一致，§5.4）；
>   b/c/d 由正文明确表述，a（Energy）由 Supp. Fig. 1a 目测且与 pooled HR 一致。
> - v1.7（D19）：Energy 量纲全量核对完成（统一 HU+1024，中位数 1.03× 论文，§4/§5.5）；
>   方向核对改用单变量 HR/SD（4/4 一致，§5.4）；新增 Energy 基准敏感性（§5.5），
>   并把「Energy 基准 HU vs HU+1024」列入 §5.2 偏离表。
> - v1.8（D19）：补病人层面 bootstrap 95% CI（§5.6）；signature/lasso/combined 下限 > 0.5，
>   clinical 的 CI 含 0.5；§6.6-4 满足（Track A）。
> - v1.9（D19）：核对 399/395 病人清单（395⊂399，差 4 例）；完成 `report.md` 第 6 章五类差异归因；
>   §6.6 六条判据全部满足（方法级复现成立）。
> - v1.10（D19）：完成 stage_bin 编码核对（§6.2）；映射正确，分期在 399 分析集中
>   无显著预后效应；同步 §5.3 的 CI 表述指向 §5.6。
> - v1.11（D20）：补 binWidth 敏感性（10/25/50 HU，两条路线，§5.7）；§5.2 增加对应行；
>   量纲锚点仍只对 bw25 成立（GLN 随级数变化，不可跨 binWidth 比较）。

## 0. 范围

- 论文总队列：**1,019 例**，来自 7 个数据集（肺癌 + 头颈癌），
  即 31 + 21 + 422 + 225 + 136 + 95 + 89。
- 本项目可用数据：**Lung1，422 例**（TCIA `NSCLC-Radiomics`，
  数据集 DOI `10.7937/K9/TCIA.2015.PF0M9REI`）。
- **Lung1 是论文的训练集，不是验证集。**
- 本项目无 Lung2 / H&N1 / H&N2，**不做外部验证**，也不声称复现
  论文的 0.65 / 0.69 / 0.69。
- 复现级别：**方法级复现**（PyRadiomics + Cox），不是数值级复现。
- 本文件所有「论文原值」均来自正文或 Supplementary Information，
  **未使用任何推测值**；补充材料获取方式见 §9。

## 1. 目标文献

| 项 | 内容 |
|---|---|
| 标题 | Decoding tumour phenotype by noninvasive imaging using a quantitative radiomics approach |
| 作者 | Aerts HJWL, et al. |
| 期刊 | *Nature Communications* |
| 年份 / 卷号 | 2014；**5**:4006 |
| DOI | `10.1038/ncomms5006` |
| 更正 | Corrigendum：`10.1038/ncomms5644`（2014-08-07）。**已核对：仅为作者姓名拼写更正（Sara Cavalho → Sara Carvalho），不影响任何数值与特征定义** |
| 数据来源 | TCIA `NSCLC-Radiomics`（Lung1），DOI `10.7937/K9/TCIA.2015.PF0M9REI` |

- **复现对象**：☑ 论文原签名（4 特征 radiomic signature）
  ☐ 其他已发表 PyRadiomics+Cox 结果
- **引用原文位置（汇总）**：
  - 特征总数与四类划分：Abstract；Methods「Radiomics features」
  - 4 个 signature 特征：Results「Building prognostic radiomic signature」+ Fig. 3
  - 验证集 C-index：Results「Prognostic validation of radiomic signature」
    + Fig. 4a + Supplementary Table 1
  - 训练集中位数阈值：Methods「Data analysis」+ Supplementary Fig. 1
  - binWidth / 小波类型：Supplementary Methods, Group 3 / Group 4
  - 页码：Nature 在线版无连续页码，故以「章节/表/图」定位；
    补充材料的页码信息见 §9。

## 2. 目标数值

### 2.1 队列与 C-index（验证集）

| Dataset | Role | N | C-index | 原文逐字 | 出处 |
|---|---|---:|---:|---|---|
| Lung1 | Training | 422 | **未报告** | — | Results「Prognostic validation of radiomic signature」；Supplementary Table 1 也无 |
| Lung2 | Validation | 225 | 0.65 | "CI=0.65, *P*=2.91 × 10−09, Wilcoxon test" | Results + Fig. 4a |
| H&N1 | Validation | 136 | 0.69 | "CI=0.69, *P*=7.99 × 10−07, Wilcoxon test" | 同上 |
| H&N2 | Validation | 95 | 0.69 | "CI=0.69, *P*=3.53 × 10−06, Wilcoxon test" | 同上 |

**Lung1 训练集 C-index 已定案为「未报告」**：正文只报告三个验证集；
Supplementary Table 1 的标题即 "Prognostic performance in **validation datasets**"，
只含 Lung2 / H&N1 / H&N2。不存在"训练集值待查"的遗留项。

H&N1 的样本量在论文内部不一致：正文写 136，Supplementary Table 5 标题为
`(n = 135)`，且治疗人数 100（放疗）+ 35（放化疗）= 135。上表沿用正文口径 136；
本项目无该队列，不影响复现，引用时注明即可。

### 2.2 D16 目标数值表（8 项，逐项有出处）

| 项 | 论文原值 | 出处 | 我们的实现 | 结果 | 差异 |
|---|---|---|---|---|---|
| 队列规模 | 训练 **Lung1 = 422**；验证 225 / 136 / 95（合计 **1,019**） | Abstract；Methods「Datasets」；§2.3 Table 1 | **422**（仅 Lung1） | D16 已确认 | 无外部队列，不进入 Difference |
| 特征数 | **440**（四类） | Abstract；Methods「Radiomics features」 | PyRadiomics 按启用类别的实际计数（不追求 440） | D16 实测记录 | 见 2.4：440 无法逐项复原 |
| signature 特征数 | **4** | Results + Fig. 3 + Supplementary Table 1 | **4**（固定，不做特征选择） | D18 | — |
| 训练集 C-index | **未报告** | 正文与 Supplementary Table 1 均无 | apparent 与 5-fold×10 测试折 CV **分行报**，各标口径与 n（D19 实际；v1.3 原计划 5×5） | D18/D19 | **N/A，不计算 Difference** |
| 验证集 C-index | 0.65 / 0.69 / 0.69 | Results + Fig. 4a | 无外部数据 | **N/A** | 不计算 |
| 分组方式 | Lung1 训练集内算**中位数**，锁定后直接用于验证集，不重选阈值 | Methods「Data analysis」+ Supplementary Fig. 1 | 内部 CV 不分箱；若作 KM 分层图，用**训练折内**中位数（见 6.3） | D18 | 口径差异（CV 无"锁定阈值"概念） |
| 重采样 / spacing | **未重采样**，用原始体素（Lung1 层厚 3 mm；Lung3 1.5–5 mm） | Supplementary Methods 全文无 resampling 描述；Lung1 数据集段 | **不重采样**（参数文件中省略 `resampledPixelSpacing`，默认即 None） | D16 参数 | 无（按论文） |
| binWidth | **25 HU**（"equally spaced bins using a bin-width of 25 Hounsfield Units"） | Supplementary Methods, Group 3 首段 | **25** | D16 参数 | 起点规则可能不同（见 §4） |

### 2.3 Supplementary Table 1：完整对照（仅验证集）

| Dataset | TNM | Volume | Radiomics | TNM+Radiomics | Volume+Radiomics |
|---|---:|---:|---:|---:|---:|
| Lung2 | 0.60 | 0.63 | 0.65 | 0.64 | 0.65 |
| H&N1 | 0.69 | 0.68 | 0.69 | 0.70 | 0.69 |
| H&N2 | 0.66 | 0.65 | 0.69 | 0.69 | 0.68 |

用途：仅作**量级参照**。三个队列本项目都没有，因此不进入 `Difference` 计算。

### 2.4 关于「440」：公开材料无法逐项复原

按 Supplementary Methods 的编号可数出：

```
一阶 14（#1–14）+ 形状 8（#15–22）+ GLCM 22（#23–44）+ GLRLM 11（#45–55）= 55
小波 8 个分解 ×（一阶 14 + GLCM 22 + GLRLM 11 = 47）= 376
55 + 376 = 431 ≠ 440（差 9）
```

**结论：440 与 431 的差额 9 无法从公开材料解释，本文件不作推测。**
440 只作为"论文口径"记录，不作为本项目的特征数预期；
D16 的 QC 以 PyRadiomics 实际计数为准。
另外 PyRadiomics 的特征集与论文不同（论文只定义 #1–#55 这 55 个，
PyRadiomics 各类特征更多且含论文没有的类别），数量天然不可比，
具体计数以 D16 实测为准。

## 3. 目标 signature（4 个特征，精确定义）

| 正文名称 | 编号（正文 / 补充材料） | 数学定义 | PyRadiomics 名称 |
|---|---|---|---|
| Statistics Energy | 1 / **#1** Energy | Group 1 第 1 项，ΣX² | `original_firstorder_Energy` |
| Shape Compactness | 16 / **#16 Compactness 2** | Group 2 第 16 项 | `original_shape_Compactness2`（**PyRadiomics 3.x 已移除该特征**，由 `36π·V²/A³` 现算，列名后缀 `_derived`） |
| Grey Level Nonuniformity | 48 / **#47 GLN（GLRLM）** | Group 3 GLRLM 灰度不均匀性 | `original_glrlm_GrayLevelNonUniformity` |
| wavelet GLNU HLH | Group 4 / **Group 4** | Coiflet 1 非降采样小波 HLH 分解上的 GLRLM GLN | `wavelet-HLH_glrlm_GrayLevelNonUniformity` |

必须注意的三点：

1. **是 Compactness 2，不是 Compactness 1**。Supplementary Methods 中
   #15 = Compactness 1、#16 = Compactness 2；Supplementary Fig. 1 图注亦为
   `Shape_compactness2`。PyRadiomics 两个都有，选错会使形状特征完全失真。
2. **是 GLRLM 的 GLN，编号存在 off-by-one**。正文写 "Feature 48"，但补充材料中
   #47 = Gray Level Non-Uniformity、#48 = Run Length Non-Uniformity；
   Supplementary Fig. 1 图注用 `RLGL_grayLevelNonuniformity`（RLGL = run-length gray level），
   故取 GLRLM 的 GLN。正文编号与补充材料编号不一致，**如实记录，不替作者圆整**。
3. **Energy 不是 TotalEnergy**。论文用 ΣX²；PyRadiomics 的 `TotalEnergy` 额外乘体素体积，
   量级会差约一个体素体积因子。用下面的中位数可校验是否接错。

### 3.1 量纲校验锚点（Supplementary Fig. 1 的 Lung1 中位数）

| 特征 | Lung1 中位数（论文） |
|---|---:|
| `Stats_energy` | 12,133,187,584（≈1.21×10¹⁰） |
| `Shape_compactness2` | 0.24 |
| `RLGL_grayLevelNonuniformity` | 984.67 |
| `Wavelet_HLH_rlgl_grayLevelNonuniformity` | 1110.68 |

这 4 个值同时是论文锁定的分组阈值。D16 的特征提取结果应与之**同数量级**；
若相差一个数量级以上，优先排查特征映射、binWidth、是否误加 TotalEnergy。
注意论文为自研 Matlab 实现，**不要求逐位相同**。

**用途限定**：这 4 个中位数只能用于**量纲校验**，
不可直接作为 PyRadiomics 特征的分组阈值——特征实现不同，数值分布不可假定一致。
分组阈值应在我们的特征取值上、按训练折内中位数重新确定（见 6.3）。

### 3.2 Cox 权重

Supplementary Methods 仅给出 #1–#55 的数学定义，**未公开 4 个特征的 Cox 系数**。
复现时使用相同 4 个特征在训练折内重新拟合，权重来源记为「自拟合」，
不得写成"采用论文权重"。

### 3.3 风险评分定义

```
risk = β₁·Energy + β₂·Compactness2 + β₃·GLN + β₄·wavelet-HLH-GLN
```

- β 由训练折内 Cox 拟合得到，**不对特征做标准化**（论文明确未归一化），
  因此 β 的量纲依各特征自身尺度而定；
- 论文的 β 未公开，本项目一律标注「自拟合」；
- 分层作图时，阈值只用训练折内中位数，不在测试折或全量上重算（见 6.3）。

**D19 实际偏离**：本次 `09_cv_models.py` 的 signature 路线先用训练折 `StandardScaler`，再用带 0.1 惩罚的 Cox 拟合；这与上文「不对特征做标准化」不一致。无惩罚 Cox 的 C-index 对特征线性缩放不变，但有惩罚时惩罚施加在标准化后的系数上，结果可能略有差异。该偏离需在正式报告的方法节声明；若要做严格的论文口径，应补一次「原始尺度 + 无惩罚」的敏感性分析。

## 4. 方法细节对照

| 项 | 文献值 | 我们的做法 | 是否可对齐 |
|---|---|---|---|
| 分割来源 | 放疗医生在融合 PET-CT 上按固定窗宽勾画 GTV；TCIA 发布同一批 delineation | RTSTRUCT → 栅格化 mask（ROI 名需容错匹配） | 是（同源） |
| 重采样 spacing | 未重采样，原始体素（Lung1 层厚 3 mm） | 不重采样 | 是 |
| 插值方式 | 不适用（论文未重采样，无插值环节） | 无 | 是 |
| binWidth / 离散化 | 等宽 25 HU | `binWidth: 25` | 是（起点规则可能不同） |
| 特征类别 | 一阶 14 / 形状 8 / GLCM 22 / GLRLM 11 / 小波 8×(一阶+纹理) | PyRadiomics 同名类 | 部分（实现不同） |
| 纹理方向 | 26 邻域、13 方向，3D 特征取 13 方向均值 | PyRadiomics `distances=[1]`，3D 默认 13 方向平均 | 是 |
| 小波 | Coiflet 1，离散、一层、非降采样，8 分解 | `wavelet`（`coif1`） | 是 |
| 归一化 | **未做任何归一化**，直接用 DICOM 原始值 | `normalize: false` | 是 |
| 指标定义 | Harrell's C；模型间显著性用 bootstrap（100 次重采样）+ Wilcoxon 检验 | `lifelines.utils.concordance_index`（Harrell's C），不做 bootstrap 显著性检验 | 部分（C-index 可比，显著性检验不可比） |
| 特征筛选 | 稳定性（ICC + Friedman）→ 前 100 → 四类各选 1 | Track A 不筛选，固定 4 特征 | 否（D18 不需要） |
| 模型 | 多变量 Cox，权重在 Lung1 拟合 | lifelines Cox（D19 实际惩罚 0.1；论文未公开惩罚） | 部分（权重自拟合，惩罚口径不同） |
| 验证方式 | 3 个独立外部队列 | Lung1 内部 5-fold × 10 次重复 CV（D18 改；原计划 5×5） | 否（无外部数据） |

残余差异（D20 归因时需写明）：

- 离散化起点：论文未说明等宽分箱从全局最小值还是 ROI 最小值起算；
  PyRadiomics 从 ROI 内最小值起算。
- 形状面积：论文用三角化表面积、体素计数求体积；PyRadiomics 用 marching cubes，
  两者在曲面重建上存在小幅差异，影响 Compactness 2。
- 特征实现：Matlab 自研 vs PyRadiomics，同名特征不保证等价。
- **Energy 的取值基准**：D16 本地预跑（10 例）显示 Energy 中位数约 4.2×10⁸，
  比论文的 1.21×10¹⁰ 低约 30 倍；而另外 3 个特征（Compactness2、GLN、
  wavelet HLH GLN）与论文中位数在 0.5–1.0 倍范围内。Energy 是唯一对
  "灰度零点"敏感的求和量，其余三个是比值或相对分箱量。
  初步验证：若把 HU 加上 1024（即未减 DICOM rescale intercept 的存储值），
  LUNG1-001 的 ΣX² 从 2.28×10⁹ 变为 5.29×10¹⁰，量级进入 10¹⁰
  （该例体积 156 cm³ 偏大，绝对值高于论文中位数属正常），
  提示论文是在**未转为 HU 的存储像素值**上计算 Energy。
  **D19 状态：已完成**（`code/10_energy_scale_check.py`，全量 422 例）：
  按各例 DICOM intercept 时中位数 5.03×10⁹（0.41× 论文，被 97 例 intercept=0 拉低）；
  统一 HU+1024（论文实际口径）时中位数 1.249×10¹⁰，为论文的 **1.03×**，§6.6-2 通过。
  intercept：−1024 共 325 例、0 共 97 例（均为 CT，slope=1）；LUNG1-001 复现 2.28×10⁹ → 5.29×10¹⁰。
  **注意**：`features_all` 现为 HU 口径，论文为 HU+1024，属特征定义偏离（§5.2）；
  对 signature C-index 的影响见 §5.5（无实质影响）。

## 5. 复现范围与可比性

| Dataset | 论文 C-index | 本项目结果 | 可比性 |
|---|---:|---|---|
| Lung1 | **未报告**（正文 + 补充材料均无） | 5×10 CV：`signature` 0.581 ± 0.038；`clinical` 0.530 ± 0.026；`lasso` 0.583 ± 0.035；`combined` 0.581 ± 0.034（399 例）；apparent 未做 | **否（无数值可对照）**；只能评价"协议同口径"与"量级合理性" |
| Lung2 | 0.65 | **N/A（无数据）** | 否 |
| H&N1 | 0.69 | **N/A（无数据）** | 否 |
| H&N2 | 0.69 | **N/A（无数据）** | 否 |

`Difference = Reproduced − Paper` 只在可比性不为「否」的格子计算；
本项目**没有一格满足条件**，因此 D18/D19 不产出数值差异，
只做「协议对齐情况 + 量级判断 + 差异来源归因」。
其余写 `N/A`，不得用 `TBD` 暗示以后能补。

### 5.1 D19 四模型实测结果（399 例，5×10，seed=42）

来源：`results/tables/perf.csv`、`journal/day19.md` §3；完整逐折记录见 `results/tables/cv_folds.csv`。

| 模型 | C-index (mean ± SD) | median | train−test gap | log-rank p<0.05 的折 | 特征数 mean [min–max] | fallback 折 |
|---|---:|---:|---:|---:|---:|---:|
| `clinical` | 0.530 ± 0.026 | 0.524 | 0.026 | 10% | 7.0 [7–7] | 0 |
| `signature` | 0.581 ± 0.038 | 0.583 | 0.003 | 20% | 4.0 [4–4] | 0 |
| `lasso` | 0.583 ± 0.035 | 0.589 | 0.049 | 18% | 11.3 [2–42] | 1 |
| `combined` | 0.581 ± 0.034 | 0.585 | 0.057 | 28% | 8.0 [8–8] | 1 |

限制：50 折共享病人，`mean ± SD` 描述折间波动，**不是 95% CI**；`log-rank p<0.05 的折` 是 50 折中显著的比例，不是合并 p 值；所有模型均为 Lung1 内部 CV，不是外部验证。

### 5.2 D19 实际协议与 target 的对齐表

| 项目 | target / v1.3 | D19 实际 | 状态 | 处理 |
|---|---|---|---|---|
| 数据角色 | Lung1 = training；Lung2 / H&N1 / H&N2 = 外部验证 | 仅 Lung1，无外部队列 | 不可对齐 | 只做方法级复现；不声称 0.65 / 0.69 / 0.69 |
| 分析集 | 影像主分析 422；临床对比 399 / 395 | 四模型统一 399 | **有意偏离** | 399 用于跨模型同集比较；395⊂399 已核对（差 4 例：LUNG1-085 T 缺失、LUNG1-167/232/292 N=4）；422 signature-only 待补 |
| 外层 CV | 5 折 × 5 次重复 | 5 折 × 10 次重复 | **有意偏离**（D18 建模前改） | 主结果 5×10；5×5 仅作可选敏感性 |
| signature 拟合 | 不标准化；论文权重未公开，自拟合 | 训练折 `StandardScaler` + 0.1 惩罚 Cox | **偏离** | 方法节声明；可选「原始尺度 + 无惩罚」敏感性 |
| Energy 基准 | HU+1024（存储像素值） | HU（`features_all`） | **偏离** | 量级校验见 §4；敏感性见 §5.5（C-index 不变，多元系数重分配） |
| 临床基线 | v1 0.5459 ± 0.0301（n=395，5×5） | v1 0.530 ± 0.026（n=399，5×10） | 口径不同 | 同集比较成立；并列时标 n 与 CV，不把差值当复现差 |
| 特征数 | 论文 440（按编号复原 431） | PyRadiomics 537 | 不可比 | §2.4 已记录；只做方法与量级比较 |
| Lung1 C-index（论文训练集值） | 未报告 | apparent 未计算；仅有 5×10 测试折 CV 0.530–0.583 | 无数值可对照 | 不做 Difference |
| 验证集 C-index | 0.65 / 0.69 / 0.69（外部） | N/A | 不可对齐 | 不做 Difference |
| Compactness | Compactness 2（#16） | `original_shape_Compactness2_derived`（36πV²/A³） | 已映射 | 方法一致；实现差异见 §4 |
| wavelet 列名 | GLRLM GLN，HLH 分解 | `wavelet-HLH_glrlm_GrayLevelNonUniformity` | 已修正 | 修正 v1.3 的连字符笔误 |
| binWidth / 重采样 | 25 HU；不重采样 | 25；不重采样 | 对齐 | — |
| 方向核对 | 以 Supplementary Fig. 1 为准 | 单变量 HR/SD：Energy 1.13 / GLN 1.20 / Compactness 0.90 / wavelet GLN 1.21（§5.4） | **已核对（4/4 一致）** | 见 §5.4；heterogeneity↑→差、compactness↑→好；多元 HR 不作判据（§5.5） |
| 95% CI | 判据要求不含 0.5 | 病人层面 bootstrap：signature 0.576 [0.543–0.608] | **完成** | 见 §5.6；clinical [0.495–0.558] 含 0.5，如实报告；森林图 HR 的 pooled CI 见 §5.3，不用于本判据 |
| binWidth 敏感性 | 论文口径 25 HU（§2.2） | 10/25/50 HU 各重提特征并重跑两条路线 | **完成** | 见 §5.7；路线 1 全距 0.0009、路线 2 全距 0.007；选择不稳定且非单调 |
| 差异归因 | `report.md` 第 6 章 | 已完成 | **完成** | 见 `report.md` §6（五类归因 + §6.6 汇总表）；敏感性见 §5.4 |

方向核对说明：表中 HR 为 399 例 / 5×10 的跨折逆方差合并 pooled HR（§5.3），仅作线索；最终判据以 Supplementary Fig. 1 的分组方向为准（§5.4）。

### 5.3 D19 森林图 HR 的 95% CI 口径

任务 5 要求森林图展示“HR + 95% CI”。D19 重跑后，森林图不再使用跨折 HR 的 10–90 分位，而是把每折最终 Cox 的 `coef` 与 `se(coef)` 做逆方差合并：

```
w_i         = 1 / se_i²
beta_pooled = Σ w_i·beta_i / Σ w_i
var_pooled  = 1 / Σ w_i
95% CI      = exp(beta_pooled ± 1.96·sqrt(var_pooled))
```

- 产物：`coefficient_summary.csv` 的 `*_pooled*` 列；`cv_coefficients.csv` 的 `se / hr_lower95 / hr_upper95`。
- 限制：50 折共享病人、Cox 带 0.1 惩罚，逆方差合并把折当独立样本，CI 偏窄
  （如 `radiomics_score` 1.51 [1.39–1.69] → 1.51 [1.49–1.54]）；不能替代病人层面 bootstrap。
- 与判据的关系：该 CI 是 **HR 的近似 CI**，**不是** §6.6-4 所指的 C-index 95% CI；后者见 §5.6（病人层面 bootstrap，已完成）。
- 主结果（C-index）与上一版逐字节一致，详见 `journal/day19.md` §11 补记。

### 5.4 D19 四特征方向核对（Supplementary Fig. 1）

来源：`ncomms5006_supplementary.pdf` 第 2 页的单特征 Kaplan–Meier（面板 a–d），按 Lung1 中位数分 `<= Median` / `> Median` 两组。正文 Results 的表述为：“Features describing heterogeneity in the primary tumour were associated with worse survival in all four data sets. Also, patients with more compact/spherical tumours had better survival probability.”

方向判据采用**单变量 Cox（每 1 SD，399 例）**，不用多元系数（多元 HR 会随 Energy 基准重分配，见 §5.5）。

| 面板 | 特征 | 论文方向 | 预期 HR | 单变量 HR/SD [95% CI] (p) | 结论 |
|---|---|---|---|---|---|
| a | `Stats_energy` | 高值组预后更差 | >1 | 1.13 [1.04–1.22] (0.0025) | 一致 |
| b | `Shape_compactness2` | 更紧凑/球形→更好 | <1 | 0.90 [0.81–1.00] (0.047) | 一致（边界） |
| c | `RLGL_grayLevelNonuniformity` | 异质性高→更差 | >1 | 1.20 [1.09–1.32] (1.3e-4) | 一致 |
| d | `Wavelet_HLH_rlgl_grayLevelNonuniformity` | 异质性高→更差 | >1 | 1.21 [1.10–1.33] (8.5e-5) | 一致 |

结论：**4/4 单变量方向与论文一致**，§6.6-3 记为“满足（定性）”。其中 b/c/d 由正文明确表述；a（Energy）正文未单列方向，依据 Supp. Fig. 1a 中 `> Median` 组曲线更低。Compactness 的 p=0.047、CI 上界 1.00，属边界证据，报告需如实标注。**多元 Cox 的 HR 不作为方向判据**（理由见 §5.5）。

### 5.5 D19 Energy 基准敏感性（HU vs HU+1024）

§4 已确认论文 Energy 基准为 `HU+1024`，而 `features_all` 的 `original_firstorder_Energy` 为 HU 口径。把 Energy 替换为 `HU+1024` 后只重跑 signature（`--models signature`，固定折）：

| 指标 | HU 口径（主结果） | stored = HU+1024（敏感性） |
|---|---:|---:|
| signature C-index | 0.5808 ± 0.0377 | 0.5813 ± 0.0390 |
| Energy pooled HR | 1.09 [1.07–1.10] | 1.23 [1.18–1.28] |
| GLN pooled HR | 1.09 [1.06–1.13] | 0.98 [0.95–1.02] |
| Compactness2 pooled HR | 0.95 [0.93–0.96] | 0.94 [0.93–0.96] |
| wavelet-HLH GLN pooled HR | 1.06 [1.03–1.10] | 1.00 [0.96–1.04] |
| log-rank p<0.05 折数占比 | 20% | 24% |

- **C-index 无实质影响**（差 0.0005，远小于 SD），主结论不依赖 Energy 基准；
- **多元系数重分配**：Energy 变强、GLN/wavelet 变中性（CI 含 1），说明相关特征间权重不稳，**特征级多元 HR 不应作为方向或显著性判据**；
- 主结果保持 HU 口径，stored 作为敏感性；该偏离列入 §5.2；
- 产物：`results/cache/sens_energy_hu`、`results/cache/sens_energy_stored`（gitignore）。

### 5.6 D19 C-index bootstrap 95% CI（病人层面）

数据：`results/tables/oof_predictions.csv`（每 model × repeat 的 399 例折外预测）。
方法：病人层面有放回重采样 399 例（B=2000，seed=42），同一组重采样用于所有
model/repeat；每个 model 取 10 个 repeat 的 C-index 均值作为一个 bootstrap 复制；
取 2.5/97.5 分位。

| model | pooled OOF C-index | 95% CI | 是否排除 0.5 |
|---|---:|---|---|
| clinical | 0.527 | [0.495, 0.558] | **否** |
| signature | 0.576 | [0.543, 0.608] | 是 |
| lasso | 0.579 | [0.551, 0.608] | 是 |
| combined | 0.577 | [0.548, 0.605] | 是 |

- §6.6-4（Track A = signature）满足：下限 0.543 > 0.5。
- **clinical 的 CI 包含 0.5**：本样本量下临床基线不能排除随机，报告需如实写。
- 该 CI 只反映病人抽样不确定性，不含模型拟合/折划分变异性；
  与 `perf.md` 的 50 折 `mean ± SD` 是两种口径，不能互相替代。
- `cindex_obs` 为“每 repeat 的 399 例 OOF C-index 均值”，与 50 折折均值
  （0.530/0.581/0.583/0.581）略有差异，属聚合方式不同。
- 产物：`results/repro/cindex_bootstrap.csv`。

### 5.7 D20 binWidth 敏感性（10 / 25 / 50 HU）

固定分析集（399 例）、固定 5×10 折与 seed=42，只改 `params*.yaml` 的 `binWidth`
（其余参数逐行 diff 确认只差第 24 行），重提 422 例特征后重跑两条路线。
**这是敏感性分析，不是与论文对齐的协议**（论文口径为 25 HU，§2.2）。

| binWidth | 路线 1 signature | 路线 2 lasso | 路线 2 特征数 mean [min–max] | 路线 2 log-rank p<0.05 |
|---:|---|---:|---|---:|
| 10 | 0.5803 ± 0.0372 | 0.5830 ± 0.0328 | 11.6 [2–47] | 24% |
| 25（主结果） | 0.5808 ± 0.0377 | 0.5831 ± 0.0348 | 11.3 [2–42] | 18% |
| 50 | 0.5812 ± 0.0384 | 0.5901 ± 0.0328 | 11.5 [2–53] | 30% |

- 路线 1 全距 **0.0009**，路线 2 全距 **0.007**（约 0.2 个折间 SD，且非单调）；
  两者均远小于折间 SD（0.033–0.038）→ 判别力对 binWidth 不敏感。
- 路线 1 四个特征的 pooled HR 方向三档一致；最大变动 0.033（wavelet-HLH GLN
  1.056→1.093），Energy 与 wavelet GLN 间存在轻微系数重分配（同 §5.5 现象）。
- **选择不稳定且非单调**：`wavelet-LHL_glcm_MCC` 入选率 0.08 / 0.60 / 0.76，
  `wavelet-LHH_glcm_Correlation` 0.44 / 0.56 / 0.76，`wavelet-HHH_glcm_Idn`
  0 / 0.32 / 0.04；三个小波一阶特征稳定（`HHL_TotalEnergy` 0.90/0.86/0.84、
  `LHL_Skewness` 0.82/0.78/0.88、`LLH_Variance` 0.74/0.68/0.60）。
  "掉下去又跳回来"说明中频 GLCM 的选择接近随机，不是分箱的单调函数。
- **量纲锚点只对 bw25 成立**：GLN 中位数 bw10 499.2 / bw25 953.7 / bw50 1225
  （论文 984.7）。GLN 是计数类量，灰度级数越少越集中，不能用跨 binWidth 的
  "偏离论文几倍"评价实现正确性。
- 产物：`results/cache/features_bw10|features_bw50`（逐例缓存，gitignore）、
  `results/tables/features_all_bw10.csv|features_all_bw50.csv`、
  `results/cache/sens_bw10|sens_bw10_sig|sens_bw50|sens_bw50_sig`（gitignore）、
  `results/figures/report/binwidth_sensitivity.png`。
- 报告位置：`report.md` §5.4（图 7）。

## 6. 评估协议（先定后跑）

### 6.1 分析集

| 用途 | n | 说明 |
|---|---:|---|
| 影像主分析 | **422** | 生存结局完整，radiomic signature 不依赖 age |
| 与临床 v1 对比 | **399** | 与 `code/04_cox_baseline.py` 一致（排除 age 缺失 22、stage 缺失 1） |
| 与临床 v2 对比 | **395** | 与 `code/04b_cox_clinical_v2.py` 一致；额外排除 T=5、N=4 等含义丢失编码 |

跨模型比较（临床基线 vs 影像 vs 联合模型）**必须使用同一分析集**，
并在结果表中注明 n；不得用 422 的影像结果去对比 399/395 的临床结果。

**D19 实际执行**：四个模型统一使用 399 例（完整病例），以满足跨模型同集比较；v1.3 表中的 422「影像主分析」与 395「临床 v2 对比」未作为 D19 主分析。422 的 signature-only 分析尚未运行，列为待补敏感性；不得把 399 的结果写成 422 的结果。

数据一致性核对（论文 Table 4 vs `results/tables/cohort.csv`）：

| 项 | 论文 Table 4 | 本数据集 | 结论 |
|---|---|---|---|
| 男 | 68.7%（正文 290） | 290（68.7%） | 一致 |
| 女 | 31.3%（正文 132） | 132（31.3%） | 一致 |
| I 期 | 22.0% | 93（22.0%） | 一致 |
| II 期 | 9.5% | 40（9.5%） | 一致 |
| IIIa | 26.5% | 112（26.5%） | 一致 |
| IIIb | 41.9% | 176（41.7%） | 差 0.2pp |

93 + 40 + 112 + 176 = 421，比 422 少 1 例，对应 399 分析集里被排除的
stage 缺失 1 例；IIIb 的 0.2pp 差异由此解释。
**结论：索引表与论文 Lung1 队列一致，不存在接错队列的风险。**

### 6.2 临床基线决策（D16 定，D19 执行）

- 主对照：**v1**（age + gender + stage 二分 + histology，n=399）。
- v2（age 样条 + T/N + stage 四水平 + histology，n=395）为**事后探索**，
  仅作敏感性分析；若 D18 改用 v2，必须注明"基线选择为事后决定"。
- **口径风险（必须处理）**：现有 v1 的 CV 值 0.5459 ± 0.0301
  是在 **395 例共同集**上测得的（`results/tables/cox_cv_comparison.csv`），
  而 v1 的分析集是 399 例。若 D18 直接拿 399 例的影像模型对比该值，两者不同集。
  处理方式二选一，并在 D18/D19 日志写明：
  1. 在 399 例上重跑 v1 的 5×5 CV，用新值作主对照（D19 实际采用 5×10，见下表）；
  2. 主对照统一改用 395 例共同集（影像模型也只在 395 上评估）。
  未处理前，不得把 399 的影像结果与 395 的临床 CV 值并列。

现有临床基线口径（除注明外为 D16 实测值，n=395，见 `results/tables/`）：

| 模型 | 口径 | n | C-index | 可否用于跨模型比较 |
|---|---|---:|---:|---|
| 临床 v2 | apparent（全量拟合，仅描述） | 395 | 0.5909 | **否**（样本内，偏乐观） |
| 临床 v2 | 5×5 CV 测试折 | 395 | 0.5706 ± 0.0244 | 是（敏感性分析用） |
| 临床 v1 | 5×5 CV 测试折 | 395 | 0.5459 ± 0.0301 | 是（D16 值；D19 同集值见下行） |
| 临床 v1 | 5×10 CV 测试折（D19） | 399 | 0.530 ± 0.026 | 是（与 D19 四模型同集） |

**D19 处理结果**：D19 选择在 399 例上重跑临床 v1，以满足与四模型的同集比较；CV 采用 5×10，因此 0.530 ± 0.026 与上表 395/5×5 的 0.5459 ± 0.0301 不能直接相减。两者并列时必须标 n 与 CV。

**apparent 与 CV 不得并列比较**：前者在同一批病人上拟合并打分，系统性高于后者
（上表 0.5909 vs 0.5706 即为例证）。影像 signature 同样规则——apparent 与 CV
分行报，各自标注口径与 n。

**D19 stage_bin 编码核对（day19 §7-1 / §8-2）**：在 399 例上核对：

- 映射：I/II → 0、IIIa/IIIb → 1，与 `Overall.Stage` 一一对应，无错配；
- 分布（399）：I 84 / II 37 / IIIa 109 / IIIb 169，与论文 422 的
  I 93 / II 40 / IIIa 112 / IIIb 176 同形（差异来自 age/stage 缺失的 23 例）；
- 单变量：log-rank p=0.528；stage_bin HR 0.93 [0.74–1.16]；
  4 水平 Cox（参考 I 期）LRT p=0.574；
- 多变量（D19 clinical pooled）：stage_bin HR 1.04 [1.00–1.08]（CI 含 1）；
- 反向 sanity check：age HR 1.20 / 10 岁（p=0.0018）、male HR 1.29（p=0.032），方向正常。

结论：**stage_bin 编码无误**；本分析集中分期本身缺乏判别力。
clinical 的 0.530（bootstrap CI 0.495–0.558）不是编码问题，报告应写
"本队列分期判别力弱"，而不是"分期编码错误"。

### 6.3 Track A（主分析，对标论文）

> **口径变更（D18，建模前）**：v1.3 原写 5×5；D18 为提高折间稳定性改为 5×10，并在建模前固定。D19 按 5×10 报告。此处保留变更记录，不把 5×10 写成 v1.3 的原计划。

- 固定论文 4 个特征（§3 的 PyRadiomics 映射）；
- **不做特征选择**；
- 权重在训练折内重新拟合（论文权重未公开，见 §3.2）；
- 报告 5-fold × 10 次重复的测试折 C-index 均值 ± SD（规则见 6.5）；
- 次要输出：按 training fold 内的 signature 中位数分层画 KM 曲线
  （阈值只在训练折确定，不在测试折或全量上重算）。

### 6.4 Track B（次要，探索）

- 使用全量 PyRadiomics 特征；
- 稳定性筛选 + 单变量筛选**只在训练折内**进行；
- 结果仅作探索，不作为"复现论文 signature"的主结果。

### 6.5 共同规则

- **内部验证**：Lung1 上 5-fold 交叉验证 × 10 次重复，按事件分层（D18 改；原计划 5×5，见 §6.3 变更说明）；
- **主指标**：测试折 C-index 的均值 ± SD（保留 3 位小数）；
- **另报表观 C-index**：全量拟合后在 Lung1 上计算，明确标注 `apparent`（D19 未做，待补）；
- 校准图与 IBS 作为次要指标，D19 未做；如报告需要，另定时间点；
- 不因结果好坏更换划分、指标或特征集；任何偏离都要在日志中写明理由。

### 6.6 复现成功判据（可验收）

复现判定为"方法级复现成立"，需同时满足：

1. 4 个特征在 PyRadiomics 中均可提取，且与 §3 的映射一致；
2. 量纲校验：4 个特征在 Lung1 上的中位数与 §3.1 的论文值同数量级
   （不要求逐位相同，但不得差一个数量级；D19 已完成：Energy 统一 HU+1024 中位数 1.03× 论文）；
3. 方向一致：4 个特征的风险方向与 Supplementary Fig. 1 的 KM 曲线一致
   （正文明确"更紧凑/更球形 → 生存更好"；两处 GLN 属异质性描述，
   方向以图中分组标注为准；Energy 方向需从图中读取后在 D18 核对；
   D19 已完成：单变量 HR/SD 4/4 一致，见 §5.4）；
4. Track A 的 CV C-index 95% CI 不含 0.5（即优于随机；D19 已完成：signature 0.576 [0.543–0.608]，见 §5.6）；
5. 与临床基线的比较使用同一分析集（见 6.1 / 6.2）；
6. 所有差异按"特征实现 / 预处理参数 / 队列版本 / 切分方式 / 指标定义"
   五类归因，写进 `report.md`。

任一条不满足，报告须明确写"该条未满足"及原因，不得调整判据以迁就结果。

## 7. 待核实事项

标注 D16/D18/D19 表示必须关闭的时间点。

- [x] 补充材料可得性：Open access，Supplementary Information 32 页，已获取（见 §9）；
- [x] Supplementary Table 1 是否含 Lung1 训练集 C-index：**不含**，仅验证集；
- [x] 4 个特征的数学定义与编号：见 §3（含正文编号 off-by-one）；
- [x] signature 的 4 个 Cox 系数是否公开：**未公开**；
- [x] 重采样 / spacing：论文未重采样；
- [x] binWidth：25 HU；
- [x] 小波类型：Coiflet 1，8 分解，非降采样；
- [x] 分组阈值：Supplementary Fig. 1 给出 4 个 Lung1 中位数；
- [x] Corrigendum（`10.1038/ncomms5644`）已核对：仅为作者姓名拼写更正
      （Sara Cavalho → Sara Carvalho），**不影响任何数值与特征定义**；
- [ ] D16｜（备查）Fig. 4b 为 GSEA 热图，其特征标注与正文命名存在差异，
      仅影响引用表述，不影响复现；Supplementary Fig. 1 图注已给出一种写法；
- [x] D16｜记录实际使用的 PyRadiomics / SimpleITK / Python 版本与随机种子：
      Python 3.10.22、numpy 1.26.4、SimpleITK 2.5.6、pydicom 3.0.2、
      pyradiomics 3.0.1（镜像 `intern-radiomics:1.0`，ID `f7ee2f9daa9e`）；
      提取消除了随机性（无采样、无随机划分），**不设随机种子**；
- [x] D16｜实测 PyRadiomics 特征数与每例耗时：**537 特征/例**
      （original 73 + wavelet 464），容器内 22.4 s/例、422 例外推约 158 min；
      与论文 440 / 按编号复原的 431 不可比，原因见 §2.4；
- [x] D18｜确认 399 与 395 两种分析集的病人清单一致可追溯：395⊂399，差 4 例（LUNG1-085 T 缺失；LUNG1-167/232/292 N=4）；
- [x] D18｜按 6.2 处理 v1 CV 口径问题：D19 已在 399 例上重跑 v1（0.530 ± 0.026，5×10）；与 v1.3 的 395/5×5 口径差异见 §5.2，正式报告需标 n 与 CV；
- [x] D19｜四模型 5×10 结果回填（§5.1）与协议对齐表（§5.2）；
- [x] D19｜全量 422 例确认 Energy 量纲（§4）；统一 HU+1024 中位数 1.03× 论文；
- [x] D19｜4 个特征方向与 Supplementary Fig. 1 核对（§5.2、§5.4、§6.6-3）；单变量 HR/SD 4/4 一致；多元系数不作判据（§5.5）；
- [x] D19｜Track A 的 95% CI 不含 0.5（§6.6-4）；signature 0.576 [0.543–0.608]（§5.6）；clinical 的 CI 含 0.5（0.495–0.558），如实报告；
- [x] D19｜在 `report.md` 第 6 章完成差异归因（§6.6-6）；六条判据全部满足。
- [x] D19｜stage_bin 编码核对（day19 §7-1/§8-2）：映射正确；单变量 HR 0.93 [0.74–1.16]、log-rank p=0.53；多变量 HR 1.04；age/gender 方向正常；见 §6.2。

已核实的历史口径：545 = 225 + 136 + 95（生存验证 456）+ 89（Lung3，基因关联）。

## 8. 复现说明

- 原论文：`All feature algorithms were implemented in Matlab.`
  即自研实现；论文发表于 2014 年，PyRadiomics 尚未发布（2016 年后才出现），
  因此不存在"论文不用 PyRadiomics"的选择问题，而是**只能方法级复现**。
- 原论文特征直接从 DICOM 原始值计算，**未做归一化**，未按队列/扫描仪校正，
  也**未做体素重采样**。
- 数值级复现要求输入影像、ROI、特征定义、预处理、算法实现和模型参数一致；
  缺少原始 Matlab 实现或必要参数时，不得声称完成数值级复现。
- 本项目只在 Lung1 内做内部验证，结论表述为
  「在论文训练集上的内部验证结果」，不得表述为「复现了论文的外部验证」。
- 复现边界声明（同步写入 `report.md` 方法节）：

  > 我们复现的是**方法层面**：用公开数据 Lung1（422 例）+ PyRadiomics + Cox 模型，
  > 重建与原论文**同类型**的 radiomic signature 与风险分层，并**量化**我们得到的
  > C-index 与论文报告值的差距，逐项分析差异来源（特征实现、预处理参数、队列版本、
  > 切分方式、指标定义）。
  > 我们**不声称**数值一致；任何不一致都必须被解释，而不是被隐藏。

  上述差异将在 `report.md` 第 6 章逐项归因，**不通过调参掩盖不一致**。

## 9. 参考

**论文**

Aerts HJWL, Rios Velazquez E, Leijenaar RTH, et al.
Decoding tumour phenotype by noninvasive imaging using a quantitative radiomics approach.
*Nature Communications*. 2014;5:4006. DOI: `10.1038/ncomms5006`.

Corrigendum: *Nature Communications*. 2014;5:4644. DOI: `10.1038/ncomms5644`
（2014-08-07）。已核对：内容仅为作者姓名拼写更正（Sara Cavalho → Sara Carvalho），
不影响本文件引用的任何数值或特征定义。

**补充材料（已获取，未入库）**

- 内容：Supplementary Methods（特征定义 #1–#55）、Supplementary Figs 1–4、
  Supplementary Tables 1–7、Supplementary References。
- 入口：`https://www.nature.com/articles/ncomms5006#MOESM716`
- 直接地址：`https://static-content.springer.com/esm/art%3A10.1038%2Fncomms5006/MediaObjects/41467_2014_BFncomms5006_MOESM716_ESM.pdf`
- 获取日期：2026-11-10；大小 1,252,817 B；32 页；Open access。
- 本地路径：`data/paper/ncomms5006_supplementary.pdf`（已被 `.gitignore` 排除，
  不随仓库分发，需要时按上述地址重新下载）。

**数据集**

TCIA NSCLC-Radiomics (Lung1). DOI: `10.7937/K9/TCIA.2015.PF0M9REI`.
