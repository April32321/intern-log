---
week: 1
days: D1–D5
dates: 2026-10-19 ~ 2026-10-23
gate: G1
written: 2026-10-27（D6 上午补交）
---

# 第一周复盘（D1–D5）：基础技能

> 范围：Markdown 笔记、Git、Linux CLI、SSH、Kilo 协作。
> 原则：只写能拿出证据的结论；没有证据的写「未验证」，不估算、不美化。

## 一句话结论

**手上功夫达标，收尾纪律是短板。** 55 个提交、5 篇日志、双端哈希与免密登录都能复核，
但 D5 的两项硬性收尾（`week1-review.md`、`INDEX.md` D5 行）拖到 D6 才补，38 个提交还没推送。
按《总纲》G1 未通过的兜底规则，今天上午先补 G1，D6 的 Kilo 任务顺延半天。

## 本周产出清点

| 项目 | 实际产出 | 证据 |
|---|---|---|
| 工作日志 | 5 篇（day01–day05），合计 1,503 行 | `journal/`、`wc -l journal/day*.md` |
| 本复盘 | `journal/week1-review.md` | 本文件 |
| 打卡表 | D1–D5 五行全部回填 | `journal/INDEX.md`、`2386fea` |
| 知识笔记 | 8 个文件；3 个有 W1 实质内容（markdown / git / linux-cli），SSH 偏薄，Conda/Docker 仍是占位 | `notes/`；`notes/linux-cli.md` 61 KB、`notes/SSH.md` 14 行 |
| 脚本 | `code/setup_check.sh`，60 行，两端可跑 | Mac 73 GB→`WARN`/exit=1；t12ub 3,533 GB→`PASS`/exit=0 |
| 环境证据 | `ssh-check.txt`，7 行/332 B | 仓库根；双端 SHA-256 一致 |
| 数据证据 | `results/tables/name_audit.csv`，31 行 | 30 个文件名中 27 合规、3 不合规 |
| 数据冒烟 | 2 例 / 232 个 `.dcm` / 150 MB | 双端 SHA-256 232/232 一致；Slicer 打开 CT（94 层） |
| 提交 | D1–D5 共 55 条；截至本文件 56 条 | `git rev-list --count 97eb53e^..567097d` |
| 凭据与数据入库 | 0 | `git ls-files` 无 `.dcm`、无 `data/raw/`、无 Key 文件 |

## 五个能力点自评

> 评分只对 W1 的验收动作负责：能做到且能复现 = 4–5 分；做得到但证据不全 = 3 分；
> 只会照抄 = 2 分以下。不用「感觉学会了」当证据。

### 1. Markdown 与笔记 —— 4/5

**做到的：**

- 5 篇日志结构完整：目标 → 交付表 → 关键命令 → 卡点原文 → Kilo 记录 → 结论 → 明日 3 件事。
- 代码块标了语言（`bash`/`text`/`diff`），表格用于实测矩阵，链接用相对路径。
- VS Code 预览快捷键实测并写进 `notes/markdown.md`：`Cmd+K` 松开再按 `V`；`Cmd+Shift+V` 全屏。
- 卡点不空：W1 日志里的报错都在本复盘汇总成 17 条（见下表），每条都有根因和「下次怎么避免」。

**扣分原因：**

- `journal/day04.md` 仍留 2 条「答：待填 / 核实：待填」（Kilo 代码评审那两问），违反「日志不留占位符」。
- 本复盘迟至 D6 才写，说明笔记体系里缺一个「周复盘」的固定收尾动作。
- 笔记厚薄不均：`notes/linux-cli.md` 61 KB，`notes/SSH.md` 只有 14 行通用内容。

### 2. Git 版本管理 —— 4/5

**做到的：**

- 55 条提交基本符合 `<scope>: <做了什么> - <一句话结论>`，且一个提交只做一件事。
  例外 2 条：`f77a4d2 day 04: …。`（scope 写成 `day 04`、缺结论段、句末多句号）与
  `f844aef docs: organize notes into notes folder`（无 ` - 结论`，中英混用）。
