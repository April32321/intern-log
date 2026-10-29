---
day: 09
date: 2026-10-29
theme: Conda 环境隔离与可重建
gate: -
---

# Day 09｜Conda：环境隔离与可重建

## 今日目标

- 用户级安装 Miniconda（不 sudo），环境装在 `$HOME/miniconda3`
- 建项目专用环境 `radiomics`，锁定 **Python 3.10**
- 分层装依赖：conda/conda-forge 优先，pip 只补 conda 缺失的包
- 导出 `environment.yml` / `conda-explicit.txt` / `pip-freeze.txt` 三个锁定文件
- **删掉环境后能一次重建**（今天的硬验收）

## 今日完成

| 计划项 | 状态 | 证据 |
|---|---|---|
| 确认目标机环境 | ✅ | t12ub：`Linux x86_64`，Ubuntu 24.04.4 LTS（noble）；`/` 3.9T，可用 3.5T，家目录在本地 LVM 非 NFS |
| 打通 t12ub → GitHub | ✅ | Mac 侧 22 端口 `kex_exchange_identification` 被断；改用 agent 转发 `ssh -A t12ub` 后 `git clone` 成功（296 objects） |
| 克隆仓库到远端 | ✅ | `/home/jqw/intern-log`，`git clone git@github.com:April32321/intern-log.git` |
| 安装 Miniconda | ✅ | `Miniconda3-latest-Linux-x86_64.sh`（211MB）→ `~/miniconda3`；`conda 26.9.4`；base 为 Python 3.14.9 |
| `conda init bash` | ✅ | 修改 `~/.bashrc`，重开会话后 `(base)` 生效 |
| 创建 `radiomics` 环境 | ✅ | Python **3.10.22**；`which python` → `/home/jqw/miniconda3/envs/radiomics/bin/python` |
| 装科学计算依赖（conda-forge） | ✅ | numpy 1.26.4 / pandas 2.3.3 / scipy 1.15.2 / scikit-learn 1.7.2 / matplotlib 3.10.9 / seaborn 0.13.2 / tqdm 4.70.0 / pydicom 3.0.2 / SimpleITK 2.5.6 |
| `lifelines` / `scikit-survival` | ✅ | conda-forge：lifelines 0.30.0；scikit-survival 0.25.0（`np2py310h99cdc5b_1`） |
| `pyradiomics` | ✅ | conda-forge 无此包 → pip 源码编译：3.0.1（`Channel=pypi`），附带 PyWavelets 1.8.0 / pykwalify 1.8.0 / docopt 0.6.2 / ruamel.yaml 0.19.1 |
| 功能验证 | ✅ | `import radiomics, lifelines, sksurv, pydicom` → `OK`；`from radiomics import featureextractor` → `featureextractor OK` |
| 编写 `env/environment.yml` | ✅ | 手工编写（未用 `--from-history`，避免 `prefix:` 与 `defaults`）；`yaml.safe_load` 通过、无 Tab。初版含 `pip:` 段（`versioneer` + `pyradiomics==3.0.1`），卡点 11 之后**整段删除**，只保留 `- pip` |
| `jupyter` | ✅ | `jupyter --version`：jupyterlab 4.6.3 / notebook 7.6.2 / ipykernel 7.3.0 / jupyter_core 5.9.1 |
| 导出 `conda-explicit.txt` / `pip-freeze.txt` | ✅ | 重建后导出；渠道分布 `311 conda-forge + 6 pypi`，`defaults` 零条 |
| 重建前快照 | ✅ | `/tmp/before-rebuild-conda.txt`、`/tmp/before-rebuild-pip.txt`（首次误在 `(base)` 下导出，已重做，见卡点 9） |
| **删环境重建一次通过** | ✅ | 第一次 `PIP_NO_BUILD_ISOLATION=1 conda env create` 在 pip 段失败（见卡点 11）；改为「`conda env create` + 单独 `pip install --no-build-isolation pyradiomics`」后成功，`import radiomics, lifelines, sksurv, pydicom` → `OK`，日志 `logs/day09-rebuild.log` |
| 重建一致性对照 | ✅ | `diff` 发现 4 处**传递依赖**漂移（brotli 1.0.9→1.2.1、urllib3 2.5.0→2.7.0、zstandard 0.25.0→backports.zstd 1.7.0）；15 个顶层包版本与 build 号完全一致 |
| `env/README.md` | ⬜ 未开始 | 内容已拟好，待落盘 |
| `env/rebuild.sh` | ⬜ 未开始 | 用于把「建环境 + 编译 pyradiomics」固化成一条命令 |

## 环境现状

```bash
$ conda --version
conda 26.9.4

$ python --version && which python
Python 3.10.22
/home/jqw/miniconda3/envs/radiomics/bin/python
```

