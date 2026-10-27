---
day: 05
date: 2026-10-23
theme: SSH 全链路（免密/传输/校验/转发）+ 第一周复盘
gate: G1
---

# Day 05｜SSH 全链路 + 第一周复盘（G1）

## 今日目标

安全、免密、可传输、可长跑地连上 `t12ub`，并把第 1 周（D1–D5）的证据收口，过 G1。

今天不是「从零配 SSH」，而是**验证已有链路 + 补齐可复核证据**：D4 已经用 `ssh t12ub` 传过数据，
说明别名和认证在 10-22 就通了。今天要把「为什么通」讲清楚，并留下 `ssh-check.txt`、哈希比对、
端口转发和一周复盘。

## 平台与配置现状（开工先核实，2026-10-23 实测）

> 计划按通用环境写（端口 22、新建 ed25519）；本机现状与计划有出入，先记录再执行，
> 否则照抄计划里的 `-p 22` 会连不上。

| 项 | 计划写法 | 本机实测 | 结论 |
|---|---|---|---|
| 端口 | `22` | `10022`（`ssh -G t12ub` 输出 `port 10022`） | **以 10022 为准**；计划里的 22 不适用于当前 t12ub |
| 用户名 | `<用户名>` | `jqw` | 已固化在 `~/.ssh/config` |
| 主机 | `192.168.18.87` | 同左 | 一致 |
| 主机别名 | 今天新建 `Host t12ub` | **已存在**，D4 已用 `ssh t12ub` 成功 | 不重建，只核对字段 |
| 认证密钥 | 新建 `~/.ssh/id_ed25519` | 实际用 `/Users/wangjiaqi/Desktop/jqw/id_rsa`（RSA） | 沿用现有密钥；是否另建 ed25519 见下 |
| `ServerAliveInterval` | `60` | `60` | 一致 |
| `ServerAliveCountMax` | `3` | 生效值 `3`（未显式写在 Host 段，用默认） | 可显式补上，便于阅读 |
| 本机 SSH 客户端 | — | `OpenSSH_9.7p1, LibreSSL 3.3.6` | 支持 ed25519 / `-L` / `-N` |
| `~/.ssh` 权限 | `700` | `drwx------`（700） | 已合规 |
| `~/.ssh/config` 权限 | `600` | `-rw-------`（600） | 已合规 |
| 现有私钥权限 | `600` | `-rw-------`（600） | 已合规 |
| `ssh-copy-id` | 可能没有（Windows） | `/usr/bin/ssh-copy-id` 存在 | macOS 可直接用 |
| 环境自检 | D4 产物能跑 | `bash code/setup_check.sh` → `RESULT: WARN`，`exit=1`（Home avail 75GB < 150GB） | 脚本可跑；WARN 是磁盘阈值，不是脚本故障 |
| 服务器仓库目录 | 默认 `~/work/intern-<用户>-nsclc-survival` | **开工时不存在**；`find` 只命中空的 `~/kilo-work/nsclc-radiomics` 和原始数据 `~/.data/nsclc-radiomics` | 已 `mkdir -p ~/work/intern-jqw-nsclc-survival`，在其中生成证据 |

**今天的策略**：先验证现有 `t12ub` 链路（不动可用配置），再决定是否新增一把 ed25519 专用于实习仓库。
若新增，只追加 `IdentityFile`，不要覆盖现有 RSA 配置——覆盖会导致 D4 已验证的免密链路失效。
**实测结论**：不新增。现有 RSA 已被服务器 `authorized_keys:1` 接受，`BatchMode` 免密通过，
再加一把只会多一个需要维护的凭据。

## 今天这串操作用的到底是什么（原理串讲）

> 表面是敲几条命令，实际是在建立一条**可验证的信任链**：
> 连得上 → 连的是对的机器 → 只有我能连 → 文件没被改 → 服务能安全暴露。

| 步骤 | 表面动作 | 实际验证的东西 |
|---|---|---|
| `ssh -G t12ub` | 查看配置 | 别名把 host/port/user/key 解析成什么；开工先发现端口是 10022 而不是计划里的 22，避免超时误判 |
| `ssh -p 10022 jqw@...` 或 `ssh t12ub` | 登录 | TCP 可达、主机身份、用户认证三件事同时成立 |
| 首次指纹输入 `yes` | 接受 host key | 防中间人：确认对端确实是 t12ub，而不是同网段的冒充者 |
| `ssh-check.txt` | 记录主机信息 | 证明「我确实在目标机器上执行过」，D20 仍可复核；`pwd` 同时证明落点是约定目录 |
| `ssh -o BatchMode=yes ...` | 禁止交互后再连一次 | 排除手输密码/口令的干扰，证明认证只靠公钥，而不是「看起来没提示密码」 |
| `~/.ssh` 700、`authorized_keys` 600 | 看权限位 | `StrictModes` 的前提：公钥白名单不能被同组或其他用户篡改 |
| `scp` / `rsync` | 拷文件 | 数据通道复用同一条加密链路；`-P` 是端口，`-p` 在 scp 里是保留时间戳 |
| SHA-256 双端比对 | 算哈希 | 完整性：传输中没有截断、编码转换或拷错文件。**哈希相同 ≠ 文件可信**，只证明两端一致 |
| `ssh -N -L 8889:127.0.0.1:8888` | 端口转发 | 把远程 `127.0.0.1:8888` 映射到本机 8889，流量仍走 SSH 加密通道；为 D14 的 Jupyter 铺路 |