- 能演示 `git diff` / `git diff --staged` / `git log --oneline` / `git show <hash> --stat`。
- `git restore` 与 `git restore --staged` 都实测过，能说清「丢内容」与「只退暂存」的区别（day02）。
- 能解释「已推送用 `revert`、未推送才 `amend`/`restore`」，并知道冲突先 `git merge --abort`。
- 建过分支 `day02-notes` 并切回 `main`；D2 成功 `git push -u origin main`。
- `.gitignore` 挡住了 `data/raw/`、`*.dcm`、`.kilo/`；`git ls-files` 复核无影像文件。

**扣分原因：**

- **INDEX 回填不守时**：D4 行拖到 10-23（`804e099`），D5 行拖到 10-27（`2386fea`），晚了 4 天。
- **推送断档**：D2 之后没再 push，收尾时 `main` 领先 `origin/main` **38 条**。远程没有任何 D3–D5 记录。
- 有一次 `git add` 打错成 `cgit`，随后的 `git commit` 因暂存区为空而中止，但一度以为「提交了」（D6 补记）。

### 3. Linux CLI 与脚本 —— 4/5

**做到的：**

- 纯命令行完成「找文件 → 过滤 → 统计 → 存档」：30 个假 DICOM 名，`grep -E` 判合规、`awk` 出 CSV、`sort | uniq -c` 按患者计数。
- 权限能换算：`r=4/w=2/x=1`，`chmod 700`→`rwx------`，`644`→`rw-r--r--`；目录缺 `x` 时 `cd` 报 `Permission denied`（实测）。
- 管道与退出码：`2>&1 | tee` 后 `status=0`，开 `set -o pipefail` 恢复 `status=2`，三个值都实测。
- 进程与长任务：区分 `&` / `nohup` / `disown` / `setsid` / tmux；用 `SID`、`TTY`、`PPID` 判断进程是否会随终端死。
- tmux 验收：`sleep 300` 运行中 detach → 断 SSH → 重连 attach，任务仍在。
- 环境变量：`command not found` 四类排查（没装 / 不在 PATH / hash 旧路径 / 装进别的环境），`hash -r` 修复实测。
- 写出 60 行 `code/setup_check.sh`：缺命令输出 `MISSING` 不崩，`PASS/WARN` 退出码可区分，缩小 PATH 仍能跑完。
- 归档：`tar.gz` 33 K（含 `.DS_Store`）→ 排除后 32 K，解压后 `diff -r` 一致。

**扣分原因：**

- day04 的 4 道路径自测标「终端复跑待做」，验收框至今未勾（`journal/day04.md:46`）。
- `setup_check.sh` 的 150 GB 阈值对 Mac（73 GB）只报 `WARN`，没做成参数，换机器就得改脚本。
- `notes/linux-cli.md` 里有 2 条 awk 写法仍标「待验证」，没在 W1 内收口。

### 4. SSH 远程链路 —— 4/5

**做到的：**

- 免密有硬证据：`ssh -o BatchMode=yes t12ub 'hostname'` → `t12ub`，禁用了密码/口令交互。
- 先 `ssh -G t12ub` 核对生效配置：`jqw` / `192.168.18.87` / `10022` / `Desktop/jqw/id_rsa`，没有照抄计划里的 22 端口。
- `scp -P 10022` 往返成功；`rsync` 二次同步 39 considered / **0 transferred**。
- 双端 SHA-256 一致：`ssh-check.txt` 为 `8d5ebcc…`；README 为 `d90e80b…`。
- 端口转发：本机 8888 被 Jupyter 占用，改 `-L 8889:127.0.0.1:8888`，`curl -I` 返回 `200 OK`，收尾端口已释放。
- 能解释 `StrictModes` 下的权限链：家目录 750（组不可写）、`~/.ssh` 700、`authorized_keys` 600、私钥 600。

**扣分原因：**

