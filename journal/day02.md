---
day: 02
date: 2026-10-20
theme: Git 基础二（提交规范/撤销/远程）
gate: -
---

# Day 02｜Git 基础（二）：提交规范、撤销、远程

## 今日目标

从"能提交"升级到"**提交得干净、改错了能退、换台机器能拿到**"。

## 今日要交付什么

> 09:00–09:20 计划时段填写，收尾时逐项打勾并补证据。

| # | 交付物 | 具体要求 | 证据 | 状态 |
|---|---|---|---|---|
| 1 | 干净的提交历史 | ≥4 个提交；message 符合 `<scope>: <做了什么> - <一句话结论>`；一个提交只做一件事 | `git log --oneline` | ✅ |
| 2 | `notes/git.md` | 提交规范 + `diff`/`log` 四条命令 + 撤销四条命令 + `.gitignore` 语法；**不写冲突** | 文件本身 | ✅ 已合并 |
| 3 | `journal/day02.md` | 今日目标、完成表、卡点原文、关键命令、Kilo 抓错记录、明日 3 件事 | 本文件 | ✅ |
| 4 | 撤销演示 | 各执行一次 `git restore <file>` 与 `git restore --staged <file>`，能说清区别 | 命令输出 | ✅ |
| 5 | 分支练习 | `git switch -c day02-notes` → 提交一次 → `git switch main` | `git log --oneline --all` | ✅ |
| 6 | 远程同步 | `git push -u origin main` 成功；若失败，在日志写明原因 | 远程仓库页面 / 命令输出 | ❌ 未推送 |
| 7 | 收尾提交与打卡 | commit `day02: git 提交规范、撤销与远程 - <结论>`；`journal/INDEX.md` 补 D2 行 | `git log`、`journal/INDEX.md` | 待办 |

## 今日验收标准（收尾逐条核对）

- [x] 仓库里 ≥4 个提交，message 符合规范、粒度合理
- [x] 能演示 `git diff` 与 `git log --oneline`
- [x] 能演示一次 `git restore` 撤销，且说清它和 `git restore --staged` 的区别
- [ ] 远程 `push` 成功（或说明为何暂无远程）
- [x] 能解释 `git revert` 与 `git reset --hard` 的区别，并说明为什么**优先用 revert**
- [x] 会建分支并切回 `main`；知道遇冲突先 `git merge --abort`
- [x] 日志含当日报错原文，以及至少 1 条"Kilo 说 X，我核实是 Y"

## 今日完成

| 计划 | 状态 | 证据（文件/命令/链接） |
|---|---|---|
| 干净的提交历史 | ✅ | `git log --oneline`：D1 四条 + D2 三条（`4e8b79e`、`ada6c39`、`fcdf8c9`），另有 `f844aef` 整理 notes 目录；message 均符合 `<scope>: 做了什么 - 结论` |
| 写 `notes/git.md` | ✅ | 合并 `Git copy.md` 原内容与 scope 分类，补齐提交规范、`diff`/`log`、撤销、`.gitignore`、远程与易错点；重复文件已删除 |
| 补全 `journal/day02.md` | ✅ | 本文件：今日完成、关键命令、5 条卡点、Kilo 记录、7 条结论 |
| 演示 `git restore` 与 `--staged` | ✅ | `restore` 后 `working tree clean`；`restore --staged` 后显示 `Changes not staged for commit`，内容仍在 |
| 分支 `day02-notes` 建→提交→切回 | ✅ | `git log --oneline --all`：`3fb6902` 在 `day02-notes`，`main` 停在 `ada6c39` |
| `git push -u origin main` | ❌ 未完成 | `git status`：`ahead of 'origin/main' by 8 commits`，尚未推送 |
| 收尾 commit + 补 INDEX D2 行 | 待办 | `journal/INDEX.md` D2 行仍为空，收尾提交未做 |

## 关键命令

```bash
# 状态与历史
git status
git log --oneline -10
git log --oneline --all
git show ada6c39
git show ada6c39 --stat
git diff
git diff --staged

# 两次提交（一个提交只做一件事）
git add journal/day02.md
git commit -m "day02: 写入今日交付清单与验收标准 - 7 项交付待逐项验证"

git add notes/git.md
git commit -m "day02: 新增 git scope 速查 - 记录 6 类提交前缀的用途与示例"

# 撤销演示：工作区改动
echo "临时演示" >> notes/git.md
git diff
git restore notes/git.md
git status

# 撤销演示：取消暂存（内容保留）
echo "临时演示" >> notes/git.md
git add notes/git.md
git diff
git diff --staged
git restore --staged notes/git.md
git status
git restore notes/git.md
git status

# 分支练习
git switch -c day02-notes
touch notes/_branch-demo.txt
git add notes/_branch-demo.txt
git commit -m "day02: 分支练习 - 验证分支独立提交"
git switch main
git log --oneline --all

# 冲突原则（未触发）
git merge --abort
```

## 卡点与报错（本节不许空着）

### 卡点 1：`git diff -staged` 报 invalid option

- **报错原文**：

  ```text
  error: invalid option: -staged
  ```

- **我的猜测**：选项名写错了，但不确定单双横线有区别。
- **验证过程**：改成 `git diff --staged` 后正常输出暂存区 diff。
- **根因**：`--staged` 是长选项，必须两个连字符；`-staged` 被解析成短选项组合，git 没有这组选项。
- **解决**：用 `git diff --staged`（等价 `--cached`）。
- **下次怎么避免**：长选项统一写 `--`，短选项才是 `-`。

### 卡点 2：`git log -- oneline -10` 没有任何输出