一句话：今天不是「学会 `ssh` 命令」，而是能回答四个问题——
**连的是谁**（host key）、**我是谁**（publickey）、**文件有没有变**（SHA-256）、
**服务怎么安全暴露**（tunnel）。权限位是这条链的地基，任何一环松了，后面的证据都不成立。

## 今日要交付什么

> 早上填写，收尾逐项打勾并补证据；证据必须可复核。任何一项没做就留「待做」，不写推测结果。

| # | 交付物 | 具体要求 | 证据 | 状态 |
|---|---|---|---|---|
| 1 | `ssh-check.txt` | 在 t12ub 仓库目录生成，含 `hostname`/`whoami`/`pwd`/`uname -a`/`date`/`df -h "$HOME"` | 远程文件 + 本地副本 | ✅ 2026-10-23 09:58 HKT 生成；7 行 332B；本机副本同为 332B |
| 2 | 免密登录验证 | `ssh t12ub` 不提示密码；`hostname`/`whoami`/`pwd` 输出正确 | 终端记录 | ✅ `ssh -o BatchMode=yes t12ub 'hostname'` → `t12ub`，无密码/口令交互 |
| 3 | 别名与保活配置 | `Host t12ub` 含 HostName/User/Port/ServerAliveInterval/ServerAliveCountMax；`chmod 600 ~/.ssh/config` | `ssh -G t12ub` 输出 | ✅ 配置已存在且权限 600（端口 10022；`ServerAliveCountMax` 生效值 3，未显式写入；本次未改配置） |
| 4 | 本机 → 远程传输 | `scp` 或 `rsync` 上传一个小文件，远程可见 | 两端 `ls -l` | ✅ 首次 133 文件/681103B；清理后二次 `sent 869B`、`speedup 194.17` |
| 5 | 远程 → 本机传输 | 取回 `ssh-check.txt` 到仓库根 | 本地文件 | ✅ `scp -P 10022 ...` 100% 332B；本地 `ls -l` 332B |
| 6 | 目录同步 | `rsync -avP --exclude` 同步一次目录，确认排除生效 | `rsync` 输出 | ✅ 39 considered / 0 transferred；反向 27 文件，两端 27/27 一致 |
| 7 | SHA-256 一致性 | 两端对 `ssh-check.txt` 计算，哈希逐字相同 | 两条命令输出 + `diff` | ✅ 双端 `8d5ebcc9c887834a60a5d185f1c0bedb026929143b8a3e8e78249cf1e1fdebba` |
| 8 | 端口转发 | `ssh -N -L 8888:localhost:8888 t12ub` 能建立；远程起临时 HTTP 服务验证 | 本机 `curl`/浏览器结果 | ✅ 本机 8888 被 Jupyter 占用，改用 8889；`curl -I` → `200 OK`（Python 3.12.3） |
| 9 | `journal/week1-review.md` | 五能力点自评 1–5 + 证据；报错原文 ≥5 条 + 根因；下周改进 2 件 | 文件本身 | ✅ |
| 10 | 当日 commit | 格式 `<scope>: <做了什么> - <一句话结论>` | `git log --oneline` | ✅ `d28a1a6` 骨架、`b400b78` 免密+哈希 |
| 11 | `journal/INDEX.md` D5 行 | 回填日期、commit、验收结果 | 文件本身 | ✅ |

## 今日验收标准（G1，收尾逐条核对）

- [x] `ssh t12ub` 免密进入，`hostname` / `whoami` / `pwd` 输出正确（`BatchMode=yes` → `t12ub`）
- [x] `ssh-check.txt` 已生成，本机副本 SHA-256 与远程一致（`8d5ebcc…`）
- [x] 能解释 `700` / `600` 权限与免密登录的关系（见下文，需用自己的话复述）
- [x] `bash code/setup_check.sh` 能跑（今日 `WARN`/`exit=1`，75GB 阈值告警）；`set -euo pipefail` 解释见 `journal/day04.md`
- [x] `journal/` 有 D1–D5 五篇日志 + `week1-review.md`
- [x] `git log` 有 5 个以上按规范命名的 commit（`git rev-list --count HEAD` = 56）
- [x] `journal/INDEX.md` D5 行回填完成

