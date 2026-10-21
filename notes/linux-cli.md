# Linux CLI（一）：文件、权限、管道、文本处理

> Day 3 笔记。来源：`每日计划/Day03.md` + 2026-10-21 在 `t12ub` 的 `~/d3-practice` 实际操作。
> 练习目录与仓库分离：命令在服务器跑，笔记、日志和 commit 在 Mac 仓库完成。

## 1. 目录结构与导航

```text
~/d3-practice
├── demo.txt                    # 软链接指向它，现内容为“第一行”
├── fake_dicom/
│   └── LUNG1-001_ct_01.dcm     # 空文件，仅用于命名练习
├── numbers.txt                 # seq 1 100
├── n200.txt                    # seq 1 200
├── sub/
│   ├── demo-renamed.txt        # 由 demo-copy.txt 改名后移入
│   └── deep/nested/            # mkdir -p 一次建出的三层目录
└── sub-copy/                   # cp -r sub sub-copy 的完整副本
```

| 命令 | 作用 |
|---|---|
| `pwd` | 显示当前绝对路径 |
| `ls -lah` | `-l` 长格式、`-a` 含 `.`/`..` 与隐藏文件、`-h` 大小带单位 |
| `cd -` | 回到上一个所在目录 |
| `cd ~` | 回家目录 `/home/jqw` |
| `tree -L 2` | 树形展示，`-L` 限制向下层数；未安装则用 `find . -maxdepth 2` |
| `du -sh .` | 当前目录总占用，`-s` 汇总、`-h` 人类可读 |

### `ls -l` 每列含义

```text
-rw-rw-r--  1 jqw jqw    0 Oct 21 10:00 demo.txt
│└┬┘└┬┘└┬┘  │  │   │     │        │
│ │  │  │   │  │   │     │        └ 文件名
│ │  │  │   │  │   │     └ 修改时间
│ │  │  │   │  │   └ 大小（字节）
│ │  │  │   │  └ 属组
│ │  │  │   └ 属主
│ │  │  │     硬链接数
│ │  │  └ 其他人权限
│ │  └ 属组权限
│ └ 属主权限
└ 类型：- 普通文件、d 目录、l 软链接
```

### 绝对路径 vs 相对路径

- 绝对路径从 `/` 开始，如 `/home/jqw/d3-practice/sub/deep`
- 相对路径以**当前目录**为基准：在 `~/d3-practice` 下，`deep` 不存在，必须写 `sub/deep`
- `mkdir -p sub/deep/nested` 只在 `sub/` 下建目录，不会在当前目录再建一个 `deep`
- `touch` 创建的是 **0 字节空文件**；`ls -lah` 里大小为 0 属正常

## 2. 文件操作

| 命令 | 说明 |
|---|---|
| `cp 源 目标` | 复制文件 |
| `cp -r 源目录 目标目录` | 递归复制整棵目录树；不加 `-r` 会报 `omitting directory` |
| `mv 源 目标` | 目标是**已存在目录**则移入；否则视为改名/移动并改名 |
| `mkdir -p a/b/c` | 一次创建多层目录，已存在也不报错 |
| `touch 文件` | 建空文件；对已存在文件只更新时间戳 |
| `ln -s 目标 链接名` | 建软链接（快捷方式），不复制内容 |
| `rm -i 文件` | 删除前逐个询问，输入 `y`/`yes` 才删 |
| `du -sh 目录` | 看目录实际占用 |
| `find . -name "*.txt"` | 按名字查找 |
| `find . -type d` | 只找目录；`-type l` 只找软链接 |
| `find . -maxdepth 2` | 限制搜索深度 |

`mv` 的两条路径可合并：

```bash
mv demo-copy.txt sub/demo-renamed.txt   # 改名 + 移动一步完成
```

注意：`mv` 覆盖同名文件时**不提示**，移动前先 `ls` 看目标目录。

## 3. 软链接

