---
day: 13
date: 2026-11-04
theme: DICOM viewer 阅片与掩膜体积交叉验证
gate: D13
status: 进行中
---

# Day 13｜DICOM viewer 阅片与掩膜体积交叉验证（进行中）

> 本日尚未收尾。提交前还需补齐 5 例截图、体积对照表、`dcm2niix` 和
> `notes/dicom-viewer.md`，最后再更新 `journal/INDEX.md` 并 commit。

## 今日目标

- 装 DICOM viewer，完成 5 例阅片并截图；
- 用 Slicer `Segment Statistics` 建立 GTV-1 体积基准；
- 用 `dcm2niix` 理解 DICOM ↔ NIfTI 的几何关系；
- 写 `notes/dicom-viewer.md`，含操作步骤、窗宽窗位、坐标系差异、体积表。

## 进度快照

| 步骤 | 状态 | 说明 |
|---|---|---|
| 1. 装 viewer | ✅ | 3D Slicer 5.12.4 + SlicerRT |
| 2. 加载与阅片 | ✅ | LUNG1-085 的 CT + RTSTRUCT 已加载；肺窗/纵隔窗、三平面联动已练 |
| 3. 5 例体积交叉验证 | 🟡 1/5 | 085 已完成（LM 16.5597 cm³ / 5280 体素）；001/014/021/128 待做 |
| 4. 导出截图 | 🟡 1/5 | 085 肺窗已拍，文件暂存桌面且文件名含冒号，需移到 `results/figures/viewer/` |
| 5. `dcm2niix` 转 NIfTI | ⬜ | 未开始 |
| `notes/dicom-viewer.md` | ⬜ | 未开始 |
| `journal/day13.md` | 🟡 | 本文件，进行中 |
| `journal/INDEX.md` + commit | 🟡 | 已有进行中提交 `2405e25`，收尾提交待做 |

## 结论先行（截至当前）

1. Slicer 5.12.4 + SlicerRT 可正常加载 CT 与 RTSTRUCT；RTSTRUCT **加载时已自动转成
   segmentation**，结构列表里直接出现 10 个 segment，不需要再手动
   `Convert to segmentation`。
2. LUNG1-085 的 CT 是 **XiO 计划系统导出的 SECONDARY 图像**，经 CTP 脱敏
   （`PatientIdentityRemoved=YES`）。`StudyDescription` / `SeriesDescription`
   标签在文件里**不存在**，所以 Slicer 显示 `No study description` /
   `Unnamed Series`，这是正常的显示占位，不是加载错误。
3. 085 的 Slicer 体积栅格是 **0.9770 × 0.9770 × 3.2857 mm、512×512×106**。
   z 间距不是 3.0，而是 `345/105` 的平均间距，说明 Slicer 把 10 个缺层
   摊平到整个 z 范围；用公式反推缺层数正好是 **10**，与 D12 的
   “断档 10 处”一致。
4. 缺层例（014/085）的 Slicer 体积是**规则化后的参考**，不是真实 3.0 mm 栅格；
   不能用 1–2% 阈值直接判 pipeline 失败，D17 需要同栅格比较或注明放宽。
5. 085 的 `GTV-1` 已完成第一份体积基准：`Labelmap` 5280 体素 /
   16559.7 mm³ = **16.5597 cm³**，自检 `16559.7 / 5280 = 3.1363`，与
   `0.9770 × 0.9770 × 3.2857` 一致；`SV` 为 16.7949 cm³（+1.42%），只作旁证。
6. 085 的 `ScalarVolume_Mean` 为 **−34.35 HU**、Min −854、Max 144，均值偏低，
   需回三平面确认 GTV 轮廓是否包到空气/支气管。
7. 节点已重命名为 `LUNG1-085_CT` / `LUNG1-085_RT` / `LUNG1-085 study 20060114`，
   重复的 `2: RTSTRUCT: 20190226_1` 已删除；肺窗截图已拍，但文件暂存桌面，
   路径待修正。
8. 5 例中仅 085 完成，001/014/021/128 未做，Day13 尚未达到验收标准。

## 环境

- 本机：macOS，3D Slicer **5.12.4**，扩展 SlicerRT；
- 数据：`data/raw/full/`，本机有 10 例，085 路径为
  `data/raw/full/LUNG1-085/`；
- 190 未参与本日操作，viewer 全程在本机 GUI 完成。

## 步骤 1：安装与加载

1. 安装 3D Slicer 5.12.4，Extension Manager 里装 SlicerRT；
2. `DICOM` 模块 → `Import DICOM files` 导入患者目录；
3. 在 `Series` 表里 **Cmd-click 同时选中 `CT` 和 `RTSTRUCT`**，再点 `Load`；
   **不加载 SEG**，避免与 RTSTRUCT 转出的 segmentation 重名、选错；
