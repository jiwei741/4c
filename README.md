# Spatio-Eco

Spatio-Eco 是一个面向区域碳汇监测、预测与情景推演的时空平台原型。当前仓库已经收敛到一条更清晰的本地链路：

- 使用高精度季度 Sentinel-2 地类特征进行训练与展示
- 提供可直接联调的后端 API、前端页面和情景推演能力
- 保留数据接入与流式处理骨架，当前主链路只保留必要模块

## 当前范围

- 季度训练数据与模型产物已经就绪
- 后端直接聚合 `services/inference/outputs` 中的模型结果
- 前端使用 Vue 3 + Vite + Cesium
- Sentinel-2 当前正式来源为本地 refined quarterly 数据表

## 目录结构

- `services/inference/`
  模型训练、预测、情景推演与数据拼接
- `services/backend/`
  平台后端 API
- `services/frontend/`
  前端可视化页面
- `services/data_ingestion/`
  数据接入与下载入口骨架
- `services/streaming/`
  流式处理与数据库侧骨架
- `data/processed/features/`
  当前用于训练和展示的处理后特征
- `data/processed/inference/`
  训练集 NPZ 与元数据
- `docs/`
  训练记录、平台说明与发布清单
- `scripts/`
  启停、联调与辅助脚本

## 数据说明

- 当前正式使用的季度 Sentinel-2 特征表：
  [sentinel2_features.csv](data/processed/features/nanjing/quarterly/sentinel2_features.csv)
- 这份表由 `data_for_memberA` 中的高精度季度源数据标准化生成
- `time_analysis.csv` 属于同源扩展表，已经视为重复副本，不再作为训练输入

## 一键启动
要求：
- Windows + PowerShell
- `uv`
- Node.js `^20.19.0 || >=22.12.0`
- 根目录存在 `.env`
- 端口 `8000`、`4173` 可用

启动：
```powershell
cd d:\4c
powershell -ExecutionPolicy Bypass -File scripts/start_platform.ps1
```

跳过自动打开浏览器：

```powershell
cd d:\4c
powershell -ExecutionPolicy Bypass -File scripts/start_platform.ps1 -NoBrowser
```

停止：
```powershell
cd d:\4c
powershell -ExecutionPolicy Bypass -File scripts/stop_platform.ps1
```

联调检查：

```powershell
cd d:\4c
python scripts/test_platform_integration.py
```

## 访问地址

- 前端：<http://127.0.0.1:4173/>
- 后端健康检查：<http://127.0.0.1:8000/api/v1/health>
- 平台总览：<http://127.0.0.1:8000/api/v1/dashboard>

## Docker 一键部署

要求：
- Docker Desktop
- 建议至少 8GB 内存

启动：
```powershell
cd d:\4c
docker compose --env-file .env.docker up -d --build
```

访问：
- 平台：<http://127.0.0.1:8080/>

停止：
```powershell
cd d:\4c
docker compose --env-file .env.docker down
```

最短部署说明见：
- [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md)

## Docker 镜像发布版

如果你们要把平台交付给使用方，并且不希望对方下载完整源码，可以使用镜像发布版。

我们内部发布镜像：
```powershell
cd d:\4c
powershell -ExecutionPolicy Bypass -File scripts\docker\build_release_images.ps1 -RegistryNamespace your-dockerhub-username -Tag v1.0.0
powershell -ExecutionPolicy Bypass -File scripts\docker\push_release_images.ps1 -RegistryNamespace your-dockerhub-username -Tag v1.0.0
```

使用方部署：
```powershell
docker compose -f docker-compose.release.yml --env-file .env.release pull
docker compose -f docker-compose.release.yml --env-file .env.release up -d
```

说明文档见：
- [DOCKER_RELEASE.md](DOCKER_RELEASE.md)
- [.env.release.example](.env.release.example)
- [docker-compose.release.yml](docker-compose.release.yml)

## 文档入口

- [详细方案](Spatio-Eco_详细方案.md)
- [成员 AA 模型训练数据补充清单](docs/02_成员AA模型训练数据补充清单.md)
- [南京季度版训练接入方案](docs/03_南京季度版训练接入方案.md)
- [平台框架与服务边界](docs/12_平台框架与服务边界_2026-03-21.md)
- [平台联调与启动说明](docs/13_平台联调与启动说明_2026-03-21.md)
- [Public 仓库发布清单](docs/15_Public仓库发布清单_2026-03-22.md)

## 当前说明

- 当前仓库默认使用本地 refined quarterly Sentinel-2 特征
- 后端接口已经收口为当前平台所需的最小集合
- 旧的远程分割原型和旧页面目录已经从主链路移除
