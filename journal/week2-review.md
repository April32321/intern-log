---
week: 2
days: D6–D10
dates: 2026-10-27 ~ 2026-10-30
gate: G2
written: 2026-11-06（D15 补交，晚于 W3）
---

# 第二周复盘（D6–D10）：环境与数据入口

> 范围：Kilo 安装与工作流、Docker 实操、Conda 可重建环境、TCIA 数据获取与小样本验证。
> 原则：只写能拿出证据的结论；没有证据的写「未验证」，不估算、不美化。

## 补写说明

本文件在 D15（2026-11-06）补写，此时 `week3-review.md` 已先完成。为避免用后见之明改写 W2，
以下判断只引用 D6–D10 的日志、提交和 `env/`、`data/`、`logs/` 里的原始输出；涉及 D11 的事实单独标「D11 补记」。
两条改进按 W4 仍可执行的标准写。

## 一句话结论

**环境和数据入口都跑通了，G2 可以过；但日程与记录纪律仍不合格。** 5 天产出 1,417 行日志、
45 条提交、32 条卡点记录，`kilo-box`、`intern-base`、`radiomics` 三个环境都能复核，G2 九项都有对应材料（其中 tmux 一项是替代证据）；
但 D6、D7 的工作都压在 10-27 一个日历日，D8 跨 10-27–10-28 完成、日期按完成日记成 10-28；D9 打卡次日补，
D10 的「当日 commit」至今仍标「待提交」，W2 末条提交 `e59336a` 也没推。
Kilo 抓错只记了 3 条，W1+W2 累计 8 条，低于 D10 的 ≥10 目标。
本复盘本身拖到 D15 才补，说明「周复盘」还没有变成固定收尾动作。

## 本周产出清点

| 项目 | 实际产出 | 证据 |
|---|---|---|
| 工作日志 | 5 篇（day06–day10），合计 1,417 行 | `wc -l journal/day0{6,7,8,9}.md journal/day10.md` |
| 本复盘 | `journal/week2-review.md` | 本文件（D15 补交） |
| 打卡表 | D6–D10 五行已填；D8 日期 10-27→10-28，D9 行 10-30 补 | `journal/INDEX.md`；`8485078`、`13b91ac`、`854fb30` |
| 知识笔记 | `kilo.md` 166 行、`docker.md` 280 行、`Conda.md` 83 行、`SSH.md` 231 行，合计 760 行 | `wc -l notes/...`；W1 末 `kilo.md` 18 行、`SSH.md` 14 行 |
| Kilo 验收 | 7.8.18；`deepseek/deepseek-flash`；`KILO_OK`、`TOOL_OK`；agents 权限与 tmux 状态有原始抓屏 | `kilo-version.txt`、`smoke-test.txt`、`logs/day06-tmux-*.txt` |
| Docker | Docker Desktop 4.97.0；`hello-world` 通过；`kilo-box:0.1` 1.01 GB；`intern-base:0.1` 310 MB；非 root `dev` | `journal/day08.md`、`logs/day08-*.txt` |
| Conda | `radiomics` Python 3.10.22；311 conda-forge + 6 pypi，0 defaults；linux-64 与 osx-arm64 均重建成功 | `journal/day09.md`、`logs/day09-rebuild.log` |
| 锁定文件 | `environment.yml` 18 行、`conda-explicit.txt` 322 行、`pip-freeze.txt` 154 行，附 `README.md` 与 `rebuild.sh` | `env/` |
| 数据入口 | 临床表 423 条记录 / 422 个唯一 PatientID；manifest 1,265 个唯一 series UID | `data/clinical/NSCLC-Radiomics-Lung1.clinical-version3-Oct-2019.csv`、`journal/day10.md` |
| 小样本 | LUNG1-001：136 个 DICOM + 3 个 LICENSE，87 MB；CT/SEG/RTSTRUCT 类型与引用正确 | `journal/day10.md` |
| 下载脚本 | `code/00_download.py` 334 行，支持 `--full/--resume/--retry`；60 秒中断后重跑 `[skip]`×2 | 脚本 + `journal/day10.md` |
| 数据说明 | `data/README.md` 342 行，含路线理由、校验方案、已知缺陷；D11 追加实际落地说明 | `data/README.md` |
| 提交 | W2 范围 45 条，其中 32 条带 `day06`–`day10` 前缀 | `git rev-list --count 8d38b66^..e59336a`；`git log --grep` |
| 凭据与数据入库 | 0 个 `.dcm`、0 个 `data/raw/`、0 个 Key 文件被跟踪 | `git ls-files` 复核 |

