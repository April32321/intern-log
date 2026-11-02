# 数据说明：NSCLC-Radiomics（Lung1）v4

## 数据身份

| 项 | 值 |
|---|---|
| Collection | NSCLC-Radiomics（Lung1） |
| 版本 | Version 4，2020-10-22 更新 |
| DOI | `10.7937/K9/TCIA.2015.PF0M9REI` |
| 论文 | Aerts et al. 2014, *Nature Communications*, DOI `10.1038/ncomms5006` |
| 许可 | **CC BY-NC 3.0**（非商业使用；必须引用 DOI） |
| 规模 | 422 subjects / 422 studies / 1,265 series / 52,073 images / 35.78 GB |
| 模态 | CT、RTSTRUCT、SEG |

数据引用：

> Aerts, H. J. W. L., Wee, L., Rios Velazquez, E., Leijenaar, R. T. H., Parmar, C.,
> Grossmann, P., Carvalho, S., Bussink, J., Monshouwer, R., Haibe-Kains, B.,
> Rietveld, D., Hoebers, F., Rietbergen, M. M., Leemans, C. R., Dekker, A.,
> Quackenbush, J., Gillies, R. J., Lambin, P. (2014).
> **Data From NSCLC-Radiomics (version 4)** [Data set]. The Cancer Imaging Archive.
> <https://doi.org/10.7937/K9/TCIA.2015.PF0M9REI>

## 下载路线

采用 **路线 B：TCIA REST API**（`getSeries` / `getImage`）。

选择理由：

1. 190（Ubuntu 24.04）到 `www.cancerimagingarchive.net` 的 TLS 握手超时
   （`curl: (28) SSL connection timeout`，`openssl s_client` 20 秒无输出），
   到 `services.cancerimagingarchive.net` 返回 `HTTP 000`，无法在 190 上直连 TCIA；
2. mac 可以访问 TCIA，mac 与 190 在局域网内可达；
3. REST API 可以脚本化，便于 D11 实现 `--full` / `--resume` / `--retry`；
4. 新版 TDR（156 MB）下载慢，而且装完后仍需访问 TCIA，因此只作为备用，不作为主路径。

备选路线 C（IDC / GCS）未采用。如果后续改用 IDC，必须记录来源、版本以及与 TCIA v4 的差异。

> **D11 实际落地（2026-11-02）**：全量数据不是由 `00_download.py` 重新下载的。
> t12ub 上已有 2026-10-14 完成的 NSCLC-Radiomics v4（IDC 布局），核验为
> 422 患者 / 1,265 series / 52,073 DICOM，DICOM 字节 35,775,589,886（约 35.78 GB），
> 与本页估算一致。脚本保留为可复现路线与备用方案。
> 重排、SSH 与传输过程见 `journal/day11.md`。

### 下载脚本

`code/00_download.py` 默认按 D11 的仓库布局写入 `data/raw/`，日志/完成标记写入 `logs/`。

在 190 上复现当前实际路径时，显式指定：

```bash
python3 code/00_download.py --full --resume --retry 3 \
  --out /home/jiaqiwang/tcia/full \
  --log-dir /home/jiaqiwang/tcia/logs
```

小样本同理：

```bash
python3 code/00_download.py --resume \
  --out /home/jiaqiwang/tcia/raw/dicom \
  --log-dir /home/jiaqiwang/tcia/logs
```

- 完成标记写在 `logs/done/<SeriesUID>`，记录 `image_count`；
  `--resume` 会复核标记与目录内实际文件数，不一致就重新下载；
- `logs/done/` 和 `logs/download_failed.txt` 已在 `.gitignore` 中排除。

## 实际位置

### t12ub（数据源）

2026-10-14 完成下载，原始为 IDC 布局；D11 已重排为与 190 一致的 `full/` 结构。

| 内容 | 路径 |
|---|---|
| 原始全量（IDC 布局） | `/home/jqw/.data/nsclc-radiomics/nsclc_radiomics/` |
| 系列级 metadata | `/home/jqw/.data/nsclc-radiomics/metadata/metadata.csv` |
| 全量 manifest | `/home/jqw/.data/nsclc-radiomics/NSCLC-Radiomics-Version-4-Oct-2020-NBIA-manifest.tcia` |
| 临床 CSV | `/home/jqw/.data/nsclc-radiomics/NSCLC-Radiomics-Lung1.clinical-version3-Oct-2019.csv` |
| 重排后全量（硬链接） | `/home/jqw/tcia/full/<PatientID>/<Modality>/<SeriesInstanceUID>/` |
| 重排脚本 | `/home/jqw/tcia/reorg.py` |
| Python 环境 | `/home/jqw/venvs/tcia`（pydicom 3.0.2） |

