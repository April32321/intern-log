---
day: 04
date: 2026-10-22
theme: Linux CLI（二）进程、tmux、环境变量、bash 脚本
gate: -
---

# Day 04｜Linux CLI（二）：进程、环境变量、bash 脚本、tmux

## 今日目标

能管长任务、能写小脚本、能看懂 PATH 问题（D6 装 Kilo 时 90% 的报错都和这有关）。

另两项：
1. 把「绝对路径 / 相对路径」练到不查资料就能写对，尤其是跨目录读写仓库文件。
2. 用 **2 例真实患者数据** 走一遍「服务器 → scp → 本地校验 → Slicer 看一眼 CT」的冒烟链路；**不做诊断、不做重新识别**。

## 今日要交付什么

> 早上填写，收尾时逐项打勾并补证据；证据必须可复核。

| # | 交付物 | 具体要求 | 证据 | 状态 |
|---|---|---|---|---|
| 1 | 路径自测记录 | `notes/linux-cli.md` §1「绝对路径 vs 相对路径」补 4 题自测表与两个坑（`cd -`、前导 `/`） | 笔记 + 实际命令输出 | 进行中（笔记已写，终端复跑待做） |
| 2 | 2 例数据冒烟 | 从 `t12ub` `scp` 2 例 `LUNG1-*` 到 `data/raw/lung1_smoke/`，两端 SHA-256 一致；Slicer 能打开 CT 看一眼 | 命令输出 + `ls data/raw/lung1_smoke` | ✅（232/232 一致，已打开 CT） |
| 3 | `code/setup_check.sh` | 检查 OS/架构/CPU/磁盘/命令是否存在，输出 PASS/WARN，能处理 MISSING，退出码有意义 | 文件 + `bash code/setup_check.sh` 输出 | 待做 |
| 4 | `notes/linux-cli.md` 下半 | §10 进程、§11 tmux、§12 环境变量/PATH、§13 脚本、§14 压缩归档；标题由「（一）」改为通用 | 文件本身 | 进行中（标题已改，§10–§11 完成；§12–§14 待做） |
| 5 | `journal/day04.md` | 本文件：卡点须有报错原文/根因/解决，至少 1 条「Kilo 说 X，我核实是 Y」 | 本文件 | 进行中 |
| 6 | `journal/INDEX.md` D4 行 | 收尾回填日期（2026-10-22）、commit hash、验收结果 | `journal/INDEX.md` | 待做 |
| 7 | 当日 commit | ≥1 次，格式 `<scope>: <做了什么> - <一句话结论>` | `git log --oneline` | ✅（day04 已 5 次，最新 `799f75b`） |
| 8 | 服务器练习目录 | `~/d4-practice/`（tmux、nohup、日志都放这里，**不写进仓库 `logs/`**） | `ls ~/d4-practice` | ✅（`trap_demo.py`、`term.log`、`kill9.log`、`nohup.out`、各 `*.pid`） |

## 平台前提（今日命令分两处跑）

> 计划照 Linux 写；仓库在 Mac，练习在服务器 `t12ub`。

| 内容 | 位置 |
|---|---|
| 进程、kill、jobs、nohup、tmux、PATH、脚本实测 | `t12ub` |
| 写脚本、写笔记、commit | Mac 仓库 `/Users/wangjiaqi/Desktop/实习日志` |
| 5 分钟 sleep + detach/attach 验收 | `t12ub`（断 SSH 才能验证） |
| 2 例数据 `scp` 到本地 + SHA-256 校验 + 打开 CT | Mac（数据落在 `data/raw/`，不入 Git） |

## 今日验收标准（收尾逐条核对）

- [ ] 4 道路径自测题全对，能解释 `cd ..` 与 `cd -`、`../notes` 与 `notes` 的区别
- [x] 2 例数据两端 SHA-256 一致（232/232），Slicer 能打开 CT 看一眼
- [ ] `bash code/setup_check.sh` 能跑，输出清晰 PASS/WARN，缺命令显示 `MISSING` 而不崩
- [x] tmux 跑 5 分钟 `sleep`，detach 后 `tmux ls` 仍可见，attach 回来任务还在
- [ ] 能解释 `pip install` 后 `command not found`（PATH + venv + shell hash 缓存）
- [ ] 日志含当日报错原文，以及至少 1 条「Kilo 说 X，我核实是 Y」
- [ ] 当日 commit 完成，`journal/INDEX.md` D4 行已回填