补充：W2 末条 `e59336a` 不在 `origin/main`，`git rev-list --count origin/main..e59336a` = 1；
其余 44 条已推送。

## 五个能力点自评

> 评分只对 W2 的验收动作负责：能做到且能复现 = 4–5 分；做得到但证据不全 = 3 分；
> 只会照抄 = 2 分以下。不用「感觉学会了」当证据。

### 1. Kilo 安装、配置与协作 —— 4/5

**做到的：**

- 版本、凭据、模型三条链能对上：`kilo --version` → 7.8.18；`kilo auth list` → Kilo Gateway (oauth) + DeepSeek (api)；
  `kilo models deepseek` → 选用 `deepseek/deepseek-flash`。
- 冒烟与工具调用都有原始输出：`KILO_OK`；让 Kilo 执行 `echo TOOL_OK`，命令实际运行并返回 `TOOL_OK`。
- Key 只在 `~/.local/share/kilo/auth.json`（600）；仓库与 `git ls-files` 无 Key，命令历史里的 `sk-` 命中均为检查命令自身。
- agents 权限用 `kilo agent list` 实测：`code` 可写；`plan` 仅能写 plans 文件；`ask` 全 deny。
- TUI 的目录、模型、版式有 `logs/day06-tmux-status.txt` 抓屏；版本从 7.8.17 到 7.8.18 的差异定位到「升级前启动的旧进程」，重启后一致。
- `notes/kilo.md` 从 W1 的 18 行补到 166 行：三类提示词模板、脚本评审、TCIA 事实核查、TUI 命令表、权限表都在。
- W2 记录 3 条抓错（D7 论文 DOI 差一位；D10 TDR 路线与 CSV 行数各 1 条），其中 2 条改变了实际操作。

**扣分原因：**

- **抓错记录没有按日落地**：D7 1 条、D10 2 条，D6/D8/D9 既没有抓错，也没有写「今日无」，无法区分「真的没出错」和「忘了记」。
- `/status` 面板没有单独截图；目录、模型、版本是由 TUI 状态栏和输入行证明的，证据可用，但不是最直接的那一份。
- D6 的 `Add credits` 是模型前缀与凭据路由错位，不是 Kilo 的知识错误；但它说明「先 `auth list` 再选模型」的顺序没有在第一次就固定下来。

### 2. Docker 实操 —— 4/5

**做到的：**

- 从 `docker run --rm hello-world` 到 `ubuntu:24.04` 容器内装 Node 22、Kilo 7.8.18、授权、冒烟，整条链跑通。
- YOLO 的判据不是「它说开了」，而是写 `/work/logs/yolo-ok.txt` 没有批准提示、宿主能看到落盘；容器内 `uid=1001(dev)`，宿主显示 `501:20`。
- `:ro` 挂载有原始日志：`ls /data/lung1_smoke` 正常；`touch` 报 `Read-only file system`，`touch exit=1`；同一容器 `/work` 可写。
- `intern-base:0.1` 做到非 root `dev`、`HOME=/home/dev`、基础镜像钉 digest、`DEBIAN_FRONTEND` 改 `ARG`、`git config --system --add safe.directory=*`、`.dockerignore` 补 `.env`。
- `docker commit` 做了 `docker diff` + `inspect` 实测，能说清它只记录可写层和运行配置，不适合作为交付环境的构建方式。

**扣分原因：**

- `hello-world` 和 YOLO 落盘的输出只写在日志正文里，没有像 `:ro`、`intern-base`、`kilo-version` 那样留下原始日志文件；复核时少一份直接证据。
- `--network none` 防外发只写在笔记的边界表里，W2 没有实测；`:ro` 证明的是「防误写」，不是「防泄密」。
- D8 的日期口径在收尾时改过一次（详见「收尾纪律」）；这不影响 Docker 能力，但说明当天的日期没有一次定清。

### 3. Conda 环境与可重建 —— 5/5

**做到的：**

- 用户级 Miniconda（不 sudo），`conda 26.9.4`，`radiomics` 环境 Python 3.10.22，`which python` 落在 `envs/radiomics/bin/python`。
- 13 条卡点覆盖了真实会挡住重建的环节：Anaconda 默认渠道 ToS、`conda search` 多包名、pyradiomics 无 conda-forge/py310 构建、
  pip 构建隔离、numpy 2.x 移除 `np.float`、`--from-history` 丢 pip 包、`PIP_NO_BUILD_ISOLATION=1` 对 `conda env create` 无效。
