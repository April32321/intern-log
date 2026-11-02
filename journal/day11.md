---
day: 11
date: 2026-11-02
theme: 全量数据核验、目录重排与传输
gate: D11
---

# Day 11｜全量数据核验、重排与传输

## 今日目标

- 确认全量 NSCLC-Radiomics v4 到底在哪台机器、是否完整；
- 把数据整理成后续脚本约定的目录结构；
- 打通 t12ub → 190 的免密传输，并完成全量搬迁；
- 留下可复核的计数、字节数和命令记录。

## 结论先行

1. **全量数据原本只在 t12ub**：开工时 mac 和 190 都没有，190 的 `~/tcia/full` 是空目录。
   传输完成后两端内容一致（各 422 患者 / 1,265 series / 52,073 DICOM / 35,775,589,886 B），
   详见下文「190 端验收（已通过）」。
2. t12ub 上的数据完整：**422 患者 / 1,265 series / 52,073 DICOM**，
   DICOM 字节数 **35,775,589,886**（约 35.78 GB），与官方 v4 完全一致。
3. 原始数据是 IDC 风格布局，已用 `pydicom` + 硬链接重排为
   `PatientID/Modality/SeriesInstanceUID/`，不额外占空间。
4. t12ub → 190 的 SSH 公钥已配置，rsync 已传完 35.79 GB（`speedup is 1.00`）；
   190 端验收 **52,073 / 422 / 1,265 / 35,775,589,886 B**，与 t12ub 完全一致。

## 数据核验（t12ub）

### 目录与计数

数据根目录：`/home/jqw/.data/nsclc-radiomics/`

```text
/home/jqw/.data/nsclc-radiomics/
├── metadata/metadata.csv                 # 684,079 B，1,265 行数据
├── nsclc_radiomics/                      # IDC 布局
│   └── LUNG1-308/
│       └── 2008-10-25-58297/
│           └── 300-Segmentation-9.930/
│               └── 09c2479f-....dcm
├── NSCLC-Radiomics-Version-4-Oct-2020-NBIA-manifest.tcia   # 77,374 B
├── NSCLC-Radiomics-Lung1.clinical-version3-Oct-2019.csv    # 23,335 B
└── sample.tcia                            # 401 B
```

实测：

```bash
find ~/.data/nsclc-radiomics -name '*.dcm' | wc -l          # 52073
find ~/.data/nsclc-radiomics/nsclc_radiomics -mindepth 1 -maxdepth 1 -type d | wc -l   # 422
find ~/.data/nsclc-radiomics -mindepth 4 -maxdepth 4 -type d | wc -l                   # 1265
du -sb ~/.data/nsclc-radiomics                              # 35,776,375,075
```

注意：`du -sb` 的 35,776,375,075 包含 4 个非 DICOM 文件
（metadata.csv 684,079 + manifest 77,374 + clinical CSV 23,335 + sample.tcia 401 = 785,189）。
**只统计 DICOM 的字节数**才是用于比对的数字：

```bash
find ~/.data/nsclc-radiomics/nsclc_radiomics -name '*.dcm' -printf '%s\n' \
  | awk '{s+=$1} END {print s}'
# 35775589886
```

### metadata.csv 校验

```bash
python3 - <<'PY'
import csv, collections
p = "/home/jqw/.data/nsclc-radiomics/metadata/metadata.csv"
rows = list(csv.DictReader(open(p, newline="", encoding="utf-8-sig")))
print("rows:", len(rows))
print("completion:", collections.Counter(r["completion_status"] for r in rows))
print("unique series:", len({r["SeriesInstanceUID"] for r in rows}))
print("unique patients:", len({r["PatientID"] for r in rows}))
print("modality:", collections.Counter(r["Modality"] for r in rows))
PY
```

输出：

```text
rows: 1265
completion: Counter({'success': 1265})
unique series: 1265
unique patients: 422
modality: Counter({'CT': 422, 'RTSTRUCT': 422, 'SEG': 421})
```

SEG 421 比 CT/RTSTRUCT 少 1 例，与官方总数 1,265 一致，不是下载缺失；
结合已知缺陷（LUNG1-128 术后无 GTV-1）记录，D12 解析时按患者逐个处理。

