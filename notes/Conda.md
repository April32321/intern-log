# Conda

开源包管理与环境管理系统，常用于 Python / 数据科学。

## 常用命令

- `conda create -n env python=3.11` 创建环境
- `conda create -n env -c conda-forge --override-channels python=3.10 -y` 只用 conda-forge 创建（避开 Anaconda 默认渠道的 ToS 检查）
- `conda activate env` 激活环境
- `conda deactivate` 退出环境
- `conda env list` / `conda info --envs` 列出所有环境
- `conda install -c conda-forge --override-channels <pkg>` 安装包
- `conda remove <pkg>` 卸载包（只删一个包；`-n env --all` 才删整个环境）
- `conda search -c conda-forge <pkg>` 查包（新版只接受一个包名，多个要分开查或用正则 `'a|b|c'`）
- `conda list` 列出当前环境所有包及渠道
- `conda env export > environment.yml` 导出环境（含精确版本，可带 `prefix:`）
- `conda env export --from-history > environment.yml` 只导出**手装**的顶层包（**会丢掉 pip 装的包**）
- `conda env create -f environment.yml` 从文件创建环境
- `conda env remove -n env -y` 删除环境（conda ≥25 可能被 ToS 检查拦住，可改用 `rm -rf ~/miniconda3/envs/env`）

## 当前在哪个环境

`conda activate` 成功时除提示符外**没有任何输出**，不主动检查很容易误判。

| 提示符 | 含义 |
|---|---|
| `(base)` | conda 自己的运行环境，**不要**往里装项目包 |
| `(myenv)` | 项目环境 |
| 无括号 | 未激活任何环境，`python` 可能是系统自带的 |

```bash
echo "env=$CONDA_DEFAULT_ENV"; which python; python -c "import sys; print(sys.prefix)"
```

- `which python` 必须落在 `.../envs/<name>/bin/python`
- 切换后 `python` 还指旧路径 → `hash -r` 清 shell 命令缓存
- `conda activate` 只切换、不创建；环境不存在报 `EnvironmentNameNotFound`
- 关闭 base 自动激活：`conda config --set auto_activate_base false`

## 三层锁

| 文件 | 命令 | 保证什么 | 局限 |
|---|---|---|---|
| `environment.yml` | 手写或 `conda env export --from-history` | 能重建出**功能等价**的环境 | 只钉顶层包，传递依赖会漂；`--from-history` 丢 pip 包 |
| `conda-explicit.txt` | `conda list --export` | 每个 conda 包的**精确 build 号** | 含 `=pypi_0` 行，不能直接用于重建 |
| `pip-freeze.txt` | `pip freeze` | pip 侧精确版本 | 只覆盖 pip 部分 |

写 yml 时注意三件事：

1. 删掉 `prefix: /home/xxx/miniconda3/envs/xxx`，否则环境绑死在某台机器
2. `channels` 只写 `conda-forge`，不要出现 `defaults`（会触发 ToS 检查）
3. 需要编译的包（要 `--no-build-isolation` 的）**不要**放进 `pip:` 段，见下

## 重建 ≠ 恢复

- **重建**：`conda env create -f` 照配方重新求解、下载、解压、编译 → 与原来「功能等价」
- **恢复**：`cp -a` 目录副本或 `conda pack` 的 tar.gz → 与原来「逐字节一致」，但要求事先备份

`~/miniconda3/pkgs/` 是**安装包缓存**，重建时被硬链接复用，所以快、也像"原来那份"，但它不是环境备份。

实测对照：`environment.yml` 重建后 15 个顶层包版本与 build 号完全一致，但 4 个**传递依赖**漂移（brotli、urllib3、`zstandard → backports.zstd`，均在 jupyter 链上）。这证明环境是当场求解出来的，而不是被还原的。

一句话：`environment.yml` 保证"能重建"，`conda-explicit.txt` 才保证"一模一样"。

## 常见坑

| 现象 | 原因 | 处理 |
|---|---|---|
| `CondaToSNonInteractiveError` | conda ≥25 校验 `~/.condarc` 里的 `defaults` 渠道条款，`-y` 下无法弹确认 | `conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main`（`pkgs/r` 同样一条）；或建环境时 `-c conda-forge --override-channels` |
| `conda env create` 报 `unrecognized arguments: --override-channels` | 该参数只属于 `conda create`/`install`，`env create` 没有 | 先 `conda tos accept` |
| `PackagesNotFoundError` | 该渠道没有这个包 | 加 `-c conda-forge`；仍没有就 `pip install` |
| 装包很慢 | 官方源远 | 用清华镜像或 `mamba` |
| pip 装完 conda 包被降级 | 顺序反了 | **先 conda 装齐，再 pip 只补缺** |
| `conda list` 里出现 `<pip>` / `pypi_0` | 该包是 pip 装的，conda 不认识 | `--from-history` 导出会丢它，必须手工补进 yml 的 `pip:` 段 |
| 新终端 `conda` 命令没了 | 只 `source activate` 没 `conda init` | `conda init bash` 后重开会话 |
| `conda env create` 里 pip 段编译失败（`No module named 'versioneer'`） | conda 内部 pip 不继承 `PIP_NO_BUILD_ISOLATION`，仍在构建隔离环境里跑 `setup.py` | 从 yml 删掉该包的 `pip:` 段，建好环境后手动 `pip install --no-build-isolation <pkg>`；用脚本封装 |

## base 与项目环境

- `base` 是 conda 自己的运行环境，版本随 Miniconda 安装包而定（`Miniconda3-latest` 会装当时最新的 Python）
- 项目环境完全独立，`python` / `site-packages` / `bin` 都分开
- 共用的只有 `pkgs/` 缓存（硬链接）和 `~/.conda/`
- 三个会穿透隔离的东西：`pip install --user`、`PYTHONPATH`、`~/.local/lib/pythonX.Y/site-packages`
