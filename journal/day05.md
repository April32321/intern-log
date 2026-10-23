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

**今天的策略**：先验证现有 `t12ub` 链路（不动可用配置），再决定是否新增一把 ed25519 专用于实习仓库。
若新增，只追加 `IdentityFile`，不要覆盖现有 RSA 配置——覆盖会导致 D4 已验证的免密链路失效。

## 今日要交付什么

> 早上填写，收尾逐项打勾并补证据；证据必须可复核。任何一项没做就留「待做」，不写推测结果。

| # | 交付物 | 具体要求 | 证据 | 状态 |
|---|---|---|---|---|
| 1 | `ssh-check.txt` | 在 t12ub 仓库目录生成，含 `hostname`/`whoami`/`pwd`/`uname -a`/`date`/`df -h "$HOME"` | 远程文件 + 本地副本 | 待做（先确认 `~/work/intern-jqw-nsclc-survival` 是否存在） |
| 2 | 免密登录验证 | `ssh t12ub` 不提示密码；`hostname`/`whoami`/`pwd` 输出正确 | 终端记录 | 待做（D4 已可用，今天补正式证据） |
| 3 | 别名与保活配置 | `Host t12ub` 含 HostName/User/Port/ServerAliveInterval/ServerAliveCountMax；`chmod 600 ~/.ssh/config` | `ssh -G t12ub` 输出 | ✅ 已存在（端口 10022；建议补 `ServerAliveCountMax 3`） |
| 4 | 本机 → 远程传输 | `scp` 或 `rsync` 上传一个小文件，远程可见 | 两端 `ls -l` | 待做 |
| 5 | 远程 → 本机传输 | 取回 `ssh-check.txt` 到仓库根 | 本地文件 | 待做 |
| 6 | 目录同步 | `rsync -avP --exclude` 同步一次目录，确认排除生效 | `rsync` 输出 | 待做 |
| 7 | SHA-256 一致性 | 两端对 `ssh-check.txt` 计算，哈希逐字相同 | 两条命令输出 + `diff` | 待做 |
| 8 | 端口转发 | `ssh -N -L 8888:localhost:8888 t12ub` 能建立；远程起临时 HTTP 服务验证 | 本机 `curl`/浏览器结果 | 待做（Jupyter 在 D14） |
| 9 | `journal/week1-review.md` | 五能力点自评 1–5 + 证据；报错原文 ≥5 条 + 根因；下周改进 2 件 | 文件本身 | 待做（**G1 硬性项**） |
| 10 | 当日 commit | 格式 `<scope>: <做了什么> - <一句话结论>` | `git log --oneline` | 待做 |
| 11 | `journal/INDEX.md` D5 行 | 回填日期、commit、验收结果 | 文件本身 | 待做 |

## 今日验收标准（G1，收尾逐条核对）

- [ ] `ssh t12ub` 免密进入，`hostname` / `whoami` / `pwd` 输出正确
- [ ] `ssh-check.txt` 已生成，本机副本 SHA-256 与远程一致
- [ ] 能解释 `700` / `600` 权限与免密登录的关系（见下文，需用自己的话复述）
- [ ] `bash code/setup_check.sh` 能跑，且能解释 `set -euo pipefail`
- [ ] `journal/` 有 D1–D5 五篇日志 + `week1-review.md`
- [ ] `git log` 有 5 个以上按规范命名的 commit
- [ ] `journal/INDEX.md` D5 行回填完成

## 关键命令

> 本机是 macOS，服务器是 Linux。**`ssh` 用小写 `-p`，`scp` 用大写 `-P`。**

```bash
# ——【Mac】开工前核对：不改任何东西，先看现状 ——
ssh -V                                  # OpenSSH_9.7p1, LibreSSL 3.3.6
ssh -G t12ub                            # 生效配置：user jqw / hostname 192.168.18.87 / port 10022
ls -ld ~/.ssh ~/.ssh/config             # 700 / 600
bash code/setup_check.sh; echo "exit=$?" # RESULT: WARN，exit=1（75GB < 150GB）
```