### DICOM 真实性抽查

```bash
f=$(find ~/.data/nsclc-radiomics -name '*.dcm' | head -1)
file "$f"                     # DICOM medical imaging data
od -An -c -j128 -N4 "$f"      # D   I   C   M
```

## 目录重排

### 问题

t12ub 原始数据是 IDC 的 descriptive 布局：

```text
nsclc_radiomics/<PatientID>/<StudyDate-StudyID>/<SeriesNumber-Description>/<SOPInstanceUID>.dcm
```

而 `code/00_download.py` 和 190 的约定是：

```text
full/<PatientID>/<Modality>/<SeriesInstanceUID>/*.dcm
```

不重排的话，后续按 `CT/SEG/RTSTRUCT` 找目录会失败。

### 做法

- 在 t12ub 建独立 venv：`~/venvs/tcia`，安装 `pydicom 3.0.2`；
- 脚本 `~/tcia/reorg.py`（SHA-256 `0a0b34d6cfce300a105a7352faba4016170f34288f5c15f58c5ab2ee10892ad5`）：
  遍历 `*.dcm`，只读头（`stop_before_pixels=True`），取
  `PatientID` / `Modality` / `SeriesInstanceUID`，用 `os.link()` 建硬链接；
- 源目录保持不动，`~/tcia/full` 与源指向同一 inode，不额外占盘。

```bash
~/venvs/tcia/bin/python ~/tcia/reorg.py
```

首次可见输出：

```text
linked 5000
linked 10000
linked 15000
done: linked=16500 errors=0
```

`linked=16500` 小于总数，是因为此前已有一轮部分执行，目标文件已存在，
被 `if dest.exists(): continue` 静默跳过；总数为 52,073，说明没有漏文件。

### 重排验收

```bash
find ~/tcia/full -name '*.dcm' | wc -l                       # 52073
find ~/tcia/full -mindepth 1 -maxdepth 1 -type d | wc -l     # 422
find ~/tcia/full -mindepth 3 -maxdepth 3 -type d | wc -l     # 1265
find ~/tcia/full -mindepth 3 -maxdepth 3 -type d -empty | wc -l   # 0
find ~/tcia/full -type f ! -name '*.dcm' | wc -l            # 0
du -sh ~/tcia/full                                           # 34G

for m in CT SEG RTSTRUCT; do
  printf '%-10s ' "$m"
  find ~/tcia/full -mindepth 2 -maxdepth 2 -type d -name "$m" | wc -l
done
# CT 422 / SEG 421 / RTSTRUCT 422

stat -c '%h %n' "$(find ~/tcia/full -name '*.dcm' | head -1)"
# 2 ...   → 硬链接成立（源 + 目标）
```

DICOM 字节数在重排前后一致：

```text
重排前 nsclc_radiomics : 35,775,589,886
重排后 tcia/full       : 35,775,589,886
```

## t12ub → 190 免密配置

### 过程

1. t12ub 连 190（`192.168.1.190:3225`）首次报 `Host key verification failed`：
   `known_hosts` 无记录，`BatchMode=yes` 又不允许交互确认。用
   `ssh-keyscan -p 3225 192.168.1.190 >> ~/.ssh/known_hosts` 解决。
2. 190 关闭密码登录，t12ub 报 `Permission denied (publickey)`。
3. 使用 t12ub 已有 RSA 公钥 `~/.ssh/id_rsa.pub`（4096 位，注释 `jqw@ubuntu`），
   追加到 190 的 `~/.ssh/authorized_keys`。
4. 手动粘贴时把文档里的占位符 `AAAAB3...DXgw==` 当成公钥写入，产生一条 34 字节的
   无效行；用 `awk 'length($0) > 50'` 清理后只剩两条有效 key。
5. 190 权限：家目录 `755`、`.ssh` `700`、`authorized_keys` `600`。

### 验证

```bash
ssh -p 3225 -o BatchMode=yes jiaqiwang@192.168.1.190 'hostname; rsync --version | head -1'
```

