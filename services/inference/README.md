# Inference Framework

成员 A 的算法框架先按“可尽快跑通”来落，不直接依赖 PyG。
第一版采用两条线并行：

- `LSTM baseline`：单节点时序基线，负责保底。
- `ST-GNN v1`：`GraphConv + LSTM`，先把空间邻接和时间建模跑通，后续再替换成更完整的 PyG 版本。

## 先写哪些文件

- `create_mock_dataset.py`
  - 生成一个能直接训练的 mock 图时序数据集，先验证训练链路。
- `build_training_dataset.py`
  - 把真实的 `Sentinel-2 + ERA5 + EDGAR + labels` 特征表拼成训练用 `NPZ`。
- `prepare_nanjing_quarterly_remote_sensing.py`
  - 清洗 `remote_sensing_output_ver.03.20` 的季度版南京遥感特征，输出正式训练输入表。
- `build_nanjing_era5_quarterly_features.py`
  - 把月度 ERA5 点位表映射到南京 309 网格，并聚合成季度气象特征。
- `download_nanjing_edgar_co2_sectors.py`
  - 下载 EDGAR 2025 CO2 工业相关 sector 年度网格图。
- `build_nanjing_edgar_quarterly_features.py`
  - 把 EDGAR 年度网格排放映射到南京 309 网格，并展开成季度特征。
- `extract_nanjing_gpp_quarterly_labels.py`
  - 从月度 GPP GeoTIFF 为南京 309 网格提取季度标签。
- `download_nanjing_gpp_appeears_area.py`
  - 通过 AppEEARS 下载南京区域 `MOD17A2HGF.061 / Gpp_500m` 的 8-day GeoTIFF。
- `extract_nanjing_gpp_quarterly_labels_from_8day.py`
  - 直接从 AppEEARS 下载的 8-day GPP GeoTIFF 为南京 309 网格生成季度标签。
- `train.py`
  - 统一训练入口，支持 `lstm_baseline` 和 `stgnn_gcn_lstm`。
- `predict.py`
  - 统一推理入口，给后端模型 API 对接做原型。
- `run_scenario.py`
  - 情景推演入口，模拟“新增工业区后重新推理”。
- `src/spatio_eco_inference/dataset.py`
  - 训练数据加载、滑窗切分、样本划分。
- `src/spatio_eco_inference/models/lstm_baseline.py`
  - 基线模型。
- `src/spatio_eco_inference/models/stgnn.py`
  - 第一版图时序模型。
- `src/spatio_eco_inference/training.py`
  - 模型构建、训练循环、指标计算。
- `src/spatio_eco_inference/scenario.py`
  - 情景推演的节点/特征修改逻辑。

## 每个文件负责什么

- `configs/lstm_baseline.yaml`
  - LSTM 的输入窗口、隐藏维度、训练参数。
- `configs/stgnn_gcn_lstm.yaml`
  - ST-GNN 的图卷积维度、时序窗口和训练参数。
- `configs/real_dataset_template.yaml`
  - 真实训练样本拼接的 manifest 模板。
- `configs/nanjing_quarterly_dataset.yaml`
  - 南京 309 网格季度版训练 manifest。
- `configs/lstm_baseline_quarterly.yaml`
  - 南京季度版 LSTM 训练配置。
- `configs/stgnn_gcn_lstm_quarterly.yaml`
  - 南京季度版 ST-GNN v1 训练配置。
- `examples/mock_scenario.json`
  - 情景推演示例输入。
- `outputs/`
  - 模型权重、训练历史、评估指标。

## 训练数据格式

成员 A 的第一版训练数据统一用 `NPZ`，避免当前环境里 `pandas` 版本冲突。

必须字段：

- `x`: `float32[T, N, F]`
  - 全时序节点特征。
- `y`: `float32[T, N]` 或 `float32[T, N, 1]`
  - 节点级预测目标。
- `adjacency`: `float32[N, N]`
  - 邻接矩阵，0/1 或带权都可以。

建议字段：

- `timestamps`: `str[T]`
- `node_ids`: `str[N]`
- `feature_names`: `str[F]`
- `target_name`: `str[1]`

当前建议的真实特征顺序：

1. `vegetation_area_ratio`
2. `ndvi_mean`
3. `land_surface_temperature`
4. `edgar_emission`
5. `u10_wind`
6. `v10_wind`
7. `precipitation`

`y` 第一版建议先定义为单目标：

- `net_carbon_flux`

正式版训练样本不是直接从 `.SAFE / .nc` 原始文件喂给模型，而是先由数据链路抽成对齐后的表，再由成员 A 这边拼成 `NPZ`。当前脚本要求 5 张表：

- `grid_nodes.csv`
  - 至少包含 `node_id, latitude, longitude`
- `sentinel2_features.csv`
  - 至少包含 `timestamp, node_id, vegetation_area_ratio, ndvi_mean`
- `era5_features.csv`
  - 至少包含 `timestamp, node_id, land_surface_temperature, u10_wind, v10_wind, precipitation`
- `edgar_features.csv`
  - 至少包含 `timestamp, node_id, edgar_emission`
- `labels.csv`
  - 至少包含 `timestamp, node_id, net_carbon_flux`

注意：只有 `Sentinel-2 + ERA5 + EDGAR` 还不能训练，因为它们只是输入特征，没有监督目标。训练一定还要有 `labels.csv`，当前建议由 `MODIS GPP / 净碳通量代理值` 来提供。

