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
2. 用 **2 例真实患者数据** 走一遍「服务器 → scp → 本地校验 → 3D Slicer 打开」的冒烟链路；**只看影像质量与元数据，不做诊断、不做重新识别**。

## 今日要交付什么

> 早上填写，收尾时逐项打勾并补证据；证据必须可复核。

| # | 交付物 | 具体要求 | 证据 | 状态 |
|---|---|---|---|---|
| 1 | 路径自测记录 | `notes/linux-cli.md` §1「绝对路径 vs 相对路径」补 4 题自测表与两个坑（`cd -`、前导 `/`） | 笔记 + 实际命令输出 | 进行中（笔记已写，终端复跑待做） |
| 2 | 2 例数据冒烟 | 从 `t12ub` `scp` 2 例 `LUNG1-*` 到 `data/raw/lung1_smoke/`，两端 SHA-256 一致；3D Slicer 能打开并记录 Series/层数/元数据 | 命令输出 + `results/figures/slicer_smoke/` 截图 | 待做 |
| 3 | `code/setup_check.sh` | 检查 OS/架构/CPU/磁盘/命令是否存在，输出 PASS/WARN，能处理 MISSING，退出码有意义 | 文件 + `bash code/setup_check.sh` 输出 | 待做 |
| 4 | `notes/linux-cli.md` 下半 | §10 进程、§11 tmux、§12 环境变量/PATH、§13 脚本、§14 压缩归档；标题由「（一）」改为通用 | 文件本身 | 待做 |
| 5 | `journal/day04.md` | 本文件：卡点须有报错原文/根因/解决，至少 1 条「Kilo 说 X，我核实是 Y」 | 本文件 | 进行中 |
| 6 | `journal/INDEX.md` D4 行 | 收尾回填日期（2026-10-22）、commit hash、验收结果 | `journal/INDEX.md` | 待做 |
| 7 | 当日 commit | ≥1 次，格式 `<scope>: <做了什么> - <一句话结论>` | `git log --oneline` | 待做 |
| 8 | 服务器练习目录 | `~/d4-practice/`（tmux、nohup、日志都放这里，**不写进仓库 `logs/`**） | `ls ~/d4-practice` | 待做 |

## 平台前提（今日命令分两处跑）

> 计划照 Linux 写；仓库在 Mac，练习在服务器 `t12ub`。

| 内容 | 位置 |
|---|---|
| 进程、kill、jobs、nohup、tmux、PATH、脚本实测 | `t12ub` |
| 写脚本、写笔记、commit | Mac 仓库 `/Users/wangjiaqi/Desktop/实习日志` |
| 5 分钟 sleep + detach/attach 验收 | `t12ub`（断 SSH 才能验证） |
| 2 例数据 `scp` 到本地 + SHA-256 校验 + Slicer 阅片 | Mac（数据落在 `data/raw/`，不入 Git） |

## 今日验收标准（收尾逐条核对）

- [ ] 4 道路径自测题全对，能解释 `cd ..` 与 `cd -`、`../notes` 与 `notes` 的区别
- [ ] 2 例数据两端 SHA-256 一致，Slicer 能打开；截图不含姓名/ID 等标识信息
- [ ] `bash code/setup_check.sh` 能跑，输出清晰 PASS/WARN，缺命令显示 `MISSING` 而不崩
- [ ] tmux 跑 5 分钟 `sleep`，detach 后 `tmux ls` 仍可见，attach 回来任务还在
- [ ] 能解释 `pip install` 后 `command not found`（PATH + venv + shell hash 缓存）
- [ ] 日志含当日报错原文，以及至少 1 条「Kilo 说 X，我核实是 Y」
- [ ] 当日 commit 完成，`journal/INDEX.md` D4 行已回填

## 今日完成

> 收尾时对照「今日要交付什么」逐行填写。

| 计划 | 状态 | 证据（文件/命令/commit） |
|---|---|---|
| 绝对/相对路径自测（4 题） | 进行中（笔记已写，终端复跑待做） | `notes/linux-cli.md` §1 新增自测表；首答 2/4 → 纠错后 4/4；`journal/day04.md` 卡点 1 + 易错点已记 |
| 2 例数据 scp + 校验 + Slicer 打开 | 待填 | |
| 进程与资源（ps/top/kill/jobs） | 待填 | |
| tmux 长任务（含 5 分钟验收） | 待填 | |
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
# ——【t12ub】先定位真实数据；路径按实际填，不确定就问，不要猜——
ssh t12ub 'ls -la ~/data/lung1 2>/dev/null || ls -la ~/d3-practice'

# ——【Mac】拉 2 例到本地；data/raw/ 已被 .gitignore 忽略——
mkdir -p data/raw/lung1_smoke
scp -r t12ub:<服务器路径>/LUNG1-001 data/raw/lung1_smoke/
scp -r t12ub:<服务器路径>/LUNG1-002 data/raw/lung1_smoke/
du -sh data/raw/lung1_smoke
find data/raw/lung1_smoke -name '*.dcm' -type f | wc -l

# 两端 SHA-256 比对（Mac 用 shasum -a 256，Linux 用 sha256sum）
find data/raw/lung1_smoke -name '*.dcm' -type f | sort | xargs shasum -a 256 | cut -d' ' -f1 | sort > /tmp/mac.hash
ssh t12ub 'find <服务器路径>/LUNG1-00{1,2} -name "*.dcm" -type f | sort | xargs sha256sum' | cut -d' ' -f1 | sort > /tmp/srv.hash
diff /tmp/mac.hash /tmp/srv.hash && echo "SHA-256 一致"