- **现象**：命令不报错，但输出为空。
- **我的猜测**：以为 `--` 和 `oneline` 之间可以有空格。
- **验证过程**：改成 `git log --oneline -10` 后正常列出 8 条历史。
- **根因**：`--oneline` 是一个整体；单独一个 `--` 表示“选项结束，后面是路径”，于是 `oneline` 和 `-10` 被当成路径，匹配不到提交。
- **解决**：`git log --oneline -10`。
- **下次怎么避免**：长选项不拆开；`--` 只用于分隔路径，如 `git log --oneline -- journal/day02.md`。

### 卡点 3：`git show <ada6c39>` 触发 zsh 语法错误

- **报错原文**：

  ```text
  zsh: parse error near `\n'
  ```

- **我的猜测**：hash 写法不对。
- **验证过程**：去掉尖括号执行 `git show ada6c39`，正常显示 commit 元数据与 diff。
- **根因**：`<`、`>` 是 shell 的重定向符；`<hash>` 只是文档里的占位符写法，不能原样粘贴。
- **解决**：`git show ada6c39`。
- **下次怎么避免**：看到 `<文件名>`、`<hash>`、`<分支名>` 一律替换成实际值并去掉尖括号。

### 卡点 4：macOS 上 `code` 命令不存在

- **报错原文**：

  ```text
  zsh: command not found: code
  ```

- **我的猜测**：以为 `code` 只有 Windows 能用。
- **验证过程**：改用 `open -a "Visual Studio Code" notes/git.md` 能正常打开；查证后确认 `code` 是 VS Code 自带 CLI，只是没加入 PATH。
- **根因**：macOS 版 VS Code 默认不安装命令行工具，Windows 安装器才会自动勾选。
- **解决**：VS Code 里 `Cmd+Shift+P` → `Shell Command: Install 'code' command in PATH`；临时用 `open -a`。
- **下次怎么避免**：报 `command not found` 先查工具是否安装、是否在 PATH，不要归因于操作系统。

### 卡点 5：`echo >>` 后 diff 显示最后一行被改写

- **现象**：追加一行，diff 却显示最后一行“删除 + 新增”，并出现：

  ```text
  \ No newline at end of file
  ```

- **我的猜测**：以为 git 把追加误判成修改。
- **验证过程**：`tail -c 20 notes/git.md | xxd` 显示文件末尾是 `22`（`"`），没有 `0a`（换行符）。
- **根因**：原文件末尾缺换行，`echo` 追加时把内容接在最后一行后面并补上换行，导致该行内容变化。
- **解决**：`git restore notes/git.md` 恢复；后续保存文件保留末尾换行。
- **下次怎么避免**：文本文件以换行结尾；追加前先确认 `tail -c 1` 是否为 `0a`。


## Kilo 使用记录

- 问：`git diff -staged` 为什么报错。答：长选项要用 `--`。核实：改为 `--staged` 后正常输出，解释与现象一致。
- 问：`git log -- oneline -10` 为什么为空。答：`--` 后内容被当作路径。核实：改为 `--oneline` 后输出 8 条历史，一致。
- 问：`git show <ada6c39>` 为什么 parse error。答：尖括号是占位符/重定向符。核实：去掉尖括号后正常显示 commit 与 30 行 diff，一致。
- 问：74 行的 `day02.md` 提交算不算“大提交”。答：按“一个提交一件事”判断，不看行数。核实：`git log --stat` 显示该提交只含 `journal/day02.md` 一个文件、单一目的，符合粒度要求。
- 问：`git show ada6c39 --stat` 与不带 `--stat` 的区别。答：前者只给文件与增删行摘要。核实：输出 `1 file changed, 30 insertions(+)`，与完整 diff 结论一致。
- **抓错记录**：Kilo 在示例中直接给出 `git add notes/git.md` 和 `git show <hash>` 两条命令，我照抄时前者因文件尚未创建会报 `pathspec` 错误，后者报 `parse error`。核实后确认：示例中的 `<hash>` 是占位符，且 `git add` 的前提是文件已经存在并修改过——命令必须结合当前仓库状态执行，不能机械粘贴。

## 今日结论

1. 提交粒度看“是否只做一件事”，不看行数：今天 `4e8b79e`（写入交付清单）与 `ada6c39`（scope 速查）各自单一目的，`day02-notes` 上的 `3fb6902` 也只做分支验证。
2. Git 选项有三条硬规则：长选项是 `--xxx` 整体、单独的 `--` 表示后面是路径、`<...>` 是占位符不是命令。
3. 暂存区三态已能区分：`git diff` 看工作区 vs 暂存区，`git diff --staged` 看暂存区 vs HEAD；`restore` 丢内容，`restore --staged` 只退暂存、内容保留。
4. 撤销原则：已推送的提交只 `revert`（新增一个反向提交、不改写历史），不 `reset --hard`（移动分支指针并丢弃工作区/暂存区改动，已推送时会造成他人历史不一致）；未推送的才用 `restore` / `amend` 处理。遇到合并冲突先 `git merge --abort` 回到干净状态，不现场硬解。
5. 文件末尾换行会影响 diff 可读性；保留末尾换行能避免“最后一行被改写”的假象。
6. `notes/git.md` 已合并 `Git copy.md` 的内容，现覆盖核心概念、提交规范、基础操作、`diff`/`log`、撤销、`.gitignore`、分支、合并、远程与易错点；重复文件 `Git copy.md` 已删除，待提交。
7. 当前状态：`main` 在 `f844aef`，`day02-notes` 在 `3fb6902` 未合并；本地领先 `origin/main` 8 个提交，尚未 push；`INDEX.md` 的 D2 行待收尾回填。

## 明日 3 件事

- [ ] 读 `每日计划/Day03.md`。
- [ ] 完成 Linux CLI 一（文件/权限/管道）练习。
- [ ] 写 `notes/linux-cli.md` 上半，补 `journal/INDEX.md` D3 行。
