# GPP 自动下载与标签生成

本文档说明如何把南京季度版小模型所需的 `GPP` 标签自动化到本地。

## 结论

当前最稳的官方路线是：

1. 用 `NASA Earthdata Login` 登录 `AppEEARS`
2. 提交南京区域 `MOD17A2HGF.061 / Gpp_500m` 面请求
3. 下载 `8-day GeoTIFF`
4. 直接对南京 `309` 个网格中心点采样
5. 聚合成季度 [labels.csv](../data/processed/features/nanjing/quarterly/labels.csv)

不再依赖手工整理月度 `GeoTIFF`。

## 官方依据

- AppEEARS API 文档  
  https://appeears.earthdatacloud.nasa.gov/api/
- AppEEARS 登录使用 NASA Earthdata Login  
  https://appeears.earthdatacloud.nasa.gov/api/
- `MOD17A2HGF.061` 产品图层查询  
  https://appeears.earthdatacloud.nasa.gov/api/product/MOD17A2HGF.061

其中 `MOD17A2HGF.061` 的可用图层包括：
- `Gpp_500m`
- `PsnNet_500m`
- `Psn_QC_500m`

当前项目只先用 `Gpp_500m`。

## 本地脚本

- 自动下载 AppEEARS GPP 8-day GeoTIFF  
  [download_nanjing_gpp_appeears_area.py](../services/inference/download_nanjing_gpp_appeears_area.py)

- 从 8-day GeoTIFF 直接生成季度标签  
  [extract_nanjing_gpp_quarterly_labels_from_8day.py](../services/inference/extract_nanjing_gpp_quarterly_labels_from_8day.py)

## 目录

- 原始下载目录  
  appeears_mod17a2hgf_061 (`data/raw/gpp/nanjing/appeears_mod17a2hgf_061`)

- 最终季度标签  
  [labels.csv](../data/processed/features/nanjing/quarterly/labels.csv)

## 环境变量

把下面两项填进 `.env.example` (`.env.example`) 对应的 `.env` (`.env`)：

```env
EARTHDATA_USERNAME=
EARTHDATA_PASSWORD=
```

## 执行命令

```bash
cd services/inference
uv sync
uv run --offline python download_nanjing_gpp_appeears_area.py
uv run --offline python extract_nanjing_gpp_quarterly_labels_from_8day.py
uv run --offline python build_training_dataset.py --config configs/nanjing_quarterly_dataset.yaml
uv run --offline python train.py --config configs/lstm_baseline_quarterly.yaml --dataset ../../data/processed/inference/nanjing_quarterly_v1.npz
uv run --offline python train.py --config configs/stgnn_gcn_lstm_quarterly.yaml --dataset ../../data/processed/inference/nanjing_quarterly_v1.npz
```

## 说明

- `download_nanjing_gpp_appeears_area.py` 会：
  - 登录 AppEEARS
  - 提交南京 bbox 面请求
  - 等待任务 `status=done`
  - 下载 bundle 中的文件到原始目录

- `extract_nanjing_gpp_quarterly_labels_from_8day.py` 会：
  - 扫描下载目录中的 `8-day GeoTIFF`
  - 从文件名解析 `YYYYMMDD`
  - 对南京 `309` 网格中心点采样
  - 直接按季度聚合

## 聚合口径

默认使用：
- `quarter_aggregator = sum`

原因：
- `MOD17A2HGF.061 / Gpp_500m` 单位是 `kgC/m^2/8day`
- 对季度目标来说，按季度求和比简单求均值更贴近“季度累计 GPP”

如果后面你们想把标签改成季度平均强度，也可以把脚本参数改成：

```bash
uv run --offline python extract_nanjing_gpp_quarterly_labels_from_8day.py --quarter-aggregator mean
```

## 当前状态

脚本和目录已经准备好，但由于本地还没有 `EARTHDATA_USERNAME / EARTHDATA_PASSWORD`，目前还不能真正把 GPP 下载到本机。  
也就是说，当前唯一剩余人工步骤是：准备一个 `NASA Earthdata Login` 账号并填入 `.env`。
