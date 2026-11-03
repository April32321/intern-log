---
day: 12
date: 2026-11-03
theme: DICOM 元数据解析与临床表合并
gate: D12
---

# Day 12｜DICOM 元数据解析 + 临床表合并

## 今日目标

- 把 `~/tcia/full` 下的文件夹变成一张 **422 行、每行一个患者**的索引表；
- 统计每例的 CT series 数、层数、层厚、有无 RTSTRUCT、ROI 名称；
- 与临床表合并成 `cohort.csv`，确认不膨胀；
- 产出缺失率表和 1 张生存时间质控图。

## 结论先行

1. `results/tables/index.csv` 共 **422 行 × 10 列**，`PatientID` 唯一；
2. CT 切片合计 **51,230**（= 52,073 全部 DICOM − 422 RTSTRUCT − 421 SEG），
   CT series 422 个，422 例层厚全为 3.0 mm，无患者被拆成多个 CT series；
3. `gtv1_present=False` 与 `has_seg=False` 的集合都恰好是 **LUNG1-128**，
   其 ROI 为 `gtv-pre-op` / `gtv-pre-operat`，与 D11 的观察一致；
4. `cohort.csv` merge 前后都是 **422 行**，`idx-only` 与 `cli-only` 均为空，
   DICOM 与临床表的 `PatientID` 完全一致，无需对齐补丁；
5. **4 例 CT 存在缺层**：LUNG1-014（缺 16）、LUNG1-021（缺 1）、
   LUNG1-085（缺 10）、LUNG1-194（缺 1，README 未记录，D12 新发现）；
6. 终点分布 373 死亡 / 49 删失；`Survival.time` 10–4454 天，无 0/负/缺失。

## 执行分工与环境

代码在 mac 的仓库里开发，全量数据只在 190（`~/tcia/full`）。
两个脚本放在 `code/`，通过环境变量切路径，mac 与 190 用同一条命令。

190 的运行环境（`~/venvs/tcia`，py3.12.3）：

| 包 | 版本 | 说明 |
|---|---|---|
| numpy | 1.26.4 | 与 mac 一致，满足 PyRadiomics 的 `numpy<2` |
| pandas | 2.3.3 | 从 3.0.6 降级，与 mac 对齐，避免 `str` dtype / CoW 行为差异 |
| pydicom | 3.0.2 | 读元数据 |
| matplotlib | 3.11.2 | 质控图 |
| scipy / scikit-learn | 1.17.1 / 1.9.1 | 本日未用 |

190 的 `~/tcia/env.sh`（已 source 进 `.bashrc`）：

```bash
export TCIA_ROOT="$HOME/tcia/full"
export TCIA_CLINICAL="$HOME/tcia/clinical/NSCLC-Radiomics-Lung1.clinical-version3-Oct-2019.csv"
export TCIA_OUT="$HOME/tcia/repo/results"
export PATH="$HOME/venvs/tcia/bin:$PATH"
```

仓库在 190 的副本是 `~/tcia/repo`，代码用 rsync 从 mac 覆盖，
结果用 rsync 拉回 mac 提交；`.git` 只在 mac。

## 步骤 1：DICOM 关键字段

字段速查、RTSTRUCT/SEG 关系图、ROI 命名观察、缺失率表都写在
`notes/dicom.md`。本日只需记住三条：

- `Modality` 是分流判据，文件夹名不可信；
- CT 切片按 `ImagePositionPatient[2]`（z）排序，文件名是 UUID，排序无意义；
- SEG ⊂ RTSTRUCT：SEG 可能是子集，甚至缺失，不能替代 RTSTRUCT。

## 步骤 2：`code/01_check_dicom.py`

```bash
python3 code/01_check_dicom.py                       # $TCIA_ROOT 或 data/raw/full
python3 code/01_check_dicom.py ~/tcia/full           # 190 全量
python3 code/01_check_dicom.py --limit 6 --sample    # 本机 6 例
```

逻辑：

- 只读头部（`stop_before_pixels=True`），逐个患者统计；
- CT 按 `SeriesInstanceUID` 分组，按 `SOPInstanceUID` 去重计层数；
- 层厚取中位数，并用相邻 z 差的中位数交叉验证（差 > 0.05 mm 报警）；
- 相邻 z 差 > 1.5 × 中位间距记为「断档」；
- ROI 取 `StructureSetROISequence` 的 `ROIName`；
- `gtv1_present` **严格**只认归一化后的 `gtv1`，
  `gtv-pre-op` 单独记为 `gtv_alias`，留给 D16 处理。

