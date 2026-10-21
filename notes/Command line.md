# Command line

命令行界面（CLI），通过文本命令操作计算机。

## 常用命令

- `ls` 列出目录内容
- `cd <dir>` 切换目录
- `pwd` 显示当前路径
- `cp` / `mv` / `rm` 复制 / 移动 / 删除
- `mkdir` 创建目录
- `cat` 查看文件内容
- `grep` 搜索文本
- `man <cmd>` 查看命令手册

## 文件编辑与写入

- `nano <file>` 编辑文件：`Ctrl+O` 保存、回车确认、`Ctrl+X` 退出
- `echo "text" >> file` 追加一行到文件末尾
- `printf 'text\n' > file` 覆盖写入文件
- `rsync -a --exclude='.git' src/ dest/` 复制目录并排除指定内容，结尾 `/` 表示复制目录里的内容

## 粘贴多行命令

- 含 `nano`、`vim` 等交互式编辑器的命令块要分段粘贴，否则后续命令会被当成文字输入编辑器
- 用 `printf` / `echo` 写文件可以避免交互，整块粘贴也能一次跑完

## 详细笔记

- Linux 文件操作、软链接、`less`、权限与管道：[linux-cli.md](linux-cli.md)
