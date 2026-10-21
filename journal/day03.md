---
day: 03
date: 2026-10-21
theme: Linux CLI（一）文件、权限、管道、文本处理
gate: -
---

# Day 03｜Linux CLI（一）：文件、权限、管道、文本处理

## 今日目标

不用图形界面完成"**找文件 → 过滤 → 统计 → 存档**"。

## 今日要交付什么

> 09:00–09:20 计划时段填写，收尾时逐项打勾并补证据。

| # | 交付物 | 具体要求 | 证据 | 状态 |
|---|---|---|---|---|
| 1 | `results/tables/name_audit.csv` | 造 30 个假 DICOM 文件名（`LUNG1-001_ct_01.dcm` 之类），用纯命令行统计每患者文件数、找出不符合 `<PID>_<modality>_<n>.dcm` 的文件，结果写入 CSV | 文件本身 + 生成命令 | ✅（`ba16470`） |
| 2 | `notes/linux-cli.md` | 目录结构图 + 权限数字换算表（`755`=`rwxr-xr-x`）+ **≥5 条管道实例** + 我的 awk 一行流合集 | 文件本身 | ✅（`9a1ec53`+） |
| 3 | `journal/day03.md` | 今日目标、完成表、关键命令、卡点报错原文与解决过程、至少 1 条"抓 Kilo 错" | 本文件 | 进行中 |
| 4 | `journal/INDEX.md` D3 行 | 收尾回填日期、主题、commit hash、验收结果 | `journal/INDEX.md` | 待做 |
| 5 | 当日 commit | 至少 1 次，格式 `<scope>: <做了什么> - <一句话结论>`；任务卡指定 `day03: linux cli 文件操作与文本处理` | `git log --oneline` | 进行中（`b6dc05a`…`ba16470`） |

## 今日验收标准（收尾逐条核对）

- [x] `results/tables/name_audit.csv` 已生成，且每一列、每条命令都能解释
- [x] 能口述 `chmod 700` 与 `chmod 644` 分别给属主/属组/其他人什么权限
- [x] `notes/linux-cli.md` 含权限换算表与 ≥5 条管道实例
- [x] 日志含当日报错原文，以及至少 1 条"Kilo 说 X，我核实是 Y"
- [ ] 当日 commit 完成，`journal/INDEX.md` D3 行已回填

## 今日完成

> 收尾时对照「今日要交付什么」逐行填写，证据必须是可复核的文件路径、命令输出或 commit hash。

| 计划 | 状态 | 证据（文件/命令/链接） |
|---|---|---|
| 写入今日交付清单并提交 | ✅ | commit `b6dc05a`，`journal/day03.md` 83 行 |
| 生成 `results/tables/name_audit.csv` | ✅ | commit `ba16470`；31 行（表头 + 30 条），`awk` 筛出 3 条 `valid=no` |
| 写 `notes/linux-cli.md` | ✅ | `9a1ec53` 起持续补充；权限实测、管道、awk 一行流已写入，2 条 awk 标「待验证」 |

## 关键命令

> 边做边记：命令 + 实际输出要点，收尾时整理。

