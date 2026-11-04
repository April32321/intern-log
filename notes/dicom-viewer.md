# DICOM viewer、Slicer 与 NIfTI 几何（D13）

> Day 13 笔记。目标：用眼验证数据，建立 5 例 GTV 体积基准，并理解
> DICOM → NIfTI 的几何关系。操作在 macOS 本机的 3D Slicer 5.12.4 +
> SlicerRT 完成；`dcm2niix` 与 `nibabel` 在终端完成。
>
> 数据：`data/raw/full/`；本日抽 001、014、021、085、128 五例。
> 生成文件：`work/dcm2niix/`（已 gitignore，不提交）。

## 1. 结论先行

1. Slicer 5.12.4 + SlicerRT 能正常加载 CT 与 RTSTRUCT；RTSTRUCT **加载时自动转成
   segmentation**，不需要手动 `Convert to segmentation`。
2. 5 例 GTV 体积基准已完成；001 与 128 无缺层，021 缺 1 层、085 缺 10 层、
   014 缺 16 层。缺层例的 Slicer spacing 是规则化后的平均值，不是真实 3.0 mm。
3. **014 几何存疑**：Mean/Median 约 −329 HU，SV 比 LM 大 22%，提示轮廓与
   规则化 CT 栅格可能错层；D17 不能直接按 1–2% 阈值判定。
4. **128 没有 GTV-1、没有 SEG**；主靶区是 `gtv-pre-operat`（148.458 cm³），
   `gtv-pre-op` 只有 2.72942 cm³，是独立小 ROI。pipeline 的
   `startswith("gtvpreop")` 会同时匹配两者，D16 必须修正。
5. DICOM 是 **LPS**，NIfTI/Slicer 是 **RAS**；dcm2niix 输出可能是 LAS，
   Slicer 导出的 mask 可能是 LPS。**必须读 affine**，不能按数组下标直接比较。
6. 001 的 NIfTI 与 Slicer mask 对齐后，mask 54639 体素 / 156323.43 mm³
   = 156.323 cm³，与 Slicer LM 完全一致。

## 2. 环境与数据

| 项 | 值 |
|---|---|
| Viewer | 3D Slicer 5.12.4 + SlicerRT |
| dcm2niix | v1.0.20261029（官方预编译 macOS 包） |
| Python | 3.14（miniconda base）+ nibabel |
| 数据根目录 | `data/raw/full/` |
| 5 例 | LUNG1-001、LUNG1-014、LUNG1-021、LUNG1-085、LUNG1-128 |

`work/` 已在 `.gitignore`，NIfTI 和中间产物不入库。

## 3. Slicer 操作（截图级）

### 3.1 加载

1. `Modules → DICOM`；
2. `Import DICOM files` 导入患者目录；
3. 在 `Series` 表里 **Cmd-click 同时选中 CT 和 RTSTRUCT**，再点 `Load`；
4. **不要加载 SEG**：SEG 与 RTSTRUCT 转出的 segmentation 容易重名，且 SEG 只是
   RTSTRUCT 的子集；
5. 加载后 RTSTRUCT 会自动变成 segmentation，结构列表里直接出现 ROI。

### 3.2 改名

`Modules → Data → Subject Hierarchy`，右键节点 → `Rename`：

```text
study       → LUNG1-XXX study YYYYMMDD
CT          → LUNG1-XXX_CT
RTSTRUCT    → LUNG1-XXX_RT
```

- 括号里的日期是 `StudyDate`，保留在名称里方便和 DICOM 头对照；
- **不要改 `acquisition transform`**；
- 有 `..._1` 重复 segmentation 时删副本；
- 重命名只影响 Slicer 显示，不改原始 DICOM。

### 3.3 阅片

- 布局切四宫格（三平面 + 3D），十字线联动；
- `Volumes → Display` 切换预设：
  - 肺窗 `CT-Lung`：WW 1500 / WL −600；
  - 纵隔窗 `CT-Mediastinal`：WW 350 / WL 40；
