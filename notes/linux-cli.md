# Linux CLI：文件、权限、管道、文本处理、进程与资源、tmux、PATH

> Day 3–4 笔记。§1–§9 来源：`每日计划/Day03.md` + 2026-10-21 在 `t12ub` 的 `~/d3-practice` 实际操作；
> §10–§12 来源：`每日计划/Day04.md` + 2026-10-22 在 `t12ub` 的 `~/d4-practice` 实测。
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

### 路径自测与两个坑（2026-10-22 实测）

4 道自测题，先写答案再敲命令；首答 2 对 2 错，纠错后 4/4。

| # | 从哪 | 到哪 | 正确写法 | 说明 |
|---|---|---|---|---|
| 1 | `notes/` | 仓库根 | `cd ..` | `cd -` 回的是 `OLDPWD`，取决于来路，不是回上级 |
| 2 | 仓库根 | `results/tables` | `cd results/tables` | 前导 `/` 会变成绝对路径，从文件系统根找 |
| 3 | `results/tables` | 读 `notes/git.md` | `head -n 3 ../../notes/git.md` | `..` 逐层上跳，两次才到仓库根 |
| 4 | `results/tables` | 同一个文件 | `head -n 3 ~/Desktop/实习日志/notes/git.md` | 与相对路径输出逐字一致 |

两个坑与两条补充：

- **`cd -` ≠ `cd ..`**：`cd -` 回 `OLDPWD` 并打印目标路径。从仓库根 `cd notes` 进来时它碰巧回到仓库根；从 `~/Desktop` 直接进来就会回到 `~/Desktop`。命令成功不代表规则正确。
- **前导 `/` = 绝对路径**：`cd /results/tables` 实测报 `cd: no such file or directory: /results/tables`（用 `zsh -c` 调用时前缀显示为 `zsh:cd:1:`），因为系统根下没有 `results`。仓库里的目录只能写 `results/...` 或 `~/Desktop/实习日志/results/...`。
- 失败的 `cd` **不改变**当前目录，失败后 `pwd` 仍是原目录。
- `~` 只在词首由 shell 展开为家目录；`~user` 指某用户的家目录。
- 命令里的路径参数同样相对**当前目录**解析：在 `results/tables` 下 `git add journal/day04.md` 会报 `fatal: pathspec ... did not match any files`，要 `cd` 回仓库根或写 `../../journal/day04.md`。`git status` 显示的 `../../` 前缀就是当前目录的深度。

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

## 8. 实战：DICOM 命名审计

目标：不用图形界面完成“造数据 → 找不合规 → 按患者统计 → 写成 CSV”。这是 D11 数据清点的预演。

### 合法命名规则

```text
^LUNG1-[0-9]{3}_ct_[0-9]{2}\.dcm$
```

- `^` / `$`：整行匹配，防止 `xxx.dcm.bak` 这类后缀漏过
- `[0-9]{3}`：PID 三位数字
- `_ct_`：modality 必须小写
- `[0-9]{2}`：序号两位
- `\.`：转义点号

### 造 30 个测试文件

```bash
mkdir -p audit
for p in 1 2 3 4 5 6 7 8 9 10; do
  pid=$(printf "LUNG1-%03d" "$p")
  n=$(( (p - 1) % 5 + 1 ))
  for i in $(seq -f "%02g" 1 "$n"); do
    touch "audit/${pid}_ct_${i}.dcm"
  done
done
```

- `printf "%03d"` / `seq -f "%02g"`：补零，保证文件名宽度固定
- 文件数按 1–5 循环，避免统计结果全是同一个数字

### 找不合规文件

```bash
ls audit | grep -Ev '^LUNG1-[0-9]{3}_ct_[0-9]{2}\.dcm$'
```

- `-E` 用扩展正则，`{3}`/`{2}` 才是“重复次数”
- `-v` 反向选择，输出**不匹配**的行
- 不加 `-E` 时必须写 `\{3\}`/`\{2\}`；写成 `{3}` 会被当字面量，`grep -c` 结果为 0

实测：30 个文件中 27 个合规、3 个不合规。

### 按患者统计文件数

```bash
ls audit | cut -d_ -f1 | sort | uniq -c
```

- `cut -d_ -f1` 取第一个下划线前的 PID
- `sort` 必须在前，`uniq -c` 只合并相邻重复
- 输出格式：`次数 PID`

实测输出（10 行）：

```text
1 LUNG1-001
2 LUNG1-002
3 LUNG1-003
4 LUNG1-004
5 LUNG1-005
1 lung1-006
2 LUNG1-007
3 LUNG1-008
4 LUNG1-009
5 LUNG1-010
```

发现：`LUNG1-006` 因为文件被改成小写，整组从统计里消失，另立为 `lung1-006`。**大小写错误会把同一患者拆成两个 PID**，必须在合并临床表之前审计。

### 生成 `name_audit.csv`

```bash
declare -A cnt
for f in $(ls audit); do
  pid=${f%%_*}
  cnt[$pid]=$(( ${cnt[$pid]:-0} + 1 ))
done

{
  echo "filename,pid,modality,seq_no,valid,patient_file_count"
  for f in $(ls audit); do
    if [[ "$f" =~ ^(LUNG1-[0-9]{3})_(ct)_([0-9]{2})\.dcm$ ]]; then
      pid=${BASH_REMATCH[1]}
      mod=${BASH_REMATCH[2]}
      seq=${BASH_REMATCH[3]}
      valid=yes
    else
      pid=${f%%_*}
      mod=""
      seq=""
      valid=no
    fi
    echo "$f,$pid,$mod,$seq,$valid,${cnt[$pid]}"
  done
} > name_audit.csv
```

CSV 列含义：