关键版本（`conda list` 实测）：

| 包 | 版本 | 渠道 |
|---|---|---|
| python | 3.10.22 | conda-forge |
| numpy | 1.26.4 | conda-forge |
| scipy | 1.15.2 | conda-forge |
| scikit-learn | 1.7.2 | conda-forge |
| pandas | 2.3.3 | conda-forge |
| matplotlib | 3.10.9 | conda-forge |
| seaborn | 0.13.2 | conda-forge |
| tqdm | 4.70.0 | conda-forge |
| pydicom | 3.0.2 | conda-forge |
| SimpleITK | 2.5.6 | conda-forge |
| lifelines | 0.30.0 | conda-forge |
| scikit-survival | 0.25.0 | conda-forge |
| **pyradiomics** | **3.0.1** | **pypi（源码编译）** |

## 关键命令

```bash
# 安装 Miniconda（用户级，不 sudo）
curl -fsSL -o /tmp/miniconda.sh \
  https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash /tmp/miniconda.sh -b -p "$HOME/miniconda3"
"$HOME/miniconda3/bin/conda" init bash
exec bash
conda --version      # conda 26.9.4
```

```bash
# 建环境：只用 conda-forge，避开 Anaconda 默认渠道的 ToS 检查
conda create -n radiomics -c conda-forge --override-channels python=3.10 -y
conda activate radiomics
python --version && which python
```

```bash
# 科学计算依赖（conda 侧）
conda install -c conda-forge --override-channels -y \
  numpy pandas scipy scikit-learn matplotlib seaborn jupyter tqdm pydicom simpleitk
conda install -c conda-forge --override-channels -y lifelines scikit-survival
```

```bash
# pyradiomics：conda 无包，走 pip 源码编译
pip install versioneer                                   # setup.py 需要
pip install --no-build-isolation --no-cache-dir pyradiomics
# → Successfully installed PyWavelets-1.8.0 docopt-0.6.2 pykwalify-1.8.0
#   pyradiomics-3.0.1 ruamel.yaml-0.19.1
```

```bash
# 功能验证（两层）
python -c "import radiomics, lifelines, sksurv, pydicom; print('OK')"
python -c "from radiomics import featureextractor; print('featureextractor OK')"
```

```bash
# 锁定文件（导出环节）
conda env export --from-history > env/environment.yml     # 本轮改为手工编写
conda list --export > env/conda-explicit.txt
pip freeze > env/pip-freeze.txt
```

```bash
# 重建验证（实际做法：两段式）

# 1) 环境本体
conda deactivate
rm -rf "$HOME/miniconda3/envs/radiomics"          # env remove 会被 ToS 检查拦住，见卡点 10
conda env create -f env/environment.yml 2>&1 | tee logs/day09-rebuild.log

# 2) pyradiomics 单独编译（yml 的 pip 段做不到，见卡点 11）
conda activate radiomics
pip install versioneer
pip install --no-build-isolation --no-cache-dir pyradiomics==3.0.1 2>&1 | tee -a logs/day09-rebuild.log
python -c "import radiomics, lifelines, sksurv, pydicom; print('OK')" 2>&1 | tee -a logs/day09-rebuild.log
```

> 因此 `environment.yml` 里**不写 `pip:` 段**，只保留 `- pip`；pyradiomics 由 `env/rebuild.sh` 负责补装。

```bash
# 重建后重新导出锁文件（必须在重建之后）
conda list --export > env/conda-explicit.txt
pip freeze > env/pip-freeze.txt
diff /tmp/before-rebuild-conda.txt env/conda-explicit.txt
conda list | awk '{print $4}' | sort | uniq -c | sort -rn    # 渠道分布
```

## 知识点：conda 与 pip 的边界

一句话：**conda 管"环境 + 二进制包 + 依赖求解"，pip 只会在当前环境里装 Python 包，不管环境本身。**

分层的实际理由：

1. conda 包是**预编译二进制**，连 cudatoolkit、gcc 这类非 Python 依赖也能一起给你；pip 的 wheel 只管 Python 层，遇到 C 扩展要现编译。
2. conda 会**全局求解**依赖，`numpy`/`scipy`/`scikit-learn` 的 ABI 组合由它一起算；pip 逐个安装，A 包要求的 numpy 和 B 包要求的不一致时，它只会满足最后一个。
3. 混用后 `conda list` 会出现 `<pip>` 标记（本次 `pyradiomics 3.0.1 pypi_0 pypi` 即是），**这个标记就是在提示：conda 不认识这个包的来源，重建时它拿不到**。

本次的实践结论：

