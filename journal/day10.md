---
day: 10
date: 2026-10-30
theme: 数据获取方案 + 小样本试下载
gate: G2
---

# Day 10｜数据获取方案 + 小样本试下载（G2）

## 今日目标

- 搞清楚数据**从哪儿下、怎么下、下多少、怎么验**；
- 选定下载路线并写清理由；
- 用 LUNG1-001 跑通 CT + RTSTRUCT + SEG 的小样本流程；
- 完成 G2 门禁材料：`data/README.md`、环境可重建、容器内 Kilo 冒烟、tmux 下载。

## 今日完成

| 计划项 | 状态 | 证据 |
|---|---|---|
| 数据身份、DOI、许可、规模 | ✅ | 写入 `data/README.md` |
| 临床 CSV | ✅ | 423 条记录（1 表头 + 422 数据），10 列，422 个唯一 PatientID |
| 全量 manifest | ✅ | 1,265 个唯一 series UID，1,271 行 |
| 下载路线选择 | ✅ | 路线 B：TCIA REST API；理由见 `data/README.md` |
| 小样本 LUNG1-001 | ✅ | 3 series，136 个 DICOM + 3 个 LICENSE，约 87 MB |
| DICOM 头部核验 | ✅ | CT/SEG/RTSTRUCT 的 SOPClassUID 正确；`RTSTRUCT -> CT`、`SEG -> CT` 均为 `True`；SEG 536 frames = 4 × 134 |
| 下载脚本 `--full/--resume/--retry` | ✅ | `code/00_download.py`；`--limit 1` 首跑 `ok=1`，重跑 `--resume` 输出 `[skip]`，`ok=0 skip=1` |
| 60 秒 `--full --resume` 断点验收 | ✅ | 60 秒完成 2 个 series；重跑同命令输出 `[skip]` ×2，未从 0 开始 |
| 磁盘与人日估算 | ✅ | 单例 89,922,837 B；×422 = 37.95 GB / 35.34 GiB，与官方 35.78 GB 同量级 |
| `data/README.md` | ✅ | 数据身份、路线、路径、校验、已知缺陷、不入 Git |
| `environment.yml` 删环境重建 | ✅ | D9 已完成：`logs/day09-rebuild.log` + `journal/day09.md` 验收对照 |
| 容器内 `kilo --version` / `KILO_OK` | ✅ | D8：`kilo-version.txt` 7.8.18、`smoke-test.txt` KILO_OK、`logs/day08-kilo-version.txt` |
| `docker build` 成功 | ✅ | D8：`journal/day08.md:31` + `logs/day08-intern-base.txt`（`intern-base:0.1`） |
| tmux 内运行下载 | ✅ | TDR 续传循环在 `tmux` 会话 `dl` 中运行；小样本另走 HTTP 中转 |
| 当日 commit | ⬜ 待提交 | `code/00_download.py` 与本次文档更新 |

## 数据身份

| 项 | 值 |
|---|---|
| 数据集 | TCIA NSCLC-Radiomics（Lung1）version 4，2020-10-22 |
| 规模 | 422 subjects / 422 studies / 1,265 series / 52,073 images / 35.78 GB |
| 模态 | CT、RTSTRUCT、SEG |
| 数据 DOI | `10.7937/K9/TCIA.2015.PF0M9REI` |
| 论文 | Aerts et al. 2014, *Nature Communications*, DOI `10.1038/ncomms5006` |
| 许可 | CC BY-NC 3.0（非商业 + 引用 DOI） |

已知缺陷：LUNG1-014/021/085 缺层；LUNG1-128 无 GTV-1（术后）；TNM 的 5/4/3 编码含义已丢失。

## 关键命令

### 临床 CSV 校验

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
# 423 / 422 / 10 / 422
```

`wc -l` 得到 422，是因为文件末行没有换行符；Python `csv` 读取为 423 条记录。

### manifest 校验

```bash
grep -c '^1\.' ~/tcia/manifests/NSCLC-Radiomics-v4.tcia
# 1265

grep '^1\.' ~/tcia/manifests/NSCLC-Radiomics-v4.tcia | sort -u | wc -l
# 1265

wc -l ~/tcia/manifests/NSCLC-Radiomics-v4.tcia
# 1271（6 header + 1265 UID）
```

### 小样本验收

```bash
find ~/tcia/raw/dicom/LUNG1-001 -type f -name '*.dcm' | wc -l
# 136

find ~/tcia/raw/dicom/LUNG1-001 -type f -name 'LICENSE' | wc -l
# 3

