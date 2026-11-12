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

## 实战：审查 setup_check.sh（D7）

用审查型模板做了**静态审查**（未执行脚本），按三组给结论。

### 必须修改

1. **缺关键命令仍然 `RESULT: PASS`**（43–50 行）。`for` 循环只打印 `MISSING`，从不置 `fail`：`git`/`conda`/`docker`/`kilo` 全缺也会 PASS 并 `exit 0`。
   改法：关键依赖缺失时置 `fail`，结果分 `PASS` / `WARN`（空间）/ `FAIL`（缺依赖）。
2. **`avail` 未做数字校验**（29–37 行）。`df -g` 失败时 `avail` 为空，第 35 行打印 `${avail:-unknown}`，第 37 行只判 `-n`，于是 `[ "unknown" -lt 150 ]` 报 `integer expression expected`；该错误在 `if` 条件里被吞掉，直接落到 `RESULT: PASS`，**磁盘检查静默失效**。
   改法：比较前用 `case "$avail" in ''|*[!0-9]*)` 归一，无法解析按 WARN 处理。

### 建议修改

- 磁盘对象写死 `$HOME`；数据在 `~/.data`，D8 起镜像与 build cache 也占空间 → 改成 `target="${1:-$HOME}"`。
- `command -v docker` 只证明有二进制，不证明 daemon 活着 → 加 `docker info >/dev/null 2>&1`。
- 输出加 `date -Iseconds`、主机名，便于直接 `tee logs/`。
- 退出码分级 0 / 1 / 2，别让“空间不足”和“缺依赖”共用 1。

### 可以保留

- `set -euo pipefail`，以及用 `if avail="$(...)"` 包住可能失败的命令（裸赋值会让 `set -e` 直接退出）。
- Darwin / `/etc/os-release` 双分支探测 OS。
- 用 `command -v` 而不是 `which`。
- `printf '%-24s'` 对齐，无副作用、可重复执行。

### 采纳判断

| 条目 | 判断 | 理由 |
|---|---|---|
| 必须修改 1（缺依赖影响结果码） | 采纳 | 直接影响 PASS 可信度，D8 装 Docker/Kilo 前必须先修 |
| 必须修改 2（磁盘数值校验） | 采纳 | 否则检查失效仍报 PASS，违背脚本用途 |
| `docker info` | 采纳 | D8 要真跑容器，daemon 未启动是最常见坑 |
| 磁盘目标可配 | 暂缓 | D8 真正 build 镜像时再按实际路径改 |
| 联网检查 | 不采纳进本脚本 | 保持脚本离线可用，D8 在容器里单独验 |

- 改脚本留到 D8 前做，避免今天把评审和改动混进同一个 commit。

## 事实核查：TCIA NSCLC-Radiomics（D7）

先凭记忆作答，再查官方页面，最后用 Crossref 交叉验证。

| 问题 | 首答（未查证） | 官方来源 | 结论 |
|---|---|---|---|
| 患者数 | 422 例 | 422 subjects | ✅ |
| 数据集 DOI | 10.7937/K9/TCIA.2015.PF0M9REI | 同左（Version 4，2020/10/22） | ✅ |
| 论文 DOI | 10.1038/ncomms4006 | **10.1038/ncomms5006** | ❌ 差一位 |
| 体量 | 约 35.8 GB | 35.78 GB / 1,265 series / 52,073 images | ✅ |
| 许可 | CC BY-NC 3.0 | CC BY-NC 3.0 | ✅ |

- 官方页面：https://www.cancerimagingarchive.net/collection/nsclc-radiomics/
- Crossref：`10.1038/ncomms5006` → Aerts et al. 2014《Decoding tumour phenotype by noninvasive imaging using a quantitative radiomics approach》；`10.1038/ncomms4006` → 另一篇《Predicting network functions with nested patterns》，与影像组学无关。
- **差一位的 DOI 格式合法、`doi.org` 也能解析**，是最难自查的错误类型；引用前先 `curl -sI https://doi.org/<doi>` 解析一次。
- 三个易混数字：**1,019** 是论文里肺 + 头颈合计队列；本 collection **422** 例；其中 LUNG1-128 为术后病例、无 GTV-1，可做 GTV-1 特征的是 **421** 例（官方 Version 3 说明，推断值）。
- 数据集 DOI 可直接引用；论文 DOI 必须写 `10.1038/ncomms5006`。