## 今日完成

> 收尾时对照「今日要交付什么」逐行填写。

| 计划 | 状态 | 证据（文件/命令/commit） |
|---|---|---|
| 绝对/相对路径自测（4 题） | 进行中（笔记已写，终端复跑待做） | `notes/linux-cli.md` §1 新增自测表；首答 2/4 → 纠错后 4/4；`journal/day04.md` 卡点 1 + 易错点已记 |
| 2 例数据 scp + 校验 + 打开 CT | ✅ | `data/raw/lung1_smoke/` 2 例 232 个 `.dcm`、150M；两端 SHA-256 232/232 一致；Slicer 5.12.4 打开 CT（94 层） |
| 进程与资源（ps/top/kill/jobs） | ✅ | `notes/linux-cli.md` §10；`t12ub` 实测：`nproc=12`、load 0.03；`jobs` 三态；TERM 有 `got SIGTERM, cleaning up`、KILL 只有 `start`（退出码 137）；3A/3B/3C 与四组保命对照见「实验记录」 |
| tmux 长任务（含 5 分钟验收） | ✅ | 默认会话 `0` 改名为 `work`；`sleep 300` 运行中 `Ctrl+b d` detach → `tmux ls` 无 attached → `exit` 断 SSH → 重连 `attach` 仍在；`notes/linux-cli.md` §11 |
| 环境变量与 PATH 排错 | 待填 | |
| 写 `code/setup_check.sh` 并两端跑通 | 待填 | |
| 压缩与归档（tar/unzip） | 待填 | |
| 笔记与收尾 | 待填 | |

## 关键命令

> 边做边记：命令 + 实际输出要点，收尾时整理。输出留空处必须换成真实输出。

```bash
# ——【Mac】仓库：确认位置与现状 ——
pwd                                  # 预期 /Users/wangjiaqi/Desktop/实习日志
ls code logs                         # code/ 为空，今天新建 setup_check.sh

# ——【t12ub】建练习目录 ——
mkdir -p ~/d4-practice
cd ~/d4-practice
pwd                                  # 预期 /home/.../d4-practice
```

```bash
# ——【Mac】绝对/相对路径自测（先写答案，再敲命令验证）——
cd ~/Desktop/实习日志
pwd
cd notes && pwd                      # 相对：进入当前目录下的 notes
cd .. && pwd                         # 回仓库根
cd -                                 # 回上一个目录（notes）
cd ~                                 # 家目录
cd /                                 # 根目录；再 cd - 回来

# 1) 在 notes/ 下回仓库根：
cd ~/Desktop/实习日志/notes && cd .. && pwd
# 2) 在仓库根进 results/tables：
cd ~/Desktop/实习日志 && cd results/tables && pwd
# 3) 在 results/tables 下读 notes/git.md（相对路径）：
head -n 3 ../../notes/git.md
# 4) 用绝对路径读同一个文件，输出应完全一致：
head -n 3 ~/Desktop/实习日志/notes/git.md
# 结果：待填（4 题对几题）
```

```bash
# ——【t12ub】确认数据位置（只读）——
D=/home/jqw/.data/nsclc-radiomics/nsclc_radiomics
ssh t12ub "ls $D | wc -l"                    # 422 例
ssh t12ub "du -sh $D/LUNG1-308"              # 64M

# ——【Mac】拉 2 例到本地；data/raw/ 已被 .gitignore 忽略——
mkdir -p data/raw/lung1_smoke
scp -r t12ub:$D/LUNG1-308 data/raw/lung1_smoke/
scp -r t12ub:$D/LUNG1-001 data/raw/lung1_smoke/
du -sh data/raw/lung1_smoke                  # 150M
find data/raw/lung1_smoke -name '*.dcm' -type f | wc -l   # 232

# 两端 SHA-256 比对（Mac 用 shasum -a 256，Linux 用 sha256sum）
find data/raw/lung1_smoke -type f | sort | xargs shasum -a 256 | awk '{print $1}' | sort > /tmp/mac.sha
ssh t12ub "find $D/LUNG1-308 $D/LUNG1-001 -type f | sort | xargs sha256sum" | awk '{print $1}' | sort > /tmp/srv.sha
wc -l /tmp/mac.sha /tmp/srv.sha              # 232 / 232
diff /tmp/mac.sha /tmp/srv.sha && echo "哈希一致"

# ——【Mac】Slicer 看一眼 CT ——
open -a Slicer
# Add DICOM Data → 选 data/raw/lung1_smoke/LUNG1-308 → Import
# 选中 Modality=CT 的 series → Load，滚一圈确认能显示
```