```bash
# ——【Mac】仓库：写入计划并提交 ——
cd ~/Desktop/实习日志
git add journal/day03.md
git diff --staged --stat        # 1 file changed, 83 insertions(+)
git commit -m "day03: 写入今日交付清单与验收标准 - 5 项交付待逐项验证"
git log --oneline -3            # b6dc05a

# ——【t12ub】练习目录 ——
ssh t12ub
pwd                             # /home/jqw/d3-practice
mkdir -p ~/d3-practice/fake_dicom
cd ~/d3-practice
tree -L 2                       # 4 directories, 1 file

# 文件操作
cp demo.txt demo-copy.txt
cp -r sub sub-copy
mv demo-copy.txt demo-renamed.txt
mv demo-renamed.txt sub/
mkdir -p sub/deep/nested
touch fake_dicom/LUNG1-001_ct_01.dcm
ls -l sub/                      # deep/、demo-renamed.txt

# 软链接
ln -s ../demo.txt fake_dicom/link-to-demo
ls -l fake_dicom                # lrwxrwxrwx ... -> ../demo.txt
cat fake_dicom/link-to-demo
echo "第一行" >> fake_dicom/link-to-demo
cat demo.txt                    # 第一行
wc -c demo.txt fake_dicom/link-to-demo   # 10 / 10
readlink fake_dicom/link-to-demo         # ../demo.txt
find . -type l
rm -i fake_dicom/link-to-demo   # 只删链接

# 文本查看
seq 1 100 > numbers.txt
head -n 5 numbers.txt
tail -n 3 numbers.txt
wc -l numbers.txt
less numbers.txt                # /50、n、N、q
sed -n '50p' numbers.txt
seq 1 200 > n200.txt
less n200.txt                   # /50 → 第 50 行；n → 第 150 行
less n200.txt                   # /^50$ 只匹配整行等于 50 的行

# 权限
touch script.sh
ls -l script.sh                 # -rw-rw-r--
chmod 700 script.sh             # -rwx------
chmod 644 script.sh             # -rw-r--r--
chmod +x script.sh              # -rwxr-xr-x（755）
umask                           # 0002

mkdir -p permtest               # drwxrwxr-x（775）
touch permtest/a.txt            # -rw-rw-r--
chmod 600 permtest              # drw-------
cd permtest                     # Permission denied（无 x）
chmod 700 permtest              # drwx------
cd permtest && pwd && cd ..     # 进入成功

# 管道与文本处理
ls -l | wc -l                   # 9（含 total、.、..）
find . -type f | wc -l          # 7
grep -n "5" numbers.txt | head -n 3     # 5:5、15:15、25:25

ls -l | awk '{print $9}' | head         # 文件名列；total 行输出空行
head -n 5 /etc/passwd | cut -d: -f1     # root/daemon/bin/sys/sync
head -n 5 /etc/passwd | awk -F: '{print $1, $7}'
cut -d: -f7 /etc/passwd | sort | uniq -c | sort -rn | head
sed -n '1,5p' numbers.txt               # 只打印第 1–5 行

ls /no-such-path 2>&1 | tee err.log     # 屏幕与文件各一份
cat err.log

ls /no-such-path; echo "status=$?"                        # 2
ls /no-such-path 2>&1 | tee err.log; echo "status=$?"     # 0
set -o pipefail
ls /no-such-path 2>&1 | tee err.log; echo "status=$?"     # 2

# 命名审计（第 7 步，完整脚本见 notes/linux-cli.md 第 8 节）
mkdir -p audit
for p in 1 2 3 4 5 6 7 8 9 10; do
  pid=$(printf "LUNG1-%03d" "$p")
  n=$(( (p - 1) % 5 + 1 ))
  for i in $(seq -f "%02g" 1 "$n"); do
    touch "audit/${pid}_ct_${i}.dcm"
  done
done
ls audit | wc -l                                             # 30

# 改坏 3 个名字：缺序号、modality 大写、PID 小写
mv audit/LUNG1-002_ct_02.dcm audit/LUNG1-002_ct.dcm
mv audit/LUNG1-004_ct_03.dcm audit/LUNG1-004_CT_03.dcm
mv audit/LUNG1-006_ct_01.dcm audit/lung1-006_ct_01.dcm

ls audit | grep -Ev '^LUNG1-[0-9]{3}_ct_[0-9]{2}\.dcm$'      # 3 个不合规
ls audit | grep -Ec '^LUNG1-[0-9]{3}_ct_[0-9]{2}\.dcm$'     # 27
ls audit | grep -c  '^LUNG1-[0-9]{3}_ct_[0-9]{2}\.dcm$'     # 0（BRE 不识别 {3}）
ls audit | grep -c  '^LUNG1-[0-9]\{3\}_ct_[0-9]\{2\}\.dcm$'  # 27

# 按 PID 统计，生成 CSV 后核对
ls audit | cut -d_ -f1 | sort | uniq -c                      # LUNG1-006 消失，lung1-006 单列
wc -l name_audit.csv                                         # 31
awk -F, 'NR>1 && $5=="no"' name_audit.csv                    # 3 行

# 回 Mac 仓库
scp t12ub:~/d3-practice/name_audit.csv results/tables/

# scp 完整性校验
shasum -a 256 results/tables/name_audit.csv      # Mac
sha256sum ~/d3-practice/name_audit.csv           # t12ub
# 两端均为 8d2dc622597302c889bbbc19428246f943e2713d522578444cc834b570440654
```

## 卡点与报错（本节不许空着）

### 卡点 1：`ls -l deep` 报 No such file or directory

- **报错原文**：
  ```text
  ls: cannot access 'deep': No such file or directory
  ```
- **我的猜测**：以为 `mkdir -p sub/deep/nested` 会在当前目录也建一个 `deep`。
- **验证过程**：`ls -l sub/` 能看到 `deep`，说明它只在 `sub/` 下。
- **根因**：`deep` 在 `sub/` 下，相对路径以当前目录 `~/d3-practice` 为基准。
- **解决**：`ls -l sub/deep`。
- **下次怎么避免**：相对路径先想清“从当前目录怎么走”，不确定就用 `find . -name deep`。

### 卡点 2：`less` 里输入 50 后出现 `^[OA50: command not found`