```text
pvmed-190
rsync  version 3.2.7  protocol version 31
```

t12ub 公钥指纹：

```text
4096 SHA256:VjrBXENgZa7SLgWbiWNJuntKmfu3NFlA+qzpEFyrE4A jqw@ubuntu (RSA)
```

## 传输

```bash
tmux new -s push190
rsync -avhP -e 'ssh -p 3225' ~/tcia/full/ jiaqiwang@192.168.1.190:~/tcia/full/
```

- 源路径末尾 `/`：复制 `full/` 的内容到对端 `~/tcia/full/`；
- 52,073 个小文件，rsync 先扫描再传输，启动后短暂停顿属正常；
- 中断后重跑同一条命令即可按文件续传；不要加 `--delete`。

最终输出：

```text
sent 35.79G bytes  received 1.01M bytes  3.63M bytes/sec
total size is 35.78G  speedup is 1.00
```

- 实测约 3.5 MB/s，全程约 2 小时 45 分（10:50 前后开始，13:34 完成）；
- `speedup is 1.00`：没有重复传输，目标端文件集合与源一致；
- 传输是 t12ub → 190 直连，不经过 mac，mac 睡眠或断网不影响任务。

### 190 端验收（已通过）

```bash
find ~/tcia/full -name '*.dcm' | wc -l                       # 52073
find ~/tcia/full -mindepth 1 -maxdepth 1 -type d | wc -l     # 422
find ~/tcia/full -mindepth 3 -maxdepth 3 -type d | wc -l     # 1265
find ~/tcia/full -name '*.dcm' -printf '%s\n' \
  | awk '{s+=$1} END {print s}'                              # 35775589886
du -sh ~/tcia/full                                           # 34G
```

| 项 | 190 实测 | t12ub / 期望 |
|---|---:|---:|
| DICOM | 52,073 | 52,073 |
| 患者目录 | 422 | 422 |
| series 目录 | 1,265 | 1,265 |
| DICOM 字节 | 35,775,589,886 | 35,775,589,886 |
| `du -sh` | 34G | 34G |

DICOM 头抽查（190，pydicom venv）：

```text
/home/jiaqiwang/tcia/full/LUNG1-001/CT/1.3.6.1.4.1.32722.99.99.29899.../<uid>.dcm
LUNG1-001 CT 1.3.6.1.4.1.32722.99.99.29899...
```

metadata.csv 同步后 190 上为 `1266` 行（1 表头 + 1,265 数据），与 t12ub 一致。

注意：比对用 **DICOM 字节数 35,775,589,886**，不要用 `du -sb ~/tcia/full` 和
源根目录的 `du -sb` 直接比——源根目录还包含 metadata.csv 等 4 个非 DICOM 文件。

### 系列级索引同步

```bash
ssh -p 3225 jiaqiwang@192.168.1.190 'mkdir -p ~/tcia/metadata'

rsync -avhP -e 'ssh -p 3225' \
  ~/.data/nsclc-radiomics/metadata/metadata.csv \
  jiaqiwang@192.168.1.190:~/tcia/metadata/
```

结果：`metadata.csv` 684.08K，`sent 684.34K bytes`，`speedup is 1.00`；
190 上为 `/home/jiaqiwang/tcia/metadata/metadata.csv`（1,266 行：1 表头 + 1,265 数据）。

注意：rsync 默认走 SSH 22 端口，必须显式带 `-e 'ssh -p 3225'`；
漏掉会报 `ssh: connect to host 192.168.1.190 port 22: Connection refused`。

## 卡点与报错

### 卡点 1：在 190 上执行 `ssh pvmed190`

- 报错：`ssh: Could not resolve hostname pvmed190: Temporary failure in name resolution`
- 根因：`Host pvmed190` 别名只存在于 mac 的 `~/.ssh/config`，190 上没有。
- 处理：已经在 190 上就直接跑本地命令；需要远程时用 `ssh -p 3225 jiaqiwang@192.168.1.190`。

### 卡点 2：`Host key verification failed`

