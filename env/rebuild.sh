#!/usr/bin/env bash
# 一次性重建 radiomics 环境
# 前置：conda >= 25 需先接受默认渠道条款，见 env/README.md
set -euo pipefail
cd "$(dirname "$0")/.."

conda env remove -n radiomics -y 2>/dev/null || rm -rf "$HOME/miniconda3/envs/radiomics"
conda env create -f env/environment.yml

# pyradiomics 必须单独装：conda env create 内部的 pip 不继承
# PIP_NO_BUILD_ISOLATION，会退回构建隔离而失败（见 journal 卡点 11）
conda run -n radiomics pip install versioneer
conda run -n radiomics pip install --no-build-isolation --no-cache-dir pyradiomics==3.0.1

conda run -n radiomics python -c "import radiomics, lifelines, sksurv, pydicom; print('OK')"