| 列 | 含义 |
|---|---|
| `filename` | 原始文件名 |
| `pid` | 文件名第一段；不合规时仅按 `_` 切分，可能带大小写问题 |
| `modality` | 仅合规行填写；不合规留空 |
| `seq_no` | 仅合规行填写；不合规留空 |
| `valid` | `yes`/`no`，由整行正则判定 |
| `patient_file_count` | 该 PID 前缀下的**全部**文件数（含不合规文件） |

坑：`declare -A` 只在当前 shell 会话有效；退出 SSH 或新开终端后数组丢失，需要重跑统计段。

### 多层目录的写法（D11 用，未验证）

```bash
find audit -type f -name '*.dcm' -printf '%f\n' \
  | awk -F_ '{
      pid=$1; mod=$2; seq=$3
      sub(/\.dcm$/, "", seq)
      ok = ($0 ~ /^LUNG1-[0-9]{3}_ct_[0-9]{2}\.dcm$/) ? "yes" : "no"
      print $0 "," pid "," mod "," seq "," ok
    }'
```

- `find` 递归，`-printf '%f\n'` 只输出文件名（GNU find；macOS 用 `-exec basename {} \;`）
- `awk -F_` 分列，`sub()` 去掉 `.dcm`，`$0 ~ /正则/` 判定合规
- 本条尚未在真实多层目录跑过，D11 使用时先小样本验证再全量

## 9. 今日易错点

1. `ls -l deep` 失败：`deep` 在 `sub/` 下，相对路径要写 `sub/deep`
2. `/50` 搜的是**内容**，`50g` 才是跳**行号**
3. `less` 里搜索必须先按 `/`；在 shell 里敲 `50` 会被当成命令
4. `mv` 覆盖同名文件不提示，移动前先 `ls` 目标目录
5. `rm -rf "$VAR"/` 在 `$VAR` 为空时会删到根目录：脚本里用 `set -u`，删除前先 `echo "$VAR"` 并 `ls` 确认
6. 路径含空格必须加引号：`"$var"`，不要裸写 `$var`
7. 引号未闭合时提示符变成 `>`（PS2 续行），不是重定向；按 `Ctrl+C` 取消重来
8. 管道退出码默认取最后一条命令，`ls | tee` 可能显示报错却返回 `0`；脚本用 `set -o pipefail`

## 10. 进程与资源

> 2026-10-22 在 `t12ub`（Ubuntu，共享机，`nproc=12`）实测。§10.1–§10.7 全部为当日实测结果；
> tmux 那一列与 §11 一起补。

### 10.1 `ps` 是什么

`ps` = process status：给「当前这一瞬间」的进程表拍快照，打印完就退出，**不刷新**。
它读的是内核维护的 `/proc/<PID>/`，不是自己监控出来的：

```bash
cat /proc/1/status | head -5          # 内核里的原始信息
tr '\0' ' ' < /proc/1/cmdline; echo   # 完整启动命令（参数用 \0 分隔）
```

它和 `top` 的分工：

| | `ps` | `top` |
|---|---|---|
| 形式 | 一次性快照，跑完退出 | 持续刷新的全屏监视器 |
| 适合 | 精确查某个进程、拿 PID 给 `kill`、脚本里处理 | 人眼看实时变化 |
| 可进管道 | 是（`\| grep`、`\| sort`、`\| wc -l`） | 只能配 `-b` 批处理模式 |

**顺序是固定的**：`ps` 找到 PID → `kill` 用 PID 动手；`jobs` 只看当前 shell 自己的作业表。

### 10.2 两套选项语法

| 风格 | 写法 | 典型 | 备注 |
|---|---|---|---|
| BSD | 不带横线，字母可合并 | `ps aux`、`ps ax` | 带 `%CPU`/`%MEM`/`VSZ`/`RSS` |
| UNIX | 带横线 | `ps -ef`、`ps -eo pid,ppid,stat,cmd` | `-ef` 多 `PPID`，看父子关系 |
| GNU 长选项 | 双横线 | `ps --sort=-%cpu` | 只部分平台支持 |

```bash
ps aux                        # 全机所有进程（a 所有用户 + u 用户格式 + x 含无终端）
ps -u jqw                     # 只列自己的——动手 kill 之前先跑这条
ps -ef                        # 全量 + PPID
ps -p 12345                   # 只看指定 PID
ps -p 12345 -o pid,ppid,pgid,sid,tty,stat,etime,cmd   # 自定义列
ps --sort=-%cpu | head -6     # 按累计 CPU 排序（注意是平均值，见 §10.6 ②）
ps -e --forest                # 树形，看谁是谁的子进程
ps -eLf --no-headers | wc -l  # 线程数（含内核线程），会比 ps aux 行数多
pgrep -af python              # 按名字找 PID，grep 的专职替代
```

`ps -p <PID>` 是后续实验的核对工具：进程在 → 退出码 `0` 且有输出；已退出 → 无输出、`exit=1`。

```bash
ps -p 12345; echo "exit=$?"   # 存在 exit=0；不存在 exit=1
```

### 10.3 `ps aux` 每列含义（用本机 PID 1/2 实测对照）

```text
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root           1  0.0  0.1  22584 12656 ?        Ss   Oct08   0:25 /usr/lib/systemd/systemd --system --deserialize=132
root           2  0.0  0.0      0     0 ?        S    Oct08   0:00 [kthreadd]
```

| 列 | 值 | 含义 |
|---|---|---|
| `USER` | `root` | 进程属主；决定你有没有权限 `kill` 它 |
| `PID` | `1` / `2` | 进程号；1 号是 `systemd`（用户态万物祖先，`PPID=0`），2 号是内核线程总管家 |
| `%CPU` | `0.0` | **累计 CPU 时间 ÷ 存活时长**，不是瞬时值（见 §10.6 ②） |
| `%MEM` | `0.1` | 物理内存占用百分比 |
| `VSZ` | `22584` | 虚拟内存 KB（≈22 MB），含尚未真正加载的部分，**不能当实际占用** |
| `RSS` | `12656` | 实际驻留物理内存 KB（≈12 MB）；内核线程为 `0` |
| `TTY` | `?` | 无控制终端 = 不在任何登录会话里；`pts/0` 才是挂在终端上 |
| `STAT` | `Ss` | 状态码，见下表 |
| `START` | `Oct08` | 启动时间，不是运行时长 |
| `TIME` | `0:25` | **累计占用 CPU 的时间**；13 天只花 25 秒属正常 |
| `COMMAND` | 路径 / `[kthreadd]` | 带方括号的是内核线程：没有用户态可执行文件，`/proc/2/cmdline` 为空 |