- 三层锁齐全：`environment.yml`、`conda-explicit.txt`、`pip-freeze.txt`；`env/rebuild.sh` 把「建环境 + 单独编译 pyradiomics」固化成一条命令。
- 删环境重建有日志（`logs/day09-rebuild.log`，26 KB），重建后 `import radiomics, lifelines, sksurv, pydicom` → `OK`，`featureextractor OK`。
- 跨平台验证：同一份 `environment.yml` 在 linux-64 与 osx-arm64 都成功，顶层版本一致（python 3.10.22 / numpy 1.26.4 / pyradiomics 3.0.1），build 串不同。
- `notes/Conda.md` 83 行，包含环境判别、三层锁、重建 ≠ 恢复、已知坑表；不是命令堆砌。

**保留意见（不扣分）：**

- `env/README.md` 只有 17 行，信息密度高但偏薄；交接时仍需配合 `journal/day09.md` 阅读。它不影响「删掉能重建」这条硬验收。

### 4. 数据获取与 DICOM 验证 —— 4/5

**做到的：**

- 数据身份写清：TCIA NSCLC-Radiomics v4、422 subjects、1,265 series、52,073 images、35.78 GB、CC BY-NC 3.0、数据集 DOI 与论文 DOI 分开。
- 临床表用 Python `csv` 读为 423 条记录 / 422 个唯一 PatientID；manifest 为 1,265 个唯一 series UID，与官方 v4 规模一致。
- LUNG1-001 小样本落地：3 个 series，136 个 DICOM + 3 个 LICENSE，87 MB。
- DICOM 头部核验：CT `1.2.840.10008.5.1.4.1.1.2`、SEG `...1.1.66.4`、RTSTRUCT `...1.1.481.3`；
  `RTSTRUCT -> CT`、`SEG -> CT` 均为 `True`；SEG 536 frames = 4 segments × 134 slices，不是 536 层 CT。
- `code/00_download.py` 334 行，支持 `--full/--resume/--retry`；`--limit 1` 首跑 `ok=1`，重跑 `skip=1`；
  60 秒全量中断测试完成 2 个 series，重跑 `[skip]`×2。
- 磁盘估算有算术过程：单例 89,922,837 B × 422 = 37.95 GB / 35.34 GiB，与官方 35.78 GB 同量级。
- `data/README.md` 342 行，路线选择、校验方案、已知缺陷、不入 Git 都写了。

**扣分原因：**

- **`--full` 没有端到端验证**：W2 只跑了 60 秒 / 2 个 series；D11 实际全量数据来自 t12ub 已有副本（D11 补记），
  所以 `00_download.py` 的完整 422 例下载路线仍是「已实现、未全程验证」。
- **G2 的 tmux 证据是替代证据**：`tmux` 会话 `dl` 里跑的是 TDR 续传，不是 `00_download.py`；TDR 后来又不是最终路线。
  这能证明 tmux 里能跑下载，但不能证明脚本在 tmux 里跑完全量。
- `journal/day10.md:37` 仍写着「当日 commit | 待提交」，而当天实际已有 `c10094c` 等提交；这是收尾漏改，不是没提交。
- W2 末条 `e59336a` 未推，D10 的「完成」在远程仓库里缺最后一步。

### 5. 收尾、提交与证据纪律 —— 3/5

**做到的：**

- D6、D7 的 INDEX 行当天回填；D8 在 10-27 先填、10-28 按完成日修正；D10 的 G2 九项在 10-30 收尾时全部结案。
- W1 的「笔记回填」问题明显改善：`notes/kilo.md` 18→166 行，`notes/SSH.md` 14→231 行，`docker.md`、`Conda.md` 也从占位变成可读手册。
- 提交粒度总体更细，`day06`–`day10` 前缀共 32 条；44/45 条已进 `origin/main`。
- 仓库没有 `.dcm`、`data/raw/`、Key 文件；`.gitignore` 与 `git ls-files` 复核一致。

**扣分原因：**