- 根因：t12ub 的 `known_hosts` 没有 190 的记录，`BatchMode` 禁止交互确认。
- 处理：`ssh-keyscan -p 3225 192.168.1.190 >> ~/.ssh/known_hosts`。
- 结论：这条报错说明 TCP 和 SSH 服务是通的，只是客户端信任库没记录。

### 卡点 3：`Permission denied (publickey)`

- 根因：190 禁用密码登录，t12ub 的公钥未加入 `authorized_keys`。
- 处理：把 t12ub 的 `id_rsa.pub` 追加到 190 的 `authorized_keys`，并保持 `700/600` 权限。

### 卡点 4：把占位符当公钥粘贴

- 现象：`authorized_keys` 出现一行长度 34 的 `ssh-rsa AAAAB3...DXgw== jqw@ubuntu`。
- 根因：手动复制了文档中的省略写法，没有使用 `cat id_rsa.pub` 的完整输出。
- 处理：`awk 'length($0) > 50'` 过滤短行；以后统一用命令直接追加，不手抄。

### 卡点 5：`reorg.py` 的 `linked=16500`

- 现象：脚本正常 `done`、`errors=0`，但 linked 只有 16,500。
- 根因：此前已有一轮部分执行，目标文件存在被跳过。
- 验证：总数 52,073、series 1,265、患者 422 全部对上；`stat` 显示硬链接数为 2。
- 教训：脚本的 `linked` 是"本次新建"数量，不是"总量"；验收要以目录计数为准。

### 卡点 6：把 422 当成患者数/ series 数

- 现象：在 t12ub 上 `-mindepth 3 -maxdepth 3` 数出 422，被误认为 series 数。
- 根因：IDC 布局是 `患者/study/series/文件`，depth 3 是 study 层。
- 处理：患者用 depth 1（在 `nsclc_radiomics` 下），series 用 depth 4。
- 结论：数目录前先确认层级，不要套用 190 布局的 depth 习惯。

## Kilo 使用记录

- 让 Kilo 判断"全量已下载"到底在哪台机器：本机 `~/tcia`、`data/raw`、`tcia-share`
  都没有全量，t12ub 的 `~/.data/nsclc-radiomics` 才有；避免了在 mac 上重复下载 35 GB。
- 让 Kilo 根据 IDC 布局和 190 约定生成重排脚本，并解释硬链接不占额外空间。
- 抓错 1：曾把 depth 3 的 422 当成 series 数，Kilo 指出那是 study 层，series 在 depth 4。
- 抓错 2：曾建议用 `du -sb` 直接比对 t12ub 的 `full/` 和源根目录，
  Kilo 核实源根目录多出 785,189 B 的非 DICOM 文件，改为只统计 DICOM 字节。

## 今日结论

1. 全量数据无需重新下载：t12ub 上 2026-10-14 的下载已完整，
   52,073 个 DICOM、1,265 个 series、422 个患者，DICOM 字节 35,775,589,886；
   D11 已通过 rsync 在 190 的 `~/tcia/full` 建立同内容副本，两端计数与字节数一致。
2. IDC 布局与 190 约定不一致，已用 pydicom + 硬链接重排，源数据保持原样，
   磁盘占用不增加。
3. t12ub → 190 的免密已打通；rsync 传输完成，耗时约 2 小时 45 分，
   平均 3.63 MB/s，`sent 35.79G bytes`、`speedup is 1.00`。
4. 190 端验收通过：52,073 DICOM、422 患者、1,265 series、35,775,589,886 B，
   与 t12ub 完全一致。
5. 验收口径已修正：用 DICOM 数量和 DICOM 字节数比对，不用包含 metadata 的目录总量。
6. `metadata.csv` 已同步到 190 的 `~/tcia/metadata/`，作为系列级索引；
   t12ub 源目录暂不清理，等 D12 在 190 上跑通后再决定。

## 明日 3 件事

1. D12：用 pydicom 解析 CT/SEG/RTSTRUCT 元数据，与临床表按 PatientID 合并；
2. 用 `metadata.csv` 做 series 级索引，确认 SEG 421 例中缺哪一例；
3. 从 190 拉取 1–2 个患者到 mac，验证 Slicer + SlicerRT 的 CT/RTSTRUCT/SEG 显示。