### 190（目标）

| 内容 | 路径 |
|---|---|
| 临床 CSV | `/home/jiaqiwang/tcia/clinical/NSCLC-Radiomics-Lung1.clinical-version3-Oct-2019.csv` |
| 全量 manifest | `/home/jiaqiwang/tcia/manifests/NSCLC-Radiomics-v4.tcia` |
| 小样本 DICOM | `/home/jiaqiwang/tcia/raw/dicom/LUNG1-001/{CT,SEG,RTSTRUCT}/<SeriesUID>/` |
| 全量数据（D11） | `/home/jiaqiwang/tcia/full/<PatientID>/<Modality>/<SeriesInstanceUID>/` |
| 系列级 metadata | `/home/jiaqiwang/tcia/metadata/metadata.csv` |
| 日志 | `/home/jiaqiwang/tcia/logs/` |

这些路径在 t12ub / 190 上，不在 git 仓库内；仓库只保留本说明文件。

### D11 核验口径

- 全量应为 **422 患者 / 1,265 series / 52,073 DICOM**；
- 模态分布：CT 422、RTSTRUCT 422、SEG 421
  （SEG 少 1 例，与官方总数 1,265 一致，不是下载缺失）；
- DICOM 字节数（不含 metadata.csv 等非 DICOM 文件）：

  ```bash
  find <full>/ -name '*.dcm' -printf '%s\n' | awk '{s+=$1} END {print s}'
  # 35775589886
  ```

- 不要用 `du -sb <根目录>` 直接比对：t12ub 源根目录还包含
  metadata.csv（684,079 B）、manifest（77,374 B）、临床 CSV（23,335 B）和
  sample.tcia（401 B），合计 785,189 B。

## 已落地与校验

### 临床 CSV

- 423 条记录（1 行表头 + 422 行数据），10 列，422 个唯一 `PatientID`；
- 表头：

  ```text
  PatientID,age,clinical.T.Stage,Clinical.N.Stage,Clinical.M.Stage,Overall.Stage,Histology,gender,Survival.time,deadstatus.event
  ```

- `Survival.time` 单位为**天**，从治疗开始计算；
- `deadstatus.event`：`1` = 死亡，`0` = 右删失；
- 注意实际列名是 `gender`（小写）和 `clinical.T.Stage`（小写 `c`），不要按计划文档里的 `Gender` 写死；
- `wc -l` 显示 422 是因为文件末行没有换行符，Python `csv` 读取为 423 条记录，不是数据缺失。

校验：

```bash
python3 - <<'PY'
import csv
p = "/home/jiaqiwang/tcia/clinical/NSCLC-Radiomics-Lung1.clinical-version3-Oct-2019.csv"
rows = list(csv.reader(open(p, newline="", encoding="utf-8-sig")))
print("总记录数:", len(rows))
print("数据行数:", len(rows) - 1)
print("列数:", len(rows[0]))
print("唯一 PatientID:", len({r[0] for r in rows[1:]}))
PY
```

期望：`423`、`422`、`10`、`422`。

### 全量 manifest

- 1,265 个唯一 series UID；
- 1,271 行（6 行 header + 1,265 个 UID）；
- `manifestVersion=3.0`；
- 下载服务器：`public.cancerimagingarchive.net`。

校验：

```bash
grep -c '^1\.' /home/jiaqiwang/tcia/manifests/NSCLC-Radiomics-v4.tcia
# 1265

grep '^1\.' /home/jiaqiwang/tcia/manifests/NSCLC-Radiomics-v4.tcia | sort -u | wc -l
# 1265
```

### 小样本 LUNG1-001

| Modality | 文件数 | 说明 |
|---|---:|---|
| CT | 134 | 术前 CT |
| SEG | 1（536 frames） | 4 个 segment：Neoplasm, Primary；Lung；Lung；Spinal cord |
| RTSTRUCT | 1 | GTV-1、Spinal-Cord、Lung-Left、Lung-Right |

- 共 3 个 series；
- 136 个 DICOM 文件（`.dcm`）+ 3 个 `LICENSE` 文件；
- 总体积约 87 MB；
- 3 个 `LICENSE` 分别位于三个 series 目录下，是 CC BY-NC 3.0 的合规材料，**不要删除**。

校验：

```bash
find ~/tcia/raw/dicom/LUNG1-001 -type f -name '*.dcm' | wc -l
# 136

find ~/tcia/raw/dicom/LUNG1-001 -type f -name 'LICENSE' | wc -l
# 3

du -sh ~/tcia/raw/dicom/LUNG1-001
# 约 87M
```

### 全量数据（D11，t12ub → 190）