- **日期口径反复**：D6、D7 的日志日期都是 10-27；D8 从 10-27 下午开始，10-28 继续做 `intern-base`、镜像加固和 `docker commit`，最终按完成日写成 10-28。
  `day08.md` 与 `INDEX.md` 的日期也从 10-27 改成 10-28（`13b91ac`、`016b42e`）。按完成日记日期本身合理，但先填 10-27 再改 10-28，说明回填时没有先定口径。
  五个工作日实际落在 10-27–10-30 四个日历日，D6/D7 同日。
- **D9 打卡晚一天**：D9 日志日期 10-29，INDEX 行到 10-30 16:52 才补；虽然只晚一天，但 W1 的「当天回填」标准没有完全守住。
- **D10 收尾不完整**：`day10.md:37` 的「当日 commit」仍是待提交；W2 末条提交未推；G2 在 16:52 还是「三项待复查」，16:55 才按 D8/D9 证据转全绿。
- **周复盘再次迟交**：W1 复盘拖到 D6，W2 复盘拖到 D15，而且 W3 复盘先写完；「周末复盘」没有进入固定流程。
- **抓错记录缺日**：W2 只有 3 条，未达「每天至少 1 条（含今日无）」的 W1 改进目标；累计 8 条，低于 D10 的 ≥10。
- 部分 `docs(...)` 提交只写「做了什么」，没有「 - 一句话结论」段；提交规范只部分保持。

## G2 验收自检

> D10 的 G2 清单在 `journal/day10.md` 有 9 条。下表只把原始输出或可重跑命令当证据，不把日志正文的结论当证据。

| 验收项 | 证据 | 状态 |
|---|---|---|
| 临床 CSV 是 422 行数据 + 表头，字段能解释 | `wc -l` 422；Python `csv` 读 423 条记录 / 422 个唯一 PatientID | 通过 |
| `data/README.md` 含路线选择理由与校验方案 | 342 行；路线 B（TCIA REST API）、校验、已知缺陷、不入 Git；D11 追加实际落地说明 | 通过，附 D11 路线变更 |
| 3 个 series 已落地，`du -sh` 数字合理 | LUNG1-001：136 个 DICOM + 3 个 LICENSE，87 MB | 通过 |
| DICOM 头部可读，类型正确，掩膜引用 CT | CT/SEG/RTSTRUCT 的 SOPClassUID 正确；`RTSTRUCT -> CT`、`SEG -> CT` 均为 `True` | 通过 |
| 下载脚本支持 `--full` / `--resume` / `--retry`，断点逻辑已实测 | 334 行；`--limit 1` 首跑 `ok=1`、重跑 `skip=1`；60 秒中断后 `[skip]`×2 | 通过（未跑完整 422 例） |
| `environment.yml` 删环境后可重建 | `logs/day09-rebuild.log` 26 KB；重建后 import OK；linux-64 与 osx-arm64 都成功 | 通过 |
| 容器内 `kilo --version` 与 `KILO_OK` 有记录 | `logs/day08-kilo-version.txt` → 7.8.18；`smoke-test.txt` → `KILO_OK` | 通过 |
| `tmux` 内能跑下载脚本 | `tmux` 会话 `dl` 跑的是 TDR 续传，不是 `00_download.py`；小样本走 HTTP 中转 | 部分（替代证据） |
| `docker build` 成功 | `logs/day08-intern-base.txt`：`intern-base:0.1`，`User=dev`，`uid=1001(dev)` | 通过 |

**判定：G2 通过（D10 当天结案），附三项偏差：**

1. **D8 日期口径**：D8 从 10-27 开始、10-28 继续完成，日期按完成日记成 10-28；`INDEX.md` 先填 10-27 后改 10-28，口径在当天没有一次定清。
2. **tmux 证据替代**：G2 的 tmux 项由 TDR 续传满足，不是最终下载脚本；TDR 后来被放弃。
3. **全量路线变更**：D11 实际全量数据来自 t12ub 已有副本，不是 `00_download.py` 重新下载；脚本的 `--full` 仍是备用路线（D11 补记）。

另外，G2 的三项 D8/D9 证据是在 D10 16:52–16:55 之间由「待复查」转为「全绿」的。
这符合「用已有证据结案」的规则，但也说明 G2 不是当天全部动作都做完才勾，而是收尾时统一核对；
证据的时效性要在报告里写清。

## 报错与卡点（32 条，摘 13 条原文）

> 按日志里的「### 卡点」标题计：D6 3 条、D7 2 条、D8 6 条、D9 13 条、D10 8 条，共 32 条。
> 下面只摘会改变操作或最耗时的 13 条；其余原文见各日日志。