4. 加载后 `Data` 模块的 `Subject Hierarchy` 里看到：

```text
LUNG1-085 (LUNG1-085)
└ No study description (20060114)
   ├ 1: Unnamed Series                  ← CT
   │  └ 1: Unnamed Series acquisition transform
   └ 2: RTSTRUCT: 20190226              ← 已自动转成 segmentation
      ├ gtv-6
      ├ Lung-Right
      ├ Lung-Left
      ├ Heart
      ├ Esophagus
      ├ Spinal-Cord
      ├ gtv-3_2l2
      ├ gtv-2_4r
      ├ gtv_2l
      └ GTV-1
```

- `No study description` 是占位符，括号里是 `StudyDate=20060114`；
- `1: Unnamed Series` 是 CT，`SeriesDescription` 为空；
- `acquisition transform` 是 SlicerRT 加的采集变换，**不要改名、不要删**；
- 重命名只影响显示，不改 DICOM 文件。为截图带患者 ID，建议改成：
  `LUNG1-085 study 20060114` / `LUNG1-085_CT` / `LUNG1-085_RT`。

## 步骤 2：阅片操作

- 布局切三平面（四宫格），十字线联动；
- `Volumes → Display` 里切换预设：
  - **肺窗** `CT-Lung`：WW 1500 / WL −600，区间 [−1350, 150] HU；
  - **纵隔窗** `CT-Mediastinal`：WW 350 / WL 40，区间 [−135, 215] HU；
- 085 有 10 个 ROI，阅片时只勾 `GTV-1`，其余全部隐藏；
  `gtv-2_4r`、`gtv-3_2l2`、`gtv_2l`、`gtv-6` 是另一套靶区，不能并入 `GTV-1`；
- 截图要求：三平面 + 患者 ID + GTV 轮廓，存
  `results/figures/viewer/LUNG1-085_gtv1_3plane_lung.png`（PNG）；
- 085 肺窗已截图，但文件暂存在桌面：
  `~/Desktop/results:figures:viewer:LUNG1-085_gtv1_3plane_lung.png`
  （保存时把路径写进了文件名，macOS 把 `/` 换成了 `:`，需要移动并改名）；
- 085 纵隔窗已拍，未确认落盘，可选；
- 其余 4 例截图未做。

## 步骤 3：元数据核对

在 `DICOM` 模块的 `Series` 表选中 CT → 右键 → `View DICOM metadata`
（注意：不是 `Data` 模块的右键菜单）。085 的 CT 关键字段：

| 字段 | 值 | 说明 |
|---|---|---|
| `(0010,0020) PatientID` | `LUNG1-085` | 与临床表一致 |
| `(0008,0020) StudyDate` | `20060114` | 与 study 节点括号一致 |
| `(0008,0060) Modality` | `CT` | |
| `(0008,0016) SOPClassUID` | `1.2.840.10008.5.1.4.1.1.2` | CT Image Storage |
| `(0008,0008) ImageType` | `ORIGINAL\SECONDARY\AXIAL` | 二次导出，不是扫描仪原始图 |
| `(0008,0070) Manufacturer` | `CMS, Inc.` | |
| `(0008,1090) ManufacturerModelName` | `XiO` | 治疗计划系统 |
| `(0012,0062) PatientIdentityRemoved` | `YES` | 已脱敏 |
| `(0013,0010) PrivateCreator` | `CTP` | 脱敏工具 |
| `(0018,0050) SliceThickness` | `3.00000` | 与 D12 一致 |
| `(0018,5100) PatientPosition` | `HFS` | 头先进仰卧 |
| `(0020,0011) SeriesNumber` | `1` | |
| `(0028,0030) PixelSpacing` | `0.9770\0.9770` | 行、列间距 |
| `(0020,0037) ImageOrientationPatient` | `1,0,0,0,1,0` | 标准轴位，无倾斜 |
| `(0020,0032) ImagePositionPatient` | `−250.112, −250.112, −526.900` | 当前显示文件的单层 IPP，LPS |

- `(0008,1030) StudyDescription` 与 `(0008,103E) SeriesDescription`
  **在文件中不存在**（不是空值），所以 Slicer 只能显示占位符；
- 元数据对话框里的 `1 / 106` 是文件列表序号，**不等于 z 排序**；
  085 的 volume 首层 z 约为 −715.9（截图第三列被裁，待核对），
  我们看到的 −526.9 只是中间某一层。

## 步骤 4：缺层与 spacing 规则化（本日关键发现）

### 085 的实际值