# ——【Mac】3D Slicer：只从官网下载——
# https://download.slicer.org → macOS 版 → 拖进 /Applications
open -a Slicer
# File → Add Data → 选 data/raw/lung1_smoke/LUNG1-001（DICOM 文件夹）
# 记录 Series 数、Modality、层数、Slice Thickness、Pixel Spacing
# 截图前确认界面不显示 PatientName / PatientID，图存 results/figures/slicer_smoke/
# 输出要点：
```

```bash
# ——【t12ub】进程与资源 ——
ps aux | grep -i python
top -b -n1 | head -20

sleep 300 &                          # 造一个可杀的进程
jobs -l
kill %1                              # 先礼
kill -9 <PID>                        # 后兵：换成真实 PID

# 输出要点：
```

```bash
# ——【t12ub】tmux（今日重点）——
tmux new -s work
#   会话内：sleep 300
#   Ctrl+b 松开后按 d  → detach

tmux ls
tmux attach -t work
#   回来确认 sleep 仍在跑；再退出用 exit
# 输出要点：
```

```bash
# ——【t12ub】nohup 与日志 ——
nohup sleep 300 > ~/d4-practice/long_run.log 2>&1 &
jobs -l
tail -n 5 ~/d4-practice/long_run.log
# 对比结论（nohup vs tmux）写进 notes/linux-cli.md §11
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

| 项 | 实测 | 证据 |
|---|---|---|
| 例数 / 每例 Series 数 | | `ls data/raw/lung1_smoke` |
| `.dcm` 文件总数 | | `find ... -name '*.dcm' \| wc -l` |
| 本地总大小 | | `du -sh data/raw/lung1_smoke` |
| 两端 SHA-256 是否一致 | | `/tmp/mac.hash` vs `/tmp/srv.hash` |
| Slicer 版本 | | `Slicer → About` |
| Modality / 层数 / Slice Thickness / Pixel Spacing | | Slicer Volumes / Info |
| 截图路径 | | `results/figures/slicer_smoke/` |
| 界面是否含姓名/ID | | 截图前肉眼确认 |

### 进程状态表

> 边做边填，只写实测到的。

| 场景 | 命令 | 关键输出 | 结论 |
|---|---|---|---|
| 查 python 进程 | `ps aux \| grep -i python` | | |
| 后台作业 | `sleep 300 &` + `jobs -l` | | |
| 温和终止 | `kill %1` | | |
| 强制终止 | `kill -9 <PID>` | | |
| 断 SSH 后 | 重连 + `ps` | | |

### nohup / tmux 对比

| 维度 | `nohup ... &` | `tmux` |
|---|---|---|
| 断 SSH 是否存活 | | |
| 能否重新接管/交互 | | |
| 输出落点 | | |
| 适用场景 | | |

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
| `open -a Slicer` | 应用名可能是 `3D Slicer` | `open -a "3D Slicer"` 或 Finder 启动 | 待填 |
| `scp -r src/ dst/` | 源目录尾斜杠影响是否复制目录本身 | 先 `scp -r src dst/`，再 `ls dst` 确认层级 | 待填 |

## 数据与合规边界（本日新增两项）

> 这两项是今天唯一触碰真实数据的环节，边界先写死。

- **许可**：数据为 CC BY-NC 3.0，仅限非商业用途；引用须署名并标注 DOI `10.7937/K9/TCIA.2015.PF0M9REI`。
- **只做什么**：下载、完整性校验、Slicer 打开、记录影像质量与元数据（层数、层厚、像素间距等）。
- **不做什么**：不重新识别患者，不做临床诊断，不给治疗结论，不写「可商用」「可替代医生诊断」。
- **不入 Git**：`data/raw/` 与 `*.dcm` 均在 `.gitignore` 中；提交前 `git status` 必须看不到影像文件。
- **截图去标识**：Slicer 界面若显示 PatientName/PatientID 等字段，先隐藏再截；做不到就不把截图入库。
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

### 卡点 2：待填

- **现象**：
  ```text
  ```
- **我的猜测**：
- **验证过程**：
- **根因**：
- **解决**：
- **下次怎么避免**：

### 卡点 3：待填

- **现象**：
  ```text
  ```
- **我的猜测**：
- **验证过程**：
- **根因**：
- **解决**：
- **下次怎么避免**：

## Kilo 使用记录

> 今日玩法：把 `code/setup_check.sh` 贴给 Kilo 做**代码评审**（不是让它生成代码）。

- 问：这个脚本在 Bash 3.2（macOS 自带）上会出问题吗？有没有注入或路径空格问题？答：待填。核实：待填。
- 问：`set -euo pipefail` 在 `[ ... ] && { ...; }` 这种写法下会不会提前退出？答：待填。核实：待填（实测命令 + 退出码）。
- 问：Slicer 截图里哪些字段算 PHI、必须隐藏？答：待填。核实：对照界面实际显示项确认，未核实前不截图入库。
- **抓错记录 1**：Kilo 说 X，我核实是 Y。待填（今日至少 1 条；计划里那 5 条平台差异是好素材，但必须实测过才算）。

## 今日结论

> 收尾时补 3–7 条，只写验证过的结论；说不清为什么的结果标 `未验证`。

1. 待填
2. 待填
3. 待填

## 明日 3 件事

- [ ] 读 `每日计划/Day05.md`（SSH 全链路 + G1）。
- [ ] 复盘 `notes/SSH.md`，把今天 PATH/hash 的排错串进 SSH 免密与端口转发。
- [ ] 准备 G1 验收材料：笔记索引、`journal/INDEX.md` D1–D4 全绿、环境检查脚本可跑。
