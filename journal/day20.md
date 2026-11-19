# Day 20 工作日志

- 日期：2026-11-17
- 主题：把"数字不一样"变成"结构化的差异归因" + binWidth 敏感性 + 报告初稿配图
- 状态：差异归因汇总表完成；binWidth 敏感性（10/25/50 × 两条路线）完成；
  报告 `report.md` 升 v2.0（按交付模板重排，含 7 张图）；`target.md` 升 v1.11

## 1. 今日目标

1. 差异归因表：逐项排查，每项给出证据；
2. 敏感性分析（至少 1 项）：binWidth = 10 / 25 / 50 各跑路线 2，看 C-index 波动；
3. 图表打磨：进报告 4–6 张，图注完整、坐标轴带单位、无中文乱码。

## 2. 执行

### 2.1 前置：数据位置与参数文件

- `05_extract_features.py` 的默认 `--raw-root data/raw/full` **不存在**；
  原始 DICOM 在 `/home/jiaqiwang/tcia/full`（422 例，34 G）。所有提取命令都显式指定该路径。
- 新建 `code/params_bw10.yaml`、`code/params_bw50.yaml`；与 `code/params.yaml`
  逐行 diff 确认**只差第 24 行 `binWidth`**（10 / 50），其余完全一致。
- 缓存按 `params_sha256` 与 `script_sha256` 双校验，三套缓存目录相互独立。

### 2.2 冒烟（3 例）

| binWidth | Energy | Compactness2 | original GLN | wavelet-HLH GLN |
|---:|---:|---:|---:|---:|
| 10 | 2.284e9 | 0.2163 | 2562 | 5314 |
| 25 | 2.284e9 | 0.2163 | 4703 | 9021 |
| 50 | 2.284e9 | 0.2163 | 5339 | 1.21e4 |

- Energy 与 Compactness2 三档**逐位相同** → 参数文件只改了分箱，未误伤其他设置。
- 两个 GLN 随 binWidth 单调升高（分箱越粗 → 灰度级越少 → GN 越集中）。
  这一点与直觉相反，已在报告中写明机制，避免被误读为"bw50 实现错了"。
- 冒烟产物统一落在 `results/cache/smoke/`（`.gitignore` 的 `results/cache/` 覆盖），
  不污染 `results/tables`。

### 2.3 全量提取（422 例）

```bash
python code/05_extract_features.py --all \
  --raw-root /home/jiaqiwang/tcia/full --params code/params_bw10.yaml \
  --cache-dir results/cache/features_bw10 --out-name features_all_bw10 \
  --jobs 4 --chunk 80 --expect 422
```

- bw10：2820.1 s（47.0 min），422/422 成功，537 特征，非有限值 0；
- bw50：818.8 s（13.6 min），422/422 成功；`--expect 422` 保证不会少人。
- 单例耗时差异来自磁盘缓存：bw10 首次冷读 26.3 s/例，bw50 暖缓存 7.5 s/例。

### 2.4 敏感性 CV（同一分析集、同一 5×10 折、seed=42）

| 运行 | 命令要点 | 耗时 |
|---|---|---:|
| bw10 lasso | `--models lasso --out-dir results/cache/sens_bw10` | 2590.9 s |
| bw10 signature | `--models signature --out-dir results/cache/sens_bw10_sig` | 19 s |
| bw50 signature | 同上，指向 bw50 特征表 | 20 s |
| bw50 lasso | 同上，`--out-dir results/cache/sens_bw50` | 3166.1 s |

注意：`09` 对子集运行强制要求非默认 `--out-dir/--figures-dir`，且只在 50 折全部结束后
一次性落盘——中途崩溃等于全部重跑。

## 3. 结果

### 3.1 binWidth 敏感性

| binWidth | 路线 1 signature | 路线 2 lasso | 路线 2 特征数 | 路线 2 log-rank p<0.05 |
|---:|---|---:|---|---:|
| 10 | 0.5803 ± 0.0372 | 0.5830 ± 0.0328 | 11.6 [2–47] | 24% |
| 25（主结果） | 0.5808 ± 0.0377 | 0.5831 ± 0.0348 | 11.3 [2–42] | 18% |
| 50 | 0.5812 ± 0.0384 | 0.5901 ± 0.0328 | 11.5 [2–53] | 30% |

- 路线 1 全距 0.0009；路线 2 全距 0.007（≈0.2 SD，且非单调）。
- 结论：**判别力对 binWidth 不敏感**；不能用三点差异声称"bw50 更好"。

### 3.2 选择稳定性（关键反向证据）

| 特征 | bw10 | bw25 | bw50 | 模式 |
|---|---:|---:|---:|---|
| wavelet-HHL_firstorder_TotalEnergy | 0.90 | 0.86 | 0.84 | 稳定 |
| wavelet-LHL_firstorder_Skewness | 0.82 | 0.78 | 0.88 | 稳定 |
| wavelet-LLH_firstorder_Variance | 0.74 | 0.68 | 0.60 | 缓慢下降 |
| wavelet-LHL_glcm_MCC | 0.08 | 0.60 | 0.76 | **非单调（V 形）** |
| wavelet-LHH_glcm_Correlation | 0.44 | 0.56 | 0.76 | 上升 |
| wavelet-HHH_glcm_Idn | 0.00 | 0.32 | 0.04 | **非单调** |

"掉下去又跳回来"说明中频 GLCM 特征的入选接近随机，不是分箱的单调函数。
这与 D19 §3.4 的"固定签名与 LASSO 特征集几乎不重叠、性能却相当"一致：
**性能稳健 ≠ 某个 signature 稳健**。

### 3.3 量纲锚点