Slicer `Volumes → Information`：

```text
Image Dimensions: 512 × 512 × 106
Image Spacing:    0.9770 × 0.9770 × 3.2857 mm
```

`3.2857 = 345 / 105`，而 345 mm 正好是 **116 层 × 3 mm** 的 z 范围。
Slicer 只能存规则体素栅格，缺层只能被“平均”到整个 z 范围。

### 用 spacing 反推缺层数

```text
缺层数 = (spacing_z / 3.0 − 1) × (n_slices − 1)

085: (3.2857 / 3.0 − 1) × (106 − 1)
   = 0.09524 × 105
   = 10.0  → 缺 10 层
```

与 D12 的“085 断档 10 处”一致。这个公式要求缺层都是孤立的 3 mm 缺口，
本队列的 4 例都满足。

### 5 例的预期 spacing（待逐例核对）

| 病例 | 现有层数 | 缺层 | 真实层数 | z 范围 | 预期 Slicer spacing |
|---|---:|---:|---:|---:|---:|
| LUNG1-001 | 134 | 0 | 134 | 399 mm | 3.000 |
| LUNG1-021 | 197 | 1 | 198 | 591 mm | 3.015 |
| LUNG1-085 | 106 | 10 | 116 | 345 mm | **3.2857** |
| LUNG1-128 | 100 | 0 | 100 | 297 mm | 3.000 |
| LUNG1-014 | 87 | 16 | 103 | 306 mm | **3.558** |

### 对体积对照的影响

- 不能简单认为 085 的体积会按 `3.2857/3 = +9.5%` 放大：GTV 跨越的层数会同比减少，
  体素数 × 体素体积大致抵消；
- 真正的风险是：RTSTRUCT 轮廓的 z 是真实位置，而 Slicer 的规则层位被拉伸成
  3.2857 mm，轮廓会被量化到最近的规则层；GTV 跨层数少时，一次层错位就可能
  带来几个百分点的体积差；
- 因此 **014 / 085 的体积差可能超过 1–2% 阈值，这是参考几何被规则化的问题，
  不是 pipeline 写错**。D17 对这两例要么把 pipeline 掩膜重采样到 Slicer 的同一
  栅格再比，要么在表里明确“缺层例，阈值放宽”；
- 001 / 021 / 128 才是严格 1–2% 的对照，其中 021 只有 1 个缺口，spacing 3.015，
  影响很小。

### 各例的自检体素体积

`Volume_mm3 / VoxelCount` 应接近下表（用 Slicer 实际 spacing 算，不要一律用 2.8636）：

| 病例 | Slicer spacing z | 预期体素体积 (mm³) | 说明 |
|---|---:|---:|---|
| LUNG1-001 | 3.000 | 2.8636 | 正常 |
| LUNG1-021 | 3.015 | 2.8782 | 1 缺层 |
| LUNG1-085 | 3.2857 | 3.1363 | 10 缺层，拉伸栅格 |
| LUNG1-128 | 3.000 | 2.8636 | 正常 |
| LUNG1-014 | 3.5581 | 3.3963 | 16 缺层，拉伸栅格 |

## 步骤 5：体积基准（085 已完成，其余待做）

### 085 的结果（2026-11-04 11:26）

`Segment Statistics` 输出（表节点 `Table`，另存为 `~/Desktop/Table.tsv`）：

| 表示 | VoxelCount | Volume mm3 | Volume cm3 | 说明 |
|---|---:|---:|---:|---|
| **LM（Labelmap）** | **5280** | **16559.7** | **16.5597** | 今天的主基准 |
| SV（另一路） | 5355 | 16794.9 | 16.7949 | 比 LM 大 1.42%，只作旁证 |

- 自检：`16559.7 / 5280 = 3.1363`，与 `0.9770 × 0.9770 × 3.2857` 一致；
- 强度：`Mean = −34.3462`、`Minimum = −854`、`Maximum = 144`；
- 结论：几何正确；均值偏低，截图时复核轮廓是否包含空气/支气管。

### 实际操作中的两个问题

1. **一开始只出 ClosedSurface**：`Segment Statistics` 最初只给
   `Surface area [mm2]` / `Volume (CS)`，没有 `Labelmap_*` 列。原因是 segmentation
   当时只有 `Closed surface` / `Planar contour`；在 `Segmentations → Representations`
   勾选 `Binary labelmap` 并重跑 `Apply` 后，才出现 `Voxel count (LM)` /
   `Volume (LM)`。
2. **重复 segmentation**：操作过程中生成了 `2: RTSTRUCT: 20190226_1`，与原始
   `2: RTSTRUCT: 20190226` 重名，容易在 `Segment Statistics` 里选错；已删除副本。