- `Segmentations` 里只显示目标 ROI，其余全部隐藏；
- 085 有 10 个 ROI，只能选 `GTV-1`；`gtv-2..7` 是另一套靶区，不能合并。

### 3.4 Segment Statistics

1. `Segmentations` 里只勾目标 segment；
2. `Representations` 勾 `Binary labelmap`；否则只出 ClosedSurface 列；
3. `Modules → Segment Statistics`（独立模块，不在 Segmentations 里）；
4. 输入：
   - `Segmentation` = `LUNG1-XXX_RT`
   - `Scalar volume` = `LUNG1-XXX_CT`
   - `Output table` = `Create new table`，命名 `stats_<ID>`
5. `Apply`；
6. 主表用：
   - `Voxel count (LM)`
   - `Volume mm3 (LM)` / `Volume cm3 (LM)`
   - `ScalarVolume_Mean`
7. `SV`、`CS` 只作旁证，不要用 `ClosedSurface_Volume_mm3` 替代 LM。

### 3.5 截图

- 三平面 + 患者 ID + GTV 轮廓；
- 肺窗为主，纵隔窗可选；
- 文件名：

```text
results/figures/viewer/<PatientID>_gtv1_3plane_lung.png
128: results/figures/viewer/LUNG1-128_gtvpreoperat_3plane_lung.png
```

- 021 当前只有纵隔窗：`LUNG1-021_gtv1_3plane_mediastinal.png`；
- 014 冠状面为空，建议重拍时把三平面都对准病灶。

### 3.6 导出 GTV mask 为 NIfTI

GUI 里如果找不到 `Export to files`，用 Slicer Python Console。先确认
segmentation 名称和 segment ID：

```python
seg = slicer.util.getNode('3: RTSTRUCT: 20190225')
segmentation = seg.GetSegmentation()

for sid in segmentation.GetSegmentIDs():
    s = segmentation.GetSegment(sid)
    print(repr(s.GetName()), sid)
```

再导出 GTV-1：

```python
import os

gtv_ids = [
    sid for sid in segmentation.GetSegmentIDs()
    if segmentation.GetSegment(sid).GetName() == 'GTV-1'
]

vols = [
    n for n in slicer.util.getNodesByClass('vtkMRMLScalarVolumeNode')
    if n.GetClassName() == 'vtkMRMLScalarVolumeNode'
]

ct = next(
    (n for n in vols
     if n.GetImageData() and tuple(n.GetImageData().GetDimensions()) == (512, 512, 134)),
    vols[0]
)

seg.CreateBinaryLabelmapRepresentation()

labelmap = slicer.mrmlScene.AddNewNodeByClass(
    'vtkMRMLLabelMapVolumeNode', 'LUNG1-001_GTV1')

ok = slicer.modules.segmentations.logic().ExportSegmentsToLabelmapNode(
    seg, gtv_ids, labelmap, ct)

print("export ok:", ok)
slicer.util.saveNode(
    labelmap,
    "/Users/wangjiaqi/Desktop/实习日志/work/dcm2niix/LUNG1-001/LUNG1-001_GTV1.nii.gz")
```

注意：

- `ExportSegmentsToLabelmapNode` 要的是 **segment ID**，不是名字；
- 这个 Slicer 版本的 `vtkMRMLSegmentationNode` 没有 `GetMasterVolumeNode()`，
  直接列 `vtkMRMLScalarVolumeNode`，按 `(512, 512, 134)` 选 CT；
- 只有 `Binary labelmap` 表示存在时，导出才会得到 voxel mask。

## 4. 窗宽窗位

只影响显示，不改 HU：

```text
显示区间 = [WL − WW/2, WL + WW/2]
g = clip((HU − (WL − WW/2)) / WW, 0, 1) × 255
```