## 关键命令

> 其中 `ssh -V`、`ssh -G`、`ls ~/.ssh`、`bash code/setup_check.sh` 属于 Kilo 代跑的只读检查，其余登录、生成证据、传输和隧道命令由本人在终端执行。
> 本机是 macOS，服务器是 Linux。**`ssh` 用小写 `-p`，`scp` 用大写 `-P`。**

```bash
# ——【Mac】开工前核对：不改任何东西，先看现状 ——
ssh -V                                  # OpenSSH_9.7p1, LibreSSL 3.3.6
ssh -G t12ub                            # 生效配置：user jqw / hostname 192.168.18.87 / port 10022
ls -ld ~/.ssh ~/.ssh/config             # 700 / 600
bash code/setup_check.sh; echo "exit=$?" # RESULT: WARN，exit=1（75GB < 150GB）
```

```bash
# ——【t12ub】登录后立刻验收，证据写进仓库 ——
ls ~/work                                   # 实测：No such file or directory → 目录不存在
find ~ -maxdepth 4 -type d -name '*nsclc*'  # 只命中 ~/kilo-work/nsclc-radiomics（空）与 ~/.data/...（原始数据）
find ~ -maxdepth 4 -type d -name 'intern-*' # 空输出 → 服务器上没有仓库副本
mkdir -p ~/work/intern-jqw-nsclc-survival   # 按计划约定新建；不要 git init，避免阻塞未来 clone
cd ~/work/intern-jqw-nsclc-survival
pwd                                         # /home/jqw/work/intern-jqw-nsclc-survival
{ hostname; whoami; pwd; uname -a; date; df -h "$HOME"; } | tee ssh-check.txt
ls -l ssh-check.txt                         # -rw-rw-r-- 332 字节
cat ssh-check.txt
```

```bash
# ——【Mac】免密验证（现有链路）——
ssh -o BatchMode=yes t12ub 'hostname'   # 实测输出 t12ub；BatchMode 禁止密码/口令交互

# 服务器侧权限（StrictModes 的前提）
ssh t12ub 'ls -ld ~ ~/.ssh; ls -l ~/.ssh/authorized_keys'
# drwxr-x--- 15 jqw jqw  /home/jqw                 ← 750，组可读/进入但不可写
# drwx------  2 jqw jqw  /home/jqw/.ssh            ← 700
# -rw-------  1 jqw jqw  /home/jqw/.ssh/authorized_keys  ← 600，736 字节

# 公钥被接受的证据（本次 ssh -v 的实际输出）
ssh -v t12ub true 2>&1 | tail -n 20
# debug1: Remote: /home/jqw/.ssh/authorized_keys:1: key options: ...
# debug1: Exit status 0
```

```bash
# ——【Mac】双向传输 ——
# 远程 → 本机（已做）：100% 332B，本地 ls -l 同为 332B
scp -P 10022 t12ub:~/work/intern-jqw-nsclc-survival/ssh-check.txt ./

# 本机 → 远程（已做）：首次 198 considered / 133 transferred / sent 681103B
# 清理远端 .kilo 与 plans20.zip 后重跑：39 considered / 0 transferred / sent 869B / speedup 194.17
rsync -avP --exclude '.git' --exclude '.kilo' --exclude 'data/raw' \
  --exclude '*.zip' --exclude '.DS_Store' \
  ./ t12ub:~/work/intern-jqw-nsclc-survival/

# 远程 → 本机目录（已做）：27 个文件 / 175927B；用 /tmp 避免 backup/ 污染仓库
rsync -avP t12ub:~/work/intern-jqw-nsclc-survival/ /tmp/d5-backup/

# 第一次只排除了 .git/data/raw/.DS_Store，把 .kilo 和 plans20.zip 也传了
# 原因：.gitignore 对 rsync 无效，必须显式 --exclude；dry-run 清单已经列出来了
# 注意：scp 的端口是大写 -P；小写 -p 在 scp 里表示保留时间戳，报 “unknown option” 才是版本差异
# 源目录结尾的 ./ 与目标目录结尾的 / 都不能少，否则会多套一层目录
```

```bash
# ——两端哈希（必须一致）——
shasum -a 256 ssh-check.txt                        # macOS / 本机
ssh t12ub 'sha256sum ~/work/intern-jqw-nsclc-survival/ssh-check.txt'   # Linux / 远程
# 实测两边都是：
# 8d5ebcc9c887834a60a5d185f1c0bedb026929143b8a3e8e78249cf1e1fdebba
```

