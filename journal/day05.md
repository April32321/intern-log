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
| `ssh -N -L 8888:localhost:8888` | 端口转发 | 把远程 `localhost:8888` 映射到本机，流量仍走 SSH 加密通道；为 D14 的 Jupyter 铺路 |

一句话：今天不是「学会 `ssh` 命令」，而是能回答四个问题——
**连的是谁**（host key）、**我是谁**（publickey）、**文件有没有变**（SHA-256）、
**服务怎么安全暴露**（tunnel）。权限位是这条链的地基，任何一环松了，后面的证据都不成立。

## 今日要交付什么

> 早上填写，收尾逐项打勾并补证据；证据必须可复核。任何一项没做就留「待做」，不写推测结果。

| # | 交付物 | 具体要求 | 证据 | 状态 |
|---|---|---|---|---|
| 1 | `ssh-check.txt` | 在 t12ub 仓库目录生成，含 `hostname`/`whoami`/`pwd`/`uname -a`/`date`/`df -h "$HOME"` | 远程文件 + 本地副本 | ✅ 2026-10-23 09:58 HKT 生成；7 行 332B；本机副本同为 332B |
| 2 | 免密登录验证 | `ssh t12ub` 不提示密码；`hostname`/`whoami`/`pwd` 输出正确 | 终端记录 | ✅ `ssh -o BatchMode=yes t12ub 'hostname'` → `t12ub`，无密码/口令交互 |
| 3 | 别名与保活配置 | `Host t12ub` 含 HostName/User/Port/ServerAliveInterval/ServerAliveCountMax；`chmod 600 ~/.ssh/config` | `ssh -G t12ub` 输出 | ✅ 已存在（端口 10022；`ServerAliveCountMax` 生效值 3，未显式写入；建议补上） |
| 4 | 本机 → 远程传输 | `scp` 或 `rsync` 上传一个小文件，远程可见 | 两端 `ls -l` | 待做（上传方向尚未执行） |
| 5 | 远程 → 本机传输 | 取回 `ssh-check.txt` 到仓库根 | 本地文件 | ✅ `scp -P 10022 ...` 100% 332B；本地 `ls -l` 332B |
| 6 | 目录同步 | `rsync -avP --exclude` 同步一次目录，确认排除生效 | `rsync` 输出 | 待做 |
| 7 | SHA-256 一致性 | 两端对 `ssh-check.txt` 计算，哈希逐字相同 | 两条命令输出 + `diff` | ✅ 双端 `8d5ebcc9c887834a60a5d185f1c0bedb026929143b8a3e8e78249cf1e1fdebba` |
| 8 | 端口转发 | `ssh -N -L 8888:localhost:8888 t12ub` 能建立；远程起临时 HTTP 服务验证 | 本机 `curl`/浏览器结果 | 待做（Jupyter 在 D14） |
| 9 | `journal/week1-review.md` | 五能力点自评 1–5 + 证据；报错原文 ≥5 条 + 根因；下周改进 2 件 | 文件本身 | 待做（**G1 硬性项**） |
| 10 | 当日 commit | 格式 `<scope>: <做了什么> - <一句话结论>` | `git log --oneline` | 进行中（骨架提交 `d28a1a6`；证据待提交） |
| 11 | `journal/INDEX.md` D5 行 | 回填日期、commit、验收结果 | 文件本身 | 待做 |

## 今日验收标准（G1，收尾逐条核对）

- [x] `ssh t12ub` 免密进入，`hostname` / `whoami` / `pwd` 输出正确（`BatchMode=yes` → `t12ub`）
- [x] `ssh-check.txt` 已生成，本机副本 SHA-256 与远程一致（`8d5ebcc…`）
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
ssh t12ub 'whoami'                      # 本次未单独跑；ssh-check.txt 中为 jqw
ssh t12ub 'pwd'                         # 本次未单独跑；ssh-check.txt 中为仓库路径

# 服务器侧权限（StrictModes 的前提）
ssh t12ub 'ls -ld ~ ~/.ssh; ls -l ~/.ssh/authorized_keys'
# drwxr-x--- 15 jqw jqw  /home/jqw                 ← 750，组可读/进入但不可写
# drwx------  2 jqw jqw  /home/jqw/.ssh            ← 700
# -rw-------  1 jqw jqw  /home/jqw/.ssh/authorized_keys  ← 600，736 字节

# 认证路径取证：tail 只截会话尾部，Offering/Accepts 行要靠 grep
ssh -v t12ub true 2>&1 | grep -E 'Offering public key|Server accepts key|Authenticated to|Authentications that can continue'
# 实测 tail -n 20 只看到：
#   debug1: Remote: /home/jqw/.ssh/authorized_keys:1: key options: ...
#   debug1: Exit status 0
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
# ——【Mac】双向传输 ——
# 远程 → 本机（已做）：100% 332B，本地 ls -l 同为 332B
scp -P 10022 t12ub:~/work/intern-jqw-nsclc-survival/ssh-check.txt ./