`systemd` 的 `--deserialize=132` 是它 re-exec 时从 initrd 交接的序列化状态（132 是 fd 号），属正常启动流程。

### 10.4 状态码 `STAT`

主状态（第一位）：

| 字母 | 含义 | 典型场景 |
|---|---|---|
| `R` | running / runnable | 正在跑或排队 |
| `S` | 可中断睡眠 | 等事件，最常见 |
| `D` | 不可中断睡眠 | 多在等磁盘 I/O，`kill -9` 也杀不掉，只能等 |
| `T` | 暂停 | `Ctrl+Z` 或 `SIGSTOP` |
| `Z` | 僵尸 | 已退出但父进程没 `wait`，会一直挂着 |
| `I` | idle 内核线程 | `kworker`、`rcu_*` 等，`RSS=0`，不用管 |

修饰符（后面小写/符号）：

| 修饰 | 含义 |
|---|---|
| `s` | session leader（会话首进程） |
| `l` | 多线程 |
| `+` | 属于前台进程组 |
| `<` / `N` | 高 / 低优先级（nice） |
| `L` | 有内存页被 `mlock` 锁定 |

所以 `Ss` = 睡眠中的会话首进程；`Ssl` = 再加多线程，是**守护进程的典型指纹**（配合 `TTY=?`）。

### 10.5 `top -b -n1` 每段读什么（2026-10-22 11:39 实测）

```text
top - 11:39:53 up 13 days, 20:41,  5 users,  load average: 0.03, 0.05, 0.01
Tasks: 302 total,   1 running, 301 sleeping,   0 stopped,   0 zombie
%Cpu(s):  1.3 us,  0.6 sy,  0.0 ni, 96.8 id,  1.3 wa,  0.0 hi,  0.0 si,  0.0 st
MiB Mem :  11958.4 total,   4178.5 free,   3345.5 used,   4803.7 buff/cache
MiB Swap:   4096.0 total,   1381.4 free,   2714.6 used.   8612.9 avail Mem
```

**第一行**

| 字段 | 本次值 | 含义 |
|---|---|---|
| `up` | `13 days` | 系统连续运行时长；`5 users` 是**登录会话数**，不是进程数 |
| `load average` | `0.03, 0.05, 0.01` | 最近 1 / 5 / 15 分钟的「可运行 + 不可中断」进程数均值。**不是 CPU 百分比**，过载阈值是核数（`nproc`） |

**`%Cpu(s)`**

| 字段 | 本次 | 含义 |
|---|---|---|
| `us` | 1.3 | 用户态（你的程序） |
| `sy` | 0.6 | 内核态（系统调用） |
| `id` | 96.8 | 空闲 |
| `wa` | 1.3 | 等 I/O；持续偏高说明瓶颈在磁盘/网络 |
| `st` | 0.0 | 被虚拟化层偷走的 CPU（云主机要盯） |

**内存两行**：单位是 MiB（11958 MiB ≈ 11.7 GiB）。`buff/cache` 是**可回收缓存，不算真实占用**，以 `avail Mem` 为准；Swap 的 `used` 反映历史内存压力。

**进程区**：`PR/NI` 优先级与 nice（内核线程 `-20`），`VIRT/RES/SHR` 对应 `ps` 的 `VSZ/RSS`，`S` 是状态，`TIME+` 是累计 CPU（百分之一秒）。

**采样坑**：`-b -n1` 第一屏的 `%CPU` 和 `ps` 一样是「自启动以来的均值」；要瞬时增量得采两次：

```bash
top -b -n2 -d1 | tail -20      # 第二屏才是最近 1 秒的真实占用
```

### 10.6 本机资源画像（实测结论）

**① 有没有自己的 python 在跑**

```bash
ps aux | grep -i '[p]ython'
```

```text
root        1122 ... Ssl  Oct08   0:00 /usr/bin/python3 .../unattended-upgrade-shutdown --wait-for-signal
xufumin     1318 ... Ssl  Oct08  37:51 .../python3.12 .../devpi-server --configfile ...
```

两行都不是 `jqw` 的，且都是 `Ssl` + `TTY=?` 的常驻服务：PID 1122 是系统自动更新的等待进程（RSS 6.2 MB），PID 1318 是别人的私有 PyPI 镜像 `devpi-server`（RSS 1.38 GB，`%MEM 11.3`）。
结论：**自己当前没有任何 python 任务**，后续实验里的进程都要自己造。

**② `%CPU` 排序排的是"历史平均值"**

```bash
ps aux --sort=-%cpu | head -5
```

本次榜首是百度网盘 renderer，`%CPU 2.7`、`TIME 543:36`、`START Oct08`。验算：`Oct08` 到 11:39 约 13.8 天 ≈ 19872 分钟，`543:36 ≈ 544` 分钟，`544 / 19872 ≈ 2.7%` —— 和显示值完全一致。

结论：`ps` 的 `%CPU` = 累计 CPU ÷ 存活时长，排行榜回答的是「谁长期最费 CPU」，**不是「此刻谁在狂转」**；后者只能靠 `top -b -n2`。

**③ 整体负载与容量**