| 预设 | WW | WL | HU 区间 |
|---|---:|---:|---|
| 肺窗 | 1500 | −600 | [−1350, 150] |
| 纵隔窗 | 350 | 40 | [−135, 215] |

组学特征必须从原始 HU 算，不能从截图或 8-bit 窗化图算；PyRadiomics 用
`binWidth` 自己离散化，不读窗宽窗位。

## 5. 缺层与 spacing

### 5.1 反推公式

```text
spacing_z = (z_max − z_min) / (n_present − 1)
n_true    = round((z_max − z_min) / 3.0) + 1
missing   = n_true − n_present
          = (spacing_z / 3.0 − 1) × (n_present − 1)
```

前提：名义层距 3.0 mm，缺层是孤立缺口。

### 5.2 5 例的层数与 spacing

| 病例 | 现有层数 | 缺层 | 真实层数 | z 范围 | Slicer spacing |
|---|---:|---:|---:|---:|---:|
| LUNG1-001 | 134 | 0 | 134 | 399 mm | 3.000 |
| LUNG1-021 | 197 | 1 | 198 | 591 mm | 3.0153 |
| LUNG1-085 | 106 | 10 | 116 | 345 mm | 3.2857 |
| LUNG1-128 | 100 | 0 | 100 | 297 mm | 3.000 |
| LUNG1-014 | 87 | 16 | 103 | 306 mm | 3.5581 |

缺层例的 Slicer 体素栅格是规则化的平均 spacing，不是真实 3.0 mm。
014/085 的轮廓 z 与规则层位可能错位，这是体积差异的主要风险。

## 6. 5 例体积表

主表用 **LM**；`pipeline cm³` 与 `Δ%` 留给 D17。

| PatientID | ROI | Slicer cm³ | VoxelCount | Mean HU | Slicer z spacing | pipeline cm³ | Δ% | 备注 |
|---|---|---:|---:|---:|---:|---:|---:|---|
| LUNG1-001 | GTV-1 | 156.323 | 54639 | −64.13 | 3.000 | | | 无缺层；LM=SV；CS=154.998 |
| LUNG1-014 | GTV-1 | 9.5675 | 2817 | −328.89 | 3.5581 | | | 缺 16 层；几何存疑 |
| LUNG1-021 | GTV-1 | 214.299 | 74456 | −63.66 | 3.0153 | | | 缺 1 层；SV +2.76% |
| LUNG1-085 | GTV-1 | 16.5597 | 5280 | −34.35 | 3.2857 | | | 缺 10 层；SV +1.42% |
| LUNG1-128 | gtv-pre-operat | 148.458 | 51890 | −17.86 | 3.000 | | | 无 GTV-1/SEG；另有小 ROI 2.72942 |

完整 20 列数据见：

```text
results/tables/slicer_stats_all.tsv
```

原始单表在 `results/tables/slicer_raw/`。

## 7. 各例 QC

### LUNG1-001

- LM 156.323 cm³ / 54639；SV 与 LM 相同；CS 154.998（−0.85%）；
- Mean −64.127，Min −1021，Max 1040，SD 202.863，Median 11，P5 −563，
  P95 68，Surface 20035.6 mm²；
- 无缺层，spacing 0.9765625 × 0.9765625 × 3.0，是干净基准。

### LUNG1-014

- LM 9.5675 cm³ / 2817；SV 11.6732（+22.0%）；CS 9.6952（+1.33%）；
- Mean −328.887，Median −329，P5 −872，P95 152，SD 358.802；
- 缺 16 层，z spacing 3.5581；
- Mean/Median 约 −329、SV +22% 是几何错层的强提示；D17 不作可靠体积基准，
  应同栅格比较、Dice/质心或直接排除 1–2% 阈值。

### LUNG1-021

- LM 214.299 cm³ / 74456；SV 220.208（+2.76%）；CS 215.614（+0.61%）；
- Mean −63.656，SD 308.629，Min −1001，Max 1062，Median 35，P5 −749，
  P95 335，Surface 22405.1 mm²；