## VS Code 扩展：远程 SSH 主机安装（2026-11-12 实测，t12ub / pvmed-190）

### 1. 两个东西别混

| 形态 | 装法 | 落点 |
|---|---|---|
| Kilo **CLI**（`kilo` 命令） | `npm install -g @kilocode/cli` | `~/.npm-global/bin/kilo`（D6 已装 7.8.18） |
| Kilo Code **VS Code 扩展** | 扩展市场，ID `kilocode.kilo-code` | 本地 `~/.vscode/extensions/`；远程 `~/.vscode-server/extensions/` |

问「怎么装 kilo」先确认要哪个，两者互不替代。

### 2. 远程窗口必须装在「远程扩展宿主」

扩展声明为 workspace 类型，SSH 窗口里本机那份会被禁用：

> 此扩展在此工作区中被禁用，因为其被定义为在远程扩展主机中运行。请在 'SSH: t12ub' 中安装扩展以进行启用。

即扩展跑在服务器上，装到 `~/.vscode-server/extensions/`，本机那份不参与该窗口。

### 3. 平台专用包

7.8.x 的包按平台分发（内含 Playwright/Chromium 二进制，500 MB 量级）：

```text
darwin-arm64  darwin-x64  linux-x64  linux-arm64  alpine-x64  alpine-arm64  win32-x64  win32-arm64
```

| 主机 | 需要 | 实测 |
|---|---|---|
| Mac（Apple Silicon） | `darwin-arm64` | `kilocode.kilo-code-7.8.27-darwin-arm64` |
| t12ub / pvmed-190（Ubuntu 24.04, x86_64） | `linux-x64` | `kilocode.kilo-code-7.8.28`（手动 VSIX 无后缀） |

市场 API 里每个平台是 `versions[]` 的**独立条目**，`versions[0]` 不等于「最新版」。

### 4. 报错排查：四层证据

现象（t12ub）：

- UI 点「在 SSH: t12ub 中安装」→ `无法安装“kilocode.kilo-code”扩展，因为它不兼容。`
- 集成终端跑 `remote-cli/code --install-extension` → `No extension gallery service configured.`

逐层实测：

| 层 | 命令 | 结果 | 判断 |
|---|---|---|---|
| 版本 | 扩展 `engines.vscode` vs server | `^1.105.1` vs `1.145.1` | 满足 |
| 架构 | `uname -m` | `x86_64`，市场有 `linux-x64` | 满足 |
| 两端一致性 | client / server `product.json` 的 `commit` | 都是 `6bab64e2…` | 一致 |
| server gallery 配置 | `grep -A8 extensionsGallery <server>/product.json` | `serviceUrl` 完整 | 未损坏 |
| client gallery 配置 | 本机 `product.json` | 同上 | 未损坏 |
| 市场 API | POST `extensionquery` | `200` + 返回 Kilo 元数据 | 通 |
| 控制配置 | `main.vscode-cdn.net/extensions/marketplace.json` | `200` | 通 |
| 误导项 | GET `/_apis/public/gallery`、`www.vscode-unpkg.net` | `404` | **正常**，POST-only / 无根路径，不能当失败证据 |

结论：两处报错都不是字面原因；同一窗口的扩展视图还显示「登录以访问扩展市场」，说明**该远程窗口的 gallery 服务状态异常**（排除法结论，未从源码坐实）。`Reload Window` / `Kill VS Code Server on Host` 可尝试恢复，不保证。