| 指标 | 实测 | 判读 |
|---|---|---|
| load average | 0.03 / 0.05 / 0.01 | 接近 0，机器基本空闲（需与 `nproc` 核数比较） |
| `%Cpu(s) id` | 96.8 | 空闲为主；`wa 1.3` 无 I/O 瓶颈 |
| 内存 | 总 11.7 GiB，used 3.3 GiB，buff/cache 4.7 GiB，**avail 8.4 GiB** | 充足；`used` 不含可回收缓存 |
| Swap | 4.0 GiB 中已用 **2.7 GiB** | 历史上出现过内存压力；不紧急，但 D17 全量特征提取时要盯 `si/so` |
| 磁盘 | `/` 3.9 T，已用 201 G，**可用 3.5 T（6%）** | 远超 `setup_check.sh` 的 `need_gb=150`，该项应 PASS |
| 家目录挂载点 | `df -h ~` 显示 `/` | 家目录没单独分区，看到的是整盘 |

**④ 共享机边界**

- `ps aux` 是**全机**视角，别人的进程也在里面（`root`、`xufumin`）；动手前先 `ps -u jqw`。
- 只 kill 属主是自己的 PID；禁止 `pkill python` 这类按名字批量杀，可能杀掉别人的服务。
- `TTY=?` + `Ssl` 的守护进程能活过 SSH 断开，正好是 §10.7 断连实验的对照基准。

### 10.7 作业控制与信号（2026-10-22 实测）

#### 作业控制三态

```bash
sleep 300                 # 前台：提示符消失
# Ctrl+C                  → echo $? 得 130
sleep 300 &               # 后台：[1] 1635730
jobs -l                   # [1]+ 1635730 Running   sleep 300
ps -p "$(jobs -p)" -o pid,ppid,pgid,sid,tty,stat,cmd -ww
fg %1                     # 拉回前台
# Ctrl+Z                  → [1]+ Stopped
bg %1                     # 挂起态转后台继续
kill %1                   # 按作业号终止
```

| 动作 | 命令 / 按键 | `jobs` 状态 | 关键输出 |
|---|---|---|---|
| 前台中断 | `Ctrl+C` | — | `exit=130`（128 + 2 号 `SIGINT`） |
| 后台启动 | `sleep 300 &` | `Running` | `[1] 1635730` |
| 查看归属 | `ps -p ... -ww` | — | `PPID=1630611`、`PGID=1635730`、`SID=1630611`、`TTY=pts/1` |
| 挂起 | `Ctrl+Z`（`SIGTSTP`） | `Stopped` | `[1]+ Stopped  sleep 300` |
| 恢复后台 | `bg %1`（`SIGCONT`） | `Running` | 回显 `[1]+ sleep 300 &` |
| 终止 | `kill %1` | 空 | `[1]+ Terminated`；`ps` 空输出 + `exit=1` |

结论：后台作业的 `PGID` 独立成组，所以前台 `Ctrl+C` 打不到它；但 `SID` 与 shell 相同、`TTY=pts/1`，
说明 **`&` 只改变作业调度，没有脱离会话**。`jobs` 的状态变化是 `Running → Stopped → Running → Terminated`，
`[1]+` 的 `+` 表示当前作业（`-` 是上一个作业）。

#### 信号速查（`kill -l` 已核对编号）

| 信号 | 编号 | 默认行为 | 能否捕获 |
|---|---|---|---|
| `SIGHUP` | 1 | 终止 | 能（`nohup` 即忽略它） |
| `SIGINT` | 2 | 终止 | 能（`Ctrl+C`） |
| `SIGKILL` | 9 | 强制终止 | **不能**，内核直接销毁，不做清理 |
| `SIGTERM` | 15 | 终止 | 能（`kill` 默认发它） |
| `SIGSTOP` / `SIGCONT` | 19 / 18 | 暂停 / 继续 | `STOP` 不能捕获；`SIGTSTP` 20 号是 `Ctrl+Z` |

#### 先礼后兵：TERM 可捕获，KILL 不可

用一个装了 `SIGTERM` 处理器的脚本做对照（文件名 `~/d4-practice/trap_demo.py`）：

```python
import os, signal, sys, time

def on_term(signum, frame):
    print("got SIGTERM, cleaning up", flush=True)
    sys.exit(0)

signal.signal(signal.SIGTERM, on_term)
print("start pid=%d" % os.getpid(), flush=True)
time.sleep(600)
```

| 终止方式 | `jobs` 通知 | 日志内容 | 退出码 |
|---|---|---|---|
| `kill %1`（`SIGTERM`） | `Done` | `start pid=...` + **`got SIGTERM, cleaning up`** | `0`（处理器里 `sys.exit(0)`） |
| `kill -9 <PID>`（`SIGKILL`） | `Killed` | 只有 `start pid=...` | `137`（128 + 9） |

- TERM 显示 `Done` 而不是 `Terminated`，是因为处理器正常退出、退出码为 0；没装处理器的 `sleep` 才显示 `Terminated`。
- 想拿 KILL 的数字证据：起进程后 `kill -9 "$PID"; wait "$PID"; echo "exit=$?"` → `137`。
- 结论：`SIGKILL` 由内核直接销毁进程，**不给清理机会**；所以脚本里应「先 TERM，等几秒无响应再 KILL」。

#### 三组对照：手动 `exit` ≠ 断开连接

这台机器 `shopt huponexit` 为 **off**，所以原计划里「`exit` 后任务会死」的验证方式**不成立**，
必须拆成三组，否则会得出「`&` 也能扛断线」的错误结论。

| 组 | 做法 | 重连后 `ps -p <PID> -o pid=,ppid=,sid=,tty=,stat=,cmd=` | 结论 |
|---|---|---|---|
| 3A | `sleep 300 &` 后手动 `exit` | **存活**：`1640524 PPID=1 SID=1630611 TTY=? S` | 手动退出不发 HUP；进程被 systemd 收养 |
| 3B | 起同样进程后真断线（Mac 端 `pkill -f 'ssh.*t12ub'`）或 `kill -HUP $$` | **空输出 + `exit=1`** | 内核关 pty → 给会话首进程发 HUP → bash 转发给所有作业 |
| 3C | `shopt -s huponexit` 后 `exit` | **空输出 + `exit=1`** | 3A 的存活是开关造成的，不是 `&` 有保护 |