```bash
# ——端口转发（已做；本机 8888 被 Jupyter 占用，改用 8889）——
# 终端 A（本机）：左边是本机端口，右边是「服务器视角」的回环地址
ssh -N -L 8889:127.0.0.1:8888 t12ub
# 终端 B（服务器）：只监听回环，不暴露给局域网
ssh t12ub 'cd /tmp && python3 -m http.server 8888 --bind 127.0.0.1'
# 终端 C（本机）：lsof 看到 ssh 在 8889 LISTEN；curl 返回 200 OK
lsof -nP -iTCP:8889 -sTCP:LISTEN
curl -I http://127.0.0.1:8889
# 实测：HTTP/1.0 200 OK / Server: SimpleHTTP/0.6 Python/3.12.3
# 收尾：B、A 各 Ctrl+C；本机 8889 与远程 8888 都应无监听
# 关键：-L 右侧的 127.0.0.1 是服务器的回环，不是 Mac 的；本机 8888 的 Jupyter 不受影响
```

## 实验记录

### SSH 链路验收

| 项 | 实测 | 结论 |
|---|---|---|
| 客户端版本 | `OpenSSH_9.7p1, LibreSSL 3.3.6` | ✅ 支持 ed25519 / `-L` / `-N` |
| 生效主机名 | `192.168.18.87` | ✅ 与计划一致 |
| 生效端口 | `10022` | ✅ 以实测为准（计划写的 22 不适用） |
| 生效用户 | `jqw` | ✅ 来自 `~/.ssh/config` |
| 生效 IdentityFile | `/Users/wangjiaqi/Desktop/jqw/id_rsa` | ✅ 现有 RSA 密钥，权限 600 |
| 免密结果 | `ssh -o BatchMode=yes t12ub 'hostname'` → `t12ub` | ✅ 无密码/口令交互，只靠公钥 |
| `hostname` | `t12ub` | ✅ |
| `whoami` | `jqw` | ✅ |
| `pwd` | `/home/jqw/work/intern-jqw-nsclc-survival` | ✅ 与交付物落点一致 |

### 免密与权限

| 检查点 | 命令 | 实测 | 判定 |
|---|---|---|---|
| 本机 `~/.ssh` | `ls -ld ~/.ssh` | `drwx------`（700） | ✅ |
| 本机 config | `ls -l ~/.ssh/config` | `-rw-------`（600） | ✅ |
| 本机私钥 | `ls -l /Users/wangjiaqi/Desktop/jqw/id_rsa` | `-rw-------`（600） | ✅ |
| 服务器 `~/.ssh` | `ssh t12ub 'ls -ld ~/.ssh'` | `drwx------ 2 jqw jqw 4096 Oct 19 13:58 /home/jqw/.ssh` | ✅ 700 |
| 服务器 `authorized_keys` | `ssh t12ub 'ls -l ~/.ssh/authorized_keys'` | `-rw------- 1 jqw jqw 736 Oct 15 17:22 /home/jqw/.ssh/authorized_keys` | ✅ 600 |
| 服务器家目录 | `ssh t12ub 'ls -ld ~'` | `drwxr-x--- 15 jqw jqw 4096 Oct 23 09:57 /home/jqw` | ✅ 750；组可读/进入、不可写，满足 `StrictModes` |
| `ssh -v` 命中密钥 | `ssh -v t12ub true 2>&1 \| tail -n 20` | `Remote: /home/jqw/.ssh/authorized_keys:1: key options: ...`；`Exit status 0` | ✅ 公钥被接受 |

### 传输与哈希

| 项 | 实测 |
|---|---|
| 上传命令 / 结果 | `rsync -avP --exclude '.git' --exclude '.kilo' --exclude 'data/raw' --exclude '*.zip' --exclude '.DS_Store' ./ t12ub:.../`；首次 198 considered / 133 transferred / sent 681103B；清理后 39 considered / **0 transferred** / sent 869B / speedup 194.17 |
| 下载命令 / 结果 | `scp -P 10022 t12ub:~/work/intern-jqw-nsclc-survival/ssh-check.txt ./` → `100% 332 37.3KB/s`；本地 `ls -l` 332B |
| 目录同步 / 排除是否生效 | 反向 `rsync -avP t12ub:.../ /tmp/d5-backup/` → 27 文件 / 175927B；两端 `find -type f \| wc -l` 均为 27；`.git`、`.kilo`、`data/raw`、`*.zip` 均未上传 |
| 本机 SHA-256 | `8d5ebcc9c887834a60a5d185f1c0bedb026929143b8a3e8e78249cf1e1fdebba` |
| 远程 SHA-256 | `8d5ebcc9c887834a60a5d185f1c0bedb026929143b8a3e8e78249cf1e1fdebba` |
| README 双端 SHA-256 | `d90e80b298f6ecb6463dce9a967c0ac0ae3f6a0bea1c869af729c97d16c70967`（两端一致） |
| 是否一致 | ✅ 逐字相同；本次未跑 `diff`，是目视两条输出 |