- `numpy/pandas/scipy/sklearn/matplotlib/seaborn/jupyter/tqdm/pydicom/simpleitk/lifelines/scikit-survival` 全部走 conda-forge
- 只有 `pyradiomics` 走 pip，原因不是偏好，是 conda-forge 确实没有、官方 `radiomics` 渠道只构建到 **py39**
- 顺序必须是**先 conda 装齐，再 pip 补缺**。反过来的话，conda 求解时可能把 pip 装的东西重装或降级，`pyradiomics` 会莫名其妙消失

## 知识点：为什么要锁版本

这次有两个非常具体的例子，不是理论：

**例子 1：numpy 2.x 编不动 2021 年的包。**
PyRadiomics 3.0.1 发布于 2021 年，代码里用了 `np.float`、`np.int` 这些在 numpy 1.24 就移除的别名。环境里原本是 numpy 2.2.6，pip 编译时直接失败。降到 `numpy=1.26.4` 后才通过。

**例子 2：`--from-history` 会丢掉 pip 包。**
`conda env export --from-history` 只记录"你显式要求 conda 安装的顶层包"。`pyradiomics` 是 pip 装的，导出的 yml 里**完全没有它**。如果直接拿那份 yml 重建，`import radiomics` 必然失败——而失败发生在重建之后，那时原环境已经删了。

所以锁定文件必须是"三件套"，各自回答不同问题：

| 文件 | 回答什么 | 精度 |
|---|---|---|
| `environment.yml` | 这个环境**由什么组成**（给人看、给 `env create` 用） | 顶层包 + 版本约束 |
| `conda-explicit.txt` | 每个 conda 包的**精确 build 号** | 完全确定 |
| `pip-freeze.txt` | pip 侧每个包的**精确版本** | 完全确定 |

## 知识点：`environment.yml` 的三个隐式陷阱

1. **`prefix:` 行会绑死机器**。`conda env export` 默认会写入 `prefix: /home/jqw/miniconda3/envs/radiomics`，别人拿到后重建会试图往这个路径装，或者直接报错。必须手工删掉。
2. **`channels` 里出现 `defaults` 会触发 ToS**。新版 conda 对 `repo.anaconda.com/pkgs/main`、`/pkgs/r` 要求先 `conda tos accept`，非交互的 `conda env create` 会直接失败。本环境创建时用 `--override-channels` 只走 conda-forge，导出的 yml 也保持单一渠道。
3. **`pip:` 段不会自动带上构建参数，也传不进去**。`--no-build-isolation` 是 CLI flag，yml 里无处可写；实测用 `PIP_NO_BUILD_ISOLATION=1 conda env create` 同样无效（日志里仍出现 `Installing build dependencies`，见卡点 11）。结论是**需要编译的包不能交给 yml 的 `pip:` 段**，必须建好环境后单独安装。本轮最终把 `pip:` 段整段删掉，只保留 `- pip`。

## 知识点：如何确认当前在哪个环境

`conda activate` 是**静默**的：切换到不存在的环境会报错，但切换成功时只有提示符前面多一行括号，没有任何其他输出。所以"我以为在 radiomics 里"是本次最容易被坑的地方。

### 三个判据，从快到准

| 判据 | 命令 | 看什么 |
|---|---|---|
| 提示符前缀 | 看终端 | `(base)` / `(radiomics)` / 无括号 |
| 解释器路径 | `which python` | 必须落到 `.../envs/<name>/bin/python` |
| 解释器自报 prefix | `python -c "import sys; print(sys.prefix)"` | 输出就是当前环境根目录 |
| 环境变量 | `echo $CONDA_DEFAULT_ENV` | 当前激活的环境名 |

一条命令全查：

```bash
echo "env=$CONDA_DEFAULT_ENV"; which python; python -c "import sys; print(sys.prefix)"
```

### 三种提示符的含义

| 提示符 | 含义 | 能做什么 |
|---|---|---|
| `(base)` | conda 自己的运行环境（本次 Python 3.14.9） | 只能运行 conda 命令；**不要**往里装项目包，可能把 conda 弄坏 |
| `(radiomics)` | 项目环境（本次 Python 3.10.22） | 所有项目命令都在这里执行 |
| 无括号 | 没有激活任何环境 | `python` 可能是系统自带的 `/usr/bin/python3`，与项目无关 |

### 本次踩到的实例

执行"重建前快照"时，提示符是 `(base)`，于是 `conda list --export` 和 `pip freeze` 导出的都是 **base（Python 3.14）** 的内容，而不是项目环境。这种错误不会报错，只会安静地产生一份错误的记录——如果没检查就写进 `env/`，等于给了一份假快照。

正确的做法是先切换、再自查、最后导出：