```bash
# ——【Mac】第一次连接（如果还没采信过主机指纹）——
# 端口以 ssh -G 为准：当前是 10022，不是计划里的 22
ssh -p 10022 jqw@192.168.18.87
# 首次会显示 ED25519/ECDSA 指纹 → 先找负责人核对，再输入完整的 yes
# 密码输入不回显字符，正常
```

```bash
# ——【t12ub】登录后立刻验收，证据写进仓库 ——
cd ~/work/intern-$(whoami)-nsclc-survival    # 若不存在，先 ls ~/work 找实际路径
pwd
{ hostname; whoami; pwd; uname -a; date; df -h "$HOME"; } | tee ssh-check.txt
cat ssh-check.txt
```

```bash
# ——【Mac】免密验证（现有链路）——
ssh t12ub 'hostname'                    # 不应提示密码
ssh t12ub 'whoami'
ssh t12ub 'pwd'
# 若提示密码：先看服务器 ~/.ssh 700、authorized_keys 600，再看本机私钥是否 600
```

```bash
# ——可选：新增一把 ed25519 专用于实习（不覆盖现有 RSA）——
ssh-keygen -t ed25519 -C "intern@t12ub" -f ~/.ssh/id_ed25519_intern
ssh-copy-id -i ~/.ssh/id_ed25519_intern.pub -p 10022 jqw@192.168.18.87
# 然后在 ~/.ssh/config 的 Host t12ub 段【追加】一行，不要删原来的 IdentityFile：
#     IdentityFile ~/.ssh/id_ed25519_intern
# 验证：ssh -v t12ub 观察 “Offering public key” 命中的是哪一把
```

```bash
# ——【Mac】配置文件核对（已存在，只补字段）——
cat ~/.ssh/config
chmod 600 ~/.ssh/config
# Host t12ub 目标形态：
#   HostName 192.168.18.87
#   User jqw
#   Port 10022
#   IdentityFile /Users/wangjiaqi/Desktop/jqw/id_rsa
#   IdentitiesOnly yes
#   ServerAliveInterval 60
#   ServerAliveCountMax 3
```

```bash
# ——【Mac】双向传输（占位路径按实际目录替换）——
scp -P 10022 ./README.md t12ub:~/work/                 # 本机 → 远程
scp t12ub:~/work/intern-jqw-nsclc-survival/ssh-check.txt ./   # 远程 → 本机
rsync -avP --exclude 'data/raw' t12ub:~/work/repo/ ./backup/  # 目录同步（可续传/可排除）
# 注意：scp 的端口是大写 -P；小写 -p 在 scp 里表示保留时间戳，报 “unknown option” 才是版本差异
```

```bash
# ——两端哈希（必须一致）——
shasum -a 256 ssh-check.txt                        # macOS / 本机
ssh t12ub 'sha256sum ~/work/intern-jqw-nsclc-survival/ssh-check.txt'   # Linux / 远程
# 可选：落到文件后 diff
shasum -a 256 ssh-check.txt | awk '{print $1}' > /tmp/mac.sha
ssh t12ub 'sha256sum ~/work/intern-jqw-nsclc-survival/ssh-check.txt' | awk '{print $1}' > /tmp/srv.sha
diff /tmp/mac.sha /tmp/srv.sha && echo "哈希一致"
```

```bash
# ——端口转发（D14 的 Jupyter 预演）——
ssh -N -L 8888:localhost:8888 t12ub
# 另开一个终端，在远程起临时服务验证：
ssh t12ub 'cd /tmp && python3 -m http.server 8888'
# 本机浏览器打开 http://localhost:8888，或 curl -I http://localhost:8888
# 验证完 Ctrl+C 结束两条命令；若 8888 被占用，改 -L 8889:localhost:8888
```

```bash
# ——断线长跑（“可长跑”的验收）——
ssh t12ub
tmux new -s d5        # 或复用已有会话
# 会话内跑一个 5 分钟任务
sleep 300
# Ctrl+b 松开后按 d → detach
exit                  # 断开 SSH
ssh t12ub 'tmux ls'   # d5 仍在
ssh -t t12ub 'tmux attach -t d5'   # 回到 pane，任务还在
```