```bash
# ——【t12ub】进程与资源 ——
ps aux | grep -i '[p]ython'          # 2 行：root 的 unattended-upgrade、xufumin 的 devpi-server；无 jqw
ps aux --sort=-%cpu | head -5        # 榜首百度网盘 %CPU 2.7 / TIME 543:36（平均值，非瞬时）
top -b -n1 | head -20                # load 0.03/0.05/0.01，302 tasks，id 96.8，wa 1.3
free -h; uptime; df -h ~             # 内存 3.3G 用 / 8.4G 可用；swap 用 2.7G；磁盘 3.5T 可用（6%）
nproc                                # 12 → load 0.03 约 0.25%，基本空闲

sleep 300                            # 前台，Ctrl+C → exit=130
sleep 300 &                          # [1] 1635730；PGID 独立，SID=shell，TTY=pts/1
jobs -l                              # Running
fg %1                                # 拉回前台，Ctrl+Z → Stopped
bg %1                                # 回 Running
kill %1                              # [1]+ Terminated；ps 空 + exit=1

# 先礼后兵（trap_demo.py 装了 SIGTERM 处理器）
kill %1                              # term.log：start + got SIGTERM, cleaning up；jobs=Done；exit=0
kill -9 "$PID"                       # kill9.log 只有 start；jobs=Killed；wait → exit=137

# 断线三组：手动 exit 不发 HUP（huponexit=off）
#   3A exit       → 存活 PPID=1 SID=旧shell TTY=?
#   3B 真断线     → DEAD exit=1
#   3C huponexit on + exit → DEAD exit=1
# 四组对照（一次 kill -HUP $$ 断线）：plain DEAD；nohup/disown 活（SID 不变）；setsid 活（SID=自身）
```

```bash
# ——【t12ub】tmux（今日重点）——
tmux ls                              # 0: 1 windows (created Tue Oct 20 17:25:43 2026) —— 默认名是数字
tmux rename-session -t 0 work        # 改名不影响进程
tmux list-windows -t work            # 0: bash* (1 panes) [81x29] ... (active)
tmux list-panes -t work -F '#{window_index}.#{pane_index} pid=#{pane_pid} tty=#{pane_tty} cmd=#{pane_current_command}'
                                     # 0:0.0 pid=1390256 tty=/dev/pts/4 cmd=bash

tmux attach -t work
#   会话内：sleep 300
#   Ctrl+b 松开后按 d  → detach
tmux ls                              # work: 1 windows ...（无 attached = 已 detach）
exit                                 # 彻底断开 SSH

# 重连后
tmux ls                              # work 仍在
tmux attach -t work                  # 回到 pane，sleep 仍在跑 → Ctrl+C
```

```bash
# ——【t12ub】tmux 机制证据 ——
ps -o pid,ppid,sid,tty,stat,cmd -p 1390255   # server：PPID=1、SID=自身、TTY=?、Ss
ps -o pid,ppid,pgid,sid,tty,stat,cmd -p 1390256  # pane bash：PPID=1390255、SID=自身、TTY=pts/4、Ss+
pgrep -a tmux                        # 混有 xufumin 的 wk 会话；用 pgrep -u "$USER" 过滤
```

```bash
# ——【t12ub】nohup 与日志 ——
nohup sleep 300 > ~/d4-practice/long_run.log 2>&1 &
jobs -l
tail -n 5 ~/d4-practice/long_run.log   # sleep 无输出 → 文件 0 字节
# 实测：kill -HUP $$ 断线后进程存活，SID 仍是旧 shell、TTY=?；见「信号与保命方式四组对照」
```