- `notes/SSH.md` 没回填：仍是 14 行通用内容，10022、别名、BatchMode、隧道、权限链全散在 day05 日志里，笔记模块等于没交付。
- 没有实测 `ssh-keygen` 新建密钥流程（沿用现有 RSA 是合理决策，但「会生成/换密钥」这项没证据）。
- `~/.ssh/config` 的 `ServerAliveCountMax` 靠默认值生效，未显式写入，下次换机器容易漏。

### 5. Kilo 协作与证据意识 —— 3/5

**做到的：**

- 5 天里用 Kilo 做解释、脚本评审、日志分析与命令核对，没有一次批准 `sudo`、删文件、改仓库外文件。
- 明确标注的「抓错」共 5 条（day02 1、day03 3、day04 1），其中 4 条改变了实际操作。
- 已形成三条使用原则并写进 `notes/kilo.md`：先解释再执行、核对占位符、核对工作目录。

**扣分原因：**

- **Kilo 已装上并配好 API，但仓库里没有验收证据**：没有 `kilo-version.txt`、`smoke-test.txt`，没有 provider/model ID 记录，D6 的验收还没闭环，所以这项最高只能给 3。
- `notes/kilo.md` 只有 18 行原则，缺安装路径、版本、provider/model ID、TUI 命令表、Key 存放位置。
- D5 写的是「今日无」（`day05.md:379`），不是漏写；但 5 天只有 5 条抓错，D5 没有产出新记录，节奏偏松。
- day04 的两条 Kilo 评审记录仍是「待填」。

## G1 验收自检

| 验收项 | 证据 | 状态 |
|---|---|---|
| `ssh t12ub` 免密，`hostname`/`whoami`/`pwd` 正确 | `BatchMode=yes` → `t12ub`；`pwd` → `/home/jqw/work/intern-jqw-nsclc-survival` | ✅ D5 |
| `ssh-check.txt` 双端 SHA-256 一致 | 7 行/332 B；`8d5ebcc9…fdebba` | ✅ D5 |
| 能解释 700/600 与免密的关系 | day05「`700` / `600` 与免密登录的关系」小节 | ✅ D5 |
| `bash code/setup_check.sh` 能跑，能解释 `set -euo pipefail` | Mac `WARN`/exit=1；t12ub `PASS`/exit=0；day04 结论 6 | ✅ D4 |
| `journal/` 有 D1–D5 五篇 + 本复盘 | day01–day05 + `week1-review.md` | ✅（本文件 D6 补交） |
| `git log` ≥5 条规范提交 | D1–D5 共 55 条 | ✅ |
| 建仓库 / 推远程 | 沿用现有 `intern-log`，未从零 `git init`；D2 `9cd8942..6a1d45c` 推送成功，D3–D5 未再推 | ⚠️ 能力有证据，命名与推送纪律有偏差 |
| `journal/INDEX.md` D5 行回填 | `2386fea`（2026-10-27 补） | ✅（迟 4 天） |

**判定：G1 通过（补交后），附两项偏差记录：**

- **仓库命名**：实际用 `intern-log`，不是《总纲》的 `intern-<姓名>-nsclc-survival`；day01 已记录该决定，
  D20 前要么改名，要么在报告里说明。
- **推送断档**：D2 之后 D3–D5 的 37 条提交没推；加上今天的 INDEX 补交，收尾时共 38 条停在本机。
  「会推」有证据，「每天推」没有。

但「D5 当天全绿」这个事实不成立，记录在此，不修改历史。

## 报错原文汇总（17 条）

> 只统计**真实踩到**的报错。故意制造的实验不计入：`ls /no-such-path`（验证退出码）、
> `cd permtest`（验证目录缺 `x` 位）、`demo-cmd`（验证 PATH/`exit=127`）。