- 缺 1 层，z spacing 3.0153，影响较小；
- 截图当前是纵隔窗，肺窗可补。

### LUNG1-085

- LM 16.5597 cm³ / 5280；SV 16.7949（+1.42%）；CS 16.5812（+0.13%）；
- Mean −34.3462，SD 190.287，Min −854，Max 144，Median 52，P5 −500，
  P95 99，Surface 3604.92 mm²；
- 缺 10 层，z spacing 3.2857，拉伸栅格；D17 放宽阈值或同栅格比较。

### LUNG1-128

- 无 GTV-1、无 SEG；
- `gtv-pre-operat`：LM 148.458 cm³ / 51890；SV 与 LM 相同；
  CS 146.478（−1.33%）；Mean −17.8635，Median −1，P5 −921，P95 435，
  SD 302.563，Surface 21743 mm²；大靶区，含空洞/空气；
- `gtv-pre-op`：LM 2.72942 cm³ / 954；SV 与 LM 相同；CS 1.92077（−29.6%）；
  Mean 63.2013，Median 11，P5 −87，P95 378，Surface 1878.05 mm²；
  独立小 ROI，不能与大的合并；
- pipeline 的 `startswith("gtvpreop")` 会同时匹配两个 ROI，D16 必须改成精确匹配
  `gtv-pre-operat` 或明确优先级。

## 8. DICOM LPS ↔ NIfTI / Slicer RAS

```text
DICOM 患者坐标：+x Left,   +y Posterior, +z Superior
NIfTI / Slicer：+x Right,  +y Anterior,  +z Superior

p_RAS = (−x_LPS, −y_LPS, z_LPS)
M_RAS = F · M_LPS,  F = diag(−1, −1, 1, 1)
```

方向余弦：

```text
r = IOP[0:3]          # 列索引增大方向
c = IOP[3:6]          # 行索引增大方向
n = r × c             # 切片法向

Δr = PixelSpacing[0]  # 行间距，沿 c
Δc = PixelSpacing[1]  # 列间距，沿 r
Δs = (IPP_{k+1} − IPP_k) · n

p_LPS = IPP + i·Δc·r + j·Δr·c + k·Δs·n
```

- `PixelSpacing` 顺序是 **[行, 列]**，最容易写反；
- 真实层距用相邻 IPP 差，不要用 `SliceThickness`；
- dcm2niix 可能做轴置换/翻转，以文件里的 affine 为准。

## 9. dcm2niix 实操（001）

### 9.1 转换

```bash
mkdir -p work/dcm2niix/LUNG1-001

dcm2niix -z y -b y \
  -o work/dcm2niix/LUNG1-001 \
  -f "LUNG1-001_CT" \
  "data/raw/full/LUNG1-001/CT/1.3.6.1.4.1.32722.99.99.298991776521342375010861296712563382046"
```

输出：

```text
Found 134 DICOM file(s)
Convert 134 DICOM as .../LUNG1-001_CT (512x512x134x1)
```

### 9.2 NIfTI 几何

```text
shape   = (512, 512, 134)
zooms   = (0.9765625, 0.9765625, 3.0)
voxel   = 2.8610 mm³
axcodes = ('L', 'A', 'S')

affine =
[[ -0.9765625,  0,          0,          249.51171875],
 [  0,          0.9765625,  0,          -38.51171875],
 [  0,          0,          3.0,        -681.5],
 [  0,          0,          0,          1]]
```

### 9.3 Slicer mask 与 j 轴翻转

Slicer 导出：

```text
work/dcm2niix/LUNG1-001/LUNG1-001_GTV1.nii.gz
mask values = {0, 1}
voxels      = 54639
volume      = 156323.43 mm³ = 156.323 cm³
```

几何：

```text
mask axcodes = ('L', 'P', 'S')
mask affine y = −0.9765625·j + 460.51171875
CT   affine y = +0.9765625·j − 38.51171875
```