| 特征 | bw10 | bw25 | bw50 | 论文 |
|---|---:|---:|---:|---:|
| original GLN | 499.2 | 953.7 | 1225 | 984.7 |
| wavelet-HLH GLN | 1184 | 2085 | 2897 | 1111 |

bw25 的 GLN 中位数最接近论文值（0.97×），支持"binWidth=25 与论文对齐"的结论；
但 GLN 是计数类量，**不能跨 binWidth 比较**与论文的倍数。

## 4. 报告与图

### 4.1 `report.md` v2.0（按交付模板重排）

v1.1 先补齐内容（§3.4 图表、§6.6 汇总表、§6.8 敏感性），随后按交付模板重排为 v2.0：

- YAML 头（title/author/date/repo/env/kilo_version/model）；
- 十章结构：摘要 / 目标与范围 / 数据 / 方法 / 结果 / 差异分析 / 局限 /
  可复现性 / 合规 / 参考文献；
- 三个附录：A 术语表（18 条）、B 关键数字—来源对照表（16 条）、C 环境清单；
- 敏感性从旧 §6.8 移入 §5.4（结果章），差异分析保留 §6.1–§6.7；
- 图改为**就近嵌入**，图号按首次出现递增：图 1→§3.2、图 2→§3.3、
  图 3–6→§5.1、图 7→§5.4；删除原先集中贴图的"§5.5 图表"一节；
- 全篇交叉引用与新编号对齐；正文约 2.2 万字符（远超 2,000 字要求）；
  两处命令块使用 `bash` 围栏；7 张图的相对路径全部存在。
- 两处口径隐患在重排时一并纠正：重采样明确为"不重采样、原始体素 3 mm"
  （未使用 1×1×1 mm）；binWidth 标为"25 HU 已核对 + 起点不可验证 + 已做敏感性"。

### 4.2 新增脚本 `code/13_report_figures.py`

只读现有产物，不重跑 `09` 主流程：

| 图 | 内容 | 关键数字 |
|---|---|---|
| 1 | `data_preview_ct_gtv.png` CT + GTV-1 轮廓（轴位/冠状位） | 156.2 / 34.8 cm³ |
| 2 | `qc_survival_time.png` 生存时间分布 + 累积死亡 | n=399，中位 OS 555 天 |
| 3 | `km_risktable_*.png` 折外 KM + at-risk 表 | signature 199/200，p=0.060 |
| 4 | `cindex_boxplot.png`（09 产出） | 50 折分布 |
| 5 | `forest_combined.png`（09 产出） | pooled HR + 95% CI |
| 6 | `calibration_1y_2y.png` 十分位校准 | ICI 0.076 / 0.050 |
| 7 | `binwidth_sensitivity.png` 三点曲线 | 见 §3.1 |

**校准图的方法说明**：`09` 不保存逐折模型，`oof_predictions.csv` 的 risk 又是折内尺度，
不能直接拼。脚本按 `09` 的 signature 折内流程（训练折 StandardScaler + penalizer 0.1）
在固定 5×10 折上重拟合，用 Breslow 基线得到 365/730 天预测生存率，10 个 repeat 取平均。
自检：平均预测的风险排序 C-index = 0.572（1 年）/ 0.575（2 年），与 pooled OOF 0.576 一致；
ICI 0.076 / 0.050。该图不使用 LASSO 路线（逐折特征集不同，单条校准曲线无意义）。

**viewer 截图**：用 `data_preview_ct_gtv.png` 替代人工截图（直接读 DICOM + RTSTRUCT，
可复现）。若导师要求真实软件截图，需另行补。

## 5. 问题与限制

1. 50 折 `mean ± SD` 不是 95% CI；三点差异只在"折间波动"意义上解读。
2. binWidth 敏感性只覆盖 10/25/50 HU，未覆盖更细/更粗（如 5/100）。
3. 路线 2 在 bw50 的 0.590 略高，但非单调，不得挑选该点作为主结果。
4. 校准图是**内部** OOF 校准，不能替代外部验证；预测值域窄（1 年 0.49–0.71）
   与 C-index≈0.58 一致。
5. 仍未完成：422 例 signature-only、5×5 敏感性、apparent C-index。
6. `features_all_bw10/bw50.csv` 已写入 `results/tables`（4.2–4.3 MB），
   属于正式产物；对应的逐例缓存与 CV 产物在 `results/cache/`（gitignore）。

## 6. 产物

| 文件 | 内容 |
|---|---|
| `report.md` | v2.0：按交付模板十章 + 三附录；敏感性移入 §5.4；新增 §8/§9/§10 与附录 A/B/C |
| `results/repro/target.md` | v1.11：§5.2 新增行、§5.7 binWidth 敏感性 |
| `code/13_report_figures.py` | 报告用图脚本（只读产物 + 校准重拟合） |
| `code/params_bw10.yaml` `code/params_bw50.yaml` | 仅 binWidth 不同 |
| `results/tables/features_all_bw10.csv` `features_all_bw50.csv` | 422 × 537 特征 |
| `results/figures/report/` | 图 1/2/3/6/7、`calibration_points.csv`、`CAPTIONS.md` |
| `results/cache/sens_bw10` `sens_bw10_sig` `sens_bw50` `sens_bw50_sig` | 敏感性 CV 产物 |
| `logs/extract_bw10.log` `extract_bw50.log` `cv_bw*.log` | 运行日志 |

## 7. 下一步

1. 422 例 signature-only 敏感性（回答"排除 age/stage 缺失是否改变结论"）。
2. 5×5 重复敏感性（对齐论文的重复次数）。
3. apparent C-index（全量拟合，明确标 `apparent`）。
4. 若需要外部可比性：申请 Lung2 / H&N 数据；否则报告中继续声明"方法级复现"。
5. 图表收尾：如导师要求真实 viewer 截图，补 1–2 张；其余图已可复现生成。