方法论：报错文案不能直接当归因——先证伪「版本/架构」，再证伪「配置」，最后用真实 API 调用证伪「网络」，剩下的才是窗口状态。

### 5. 离线安装 VSIX（确定性路径）

市场 `vspackage` 直链返回 **gzip 流**，必须先解压：

```bash
curl -L -o kilo.gz "https://marketplace.visualstudio.com/_apis/public/gallery/publishers/kilocode/vsextensions/kilo-code/7.8.28/vspackage?targetPlatform=linux-x64"
file kilo.gz              # gzip compressed data（正常）
gunzip -c kilo.gz > kilo.vsix
file kilo.vsix            # Zip archive data（必须是这个）
unzip -l kilo.vsix | tail -2
```

实测 7.8.28 `linux-x64`：磁盘 144 MB，解压后 578,547,266 B / 1399 个文件。

安装：远程窗口 `Cmd+Shift+P` → **扩展: 从 VSIX 安装…** → 文件框浏览的是**远端**文件系统 → 输入 `/home/<user>/kilo.vsix` → `Developer: Reload Window`。

验证：

```bash
ls -d ~/.vscode-server/extensions/kilocode.kilo-code-*
jq -r '.version, .__metadata.targetPlatform' ~/.vscode-server/extensions/kilocode.kilo-code-7.8.28/package.json
```

### 6. 踩坑

| 现象 | 根因 | 处置 |
|---|---|---|
| 远端 `code --install-extension` 报 `No installation of Visual Studio Code stable was found` | PATH 里的 `code` 是 `~/.local/bin/code`（微软独立 CLI），不是远程 CLI | 用 `~/.vscode-server/bin/<commit>/bin/remote-cli/code`，且必须在**集成终端**里跑 |
| 把路径填进扩展搜索框 | 搜索框只做市场关键词搜索 | 用命令面板 `扩展: 从 VSIX 安装…` |
| 选的 `.vsix` 其实是 gzip | 市场直链返回 gzip 流 | `gunzip -c` 后装解压出来的 zip |
| `.../extension/package.json` 不存在 | 安装时剥掉 VSIX 内的 `extension/` 层，目录是扁平结构 | 读 `~/.vscode-server/extensions/<id>-<ver>/package.json`；只有 VSIX **包内**才有 `extension/` 前缀 |
| `.__metadata.targetPlatform` 为 `undefined` | 手动安装不写市场元数据 | 不影响运行；用 `file bin/*` 确认 `ELF 64-bit x86-64` |
| 目录名有的带 `-linux-x64` 有的不带 | 手动 VSIX 安装不按平台改名 | 匹配目录别写死后缀 glob |

### 7. 升级 SOP（任意 linux 远端）

```bash
# 1) 查最新 linux-x64 版本
curl -sS -X POST 'https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery' \
  -H 'Content-Type: application/json' -H 'Accept: application/json;api-version=7.2-preview.1' \
  -d '{"filters":[{"criteria":[{"filterType":7,"value":"kilocode.kilo-code"}]}],"flags":914}' -o /tmp/q.json
jq -r '.results[0].extensions[0].versions[] | select(.targetPlatform=="linux-x64") | .version' /tmp/q.json | head -3

# 2) 下载 → 解压 → 校验
V=<版本>
curl -L -o kilo.gz "https://marketplace.visualstudio.com/_apis/public/gallery/publishers/kilocode/vsextensions/kilo-code/$V/vspackage?targetPlatform=linux-x64"
gunzip -c kilo.gz > kilo.vsix && unzip -l kilo.vsix | tail -2

# 3) 远程窗口：扩展: 从 VSIX 安装 → Reload Window → 验证目录
```

- 扩展不会自动更新，直到该窗口的市场通道恢复；恢复办法是 `Remote-SSH: Kill VS Code Server on Host` 后重连，让它重拉与客户端同 commit 的 server。
- 本机（Mac）保留 `darwin-arm64` 版本，与远端并存，不冲突，不必卸载。