```bash
# ——【t12ub】环境变量与 PATH ——
echo $PATH | tr ':' '\n'
which python
type -a python
export MYVAR=test
echo $MYVAR
bash -c 'echo $MYVAR'                # 子进程可见
tail -n 3 ~/.bashrc                  # 服务器是 bash
source ~/.bashrc
# Mac 对应 ~/.zshrc；export 只影响当前会话及子进程
```

```bash
# ——【Mac】写脚本，【t12ub】跑 ——
cd ~/Desktop/实习日志
# 编辑 code/setup_check.sh（set -euo pipefail + 三个平台分支）
chmod +x code/setup_check.sh
bash code/setup_check.sh; echo "exit=$?"

# 缺命令场景（Linux）：临时把 PATH 缩小，确认输出 MISSING 而不是崩溃
PATH=/usr/bin:/bin bash code/setup_check.sh; echo "exit=$?"

# 服务器上跑同一份脚本（先 scp 过去）
scp code/setup_check.sh t12ub:~/d4-practice/
ssh t12ub 'bash ~/d4-practice/setup_check.sh; echo "exit=$?"'
# 输出要点：
```

```bash
# ——压缩与归档——
tar -czf /tmp/demo.tar.gz code notes
tar -tzf /tmp/demo.tar.gz | head   # 先看内容再解压
unzip -l /tmp/x.zip
# *.tar.gz / *.zip 已被 .gitignore 挡住，不放仓库
```

## 实验记录

### 路径实验（4 题）

| # | 题面 | 我的答案 | 实际命令 | 输出 | 对/错 |
|---|---|---|---|---|---|
| 1 | 在 `notes/` 下回仓库根 | `cd -`（以为回上级） | `cd ..` | `/Users/wangjiaqi/Desktop/实习日志` | ❌→✅ |
| 2 | 在仓库根进 `results/tables` | `cd /results/tables`（前导 `/` 变绝对路径） | `cd results/tables` | `.../results/tables` | ❌→✅ |
| 3 | 在 `results/tables` 下读 `notes/git.md` | `head -n 3 ../../notes/git.md` | 同左 | `# Git` + 说明两行 | ✅ |
| 4 | 用绝对路径读同一文件，结果是否一致 | 完全一致 | 两条 `head` 各跑一次 | 逐字相同 | ✅ |

结论：首答 2/4，纠错后 4/4。绝对路径从 `/` 数起、不随 `pwd` 变化；相对路径从当前目录数起，`..` 每层上跳一次。`cd -` 回的是 `OLDPWD` 不是上级，失败的 `cd` 不改变当前目录。

### 2 例数据冒烟

| 项 | 实测 |
|---|---|
| 例数 / 文件数 | 2 例 / 232 个 `.dcm` |
| 本地总大小 | 150M |
| 两端 SHA-256 | 一致（232/232） |
| 打开 CT | 能（Slicer 5.12.4，macOS amd64 / Rosetta） |

### 进程状态表

> 边做边填，只写实测到的。

| 场景 | 命令 | 关键输出 | 结论 |
|---|---|---|---|
| 查 python 进程 | `ps aux \| grep -i '[p]ython'` | 2 行：PID 1122 `root` `unattended-upgrade-shutdown`（RSS 6292KB）；PID 1318 `xufumin` `devpi-server`（RSS 1384616KB，%MEM 11.3）；均 `Ssl`、`TTY=?`；无 jqw | 自己没跑 python；两条都是别人的守护进程 |
| 后台作业 | `sleep 300 &` + `jobs -l` | `[1] 1635730`；`PGID=1635730`、`SID=1630611`（= shell）、`TTY=pts/1`、`S` | `&` 只改作业调度，未脱离会话 |
| 温和终止 | `kill %1`（trap_demo.py） | `jobs` 显示 `Done`；`term.log`：`start pid=...` + `got SIGTERM, cleaning up` | TERM 可捕获，处理器 `sys.exit(0)` → 退出码 0 |
| 强制终止 | `kill -9 1639587` | `jobs` 显示 `Killed`；`kill9.log` 只有 `start`；`ps` 空 + `exit=1`；`wait` → `137` | KILL 不可捕获，无清理机会 |
| 断 SSH 后 | 3A 手动 `exit` | 存活：`1640524 PPID=1 SID=1630611 TTY=? S` | `huponexit=off`，手动退出不补发 HUP |
| 断 SSH 后 | 3B 真断线（`pkill` / `kill -HUP $$`） | 空输出 + `exit=1` | 内核发 HUP → bash 转发给所有作业 |
| 断 SSH 后 | 3C `shopt -s huponexit` + `exit` | 空输出 + `exit=1` | 3A 的存活由开关造成，不是 `&` 有保护 |

