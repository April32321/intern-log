---
day: 01
date: 2026-10-19
theme: 开工、Markdown 笔记体系、Git 基础（一）
gate: -
---

# Day 01｜开工、Markdown 笔记体系、Git 基础（一）

## 今日目标

- 在现有 `intern-log` 仓库中建立 `journal/ notes/ env/ data/ code/ results/ logs/` 目录骨架。
- 完成本机环境盘点，并把结果写入本日志。
- 完成 `README.md`、`notes/markdown.md`、`journal/INDEX.md` 和本日志，提交第一个 commit。

## 环境盘点

| 项目 | 结果 |
|---|---|
| 主机名 | `AprilMacBook-Pro.local` |
| 当前用户 | `wangjiaqi` |
| 仓库路径 | `/Users/wangjiaqi/Desktop/实习日志` |
| 系统 | macOS 14.6.1（Build 23G93） |
| 内核/架构 | Darwin 23.6.0，arm64 |
| CPU | 8 核 |
| 内存 | 16 GiB（17179869184 bytes） |
| 家目录磁盘 | 总 460 GiB，已用 362 GiB，可用 **71 GiB**（84%） |

> 风险记录：可用空间 71 GiB，低于《总纲》要求的 ≥150 GB。D10/D11 全量下载前必须处理（清理空间或改用有足够空间的机器），否则数据可能下不全。

## 今日完成

| 计划 | 状态 | 证据（文件/命令/链接） |
|---|---|---|
| 建立目录骨架 | ✅ | `journal/ notes/ env/ data/clinical/ code/ results/{tables,figures,repro}/ logs/` |
| 环境盘点 | ✅ | 本页「环境盘点」表 |
| 写 `README.md` | ✅ | `/Users/wangjiaqi/Desktop/实习日志/README.md` |
| 写 Markdown 速查 | ✅ | `notes/markdown.md` |
| 建 20 天打卡表 | ✅ | `journal/INDEX.md` |
| 首次 commit | ✅ | `day01: 建立仓库骨架与笔记规范` |

## 关键命令

```bash
mkdir -p journal notes env data/clinical code results/tables results/figures results/repro logs
hostname
uname -a
sw_vers
df -h "$HOME"
sysctl -n hw.ncpu
sysctl -n hw.memsize
git status
git add .gitignore README.md journal/INDEX.md journal/day01.md notes/markdown.md
git commit -m "day01: 建立仓库骨架与笔记规范"
git log --oneline
```

## 卡点与报错（本节不许空着）

### 卡点 1：macOS 上 `free -h` 和 `nproc` 不存在

- **报错原文**：

  ```text
  zsh:1: command not found: free
  zsh:1: command not found: nproc
  ```

- **我的猜测**：这两个命令是 Linux 工具，macOS 没有预装。
- **验证过程**：在 macOS 终端直接执行 → 都返回 `command not found`；改用 `sysctl -n hw.ncpu` 得到 8 核，用 `sysctl -n hw.memsize` 得到 17179869184 bytes。
- **根因**：`free` 和 `nproc` 属于 Linux 的 procps/coreutils 体系，Darwin 没有对应命令。
- **解决**：CPU 核数用 `sysctl -n hw.ncpu`；内存用 `sysctl -n hw.memsize`；磁盘用 `df -h "$HOME"`。
- **下次怎么避免**：看到教程里的命令先确认平台，Linux 与 macOS 的命令不通用。

### 卡点 2：VS Code 打开的不是新目录

- **现象**：在 `~/Desktop/实习日志` 里执行 `open -a "Visual Studio Code" .`，打开的是 `实习日志` 工作区，看不到新建的 `journal/`、`notes/`。
- **根因**：`open ... .` 里的 `.` 指当前终端目录；当时终端还在 `实习日志`，没有 `cd` 到目标目录。
- **解决**：先 `cd` 到目标目录再执行，或用 VS Code 的 `File → Open Folder...` 选择绝对路径；最终用多根工作区同时打开两个目录。
- **下次怎么避免**：执行任何 `open`/`git` 命令前先 `pwd`。

### 卡点 3：仓库命名与《总纲》不一致

- **现象**：《总纲》要求仓库名为 `intern-<姓名>-nsclc-survival`，当前实际使用的是已有的 `intern-log` 仓库（远程 `git@github.com:April32321/intern-log.git`）。
- **决定**：为避免维护两个仓库，本实习内容统一放在 `intern-log` 中；`README.md` 顶部保留项目名 `intern-wangjiaqi-nsclc-survival`。
- **待办**：D20 交付时在报告中说明命名差异，或提前在 GitHub 上把仓库重命名为 `intern-wangjiaqi-nsclc-survival`。

## Kilo 使用记录

- 问：`git add` 和 `git commit` 的区别、`HEAD` 是什么。答：`git add` 把工作区改动放入暂存区，`git commit` 把暂存区内容固化为一次提交，`HEAD` 指向当前分支的最新提交。核实方式：执行 `git status` 观察文件从 untracked/modified 变为 staged，提交后 `git log --oneline` 出现新记录——与解释一致。
- 问：如何在同一个 VS Code 窗口打开两个目录。答：使用多根工作区（`.code-workspace`），已在 `~/work/nsclc-workbench.code-workspace` 验证。
- 核实后修正：Kilo 最初建议新建 `~/work/intern-wangjiaqi-nsclc-survival` 仓库，但我的实际需求是继续用现有 `intern-log`；确认远程地址后改为在现有仓库根目录建结构，避免双仓库。

## 今日结论

1. 工作台已就绪：目录结构、打卡表、笔记规范和第一次 commit 都在 `intern-log` 仓库里。
2. macOS 与 Linux 的命令不能照抄，环境盘点要用 `sysctl`、`df` 等对应工具。
3. 磁盘只剩 71 GiB，是后续全量下载的硬约束，必须在 D10 前解决。

## 明日 3 件事

- [ ] 阅读 `每日计划/Day02.md`，完成提交规范、撤销与远程仓库练习。
- [ ] 写 `notes/git.md`（命令速查 + 提交规范 + 撤销场景）。
- [ ] 确认 `git remote -v` 与远程推送正常，补齐 `journal/INDEX.md` 的 D2 行。