| # | 天 | 报错原文 | 根因 | 修复 / 证据 |
|---|---|---|---|---|
| 1 | D6 | `Error: Add credits to continue, or switch to a free model` | `kilo/` 前缀走托管 Gateway，OAuth 账号无额度；模型 ID 也不在 `kilo models deepseek` 列表 | 改用 `deepseek/deepseek-flash`，冒烟返回 `KILO_OK` |
| 2 | D8 | `failed to resolve reference "docker.io/library/hello-world:latest" ... context deadline exceeded` | 本机到 `registry-1.docker.io:443` 不通；Docker Desktop 的 Linux VM 不走 macOS 系统代理 | 配 `docker.m.daocloud.io` + `docker.1ms.run`，`/v2/` 返回 401 后拉取成功 |
| 3 | D8 | `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/...` 停在 0 字节 | `raw.githubusercontent.com` 不可达 | 不装 nvm；用 npmmirror 的 Node 22 tarball + npmmirror registry |
| 4 | D8 | `EOF` 和 `docker run ...` 粘在同一行，提示符停在 `>` | heredoc 结束符必须独占一行且完全匹配；后面的命令被当成文件内容 | `Ctrl-C` 取消；多行写入改用编辑器，或先确认末行只有 `EOF` |
| 5 | D8 | `docker start kilo-box` 后 `docker ps -a` 又显示 `Exited (0)` | 容器主进程是交互式 `bash`；后台 `start` 没有 stdin，bash 读到 EOF 就退出 | `docker start -ai` / `attach`；服务型容器才用 `start` |
| 6 | D8 | `docker exec -u dev` 后 `HOME` 仍是 `/root` | `--user` 只改 uid/gid，不改镜像里的 `HOME`；Kilo 去 `/root` 找配置 | 显式 `-e HOME=/home/dev`；进容器先 `echo $HOME` |
| 7 | D9 | `kex_exchange_identification: Connection closed by remote host` | Mac 所在链路对 `github.com:22` 有干预；t12ub 上是 `Permission denied (publickey)`，说明链路可达但没私钥 | `ssh -A t12ub` + `ForwardAgent yes` + `ssh-add`，在 t12ub 上 `git clone` 成功 |
| 8 | D9 | `CondaToSNonInteractiveError: Terms of Service have not been accepted ...` | conda ≥25 在执行前校验 `~/.condarc` 的 `defaults` 渠道条款；`-y` 非交互模式无法弹确认 | `conda tos accept` 两条；建环境用 `-c conda-forge --override-channels` |
| 9 | D9 | `ERROR: Failed to build 'pyradiomics' ... No module named 'numpy'`；加 `--no-build-isolation` 后变 `No module named 'versioneer'` | pip 默认 PEP 517 构建隔离，隔离环境里只有 setuptools/wheel；且 numpy 2.x 不提供 `np.float`（1.24 起移除） | numpy 降到 1.26.4；`pip install versioneer`；`pip install --no-build-isolation --no-cache-dir pyradiomics` |
| 10 | D9 | `PIP_NO_BUILD_ISOLATION=1` 对 `conda env create` 无效，日志仍出现 `Installing build dependencies` | `conda env create` 内部另起 pip 子进程执行 `-r requirements.txt`，yml 的 `pip:` 段没有位置传 flag | 从 yml 删掉 `pip:` 段；`env/rebuild.sh` 两段式：建环境 + 单独编译 |
| 11 | D10 | `curl: (28) SSL connection timeout`；`HTTP 000` | 190 到 TCIA 的 443 TCP 能到，但 TLS 握手完不成，出口被限制 | 不在 190 上继续调网络；mac 下载 + 局域网 HTTP 中转 |
| 12 | D10 | `[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate` | Python.org 的 macOS 安装包不自动把系统 CA 装进 Python 信任库 | 脚本优先用 `certifi.where()` 建 SSLContext；回退系统 CA 路径 |
| 13 | D10 | `wc -l` 显示 422，但 Python `csv` 读为 423 条 | 文件末行没有换行符，`wc -l` 数的是换行符个数 | 以 CSV 解析器为准；不修改原始数据 |

另有 D10 小样本 `find` 139 个文件 vs 136 个 DICOM（3 个 LICENSE）、`find /data` 扫盘过慢、
D8 macOS 桌面目录授权弹窗等，原文见 `journal/day08.md`–`day10.md`。