# 本机 → 远程（待做）：用 rsync 同时验证排除规则
rsync -avP --exclude '.git' --exclude 'data/raw' --exclude '.DS_Store' \
  ./ t12ub:~/work/intern-jqw-nsclc-survival/
# 远程 → 本机目录（待做）：落到 /tmp，避免 backup/ 污染仓库
rsync -avP t12ub:~/work/intern-jqw-nsclc-survival/ /tmp/d5-backup/

# 注意：scp 的端口是大写 -P；小写 -p 在 scp 里表示保留时间戳，报 “unknown option” 才是版本差异
# 源目录结尾的 ./ 与目标目录结尾的 / 都不能少，否则会多套一层目录
```

```bash
# ——两端哈希（必须一致）——
shasum -a 256 ssh-check.txt                        # macOS / 本机
ssh t12ub 'sha256sum ~/work/intern-jqw-nsclc-survival/ssh-check.txt'   # Linux / 远程
# 实测两边都是：
# 8d5ebcc9c887834a60a5d185f1c0bedb026929143b8a3e8e78249cf1e1fdebba

# 可选：落到文件后 diff（本次是目视两条输出逐字相同，未跑 diff）
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
| `ssh -v` 命中密钥 | `ssh -v t12ub true 2>&1 \| grep 'authorized_keys'` | `Remote: /home/jqw/.ssh/authorized_keys:1: key options: ...`；`Exit status 0` | ✅ 公钥被接受（末 20 行不含 `Offering public key`，取证要按关键词过滤） |

### 传输与哈希

| 项 | 实测 |
|---|---|
| 上传命令 / 结果 | 待做（计划用 `rsync --exclude '.git' --exclude 'data/raw'`） |
| 下载命令 / 结果 | `scp -P 10022 t12ub:~/work/intern-jqw-nsclc-survival/ssh-check.txt ./` → `100% 332 37.3KB/s`；本地 `ls -l` 332B |
| 目录同步 / 排除是否生效 | 待做 |
| 本机 SHA-256 | `8d5ebcc9c887834a60a5d185f1c0bedb026929143b8a3e8e78249cf1e1fdebba` |
| 远程 SHA-256 | `8d5ebcc9c887834a60a5d185f1c0bedb026929143b8a3e8e78249cf1e1fdebba` |
| 是否一致 | ✅ 逐字相同；本次未跑 `diff`，是目视两条输出 |

### 端口转发

| 项 | 实测 |
|---|---|
| 转发命令 | `ssh -N -L 8888:localhost:8888 t12ub` |
| 本机监听 | 待做（`lsof -nP -iTCP:8888 -sTCP:LISTEN`） |
| 远程临时服务 | 待做（`python3 -m http.server 8888`） |
| 访问结果 | 待做（浏览器 / `curl -I`） |
| 结束后是否释放端口 | 待做 |

### 断线长跑

| 项 | 实测 |
|---|---|
| tmux 会话名 | 待做（建议 `d5`） |
| detach 后 `tmux ls` | 待做 |
| 断开 SSH 后是否存活 | 待做 |
| attach 回来任务是否还在 | 待做（D4 已用 `work` 会话验证过同一机制） |

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
| 计划把配置当“今天新建” | `Host t12ub` 已存在且可用 | 改为核对 + 补 `ServerAliveCountMax`，不重写 |
| 计划用 `scp ./README.md t12ub:~/work/` | 目标目录已建且可写，但计划路径是 `~/work/` 根，不是约定仓库目录 | 上传统一落到 `~/work/intern-jqw-nsclc-survival/` |

> 结论：**计划里的 22 端口、ed25519、`~/work/<repo>` 都是通用假设，不是本环境的现状。**
> 照抄 22 会得到 `Connection timed out`，然后误判为防火墙问题；照抄目录会在第一步就报
> `No such file or directory`。开工前先用 `ssh -G` 和 `ls`/`find` 核对，比照着计划试错快得多。

## 预判坑（待实测确认，未验证的不进结论）

