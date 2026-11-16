# 交叉验证设计（Day 18）

- 生成时间：2026-11-13 16:14:10
- 脚本：`code/08_cv_split.py`
- 状态：**建模前预先指定**（pre-specified）；后续模型不得更改切分
- 分析集：`results/tables/analysis_set.csv`
- 划分文件：`results/tables/cv_assignment.csv`
- 审计文件：`results/tables/cv_audit.csv`

## 1. 目标

在没有独立外部验证集的前提下，用重复分层 K 折交叉验证估计四个模型的折外性能，并给出带不确定性的性能数字。

## 2. 分析集

- n = **399**
- events = **352**（88.2%）
- censored = **47**（11.8%）
- 特征数：537（列名锁定于 `feature_columns.txt`）
- 分析集定义见 `analysis_set.md`；本设计不重新筛人

## 3. 外层划分

```python
RepeatedStratifiedKFold(
    n_splits=5, n_repeats=10, random_state=42
)
```

- 折数：5 × 10 = **50** 个外层测试折
- 分层变量：`deadstatus.event`（1=死亡，0=删失）
- 随机种子：`SEED=42`
- 每个病人被测试 **10** 次（每个重复一次）
- 训练折大小：319–320 例
- 测试折大小：79–80 例
- 测试折 event 数：70–71
- 测试折 censored 数：9–10

选择理由：5 折使每轮训练集约占 80%，10 次重复降低“单次划分运气”带来的估计波动；50 个折外分数足以报告均值±SD。

## 4. 内层划分

每个外层训练折内部再做 5 折分层 CV，仅用于选择超参数（LASSO-Cox 的 alpha）与完成折内特征筛选；外层验证折不参与任何 fit 或选择。

```python
StratifiedKFold(
    n_splits=5, shuffle=True,
    random_state=SEED + 100 * repeat + fold
)
```

## 5. 折内处理顺序（下游实现必须遵守）

1. 缺失/方差过滤（只用训练折）
2. 高度相关去冗余：`|r| > 0.9` 保留一个（只用训练折）
3. 单变量 Cox 筛选：`p < 0.05`（只用训练折）
4. 标准化：`StandardScaler.fit(训练折)`
5. LASSO-Cox：`l1_ratio=1.0`，alpha 由内层 CV 选择
6. 外层训练折拟合，外层验证折只 `predict`

## 6. 指标与汇总

- 主指标：每个外层测试折的 C-index
  - `sksurv.metrics.concordance_index_censored(event, time, risk)`
  - risk 越高表示风险越高，符号不得写反
- 汇总：50 折的均值 ± 标准差
- 辅助：中位数 [IQR]、事件分层 log-rank（训练折中位数阈值）
- log-rank 汇总：中位 p、p<0.05 的折占比；不把 50 个相关 p 值当作独立检验合并
- 次级汇总：OOF（每例在每轮被预测一次，10 轮取平均）C-index 与 log-rank

## 7. 模型对照

四个模型必须共用本文件的 50 个外层折：

1. 仅临床
2. 路线 1：先验 signature（4 特征）
3. 路线 2：LASSO-Cox（全特征，折内筛选）
4. 临床 + 影像

## 8. 7:3 留出（可选，非主结果）

如额外做一次固定 7:3 分层留出，仅作为稳定性补充：

```python
train_test_split(..., test_size=0.3, stratify=event, random_state=42)
```

7:3 的结果不得替代 5×10 CV 的主结果，也不得用来反向挑选模型。

## 9. 随机种子与复现

- 外层：`RepeatedStratifiedKFold(random_state=42)`
- 内层：`SEED + 100 * repeat + fold`
- 记录环境版本：Python 3.12.3，scikit-learn 1.9.1
- 禁止 seed shopping：不得因某个种子结果更好而更换种子
- 完整测试折分配见 `cv_assignment.csv`；训练折 = 该重复中除测试折外的其余病例

## 10. 审计结果

- 外层测试折：**50** 个
- 每个重复测试例数：399
- 每个重复 event 数：352
- 每个重复 censored 数：47
- 训练/测试无交集、每例每轮恰好测试一次、每折事件与删失均非空：**通过**

| repeat | folds | n_test | events_test | censored_test |
|---:|---:|---:|---:|---:|
| 0 | 5 | 399 | 352 | 47 |
| 1 | 5 | 399 | 352 | 47 |
| 2 | 5 | 399 | 352 | 47 |
| 3 | 5 | 399 | 352 | 47 |
| 4 | 5 | 399 | 352 | 47 |
| 5 | 5 | 399 | 352 | 47 |
| 6 | 5 | 399 | 352 | 47 |
| 7 | 5 | 399 | 352 | 47 |
| 8 | 5 | 399 | 352 | 47 |
| 9 | 5 | 399 | 352 | 47 |

## 11. 防泄漏检查清单

- [ ] 外层循环前没有全量 `fit/transform/corr/Coxnet`
- [ ] 标准化、相关过滤、单变量 Cox、alpha 选择只使用训练折
- [ ] 验证折只用于 `predict` 与打分
- [ ] KM 阈值来自训练折中位数，不来自验证折
- [ ] 四个模型使用同一份 `cv_assignment.csv`
- [ ] C-index 的 risk 方向正确（越高越差）

## 12. 限制

- 内部 CV 只能说明“在同一队列内换划分”的稳定性，不能替代外部验证，也不能证明跨人群可迁移。
- 50 个折共享病人，折间分数不独立；SD 描述划分波动，不能当作 95% 置信区间。
- 事件率较高（88%），C-index 与 log-rank 的折间波动可能较小，报告时仍需给出 SD。