| # | 天 | 报错原文 | 根因 | 修复 / 证据 |
|---|---|---|---|---|
| 1 | D1 | `zsh:1: command not found: free`；`zsh:1: command not found: nproc` | 这两个是 Linux procps/coreutils 工具，macOS 不自带 | 改用 `sysctl -n hw.ncpu` / `hw.memsize` |
| 2 | D2 | `zsh: command not found: code` | macOS 版 VS Code 默认不把 CLI 装进 PATH | `open -a "Visual Studio Code"`；PATH 方案未执行 |
| 3 | D2 | `error: invalid option: -staged` | 长选项必须两个连字符，`-staged` 被拆成短选项组合 | 改 `git diff --staged` |
| 4 | D2 | ``zsh: parse error near `\n'`` | `<hash>` 里的 `<` 是 shell 重定向符，占位符不能原样粘贴 | 去掉尖括号：`git show ada6c39` |
| 5 | D2 | `git log -- oneline -10` 无输出、不报错 | 单独的 `--` 表示「选项结束」，`oneline`/`-10` 被当成路径 | 写成一个整体 `--oneline` |
| 6 | D2 | `\ No newline at end of file` | 原文件末尾缺 `\n`，`echo` 追加时把最后一行连写并补换行 | `tail -c 20 \| xxd` 确认末尾是 `22`；`git restore` 后保留末尾换行 |
| 7 | D3 | `ls: cannot access 'deep': No such file or directory` | 相对路径以当前目录为基准，`deep` 在 `sub/` 下 | `ls -l sub/deep` |
| 8 | D3 | `^[OA50: command not found` | 已经退出 `less` 回到 shell，上方向键的转义序列与 `50` 拼成命令名 | 进 `less` 后用 `/50` 搜索，`n`/`N` 跳转，`q` 退出 |
| 9 | D3 | 屏幕上 `No such file or directory`，但 `status=0` | 管道默认只取最后一条命令的退出码，`tee` 成功即 0 | `set -o pipefail` 后恢复 `status=2` |
| 10 | D3 | `ls audit \| grep -c '...{3}...'` → `0`（`-E` 下为 27） | 默认 BRE 不把 `{n}` 当量词，只当普通字符 | 用 `grep -E` 或写 `\{3\}` |
| 11 | D3 | `fatal: not a git repository (or any of the parent directories)` | 在 `~` 下执行 `git add journal/day03.md`，当前目录不是仓库 | 先 `cd ~/Desktop/实习日志`；命令本身没错，缺工作目录前提 |
| 12 | D4 | `cd: no such file or directory: /results/tables` | 前导 `/` 表示从文件系统根解析，与仓库根无关 | 用相对路径 `cd results/tables` |
| 13 | D4 | `fatal: pathspec 'journal/day04.md' did not match any files` | `git add` 的 pathspec 相对**当前工作目录**，当时在 `results/tables` | 回仓库根，或 `git add ../../journal/day04.md` |
| 14 | D4 | heredoc 已输入 `EOF`，提示符仍停在 `>` | 终止符必须独占一行、从第 1 列开始、后面无空格；粘贴的 `EOF` 带了尾随空格 | `Ctrl+C` 放弃；改用 `printf '%s\n' ... > file` |
| 15 | D4 | `-bash: jobs: -1: invalid option` | 长格式选项是小写字母 `l`，被敲成数字 `1` | `jobs -l` |

另外两条 D5 的报错单独列出（不属于「命令用法」类，而是环境假设类）：

| # | 天 | 报错原文 | 根因 | 修复 / 证据 |
|---|---|---|---|---|
| 16 | D5 | `ls: cannot access '/home/jqw/work': No such file or directory` | 计划假设 `~/work/<repo>` 已存在，实际服务器上没有仓库副本 | `mkdir -p ~/work/intern-jqw-nsclc-survival`，只放证据，不 `git init` |
| 17 | D5 | `bind [127.0.0.1]:8888: Address already in use` | `-L` 左侧是**本机**监听端口，8888 被本机 Jupyter（Tornado，PID 1083）占用 | 只改左侧：`-L 8889:127.0.0.1:8888`，`curl -I` 得 `200 OK` |

### 最耗时的三个坑

| 坑 | 为什么耗时 | 教训 |
|---|---|---|
| heredoc 终止符尾随空格 | 屏幕上看不出空格，提示符停在 `>` 像卡死；重敲 `EOF` 仍无效 | 粘贴多行内容前先确认末行干净；`>` 是 PS2，不是重定向 |
| 路径前导 `/` | `cd /results/tables` 报错信息像「目录不存在」，容易去查文件是否存在 | 先看路径开头有没有 `/`，再判断是绝对还是相对 |
| `rsync` 把 `.kilo/`、`plans20.zip` 传上服务器 | `.gitignore` 对 rsync 完全无效，远端一度 1.2 M | 传输层的排除必须显式 `--exclude`，先 `-n` 看清单 |

## Kilo 抓错记录（W1 累计 5 条）

| 天 | Kilo 说 | 我核实到 | 结论 |
|---|---|---|---|
| D2 | 示例直接给 `git show <hash>`、`git add notes/git.md`，未写前提 | 照抄分别报 `parse error` 与 `pathspec did not match` | 示例里的占位符和「先有改动/先有文件」的前提必须自己补齐 |
| D3 | `chmod +x` 后权限应为 `-rwxr--r--`（744） | 实测 `-rwxr-xr-x`（755），`+x` 默认作用于 u/g/o 三类 | `chmod u+x` 才是 744；`+x` 是 755 |
| D3 | 给命令时只标【Mac】，未写「先进入仓库」 | 在 `~` 下执行报 `fatal: not a git repository` | 命令正确 ≠ 可直接执行，工作目录是前提 |
| D3 | 说「基础正则也能用，因为没写 `{}`」，但给的命令含 `{3}`/`{2}` | `grep -c` 得 0，加 `-E` 或 `\{3\}` 才得 27 | 用 `{n}` 必须配 `-E` 或转义；Kilo 自述与命令自相矛盾 |
| D4 | 「Slicer 有 macOS arm64 版，D13 前换 arm64」 | 5.12.4 / 5.13.0 的 macOS 包只有 `amd64`，Apple Silicon 走 Rosetta | 不存在「待换 arm64」这项整改；AI 的版本信息必须回官方页面核对 |

D5 当天没有抓错记录，也没有写「今日无」——这是漏项，不是零错误。

## 下周改进的 2 件事

### 改进 1：把「收尾」变成每天最后一条命令

**问题**：D4/D5 的 INDEX 行都不是当天回填，D5 那条晚了 4 天；38 个提交还停在本机。
根因不是不会 Git，是收尾没有固定动作，靠「想起来」。

**做法**（17:30 固定执行，不看心情）：

```bash
cd ~/Desktop/实习日志
git status -sb                          # 先看有没有意外文件、ahead 几条
git diff --staged --stat                # 确认这次提交只做一件事
git add journal/dayNN.md journal/INDEX.md notes/<当天改的>.md
git commit -m "dayNN: <做了什么> - <一句话结论>"
git push
git log --oneline -3                    # 顶部必须是新 hash，第二行才是上一条
```

**验收标准（D6–D10 可逐条检查）：**

- 每个工作日结束时 `git status -sb` 显示 `ahead 0`，不把推送留到下周。
- `INDEX.md` 的日期等于当天日期；`git log --oneline` 里不再出现「次日回填 INDEX」的提交。
- 收尾 commit 必须同时包含当天的日志和 INDEX 行，缺一不算收尾。

### 改进 2：笔记与抓错当天归档，不再「先记日志、笔记以后补」

**问题**：`notes/SSH.md` 只有 14 行，D5 的 10022、别名、BatchMode、隧道、权限链全在日志里；
`notes/kilo.md` 只有 18 行原则；D4 还有 2 条「待填」。日志越来越厚，笔记模块却没长。

**做法：**

- 每天 16:30–17:30 把当天实测结论回填到对应 `notes/*.md`，只写「命令 + 实测输出 + 结论」，不抄教程。
- `notes/SSH.md` 下周补到 ≥60 行：端口 10022、`ssh -G` 解析、`BatchMode` 证明免密、
  `shasum -a 256` 与 `sha256sum` 的分工、`-L` 左右端含义、750/700/600 权限链。
- `notes/kilo.md` 随 D6 安装一起补齐：安装路径、版本、provider/model ID（**不含 Key**）、
  TUI 命令表（`/connect` `/models` `/status` `/agents`）、Key 存放位置、抓错清单。
- 每天至少 1 条「Kilo 说 X，我核实是 Y」；当天没有就写「今日无」，不留空。

**验收标准：**

```bash
wc -l notes/SSH.md notes/kilo.md                 # SSH ≥60；kilo 覆盖 D6 全部要点
grep -c "抓错" journal/day0[6-9].md journal/day10.md   # 每天 ≥1（含「今日无」）
grep -rn "待填" journal/ notes/                  # D10 前清零
```

D10 时抓错记录累计 ≥10 条（《总纲》4.2 的要求），且每条都有核实动作，不是只抄 AI 的话。

## 遗留问题（不阻塞 G1，但要在 D6–D7 清掉）

| 项 | 现状 | 处理 |
|---|---|---|
| `journal/day04.md` 路径自测 4 题的终端复跑 | 验收框未勾（`day04.md:46`、`:60`） | 补跑并勾选，或明确写「未验证」 |
| `journal/day04.md` Kilo 评审 2 条「待填」 | `day04.md:530-531` | 补答或删掉模板，不留空 |
| `notes/SSH.md` | 14 行通用内容 | 按改进 2 回填 |
| 未推送提交 | 38 条（D5 收尾时 37 条） | `git push` 后确认 `ahead 0` |
| D6 任务 | 安装/配置主体已做，证据与笔记未入库 | 冒烟测试 + 两个 txt + `notes/kilo.md` + `journal/day06.md` + INDEX D6 |

## 本周结论（只写验证过的）

1. **平台差异是最大的噪声源。** `free`/`nproc`/`code`/`top -b`/`sha256sum` 在 macOS 上都不可用或行为不同；
   先确认平台再敲命令，比报错后查半天快。
2. **屏幕有报错 ≠ 命令失败，屏幕没输出 ≠ 命令成功。** `2>&1 | tee` 会把 `status` 变成 0，
   必须 `echo $?` + `set -o pipefail`；反过来，`git log -- oneline` 静默返回空也不是「没有历史」。
3. **计划里的端口、路径、工具都是假设。** 22→10022、`~/work` 不存在、8888 被占、Slicer 只有 amd64——
   这四处全部靠开工前 `ssh -G`/`ls`/`lsof`/官网核对才发现，照抄会误判成网络或防火墙问题。
4. **证据链 = 文件 + 双端哈希 + 可重跑命令 + commit。** `ssh-check.txt` 332 B 本身不重要，
   重要的是同一哈希能在两端复算、生成命令能被人重跑。
5. **Git 的坑集中在四处：选项形态（`--`）、占位符（`<>`）、路径基准（cwd vs 仓库根）、工作目录。**
   W1 的 Git 报错全部落在这四类里，没有一条是「Git 本身难」。
6. **`.gitignore` 只管 Git。** `rsync` 和 `tar` 都不读它，`.kilo/`、`plans20.zip`、`.DS_Store`
   照样被传输或打包；排除规则必须在传输/归档层再写一遍。
7. **长任务是否随终端死，看 `SID`/`TTY`，不看 `&`。** `&` 只换 `PGID`；
   `nohup`/`disown` 只是绕过 HUP；只有换会话（`setsid`/tmux）才真正脱离。
8. **Kilo 的输出是草稿，不是结论。** 5 条抓错里有 2 条是「示例缺前提」而不是「知识错误」——
   这类错误最危险，因为命令看起来完全正确，复制就报错。
9. **日志写得厚，不等于笔记写得好。** day05 有 402 行，`notes/SSH.md` 只有 14 行；
   能力点自评时只能拿日志当证据，说明知识没有沉淀到该去的地方。
10. **最薄弱的环节是收尾，不是技术。** INDEX 迟填、笔记不回填、38 条未推送，
    都是「做完就停」造成的；下周把收尾做成固定命令，比多学一个工具更有价值。