### 端口转发

| 项 | 实测 |
|---|---|
| 转发命令 | `ssh -N -L 8889:127.0.0.1:8888 t12ub`（本机 8888 被 Jupyter 占用，左侧改 8889） |
| 本机监听 | `lsof -nP -iTCP:8889 -sTCP:LISTEN` → `ssh` PID 51614 在 `127.0.0.1:8889` 与 `[::1]:8889` LISTEN |
| 远程临时服务 | `ssh t12ub 'cd /tmp && python3 -m http.server 8888 --bind 127.0.0.1'`；`ss -ltn` → `127.0.0.1:8888 LISTEN` |
| 访问结果 | `curl -I http://127.0.0.1:8889` → `HTTP/1.0 200 OK`，`Server: SimpleHTTP/0.6 Python/3.12.3` |
| 结束后是否释放端口 | ✅ 本机 8889 与远程 8888 均无监听 |

## `700` / `600` 与免密登录的关系（G1 必答）

`sshd` 默认开启 `StrictModes`，会检查认证相关路径的**所有者**和**写权限**：

- `~/.ssh` 必须是 `700`（`drwx------`）：只有属主能进入、列目录、增删文件。
  若同组或其他用户可写，别人就能往目录里塞文件、替换 `authorized_keys`，因此 `sshd` 直接拒绝使用该目录。
- `~/.ssh/authorized_keys` 必须是 `600`（`-rw-------`）：只有属主可读写。
  若组/其他用户可写，等于公钥白名单可被他人篡改，同样被拒。
- 家目录本身也不能对组/其他用户可写（常见 `777` 家目录导致免密失败）。

失败时 `sshd` 只在客户端显示 `Permission denied (publickey)`，服务器日志才可能给出
`Authentication refused: bad ownership or modes`，所以“静默拒绝”要靠权限位排查。

本机私钥是另一条独立规则：`ssh` 客户端发现私钥可被他人读取时会报
`WARNING: UNPROTECTED PRIVATE KEY FILE` 并拒绝使用，需要 `chmod 600`。

一句话记忆：**目录 700 防“换文件”，文件 600 防“改内容”，私钥 600 防“被抄走”。**

## 计划与现实的偏差（今天必须先处理的）

| 计划写法 | 本机/服务器现实 | 处理 |
|---|---|---|
| `ssh -p 22 jqw@...`、`scp -P 22` | `t12ub` 实际端口 `10022` | 全部改用 10022；`ssh t12ub` 已封装端口，优先用别名 |
| 新建 `~/.ssh/id_ed25519` 并 `ssh-copy-id` | 已有 RSA 密钥在 `~/Desktop/jqw/id_rsa`，D4 免密可用 | 不覆盖；需要新密钥时另起文件名并追加 `IdentityFile` |
| 计划默认 `~/work/intern-<用户名>-nsclc-survival` | 服务器上 `~/work` 不存在；`find` 只命中**空目录** `~/kilo-work/nsclc-radiomics` 和原始数据 `~/.data/nsclc-radiomics` | `mkdir -p ~/work/intern-jqw-nsclc-survival` 后生成；不 `git init`，保留未来 clone 的可能 |
| `~/kilo-work/nsclc-radiomics` 看起来像工作目录 | `ls -la` 只有 `.` 和 `..`，不是 Git 仓库 | 不写入任何交付物；`~/.data/nsclc-radiomics` 是原始数据，也不碰 |
| 计划把配置当“今天新建” | `Host t12ub` 已存在且可用 | 只读核对，未改配置 |
| 计划用 `scp ./README.md t12ub:~/work/` | 目标目录已建且可写，但计划路径是 `~/work/` 根，不是约定仓库目录 | 上传统一落到 `~/work/intern-jqw-nsclc-survival/` |
| 计划默认本机 8888 空闲 | 8888 被本机 Jupyter（Tornado/6.5.5，PID 1083，2026-07-08 启动）长期监听；`curl -I` 对它返回 405（Jupyter 不接受 HEAD） | 隧道左侧改 8889，不杀现有 Jupyter |
| 计划只排除 `data/raw` | `.kilo/` 与 `plans20.zip` 也被 rsync 传上去（`.gitignore` 不作用于 rsync），远端一度 1.2M | 增加 `--exclude '.kilo' --exclude '*.zip'`，清理后 276K；二次同步 0 传输 |

