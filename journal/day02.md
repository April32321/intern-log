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
| 1 | 干净的提交历史 | ≥4 个提交；message 符合 `<scope>: <做了什么> - <一句话结论>`；一个提交只做一件事 | `git log --oneline` | 待办（已有 4 个 D1 提交，需复核粒度） |
| 2 | `notes/git.md` | 提交规范 + `diff`/`log` 四条命令 + 撤销四条命令 + `.gitignore` 语法；**不写冲突** | 文件本身 | 待办 |
| 3 | `journal/day02.md` | 今日目标、完成表、卡点原文、关键命令、Kilo 抓错记录、明日 3 件事 | 本文件 | 进行中 |
| 4 | 撤销演示 | 各执行一次 `git restore <file>` 与 `git restore --staged <file>`，能说清区别 | 命令输出 | 待办 |
| 5 | 分支练习 | `git switch -c day02-notes` → 提交一次 → `git switch main` | `git log --oneline --all` | 待办 |
| 6 | 远程同步 | `git push -u origin main` 成功；若失败，在日志写明原因 | 远程仓库页面 / 命令输出 | 待办 |
| 7 | 收尾提交与打卡 | commit `day02: git 提交规范、撤销与远程 - <结论>`；`journal/INDEX.md` 补 D2 行 | `git log`、`journal/INDEX.md` | 待办 |

## 今日验收标准（收尾逐条核对）

- [ ] 仓库里 ≥4 个提交，message 符合规范、粒度合理
- [ ] 能演示 `git diff` 与 `git log --oneline`
- [ ] 能演示一次 `git restore` 撤销，且说清它和 `git restore --staged` 的区别
- [ ] 远程 `push` 成功（或说明为何暂无远程）
- [ ] 能解释 `git revert` 与 `git reset --hard` 的区别，并说明为什么**优先用 revert**
- [ ] 会建分支并切回 `main`；知道遇冲突先 `git merge --abort`
- [ ] 日志含当日报错原文，以及至少 1 条"Kilo 说 X，我核实是 Y"

## 今日完成

| 计划 | 状态 | 证据（文件/命令/链接） |
|---|---|---|
|  |  |  |

## 关键命令

```bash
# 待执行后回填
```

## 卡点与报错（本节不许空着）

待填：报错原文 → 我的猜测 → 验证过程 → 根因 → 解决 → 下次怎么避免。

## Kilo 使用记录

待填：

- 问：
- 答：
- 核实结果：Kilo 说 X，我核实是 Y。

## 今日结论

待填：

1.
2.
3.

## 明日 3 件事

- [ ] 读 `每日计划/Day03.md`。
- [ ] 完成 Linux CLI 一（文件/权限/管道）练习。
- [ ] 写 `notes/linux-cli.md` 上半，补 `journal/INDEX.md` D3 行。
