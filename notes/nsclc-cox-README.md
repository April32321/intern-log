> 位置说明：本文件由 `nsclc-cox/README.md` 迁入。内容已并入仓库根 `report.md`（实习报告 v3.0）与 `notes/nsclc-cox-report-v2.0.md`（复现报告 v2.0）。
> 其中 `environment.yml` 对应 `env/environment.nsclc-cox.yml`。

# NSCLC-Radiomics Cox 复现

基于 TCIA NSCLC-Radiomics（Lung1, v4）的影像组学生存分析复现。

- 数据：422 例，CT + RTSTRUCT/SEG，原始 DICOM 不进入本仓库
- 数据路径：/home/jiaqiwang/tcia/full（CT + RTSTRUCT，422 例）
- 环境：conda env `radiomics`（Python 3.10.22 + PyRadiomics 3.0.1）；重建：`conda env create -f environment.yml`
- 管线：DICOM -> GTV-1 掩膜 -> PyRadiomics 特征 -> Cox -> C-index

## 目录

| 目录 | 用途 |
|---|---|
| code/ | 下载、特征提取、建模脚本 |
| configs/ | PyRadiomics 参数等配置 |
| journal/ | 工作日志 |
| logs/ | 运行日志（默认不入库） |
| results/ | 特征表、模型结果与图 |

## 许可

数据来自 TCIA NSCLC-Radiomics，CC BY-NC 3.0，仅限非商业研究使用。
引用 DOI: 10.7937/K9/TCIA.2015.PF0M9REI
