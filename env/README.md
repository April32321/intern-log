# radiomics 环境

Python 3.10 + conda-forge；pyradiomics 走 pip 源码编译。

## 重建

    bash env/rebuild.sh

## 说明

- conda env create 无法传 --no-build-isolation，
  所以 pyradiomics 由 rebuild.sh 单独编译。
- conda >= 25 需先 conda tos accept，见 journal 卡点 10。
- numpy 固定 1.26：pyradiomics 3.0.1 用了 np.float。

## 锁文件

environment.yml / conda-explicit.txt / pip-freeze.txt