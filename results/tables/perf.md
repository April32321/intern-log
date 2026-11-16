# 固定折 Cox 模型性能汇总

- 生成时间：2026-11-16 16:25
- 分析集：399 例 / 352 events
- CV：5×10 重复分层 K 折，seed=42，共 200 个模型-折记录
- 折内流程：方差过滤 → |r|>0.9 去冗余 → 单变量 Cox p<0.05 → 标准化 → （LASSO 内层 5 折选 alpha）→ 最终 Cox
- 运行耗时：2917.6s

## 1. 性能

| model | folds | C-index (mean ± SD) | median | train−test gap | log-rank p<0.05 | features mean [min–max] | alpha median [min–max] | Cox penalizer | fallback folds |
|---|---|---|---|---|---|---|---|---|---|
| clinical | 50 | 0.530 ± 0.026 | 0.524 | 0.026 | 0.100 | 7.0 [7–7] | – | 0.10 | 0 |
| signature | 50 | 0.581 ± 0.038 | 0.583 | 0.003 | 0.200 | 4.0 [4–4] | – | 0.10 | 0 |
| lasso | 50 | 0.583 ± 0.035 | 0.589 | 0.049 | 0.180 | 11.3 [2–42] | 5.633e-02 [7.603e-03–2.004e-01] | 0.10 | 1 |
| combined | 50 | 0.581 ± 0.034 | 0.585 | 0.057 | 0.280 | 8.0 [8–8] | 5.633e-02 [7.603e-03–2.004e-01] | 0.10 | 1 |

## 2. LASSO 特征稳定性（前 10）

| feature | 被选折数 | 频率 | 平均 LASSO 系数 |
|---|---|---|---|
| wavelet-HHL_firstorder_TotalEnergy | 43 | 0.860 | 0.1579 |
| wavelet-LHL_firstorder_Skewness | 39 | 0.780 | -0.0882 |
| wavelet-LLH_firstorder_Variance | 34 | 0.680 | -0.0479 |
| wavelet-LHL_glcm_MCC | 30 | 0.600 | 0.0788 |
| wavelet-LHH_glcm_Correlation | 28 | 0.560 | -0.0854 |
| original_shape_Maximum3DDiameter | 24 | 0.480 | 0.0621 |
| wavelet-HHL_firstorder_Skewness | 21 | 0.420 | 0.0364 |
| wavelet-HLH_firstorder_TotalEnergy | 20 | 0.400 | 0.1190 |
| wavelet-LHH_glcm_MCC | 17 | 0.340 | 0.0472 |
| wavelet-HHH_glcm_Idn | 16 | 0.320 | 0.0382 |

## 3. 主要系数（跨折入选频率 ≥ 0.99）

| model | term | folds | HR (pooled 95% CI) |
|---|---|---|---|
| clinical | age | 50/50 | 1.01 [1.01–1.02] |
| clinical | gender_num | 50/50 | 1.17 [1.13–1.21] |
| clinical | hist_large | 50/50 | 0.92 [0.88–0.96] |
| clinical | hist_nos | 50/50 | 0.94 [0.89–0.99] |
| clinical | hist_squamous | 50/50 | 1.12 [1.07–1.17] |
| clinical | hist_unknown | 50/50 | 1.09 [1.02–1.16] |
| clinical | stage_bin | 50/50 | 1.04 [1.00–1.07] |
| signature | original_firstorder_Energy | 50/50 | 1.09 [1.07–1.10] |
| signature | original_glrlm_GrayLevelNonUniformity | 50/50 | 1.09 [1.06–1.13] |
| signature | original_shape_Compactness2_derived | 50/50 | 0.95 [0.93–0.96] |
| signature | wavelet-HLH_glrlm_GrayLevelNonUniformity | 50/50 | 1.06 [1.03–1.10] |
| combined | age | 50/50 | 1.01 [1.01–1.02] |
| combined | gender_num | 50/50 | 1.09 [1.06–1.13] |
| combined | hist_large | 50/50 | 0.96 [0.91–1.00] |
| combined | hist_nos | 50/50 | 0.96 [0.91–1.02] |
| combined | hist_squamous | 50/50 | 1.06 [1.01–1.11] |
| combined | hist_unknown | 50/50 | 1.24 [1.16–1.33] |
| combined | radiomics_score | 50/50 | 1.51 [1.49–1.54] |
| combined | stage_bin | 50/50 | 0.97 [0.94–1.01] |

## 4. 口径与限制

1. C-index 在外层测试折上计算；主结果是 50 折的均值 ± SD。这些折共享病人（每例被测试 10 次），**SD 不是 95% CI**。
2. 方差过滤、相关性去冗余、单变量 Cox、标准化和 alpha 选择全部只在当前外层训练折内完成；测试折不参与任何拟合。
3. log-rank 的高低危阈值取该折**训练集**风险的中位数，在测试折上分组；`log-rank p<0.05` 是 50 折中显著的比例。
4. train−test gap = 训练折 C-index − 测试折 C-index 的均值，用于描述乐观偏差；正值越大，过拟合越明显。
5. KM 图只使用**单个 repeat** 的折外预测，每组 399 例各出现一次；不把 10 个 repeat 的 3990 条记录合并，避免同一病人重复计入。
6. 森林图的 HR 为跨折逆方差合并（每折最终 Cox 的 `coef` 与 `se(coef)`），误差条是合并后的解析 95% CI。50 折共享病人、且 Cox 带惩罚，该 CI 为近似值、可能偏窄，不能替代病人层面 bootstrap；LASSO 模型只展示入选频率≥ 0.50 的特征。
7. 所有 Cox 拟合使用 0.1 / 1 / 10 的惩罚阶梯，表中记录实际生效的惩罚值中位数；若与论文的无惩罚 Cox 并排比较，需在方法中声明。
8. LASSO 在某折选中 0 个特征时，回退到单变量 p 值最小的前 10 个特征，并在 `notes` 中标记；回退折仍计入稳定性分母，但不贡献入选次数，也不写入 LASSO 的逐折系数表与森林图。

## 5. 产物

- `results/tables/cv_folds.csv`：逐折指标
- `results/tables/oof_predictions.csv`：折外风险与高低危标签
- `results/tables/selection_stability.csv`：LASSO 特征稳定性
- `results/tables/cv_coefficients.csv`：逐折 Cox 系数
- `results/tables/coefficient_summary.csv`：系数跨折汇总
- `results/tables/perf.csv`：性能汇总（机器可读）
- `results/tables/perf.md`：本报告
- `results/figures/cv/cindex_boxplot.png`：图形
- `results/figures/cv/km_oof_clinical_repeat0.png`：图形
- `results/figures/cv/km_oof_signature_repeat0.png`：图形
- `results/figures/cv/km_oof_lasso_repeat0.png`：图形
- `results/figures/cv/km_oof_combined_repeat0.png`：图形
- `results/figures/cv/forest_clinical.png`：图形
- `results/figures/cv/forest_signature.png`：图形
- `results/figures/cv/forest_lasso.png`：图形
- `results/figures/cv/forest_combined.png`：图形