> 结论：**计划里的 22 端口、ed25519、`~/work/<repo>`、空闲的 8888 都是通用假设，不是本环境的现状。**
> 照抄 22 会得到 `Connection timed out`，然后误判为防火墙问题；照抄目录会在第一步就报
> `No such file or directory`；照抄 8888 会报 `Address already in use`。
> 开工前先用 `ssh -G`、`ls`/`find`、`lsof` 核对，比照着计划试错快得多。

## 预判坑（含实测结果，未验证的不进结论）

| 计划里的写法 | 在本环境的可能问题 | 替代写法 | 是否实际踩到 |
|---|---|---|---|
| `ssh -p 22 ...` | 实际端口 10022，与计划不一致 → 连错端口/超时 | `ssh t12ub` 或 `-p 10022` | 未踩（开工先 `ssh -G` 发现） |
| `scp -p 22` | `scp` 的 `-p` 是“保留时间戳”，端口要大写 `-P` | `scp -P 10022` | 未踩（一直用 `-P 10022`） |
| `sha256sum`（Mac） | macOS 无此命令 | `shasum -a 256` | 未踩（本机用 `shasum`） |
| `ssh-copy-id` 后仍要密码 | 服务器 `~/.ssh`/`authorized_keys` 权限过宽 | `chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys` | 未踩（沿用现有密钥，未执行 copy-id） |
| 直接覆盖 `~/.ssh/config` | D4 已验证的 RSA 链路会失效 | 只追加字段，改前先 `cp ~/.ssh/config ~/.ssh/config.bak` | 未踩（只读核对，未改配置） |
| `ssh -N -L 8888:...` | 本机 8888 已被 Jupyter（Tornado，PID 1083）占用 | 换 `8889:127.0.0.1:8888` | **实际踩到**：`bind: Address already in use` |
| `rsync` 同步整个仓库 | 会把 `data/raw` 大文件也拉下来 | `--exclude 'data/raw' --exclude '.git'` | 未踩（已排除）；但漏了 `.kilo`/`*.zip`，见下一行 |
| 以为 `.gitignore` 能管住 rsync | `.kilo/` 和 `plans20.zip` 照样上传，远端 1.2M | 显式 `--exclude '.kilo' --exclude '*.zip'`，清理后 276K | **实际踩到**：首次 133 文件/681KB |
| 会话里直接跑长任务 | 断线收 SIGHUP，任务死 | `tmux` / `nohup`（D4 已验证） | D4 已验证；今天未复验 |

## 卡点与报错（本节不许空着）

> 每个卡点六件齐全：现象（报错原文）、我的猜测、验证过程、根因、解决、下次怎么避免。
> 收尾时删掉未使用的模板。

### 卡点 1：服务器上 `~/work` 不存在，`cd` 直接失败

- **现象**：
  ```text
  jqw@t12ub:~$ ls ~/work
  ls: cannot access '/home/jqw/work': No such file or directory
  ```
- **我的猜测**：D4 已经在服务器上 clone 过仓库，`~/work` 应该存在；或者仓库在 `kilo-work` 下。
- **验证过程**：
  ```text
  find ~ -maxdepth 4 -type d -name '*nsclc*' 2>/dev/null
  # /home/jqw/kilo-work/nsclc-radiomics
  # /home/jqw/.data/nsclc-radiomics
  # /home/jqw/.data/nsclc-radiomics/nsclc_radiomics

  find ~ -maxdepth 4 -type d -name 'intern-*' 2>/dev/null
  # 空输出

  ls -la ~/kilo-work/nsclc-radiomics
  # total 8 ... 只有 . 和 ..
  ```
- **根因**：计划假设 `~/work/intern-<用户名>-nsclc-survival` 已存在，实际服务器上**没有仓库副本**。
  D4 只在 `~/d4-practice` 和 `~/.data/nsclc-radiomics` 工作过，仓库一直只在 Mac 上。
  `kilo-work/nsclc-radiomics` 是空目录，不是 Git 仓库。
- **解决**：`mkdir -p ~/work/intern-jqw-nsclc-survival`，在其中生成 `ssh-check.txt`。
  **没有 `git init`**——目录一旦非空，之后想 `git clone` 到同一路径会失败。
- **下次怎么避免**：执行计划里的 `cd <路径>` 前先 `ls`/`find` 验证；交付物落点与仓库实际位置分开确认；
  空目录不能当仓库，看到 `total 8` 且只有 `.`/`..` 就先怀疑。

### 卡点 2（取证方法）：`ssh -v ... | tail -n 20` 看不到 `Offering public key`