```bash
conda activate radiomics
python -c "import sys; print(sys.prefix)"        # 必须含 envs/radiomics
conda list --export > /tmp/before-rebuild-conda.txt
pip freeze > /tmp/before-rebuild-pip.txt
grep -E "^(python|numpy|pyradiomics)=" /tmp/before-rebuild-conda.txt
# build 串里应出现 py310；pyradiomics 那行应为 pypi_0
```

### 三个易混淆点

1. **`conda activate` 只切换、不创建**。环境不存在时报 `EnvironmentNameNotFound`，需要 `conda create` 先建。
2. **切换后 `python` 仍指向旧路径**，多为 shell 的命令哈希缓存。`hash -r` 清缓存，或 `conda deactivate` 再 `conda activate`。
3. **base 自动激活是 `conda init` 的默认行为**。想关掉：`conda config --set auto_activate_base false`，之后新终端不带 `(base)`，需要时手动激活。

## 知识点：重建 ≠ 恢复

`rm -rf envs/radiomics` 之后再 `conda env create`，环境"回来了"，但**不是把删掉的东西还原**，而是照配方重新装了一份。这两件事的结果常常看起来一样，机制完全不同。

### 两者在做什么

| | 恢复（restore） | 重建（rebuild） |
|---|---|---|
| 输入 | 旧环境的**文件副本**（`cp -a`、`conda pack` 的 tar.gz） | `environment.yml` 这份**文本配方** |
| 过程 | 解压/拷回，逐字节还原本地文件 | 重新求解依赖 → 下载 → 解压 → 编译 |
| 结果 | 与原来**完全一致** | 与原来**功能等价**，细节可能不同 |
| 前提 | 事先必须备份 | 只要有配方，任何时候都能做 |

### 本次的实际时间线

| 步骤 | 动作 | 结果 |
|---|---|---|
| 1 | `conda list --export > /tmp/before-rebuild-*.txt` | 只留下一张"名字=版本=build"的清单，不含任何文件 |
| 2 | `rm -rf ~/miniconda3/envs/radiomics` | 2.2G 删除，**不可恢复**（无回收站） |
| 3 | 第一次 `conda env create` | conda 包到位，pip 段失败（卡点 11） |
| 4 | `rm -rf` 再删一次 | 清掉半个环境 |
| 5 | 改 yml（删 `pip:` 段）后 `conda env create` | 新环境长出 |
| 6 | `pip install --no-build-isolation pyradiomics` | **本地重新编译**出 `pyradiomics-3.0.1` |
| 7 | 验证 | `import radiomics,...` → `OK` |

### 为什么"看起来一模一样"

两个错觉来源：

1. **`~/miniconda3/pkgs/` 缓存被复用**。下载过的包以压缩文件留在缓存里，重建时硬链接过去，既快又像"原来那份"。但它是**安装包缓存**，不是环境备份。
2. **顶层包被钉了版本**。`python=3.10`、`numpy=1.26` 让求解器只能给出同一批顶层包。

### 差异就是证据

重建后的 `diff` 与重建前快照不一致：

```text
+ backports.zstd=1.7.0
~ brotli-python 1.0.9 → 1.2.1
~ urllib3      2.5.0 → 2.7.0
- zstandard     0.25.0
```

四处全部是**传递依赖**，且都挂在 jupyter 那条链上。若是"恢复"，这四处不可能变化；它们变了，说明新环境是**当场求解**出来的。`environment.yml` 只约束顶层，求解器对传递依赖取当时可用的最新版本。

### 由此得到的三层锁分工

| 层次 | 文件 | 保证什么 |
|---|---|---|
| 顶层声明 | `environment.yml` | 能装出**功能等价**的环境 |
| conda 精确快照 | `conda-explicit.txt` | 每个 conda 包的 build 号一致（含 `pypi_0` 行，不能直接用于重建） |
| pip 精确快照 | `pip-freeze.txt` | pip 侧版本一致 |

一句话：**`environment.yml` 保证"能重建"，`conda-explicit.txt` 才保证"一模一样"**，两者本来就不是同一个目标。

### 什么才算真恢复

```bash
cp -a ~/miniconda3/envs/radiomics ~/env-backup/radiomics-$(date +%F)   # 备份
conda pack -n radiomics -o radiomics.tar.gz                            # 打包，可跨机
```

本次**故意不做备份**：留着旧环境作对照，验证的就不是配方，而是备份。真正的可复现性，必须建立在"删掉也能长出来"之上。

## 卡点与报错

### 卡点 1：Mac 侧 GitHub 22 端口握手即断

- **报错原文**：
  ```text
  kex_exchange_identification: Connection closed by remote host
  Connection closed by 20.27.177.113 port 22
  ```