```bash
ln -s ../demo.txt fake_dicom/link-to-demo
ls -l fake_dicom
# lrwxrwxrwx 1 jqw jqw 11 ... link-to-demo -> ../demo.txt
```

| 现象 | 解释 |
|---|---|
| 行首 `l` | 这是软链接，不是普通文件 |
| 权限 `rwxrwxrwx` | 软链接权限固定显示，实际权限看目标文件 |
| 大小 `11` | 目标是字符串 `../demo.txt`，共 11 字节，不是内容大小 |
| `-> ../demo.txt` | 相对目标：**相对链接所在目录**解析，即 `fake_dicom/` 的上一层 |

用法与验证：

```bash
cat fake_dicom/link-to-demo          # 读：输出目标内容
echo "第一行" >> fake_dicom/link-to-demo   # 写：改的是 demo.txt
wc -c demo.txt fake_dicom/link-to-demo     # 都显示 10（跟随链接读目标）
readlink fake_dicom/link-to-demo           # 只看指向路径
find . -type l                             # 列出所有软链接
rm -i fake_dicom/link-to-demo              # 只删链接，不动目标
```

要点：

- 软链接不复制内容，读写都作用在目标文件上
- 删除链接不影响目标；删除目标则链接变成“断链”
- 移动链接位置可能断链，因为相对目标按**链接所在目录**解析
- 用途：避免复制大文件、多个目录共用同一份数据（如 `ln -s /data/nsclc data/raw`）

## 4. 文本查看与编辑

| 命令 | 作用 |
|---|---|
| `cat 文件` | 一次输出全部内容，适合小文件 |
| `less 文件` | 分页查看，大文件首选 |
| `head -n 5 文件` | 前 5 行 |
| `tail -n 3 文件` | 后 3 行；`-f` 持续跟踪新内容（`Ctrl+C` 退出） |
| `wc -l 文件` | 行数 |
| `wc -c 文件` | 字节数（UTF-8 一个汉字 3 字节） |
| `sed -n '50p' 文件` | 只打印第 50 行 |
| `nano 文件` | 编辑：`Ctrl+O` 保存 → 回车确认，`Ctrl+X` 退出 |

### `less` 常用按键

| 按键 | 作用 |
|---|---|
| `/关键词` + 回车 | 向下搜索（按**内容**匹配，不是行号） |
| `?关键词` + 回车 | 向上搜索 |
| `n` | 跳到下一个匹配（无需回车） |
| `N` | 跳到上一个匹配 |
| `50g` | 跳到第 50 行（行号，不看内容） |
| `g` / `G` | 文件开头 / 末尾 |
| `q` | 退出 |

搜索是正则匹配：

- `/50` 命中所有**包含** `50` 的行，如 50、150、501
- `/^50$` 只命中整行恰好等于 `50` 的行
- 只有一条匹配时按 `n` 会提示找不到下一个

> 典型误操作：已经退出 `less` 回到 shell，仍直接敲 `50` 回车，结果 `50: command not found`；若此时按了方向键，还会把转义序列一起带进命令（如 `^[OA50`）。判断方法：屏幕底部有 `:`/`(END)` 才在 `less` 里，看到 shell 提示符就不是。

## 5. 重定向、管道与退出码

### 重定向

| 写法 | 作用 |
|---|---|
| `命令 > 文件` | 标准输出写入文件，**覆盖**原内容 |
| `命令 >> 文件` | 标准输出追加到文件末尾 |
| `命令 2> 文件` | 只把错误输出写入文件 |
| `命令 2>&1` | 把错误输出并入标准输出，之后才能进管道 |
| `命令 \| tee 文件` | 同时输出到屏幕和文件 |

```bash
seq 1 100 > numbers.txt          # 覆盖写入
echo "第一行" >> demo.txt         # 追加
ls /no-such-path 2> err.log      # 只存错误
ls /no-such-path 2>&1 | tee err.log   # 屏幕 + 文件各一份
```