### 最耗时的三个坑

| 坑 | 为什么耗时 | 教训 |
|---|---|---|
| pyradiomics 的「构建隔离 + ToS + numpy 2」三连 | 第一次 `conda env create` 在 pip 段失败，删了半个环境；`PIP_NO_BUILD_ISOLATION=1` 又不生效，必须改成两段式 | 需要 `--no-build-isolation` 的包不能交给 yml 的 `pip:` 段；环境本体与编译包分开重建 |
| 网络出口 | Docker Hub、GitHub raw、TCIA、PyPI 四个源分别以不同方式失败；TDR 包 156 MB，下载中断在 26 MB，最终仍用不上 | 先探测 DNS/TCP/TLS/应用层握手，再决定装什么工具；能上 GitHub 不等于能上 TCIA |
| 日期与证据漂移 | D8 日期口径改过一次、D9 打卡次日补、D10 的 commit 行没更新、周复盘拖到 D15 | 日期和 hash 要在动作发生时写；周复盘是门禁项，不是「想起来再做」 |

## Kilo 抓错记录（W2 3 条）

| 天 | Kilo 说 | 我核实到 | 结论 |
|---|---|---|---|
| D7 | 论文 DOI 是 `10.1038/ncomms4006` | 官方页面与 Crossref 都是 `10.1038/ncomms5006`；`ncomms4006` 是另一篇网络函数论文 | 差一位的 DOI 格式合法、能解析，最难自查；引用前必须解析并核对标题/作者 |
| D10 | 建议优先用 TDR 下全量 | 190 到 TCIA 的 TLS 出口不通，TDR 装完也拉不到数据 | 先确认数据源可达，再决定下载工具；工具不能绕过出口限制 |
| D10 | 预期 CSV `wc -l` 为 423 | 本机 `wc -l` = 422；Python `csv` 读为 423 条，差在末行无换行符 | 行数校验以 CSV 解析器或 `awk 'END{print NR}'` 为准，不只看 `wc -l` |

W1 已记 5 条，W1+W2 累计 8 条，低于 D10 的 ≥10 目标。
更关键的是 D6/D8/D9 连「今日无」都没写，说明不是「Kilo 没出错」，而是「没有每天记录」。
本复盘只补录有原文的 3 条，不事后编造。

## 两条改进（W4 仍适用）

### 改进 1：先验证目标可达性，再选工具和路线

**问题**：W2 的 32 条卡点里，网络/出口类约占三分之一。Docker Hub 超时换镜像源、GitHub raw 超时换 Node tarball、
TCIA TLS 超时改 mac 中转、PyPI 慢改清华镜像——每次都是先撞墙再换工具。TDR 包 156 MB，下载中断在 26 MB，最后因为 190 到 TCIA 不通而没用上。

**做法**：任何下载/安装任务，开工前固定做三层探测，并记录哪一层失败：

```bash
getent hosts <host> || dig +short <host>
curl -sS -o /dev/null -w '%{http_code} %{time_total}s\n' --connect-timeout 5 https://<host>/
openssl s_client -connect <host>:443 -servername <host> </dev/null 2>/dev/null | head -5
```

- DNS 返回 `198.18.0.0/15` 时，按 fake-IP/透明代理处理，`nc` 成功没有证明力；
- TLS 握手失败就换路线，不要继续装「仍然需要访问同一个域名」的工具；
- 探测结果写进当天日志的「关键命令」，不靠回忆。

**验收标准（W4 可检查）：**

- 下载/安装任务开始前，日志里能指出失败发生在 DNS、TCP、TLS 还是应用层；
- 不再出现「工具装完才发现数据源不可达」；
- 至少一次在换路线前就停下，而不是先花半小时下载安装包。

### 改进 2：把周复盘和抓错记录钉进每日收尾

**问题**：W1 复盘拖到 D6，W2 复盘拖到 D15，而且 W3 复盘先完成；抓错 W2 只有 3 条，D6/D8/D9 没有「今日无」。
这不是写作能力问题，是收尾没有固定动作。

**做法：**

- 每日日志模板最后固定两节：`## Kilo 抓错`（没有就写「今日无」）与 `## 收尾`（INDEX 行、commit、push、明日门禁）。
- D5/D10/D15 的收尾 commit 必须同时包含 `journal/weekN-review.md` 和 `journal/INDEX.md` 的对应行；
  周复盘不跨周补，更不允许下一周复盘先于上一周。
