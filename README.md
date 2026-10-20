# intern-wangjiaqi-nsclc-survival

## 项目目标

在 20 个工作日内，从 Git / SSH / Linux CLI 基础出发，搭建可重建的 Docker + Conda 环境，下载 TCIA NSCLC-Radiomics 数据，复现一项已发表的影像组学生存分析（DICOM → GTV-1 掩膜 → PyRadiomics 特征 → Cox 模型 → C-index），并保留完整、可追溯的工作日志。

## 目录说明

| 目录/文件 | 用途 |
|---|---|
| `journal/` | 每日工作日志（`day01.md` … `day20.md`）与打卡表 `INDEX.md` |
| `notes/` | 9 个能力模块的知识笔记 |
| `env/` | Conda 环境、Dockerfile 与重建说明 |
| `data/` | 数据说明、临床表、manifest；原始影像放 `data/raw/`，不入库 |
| `code/` | 从下载到建模的完整管线 |
| `results/` | 特征表、模型结果与图（`tables/`、`figures/`、`repro/`） |
| `logs/` | 运行日志 |
| `report.md` | 复现报告（D20 定稿） |
| `reflection.md` | 学习反思（D20 定稿） |

## 快速开始

```bash
cd ~/Desktop/实习日志
git status
git log --oneline
```

## 当前进度

- **D1（2026-10-19）**：建立目录骨架、笔记规范与首次 commit。

## 许可声明

本项目仅用于非商业学习与研究。数据来自 TCIA **NSCLC-Radiomics** 数据集（Aerts et al., 2014），采用 **CC BY-NC 3.0** 许可：仅限非商业使用，必须署名并引用 DOI [`10.7937/K9/TCIA.2015.PF0M9REI`](https://doi.org/10.7937/K9/TCIA.2015.PF0M9REI)。不得用于商业用途，不得用于临床诊断或治疗决策。