- **现象**：日志末尾只有 channel/env/`Exit status 0`，没有预期的
  `Offering public key` 和 `Server accepts key`，一度怀疑认证没走公钥。
- **我的猜测**：密钥没被用上，可能回退到了密码认证。
- **验证过程**：同一段日志里有
  `Remote: /home/jqw/.ssh/authorized_keys:1: key options: ...`；另跑
  `ssh -o BatchMode=yes t12ub 'hostname'` 仍返回 `t12ub`——`BatchMode` 禁用密码交互，能过就排除了密码回退。
- **根因**：`Offering public key` / `Server accepts key` / `Authenticated to` 打印在**认证阶段**，
  早于 channel 建立；`tail -n 20` 只保留会话尾部，把关键行截掉了。
- **解决**：用已经拿到的两处输出交叉验证：`Remote: .../authorized_keys:1: key options` 说明服务端读到了公钥；
  `BatchMode=yes` 仍能登录说明没有回退到密码。没有额外执行新命令。
- **下次怎么避免**：长日志按关键词定位，不按固定行数截断；判断认证方式优先看
  `Authenticated to ... using "publickey"`，而不是猜。

### 卡点 3：`-L 8888` 报 `bind: Address already in use`

- **现象**：
  ```text
  bind [127.0.0.1]:8888: Address already in use
  channel_setup_fwd_listener_tcpip: cannot listen to port: 8888
  Could not request local forwarding.
  ```
- **我的猜测**：服务器 8888 被别的服务占了，或者 sshd 禁止端口转发。
- **验证过程**：
  ```text
  lsof -nP -iTCP:8888 -sTCP:LISTEN
  # Python 1083 wangjiaqi ... TCP 127.0.0.1:8888 (LISTEN)
  # Python 1083 wangjiaqi ... TCP [::1]:8888 (LISTEN)

  ps -p 1083 -o pid,user,lstart,command
  # 1083 wangjiaqi Wed Jul  8 12:09:48 2026 /opt/homebrew/.../Python

  curl -sI http://127.0.0.1:8888 | head -5
  # HTTP/1.1 405 Method Not Allowed
  # Server: TornadoServer/6.5.5
  ```
- **根因**：`-L` 左侧的 8888 是**本机**监听端口，本机已有 Jupyter（Tornado）长期占用，
  SSH 在本地 bind 失败，连接还没走到服务器就被拒绝。与 t12ub 无关。
- **解决**：只改左侧端口，右侧保持服务器真实监听地址：
  `ssh -N -L 8889:127.0.0.1:8888 t12ub`，`curl -I http://127.0.0.1:8889` 返回 `200 OK`。
- **下次怎么避免**：建隧道前先 `lsof -nP -iTCP:<本机端口> -sTCP:LISTEN`；
  端口冲突只换左边，不要动右边；不要为了腾端口去杀不认识的进程。

### 卡点 4（操作）：前台常驻命令运行时，继续输入的命令没有执行

- **现象**：`ssh t12ub 'cd /tmp && python3 -m http.server 8888 --bind 127.0.0.1'` 运行中，
  同一终端继续输入 `ssh t12ub 'ss -ltn | grep :8888'`，没有任何输出，也没有新提示符。
- **我的猜测**：服务器服务没起来，或第二条命令写错了。
- **验证过程**：另开终端执行 `ss -ltn | grep :8888`，看到 `127.0.0.1:8888 LISTEN`；
  回到原终端按 `Ctrl+C` 后提示符才恢复，说明第二条命令根本没被本地 shell 执行。
- **根因**：前台服务占用终端；`ssh` 未分配 tty 时，本地 stdin 直接接到远端 `http.server` 进程，
  后续键入被当作它的输入（它不读 stdin，于是静默丢弃），不是输入到 bash。
- **解决**：常驻服务、隧道各占一个终端；验证命令另开标签页。需要同终端时用 `&` 或 `tmux`。
- **下次怎么避免**：命令不返回时先判断它是不是常驻进程（server、`-N` 隧道、`tail -f`），
  是就换终端，不要在忙终端里继续敲命令。

## Kilo 使用记录

> 今日玩法：`ssh -v` 输出很长，只截最后 20 行判断卡在哪一步。
> **发日志前先确认里面没有密码、私钥、token、内网口令。**