- **我的猜测**：私钥没配好。
- **验证过程**：`ssh -T git@github.com` 报的是 `Connection closed` 而不是 `Permission denied`；`kex_exchange_identification` 发生在 SSH 版本号交换阶段，说明 TCP 通了但中间设备把连接掐了。同一时间在 t12ub 上执行同一条命令，报的是 `Permission denied (publickey)`——**已经走到公钥鉴权**，证明 t12ub 的网络是通的。20.27.177.113 也是 GitHub 的合法地址，DNS 没有污染。
- **根因**：Mac 所在链路对 github.com:22 有干预；而 t12ub 的出口能到 GitHub，只是那台机器上没有私钥。
- **解决**：不修 Mac 的网络，改用 **agent 转发**：Mac 上 `ssh-add --apple-use-keychain ~/.ssh/id_ed25519`，`~/.ssh/config` 加 `ForwardAgent yes`，然后 `ssh -A t12ub`。在 t12ub 上 `ssh-add -l` 能看到 Mac 的 key 指纹，`git clone` 成功。
- **下次怎么避免**：碰到 `kex_exchange_identification` 先判断是网络问题（握手前断开）还是密钥问题（`Permission denied`）；两处报错性质完全不同，别把网络问题当密钥问题排查。

### 卡点 2：t12ub 的 DNS 返回 `198.18.x.x`

- **现象**：`dig +short github.com` → `198.18.0.20`；`nc -vz ssh.github.com 443` 显示"成功"，但本地 `ss -tlnp` 看不到任何代理进程，`env | grep -i proxy` 也为空。
- **根因**：`198.18.0.0/15` 是 RFC 2544 保留网段，实测说明**网关侧**跑了 fake-IP 的透明代理（Clash 类），DNS 由它统一应答。`nc` 的"成功"只是连到了本地代理，不代表真实可达。
- **解决**：不修改 `/etc/resolv.conf`。真正的判据换成 SSH 握手结果（`Permission denied (publickey)` 即表示链路可达）。
- **下次怎么避免**：`nc` 成功配合 fake-IP 时**没有证明力**；判断外网可达性要看应用层握手，或者 `dig` 出来的地址是否落在 198.18/15。

### 卡点 3：`Broken pipe` 导致会话中断

- **报错原文**：`client_loop: send disconnect: Broken pipe`
- **根因**：SSH 空闲超时或网络抖动，NAT/防火墙回收了长连接。
- **解决**：`~/.ssh/config` 给 t12ub 加 `ServerAliveInterval 30`、`ServerAliveCountMax 3`；长任务放进 `tmux`（`tmux new -s d9`，重连 `tmux attach -t d9`）。
- **下次怎么避免**：tmux 恢复后 `SSH_AUTH_SOCK` 指向旧 socket，agent 转发会失效，需重新导出 socket 路径，否则 push 报 `Permission denied`。

### 卡点 4：`CondaToSNonInteractiveError`

- **报错原文**：
  ```text
  CondaToSNonInteractiveError: Terms of Service have not been accepted for the following channels:
      - https://repo.anaconda.com/pkgs/main
      - https://repo.anaconda.com/pkgs/r
  ```
- **我的猜测**：装错了东西或者网络问题。
- **验证过程**：`conda create -n radiomics python=3.10` 未指定渠道，默认去查 Anaconda 的 `pkgs/main`；conda 25+ 对这两个渠道强制 ToS，非交互模式（`-y`）不会弹确认。
- **根因**：Anaconda 默认渠道的条款接受是交互式的，`-y` 下直接抛异常。
- **解决**：改用 `conda create -n radiomics -c conda-forge --override-channels python=3.10 -y`，完全不查询默认渠道。
- **下次怎么避免**：项目环境一律 `-c conda-forge --override-channels`。顺带的好处是导出的 yml 里只有 `conda-forge`，别人重建时不会撞同一个 ToS 提示。

### 卡点 5：`conda search` 不接受多个包名

- **报错原文**：`conda: error: unrecognized arguments: lifelines scikit-survival`
- **根因**：新版 conda 的 `search` 只接受一个 `MATCH_SPEC`（旧版可以并列）。
- **解决**：逐个查；或用正则 `conda search -c conda-forge --override-channels 'pyradiomics|lifelines|scikit-survival'`（引号不能省，否则 `|` 被 shell 当管道）。

### 卡点 6：pip 装 pyradiomics 报构建失败

- **报错原文（两次，逐层暴露）**：
  ```text
  ERROR: Failed to build 'pyradiomics' when getting requirements to build wheel
  # 加 -v 后：
  File "<string>", line 7, in <module>
  ModuleNotFoundError: No module named 'numpy'

  # 改用 --no-build-isolation 后：
  File "<string>", line 8, in <module>
  ModuleNotFoundError: No module named 'versioneer'
  ```