### Segment Statistics 操作

1. `Segmentations` 里只勾 `GTV-1`；
2. `Modules` → `Segment Statistics`；
3. 输入：
   - `Segmentation` = `LUNG1-085_RT`
   - `Scalar volume` = `LUNG1-085_CT`
   - `Output table` = `Create new table`（实际节点名 `Table`）
4. `Apply`；
5. 找 `Segment` 列为 `GTV-1` 的行，抄：
   - `Labelmap_VoxelCount`
   - `Labelmap_Volume_mm3`（**不要用 `ClosedSurface_Volume_mm3`**）
   - `ScalarVolume_Mean`
6. `V_cm3 = Labelmap_Volume_mm3 / 1000`；
7. 用上面的“预期体素体积”做自检；GTV 的 `ScalarVolume_Mean` 通常在约 20–60 HU；
   085 实测 −34.35，偏低，需复核轮廓。

### 5 例体积表（1/5 已填）

| PatientID | ROI | Slicer cm³ | VoxelCount | Mean HU | Slicer z spacing | pipeline cm³ | Δ% | 备注 |
|---|---|---:|---:|---:|---:|---:|---:|---|
| LUNG1-001 | GTV-1 | | | | 3.000 | | | 对照 |
| LUNG1-014 | GTV-1 | | | | 3.558 | | | 缺 16 层 |
| LUNG1-021 | GTV-1 | | | | 3.015 | | | 缺 1 层 |
| LUNG1-085 | GTV-1 | **16.5597** | **5280** | **−34.35** | 3.2857 | | | 缺 10 层，拉伸栅格；SV=16.7949；Mean 偏低待复核 |
| LUNG1-128 | gtv-pre-op | | | | 3.000 | | | 无 GTV-1、无 SEG，D16 决策 |

```
Δ% = (V_pipeline − V_slicer) / V_slicer × 100
```

体积一致不等于位置正确。D17 回填时还要加：

- 质心一致性（LPS→RAS，误差 < 1 体素）；
- 与 Slicer 导出 labelmap 的 Dice（目标 > 0.95）。

## 原理记录

### 1. 窗宽窗位

只影响显示，不改 HU：

```text
显示区间 = [WL − WW/2, WL + WW/2]
g = clip((HU − (WL − WW/2)) / WW, 0, 1) × 255
```

- 肺窗 WW 1500 / WL −600 → 区间 [−1350, 150]；
- 纵隔窗 WW 350 / WL 40 → 区间 [−135, 215]。

组学特征必须从原始 HU 算，不能从截图或 8-bit 窗化后的图算；PyRadiomics 自己用
`binWidth` 离散化，不读窗宽窗位。

### 2. DICOM LPS ↔ NIfTI / Slicer RAS

```text
DICOM 患者坐标：+x Left,   +y Posterior, +z Superior
NIfTI / Slicer：+x Right,  +y Anterior,  +z Superior

p_RAS = (−x_LPS, −y_LPS, z_LPS)
```

例：IPP = `(−250.112, −250.112, −526.900)` → NIfTI 平移
`(250.112, 250.112, −526.900)`。

### 3. 方向余弦与体素→患者坐标

`ImageOrientationPatient = [r(3), c(3)]`：

- `r` = 列索引增大的方向（第一行方向余弦）；
- `c` = 行索引增大的方向（第一列方向余弦）；
- 法向 `n = r × c`；
- `PixelSpacing = [Δr, Δc]`，**Δr 沿 c，Δc 沿 r**（最易写反）。

```text
[x,y,z]ᵀ = IPP + i·Δc·r + j·Δr·c + k·Δs·n
Δs = (IPP_{k+1} − IPP_k) · n    # 不要用 SliceThickness
```

085 是标准轴位，`r=(1,0,0), c=(0,1,0), n=(0,0,1)`，退化为：

```text
x = −250.112 + i × 0.9770
y = −250.112 + j × 0.9770
z = −526.900 + k × 3.0
```

NIfTI affine 由 `M_RAS = F · M_LPS` 得到，`F = diag(−1, −1, 1, 1)`。
`dcm2niix` 可能做轴置换/翻转，**以文件里的 affine 为准**，不要自己假设矩阵形式。

### 4. 为什么 radiomics 要先转 NIfTI / 重采样

- DICOM 一层一个文件，几何分散在每层 IPP/IOP；NIfTI 一个文件带一个 affine；
- RTSTRUCT 是矢量轮廓，`dcm2niix` 不会转换，必须先栅格化成 labelmap
  （SlicerRT 导出，或 dcmqi 处理 SEG）；
