# 分析集定义与固定（Day 18）

- 生成时间：2026-11-13 16:13:30
- 脚本：`code/07_analysis_set.py`
- 临床表：`results/tables/cohort.csv`
- 特征表：`results/tables/features_all.csv`
- 输出：`results/tables/analysis_set.csv`、`results/tables/excluded_patients.csv`、`results/tables/feature_columns.txt`

## 1. 目的

为 Day 18 的四个模型（仅临床、路线 1 签名模型、路线 2 LASSO-Cox、临床+影像）提供**唯一、固定、可复现**的建模人群，确保所有模型使用同一批病人、同一套外层交叉验证折。

## 2. 原则

1. 先声明建模变量与缺失规则，再做排除；禁止对合并表直接 `dropna()`。
2. 只对预先声明的建模变量做完整病例筛选。
3. 分析集一旦固定，下游脚本不得再次筛人、不得重新编码变量。
4. 所有排除逐例记录原因，保留审计清单。

## 3. 病例流转

| 步骤 | 排除 | 剩余 |
|---|---:|---:|
| 原始队列（cohort ∩ features） | 0 | 422 |
| 缺 `age` | 22 | 400 |
| 缺 `gender` | 0 | 400 |
| 缺 `Overall.Stage` | 1 | 399 |
| 缺 `Survival.time` | 0 | 399 |
| 缺 `deadstatus.event` | 0 | 399 |
| **固定分析集** | | **399** |
| 其中 events / censored | | **352 / 47** |

排除按 `EXCLUSION_VARS` 顺序依次进行；同一病例若存在多项缺失，计入首个命中变量。

## 4. 排除清单

### 4.1 `age`（22 例）

LUNG1-056、LUNG1-149、LUNG1-174、LUNG1-241、LUNG1-249、LUNG1-270、LUNG1-275、LUNG1-287、LUNG1-299、LUNG1-303、LUNG1-305、LUNG1-307、LUNG1-308、LUNG1-309、LUNG1-315、LUNG1-328、LUNG1-332、LUNG1-339、LUNG1-341、LUNG1-349、LUNG1-354、LUNG1-385。

### 4.2 `Overall.Stage`（1 例）

LUNG1-272。

完整清单（含 age、gender、stage、Histology、time、event）见 `results/tables/excluded_patients.csv`。

## 5. 变量定义与编码

| 变量 | 来源列 | 类型 | 编码/处理 |
|---|---|---|---|
| 生存时间 | `Survival.time` | 连续 | 天，要求 > 0 |
| 事件 | `deadstatus.event` | 二值 | 1=死亡，0=删失 |
| 年龄 | `age` | 连续 | 年，不缩放、不插补 |
| 性别 | `gender` | 二分类 | male=1，female=0 |
| 分期 | `Overall.Stage` | 二分类 | I/II=0，IIIa/IIIb=1 |
| 组织学 | `Histology` | 多分类 | adeno/squamous/large/nos/unknown；原始缺失→unknown |

下游建模使用编码后的 `gender_num`、`stage_bin`、`histology`；原始 `Histology` 保留用于审计，其中 33 例为空。

不纳入 `clinical.T.Stage`、`Clinical.N.Stage`、`Clinical.M.Stage`，原因：T=5（2 例）与 N=4（3 例）的编码含义已丢失；`clinical.T.Stage` 另缺 1 例（`LUNG1-085`，event=1）；纳入会使分析集进一步缩小，并与 Day 15 的 v1 不可比。

## 6. 纳入 vs 排除基线

| 变量 | 纳入（n=399） | 排除（n=23） |
|---|---:|---:|
| events | 352（88.2%） | 21（91.3%） |
| male | 273（68.4%） | 17（73.9%） |
| female | 126（31.6%） | 6（26.1%） |
| Stage III | 278（69.7%） | 10（43.5%） |
| Stage I–II | 121（30.3%） | 12（52.2%） |
| Stage 缺失 | 0（0.0%） | 1（4.3%） |
| Histology: adeno | 49（12.3%） | 2（8.7%） |
| Histology: squamous | 149（37.3%） | 3（13.0%） |
| Histology: large | 109（27.3%） | 5（21.7%） |
| Histology: nos | 59（14.8%） | 4（17.4%） |
| Histology: unknown | 33（8.3%） | 9（39.1%） |

\* 排除组 23 例中 1 例分期缺失；在 22 例分期可查者中 Stage III 为 10/22 = 45.5%。

年龄：纳入者中位数 68.7（IQR 61.4–75.9；范围 33.7–91.7）。排除组中 22/23 例年龄缺失，无法做组间年龄比较。

## 7. 分析集特征

- n=399；events=352（88.2%）；censored=47（11.8%）
- male 273（68.4%）/ female 126（31.6%）
- Stage III 278（69.7%）/ Stage I–II 121（30.3%）
- 组织学：adeno 49（12.3%）、squamous 149（37.3%）、large 109（27.3%）、nos 59（14.8%）、unknown 33（8.3%）
- 影像特征：537 个，全部有限；列名与顺序锁定于 `feature_columns.txt`

## 8. 下游使用约定

```python
analysis = pd.read_csv("results/tables/analysis_set.csv")
feats = pd.read_csv("results/tables/features_all.csv")
feature_cols = pd.read_csv(
    "results/tables/feature_columns.txt", header=None
)[0].tolist()

model = analysis.merge(
    feats[["PatientID"] + feature_cols],
    on="PatientID", validate="one_to_one",
)
assert len(model) == 399
```

- 所有模型必须从 `analysis_set.csv` 读取病人；
- 不得再次 `dropna()` 或按其他变量筛人；
- 外层折划分只基于这 399 例，见 `cv_assignment.csv`。

## 9. 局限

- 完整病例分析排除 23 例（5.5%），其中 22 例因 `age` 缺失。
- 排除组事件率 91.3%（纳入 88.2%）、Stage III 比例 45.5%（纳入 69.7%）、组织学 unknown 比例 39.1%（纳入 8.3%），提示缺失并非完全随机，结果外推需谨慎。
- 未使用多重插补。若后续做敏感性分析，可在 CV 折内对 `age` 做中位数插补并保留 422 例，但不得与主分析混用。

## 10. 结论

- 固定分析集：**399 例，352 events，47 censored**。
- 临床变量编码、缺失规则、特征列均已锁定。
- 本文件与 `excluded_patients.csv` 共同作为 Day 18 的数据审计证据。