3A 的细节值得记住：进程 `PPID` 变 1、`TTY` 从 `pts/1` 变成 `?`（pty 已关闭），
但 `SID` 仍是那个已消失会话的 `1630611` —— **它活着只是因为没收到 HUP，会话归属并没有变**。
`shopt -s` 只影响当前 shell，新会话自动回到 off。

#### 四组对照：`nohup` / `disown` / `setsid` 谁真能扛 HUP

用不同 `sleep` 时长当标签（`setsid` 会 fork，`$!` 不一定等于 `sleep` 的 PID，所以用 `pgrep -f` 抓）。
同一次 `kill -HUP $$` 断线后重连检查：

| 方式 | 启动 | 断线前 `SID` / `TTY` | 断线后 | 说明 |
|---|---|---|---|---|
| 普通 `&`（对照） | `sleep 311 &` | shell 的 SID / `pts/1` | **DEAD** | 收到转发的 HUP，默认动作终止 |
| `nohup` | `nohup sleep 313 > long_run.log 2>&1 &` | shell 的 SID / `pts/1` | 存活（SID 不变、`TTY=?`） | 只把 HUP 处置改成忽略，**没脱离会话** |
| `disown` | `sleep 317 &` 后 `disown` | shell 的 SID / `pts/1` | 存活（SID 不变、`TTY=?`） | 从作业表摘掉，shell 转发 HUP 时找不到它 |
| `setsid` | `setsid sleep 319 > /dev/null 2>&1 &` | **自身 PID** / `?`，`PPID=1`、`Ss` | 存活（SID 仍为自身） | 新会话，彻底与控制终端无关 |

结论：`nohup` 和 `disown` 是「让进程收不到/忽略 HUP」，`setsid` 是「换一个会话」；
真正把任务从你的登录会话里独立出去的只有 `setsid`（tmux 内部也是这么做的）。

#### `nohup.out` 的两个细节

```bash
rm -f nohup.out
nohup sleep 5 &
# nohup: ignoring input and appending output to 'nohup.out'
ls -l nohup.out     # -rw------- 1 jqw jqw 0
```

- 只有**没有重定向 stdout** 时才生成 `nohup.out`；已写 `> file 2>&1` 就不会生成
- 权限固定 `600`（coreutils 建这个文件用 0600，不是 umask 推出的 664）
- 那句提示走 **stderr**，所以屏幕看得到、不会进文件
- `sleep` 没有输出，文件是 0 字节；输出内容要等程序真正打印才写入

#### `nohup` 与 `tmux` 对比

| 维度 | `nohup ... &` | `tmux` |
|---|---|---|
| 断 SSH 是否存活 | 是（忽略 HUP，但结果取决于是否重定向/是否 disown） | 是（pane 挂在 tmux server 下，与 sshd 无关） |
| 能否重新接管/交互 | 不能，只能看日志文件 | 能，`attach` 回来继续操作、向上翻输出 |
| 输出落点 | `nohup.out` 或你指定的重定向文件 | pane 的 scrollback，可复制、可分屏 |
| 适用场景 | 一次性脚本、跑完只要结果 | 需要观察进度、中途交互、多任务并行（D17 用） |

tmux 那一列的实现证据（`t12ub` 上已存在的会话，`ps -u jqw` 实测）：

```text
1390255       1 ... Ss   tmux                                  ← server，PPID=1，无终端
1390256 1390255 ... Ss+  -bash                                 ← pane 里的 shell，父进程是 tmux
```

pane 的 shell `PPID` 是 tmux server，不是 sshd，所以断 SSH 碰不到它。


### 10.8 本节易错点

1. `ps aux | grep python` 会匹配到 `grep python` 自己，看起来像「有 python 在跑」；用 `'[p]ython'` 或 `pgrep -af`。
2. `%CPU` 是**平均值**，不是瞬时值；`ps --sort=-%cpu` 的榜首往往是跑了很多天的守护进程。
3. `top -b -n1` 第一屏同样是均值，要增量就 `-n2 -d1`。
4. `VSZ` 是虚拟内存，`RSS` 才是实际占用；`buff/cache` 不算真占用，看 `available`。
5. `TIME` / `TIME+` 是累计 CPU 时间，不是运行时长。
6. `load average` 不是 CPU 使用率，要拿核数当分母。
7. 作业号 `%1` 只属于当前 shell 会话，换终端或断连后失效，只能用 PID。
8. 后台 `&` 不等于脱离终端；`TTY` 还在 `pts/*` 就说明它仍挂在会话上，SSH 一断照样收 `SIGHUP`。
9. `cat > 文件 <<'EOF'` 的终止符**不能有尾随空格或缩进**，否则提示符一直停在 `>`，看起来像卡死；`Ctrl+C` 安全退出。粘贴多行代码时优先用 `printf '%s\n' ...` 或 `python3 - <<'PY'`。
10. `jobs -l` 的 `l` 是字母 L；敲成 `jobs -1` 会报 `invalid option`。`jobs` 只列当前 shell 的作业，`ps` 才是全机视角。

## 11. tmux：可重连的长任务会话

> 2026-10-22 在 `t12ub` 实测：把一个默认名为 `0` 的会话改名为 `work`，跑 `sleep 300` 后 detach，
> 再 `exit` 断开 SSH、重连、`attach` 回来，任务仍在。

### 11.1 解决什么问题

`nohup` 只能保证进程**不死**，看不到、也接不回去；tmux 把 shell 放进一个由 tmux server 托管的伪终端里，
**断 SSH 只是断开了「观看者」，会话本身还在**，重连后 `attach` 就能接着操作、向上翻历史输出。
D17 的全量特征提取跑几小时，必须在这种会话里跑。