- 3D 纹理的邻域依赖 spacing，各向异性（0.977 × 0.977 × 3.0）时“邻域”不是
  各向同性；重采样到统一各向同性 spacing（图像 B-spline，掩膜最近邻）才能跨患者比较；
- 体积要在原始栅格上算，不要用重采样后的掩膜算体积。

## 公式速查

> 这一节按“输入 → 公式 → 输出”整理，收尾时会同步到 `notes/dicom-viewer.md`。

### 1. 窗宽窗位显示映射

```text
显示区间 = [WL − WW/2, WL + WW/2]
g = clip((HU − (WL − WW/2)) / WW, 0, 1) × 255
```

| 预设 | WW | WL | HU 区间 |
|---|---:|---:|---|
| 肺窗 | 1500 | −600 | [−1350, 150] |
| 纵隔窗 | 350 | 40 | [−135, 215] |

窗宽窗位只影响显示，不改 HU；组学特征从原始 HU 算。

### 2. 体素体积与掩膜体积

```text
V_vox = Δr × Δc × Δs
      = PixelSpacing[0] × PixelSpacing[1] × spacing_z

V_mask = N_voxels × V_vox
V_cm3  = V_mask / 1000
```

- `Δr = PixelSpacing[0]`：行间距，沿 `c` 方向；
- `Δc = PixelSpacing[1]`：列间距，沿 `r` 方向；
- `Δs`：真实层间距，用相邻 IPP 差，不要用 `SliceThickness`；
- 085 的 Slicer 栅格：`0.9770 × 0.9770 × 3.2857 = 3.1363 mm³`；
- 真实 3.0 mm 栅格：`0.9770 × 0.9770 × 3.0 = 2.8636 mm³`。

### 3. 用 Segment Statistics 自检

```text
V_vox_implied = Labelmap_Volume_mm3 / Labelmap_VoxelCount
```

| 病例 | Slicer spacing z | 预期 V_vox (mm³) |
|---|---:|---:|
| LUNG1-001 | 3.000 | 2.8636 |
| LUNG1-021 | 3.015 | 2.8782 |
| LUNG1-085 | 3.2857 | 3.1363 |
| LUNG1-128 | 3.000 | 2.8636 |
| LUNG1-014 | 3.5581 | 3.3963 |

若反算值明显偏离，优先查：labelmap 是否在 CT 栅格上、`PixelSpacing` 行列是否写反、
`Δs` 是否误用了 `SliceThickness`。

### 4. 体积差异

```text
Δ% = (V_pipeline − V_slicer) / V_slicer × 100
```

- 通过：`|Δ%| < 1–2%`；
- 014 / 085 是缺层例，Slicer 参考被规则化，阈值放宽或在同一栅格上比较；
- 体积一致不等于位置正确，D17 还要加质心与 Dice。

### 5. 缺层反推

```text
spacing_z = (z_max − z_min) / (n_present − 1)
n_true    = round((z_max − z_min) / 3.0) + 1
missing   = n_true − n_present
          = (spacing_z / 3.0 − 1) × (n_present − 1)
```

085 验证：

```text
3.2857 = 345 / 105
missing = (3.2857 / 3.0 − 1) × 105 = 10.0
```

前提：名义层距 3.0 mm、缺层是孤立缺口（本队列 4 例均满足）。
若层距本身不是 3.0，把公式里的 3.0 换成实测中位层距。

按相邻 z 差判定断档：

```text
gap if (z_{k+1} − z_k) > 1.5 × median(Δz)
该断档缺层数 = round((z_{k+1} − z_k) / 3.0) − 1
```

### 6. 体素 → 患者坐标（DICOM LPS）

```text
r = IOP[0:3]          # 列索引增大方向
c = IOP[3:6]          # 行索引增大方向
n = r × c             # 切片法向（单位向量）

Δr = PixelSpacing[0]  # 行间距
Δc = PixelSpacing[1]  # 列间距
Δs = (IPP_{k+1} − IPP_k) · n

p_LPS = IPP + i·Δc·r + j·Δr·c + k·Δs·n

M_LPS = [ r·Δc   c·Δr   n·Δs   IPP ]   # 4×4
        [  0      0      0      1  ]
```

`i` = 列索引，`j` = 行索引，`k` = 层索引。

### 7. LPS → RAS / NIfTI affine

```text
F = diag(−1, −1, 1, 1)
p_RAS = F · p_LPS
M_RAS = F · M_LPS
```

- 085 例：IPP `(−250.112, −250.112, −526.900)` →
  NIfTI 平移 `(250.112, 250.112, −526.900)`；