du -sh ~/tcia/raw/dicom/LUNG1-001
# 87M
```

目录结构：

```text
~/tcia/raw/dicom/LUNG1-001/CT/<SeriesUID>/*.dcm + LICENSE
~/tcia/raw/dicom/LUNG1-001/SEG/<SeriesUID>/*.dcm + LICENSE
~/tcia/raw/dicom/LUNG1-001/RTSTRUCT/<SeriesUID>/*.dcm + LICENSE
```

### DICOM 头部核验

190 的系统 Python 没有 pydicom，改在 `~/venvs/tcia` 里安装，不使用 sudo、不改系统环境：

```bash
python3 -m venv ~/venvs/tcia
~/venvs/tcia/bin/pip install pydicom
~/venvs/tcia/bin/python -c "import pydicom; print(pydicom.__version__)"
```

用 pydicom 读三个 series 的头部，结果：

| 对象 | SOPClassUID | 数量 | 关键信息 |
|---|---|---|---|
| CT | `1.2.840.10008.5.1.4.1.1.2` | 134 files | CT Image Storage |
| SEG | `1.2.840.10008.5.1.4.1.1.66.4` | 1 file / 536 frames | 4 segments × 134 slices |
| RTSTRUCT | `1.2.840.10008.5.1.4.1.1.481.3` | 1 file | GTV-1、Spinal-Cord、Lung-Left、Lung-Right |

```text
RTSTRUCT -> CT: True
SEG -> CT: True
```

两个细节：

- SEG 的 536 frames 是 **4 个 segment × 134 层**，不是 536 层 CT；
- SEG 的 `SegmentLabel` 里有两个 `Lung` 同名，左右需用 `SegmentNumber` /
  `SegmentIdentificationSequence` 区分，或直接用 RTSTRUCT 的 `ROIName`
  （`Lung-Left` / `Lung-Right`）。

### 下载脚本

`code/00_download.py` 使用 TCIA REST API，仅依赖 Python 标准库：

```bash
# 只下 LUNG1-001
python3 code/00_download.py

# 全量 + 断点续传 + 每 series 重试 3 次
python3 code/00_download.py --full --resume --retry 3

# 只列清单，不下载
python3 code/00_download.py --full --dry-run
```

- 默认输出到仓库 `data/raw/`，日志/标记在 `logs/`；
- 在 190 上复现现有路径时显式指定：
  ```bash
  python3 code/00_download.py --full --resume --retry 3 \
    --out ~/tcia/full --log-dir ~/tcia/logs
  ```
- 每个 series 成功后写 `logs/done/<SeriesUID>`，标记里记录 `image_count`；
  `--resume` 会复核标记与目录内实际文件数，不一致就重新下载；
- 每个 series 失败重试 N 次，最终失败写入 `logs/download_failed.txt`；
- `logs/done/` 和 `logs/download_failed.txt` 已加入 `.gitignore`，不随代码提交。

断点逻辑实测（用 `--limit 1` 快速验证）：

```bash
python3 code/00_download.py --limit 1 \
  --out /tmp/tcia-smoke --log-dir /tmp/tcia-smoke-logs --retry 1
# ok=1 skip=0 fail=0

python3 code/00_download.py --limit 1 --resume \
  --out /tmp/tcia-smoke --log-dir /tmp/tcia-smoke-logs --retry 1
# [skip] LUNG1-001 CT ... ; ok=0 skip=1 fail=0
```

60 秒全量中断验收（mac 上执行）：

```bash
python3 code/00_download.py --full --resume --retry 3 \
  --out /tmp/tcia-60 --log-dir /tmp/tcia-60-logs
# 跑 60 秒后停止进程

# 用同一命令重跑
python3 code/00_download.py --full --resume --retry 3 \
  --out /tmp/tcia-60 --log-dir /tmp/tcia-60-logs
```

实测结果：第一次 60 秒完成 2 个 series（LUNG1-135、LUNG1-189），
第二次启动直接输出：

```text
[skip] LUNG1-135 CT ...
[skip] LUNG1-189 CT ...
```

说明 `--resume` 认的是完成标记，不是从 0 重下。

### 磁盘与人日估算

以 LUNG1-001 单例外推：

```text
单例 bytes: 89,922,837
× 422:      37,947,437,214 bytes
            = 37.95 GB (10^9)
            = 35.34 GiB (2^30)
官方:       35.78 GB
```

- 十进制口径高约 6.1%；若官方按 GiB 理解，则低约 1.2%；
- 两种口径都在 10% 以内，属于同一量级；
- LUNG1-001 是 3 个 series，全量平均 1,265 ÷ 422 ≈ 3.0 series/例，
  单例有代表性。

空间规划：

```text
原始 DICOM      约 38 GB
掩膜/裁剪影像   ≤15 GB
特征与结果       ≤1 GB
合计            约 54 GB
建议预留         150 GB（更安心）
```

190 家目录可用约 132 GB，放全量够用；`/data` 有 933 GB，但需要写权限。

人日估算：60 秒完成 2 个 series（约 145–200 MB），全量下载约 **3–4 小时**；
加校验与审计，D11 按 **0.5–1 人日** 规划。

## 卡点与报错

### 卡点 1：190 到 TCIA 的 TLS 握手超时

- **报错原文**：

  ```text
  curl: (28) SSL connection timeout
  HTTP 000
  ```

- **现象**：`www.cancerimagingarchive.net` 和 `services.cancerimagingarchive.net` 都超时；
  `openssl s_client -connect www.cancerimagingarchive.net:443` 20 秒无输出。
- **判断**：TCP 能到 443，但 TLS 握手完不成；不是证书、不是 curl 参数、不是文件大小。
- **根因**：190 所在网络到 TCIA 的出口被限制或链路不可达。
- **解决**：不在 190 上继续调网络；改为 mac 下载，再通过局域网 HTTP 中转。
- **下次怎么避免**：先测目标域名，不要假设“能上 GitHub 就能上 TCIA”。

### 卡点 2：mac 直连 190 的 scp 被关闭

- **报错原文**：

  ```text
  Connection closed by 192.168.1.190 port 22
  scp: Connection closed
  ```

- **判断**：190 的 22 端口不是可用的普通 SSH（可能是跳板/网页终端/只允许特定来源），不是密码问题。
- **解决**：mac 在 `~/tcia-share` 启动 `python3 -m http.server 8000 --bind 0.0.0.0`，
  190 用 `curl` 从 mac 拉文件。
- **证据**：190 上 `curl -v http://192.168.3.171:8000/` 返回目录列表，随后成功拉取 CSV、manifest 和 `LUNG1-001.zip`。

### 卡点 3：TDR 下载慢，但不能作为今天的阻塞项

- **现象**：新版 TDR Linux 包 156,016,593 字节，GitHub release 下载很慢；曾中断在 26 MB。
- **处理**：用 `curl -C -` 续传，并放进 tmux；截至写日志仍未完成。
- **结论**：TDR 只是 D11 的备用工具；190 既然不能访问 TCIA，TDR 装完也拉不到数据，G2 不依赖它。
- **下次怎么避免**：先确认数据源可达，再决定是否值得下下载器。

### 卡点 4：`wc -l` 422 与预期 423 不一致

- **现象**：`wc -l` 显示 422，但 Python `csv` 读取为 423 条记录。
- **根因**：文件最后一行没有换行符，`wc -l` 数的是换行符个数。
- **处理**：以 CSV 解析器的结果为准；不修改原始数据。
- **下次怎么避免**：行数校验统一用 Python `csv` 或 `awk 'END{print NR}'`，不要只看 `wc -l`。

### 卡点 5：小样本 `find` 是 139 个文件，不是 136

- **现象**：`find LUNG1-001 -type f | wc -l` = 139，但 DICOM 只有 136 个。
- **根因**：每个 series 目录下各有 1 个 `LICENSE`，共 3 个。
- **处理**：保留 LICENSE；验收时分别统计 `*.dcm` 和 `LICENSE`。
- **下次怎么避免**：先看 `find ... -not -name '*.dcm'`，再判断是否异常。

### 卡点 6：在 mac 上执行了 190 的命令

- **现象**：在 mac 的 `~/tcia-share` 里执行 `curl` 和 `unzip -d ~/tcia/raw/dicom/`，
  结果文件落在 mac 的 `/Users/wangjiaqi/tcia`，而不是 190。
- **根因**：`~` 在两台机器上指向不同家目录；提示符 `wangjiaqi@AprilMacBook-Pro` 与
  `jiaqiwang@pvmed-190` 才是判断依据。
- **处理**：传输/解压命令在 190 上执行；mac 只负责 HTTP 服务和源文件。
- **下次怎么避免**：执行前先看提示符和 `hostname`；路径含 `~` 时尤其要确认机器。

### 卡点 7：`find /data` 扫描过慢

- **现象**：`find "$HOME" /data -maxdepth 5 ...` 长时间无输出，只能 `Ctrl+C`。
- **根因**：`/data` 是 5.5T 大盘，即使限深也会遍历大量目录。
- **处理**：直接看已知目录 `~/tcia/clinical`、`~/tcia/manifests`，不要全盘扫。
- **下次怎么避免**：找文件先限定到项目目录，再扩大范围。

### 卡点 8：mac Python 3.14 的 SSL 证书

- **报错原文**：

  ```text
  ERROR: getSeries failed: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED]
  certificate verify failed: unable to get local issuer certificate>
  ```

- **根因**：Python.org 的 mac 安装包不会自动把系统 CA 装进 Python 的信任库，
  `urllib` 默认找不到签发链。
- **验证**：`python3 -c "import certifi; print(certifi.where())"` 能看到 `cacert.pem`；
  `ssl.get_default_verify_paths()` 的默认 cafile 为空。
- **解决**：脚本里优先使用 `certifi.where()` 建 SSLContext，
  没有 certifi 时回退到 `/etc/ssl/certs/ca-certificates.crt`（Linux）
  或 `/etc/ssl/cert.pem`（macOS）。
- **下次怎么避免**：在新 Python 环境里先跑一次 HTTPS 请求；
  不要第一时间用 `verify=False` 绕过证书校验。

## Kilo 使用记录

- 让 Kilo 对比 A/B/C 三条下载路线的官方文档差异，并给出链接；
- 让 Kilo 写下载脚本的重试与断点逻辑，审代码后才运行；
- **抓错 1**：Kilo 建议优先用 TDR 下全量；核实 190 到 TCIA 的 TLS 出口不通，
  TDR 装完也无法拉取影像，改为 mac 下载 + 局域网 HTTP 中转。
- **抓错 2**：Kilo 预期 CSV `wc -l` 为 423；本机实际为 422，
  核实是末行无换行符，Python `csv` 读取仍为 423 条记录，不是缺数据。

## G2 验收对照

- [x] 临床 CSV 是 422 行数据 + 表头，字段能解释
- [x] `data/README.md` 含路线选择理由与校验方案
- [x] 3 个 series 已落地，`du -sh` 数字合理（87 MB）
- [x] DICOM 头部可读，CT/SEG/RTSTRUCT 类型正确，掩膜引用 CT
- [x] 下载脚本支持 `--full` / `--resume` / `--retry`，断点逻辑已实测
- [x] `environment.yml` 删环境后可重建（D9：`logs/day09-rebuild.log`）
- [x] Ubuntu 容器内 `kilo --version` 与 `KILO_OK` 有记录（D8：`kilo-version.txt`、`smoke-test.txt`）
- [x] `tmux` 内能跑下载脚本（TDR 续传循环；小样本走 HTTP 中转）
- [x] `docker build` 成功（D8：`journal/day08.md:31`、`logs/day08-intern-base.txt`）

## 今日结论

1. **190 到 TCIA 的 TLS 出口不可用**，直连 API 和 TDR 都不可行；
   mac 下载 + 局域网 HTTP 是当前可靠路径。
2. **小样本 3 个 series 已落地**，G2 的数据入口验证完成：
   CT 134 张、SEG 1 个、RTSTRUCT 1 个，共 136 DICOM + 3 LICENSE，87 MB。
3. **DICOM 对象类型与引用关系正确**：CT/SEG/RTSTRUCT 的 SOPClassUID 分别为
   `...1.1.2`、`...1.1.66.4`、`...1.1.481.3`；`RTSTRUCT -> CT`、`SEG -> CT` 均为 `True`。
   SEG 536 frames = 4 segments × 134 slices，两个 `Lung` 标签需用
   `SegmentNumber` 或 RTSTRUCT 的 `ROIName` 区分左右。
4. **下载脚本已落盘**：`code/00_download.py` 支持 `--full` / `--resume` / `--retry`；
   用 `--limit 1` 实测首跑 `ok=1`、重跑 `skip=1`；60 秒全量中断测试完成 2 个 series，
   重跑输出 `[skip]` ×2，断点逻辑成立。
5. **磁盘估算与官方一致**：单例 89,922,837 B × 422 = 37.95 GB / 35.34 GiB，
   与官方 35.78 GB 同量级（偏差 <10%）；全量约需 3–4 小时。
6. **CSV 是 423 条记录、422 个唯一 PatientID**；`wc -l` 的 422 是换行符计数问题。
7. **manifest 是 1,265 个唯一 series UID**，与官方 v4 规模一致。
8. **D11 的全量下载必须先解决 190 出网**，否则 35.78 GB 只能走 mac 中转或 IDC/GCS。

## 明日 3 件事

1. D11 全量下载方案定稿：代理/VPN、mac 中转、或 IDC/GCS（记录来源差异）；
2. 全量校验脚本：422 患者 / 1,265 series / 52,073 文件 / 35.78 GB；
3. 准备 D12 的 DICOM 元数据解析与临床表合并。