来源：t12ub 上 2026-10-14 完成的下载（IDC 布局）；D11 用 pydicom + 硬链接重排为
`<PatientID>/<Modality>/<SeriesInstanceUID>/`，再用 rsync 传到 190。

| 项 | 值 |
|---|---:|
| 患者 | 422 |
| series | 1,265 |
| DICOM 文件 | 52,073 |
| 模态 | CT 422 / RTSTRUCT 422 / SEG 421 |
| DICOM 字节 | 35,775,589,886（约 35.78 GB） |
| `du -sh`（t12ub 重排后） | 34G（硬链接，不额外占盘） |
| 190 端验收 | 52,073 / 422 / 1,265 / 35,775,589,886，与 t12ub 完全一致 |
| rsync 汇总 | `sent 35.79G bytes  received 1.01M bytes  3.63M bytes/sec` |
| 系列级索引 | `/home/jiaqiwang/tcia/metadata/metadata.csv`（1,266 行，D11 同步） |

对应磁盘占用与官方 35.78 GB 一致；详细命令与卡点见 `journal/day11.md`。

### 实际清点结果（D11）

对照 Day11 第 3–4 步，官方值与实际值如下：

| 指标 | 官方 | 实际 | 差异 | 解释 |
|---|---:|---:|---:|---|
| 患者数 | 422 | 422 | 0 | `metadata.csv` 的 1,265 行里唯一 `PatientID` 为 422；临床 CSV 共 423 行（1 表头 + 422 数据） |
| series | 1,265 | 1,265 | 0 | CT 422 + RTSTRUCT 422 + SEG 421 |
| 图像文件 | 52,073 | 52,073 | 0 | t12ub 与 190 两端逐文件计数一致 |
| 体积 | 35.78 GB | 35,775,589,886 B（35.78 GB） | 约 -0.01% | 只统计 `*.dcm` 字节；`du -sh` 显示的 34G 是 GiB 口径 |

统计口径说明：

- 体积比对只用 DICOM 字节数，不含 metadata.csv（684,079 B）、manifest（77,374 B）、
  临床 CSV（23,335 B）、sample.tcia（401 B）等非 DICOM 文件；
- 目录计数要按布局选层级：`full/<PatientID>/<Modality>/<SeriesUID>/` 下
  患者是 depth 1、series 是 depth 3；IDC 原始布局（`患者/study/series/文件`）则是
  depth 1 / depth 4，两种布局不能套同一组参数；
- `find ... -name A -o -name B` 与 `-print` / `-delete` 等动作组合时必须加括号
  `\( ... \)`，否则动作只作用于最后一个条件。

### 校验和（D11）

- 算法：SHA-256；
- 抽样规则：对 `full/` 下 52,073 个 DICOM 按路径排序后每 2,600 个取 1 个，共 21 个；
- 生成位置：190 生成，保留相对路径 `full/...`，见 `logs/raw_dicom.sha256`；
- 双机对拍：t12ub 上 `cd ~/tcia && sha256sum -c logs/raw_dicom.sha256`，
  21/21 全部 OK，说明传输后的文件与源端逐字节一致；
- 临床表与系列索引：见 `logs/clinical.sha256`；临床 CSV 两机哈希一致
  （`132f72b58b9660bf5e6b24b9817b335f1896360bc253e1f2034a3ffee593e6fd`），
  metadata.csv 为 `f8c5459b8b103e713e2d9b53a86ba7bea31b008457e6fefbc14331d5d0b2d0db`；
- 未做全量逐文件哈希：52,073 个小文件随机读远慢于抽样；完整性由
  「计数 + DICOM 字节数 + 抽样哈希」三者共同支撑。

### DICOM 头部核验（pydicom）

190 的系统 Python 没有 pydicom；已在 `~/venvs/tcia` 建独立 venv 并安装 pydicom，
不改系统环境。

| 对象 | SOPClassUID | 数量 | 关键信息 |
|---|---|---|---|
| CT | `1.2.840.10008.5.1.4.1.1.2` | 134 files | CT Image Storage |
| SEG | `1.2.840.10008.5.1.4.1.1.66.4` | 1 file / 536 frames | 4 segments × 134 slices |
| RTSTRUCT | `1.2.840.10008.5.1.4.1.1.481.3` | 1 file | GTV-1、Spinal-Cord、Lung-Left、Lung-Right |

引用关系：

```text
RTSTRUCT -> CT: True
SEG -> CT: True
```

说明：

- SEG 的 536 frames 不是 536 层 CT，而是 **4 个 segment × 134 层**；
- SEG 的 `SegmentLabel` 中有两个 `Lung`，无法只靠标签区分左右；
  D12/D13 解析时用 `SegmentNumber` / `SegmentIdentificationSequence`，
  或直接用 RTSTRUCT 的 `ROIName`（`Lung-Left` / `Lung-Right`）；
