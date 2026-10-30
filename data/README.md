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

## 实际位置（190）

| 内容 | 路径 |
|---|---|
| 临床 CSV | `/home/jiaqiwang/tcia/clinical/NSCLC-Radiomics-Lung1.clinical-version3-Oct-2019.csv` |
| 全量 manifest | `/home/jiaqiwang/tcia/manifests/NSCLC-Radiomics-v4.tcia` |
| 小样本 DICOM | `/home/jiaqiwang/tcia/raw/dicom/LUNG1-001/{CT,SEG,RTSTRUCT}/<SeriesUID>/` |
| 全量数据（D11） | `/home/jiaqiwang/tcia/full/` |
| 日志 | `/home/jiaqiwang/tcia/logs/` |

这些路径在 190 上，不在 git 仓库内；仓库只保留本说明文件。

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

| Modality | ImageCount | 说明 |
|---|---:|---|
| CT | 134 | 术前 CT |
| SEG | 1 | GTV-1 分割对象 |
| RTSTRUCT | 1 | 放疗结构 |

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
- **LUNG1-128**：术后病例，无 GTV-1，仅保留 CT；
- **TNM 编码**：`clinical.T.Stage` 的 `5`、`Clinical.N.Stage` 的 `4`、`Clinical.M.Stage` 的 `3` 含义已丢失；
- **age**：部分病例为 `NA`（如 LUNG1-056、LUNG1-149）；
- **Histology**：部分病例为 `NA`。

## 不进入 Git

- `/home/jiaqiwang/tcia/` 下的原始 DICOM、临床 CSV、manifest、zip、日志均不入库；
- 仓库通过 `.gitignore` 忽略 `data/clinical/*`（保留 `.gitkeep`）、`data/manifests/`、`data/raw/`、`*.tcia`、`*.dcm`、`*.zip`；
- 仓库只保留本 README 和目录占位文件。
