# 特征质控报告（Day 17）

- 生成时间：2026-11-13 14:35:00
- 脚本：`code/06_qc_features.py`
- 特征表：`results/tables/features_all.csv`
- 索引：`results/tables/index.csv`；本地数据：`/home/jiaqiwang/tcia/full`

## 1. 行数与缺例

- 索引中应有病例（`has_rtstruct=True` 且本地存在目录）：**422**
- 特征表实际行数：**422**；列数 **538**（`PatientID` + 537 特征）
- 缺例：**0**（全部命中）

## 2. 缺失率

- 缺失率 > 20.00% 的特征：**0** 个

- 明细：`results/tables/feature_missing_rate.csv`

## 3. 零方差 / 全缺失

- 零方差或全缺失列：**0** 个（建议剔除）

- 明细：`results/tables/feature_zero_variance.csv`

## 4. 非有限值

- NaN / inf 总数：**0**

## 5. 基准表一致性

- 未找到可比的基准表（`results/tables/features_10.csv` 缺失或无交集），跳过。

## 6. 并行一致性

- 比对表：`features_all.csv vs features_repro_j1.csv`；病例 **5** 例
- 最大相对差：**0.000e+00**；最大绝对差：0.000e+00
- 相对差 > 1e-06 的列：**0**

## 7. 分布可视化

- 随机抽取 6 个特征（seed=17）：
  - `wavelet-HLL_glrlm_RunPercentage`
  - `original_glrlm_GrayLevelNonUniformityNormalized`
  - `wavelet-LLH_firstorder_Skewness`
  - `wavelet-HHL_glcm_Imc2`
  - `wavelet-HHH_glcm_Idn`
  - `wavelet-LHH_glrlm_ShortRunLowGrayLevelEmphasis`
- 图：`results/figures/qc/hist_random6.png`

## 8. 特征构成

| 影像类型 | 特征类 | 数量 |
|---|---|---:|
| original | firstorder | 18 |
| original | glcm | 24 |
| original | glrlm | 16 |
| original | shape | 15 |
| wavelet | firstorder | 144 |
| wavelet | glcm | 192 |
| wavelet | glrlm | 128 |

- 每例特征数：[537]（应与上表合计一致）

## 9. 结论

- 已执行的检查通过；未执行：基准表一致性