- `>` 会**清空原文件**，重要文件先用 `ls` 确认
- `>>` 追加，不破坏原内容
- 文本文件末尾保留换行，可避免 `echo >>` 后 diff 显示“最后一行被改写”

### 管道

`|` 把前一条命令的 **stdout** 交给后一条命令的 **stdin**，不需要临时文件。

```text
命令A ──stdout──> | ──stdin──> 命令B
```

实测例子：

| 命令 | 结果 |
|---|---|
| `ls -l \| wc -l` | `9`（含 `total`、`.`、`..`） |
| `find . -type f \| wc -l` | `7`（递归统计普通文件） |
| `grep -n "5" numbers.txt \| head -n 3` | 只输出前 3 条匹配，格式 `行号:内容` |
| `ls -l \| awk '{print $9}'` | 取文件名列；`total` 行没有第 9 列，输出空行 |

要点：

- 管道只传 stdout，stderr 不走管道；要 `2>&1` 合并
- 右边的命令必须会读 stdin：`grep`、`wc`、`head`、`awk`、`cut`、`sort`、`uniq`、`tee`
- 可以多级串联：`cut ... | sort | uniq -c | sort -rn | head`
- `|` 是交给下一个命令，`>` 是写进文件，两者不同

### 退出码与 `pipefail`

- `$?` 取上一条命令的退出码，`0` 成功，非 `0` 失败
- **管道的退出码默认等于最后一个命令**，前面的失败会被 `tee`/`head` 的成功掩盖

```bash
ls /no-such-path; echo "status=$?"                       # status=2
ls /no-such-path 2>&1 | tee err.log; echo "status=$?"    # status=0
set -o pipefail
ls /no-such-path 2>&1 | tee err.log; echo "status=$?"    # status=2
```

- 脚本开头写 `set -euo pipefail`：出错即停、未定义变量报错、管道任一环失败即失败
- `set -o pipefail` 只对当前 shell 会话有效，新终端会恢复默认

## 6. 权限

### 权限数字换算

| 数字 | 权限 | 含义 |
|---|---|---|
| `7` | `rwx` | 读 + 写 + 执行 |
| `6` | `rw-` | 读 + 写 |
| `5` | `r-x` | 读 + 执行 |
| `4` | `r--` | 只读 |
| `0` | `---` | 无权限 |

| 设置 | 属主 | 属组 | 其他人 | 典型用途 |
|---|---|---|---|---|
| `700` | `rwx` | `---` | `---` | 私有目录/脚本，如 `~/.ssh` |
| `644` | `rw-` | `r--` | `r--` | 公开可读的普通文件 |
| `755` | `rwx` | `r-x` | `r-x` | 可执行脚本、公开目录 |

- 目录的 `x` 表示“可进入”，没有 `x` 即使有 `r` 也 `cd` 不进去
- `chmod +x` 不写 `u/g/o` 时**三类都加**执行位；只给属主用 `chmod u+x`
- `umask` 决定新建文件/目录的默认权限：常见 `0002` → 文件 `664`、目录 `775`

### 实测记录（t12ub，2026-10-21）

```text
touch script.sh      → -rw-rw-r--   664（umask 0002）
chmod 700 script.sh  → -rwx------   700
chmod 644 script.sh  → -rw-r--r--   644
chmod +x  script.sh  → -rwxr-xr-x   755（三类都加 x）
umask                → 0002

mkdir permtest       → drwxrwxr-x   775
touch permtest/a.txt → -rw-rw-r--   664

chmod 600 permtest   → drw-------   600
cd permtest          → Permission denied（无 x，不能进入）

chmod 700 permtest   → drwx------   700
cd permtest          → 成功进入
```

> 结论：目录权限里的 `x` 是“通行证”，`r` 只决定能否列出内容；`600` 的目录连 `cd` 都不行。

## 7. 文本处理三件套

### grep：按内容过滤