- W2 欠下的复盘已经补在这里，但「补交」本身要记为一次失误，不当作正常完成。

**验收标准：**

```bash
for d in 06 07 08 09 10; do
  grep -Eq "抓错|今日无" journal/day$d.md || echo "missing: day$d"
done
git log --format='%ad %s' --date=short -- journal/weekN-review.md
```

- 每天都有「抓错」或「今日无」，不出现空白；
- 周复盘文件的提交日期等于门禁日（D5/D10/D15），不是下一周；
- 收尾 commit 里能同时看到日志、INDEX 和复盘。

## 遗留问题

| 项 | 现状 | 处理 |
|---|---|---|
| D8 日期口径 | D8 跨 10-27–10-28；`day08.md` 与 `INDEX.md` 最终写 10-28，但 10-27 已有前半段实操提交 | 在 `day08.md` 顶部注明「10-27 开始、10-28 完成，日期按完成日记」，避免后续把 D8 全部算到 10-28 |
| `day10.md:37` | 仍写「当日 commit \| 待提交」，实际已有 `c10094c` 等提交 | 改成「已提交」并补 hash，或删掉该行 |
| W2 末条提交 `e59336a` | 不在 `origin/main`；当前 `main` 领先 47 条（含 D11–D15） | 与后续提交一起 push，确认 `git status -sb` 为 `ahead 0` |
| G2 的 tmux 证据 | 用 TDR 续传满足，不是 `00_download.py` | 在 `day10.md` 的 G2 表里注明「替代证据」；或在 tmux 里补一次短时 `--full --resume` 并留日志 |
| `00_download.py --full` | 只验证到 60 秒 / 2 个 series；D11 实际用 t12ub 已有副本 | 要么补一次端到端验证，要么在 `data/README.md` 明确写「可复现路线/备用方案，未做全量端到端」 |
| W2 抓错数量 | 3 条；累计 8 条，低于 D10 的 ≥10 | 不能事后编造；在 W2 记为未达标，W4 用固定小节补齐 |

## 本周结论（只写验证过的）

1. **环境可重建有两个边界**：配方可跨平台（linux-64 与 osx-arm64 都能建出 Python 3.10.22 / numpy 1.26.4 / pyradiomics 3.0.1），
   但构建产物不可跨平台搬运（build 串不同）；ToS 状态、编译器、PyPI 可达性是机器级前置。
2. **conda 与 pip 的边界有硬判据**：`conda list` 里的 `<pip>` / `pypi_0` 标记说明 conda 不认识这个包，`--from-history` 必然丢；
   需要 `--no-build-isolation` 的包不能进 yml 的 `pip:` 段，`env/rebuild.sh` 是目前唯一验证过的做法。
3. **Docker 的隔离边界要说准**：`:ro` 只挡写，不挡读和外发；`--user` 必须配 `-e HOME`；交互式容器不是服务；
   可复现镜像的底线是钉 digest、非 root、`.dockerignore` 不含密钥。
4. **网络故障要按层判断**：`kex_exchange_identification` 是链路问题，`Permission denied (publickey)` 才是密钥问题；
   fake-IP 下 `nc` 成功没有意义；能上 GitHub 不等于能上 TCIA。
5. **小样本 G2 证明的是入口，不是全量**：D10 只验证了 136 个 DICOM 和 60 秒 / 2 个 series；
   D11 的全量数据来自 t12ub 已有副本，`00_download.py --full` 仍是未端到端验证的备用路线。
6. **证据链要包含原始输出**：`kilo-version.txt`、`smoke-test.txt`、`logs/day08-*.txt`、`logs/day09-rebuild.log`
   比日志正文里的一句「已通过」更有复核价值。
7. **日期和提交也是证据**：D8 日期口径改过一次、D9 打卡次日补、D10 的「待提交」没更新、W2 末条没推，
   都会让「当天全绿」打折；技术做对不等于记录可信。
8. **本周最大的进步是笔记，最大的短板是收尾**：`kilo.md` 18→166 行、`SSH.md` 14→231 行，
   说明「当天回填」有效；但抓错 3 条、周复盘拖到 D15，说明收尾动作还没有变成肌肉记忆。
9. **W2 最可复用的不是某条命令，而是几张边界表**：Docker vs Conda、镜像 vs 容器、重建 vs 恢复、
   `--auto` vs `permission: allow`、路线 A/B/C。这些区分比多装一个工具更能减少后面的返工。