| 计划里的写法 | 在本环境的可能问题 | 替代写法 | 是否实际踩到 |
|---|---|---|---|
| `ssh -p 22 ...` | 实际端口 10022，22 无监听 → 超时 | `ssh t12ub` 或 `-p 10022` | 未踩（开工先 `ssh -G` 发现） |
| `scp -p 22` | `scp` 的 `-p` 是“保留时间戳”，端口要大写 `-P` | `scp -P 10022` | 未踩（一直用 `-P 10022`） |
| `sha256sum`（Mac） | macOS 无此命令 | `shasum -a 256` | 未踩（本机用 `shasum`） |
| `ssh-copy-id` 后仍要密码 | 服务器 `~/.ssh`/`authorized_keys` 权限过宽 | `chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys` | 未踩（沿用现有密钥，未执行 copy-id） |
| 直接覆盖 `~/.ssh/config` | D4 已验证的 RSA 链路会失效 | 只追加字段，改前先 `cp ~/.ssh/config ~/.ssh/config.bak` | 未踩（只读核对，未改配置） |
| `ssh -N -L 8888:...` | 本机 8888 已被占用（Jupyter 常见） | 换 `8889:localhost:8888` | 待验证 |
| `rsync` 同步整个仓库 | 会把 `data/raw` 大文件也拉下来 | `--exclude 'data/raw' --exclude '.git'` | 待做 |
| 会话里直接跑长任务 | 断线收 SIGHUP，任务死 | `tmux` / `nohup`（D4 已验证） | D4 已验证；今天待复验 |

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
- **解决**：
  ```bash
  ssh -v t12ub true 2>&1 | grep -E 'Offering public key|Server accepts key|Authenticated to|Authentications that can continue'
  ```
- **下次怎么避免**：长日志按关键词过滤，不按固定行数截断；判断认证方式优先看
  `Authenticated to ... using "publickey"`，而不是猜。

## Kilo 使用记录

> 今日玩法：`ssh -v` 输出很长，只截最后 20 行判断卡在哪一步。
> **发日志前先确认里面没有密码、私钥、token、内网口令。**

- 问：`~/work` 不存在，能不能直接 `git init` 凑一个仓库？答：不要，放进 `ssh-check.txt` 后目录非空，会阻塞以后 `git clone`；先建目录只放证据。核实：`find` 确认服务器无仓库副本后，只 `mkdir -p`，未 init。
- 问：怎么证明是「免密」而不是「恰好这次没提示密码」？答：用 `ssh -o BatchMode=yes`，它禁用密码和口令交互。核实：输出 `t12ub`，通过。
- 问：`ssh -v` 末 20 行看不到 `Offering public key`，是不是没走公钥？答：认证日志在会话建立前，`tail` 会截掉，应按关键词 grep。核实：`authorized_keys:1` 被接受 + `Exit status 0` + `BatchMode` 成功，确认走私钥。
- **抓错记录**：今日无。计划文件写端口 22 / 新建 ed25519，实测是 10022 / 现有 RSA——属于**计划与环境的偏差**，不是 Kilo 回答错误。

## 今日结论

> 收尾时补 3–7 条，只写验证过的结论；说不清为什么的结果标 `未验证`。

1. **免密要用 `BatchMode` 证明**：普通 `ssh t12ub` 不提示密码，可能只是 ssh-agent 缓存或本次恰好命中了密钥；`ssh -o BatchMode=yes t12ub 'hostname'` 禁止一切密码/口令交互，仍返回 `t12ub`，才能排除密码回退。
2. **先 `ssh -G` 再连**：别名把 `HostName/User/Port/IdentityFile` 解析成 `192.168.18.87 / jqw / 10022 / Desktop/jqw/id_rsa`。计划写的 22 与解析结果不一致，照抄会连错端口，再把超时误判成防火墙问题。
3. **权限是一条链，不只是一个目录**：服务器家目录 `750`（组可读/进入、不可写）、`~/.ssh` `700`、`authorized_keys` `600`，满足 `StrictModes`；本机私钥同样 `600`。任何一环对组/其他用户可写，`sshd` 都可能静默拒绝，客户端只看到 `Permission denied (publickey)`。
4. **SHA-256 一致只证明「两端相同」**：它证明传输没有截断、编码转换或拷错文件，不证明文件来源可信。来源可信由 host key（连的是谁）+ publickey（我是谁）保证，三者合起来才是完整证据链。
5. **计划里的服务器路径是假设**：`~/work` 原本不存在，`find` 只命中空的 `~/kilo-work/nsclc-radiomics` 和原始数据 `~/.data/nsclc-radiomics`。交付物最终落在新建的 `~/work/intern-jqw-nsclc-survival`；空目录没有 `git init`，避免以后 clone 失败。
6. **最小可复核证据链**：`ssh-check.txt`（7 行/332B，含 `hostname`/`whoami`/`pwd`）+ 双端同一哈希 `8d5ebcc…` + `BatchMode` 免密输出 + 权限位。四个都能被第三方重跑，才算 G1 的「可复核」。
7. **`scp` 端口是大写 `-P`**：本次下载用 `scp -P 10022`，一次成功；小写 `-p` 在 `scp` 里是保留时间戳，不是端口。

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
# 证据已就绪，先落这一笔
git add ssh-check.txt journal/day05.md
git commit -m "day05: 回填 ssh 验收实测 - BatchMode 免密 + 双端 sha256 一致"

# week1-review 完成后收口（文件不存在时先别跑这条，git add 会整体失败）
git add journal/week1-review.md journal/INDEX.md notes/SSH.md
git commit -m "day05: ssh 免密登录与文件传输验证 + w1 复盘"
git log --oneline -5
```