```bash
grep -n "5" numbers.txt        # -n 显示行号
grep -in "lung" notes/*.md     # -i 忽略大小写
grep -rn "TODO" notes/         # -r 递归目录
grep -E "LUNG1-00[1-3]" names.txt   # -E 扩展正则
grep -v "ct" names.txt         # -v 反向匹配（排除）
```

`grep -n` 输出格式为 `行号:内容`，如 `5:5` 表示第 5 行内容为 `5`。

### cut：按分隔符取列

```bash
cut -d: -f1 /etc/passwd              # 以 : 分隔，取第 1 列（用户名）
cut -d: -f7 /etc/passwd              # 取第 7 列（登录 shell）
ls audit | cut -d_ -f1 | sort | uniq -c   # 按 _ 取 PID 并计数
```

`cut` 只能处理**单个字符**分隔符，且不能按正则切；复杂场景用 `awk`。

### awk：按列取、过滤、统计

基本结构：`awk -F分隔符 '条件 {动作}' 文件`。

```bash
awk -F: '{print $1, $7}' /etc/passwd        # 打印用户和 shell
awk -F: '$3 >= 1000 {print $1, $3}' /etc/passwd   # 过滤 UID≥1000
awk 'NR>=1 && NR<=5' numbers.txt            # 打印第 1–5 行
awk '{sum += $1} END {print sum}' numbers.txt     # 求和
```

常用变量：`$0` 整行、`$1` 第 1 列、`$NF` 最后一列、`NR` 当前行号、`-F` 指定分隔符。

#### 我的 awk 一行流合集

已验证：

```bash
# 1. 取 ls -l 的文件名列
ls -l | awk '{print $9}'

# 2. 按冒号取用户名与登录 shell
awk -F: '{print $1, $7}' /etc/passwd

# 3. 统计每种 shell 的用户数（等价于 cut | sort | uniq -c）
awk -F: '{c[$7]++} END {for (k in c) print c[k], k}' /etc/passwd
```

待验证（尚未实际跑过，跑通后再移到上面）：

```bash
# 4. 过滤 UID≥1000 的用户
awk -F: '$3 >= 1000 {print $1, $3}' /etc/passwd

# 5. 对第 1 列求和
awk '{s += $1} END {print s}' numbers.txt
```

### sort | uniq -c：排序去重计数

```bash
cut -d: -f7 /etc/passwd | sort | uniq -c | sort -rn | head
```

- `sort` 必须先排序，`uniq -c` 只合并**相邻**重复行
- `uniq -c` 输出 `次数 内容`
- `sort -rn` 按次数数值倒序；`sort -u` 直接去重
- 实测结果：`32 /usr/sbin/nologin`、`3 /bin/false`、`3 /bin/bash`、`1 /bin/sync`

### sed：按行处理

```bash
sed -n '1,5p' numbers.txt       # 只打印第 1–5 行
sed -n '/LUNG1-00/p' names.txt  # 打印匹配行
```

- `-n` 关闭默认输出，配合 `p` 只打印需要的行
- 真正改文件用 `-i`，但 macOS 与 GNU 语法不同（macOS 需 `-i ''`），改前先备份

## 8. 今日易错点

1. `ls -l deep` 失败：`deep` 在 `sub/` 下，相对路径要写 `sub/deep`
2. `/50` 搜的是**内容**，`50g` 才是跳**行号**
3. `less` 里搜索必须先按 `/`；在 shell 里敲 `50` 会被当成命令
4. `mv` 覆盖同名文件不提示，移动前先 `ls` 目标目录
5. `rm -rf "$VAR"/` 在 `$VAR` 为空时会删到根目录：脚本里用 `set -u`，删除前先 `echo "$VAR"` 并 `ls` 确认
6. 路径含空格必须加引号：`"$var"`，不要裸写 `$var`
7. 引号未闭合时提示符变成 `>`（PS2 续行），不是重定向；按 `Ctrl+C` 取消重来
8. 管道退出码默认取最后一条命令，`ls | tee` 可能显示报错却返回 `0`；脚本用 `set -o pipefail`