### 信号与保命方式四组对照（2026-10-22）

同一次 `kill -HUP $$` 制造断线，四个进程用不同 `sleep` 时长区分：

| 方式 | 启动 | 断线前 SID / TTY | 断线后 |
|---|---|---|---|
| 普通 `&`（对照） | `sleep 311 &` | `1642851` / `pts/1` | **DEAD** |
| `nohup` | `nohup sleep 313 > long_run.log 2>&1 &` | `1642851` / `pts/1` | 存活 `1645929`，SID 不变、`TTY=?` |
| `disown` | `sleep 317 &` + `disown` | `1642851` / `pts/1` | 存活 `1645985`，SID 不变、`TTY=?` |
| `setsid` | `setsid sleep 319 > /dev/null 2>&1 &` | `1646044`（=自身）/ `?` | 存活 `1646044`，`Ss`、`PPID=1` |

结论：`nohup`/`disown` 让进程收不到或忽略 HUP，**会话归属没变**；只有 `setsid` 换了会话。

`nohup.out` 实测：不重定向时生成，`-rw-------`（0600）、0 字节（`sleep` 无输出），stderr 提示
`nohup: ignoring input and appending output to 'nohup.out'` 不进文件。

### nohup / tmux 对比

| 维度 | `nohup ... &` | `tmux` |
|---|---|---|
| 断 SSH 是否存活 | 是（忽略 HUP；实测四个进程里唯一 DEAD 的是普通 `&`） | 是（pane 的父进程是 tmux server，与 sshd 无关） |
| 能否重新接管/交互 | 不能，只能看日志文件 | 能，`attach` 回来继续操作、向上翻 scrollback |
| 输出落点 | `nohup.out` 或你指定的重定向文件（`nohup.out` 权限 0600） | pane 的 scrollback，可复制、可分屏 |
| 适用场景 | 一次性脚本、跑完只要结果 | 需要观察进度、中途交互、多任务并行（D17 用） |

### tmux 会话实测（2026-10-22）

| 项 | 实测 |
|---|---|
| 已有会话 | 默认名 `0`（`created Tue Oct 20 17:25:43 2026`），`1 windows`；`attach -t work` 报 `can't find session: work` |
| 改名 | `tmux rename-session -t 0 work` 成功，进程不变 |
| 窗口/pane | `0: bash* (1 panes) [81x29]`；`pane_pid=1390256`、`tty=/dev/pts/4`、`cmd=bash` |
| detach | `Ctrl+b` 松开再按 `d`；`tmux ls` 仍列出 `work`，无 `(attached)` |
| 断 SSH 后 | `exit` → 重连 → `tmux ls` 仍有 `work` → `attach` 回到 pane，`sleep 300` 仍在跑 |
| server | `1390255`：`PPID=1`、`SID=1390255`、`TTY=?`、`Ss` |
| pane shell | `1390256`：`PPID=1390255`、`PGID=1390256`、`SID=1390256`、`TTY=pts/4`、`Ss+` |
| 共享机发现 | `pgrep -a tmux` 混入 `xufumin` 的 `tmux -2 new-session -s wk`（`1431887`）；`pgrep -u "$USER"` 只剩自己的 `1390255` |

结论：pane 的父进程是 tmux server（`PPID=1390255`），server 又被 init 收养（`PPID=1`、无终端），
所以断 SSH 只销毁 sshd 的 pty，碰不到 tmux 的 pty；`attach` 回来连屏幕历史都在。

### `set -euo pipefail` 逐字解释

| 选项 | 作用 | 本地验证方式 |
|---|---|---|
| `-e` | | |
| `-u` | | |
| `-o pipefail` | | |

### PATH 排错流程（验收第 3 条）

