# GPP 月度 GeoTIFF 命名与目录规范

本文档用于让数据同学直接产出可接入成员 AA 训练链路的 GPP 月度 GeoTIFF。

目标是保证以下脚本可以直接使用：

- [extract_nanjing_gpp_quarterly_labels.py](../services/inference/extract_nanjing_gpp_quarterly_labels.py)
- [validate_gpp_monthly_directory.py](../services/inference/validate_gpp_monthly_directory.py)

## 一、目录规范

统一放在：

```text
data/raw/gpp/nanjing/monthly/
```

不要把不同年份分散到多个子目录。  
当前脚本默认直接读取这个目录下的所有月度 tif。

## 二、文件命名规范

每个月一个文件，严格按下面格式命名：

```text
map_YYYYMM.tif
```

例如：

- `map_202001.tif`
- `map_202002.tif`
- `map_202003.tif`
- `map_202412.tif`

不建议使用这些命名：

- `2020_01.tif`
- `gpp_202001.tif`
- `MOD17_2020_01.tif`
- `map_2020-01.tif`

原因很简单：当前标签提取脚本和校验脚本默认按 `map_YYYYMM.tif` 解析时间。

## 三、时间范围要求

当前季度版小模型建议准备：

- `2020-01` 到 `2024-12`

也就是总共 `60` 个 tif。

如果短期内产不出完整 `60` 个，也可以先交：

- `2021-01` 到 `2023-12`

但训练时间步会相应缩短。

## 四、空间要求

- 坐标系：`EPSG:4326 / WGS84`
- 覆盖范围：必须覆盖整个南京研究区
- 空间分辨率：保持原始 GPP 分辨率即可，不要求重采样到 10m

成员 AA 这边会按南京 `309` 网格中心点去采样，不直接要求你们先转成网格表。

## 五、像元数值要求

- 单波段栅格
- 像元值为 GPP 数值
- 如果有无效值，保留标准 `nodata`

当前提取脚本会：

- 先取网格中心点像元值
- 如果该点无效，再用周围 `3x3` 窗口均值补值

所以你们不需要先手工插值。

## 六、建议附带说明

建议在同目录再附一个简短说明文件，比如：

```text
data/raw/gpp/nanjing/monthly/README.txt
```

至少写清：

- 数据来源
- 产品名称
- 单位
- 时间范围
- 坐标系
- nodata 规则

## 七、校验命令

数据放好后，成员 AA 这边执行：

```bash
cd services/inference
uv run --offline python validate_gpp_monthly_directory.py --input-dir ../../data/raw/gpp/nanjing/monthly
```

如果命名和月份完整，脚本会返回：

- `valid: true`

## 八、标签生成命令

月度 tif 准备好后，可直接生成季度标签：

```bash
cd services/inference
uv run --offline python extract_nanjing_gpp_quarterly_labels.py --tif-dir ../../data/raw/gpp/nanjing/monthly
```

输出：

- `data/processed/features/nanjing/quarterly/labels.csv`

## 九、一句话要求

你们只需要做对三件事：

- 文件都放到同一个月度目录
- 文件名严格用 `map_YYYYMM.tif`
- 保证南京范围和 WGS84 坐标系正确