## 南京季度版接入

当前项目已经有可直接复用的南京季度遥感成果：

- `remote_sensing_output_ver.03.20/grid_nodes.csv`
- `remote_sensing_output_ver.03.20/nanjing_sentinel2_features_quarterly_2020_2024.csv`

建议先走季度版训练链路：

1. 清洗季度遥感输入
   - `uv run --offline python prepare_nanjing_quarterly_remote_sensing.py`
2. 用月度 ERA5 点位表生成南京季度气象特征
   - `uv run --offline python build_nanjing_era5_quarterly_features.py --era5-csv <monthly_era5.csv>`
3. 下载并生成季度版 EDGAR 特征
   - `uv run --offline python download_nanjing_edgar_co2_sectors.py`
   - `uv run --offline python build_nanjing_edgar_quarterly_features.py`
3. 用月度 GPP GeoTIFF 生成季度标签
   - `uv run --offline python extract_nanjing_gpp_quarterly_labels.py --tif-dir <monthly_gpp_tif_dir>`
3a. 或者直接走 AppEEARS 自动化 GPP 链路
   - `uv run --offline python download_nanjing_gpp_appeears_area.py`
   - `uv run --offline python extract_nanjing_gpp_quarterly_labels_from_8day.py`
4. 拼训练集
   - `uv run --offline python build_training_dataset.py --config configs/nanjing_quarterly_dataset.yaml`
5. 训练季度版模型
   - `uv run --offline python train.py --config configs/lstm_baseline_quarterly.yaml --dataset ../../data/processed/inference/nanjing_quarterly_v1.npz`
   - `uv run --offline python train.py --config configs/stgnn_gcn_lstm_quarterly.yaml --dataset ../../data/processed/inference/nanjing_quarterly_v1.npz`

### 关于 `computer_design` master 分支

已验证它的思路可以迁移，但它自带的数据不能直接作为南京 309 网格训练输入：

- `ERA5.py` 的变量选择可复用
- `GPP.py` 的“从月度栅格按空间节点提取标签”逻辑可复用
- 但 `data_stream-moda.csv` 只有江宁区 `15` 个点位
- 实测映射到南京 `309` 网格时，最近点距离可超过 `50km`

因此当前仓库里的 `master` 分支适合当“脚本原型参考”，不适合直接当“南京 309 网格正式数据源”。

## 第一个可运行版本怎么落地

0. 在当前目录创建隔离环境
   - `cd services/inference`
   - `uv sync`
1. 先用 mock 数据把训练链路跑通
   - `uv run --offline python create_mock_dataset.py`
2. 训练基线模型
   - `uv run --offline python train.py --config configs/lstm_baseline.yaml --dataset ../../data/processed/inference/mock/nanjing_mock_v1.npz`
3. 训练 ST-GNN v1
   - `uv run --offline python train.py --config configs/stgnn_gcn_lstm.yaml --dataset ../../data/processed/inference/mock/nanjing_mock_v1.npz`
4. 做一次预测
   - `uv run --offline python predict.py --checkpoint outputs/stgnn_gcn_lstm_mock/best.pt --dataset ../../data/processed/inference/mock/nanjing_mock_v1.npz`
5. 做一次情景推演
   - `uv run --offline python run_scenario.py --checkpoint outputs/stgnn_gcn_lstm_mock/best.pt --dataset ../../data/processed/inference/mock/nanjing_mock_v1.npz --scenario examples/mock_scenario.json`

## 真实数据接入顺序

1. 成员 B/C 先把原始数据抽成 5 张对齐表
2. 你编辑 `configs/real_dataset_template.yaml`
3. 运行 `uv run --offline python build_training_dataset.py --config configs/real_dataset_template.yaml`
4. 先跑 `LSTM baseline`
5. 基线正常后切到 `ST-GNN v1`
6. 指标和收敛正常后，再替换成更复杂的 PyG 版本

## 这台机器能承担什么

当前机器实测资源：

- GPU: `RTX 3050 Laptop GPU 4GB`
- RAM: `16GB`
- D 盘空闲: 约 `61GB`

结论：

- 能承担：
  - 训练样本拼接
  - 小范围 `LSTM baseline`
  - 小范围 `ST-GNN v1`
  - 南京市单城、`309` 节点、`20` 个季度时间步的实验
- 不能稳妥承担：
  - 大范围 `SAM-2` 批量推理
  - 全量 Sentinel-2 原始影像处理
  - 大图规模、长时间窗、复杂 ST-GNN 调参

对于当前季度版数据，如果只做：

- `309` 节点
- `20` 个季度时间步
- `4` 个季度输入窗口
- `1` 季度预测

这台机器可以训练：

- `LSTM baseline`
- 当前这版 `GraphConv + LSTM`

但前提是：

- 先把 `ERA5` 和 `GPP labels` 做成表
- 不在本机跑 `SAM-2`
- 批量大小保持在 `2-4`

如果要做正式训练，建议配置至少：

- GPU 显存：`8GB` 起步，`12GB-16GB` 更稳
- 内存：`32GB`
- 可用磁盘：`150GB+`
- 推荐环境：
  - 本机负责样本拼接、调代码、跑小实验
  - 正式训练放到学校 GPU 服务器或 AutoDL

## 当前框架定位

这版骨架解决的是三件事：

- 先把成员 A 的职责边界落成代码目录
- 先定义稳定的数据接口
- 先保证“训练 -> 推理 -> 情景推演”可以端到端跑通
