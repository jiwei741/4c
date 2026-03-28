# Spatio-Eco

Spatio-Eco 是一个面向双碳与生态监测场景的时空平台原型。当前仓库已经具备：

- 季度版模型训练与推理链路
- 后端 API、情景推演和平台管理接口
- 前端业务工作台与中英文切换
- `SAM-2` 远程执行边界与结果回传骨架

当前定位是：**本地可运行的平台 MVP + 远程 GPU 执行的遥感分割流程**。

## 当前结构

- `services/inference/`
  成员 A 算法、训练、推理、情景推演
- `services/backend/`
  平台后端 API
- `services/frontend/`
  前端业务工作台
- `services/data_ingestion/`
  数据接入与下载入口
- `services/segmentation/`
  `SAM-2` 任务清单、远程 bundle、结果导回
- `services/streaming/`
  Kafka / Flink 骨架
- `docs/`
  项目说明、训练记录、平台说明、远程执行说明
- `scripts/`
  平台启动、联调测试和辅助脚本

## 本地与远程边界

本地负责：

- 平台开发与联调
- 成员 A 模型训练与推理
- 后端、前端、数据接入骨架
- `SAM-2` 远程任务准备和结果导入

远程 GPU 负责：

- 真实 `SAM-2` 批量推理
- 大规模 `Sentinel-2` 原始影像分割

说明见：

- [平台联调与启动说明](docs/13_平台联调与启动说明_2026-03-21.md)
- [SAM-2 远程执行与本地边界](docs/14_SAM2远程执行与本地边界_2026-03-21.md)

## 快速启动

要求：

- Windows + PowerShell
- 已安装 `uv`
- 本地已创建 `.env`

启动：

```powershell
cd d:\4c
powershell -ExecutionPolicy Bypass -File scripts/start_platform.ps1
```

启动后自动打印：

- 前端地址
- 后端健康检查地址

启动成功后会自动打开浏览器；如需跳过：

```powershell
cd d:\4c
powershell -ExecutionPolicy Bypass -File scripts/start_platform.ps1 -NoBrowser
```

联调测试：

```powershell
cd d:\4c
python scripts/test_platform_integration.py
```

停止：

```powershell
cd d:\4c
powershell -ExecutionPolicy Bypass -File scripts/stop_platform.ps1
```

## 前端页面

- `/`
  平台总览
- `/models.html`
  模型指标与预测结果
- `/operations.html`
  数据源策略、远程分割状态、平台运维信息
- `/research.html`
  文档、成员边界、路线图

## 环境变量

示例模板见：

- [`.env.example`](.env.example)

实际密钥与账号只写入本地 `.env`，不要提交到仓库。

## 文档入口

- [详细方案](Spatio-Eco_详细方案.md)
- [成员 AA 模型训练数据补充清单](docs/02_成员AA模型训练数据补充清单.md)
- [南京季度版训练接入方案](docs/03_南京季度版训练接入方案.md)
- [平台框架与服务边界](docs/12_平台框架与服务边界_2026-03-21.md)
- [平台联调与启动说明](docs/13_平台联调与启动说明_2026-03-21.md)
- [SAM-2 远程执行与本地边界](docs/14_SAM2远程执行与本地边界_2026-03-21.md)

## Public 仓库说明

当前仓库已按公开发布方向整理：

- `.env` 不纳入版本控制
- 原始数据、日志、缓存、远程实验目录已默认忽略
- 为了让 public 仓库可直接演示，已保留小体量的处理后特征与模型输出
- 根 README 和 `.env.example` 已补齐

但仍建议在真正推送前完成：

1. 选择并补一个开源许可证
2. 初始化 git 并检查 `git status --ignored`
3. 确认不上传本地账号、缓存、数据和临时日志

公开发布检查清单见：

- [Public 仓库发布清单](docs/15_Public仓库发布清单_2026-03-22.md)
