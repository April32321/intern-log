# Git

分布式版本控制系统，用于跟踪代码变更、协作开发。

## 核心概念

- 工作区 → 暂存区（index）→ 仓库：`git add` 进暂存区，`git commit` 打包成快照
- 分支只是指向某个提交的指针，不是文件副本
- `HEAD` 指向当前所在的提交，通常通过当前分支间接指向

## 基础操作

- `git --version` 查看版本
- `git config --global user.name "名字"` / `user.email "邮箱"` 配置身份
- `git config --list` 查看全部配置
- `git init` 初始化仓库
- `git status` 查看状态：untracked 显示 `??`，已忽略显示 `!!`
- `git add <file>` 暂存改动，把当前内容快照放进暂存区
- `git add -A` 暂存所有改动，包括删除
- `git commit -m "msg"` 提交暂存区内容
- `git rm --cached <file>` 停止跟踪，但保留本地文件

## 查看差异与历史

- `git diff` 工作区 vs 暂存区，untracked 文件不显示
- `git diff --staged` 暂存区 vs 最后一次提交
- `git log` 完整历史，最新的在最上面
- `git log --oneline` 一行一个提交
- `git log --oneline --graph --all` 树状图并显示所有分支
- `git log --stat` 显示每个提交改了哪些文件、增删行数
- `git show <hash>` 查看某次提交的信息和 diff，hash 可用前 7 位

## 忽略文件

- `.gitignore` 每行一条规则，支持 `*.log`、目录 `journal/`、系统文件 `.DS_Store`
- 只对未跟踪文件生效；已提交的文件需先 `git rm --cached <file>`
- `.gitignore` 本身也要提交，规则才会跟着仓库走

## 分支

- `git branch` 列出分支，`*` 标记当前分支
- `git branch <name>` 创建分支但不切换
- `git switch <name>` 切换分支，工作区文件随之改变
- `git switch -` 回到上一个分支
- `git switch -c <name>` 创建并立即切换
- `git branch -vv` 查看分支及其跟踪关系
- `git branch -m <old> <new>` 重命名分支
- `git branch -d <name>` 删除已合并分支，未合并会拒绝
- `git branch -D <name>` 强制删除未合并分支

## 合并与冲突

- `git merge <branch>` 把指定分支合并到当前分支
- Fast-forward：目标分支未分叉时只移动指针，不产生合并提交
- `git merge --no-ff <branch>` 强制生成合并提交
- 冲突标记三段：`<<<<<<< HEAD` 到 `=======` 是当前分支内容，`=======` 到 `>>>>>>> 分支名` 是对方内容
- 解决冲突：编辑文件删掉标记 → `git add <file>` → `git commit`
- `git merge --abort` 放弃本次合并，恢复到合并前状态

## 远程仓库

- `git remote add origin <url>` 关联远程仓库
- `git remote -v` 查看远程地址
- `git push -u origin main` 首次推送并建立跟踪关系
- `git push` 建立跟踪后直接推送
- `git clone <url>` 克隆仓库，自动带 `origin` 和完整历史