- `nibabel` 的 `img.affine` 就是 `M_RAS`，映射 `(i,j,k,1)` → RAS mm；
- 用 `nib.aff2axcodes(img.affine)` 应得到 `('R','A','S')`。

### 8. 轮廓点 → 体素索引

```text
p_LPS = ContourData.reshape(-1, 3)
ijk   = M_LPS⁻¹ · [p_LPS, 1]
```

然后逐层做像素中心测试（如 `matplotlib.path.Path.contains_points`），
统计落在多边形内的体素，再乘 `V_vox`。同层多轮廓取并集，有孔洞时注意填充规则。

### 9. D17 回填时的位置校验

```text
Dice = 2|A ∩ B| / (|A| + |B|)
Δcentroid = ||c_pipeline − c_slicer||₂
```

目标：Dice > 0.95，质心差 < 1 个体素。

## 数据查阅位置

### 1. 一表定位

| 数据项 | 首选位置 | 字段 / 操作 | 备注 |
|---|---|---|---|
| PatientID、StudyDate、Modality | `DICOM` 模块 → `Series` 表 → 右键 `View DICOM metadata` | `(0010,0020)`、`(0008,0020)`、`(0008,0060)` | 也可用 `results/tables/index.csv` |
| StudyDescription、SeriesDescription | 同上 | `(0008,1030)`、`(0008,103E)` | 本队列**标签缺失**，显示为占位符 |
| SeriesInstanceUID、SOPInstanceUID | 同上 | `(0020,000E)`、`(0008,0018)` | `index.csv` 的 `series_dir` / `rtstruct_path` 里也含 UID |
| SliceThickness（标称层厚） | 同上 | `(0018,0050)` | 只作参考，真实层距看 IPP |
| PixelSpacing | 同上 | `(0028,0030)` | 顺序是 `[行, 列]` |
| ImageOrientationPatient | 同上 | `(0020,0037)` | 方向余弦 |
| ImagePositionPatient | 同上，逐文件看 | `(0020,0032)` | 必须按 z 排序后再用 |
| 真实层间距 `Δs` | `logs/day12-check-190.txt` / `code/01_check_dicom.py` | 相邻 IPP 差的中位数 | **不要用 Slicer 的 spacing 代替**（缺层会被规则化） |
| 层数 `n_slices` | `results/tables/index.csv` / `cohort.csv` | `n_slices` | Slicer 的 Dimensions 也显示，但缺层例只显示现有层数 |
| 缺层数 | `logs/day12-check-190.txt` 的 `WARN: 层距断档N处`；`journal/day12.md` 缺层表 | 或第 5 节公式反推 | 014 缺 16、021 缺 1、085 缺 10、194 缺 1 |
| ROI 名称 | `results/tables/index.csv` | `roi_names`（竖线分隔） | 也可看 Slicer `Segmentations` 列表 |
| 是否有 GTV-1 | `results/tables/index.csv` / `cohort.csv` | `gtv1_present` | LUNG1-128 为 False |
| 是否有 SEG | `results/tables/index.csv` / `cohort.csv` | `has_seg` | LUNG1-128 为 False |
| RTSTRUCT 轮廓点 | `rtstruct_path` 指向的文件 | `(3006,0050) ContourData` | 用 pydicom 读，reshape 成 `(-1,3)` |
| CT 切片文件目录 | `results/tables/index.csv` | `series_dir`（相对 root） | 本机 root = `data/raw/full` |
| Slicer GTV 体积 | `Segment Statistics` 输出表 | `Labelmap_VoxelCount`、`Labelmap_Volume_mm3`、`ScalarVolume_Mean` | 不要用 `ClosedSurface_Volume_mm3` |
| Slicer 几何 | `Volumes` 模块 → `Information` | Dimensions、Spacing、Origin、Directions | 缺层例的 Spacing 是规则化后的值 |
| pipeline 体积 | `results/tables/gtv_volume_check.csv` | 待 D17 建表/回填 | 与 Slicer 列并排 |
| 临床变量 | `data/clinical/NSCLC-Radiomics-Lung1.clinical-version3-Oct-2019.csv` | 原始列 | 合并后看 `cohort.csv` |
| 缺失率 / 取值分布 | `results/tables/missing_rate.csv`、`value_counts.csv` | 见 D12 | 末尾有 `#解释` 行 |
| NIfTI 几何 | `.nii.gz` 文件本身 | `nib.load()` 的 `shape`、`get_zooms()`、`affine`、`aff2axcodes` | 另看 dcm2niix 的 `.json` sidecar |
| 截图 | `results/figures/viewer/` | `LUNG1-085_gtv1_3plane.png` 等 | 需含患者 ID |

### 2. 常用入口