本机 6 例输出（节选）：

```text
LUNG1-001    CT_series=1 slices=134 thick=3mm z_gap=3 RTSTRUCT=Y SEG=Y GTV1=Y ROI=4
    ROIs: GTV-1, Spinal-Cord, Lung-Left, Lung-Right
LUNG1-009    CT_series=1 slices=105 thick=3mm z_gap=3 RTSTRUCT=Y SEG=Y GTV1=Y ROI=8
    ROIs: Lung-Right, Lung-Left, Esophagus, Spinal-Cord, gtv-4, gtv-3, gtv-2, GTV-1
```

LUNG1-009 同时有 `GTV-1` 和 `gtv-2/3/4`，未被误并，验证了严格匹配。

全量输出存于 `logs/day12-check-190.txt`，汇总：

```text
汇总: 患者=422 CT_series=422 slices=51230 无RTSTRUCT=- 无SEG=['LUNG1-128']
      无GTV1=['LUNG1-128'] 多series=- 有警告=5
```

## 步骤 3：`code/02_build_index.py`

```bash
python3 code/02_build_index.py --expect 6            # 本机
python3 code/02_build_index.py --root ~/tcia/full --out ~/tcia/repo/results   # 190
```

`02` 用 `importlib` 复用 `01` 的 `scan_patient`，不重复实现解析。
列与计划一致：

```text
PatientID, n_ct_series, n_slices, slice_thickness, has_rtstruct,
has_seg, roi_names, gtv1_present, series_dir, rtstruct_path
```

`series_dir` / `rtstruct_path` 存**相对 `--root`** 的路径，便于跨机器比对。
`roi_names` 用 `|` 连接。

写盘前内置断言（任一条失败即退出 1）：

```text
行数 == --expect（默认 422）
PatientID 唯一且非空
无 GTV-1 的集合 == {LUNG1-128}
无 SEG 的集合 == {LUNG1-128}
has_rtstruct 全为 True
```

190 输出：

```text
患者: 422
CT series: 422（多 series: -）
CT 层数合计: 51230
层厚分布: {3.0: 422}
无 RTSTRUCT: -
无 SEG: ['LUNG1-128']
无 GTV-1: ['LUNG1-128']
写出: /home/jiaqiwang/tcia/repo/results/tables/index.csv（422 行 × 10 列）
```

> 51,230 是 CT 切片数，不是 52,073。后者是全部 DICOM（含 422 个 RTSTRUCT、
> 421 个 SEG），两者相差 843，正好对上。

## ROI 命名观察

D11 的 422 例扫描（大小写敏感，按原始字符串计数）：

| ROIName | 例数 |
|---|---:|
| `GTV-1` | 421 |
| `Spinal-Cord` | 411 |
| `Esophagus` | 355 |
| `Lung-Left` / `Lung-Right` | 312 / 312 |
| `gtv-2` | 218 |
| `Heart` | 127 |
| `Lungs-Total` | 97 |
| `gtv-3` | 23 |
| `gtv-4` | 9 |
| `gtv_4r` | 5 |
| `gtv_7` / `gtv-5` | 3 / 3 |
| `gtv-6` / `gtv_2l` | 2 / 2 |

D12 抽样中又见到 `gtv-3_2l2`、`gtv-2_4r`（LUNG1-085），
说明左右/序号后缀可以叠加。归一化规则（小写 + 去 `-`、`_`、空格）后：

```text
GTV-1 / gtv_1 / Gtv 1      -> gtv1
gtv-pre-op                 -> gtvpreop（LUNG1-128 专用）
gtv-2 / gtv_2l / gtv-3_2l2 -> gtv2 / gtv2l / gtv32l2（不并入 gtv1）
```

`gtv-2..7` 是另一套靶区，不能与主靶区合并；肺轮廓同样有
`Lung-Left`（312）与 `Lungs-Total`（97）两套，D13 做全肺特征前需归一化。

## 缺层 4 例

按间距分布判定（3.0 与 6.0 两种值，6.0 的个数 = 缺失层数）：