> `pip install` 后 `command not found` 的三步排查，按顺序写实测结果。

1. `type -a <命令>`：待填
2. `echo $PATH | tr ':' '\n'`：待填
3. `hash -r` 后重试：待填

结论：待填

## 预判坑（待实测确认，未验证的不进结论）

| 计划里的写法 | 在 macOS 上的问题 | 替代写法 | 是否实际踩到 |
|---|---|---|---|
| `nproc` | 不存在 | `sysctl -n hw.ncpu` | 待填 |
| `top -b -n1` | 无 `-b` | `top -l 1 -n 10` | 待填 |
| `df -BG --output=avail` | GNU 专有 | `df -h ~` 或 `df -g` | 待填 |
| `source /etc/os-release` | 文件不存在 | `sw_vers -productVersion` | 待填 |
| 写 `~/.bashrc` | Mac 默认 zsh | `~/.zshrc` | 待填 |
| `scp -r src/ dst/` | 源目录尾斜杠影响是否复制目录本身 | 先 `scp -r src dst/`，再 `ls dst` 确认层级 | 待填 |

## 数据与合规边界（2 例数据冒烟）

> 数据冒烟是今天唯一触碰真实数据的环节，边界先写死。

- **许可**：数据为 CC BY-NC 3.0，仅限非商业用途；引用须署名并标注 DOI `10.7937/K9/TCIA.2015.PF0M9REI`。
- **只做什么**：下载、完整性校验、Slicer 打开看一眼 CT。
- **不做什么**：不重新识别患者，不做临床诊断，不给治疗结论，不写「可商用」「可替代医生诊断」。
- **不入 Git**：`data/raw/` 与 `*.dcm` 均在 `.gitignore` 中；提交前 `git status` 必须看不到影像文件。
- **不上传**：DICOM 数据不贴给任何在线服务或 AI 对话（包括 Kilo），只在本机与 `t12ub` 之间 `scp`。

## 卡点与报错（本节不许空着）

> 每个卡点必须六件齐全：现象（报错原文）、我的猜测、验证过程、根因、解决、下次怎么避免。收尾时删掉未使用的模板。

### 卡点 1：`cd /results/tables` 报 no such file or directory

- **现象**：
  ```text
  cd: no such file or directory: /results/tables
  ```
  （用 `zsh -c` 调用时前缀显示为 `zsh:cd:1:`，交互式终端不带前缀）
- **我的猜测**：以为前面加 `/` 只是"从仓库根开始找"。
- **验证过程**：`ls -d /results` 同样报 `No such file or directory`；改 `cd results/tables` 成功，`pwd` 为 `/Users/wangjiaqi/Desktop/实习日志/results/tables`。
- **根因**：以 `/` 开头即绝对路径，从文件系统根解析，与当前目录无关；系统根下没有 `results`。
- **解决**：相对路径不加前导 `/`，用 `cd results/tables`。
- **下次怎么避免**：敲路径前先看开头有没有 `/`；不确定就先 `pwd` + `ls` 确认相对基准。

### 易错点（非报错）：`cd -` 不是"回上级"

- **现象**：`cd -` 在"从仓库根进 `notes`"时确实回到仓库根，看起来和 `cd ..` 一样。
- **根因**：`cd -` 的目标是环境变量 `OLDPWD`（上一个目录），与目录层级无关；从 `~/Desktop` 直接进 `notes` 时它会回到 `~/Desktop`。
- **判定方法**：`cd -` 会打印目标路径，看它打的是不是你以为的目录。
- **结论**：回上级用 `cd ..`；`cd -` 只用于两个目录间来回跳。命令成功不代表规则正确。

### 卡点 2：`git add journal/day04.md` 报 pathspec did not match any files

- **现象**：
  ```text
  fatal: pathspec 'journal/day04.md' did not match any files
  ```