- **报错原文**：
  ```text
  50
  ^[OA50: command not found
  ```
- **我的猜测**：以为在 `less` 里直接输入数字就能搜索。
- **验证过程**：重新进入 `less`，先按 `/` 再输入 `50` 回车，能正常跳到匹配行；按 `n` 跳下一个。
- **根因**：当时已经不在 `less` 里，而在 shell 提示符下；`^[OA` 是上方向键的转义序列，与 `50` 拼成命令名。`less` 内搜索必须先按 `/`。
- **解决**：在 `less` 内用 `/50` 回车搜索，`n` 下一个、`N` 上一个、`q` 退出；终端状态异常时执行 `reset`。
- **下次怎么避免**：看屏幕底部提示判断是否还在 `less`；搜索一律先按 `/`。

### 卡点 3：管道让失败命令的退出码变成 0

- **现象**：
  ```text
  ls: cannot access '/no-such-path': No such file or directory
  status=0
  ```
- **我的猜测**：以为只要屏幕出现报错，退出码就一定非 0。
- **验证过程**：单独执行 `ls /no-such-path` 得 `status=2`；接 `2>&1 | tee err.log` 后得 `status=0`；执行 `set -o pipefail` 后再跑，恢复为 `status=2`。
- **根因**：管道默认只返回**最后一个命令**的退出码，`tee` 成功即返回 0，`ls` 的失败被吞掉。
- **解决**：脚本开头启用 `set -o pipefail`（配合 `set -euo pipefail`），让管道中任一命令失败都算失败。
- **下次怎么避免**：看到报错文字时不要只看输出，还要 `echo $?` 确认退出码。

### 卡点 4：引号未闭合导致 `>` 续行

- **现象**：执行 `echo "status=$?` 后没有回到提示符，出现 `>`，后续输入都被吞进字符串。
- **我的猜测**：以为 `>` 是重定向符，命令已经执行。
- **验证过程**：按 `Ctrl+C` 取消，补上结尾双引号重新执行，输出 `status=2` 正常。
- **根因**：双引号没有闭合，bash 显示的是**续行提示符 PS2**，等待剩余输入。
- **解决**：`Ctrl+C` 取消当前行，重新输入完整命令。
- **下次怎么避免**：引号成对输入；提示符变成 `>` 时先 `Ctrl+C`，不要继续敲命令。

### 卡点 5：`grep -c` 返回 0，但文件明明有 27 个合规名

- **现象**：
  ```text
  ls audit | grep -Ec '^LUNG1-[0-9]{3}_ct_[0-9]{2}\.dcm$'   # 27
  ls audit | grep -c  '^LUNG1-[0-9]{3}_ct_[0-9]{2}\.dcm$'   # 0
  ```
- **我的猜测**：以为 `{3}` 在两套正则里写法相同。
- **验证过程**：加 `-E` 得 27；把 `{3}` 改成 `\{3\}`、`{2}` 改成 `\{2\}` 后，不加 `-E` 也得到 27。
- **根因**：默认 BRE 中 `{n}` 是普通字符；只有 `-E`（ERE）或转义后的 `\{n\}` 才是“重复 n 次”。
- **解决**：正则里用 `{n}` 时统一加 `-E`，或写成 `\{n\}`。
- **下次怎么避免**：看到计数为 0 先检查正则语法和分隔符，不要先怀疑文件。

## Kilo 使用记录