| 想查什么 | Slicer 路径 |
|---|---|
| 节点层级、重命名、删除、转 segmentation | `Modules` → `Data` → `Subject Hierarchy` |
| DICOM 原始标签 | `Modules` → `DICOM` → `Series` 表 → 右键 `View DICOM metadata` |
| CT 的 Dimensions / Spacing / Origin / Directions | `Modules` → `Volumes` → `Information` |
| 结构列表、可见性、颜色 | `Modules` → `Segmentations` |
| 体积 / 体素数 / 平均 HU | `Modules` → `Segment Statistics` |
| 命令行补查 | `View` → `Python Console` |

### 3. 终端查 DICOM

单文件查标签：

```bash
python3 - <<'PY'
import pydicom
p = "data/raw/full/LUNG1-085/RTSTRUCT/<SeriesUID>/<SOPUID>.dcm"
ds = pydicom.dcmread(p, stop_before_pixels=True)
for k in ("PatientID", "StudyDate", "StudyDescription",
          "SeriesDescription", "Modality", "SliceThickness",
          "PixelSpacing", "ImagePositionPatient",
          "ImageOrientationPatient"):
    print(f"{k:24s} = {getattr(ds, k, '<absent>')!r}")
PY
```

批量看某一例所有 CT 切片的 z 与间距：

```bash
python3 - <<'PY'
import glob, pydicom
files = glob.glob("data/raw/full/LUNG1-085/CT/*/*.dcm")
zs = sorted(float(pydicom.dcmread(f, stop_before_pixels=True)
                     .ImagePositionPatient[2]) for f in files)
d = [b - a for a, b in zip(zs, zs[1:])]
print("n =", len(zs), "z =", zs[0], "->", zs[-1])
print("gap count =", sum(x > 4.5 for x in d))
print("unique dz =", sorted(set(round(x, 3) for x in d)))
PY
```

### 4. 查数顺序（建议）

1. **身份与层数**：`cohort.csv` / `index.csv` 看 `PatientID`、`n_slices`、`roi_names`、`gtv1_present`、`has_seg`；
2. **缺层**：`logs/day12-check-190.txt` 的 `WARN`，或用第 5 节公式从 Slicer spacing 反推；
3. **几何**：`View DICOM metadata` 看 `PixelSpacing`、`IOP`、`IPP`，真实 `Δs` 用 IPP 差；
4. **体积**：`Segment Statistics` 取 `Labelmap_Volume_mm3`，除以 1000；
5. **临床**：`cohort.csv`；缺失率看 `missing_rate.csv`；
6. **NIfTI**：`nibabel` 读 affine，和 `F·M_LPS` 对照。

> 优先级：**DICOM 头 > 派生表 > Slicer 显示值**。Slicer 的 spacing 在缺层例上是
> 规则化后的结果，不能当作真实层距；`index.csv` 是从 DICOM 头派生的，查得快，
> 但遇到争议仍要回到原始标签。

## 验收对照（当前）

| 验收标准 | 状态 | 证据 |
|---|---|---|
| 至少 5 例完成 Slicer 阅片并截图 | 🟡 1/5 | 085 已阅片并截肺窗图；文件暂存桌面，待移到 `results/figures/viewer/` |
| 能指出 LUNG1-128 无 GTV-1、014/021/085 缺层 | 🟡 部分 | 085 已用 spacing 3.2857 反推 10 缺层；014/021/128 待逐例看 |
| 体积对照表已建（pipeline 列可空） | 🟡 1/5 | 本文件 085 行已填；`results/tables/gtv_volume_check.csv` 未建 |
| 能解释窗宽窗位、层厚、spacing 对特征的影响 | ✅ | 见“原理记录” |

## 卡点与操作记录

### 卡点 1：找不到 Subject Hierarchy

`Subject Hierarchy` 不在 DICOM 模块的 `Loaded data` 列表里，在
**`Data` 模块面板顶部**（可折叠）。`Modules` 下拉框切到 `Data` 即可。

### 卡点 2：找不到 `View DICOM metadata`

不在 `Data` 模块的右键菜单里，也不在 `Loaded data` 的右键菜单里。
位置：`DICOM` 模块 → 右下角 `Series` 表 → 选中 series → 右键
`View DICOM metadata`。

### 卡点 3：`No study description`

源 DICOM 中 `(0008,1030)` / `(0008,103E)` 标签被剥离，不是空值；
CT 由 XiO 导出、CTP 脱敏（`PatientIdentityRemoved=YES`），属于 TCIA 数据的正常状态。

### 卡点 4：加载 SEG 的干扰

SEG 与 RTSTRUCT 转出的 segmentation 可能重名，且 SEG 只是 RTSTRUCT 的子集。
本日只加载 CT + RTSTRUCT；已载入的 SEG 应删除或至少隐藏。

