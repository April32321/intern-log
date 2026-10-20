# Conda

开源包管理与环境管理系统，常用于 Python / 数据科学。

## 常用命令

- `conda create -n env python=3.11` 创建环境
- `conda activate env` 激活环境
- `conda deactivate` 退出环境
- `conda env list` 列出所有环境
- `conda install <pkg>` 安装包
- `conda remove <pkg>` 卸载包
- `conda env export > environment.yml` 导出环境
- `conda env create -f environment.yml` 从文件创建环境