- **我的猜测**：以为是网络或包名问题。
- **验证过程**：`pip install -v` 的 traceback 里路径是 `/tmp/pip-build-env-xxxx/overlay/...`，证明 pip 新建了一个**构建隔离环境**，那里只有 setuptools/wheel，`setup.py` 第 7 行 `import numpy`、第 8 行 `import versioneer` 全部失败。同时当前环境是 numpy 2.2.6，即便不隔离也编不过 2021 年的代码。
- **根因**：pip 默认 PEP 517 构建隔离；且 numpy 2.x 移除了 pyradiomics 3.0.1 依赖的 `np.float`。
- **解决**：
  1. `conda install -c conda-forge --override-channels -y "numpy=1.26"` → 1.26.4
  2. `pip install versioneer`
  3. `pip install --no-build-isolation --no-cache-dir pyradiomics`
  4. 结果 `Successfully installed PyWavelets-1.8.0 docopt-0.6.2 pykwalify-1.8.0 pyradiomics-3.0.1 ruamel.yaml-0.19.1`
- **下次怎么避免**：装老包先查 conda；必须 pip 且带 C 扩展时，直接上 `--no-build-isolation`，并把构建依赖（`versioneer`/`setuptools`/`wheel`）先装进环境。

### 卡点 7：conda 上没有 pyradiomics，官方渠道只到 py39

- **现象**：`conda search -c conda-forge --override-channels pyradiomics` → `PackagesNotFoundError`；`conda search -c radiomics --override-channels pyradiomics` 有包，但 build 是 `py36 / py37 / py38 / py39`，最新 `v3.1.0 py39h9bf148f_0`。
- **根因**：conda-forge 没有该 feedstock；PyRadiomics 官方渠道没有 py310 构建。
- **决策**：守 Python 3.10（计划要求，3.12 支持不稳），接受 pyradiomics 走 pip 源码编译。若换官方渠道就要降到 Python 3.9，与计划冲突，且 `environment.yml` 会多一个第三方渠道依赖。
- **下次怎么避免**：选 Python 版本前先查关键包在各渠道的最高支持 Python 版本，别等装到最后才发现。

### 卡点 8：`curl -fsSL` 看起来像卡死

- **现象**：执行下载后终端长时间无输出，以为死锁。
- **根因**：`-s` 是 silent，故意不打印进度；文件 211MB，实测约 0.8MB/s。
- **解决**：开另一个窗口 `ls -lh /tmp/miniconda.sh` 两次对比大小，字节在增长就是在下载。要进度条就把 `-s` 换 `--progress-bar`。
- **下次怎么避免**：大文件下载不要用 `-s`，或者配 `-w`、`--progress-bar` 观察。

### 卡点 9：在 `(base)` 里导出了"重建前快照"

- **现象**：执行 `conda list --export > /tmp/before-rebuild-conda.txt` 与 `pip freeze > /tmp/before-rebuild-pip.txt` 时，提示符是 `(base)` 而不是 `(radiomics)`，两份文件记的都是 Python 3.14 的 base 环境。
- **我的猜测**：以为上一步 `conda activate radiomics` 仍然有效（同一次会话里执行过）。
- **验证过程**：`grep -E "^(python|numpy)=" /tmp/before-rebuild-conda.txt` 没有 `py310` 字样，也没有 `numpy`；重建后被 `tee` 的日志里 Python 是 3.10，两者对不上。
- **根因**：中途 `conda deactivate` 过，回到 base；`conda activate` 成功时除提示符外没有任何输出，不主动检查就会误判。
- **解决**：先 `conda activate radiomics`，再 `python -c "import sys; print(sys.prefix)"` 确认落在 `envs/radiomics`，然后重新导出。
- **下次怎么避免**：凡是要"导出/安装/建环境"的操作，前面固定加一条 `which python` 或 `echo $CONDA_DEFAULT_ENV` 的自查，不要依赖记忆中的激活状态。

### 卡点 10：`conda env remove` / `conda env create` 被 ToS 拦截

- **报错原文**：
  ```text
  CondaToSNonInteractiveError: Terms of Service have not been accepted for the following channels:
      - https://repo.anaconda.com/pkgs/main
      - https://repo.anaconda.com/pkgs/r
  ```
- **我的猜测**：以为只有"装包"才会触发条款检查。
- **验证过程**：`conda env remove -n radiomics -y` 也报同样的错；给 `conda env create` 加 `--override-channels` 直接报 `conda: error: unrecognized arguments: --override-channels`（该参数只属于 `conda create`/`install`，`env create` 子命令没有）。
- **根因**：conda 25+ 在执行前校验 **`~/.condarc` 里配置的渠道**（默认含 `defaults`），与 `environment.yml` 声明了什么渠道无关；`-y` 非交互模式下无法弹确认，只能抛异常。
- **解决**：
  1. `conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main`
  2. `conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r`
  3. 删环境改用 `rm -rf "$HOME/miniconda3/envs/radiomics"`（环境就是一个目录），绕开 `env remove` 的检查
