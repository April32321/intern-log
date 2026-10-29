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
| 编写 `env/environment.yml` | ✅ | 手工编写 21 行；`yaml.safe_load` 通过；`pip:` 嵌套解析为 `{'pip': ['versioneer', 'pyradiomics==3.0.1']}`；无 Tab |
| `jupyter` 是否装上 | ⬜ 待确认 | 环境里有 ipython 8.37.0 / python-fastjsonschema / python-json-logger，但未执行 `jupyter --version` |
| 导出 `conda-explicit.txt` / `pip-freeze.txt` | ⬜ 未开始 | 需在重建成功后导出，保证三份文件描述同一环境 |
| `env/README.md` | ⬜ 未开始 | 内容已拟好，待落盘 |
| **删环境重建一次通过** | 🔄 进行中 | 尚未执行 `conda env remove` + `PIP_NO_BUILD_ISOLATION=1 conda env create -f` |

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
# 重建验证（待执行）
conda deactivate
conda env remove -n radiomics -y
PIP_NO_BUILD_ISOLATION=1 conda env create -f env/environment.yml 2>&1 | tee logs/day09-rebuild.log
conda activate radiomics
python -c "import radiomics, lifelines, sksurv, pydicom; print('OK')" | tee -a logs/day09-rebuild.log
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
3. **`pip:` 段不会自动带上构建参数**。`--no-build-isolation` 是 CLI flag，yml 里无处可写。重建时必须用环境变量 `PIP_NO_BUILD_ISOLATION=1` 包住 `conda env create`，否则 pyradiomics 会在 pip 的隔离构建环境里找不到 `versioneer` 而失败。

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

## 今日结论

1. **conda 环境的边界是 `CONDA_PREFIX`**：`base` 是 conda 自己的运行环境（本次 Python 3.14.9），项目环境 `radiomics` 是完全独立的 3.10.22，两者共用的只有 `pkgs/` 缓存（硬链接），不是运行环境。
2. **`conda activate` 只切换、不创建**，`conda create` 才创建；切换后 `which python` 必须落在 `envs/<name>/bin/python`，否则没生效（必要时 `hash -r`）。
3. **混用 conda 与 pip 的判据是 `<pip>` 标记**：`pyradiomics 3.0.1 pypi_0 pypi` 说明 conda 不认识它，`--from-history` 导出时必然丢——这是"导出文件不等于可重建"的根源。
4. **锁版本不是形式要求**：numpy 2.2.6 → 1.26.4 这一个决定，直接决定了 pyradiomics 能不能装上。
5. **"一次重建成功"没有捷径**：`--no-build-isolation` 是 CLI flag，yml 里写不进去，必须靠 `PIP_NO_BUILD_ISOLATION=1` 环境变量在重建命令上补齐。这条限制要在 README 里写明，否则 D10 评审时复现不出来。
6. **网络问题与密钥问题要分开判断**：`kex_exchange_identification` 是链路被干预，`Permission denied (publickey)` 才是密钥；本次两台机器各缺一半，agent 转发正好补齐。
7. **fake-IP 环境下 `nc` 的成功没有意义**：`198.18.0.0/15` 的地址说明流量被网关透明代理接管，可达性要看应用层握手。

## 待完成（今日收尾，写于 2026-10-29 重建执行前）

- [ ] 完成 `conda env remove` → `PIP_NO_BUILD_ISOLATION=1 conda env create -f env/environment.yml` 的一次性重建，日志落 `logs/day09-rebuild.log`
- [ ] 重建成功后导出 `env/conda-explicit.txt`、`env/pip-freeze.txt`，并写 `env/README.md`（含 `PIP_NO_BUILD_ISOLATION=1` 的说明）
- [ ] 补齐 `jupyter --version` 证据、完成 `day09` commit 并 push，Mac 侧 `git pull` 同步

> D10 是 G2 门禁，届时需用本文件 + `env/` 三件套 + `logs/day09-rebuild.log` 证明"删掉能重建"。

## 验收对照（Day09）

- [ ] 删环境后 `conda env create -f env/environment.yml` 一次成功（**待执行**，需带 `PIP_NO_BUILD_ISOLATION=1`）
- [x] `python -c "import radiomics"` 无报错（重建前环境已验证；重建后需复验）
- [x] `from radiomics import featureextractor` 正常加载
- [ ] `env/` 下有 3 个锁定文件 + `env/README.md`（当前只有 `environment.yml`）
- [x] 能解释 conda 与 pip 的边界（见知识点，本次以 `pyradiomics` 为实例）
- [x] 能解释"为什么要锁版本"（numpy 2.x 与 `--from-history` 丢包两个实证）