| 患者 | 实际层数 | 6 mm 间隔 | 缺失层数 | 按 z 推算应有 | z 范围 | 来源 |
|---|---:|---:|---:|---:|---:|---|
| LUNG1-014 | 87 | 16 | 16 | 103 | 306 mm | README 已知 |
| LUNG1-021 | 197 | 1 | 1 | 198 | 591 mm | README 已知 |
| LUNG1-085 | 106 | 10 | 10 | 116 | 345 mm | README 已知 |
| LUNG1-194 | 127 | 1 | 1 | 128 | 381 mm | **D12 新发现** |

校验：`z范围 / 3 + 1` 与「按 z 推算应有」完全一致，
说明都是**孤立丢层**，不存在两段扫描拼接或层距不规则。

对 D13 的影响：

- spacing 可由相邻 z 差推出（恒为 3.0），与 `SliceThickness` 一致；
- 但体积/掩膜计算不能假设切片连续，需检查 RTSTRUCT 轮廓是否落在缺失层上；
- LUNG1-194 已补记到 `data/README.md` 的「已知缺陷」。

## 步骤 4：合并临床表

```python
df = idx.merge(cli, on="PatientID", how="left", validate="one_to_one")
assert len(df) == 422
```

关键输出：

```text
idx 行数/唯一: 422 True
cli 行数/唯一: 422 True
idx-only: []
cli-only: []
merge 后行数: 422
```

`idx-only` / `cli-only` 均为空，即验收第 4 条要求的
「DICOM 与 CSV 的 PatientID 完全一致」，不需要额外的对齐规则。

列名注意：实际是 `gender`（小写）、`clinical.T.Stage`（小写 c），
不是计划文档里写的 `Gender`。

终点与随访：

```text
deadstatus.event: 1 = 373, 0 = 49
Survival.time: count 422, mean 988.86, std 1035.57,
               min 10, 25% 261, 50% 545.5, 75% 1397, max 4454
Survival.time <= 0 的行数: 0
```

事件率 88.4%，删失集中在长随访段（见质控图），符合 Lung1 的结构。

缺失率（`results/tables/missing_rate.csv`）：

| 列 | 缺失 | 缺失率 |
|---|---:|---:|
| `age` | 22 | 5.21% |
| `gender` | 0 | 0.00% |
| `Histology` | 42 | 9.95% |
| `clinical.T.Stage` | 1 | 0.24% |
| `Clinical.N.Stage` | 0 | 0.00% |
| `Clinical.M.Stage` | 0 | 0.00% |
| `Survival.time` | 0 | 0.00% |
| `deadstatus.event` | 0 | 0.00% |

`age` 与 `Histology` 的缺失与 `data/README.md` 记录一致；
`clinical.T.Stage` 的 1 例缺失是本日新增细节。

取值分布（`results/tables/value_counts.csv`，长表：`column,value,n,pct`）：

> 两张表分工：`missing_rate.csv` **按列**回答“每列缺多少”，
> `value_counts.csv` **按取值**回答“每列由什么组成”。两者的 `role` 列
> 都写有这句话，打开 CSV 即可看到用途，不影响 pandas 读取。

| 变量 | 取值 | 例数 | 占比 |
|---|---|---:|---:|
| `age` | 均值 68.04，标准差 10.08，范围 33.7–91.7（n=400） | — | — |
| `gender` | male / female | 290 / 132 | 68.72% / 31.28% |
| `Histology` | squamous cell carcinoma | 152 | 36.02% |
| | large cell | 114 | 27.01% |
| | nos | 63 | 14.93% |
| | adenocarcinoma | 51 | 12.09% |
| | NaN | 42 | 9.95% |
| `clinical.T.Stage` | T2 / T4 / T1 / T3 / **T5** / NaN | 156 / 117 / 93 / 53 / 2 / 1 | 36.97% / 27.73% / 22.04% / 12.56% / 0.47% / 0.24% |
| `Clinical.N.Stage` | N0 / N2 / N3 / N1 / **N4** | 170 / 141 / 85 / 23 / 3 | 40.28% / 33.41% / 20.14% / 5.45% / 0.71% |
| `Clinical.M.Stage` | M0 / **M3** / M1 | 417 / 4 / 1 | 98.82% / 0.95% / 0.24% |
| `Overall.Stage` | IIIb / IIIa / I / II / NaN | 176 / 112 / 93 / 40 / 1 | 41.71% / 26.54% / 22.04% / 9.48% / 0.24% |

取值层面的三个问题：

1. **失效编码**：T 的 `5`（2 例）、N 的 `4`（3 例）、M 的 `3`（4 例）在
   `data/README.md` 中已注明含义丢失，共 9 条。建模时按“未知”处理，
   不能当作有序分期参与数值运算；