只差 j 轴翻转：

```text
460.51171875 − 511 × 0.9765625 = −38.51171875
```

用 `as_reoriented` 转到 CT 的 LAS：

```python
from nibabel.orientations import axcodes2ornt, ornt_transform

ornt = ornt_transform(
    axcodes2ornt(nib.aff2axcodes(mask.affine)),
    axcodes2ornt(nib.aff2axcodes(ct.affine))
)
mask_ct = mask.as_reoriented(ornt)
```

结果：

```text
mask_ct axcodes = ('L', 'A', 'S')
affine equal    = True
voxels          = 54639
volume          = 156323.43 mm³
```

`as_reoriented` 只做轴翻转，不插值，所以体素数和体积不变。
`resample_from_to` 需要 scipy；本例只差轴方向，不需要插值。

## 10. 为什么 radiomics 要先转 NIfTI / 重采样

- DICOM 一层一个文件，几何分散在每层 IPP/IOP；NIfTI 一个文件带一个 affine；
- RTSTRUCT 是矢量轮廓，dcm2niix 不会转换，必须先栅格化成 labelmap；
- 3D 纹理的邻域依赖 spacing：`0.977 × 0.977 × 3.0` 时，z 方向邻居的物理距离
  是面内的约 3 倍，不重采样就不是各向同性邻域；
- 常见做法：图像重采样到 `1 × 1 × 1 mm` 用 B-spline，mask 用最近邻；
- **体积要在原始栅格上算**，不要用重采样后的 mask 算体积；
- 图像和 mask 必须在同一 affine/栅格上；shape 相同不代表下标对齐。

## 11. 常见坑

1. `Segment Statistics` 只在 `Segmentations` 里找不到，它是独立模块；
2. 只出 ClosedSurface：在 `Representations` 勾 `Binary labelmap` 再重跑；
3. `Table.tsv` 复用会覆盖上一例；每例另存 `stats_<ID>.tsv`；
4. macOS 保存对话框把 `/` 换成 `:`，路径会变成文件名；先存桌面再 `mv`；
5. 不要改 `acquisition transform`；
6. 不要加载 SEG，容易和 RTSTRUCT 转出的 segmentation 重名；
7. 021 截图是纵隔窗，肺窗可补；014 冠状面为空；
8. 128 两个 ROI 不是重复，不能合并；`startswith("gtvpreop")` 会选错；
9. 014 的 SV +22%、Mean −329 不是普通噪声，先怀疑几何错层；
10. dcm2niix 的 CT 是 LAS，Slicer mask 可能是 LPS；不读 affine 会镜像。

## 12. 文件与复现

| 内容 | 位置 |
|---|---|
| 5 例截图 | `results/figures/viewer/` |
| 合并统计表 | `results/tables/slicer_stats_all.tsv` |
| 原始单表 | `results/tables/slicer_raw/` |
| 5 例对照摘要 | `results/tables/gtv_volume_check.csv` |
| dcm2niix 输出 | `work/dcm2niix/LUNG1-001/`（gitignore） |
| 日志 | `journal/day13.md` |
| 缺层来源 | `logs/day12-check-190.txt` |

复现 001 的 NIfTI 检查：

```bash
python3 - <<'PY'
import nibabel as nib
import numpy as np

ct = nib.load("work/dcm2niix/LUNG1-001/LUNG1-001_CT.nii.gz")
mask = nib.load("work/dcm2niix/LUNG1-001/LUNG1-001_GTV1.nii.gz")

print(ct.shape, ct.header.get_zooms()[:3], nib.aff2axcodes(ct.affine))
print(mask.shape, mask.header.get_zooms()[:3], nib.aff2axcodes(mask.affine))
print(np.allclose(ct.affine, mask.affine, atol=1e-4))
PY
```

如果 mask 是 LPS、CT 是 LAS，先用 `as_reoriented` 对齐，再比较体素和体积。