## 实验记录

### SSH 链路验收

| 项 | 实测 | 结论 |
|---|---|---|
| 客户端版本 | `OpenSSH_9.7p1, LibreSSL 3.3.6` | 待填 |
| 生效主机名 | `192.168.18.87` | 待填 |
| 生效端口 | `10022` | 待填（与计划 22 不一致，已记录） |
| 生效用户 | `jqw` | 待填 |
| 生效 IdentityFile | `/Users/wangjiaqi/Desktop/jqw/id_rsa` | 待填 |
| 免密结果 | 待填（是否提示密码） | 待填 |
| `hostname` | 待填 | 待填 |
| `whoami` | 待填 | 待填 |
| `pwd` | 待填 | 待填 |

### 免密与权限

| 检查点 | 命令 | 实测 | 判定 |
|---|---|---|---|
| 本机 `~/.ssh` | `ls -ld ~/.ssh` | `drwx------`（700） | ✅ |
| 本机 config | `ls -l ~/.ssh/config` | `-rw-------`（600） | ✅ |
| 本机私钥 | `ls -l /Users/wangjiaqi/Desktop/jqw/id_rsa` | `-rw-------`（600） | ✅ |
| 服务器 `~/.ssh` | `ssh t12ub 'ls -ld ~/.ssh'` | 待填（期望 `drwx------`） | 待填 |
| 服务器 `authorized_keys` | `ssh t12ub 'ls -l ~/.ssh/authorized_keys'` | 待填（期望 `-rw-------`） | 待填 |
| 服务器家目录 | `ssh t12ub 'ls -ld ~'` | 待填（不能 group/other 可写） | 待填 |
| `ssh -v` 命中密钥 | `ssh -v t12ub true 2>&1 \| tail -n 20` | 待填（`Offering public key` / `Server accepts key`） | 待填 |

### 传输与哈希

| 项 | 实测 |
|---|---|
| 上传命令 / 结果 | 待填 |
| 下载命令 / 结果 | 待填 |
| 目录同步 / 排除是否生效 | 待填 |
| 本机 SHA-256 | 待填 |
| 远程 SHA-256 | 待填 |
| 是否一致 | 待填 |

### 端口转发

| 项 | 实测 |
|---|---|
| 转发命令 | `ssh -N -L 8888:localhost:8888 t12ub` |
| 本机监听 | 待填（`lsof -nP -iTCP:8888 -sTCP:LISTEN`） |
| 远程临时服务 | 待填（`python3 -m http.server 8888`） |
| 访问结果 | 待填（浏览器 / `curl -I`） |
| 结束后是否释放端口 | 待填 |

### 断线长跑

| 项 | 实测 |
|---|---|
| tmux 会话名 | 待填 |
| detach 后 `tmux ls` | 待填 |
| 断开 SSH 后是否存活 | 待填 |
| attach 回来任务是否还在 | 待填 |

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
| 计划默认 `~/work/intern-<用户名>-nsclc-survival` | 未核实该目录是否存在 | 先 `ssh t12ub 'ls ~/work'`，按实际路径生成 `ssh-check.txt` |
| 计划把配置当“今天新建” | `Host t12ub` 已存在且可用 | 改为核对 + 补 `ServerAliveCountMax`，不重写 |
| 计划用 `scp ./README.md t12ub:~/work/` | `~/work/` 是否可写未核实 | 先确认目标目录与权限，再传 |

> 结论：**计划里的 22 端口和 ed25519 是通用写法，不是本环境的现状。**
> 照抄会得到 `Connection timed out`，然后误判为防火墙问题。

## 预判坑（待实测确认，未验证的不进结论）