### 卡点 5：把 `1 / 106` 当成第一层

元数据对话框的文件序号不等于 z 排序。085 的 volume 首层 z 约为 −715.9，
而对话框里看到的 −526.9 只是中间层。

### 卡点 6：一开始误判 085 体积会 +9.5%

先按 `3.2857/3` 判断体积会放大约 9.5%，随后修正：拉伸栅格下 GTV 跨层数同比减少，
体积大致抵消；真正的风险是轮廓被量化到 3.2857 mm 规则层，以及几何位置不再等于真实 IPP。

### 卡点 7：Segment Statistics 只给 ClosedSurface

首次计算只出现 `Surface area [mm2]` / `Volume (CS)`，没有 `Labelmap_*`。
在 `Segmentations → Representations` 勾选 `Binary labelmap` 后重跑 `Apply` 才出现；
`LM` 与 `SV` 的体素体积相同（3.1363 mm³），但体素数差 1.42%（5280 vs 5355），
主表统一用 `LM`。

### 卡点 8：重复 segmentation

操作中出现了 `2: RTSTRUCT: 20190226_1`，与原始节点重名。删除副本后，
`Segment Statistics` 的下拉框只剩一个 segmentation，避免选错。

### 卡点 9：截图路径被 macOS 改写

在保存对话框里把文件名写成 `results/figures/viewer/...png`，macOS 把 `/` 换成了
`:`，文件实际落在桌面：`results:figures:viewer:LUNG1-085_gtv1_3plane_lung.png`。
应先把目录建好，或用 `Cmd+Shift+5` 的 `Save to → Other Location`，再重命名。

## Kilo 使用记录

- 解释了 DICOM LPS 与 NIfTI/Slicer RAS 的差异、方向余弦、体素→患者坐标、
  NIfTI affine 的构造，以及掩膜镜像错位的三种常见原因；
- 解释了窗宽窗位的显示映射，以及为什么组学特征要用原始 HU；
- 推导了“用 Slicer spacing 反推缺层数”的公式，并在 085 上验证为 10；
- 帮助定位 Slicer 5.12 的 UI：Subject Hierarchy 在 `Data` 模块，
  DICOM 元数据在 `DICOM` 模块的 Series 表；
- 纠正了“缺层会让 Slicer 体积 +9.5%”的错误判断，改为“体积大致抵消，
  但参考几何被拉伸”；
- 定位 `Segment Statistics`：它不是 `Segmentations` 里的按钮，而是独立模块；
  下拉框搜不到时用 `slicer.util.selectModule("SegmentStatistics")`；
- 解释了 `LM` 与 `SV` 的区别，以及为什么主表用 `Labelmap`；
- 给出截图内容建议：三平面 + 患者 ID + GTV，肺窗优先，纵隔窗作补充。

## 待办（收尾前）

1. 把桌面截图移到 `results/figures/viewer/LUNG1-085_gtv1_3plane_lung.png`
   （当前文件名是 `results:figures:viewer:...`）；纵隔窗按需补；
2. 001、014、021、128 重复同一流程，并逐例记录 `Volumes → Information` 的 spacing；
3. 5 例截图存 `results/figures/viewer/`，选 2 张进报告；
4. 用 `dcm2niix` 转 001 或 085，检查 `.nii.gz` 的 `shape`、`zooms`、`aff2axcodes`；
5. 建 `results/tables/gtv_volume_check.csv`（085 行先填），并可选把
   `~/Desktop/Table.tsv` 复制成 `results/tables/stats_085.tsv`；
6. 写 `notes/dicom-viewer.md`（操作步骤、窗宽窗位、坐标系、体积表）；
7. 更新 `journal/INDEX.md`，提交：

```bash
git add results/figures/viewer results/tables/gtv_volume_check.csv \
        notes/dicom-viewer.md journal/day13.md journal/INDEX.md
git commit -m "day13: dicom viewer 阅片与掩膜体积交叉验证"
```

## 今日结论（暂定）

- Viewer 已可用，085 的 CT + RTSTRUCT 能正确加载，RTSTRUCT 自动转 segmentation；
- 数据质量有两个新确认：描述类标签被剥离、缺层会被 Slicer 规则化为平均间距；
- 缺层例的 Slicer 体积不是真实 3.0 mm 栅格，014/085 在 D17 不能直接用 1–2% 阈值判定；
- 085 完成第一份 Labelmap 体积基准（16.5597 cm³ / 5280 体素），几何自检通过；
- 目前 5 例中完成 1 例、截图 1 张；Day13 仍处于进行中。