- **我的猜测**：以为 `git add` 的路径以仓库根为基准，与当前目录无关。
- **验证过程**：提示符为 `tables %`，`pwd` 在 `results/tables`；`git status` 把改动显示为 `../../journal/day04.md`、`../../notes/linux-cli.md`；`cd` 回仓库根后 `git add journal/day04.md notes/linux-cli.md` 成功，`git diff --staged --stat` 显示 2 files changed。
- **根因**：`git add` 的 pathspec 相对**当前工作目录**解析，不是相对仓库根；`results/tables/journal/day04.md` 不存在。
- **解决**：先 `cd /Users/wangjiaqi/Desktop/实习日志`，或用 `git add ../../journal/day04.md ../../notes/linux-cli.md`。
- **下次怎么避免**：提交前先 `pwd`；在子目录里操作时，直接复制 `git status` 输出的相对路径，或先 `cd` 回仓库根。

### 卡点 3：heredoc 终止符带尾随空格，提示符卡在 `>` 不返回

- **现象**：
  ```text
  jqw@t12ub:~/d4-practice$ cat > ~/d4-practice/trap_demo.py <<'EOF'
  > import os, signal, sys, time
  > ...
  > EOF
  >
  ```
  敲了 `EOF` 回车，提示符没有回到 `jqw@...$`，仍是 `>`，看起来像卡死。
- **我的猜测**：以为 `EOF` 已经结束了输入，是终端没刷新；又试了一次 `EOF`，仍然是 `>`。
- **验证过程**：按 `Ctrl+C` 退出后 `ls -l ~/d4-practice/trap_demo.py`，文件内容不完整；改用
  `printf '%s\n' '...' > trap_demo.py` 写文件，再用 `python3 -c "import ast; ast.parse(...)"` 验证语法通过。
  回头看粘贴的那行 `EOF`，末尾带了空格（截图里不可见）。
- **根因**：heredoc 的终止符必须**独占一行、从第 1 列开始、后面紧跟换行**；多一个空格或制表符就不匹配，
  bash 会一直停留在 PS2 续行状态（`>`），等待更多输入。
- **解决**：`Ctrl+C` 放弃本次输入；重新输入时确保 `EOF` 后无空格；或改用 `printf '%s\n' ... > 文件`
  这类不依赖终止符的写法。
- **下次怎么避免**：粘贴多行内容前先确认末行干净；`>` 提示符出现时先想到「还在等输入」，
  用 `Ctrl+C` 回到主提示符再重试，不要在 `>` 里继续敲命令（会被当作文件内容写进去）。

### 易错点（非报错）：`jobs -1` 把字母 `l` 敲成数字 `1`

- **现象**：`jobs -1` 报 `-bash: jobs: -1: invalid option`。
- **根因**：`jobs` 的长格式选项是小写字母 `l`，数字 `1` 不是合法选项；同一批命令里 `jpbs -l` 则是把 `jobs` 拼错。
- **判定方法**：报错里给出用法 `jobs [-lnprs] [jobspec ...]`，对照即可。
- **结论**：`jobs -l` 的 `l` 是 list；命令拼写错误不会影响已启动的后台进程，重敲正确命令即可。

## Kilo 使用记录

> 今日玩法：把 `code/setup_check.sh` 贴给 Kilo 做**代码评审**（不是让它生成代码）。

- 问：这个脚本在 Bash 3.2（macOS 自带）上会出问题吗？有没有注入或路径空格问题？答：待填。核实：待填。
- 问：`set -euo pipefail` 在 `[ ... ] && { ...; }` 这种写法下会不会提前退出？答：待填。核实：待填（实测命令 + 退出码）。
- **抓错记录 1**：Kilo 说「Slicer 有 macOS arm64 版，建议下 arm64 并计划 D13 前更换」；我核实下载页与包列表后确认 **5.12.4 / 5.13.0 的 macOS 包都只有 `amd64`**，没有 arm64 构建。结论：官方仅提供 amd64，Apple Silicon 上经 Rosetta 运行，不存在"待换 arm64"这项整改。

## 今日结论

> 收尾时补 3–7 条，只写验证过的结论；说不清为什么的结果标 `未验证`。

1. 待填
2. 待填
3. 待填

## 明日 3 件事

- [ ] 读 `每日计划/Day05.md`（SSH 全链路 + G1）。
- [ ] 复盘 `notes/SSH.md`，把今天 PATH/hash 的排错串进 SSH 免密与端口转发。
- [ ] 准备 G1 验收材料：笔记索引、`journal/INDEX.md` D1–D4 全绿、环境检查脚本可跑。