- **下次怎么避免**：`env/README.md` 里写明这两个前置命令；换台机器重建时会再撞一次，这不是 yml 的问题。

### 卡点 11：`PIP_NO_BUILD_ISOLATION=1` 对 `conda env create` 无效

- **报错原文**（`logs/day09-rebuild.log`）：
  ```text
  Ran pip subprocess with arguments:
  ['/home/jqw/miniconda3/envs/radiomics/bin/python', '-m', 'pip', 'install', '-U',
   '-r', '/home/jqw/intern-log/env/condaenv.imzyzhxd.requirements.txt', '--exists-action=b']
  Pip subprocess output:
  Collecting pyradiomics==3.0.1 ... Installing build dependencies: started
  ... Getting requirements to build wheel: finished with status 'error'
  ERROR: Failed to build 'pyradiomics' when getting requirements to build wheel
  CondaEnvException: Pip failed
  ```
- **我的猜测**：`PIP_NO_BUILD_ISOLATION=1` 会像 `--no-build-isolation` 一样传入 conda 内部那次 pip 调用。
- **验证过程**：日志里出现 `Installing build dependencies: started / finished`——**这就是构建隔离仍然开启的证据**（该步骤只在隔离模式下存在）。而同样的包在 shell 里手动 `pip install --no-build-isolation` 一次就成功，说明问题在"变量没传到子进程"，不是包本身。
- **根因**：`conda env create` 内部另起 pip 子进程执行 `-r requirements.txt`，yml 的 `pip:` 段没有任何位置能传 flag；实测该环境变量也未能生效。
- **解决**：把 `pip:` 段从 `environment.yml` 里删除（只保留 `- pip`），改为两段式：
  ```bash
  conda env create -f env/environment.yml
  conda activate radiomics
  pip install versioneer
  pip install --no-build-isolation --no-cache-dir pyradiomics==3.0.1
  ```
  再用 `env/rebuild.sh` 把两步固化成一条命令。
- **下次怎么避免**：凡是需要编译 C 扩展、且必须带 `--no-build-isolation` 的包，**不要**放进 `environment.yml` 的 `pip:` 段；yml 只放纯 Python、有 wheel 的包。

## 今日结论

1. **conda 环境的边界是 `CONDA_PREFIX`**：`base` 是 conda 自己的运行环境（本次 Python 3.14.9），项目环境 `radiomics` 是完全独立的 3.10.22，两者共用的只有 `pkgs/` 缓存（硬链接），不是运行环境。
2. **`conda activate` 只切换、不创建**，`conda create` 才创建；切换后 `which python` 必须落在 `envs/<name>/bin/python`，否则没生效（必要时 `hash -r`）。
3. **混用 conda 与 pip 的判据是 `<pip>` 标记**：`pyradiomics 3.0.1 pypi_0 pypi` 说明 conda 不认识它，`--from-history` 导出时必然丢——这是"导出文件不等于可重建"的根源。
4. **锁版本不是形式要求**：numpy 2.2.6 → 1.26.4 这一个决定，直接决定了 pyradiomics 能不能装上。
5. **"一次重建成功"没有捷径，但"一条命令"可以有**：`--no-build-isolation` 是 CLI flag，yml 里写不进去，`PIP_NO_BUILD_ISOLATION=1` 环境变量对 `conda env create` 也无效（实测日志里隔离仍开启）。所以 yml 里不放需要编译的包，改用 `env/rebuild.sh` 封装「建环境 + 编译 pyradiomics」两步。
6. **重建 ≠ 恢复**：`conda env create` 是照配方重新装，不是还原文件；`pkgs/` 缓存复用让它看起来"一模一样"，但传递依赖 4 处漂移证明它是当场求解出来的。`environment.yml` 保证"能重建"，`conda-explicit.txt` 才保证"逐包一致"。
7. **网络问题与密钥问题要分开判断**：`kex_exchange_identification` 是链路被干预，`Permission denied (publickey)` 才是密钥；本次两台机器各缺一半，agent 转发正好补齐。
8. **fake-IP 环境下 `nc` 的成功没有意义**：`198.18.0.0/15` 的地址说明流量被网关透明代理接管，可达性要看应用层握手。
9. **长任务必须进 tmux**：`conda env create` 在裸 SSH 会话里被 `Broken pipe` 打断会留半个环境；tmux 会话在服务器端，断线不影响进程，重连 `tmux attach -t d9` 即可。
10. **渠道干净是可以验证的**：`conda list | awk '{print $4}' | sort | uniq -c` 得到 `311 conda-forge + 6 pypi + 0 defaults`，说明"yml 只写 conda-forge"不是纸面声明，而是真实结果。