| | `nohup ... &` | `tmux` |
|---|---|---|
| 断 SSH 后 | 进程活，但看不见 | 会话活，可重新接管 |
| 交互 | 无 | 有，可输入、可分屏 |
| 输出 | 只能重定向到文件 | pane 的 scrollback，可翻页/复制 |
| 结构 | 一个进程 | 多会话 / 多窗口 / 多窗格 |

### 11.2 会话的完整生命周期

```bash
tmux new -s work          # 新建并进入（名字已存在会报 duplicate session）
#  Ctrl+b 松开，再按 d    → detach：离开，会话继续跑
tmux ls                   # 列出会话（= list-sessions）
tmux attach -t work       # 重新进入；简写 tmux a -t work
tmux rename-session -t 0 work   # 在外部：把名为 0 的会话改名
tmux rename-session work        # 在 tmux 内部：改当前会话
tmux kill-session -t work       # 只杀这一个会话
```

| 动作 | 命令 | 结果 |
|---|---|---|
| 新建 | `tmux new -s work` | 进入新会话 |
| 离开但保留 | `Ctrl+b` `d` | 会话变 detached，进程继续跑 |
| 列出 | `tmux ls` | `work: 1 windows (created ...)` |
| 重新进入 | `tmux attach -t work` | 回到原来的 pane，屏幕内容还在 |
| 改名 | `tmux rename-session -t 0 work` | 标签改变，**不影响进程** |
| 销毁 | `tmux kill-session -t work` | pane 里的进程一起结束 |

> 会话名只是标签。默认名是数字（本次是 `0`），所以照抄 `attach -t work` 会报
> `can't find session: work`；先 `tmux ls` 看真实名字。

### 11.3 前缀键与常用操作

所有快捷键都要先按 **`Ctrl+b`，松开，再按功能键**（不是组合键同时按）。

| 操作 | 按键 | 说明 |
|---|---|---|
| detach | `Ctrl+b` `d` | 最常用，离开不杀 |
| 新建窗口 | `Ctrl+b` `c` | 状态栏出现 `1:bash*` |
| 切换窗口 | `Ctrl+b` `n` / `p` / 数字 | 下一个 / 上一个 / 指定编号 |
| 列出窗口 | `Ctrl+b` `w` | 交互式选择 |
| 重命名窗口 | `Ctrl+b` `,` | 如改成 `feat` |
| 左右分屏 | `Ctrl+b` `%` | |
| 上下分屏 | `Ctrl+b` `"` | |
| 切换窗格 | `Ctrl+b` `o` | |
| 关闭窗格/窗口 | `exit` 或 `Ctrl+b` `x` | `x` 会先确认 |
| 进入复制模式 | `Ctrl+b` `[` | 用方向键/`PgUp` 翻 scrollback |

复制模式里：`q` 退出，`/关键词` 向上搜索，`空格` 开始选区，`Enter` 复制到 tmux 缓冲区。
停止一个前台任务仍然是 `Ctrl+C`，与 tmux 无关。

### 11.4 状态栏怎么读

```text
[work] 0:bash*                      "t12ub" 14:30 22-Oct-26
```

- `[work]`：当前会话名
- `0:bash*`：窗口编号 `0`、窗口名 `bash`、`*` 表示当前活动窗口
- `"t12ub"` 与时间：主机名与系统时间
- 底部出现这条栏，就说明你在 tmux 里；`echo $TMUX` 有值也是判据

### 11.5 实测：detach → 断 SSH → attach

```bash
tmux attach -t work
cd ~/d4-practice
sleep 300                 # 前台运行，提示符消失
# Ctrl+b，松开，再按 d     → 回到普通 shell
tmux ls                   # work: 1 windows (created ...)   无 (attached) = 已 detach
exit                      # 彻底断开 SSH
```

重连后：

```bash
ssh t12ub
tmux ls                   # work 仍在
tmux attach -t work       # 回到 pane，sleep 300 仍在跑 → Ctrl+C 结束
```

结论：pane 里的进程与会话都没有感知到 SSH 断开；`attach` 回来连屏幕历史都还在。

### 11.6 机制：为什么断 SSH 不影响 tmux

实测 `ps` 证据（同一时刻）：

| 对象 | PID | PPID | SID | TTY | STAT | 含义 |
|---|---|---|---|---|---|---|
| tmux server | 1390255 | **1** | 1390255 | `?` | `Ss` | 已被 init 收养，没有控制终端 |
| pane 里的 bash | 1390256 | **1390255** | 1390256 | `pts/4` | `Ss+` | 父进程是 tmux server，不是 sshd；自己是新会话首进程 |

链条与 SSH 登录的对照：

```text
sshd(1630610) → bash(1630611) → 命令          ← 断线时 HUP 沿这条链传下去
tmux server(1390255, PPID=1) → bash(1390256)  ← 与 sshd 无关，HUP 传不到
```

tmux 为每个 pane 分配一个 pty 并 `setsid`，所以 pane 的 shell `SID` 等于自身；
SSH 断开只销毁 sshd 分配的那个 pty，碰不到 tmux 的 pty。
这与 §10.7 的结论一致：**只有换会话（`setsid`/tmux）才真正脱离登录会话**。

### 11.7 不进入会话也能排查

```bash
tmux ls
tmux list-windows -t work
tmux list-panes -t work -F '#{window_index}.#{pane_index} pid=#{pane_pid} tty=#{pane_tty} cmd=#{pane_current_command}'
tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index} pid=#{pane_pid} cmd=#{pane_current_command}'
```

实测输出：

```text
0: bash* (1 panes) [81x29] [layout c6dd,81x29,0,0,0] @0 (active)
0:0.0 pane_pid=1390256 tty=/dev/pts/4 cmd=bash
```