2. **M 分期几乎没有区分度**：417/422 为 M0，非零只有 6 例且其中 4 例无法解释，
   D15 多因素 Cox 建议不纳入或合并；
3. **两处缺失不是同一患者**：`clinical.T.Stage` 缺的是 LUNG1-085，
   `Overall.Stage` 缺的是 LUNG1-272，不能合并处理。

`Histology` 的 `nos`（not otherwise specified）是真实类别，不是缺失。

## 步骤 5：质控图

`results/figures/qc_survival_time.png`（1050×600，`bins=100 天`，事件分组叠加）：

- 红色 = death（373），蓝色 = censored（49）；
- 死亡集中在 0–1500 天，删失集中在 2500 天以后；
- 长尾到 4454 天，直方图按 100 天分箱仍可读，未做对数变换。

图内文字用英文，避免服务器缺少中文字体导致方块。

## 验收对照

| 验收标准 | 证据 |
|---|---|
| `index.csv` 422 行，`gtv1_present=False` 里能看到 LUNG1-128 | 02 断言 + 全量输出 |
| `cohort.csv` 仍 422 行（没膨胀） | `validate="one_to_one"`，merge 后 422 |
| 缺失率表 + 1 张质控图已生成 | `missing_rate.csv`（含 `role` 说明列）、`qc_survival_time.png` |
| 能解释 PatientID 是否一致 | `idx-only: []`、`cli-only: []`，两表各 422 唯一 |

## 卡点与报错

### 卡点 1：在 190 上执行 `ssh pvmed190`

`Could not resolve hostname pvmed190`。别名只存在于 mac 的 `~/.ssh/config`，
190 上没有。已经在 190 上就直接执行，不要加 `ssh` 前缀。

### 卡点 2：`rsync ... jiaqiwang@192.168.1.190:...` 报 Permission denied (publickey)

`Host pvmed190` 的匹配对象是命令行里的主机名；写 IP 时不会命中该段配置，
`IdentityFile` 与 `IdentitiesOnly` 都不生效。改用别名：

```bash
rsync -avhP code/ pvmed190:~/tcia/repo/code/
```

### 卡点 3：管道到 `tee` 后长时间无输出

Python stdout 被重定向为块缓冲。确认进程仍在用 `ps`，或加 `-u`；
`02` 本身只在结束时打印汇总，中途静默属正常。

### 卡点 4：pandas 3.0.6 与 mac 的 2.3.3 不一致

190 上 `pip install pandas` 装到 3.0.6，与开发机大版本不同
（字符串 dtype、Copy-on-Write 默认值有差异）。降到 2.3.3 对齐：

```bash
python -m pip install "pandas==2.3.3"
```

### 卡点 5：把 51,230 当成 52,073 的错误

52,073 是全部 DICOM 文件数；CT 切片要减去 422 个 RTSTRUCT 和 421 个 SEG。
差 843 不是丢数据。

### 卡点 6：`gtv1_present` 初版把 `gtv-pre-op` 也算成 True

导致 `无GTV1=-`，与验收标准「False 里能看到 LUNG1-128」冲突。
改为严格匹配 `gtv1`，`gtv-pre-op` 另存 `gtv_alias`。

## Kilo 使用记录

- `01` / `02` 的解析骨架由 Kilo 起草，业务判断（严格 GTV-1、别名分离、
  缺层判定）人工确认；
- 将验收标准直接写成脚本断言，422 行、唯一键、LUNG1-128 特例在写盘前拦截；
- 排障：`ssh` 别名作用域、rsync 密钥匹配、tee 缓冲、pandas 版本差异。

## 今日结论

- DICOM 侧的数据形状已经固定：422 例、422 个 CT series、无多 series、
  层厚统一 3 mm、4 例孤立缺层；
- 队列表与临床表可以一一对应，`PatientID` 无差异，后续不需要映射表；
- 掩膜相关工作的风险点收敛为两个：LUNG1-128 的 `gtv-pre-op` 命名、
  以及 4 例缺层处的轮廓连续性。

## 明日 3 件事（D13）

1. 装/用 DICOM viewer，抽 3 例做影像目视质控（含 LUNG1-128）；
2. 读取 CT 序列与 RTSTRUCT 掩膜，确认缺层处掩膜不跨断档；
3. 确定重采样参数（spacing 用 z 差推导，面内用 `PixelSpacing`）。
