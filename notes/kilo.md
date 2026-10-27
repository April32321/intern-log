# kilo

AI 编程助手 CLI 工具，帮助完成软件开发任务。

## 说明

- 通过命令行与 AI 交互，执行代码编写、调试、重构等任务
- 支持配置：`.kilo/` 目录、`kilo.json`、`AGENTS.md`
- 使用 `/help` 获取帮助
- 反馈：https://github.com/Kilo-Org/kilocode/issues

## 使用原则（来自实操）

- **先解释再执行**：让 Kilo 逐段说明命令在做什么，自己能复述后才运行
- **核对占位符**：`<hash>`、`<文件名>`、`<分支名>` 是占位符，原样粘贴会被 shell 当重定向符
- **核对工作目录**：命令没写清 `cd` 时，先 `pwd` 确认在仓库/目标目录内
- **自己复核结果**：用 `ls`、`wc -c`、`git status` 等输出验证 Kilo 的说法；无法解释的结果标 `未验证`
- 每天至少记录 1 条“Kilo 说 X，我核实是 Y”

## 提示词模板（D7，贯穿 D7–D20）

三类模板对应三种工作状态：**先懂（解释型）→ 先约（执行型）→ 先审（审查型）**。
共同原则：解释型不落盘、执行型必须先看计划、审查型禁止它直接改文件。

### 1. 解释型（学概念 / 读报错 / 读陌生代码）

> 用不超过 8 行解释 <概念>，给一个最小可运行例子，并指出最常见的 3 个误用。

使用要点：

- 8 行是硬约束，逼它讲主线而不是复述文档
- 例子要自己跑一遍，跑不通说明它在编
- 高频对象：`bind mount`、`parquet`、`nohup`、`permission`、`--auto`

### 2. 执行型（要动文件 / 要联网 / 要跑命令）

> 先给出不超过 10 步的执行计划，标出每步会写哪些文件、是否需要联网；我确认后再执行。

使用要点：

- 计划里出现写 `data/`、`results/`、`.git/`、`~/.config/` 就先停下来问
- 标了“需要联网”的步骤，要和容器里的 `--network none` 一起考虑
- 它跳过计划直接动手 = 立刻打断，切回只读 agent 重来

### 3. 审查型（review 脚本 / diff / 结果）

> 这是我的 <脚本/diff/结果>，请只做评审：列出 必须修改 / 建议修改 / 可以保留 三组，不要直接改文件。

使用要点：

- 明确“不要直接改文件”，否则它会顺手改完，自己就失去判断机会
- 三组之外的意见一律不采纳，防止用“顺便优化”扩权
- 结论要落到自己的判断：哪条采纳、哪条拒绝、为什么

### 组合用法（本项目常见链路）

| 场景 | 链路 |
|---|---|
| 读 `code/setup_check.sh` | 解释型（先懂每段）→ 审查型（提改进）→ 自己决定改不改 |
| 写新脚本 | 执行型（先看计划）→ 自己确认 → 执行 → 审查型（复核 diff） |
| 查事实（数据集、DOI、版本号） | 正常提问 → **官方页面核对** → 记录“它说 vs 官方说” |

## 安装与配置（D6，t12ub）

- 安装：`npm install -g @kilocode/cli`，目录 `~/.npm-global/lib/node_modules/@kilocode`
- 版本：**7.8.18**（`kilo --version`，证据 `kilo-version.txt`）
  - 当天 10:30 曾记录 7.8.17，10:52 复核为 7.8.18，已用新版本重跑冒烟
- 模型：`deepseek/deepseek-flash`（`kilo models deepseek` 可见）
  - 冒烟：`kilo run --auto -m deepseek/deepseek-flash "只回复 KILO_OK"` → `KILO_OK`
  - tool calling：让它执行 `echo TOOL_OK`，命令实际运行并返回 `TOOL_OK`
- 工作目录：`~/work/intern-jqw-nsclc-survival`（启动 TUI 前先 `pwd`）

### TUI 常用命令

| 命令 | 作用 |
|---|---|
| `/connect` | 选 provider 并授权 |
| `/models` | 选支持 tool calling 的模型 |
| `/status` | 确认目录、模型、会话 |
| `/agents` | 切换 primary agent（只读 / 可写） |

### 凭据位置

- 配置：`~/.config/kilo/kilo.jsonc`（无 Key）
- 凭据：`~/.local/share/kilo/auth.json`（`-rw-------` 600）
  - `kilo auth list` → Kilo Gateway (oauth) + DeepSeek (api)
  - `grep -oE 'sk-...' auth.json | wc -l` = 1：DeepSeek Key 存在该文件，不在仓库
  - 命令历史里的 `sk-` 命中均为检查命令自身，无真实 Key
- 会话库：`~/.local/share/kilo/kilo.db`（644，含会话记录，不入库）
- `kilo/` 前缀走托管 Gateway（无额度报 `Add credits`）；`deepseek/` 走自己的 API Key

## agents 权限（D6，t12ub Kilo 7.8.18 实测）

`/agents` 切换的是 primary agent；写权限由工具调用层强制，不靠提示词约束。

| agent | write / edit | bash | 结论 |
|---|---|---|---|
| `code` | 允许（继承全局默认） | 按全局配置 | 写业务文件必须用它 |
| `plan` | 默认 deny，仅放行 `plans/*.md`、`.kilo/plans/*.md`、`.plans/*.md` | 只读命令 allow，其他 ask | 受限写，不能改代码 |
| `ask` | write/edit/notebook 全 deny | 只读白名单 allow，其他 ask | 纯查询，不能写 |

- deny 是硬拒绝，模型想写也会被权限层挡住，点同意绕不过。
- 切换：`/agents`、`<leader>a` 或 Tab/Shift+Tab；本项目 `.kilo/agent/` 不存在，走内置权限。
- 实测命令：`kilo agent list`。

### TUI 证据（D6）

- `logs/day06-tmux-status.txt`：状态栏 `~/work/intern-jqw-nsclc-survival 7.8.18`，
  当前 agent `Code`，模型显示名 `DeepSeek V4.1 Flash 1017`（ID `deepseek/deepseek-flash`）
- `logs/day06-tmux-ls.txt`：`kilo` 会话创建于 2026-10-27 11:05，`attached`
- 未单独截 `/status` 面板；目录、模型、版本由 TUI 状态栏与输入行证明