`cmd=bash` 表示 pane 里当前没有前台任务；如果显示 `python3`/`sleep`，说明任务正在里面跑。
`#{pane_pid}` 是 pane 里 shell 的 PID，可以继续用 `ps` 深挖。

### 11.8 共享服务器上的注意点

`pgrep -a tmux` 会列出**全机所有用户**的 tmux 进程。本次实测混入了别人的会话：

```text
1390255 tmux new                          # jqw，自己的 server
1431887 tmux -2 new-session -s wk         # xufumin，别人的 server
1572539 tmux attach-session -t wk         # 别人的客户端
```

- 用 `pgrep -u "$USER" -a tmux` 只看自己的；用 `ps -o user= -p <PID>` 核对属主
- **禁止 `tmux kill-server`**：它杀掉该 server 上所有会话；只用自己的 `kill-session -t <名字>`
- 自己只有一个 server 时，`tmux new` 与 `tmux attach` 都作用在同一个 server 的不同会话上
- `tmux ls` 只列**当前 socket** 的会话，看不到别人（用户不同 → socket 不同）

### 11.9 易错点

1. `tmux attach -t work` 报 `can't find session`：会话默认名可能是数字，先 `tmux ls`。
2. detach 不是 `Ctrl+d` 也不是 `exit`：在提示符下 `exit` 会结束 pane 里的 shell（窗口随之关闭）；任务在跑时应先 `Ctrl+b d` 离开。
3. `Ctrl+b` 与 `d` 要**先后按**，同时按会被当成普通输入。
4. `tmux ls` 没写 `(attached)` 就是 detached；别把「没有标记」误判为异常。
5. `kill-session` 前先 `tmux ls` 确认名字；`kill-server` 会波及同 server 的所有会话。
6. 在 `~` 里随手跑 `touch result.txt` 会落在 `/home/jqw/`，练习产物统一放 `~/d4-practice/`。

## 12. 环境变量与 PATH

> 2026-10-22 在 `t12ub` 实测。目标：把「`pip install` 后 `command not found`」拆成可复现的几种原因，
> 每种都亲手制造一次，再修好。

### 12.1 变量、环境、`export`

- **shell 变量**只属于当前 shell，子进程看不到
- **环境变量**是「会传给子进程的变量」，`export` 就是给变量打上这个标记
- `export MYVAR=test` = 赋值 + 导出；`MYVAR=test` 只是赋值

```bash
MYVAR=test
bash -c 'echo "子进程: ${MYVAR:-空}"'   # 子进程: 空
export MYVAR=test
bash -c 'echo "子进程: $MYVAR"'         # 子进程: test
env | grep '^MYVAR'                     # 只列环境变量
```

- `export` 影响的是**当前 shell 及其之后启动的子进程**，改不了父进程
- 在脚本里 `export PATH=...` 只对脚本自己（及其子命令）有效，脚本结束就没了
- `set` 列全部变量（含未导出），`env` / `printenv` 只列已导出的

### 12.2 PATH 的搜索规则

`PATH` 是一串用 `:` 分隔的目录，shell 执行裸命令时**从左到右找第一个同名可执行文件**，
命中就停，后面即使有同名版本也不看。**顺序即优先级。**

本次 `echo $PATH | tr ':' '\n'`（新增演示目录之前）：

```text
/home/jqw/.npm-global/bin
/usr/local/sbin
/usr/local/bin
/usr/sbin
/usr/bin
/sbin
/bin
/usr/games
/usr/local/games
/snap/bin
```

| 工具 | 作用 | 局限 |
|---|---|---|
| `command -v 名字` | 最标准：打印解析结果，找不到返回非 0 | 不解释来源类型 |
| `type -a 名字` | 列出**全部**同名来源（别名/函数/内置/多个路径） | 输出更长 |
| `which 名字` | 打印第一个匹配路径 | 某些系统不认别名/函数 |

`type -a python3` 输出两条：

```text
python3 is /usr/bin/python3
python3 is /bin/python3
```

不是两个文件——`/bin` 是指向 `/usr/bin` 的软链接，PATH 里两条目录都命中同一个文件。

### 12.3 「command not found」的四类原因

| 类别 | 本次实例 | 判据 |
|---|---|---|
| ① 没装 | `pip`、`pip3`、`python` | `type -a` 完全没有；Ubuntu 会提示 `apt install python3-pip` |
| ② 装了但目录不在 PATH | `~/d4-practice/bin/demo-cmd` | 裸命令 `exit=127`，绝对路径能跑 |
| ③ 装了、PATH 也对，但 hash 指向旧路径 | 删掉文件后仍报旧路径 | 报错是 `bash: /旧/路径: No such file or directory`，不是 `command not found` |
| ④ 装进了另一个环境却没用那个环境 | `python3 -m pip`、venv | 报 `No module named pip` / 装到 venv 的 `bin/` 但 shell 用系统解释器 |

本次还确认：这台机器 **没有 `python`**（只有 `python3`）、**没有 pip**、
建 venv 缺 `ensurepip`（需 `apt install python3.12-venv`）、`conda`/`mamba` 不属于当前用户、`docker` 存在。

```text
$ python3 -m pip --version
/usr/bin/python3: No module named pip      # exit=1
$ python3 -m venv ~/d4-practice/venv-demo
The virtual environment was not created successfully because ensurepip is not available.
... apt install python3.12-venv            # exit=1
```

### 12.4 实测四组

#### A. 现状

```bash
echo $SHELL                       # /bin/bash
echo $PATH | tr ':' '\n'
type -a python                    # bash: type: python: not found
type -a python3                   # /usr/bin/python3、/bin/python3
which pip; which pip3             # Command 'pip' not found ... apt install python3-pip
echo "$PATH" | tr ':' '\n' | grep "\.local/bin" || echo "PATH 不含 ~/.local/bin"
```

结论：`pip install --user` 默认把脚本装进 `~/.local/bin`，而它不在 PATH —— 这是最常见的「装了却找不到」。