| 计划里的写法 | 在本环境的可能问题 | 替代写法 | 是否实际踩到 |
|---|---|---|---|
| `ssh -p 22 ...` | 实际端口 10022，22 无监听 → 超时 | `ssh t12ub` 或 `-p 10022` | 待填 |
| `scp -p 22` | `scp` 的 `-p` 是“保留时间戳”，端口要大写 `-P` | `scp -P 10022` | 待填 |
| `sha256sum`（Mac） | macOS 无此命令 | `shasum -a 256` | 待填 |
| `ssh-copy-id` 后仍要密码 | 服务器 `~/.ssh`/`authorized_keys` 权限过宽 | `chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys` | 待填 |
| 直接覆盖 `~/.ssh/config` | D4 已验证的 RSA 链路会失效 | 只追加字段，改前先 `cp ~/.ssh/config ~/.ssh/config.bak` | 待填 |
| `ssh -N -L 8888:...` | 本机 8888 已被占用（Jupyter 常见） | 换 `8889:localhost:8888` | 待填 |
| `rsync` 同步整个仓库 | 会把 `data/raw` 大文件也拉下来 | `--exclude 'data/raw' --exclude '.git'` | 待填 |
| 会话里直接跑长任务 | 断线收 SIGHUP，任务死 | `tmux` / `nohup`（D4 已验证） | 待填 |

## 卡点与报错（本节不许空着）

> 每个卡点六件齐全：现象（报错原文）、我的猜测、验证过程、根因、解决、下次怎么避免。
> 收尾时删掉未使用的模板。

### 卡点 1：待填

- **现象**：
  ```text
  待填（原样粘贴报错，不要改写）
  ```
- **我的猜测**：待填
- **验证过程**：待填（跑了什么命令，输出是什么）
- **根因**：待填
- **解决**：待填
- **下次怎么避免**：待填

### 卡点 2：待填

- **现象**：待填
- **我的猜测**：待填
- **验证过程**：待填
- **根因**：待填
- **解决**：待填
- **下次怎么避免**：待填

## Kilo 使用记录

> 今日玩法：`ssh -v` 输出很长，只截最后 20 行判断卡在哪一步。
> **发日志前先确认里面没有密码、私钥、token、内网口令。**

- 问：这段 `ssh -v` 卡在 `debug1: Authentications that can continue: publickey,password`，是密钥没被接受还是根本没发出去？答：待填。核实：待填。
- 问：`Permission denied (publickey)` 在 `StrictModes` 下最该先查哪三个权限位？答：待填。核实：待填。
- **抓错记录**：待填（Kilo 说 X，我核实是 Y；没有就写“今日无”）。

## 今日结论

> 收尾时补 3–7 条，只写验证过的结论；说不清为什么的结果标 `未验证`。

1. 待填
2. 待填
3. 待填

## 第一周复盘入口（另写 `journal/week1-review.md`）

G1 要求单独一份复盘，不在本文件里凑数。五能力点建议按下面五行自评并各附一条证据：

| 能力点 | 自评（1–5） | 证据（文件/命令/commit） |
|---|---|---|
| Git 工作流（提交规范、撤销、远程） | 待填 | `journal/day01.md`、`day02.md` |
| Linux 文件、权限、路径 | 待填 | `journal/day03.md`、`notes/linux-cli.md` §1 |
| 进程、tmux、长任务 | 待填 | `journal/day04.md`、tmux 实测 |
| 环境变量、PATH、bash 脚本 | 待填 | `code/setup_check.sh`、`notes/linux-cli.md` §12–§13 |
| SSH 远程协作（免密/传输/转发） | 待填 | 本文件 |

另外必须包含：本周报错原文 ≥5 条 + 根因、下周改进 2 件事。

## 明日 3 件事

- [ ] 读 `每日计划/Day06.md`（Kilo 安装、配置、冒烟测试）。
- [ ] 复核 G1 全部勾选，补齐 `journal/INDEX.md` D5 行。
- [ ] 把今天验证过的 SSH 结论补进 `notes/SSH.md`（端口 10022、别名、转发、权限）。

## 收尾

```bash
git add journal/day05.md journal/week1-review.md journal/INDEX.md notes/SSH.md
git commit -m "day05: ssh 免密登录与文件传输验证 + w1 复盘"
git log --oneline -5
```
