# Git

分布式版本控制系统，用于跟踪代码变更、协作开发。

## 核心概念

- 工作区 → 暂存区（index）→ 仓库：`git add` 进暂存区，`git commit` 打包成快照
- 分支只是指向某个提交的指针，不是文件副本
- `HEAD` 指向当前所在的提交，通常通过当前分支间接指向

## 提交规范

格式：

```text
<scope>: <做了什么> - <一句话结论>
```

scope 取值与示例：

| scope | 用途 | 示例 |
|---|---|---|
| `dayNN` | 当天学习日志、笔记、打卡 | `day02: 补全日志 - 记录 restore 演示与报错` |
| `feat` | 新增功能、脚本、管线 | `feat: 增加数据清点脚本 - 支持 422 例批量统计` |
| `fix` | 修 bug、修错误 | `fix: 修正 ROI 名称匹配 - GTV_1 变体导致 12 例漏提` |
| `data` | 数据相关：清单、索引表、校验、下载说明 | `data: 补充 series manifest - 422 例 UID 与文件数校验` |
| `env` | 环境：Conda、Docker、依赖版本 | `env: 锁定 pyradiomics 3.1.0 - 修复 py3.12 编译失败` |
| `docs` | 与具体某天无关的文档：README、报告、模板 | `docs: 补充 README 快速开始 - 增加 git status 自查步骤` |

判断标准：一个提交只做一件事；不看 diff 也能知道改了什么。

坏例子：`update`、`修改`、`day02`，都无法判断改动内容。

## 基础操作

- `git --version` 查看版本
- `git config --global user.name "名字"` / `user.email "邮箱"` 配置身份
- `git config --list` 查看全部配置
- `git init` 初始化仓库
- `git status` 查看状态：untracked 显示 `??`；加 `--ignored` 可查看已忽略文件
- `git add <file>` 暂存改动，把当前内容快照放进暂存区
- `git add -A` 暂存所有改动，包括删除
- `git commit -m "msg"` 提交暂存区内容
- `git rm --cached <file>` 停止跟踪，但保留本地文件

## 查看差异与历史

- `git diff` 工作区 vs 暂存区，untracked 文件不显示
- `git diff --staged` 暂存区 vs 最后一次提交（等价 `--cached`）
- `git log --oneline -10` 最近 10 条提交，一行一条
- `git show <hash>` 查看某次提交的信息和 diff，hash 可用前 7 位
- `git log` 完整历史，最新的在最上面
- `git log --oneline --graph --all` 树状图并显示所有分支
- `git log --stat` 显示每个提交改了哪些文件、增删行数

## 撤销

撤销要分三种情况：未提交的改动、已提交但未推送、已经推送。

### 未提交：`git restore`

- `git restore <file>` 用暂存区内容覆盖工作区；未暂存的改动会丢失。若改动已经 `git add`，工作区只会恢复成暂存版本，暂存本身不变
- `git restore --staged <file>` 用 HEAD 覆盖暂存区，只取消暂存，工作区改动保留
- `git commit --amend -m "新信息"` 改写最后一次提交的信息或内容；只能在未推送时用

### 已提交：`git revert` 与 `git reset --hard`

`git revert <hash>`：生成一个**反向提交**来抵消指定提交，旧提交仍保留在历史里。

```text
提交前：       A --- B --- C
revert C 后：  A --- B --- C --- C'
```

- 不改写历史，`git log` 能同时看到“做了什么”和“怎么撤销的”
- 已推送也能安全使用，不需要 force push，协作者正常 `pull` 即可
- 可能冲突：解决后 `git revert --continue`；放弃用 `git revert --abort`
- 撤销合并提交要指定主线：`git revert -m 1 <hash>`

`git reset --hard <hash>`：把分支指针移到目标提交，并强制重置暂存区和工作区。

```text
reset 前：  A --- B --- C   (main, origin/main)
reset 后：  A --- B         (main)
                  \
                   C  （游离提交，远程可能仍在 C）
```

- 目标之后的提交从分支历史里消失（短期内可用 `git reflog` 找回）
- 未提交的改动直接丢失，无法用 `restore` 找回
- 已推送时必须 `git push --force` 覆盖远程，会让其他人的历史分叉

`reset` 三种模式：

| 模式 | HEAD | 暂存区 | 工作区 | 典型用途 |
|---|---|---|---|---|
| `--soft` | 移动 | 保留 | 保留 | 把最后几次提交合并成一次 |
| `--mixed`（默认） | 移动 | 重置 | 保留 | 撤销 commit，改动退回工作区 |
| `--hard` | 移动 | 重置 | **丢弃** | 彻底放弃本地未推送的提交和改动 |

### 为什么优先用 `revert`

1. 不改写历史，提交记录完整，审计时能追溯“哪个提交出了问题、用哪次提交撤销”
2. 对已推送的提交安全，不需要 force push，不会让协作者的仓库分叉
3. `revert` 本身也是普通提交，撤错了还能再 revert 一次
4. 符合项目纪律：已推送只 `revert`，`reset` 只碰自己未推送的提交

### 三者对比

| 命令 | 作用对象 | 产生新提交 | 改写历史 | 适用场景 |
|---|---|---|---|---|
| `git restore` | 工作区 / 暂存区 | 否 | 否 | 撤销未提交的改动 |
| `git revert` | 已提交的内容 | 是（反向提交） | 否 | 已提交，尤其已推送 |
| `git reset --hard` | 分支指针 + 暂存区 + 工作区 | 否 | 是 | 本地未推送、确定不要的提交 |

原则：已推送的提交只 `revert`，不 `reset --hard`。

## 忽略文件

- `.gitignore` 每行一条规则，`#` 开头是注释
- 忽略某类文件：`*.log`
- 忽略整个目录：`data/raw/`
- 例外规则：`!keep.log`（放在 `*.log` 之后）
- 只对未跟踪文件生效；已提交的文件要先 `git rm --cached <file>`
- `.gitignore` 本身也要提交，规则才会跟着仓库走
- 绝对不能进 Git：`data/raw/`、`*.dcm`、`*.nii.gz`、模型权重（`*.pt`/`*.pth`/`*.h5`）、`.env`、私钥、`kilo.jsonc`

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
- `git fetch` 只下载远程更新，不改工作区
- `git pull` 拉取并合并远程更新（fetch + merge）
- `git clone <url>` 克隆仓库，自动带 `origin` 和完整历史

## 易错点

- 长选项是两个连字符：`git diff --staged`；写成 `-staged` 会报 `invalid option`
- `git log --oneline` 是一个整体；单独 `--` 表示后面是路径，如 `git log --oneline -- journal/day02.md`
- 文档里的 `<hash>`、`<file>` 是占位符，粘贴命令时要去掉尖括号；`<` `>` 在 shell 中是重定向符
- 文件末尾缺换行时，追加内容会让 diff 显示“最后一行被改写”，并出现 `\ No newline at end of file`
- `Changes to be committed` 只表示已暂存，执行 `git commit` 后才真正入库