- 问：`~/work` 不存在，能不能直接 `git init` 凑一个仓库？答：不要，放进 `ssh-check.txt` 后目录非空，会阻塞以后 `git clone`；先建目录只放证据。核实：`find` 确认服务器无仓库副本后，只 `mkdir -p`，未 init。
- 问：怎么证明是「免密」而不是「恰好这次没提示密码」？答：用 `ssh -o BatchMode=yes`，它禁用密码和口令交互。核实：输出 `t12ub`，通过。
- 问：`ssh -v` 末 20 行看不到 `Offering public key`，是不是没走公钥？答：认证日志在会话建立前，`tail` 会截掉；本次改用已有输出交叉确认。核实：`authorized_keys:1` 被接受 + `Exit status 0` + `BatchMode` 成功，确认走私钥。
- 问：dry-run 里出现了 `.kilo/` 和 `plans20.zip`，要不要紧？答：`.gitignore` 对 rsync 无效，必须显式 `--exclude`；已经传上去的要清理。核实：首次 133 文件/681103B；清理后二次 0 传输、`sent 869B`。
- 问：`-L 8888` 报 `Address already in use` 是服务器端口被占吗？答：是本机 bind 失败，看左侧端口。核实：`lsof` 显示本机 Jupyter（Python 1083）占 8888，换 8889 后 `200 OK`。
- **抓错记录**：今日无。计划文件写端口 22 / 新建 ed25519，实测是 10022 / 现有 RSA——属于**计划与环境的偏差**，不是 Kilo 回答错误。

## 今日结论

> 收尾时补到 8–11 条，只写验证过的结论；说不清为什么的结果标 `未验证`。

1. **免密要用 `BatchMode` 证明**：普通 `ssh t12ub` 不提示密码，可能只是 ssh-agent 缓存或本次恰好命中了密钥；`ssh -o BatchMode=yes t12ub 'hostname'` 禁止一切密码/口令交互，仍返回 `t12ub`，才能排除密码回退。
2. **先 `ssh -G` 再连**：别名把 `HostName/User/Port/IdentityFile` 解析成 `192.168.18.87 / jqw / 10022 / Desktop/jqw/id_rsa`。计划写的 22 与解析结果不一致，照抄会连错端口，再把超时误判成防火墙问题。
3. **权限是一条链，不只是一个目录**：服务器家目录 `750`（组可读/进入、不可写）、`~/.ssh` `700`、`authorized_keys` `600`，满足 `StrictModes`；本机私钥同样 `600`。任何一环对组/其他用户可写，`sshd` 都可能静默拒绝，客户端只看到 `Permission denied (publickey)`。
4. **SHA-256 一致只证明「两端相同」**：它证明传输没有截断、编码转换或拷错文件，不证明文件来源可信。来源可信由 host key（连的是谁）+ publickey（我是谁）保证，三者合起来才是完整证据链。
5. **计划里的服务器路径是假设**：`~/work` 原本不存在，`find` 只命中空的 `~/kilo-work/nsclc-radiomics` 和原始数据 `~/.data/nsclc-radiomics`。交付物最终落在新建的 `~/work/intern-jqw-nsclc-survival`；空目录没有 `git init`，避免以后 clone 失败。
6. **最小可复核证据链**：`ssh-check.txt`（7 行/332B，含 `hostname`/`whoami`/`pwd`）+ 双端同一哈希 `8d5ebcc…` + `BatchMode` 免密输出 + 权限位。四个都能被第三方重跑，才算 G1 的「可复核」。
7. **`scp` 端口是大写 `-P`**：本次下载用 `scp -P 10022`，一次成功；小写 `-p` 在 `scp` 里是保留时间戳，不是端口。
8. **rsync 的增量是内容级判断**：首次上传 133 个文件/681103B；清理后用同一命令重跑，`39 files to consider`、`0 transferred`、`sent 869B`、`speedup 194.17`。第二次只交换清单，没重复传数据。
9. **忽略规则有两层，不能混用**：`.gitignore` 只影响 Git，rsync 完全不读；`.kilo/` 和 `plans20.zip` 因此被传上去。传输层的排除必须显式 `--exclude`。dry-run 已经把这两项列出来，读清单比跑完再清理便宜。
10. **`-L` 的左右不是同一台机器**：`-L 8889:127.0.0.1:8888` 中，左边是本机监听端口，右边是**服务器视角**的回环地址。本机 8888 被 Jupyter（Tornado，PID 1083）占用，SSH 在本地 bind 就失败，与服务器无关；换 8889 后 `curl -I` 得到 `200 OK`。
11. **一个终端只承担一个角色**：服务、隧道、验证分开；前台常驻命令运行时，后续键入会进入该进程的 stdin，而不是 bash。判断“命令没反应”前，先看它是不是本来就该阻塞。

## 明日 3 件事

- [ ] 读 `每日计划/Day06.md`（Kilo 安装、配置、冒烟测试）。
- [ ] 复核 G1 全部勾选，补齐 `journal/INDEX.md` D5 行。
- [ ] 把今天验证过的 SSH 结论补进 `notes/SSH.md`（端口 10022、别名、转发、权限）。