- 问：`tree -L 2` 是什么，`nested` 有什么用。答：树形列目录，`-L` 限制层数；`nested` 只用于验证层数。核实：`tree -L 2` 输出 4 个目录 1 个文件，`tree -L 3` 才能看到 `nested`，一致。
- 问：`cp`、`cp -r`、`ls -lah` 在干什么。答：复制文件、递归复制目录、长格式列出含隐藏项。核实：输出出现 `demo-copy.txt`、`sub-copy`，权限列 `-rw-rw-r--`，一致。
- 问：两条 `mv` 和一条 `mv` 的区别。答：目标是目录则移入，否则改名；可合并为 `mv 源 sub/新名`。核实：`ls -l sub/` 显示 `demo-renamed.txt`，当前目录已无该文件，一致。
- 问：软链接怎么用。答：当普通路径读写，写入落到目标文件；删链接不影响目标。核实：`wc -c` 两边同为 10 字节，`cat demo.txt` 出现“第一行”，删链接后 `demo.txt` 仍在，一致。
- 问：`n` 到底怎么按。答：搜索后按 `n` 跳下一个、`N` 上一个，不需要回车。核实：`/5` 后连续按 `n`，依次跳到 5、15、25，一致。
- 问：`/50` 是跳到含 50 的行还是第 50 行。答：`/` 搜内容，`50g` 才是跳行号。核实：`seq 1 200` 中 `/50` 后按 `n` 跳到第 150 行，一致。
- 问：`mkdir -p` 和 `nested` 的作用。答：`-p` 一次建多层且已存在不报错；`nested` 只是第三层目录名。核实：`mkdir -p sub/deep/nested` 成功，`ls -l sub/deep` 能看到 `nested`，与解释一致。
- 问：`^[OA50: command not found` 是什么。答：当时已退出 `less`，方向键转义序列与 `50` 被拼成命令名。核实：重新进入 `less` 用 `/50` 正常，一致。
- 问：权限数字怎么来的、`umask` 是什么。答：`r=4`、`w=2`、`x=1`，三位分别对应属主/属组/其他人；`umask` 是新建文件/目录时默认屏蔽掉的位。核实：`chmod 700` → `-rwx------`，`chmod 644` → `-rw-r--r--`，`umask` 输出 `0002`，与换算一致。
- 问：什么是管道。答：`|` 把前一条的 stdout 交给后一条的 stdin，stderr 需要 `2>&1` 才会进入管道。核实：`ls -l | wc -l` 得 9，`grep ... | head -n 3` 只输出 3 行，一致。
- 问：命令明明报错，为什么说没问题。答：路径是故意写错的，用于验证 `2>&1 | tee`；报错文字与退出码是两件事。核实：`err.log` 与屏幕内容一致；退出码依次为 2、0、2，与解释一致。
- **抓错记录 1**：Kilo 说 `chmod +x` 后应为 `-rwxr--r--`（744）；我实测是 `-rwxr-xr-x`（755）。核实：不指定 `u/g/o` 时 `+x` 作用于全部三类，`umask 0002` 不含 `x` 位，不会挡住。结论：`chmod u+x` 才是 744，`chmod +x` 是 755。
- **抓错记录 2**：Kilo 给 `git add journal/day03.md` 时只标了【Mac】，没写明必须先进入仓库目录；我在 `~` 下执行报 `fatal: not a git repository`。核实后确认：命令本身没错，缺的是工作目录前提。结论：照抄命令前先核对 `pwd`。
- **抓错记录 3**：Kilo 说“基础正则下也能用，因为这里没写 `{}`”，但给出的命令里含 `{3}`、`{2}`。我实测 `grep -c` 为 `0`，加 `-E` 或写成 `\{3\}` 才是 `27`。核实：BRE 不把 `{n}` 当量词。结论：用 `{n}` 必须配 `-E` 或转义。

## 今日结论

> 收尾时补 3–7 条，只写验证过的结论；说不清为什么的结果标 `未验证`。

1. 服务器只做练习（`~/d3-practice`），仓库、日志和 commit 都在 Mac；产出要 `scp` 回仓库再提交。
2. 软链接不复制内容，读写跟随目标；删除链接不影响目标文件（`wc -c` 两边同为 10 字节，删链接后 `demo.txt` 仍在）。
3. `less` 中 `/` 搜内容、`n`/`N` 前后匹配、`数字g` 跳行号；`/50` 匹配包含 50 的行，`/^50$` 才匹配整行等于 50。
4. 相对路径以当前目录为基准：`deep` 在 `sub/` 下时，必须写 `sub/deep`；提交信息要覆盖实际改动，`b6dc05a` 只含 `journal/day03.md` 一个文件。
5. 权限：数字按 `r=4`、`w=2`、`x=1` 分三类相加；`chmod +x` 不给 `u/g/o` 时三类都加（644→755），`chmod u+x` 才只给属主（644→744）；`umask 0002` 下新文件 `664`、新目录 `775`；目录没有 `x` 时 `cd` 报 `Permission denied`。
6. 管道只传 stdout，stderr 要 `2>&1`；管道退出码默认取最后一条命令，脚本必须 `set -o pipefail`；文本处理分工：`awk` 按列、`cut` 按分隔符、`sort | uniq -c` 先排序再计数、`sed -n` 取行范围。
7. 命名审计：30 个文件中 27 个合规、3 个不合规；`valid=no` 行的 `modality`/`seq_no` 留空；大小写错误会把同一患者拆成两个 PID（`LUNG1-006` → `lung1-006`），审计必须在合并临床表之前完成；`patient_file_count` 按 PID 前缀统计，包含不合规文件。

## 明日 3 件事

- [ ] 读 `每日计划/Day04.md`。
- [ ] 完成 Linux CLI 二（进程/脚本/环境变量）练习。
- [ ] 写 `notes/linux-cli.md` 下半，补 `journal/INDEX.md` D4 行。