## 待完成（今日收尾）

- [ ] 写 `env/rebuild.sh`（封装「`conda env create` + 编译 pyradiomics」两步，含前置 ToS 提示）
- [ ] 写 `env/README.md`（重建命令、为什么不能一条 conda 命令、Python 3.10 / numpy 1.26 依据、两层锁分工、ToS 前置条件）
- [ ] t12ub 上 `git add env/ logs/day09-rebuild.log` → `git commit -m "day09: conda 环境与可重建 environment.yml"` → `git push`；Mac 侧 `git pull --ff-only`

> D10 是 G2 门禁，届时需用本文件 + `env/`（yml + 两个锁文件 + README + rebuild.sh）+ `logs/day09-rebuild.log` 证明"删掉能重建"。

## 验收对照（Day09）

- [x] 删环境后能一次重建：实际路径为 `conda env create -f env/environment.yml` + 单独 `pip install --no-build-isolation pyradiomics==3.0.1`（由 `env/rebuild.sh` 固化）；单纯 `conda env create` 无法带上编译参数，见卡点 11
- [x] `python -c "import radiomics"` 无报错（重建后已复验）
- [x] `from radiomics import featureextractor` 正常加载
- [x] `env/` 下 3 个锁定文件齐全（`environment.yml` / `conda-explicit.txt` / `pip-freeze.txt`）；`env/README.md` 与 `env/rebuild.sh` 仍待补
- [x] 能解释 conda 与 pip 的边界（见知识点，本次以 `pyradiomics` 为实例）
- [x] 能解释"为什么要锁版本"（numpy 2.x 编译失败、`--from-history` 丢 pip 包、重建后传递依赖漂移三个实证）
- [x] 能解释"重建 ≠ 恢复"（见知识点，含 `pkgs/` 缓存与 `diff` 漂移证据）

### 三个问题的口头回答（自述稿）

**1. conda 与 pip 的边界在哪？**

conda 管"环境 + 二进制包 + 全局依赖求解"，连 C 库、编译器这类非 Python 依赖也能一起给；pip 只在**当前已激活的环境里**装 Python 包，既不建环境，也不保证多个包之间的依赖一致。
判据是 `conda list` 里的 `<pip>` / `pypi_0` 标记——带这个标记说明包是 pip 装的，conda 不认识它的来源，导出和重建时都拿不到。
本次实践：12 个包全部走 conda-forge，只有 `pyradiomics` 走 pip，因为 conda-forge 没有它、官方 `radiomics` 渠道只构建到 py39。顺序必须是**先 conda 装齐，再 pip 补缺**，反过来会被 conda 求解重装或降级。

**2. 为什么要锁版本？**

因为不锁的话，"重建"结果是不确定的，而且失败往往发生在删掉原环境之后。本次有三个实证：

1. `pyradiomics 3.0.1` 在 numpy 2.2.6 下编译不过，必须 `numpy=1.26`——一个版本函数就决定了装不装得上。
2. `conda env export --from-history` 只记录手装的 conda 顶层包，pip 装的 `pyradiomics` 会**整段消失**；拿那份 yml 重建，`import radiomics` 必然失败。
3. 顶层钉死后重建，仍有 4 个**传递依赖**漂移（brotli、urllib3、`zstandard→backports.zstd`），说明锁的粒度决定复现的精度：锁顶层只能保证"功能等价"。

所以三层锁各司其职：`environment.yml` 保证能重建，`conda-explicit.txt` 保证 conda 包逐一致，`pip-freeze.txt` 保证 pip 侧一致。

**3. 重建和恢复有什么区别？**

**恢复**是把旧环境的文件副本拷回来（`cp -a`、`conda pack`），逐字节一致，但前提是事先备份；**重建**是照着 `environment.yml` 这个配方重新求解、下载、解压、编译，产出的是"功能等价"的新环境，旧数据一点都没被还原。
本次 `rm -rf` 删掉 2.2G 后无法找回，回来的环境里每个文件都是重新解压或编译出来的。
它之所以"看起来一模一样"，是因为 `~/miniconda3/pkgs/` 缓存被硬链接复用、且顶层包钉了版本；但 `diff` 显示 4 处传递依赖不同，证明它是当场求解出来的，而不是被还原的。
一句话：`environment.yml` 保证"删掉能长出来"，`conda-explicit.txt` 才保证"长出来和原来一样"。