- `GTV-1` 在 RTSTRUCT 和 SEG 中都能找到，D12 的掩膜解析可行；
  但该结论只对标准命名病例成立，LUNG1-128 的 ROI 名为 `gtv-pre-op`，见「已知缺陷」。

## 磁盘估算

以 LUNG1-001 为样本做外推（`du -sb` 为精确字节数，`du -sh` 为便于阅读的约数）：

| 项目 | 数值 |
|---|---:|
| 单例（LUNG1-001） | 89,922,837 bytes（`du -sh` 约 87 MiB） |
| 单例 series 数 | 3（CT + SEG + RTSTRUCT） |
| 全量 series 数 | 1,265 |
| 平均 series/例 | 1,265 ÷ 422 ≈ 3.0 |
| 按 422 例外推 | 37,947,437,214 bytes |
| 外推（十进制 GB） | **37.95 GB** |
| 外推（GiB） | **35.34 GiB** |
| 官方标注 | 35.78 GB |

结论：

- 按十进制 GB 比较，外推值比官方 35.78 GB 高约 **6.1%**；
- 若官方数字按 GiB 理解，35.34 GiB 比 35.78 GiB 低约 **1.2%**；
- 两种口径都在 10% 以内，属于**同一量级**；
- LUNG1-001 有 3 个 series，和全量平均 3.0 series/例一致，单例外推有代表性。

空间规划：

```text
原始 DICOM        约 38 GB
掩膜/裁剪影像     ≤15 GB
特征与结果         ≤1 GB
合计              约 54 GB
建议预留           150 GB（更安心，不是最低需求）
```

190 当前家目录可用约 132 GB，容纳全量足够；`/data` 有 933 GB 可用，但需先取得写权限。

耗时参考：60 秒测试完成 2 个 series（约 145–200 MB），按 2.4–3.3 MB/s 估算，
全量 35.78 GB 约需 **3–4 小时**；网络好时可缩短到 1–2 小时。

## 传输方式

因为 190 不能直连 TCIA，且 mac 直连 190 的 `scp` 被对端关闭（`Connection closed by 192.168.1.190 port 22`），
实际采用局域网 HTTP 中转：

1. mac 在 `~/tcia-share` 启动 `python3 -m http.server 8000 --bind 0.0.0.0`；
2. mac 从 TCIA API 下载 3 个 series 并打包为 `LUNG1-001.zip`；
3. 190 通过 `curl` 从 mac 的 HTTP 服务拉取 zip；
4. 190 解压到 `~/tcia/raw/dicom/`。

该方式只用于当前网络环境；如果 190 后续能直连 TCIA，应优先恢复 API 直连或代理。

## 已知缺陷

- **LUNG1-014 / LUNG1-021 / LUNG1-085**：CT 缺层；缺失层不穿过 GTV，但做全肺或插值相关分析时需要注意；
- **LUNG1-128**：术后病例；RTSTRUCT 的 ROI 为 `gtv-pre-op`、`gtv-pre-operat`
  （术前 GTV，命名不是 `GTV-1`），且没有 SEG；
- **SEG 共 421 例**：比 CT / RTSTRUCT 的 422 少 1 例；缺的正是 **LUNG1-128**，
  与官方 1,265 series 总数一致，不是下载缺失；
- **ROI 命名不统一**（422 例全量扫描）：`GTV-1` 421 例、`gtv-2` 218 例、
  `gtv-3` 23 例，另有 `gtv-4/5/6/7`、`gtv_4r`、`gtv_2l` 等，
  存在大小写与 `-` / `_` 混用；所有病例都至少有一个含 `gtv` 的 ROI。
  D12 匹配需归一化（小写 + 去掉 `-`、`_`、空格），主靶区优先 `gtv1`、
  退回 `gtvpreop`，不得把 `gtv-2..7` 并入同一个靶区；
- **TNM 编码**：`clinical.T.Stage` 的 `5`、`Clinical.N.Stage` 的 `4`、`Clinical.M.Stage` 的 `3` 含义已丢失；
- **age**：部分病例为 `NA`（如 LUNG1-056、LUNG1-149）；
- **Histology**：部分病例为 `NA`。

## 不进入 Git

- `/home/jiaqiwang/tcia/`（190）与 `/home/jqw/tcia/`、`/home/jqw/.data/nsclc-radiomics/`（t12ub）
  下的原始 DICOM、临床 CSV、manifest、zip、日志均不入库；
- 仓库通过 `.gitignore` 忽略 `data/clinical/*`（保留 `.gitkeep`）、`data/manifests/`、`data/raw/`、`*.tcia`、`*.dcm`、`*.zip`；
- 仓库只保留本 README 和目录占位文件。
