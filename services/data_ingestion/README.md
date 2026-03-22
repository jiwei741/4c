# Data Ingestion Service

## 目标

`services/data_ingestion` 对应成员 B 和成员 C 的数据接入边界。

这个服务不负责训练模型，而是负责把多源数据变成统一资产清单和标准化输入：

- Sentinel-2
- ERA5
- EDGAR
- NOAA
- GPP / MODIS

## 当前边界

输入：

- 外部公开数据源
- 研究区配置
- 时间范围配置

输出：

- 原始资产清单
- 统一命名的落盘目录
- 给 segmentation / inference 使用的标准化表

## 当前实现阶段

第一版只补：

- 配置模板
- 任务契约
- 目录边界

后续再把根目录和 `services/inference` 里已有的下载脚本迁移进来。

## 当前服务入口

```powershell
cd services/data_ingestion
python run_nanjing_ingestion.py sentinel-search --start-date 2025-01-01 --end-date 2025-01-31
python run_nanjing_ingestion.py sentinel-download --plan-json d:\4c\data\raw\sentinel2\nanjing\catalog\sentinel2_download_plan_nanjing_2025-01-01_to_2025-01-31.json --priority 1
python run_nanjing_ingestion.py era5-land --start-year 2020 --end-year 2024
```

说明：

- 这版是“迁移入口”，底层仍复用已经跑通过的下载脚本。
- 当前环境下外网访问仍可能受限，尤其是 Sentinel-2 catalog/token 获取。
