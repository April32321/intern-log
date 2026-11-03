# DICOM 关键字段（D12）

> 用途：`code/01_check_dicom.py`、`code/02_build_index.py` 读元数据时的字段速查。
> 层级：Patient → Study → Series → Instance，每层一个 UID。

## 1. 身份与层级

| 字段 | Tag | 简短解释 |
|---|---|---|
| `PatientID` | (0010,0020) | 患者 ID，如 `LUNG1-001`；与临床表 `merge` 的唯一键 |
| `StudyInstanceUID` | (0020,000D) | 一次检查的唯一编号；同患者多次检查靠它区分 |
| `SeriesInstanceUID` | (0020,000E) | 一个序列（CT / RTSTRUCT / SEG 各一个）的唯一编号；`series_dir` 的来源 |
| `SOPInstanceUID` | (0008,0018) | 单个文件的唯一编号；去重、排序、写清单用 |

## 2. 影像属性（CT）

| 字段 | Tag | 简短解释 |
|---|---|---|
| `Modality` | (0008,0060) | 文件类型：`CT` / `RTSTRUCT` / `SEG` / `RTDOSE`；分流第一判据 |
| `SliceThickness` | (0018,0050) | 标称层厚（mm）；实际层距用相邻切片 z 差更可靠 |
| `PixelSpacing` | (0028,0030) | 面内像素间距（mm/像素），顺序是 **[行, 列] = [y, x]** |
| `ImagePositionPatient` | (0020,0032) | 切片左上角体素中心的患者坐标 `[x, y, z]`（mm）；按 z 排序 |
| `Rows` / `Columns` | (0028,0010) / (0028,0011) | 图像高 / 宽（像素数）；`Rows` 配 `PixelSpacing[0]` |

常配套使用：`ImageOrientationPatient` (0020,0037) 方向余弦、`SpacingBetweenSlices` (0018,0088) 实际层距。

## 3. RTSTRUCT（无像素，只有轮廓）

| 字段 | Tag | 简短解释 |
|---|---|---|
| `StructureSetROISequence` | (3006,0020) | ROI 名单，Item 内含 `ROINumber`、`ROIName`（如 `GTV-1`）；`roi_names`、`gtv1_present` 的来源 |
| `ROIContourSequence` | (3006,0039) | ROI 轮廓，Item 内含 `ReferencedROINumber`、`ContourSequence` |
| `ContourData` | (3006,0050) | 轮廓点坐标 `[x1,y1,z1, ...]`（mm，患者坐标系），需 reshape 成 `(-1,3)` |

- 一个 ROI 在每层切片各有一条闭合轮廓，按 z 分组后栅格化成掩膜。
- `ROIName` 命名不统一（`GTV-1` / `GTV1` / `GTV_1`），不要写死字符串。

## 4. SEG（有像素的掩膜）

| 字段 | Tag | 简短解释 |
|---|---|---|
| `SegmentSequence` | (0062,0002) | 每个 Segment 对应一个 ROI，含 `SegmentLabel`、`SegmentNumber` |
| `PixelData` | (7FE0,0010) | 标签图而非 HU：0 = 背景，1/2/3… = 各 Segment |
| `PerFrameFunctionalGroupsSequence` | (5200,9230) | 每帧记录它对应哪张 CT 切片（`ReferencedSOPInstanceUID`） |

**SEG ⊂ RTSTRUCT**：RTSTRUCT 是全部 ROI 的矢量轮廓；SEG 只是其中一部分 ROI 栅格化后的掩膜，可能只含 `GTV-1`，也可能缺失。故 `has_rtstruct`、`has_seg` 分两列统计，不能互相替代。

## 5. 读取习惯

```python
ds = pydicom.dcmread(f, stop_before_pixels=True)   # 只读元数据，快
val = getattr(ds, "SliceThickness", None)          # 缺失字段不要直接点
```