#### B. 制造并临时修复

```bash
mkdir -p ~/d4-practice/bin
printf '#!/usr/bin/env bash\necho "demo-cmd from $0"\n' > ~/d4-practice/bin/demo-cmd
chmod +x ~/d4-practice/bin/demo-cmd

demo-cmd; echo "exit=$?"                  # demo-cmd: command not found / exit=127
command -v demo-cmd || echo "PATH 里找不到"
~/d4-practice/bin/demo-cmd                # demo-cmd from /home/jqw/d4-practice/bin/demo-cmd

export PATH="$HOME/d4-practice/bin:$PATH" # 前置 = 更高优先级
demo-cmd                                  # 可直接运行
command -v demo-cmd                       # /home/jqw/d4-practice/bin/demo-cmd
```

**判定顺序**：能绝对路径跑 → 文件、权限、解释器都没问题，问题只在 PATH。

#### C. 持久化：写进 `~/.bashrc`

```bash
echo 'export PATH="$HOME/d4-practice/bin:$PATH"  # d4-demo' >> ~/.bashrc
tail -n 3 ~/.bashrc
exit          # 不 source，直接重连
ssh t12ub
demo-cmd                              # 仍可用 → 登录时读取了 .bashrc
```

实测 `~/.bashrc` 末尾两行（注意**书写顺序决定最终优先级**）：

```bash
export PATH="$HOME/.npm-global/bin:$PATH"
export PATH="$HOME/d4-practice/bin:$PATH"  # d4-demo
```

每条都是**前置**，后执行的插到最前，所以新会话 PATH 头部是
`~/d4-practice/bin` → `~/.npm-global/bin` → … 。这也说明了为什么 npm 全局安装的 `kilo` 能找到（D6 会用到）。

- Ubuntu 登录时：`~/.profile` 会 source `~/.bashrc`（交互式），所以 SSH 新会话也生效
- `source ~/.bashrc`（等价 `. ~/.bashrc`）在**当前 shell** 重新执行该文件，改完立即生效
- 不 source 又不开新会话，改动就「看不见」——新手第一大坑
- macOS 默认是 zsh，对应文件是 `~/.zshrc`

#### D. hash 缓存：删除后仍指向旧路径

```bash
shopt checkhash                     # 默认 off：不校验缓存路径是否还存在
mkdir -p ~/d4-practice/shadow
printf '#!/usr/bin/env bash\necho "shadow 版本"\n' > ~/d4-practice/shadow/demo-cmd
chmod +x ~/d4-practice/shadow/demo-cmd
export PATH="$HOME/d4-practice/bin:$HOME/d4-practice/shadow:$PATH"

demo-cmd                            # 先跑 bin 版本，路径被记入 hash
hash                                # hits 1  /home/jqw/d4-practice/bin/demo-cmd
rm ~/d4-practice/bin/demo-cmd
demo-cmd; echo "exit=$?"            # bash: /home/jqw/d4-practice/bin/demo-cmd: No such file or directory / 127
hash -r
demo-cmd                            # shadow 版本
```

- `hash` 显示 shell 的**命令路径缓存**：命中次数 + 路径
- `checkhash=off` 时 bash 直接用缓存路径执行，所以报的是**旧路径不存在**，而不是重新搜索
- `hash -r` 清空缓存后按 PATH 重新查找
- 同理：刚 `pip install` 一个同名新版本，shell 可能还跑着旧路径，重开终端或 `hash -r` 就好

#### 附：拼写错误的干扰项

```bash
emo-cmd        # emo-cmd: command not found
```

报错文本和「装了但不在 PATH」几乎一样，所以排错第一步永远是 `command -v 名字`：
名字拼错 → 任何目录都没有；装了没进 PATH → 目录里有但 PATH 没有。

### 12.5 排错流程（按顺序执行）

```text
1. command -v 名字            → 空：没装或拼错（type -a 再确认）
2. 绝对路径能跑吗             → 能：PATH 问题；不能：文件/权限/解释器/shebang
3. echo $PATH | tr ':' '\n'   → 目录在不在？排第几？有没有被后面的同名版本抢先？
4. 目录在、文件在，仍报旧路径 → hash -r
5. pip 装的东西               → 确认装进了哪个环境：~/.local/bin、venv/bin、conda env bin
6. 改了 .bashrc 不生效        → source ~/.bashrc 或重开会话；确认改的是当前 shell 对应的文件（bash vs zsh）
```

| 现象 | 最可能原因 | 立即验证 |
|---|---|---|
| `xxx: command not found` | 没装 / 拼错 / 不在 PATH | `command -v`、`type -a` |
| 报错里带一个完整旧路径 | hash 缓存 | `hash -r` |
| `No module named pip` | 该解释器没装 pip | `python3 -m pip --version` |
| 装了包但模块/命令都没有 | 装进了别的环境 | `which python`、`which pip`、`pip --version` |
| `bad interpreter: ^M` | Windows 换行 | `sed -i 's/\r$//' 文件` |

### 12.6 易错点

1. `export PATH=$HOME/bin:$PATH` 末尾的 `:$PATH` 不能省，否则整条 PATH 被覆盖，`ls`、`vim` 都会找不到（当前 shell 用绝对路径 `/bin/ls` 或重开终端恢复）。
2. PATH 里加 `.`（当前目录）有风险：在别人目录里执行同名脚本会被劫持。
3. `.bashrc` 改完不 `source` 也不重连，当然不生效；但 `source` 只影响当前会话，其他已开终端不受影响。
4. 脚本里的 `export` 出了脚本就失效；要持久化必须写进 shell 配置文件。
5. `which` 看不到别名和函数，排错优先 `type -a`。
6. 目录存在不代表能执行：`chmod +x` 之外，挂载点若带 `noexec` 也会 `Permission denied`。
7. `PATH` 里的目录不要带尾随空格或不可见字符，肉眼看不出来但会静默失效。
