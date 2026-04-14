# Spatio-Eco 平台部署说明

## 1. 运行基础

- 已安装 `Docker Desktop`
- 可联网，用于拉取 Docker 镜像

不需要安装：

- Python
- Node.js
- `uv`
- `npm`

## 2. 文件说明

这个目录已经包含使用方部署所需的最小文件：

- `docker-compose.yml`
- `.env`
- `start.ps1`
- `stop.ps1`
- `start.cmd`
- `stop.cmd`

## 3. 最简单的启动方式

### 方式一：双击启动

直接双击：

- `start.cmd`

启动完成后，在浏览器打开：

```text
http://localhost:8080
```

### 方式二：命令行启动

在当前目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

## 4. 停止方式

### 方式一：双击停止

直接双击：

- `stop.cmd`

### 方式二：命令行停止

```powershell
powershell -ExecutionPolicy Bypass -File .\stop.ps1
```

## 5. 当前访问地址

- 平台地址：`http://localhost:8080`

## 6. 如果端口被占用

可编辑当前目录下的 `.env` 文件：

```env
PLATFORM_PORT=8080
```

例如改成：

```env
PLATFORM_PORT=9000
```

然后重新启动平台，访问：

```text
http://localhost:9000
```

## 7. 如需启用平台问答助手的智能回复

可编辑当前目录下的 `.env` 文件，填写以下任一密钥：

```env
DEEPSEEK_API_KEY=
LLM_CHAT_API_KEY=
LLM_CHAT_MODEL=deepseek-chat
LLM_CHAT_ENDPOINT=https://api.deepseek.com/v1/chat/completions
```

如果不填写，平台问答助手仍可使用，但会以内置引导回答为主。

## 8. 如果第一次启动较慢

这是正常现象。

原因是首次启动时会执行：

- 拉取镜像
- 创建容器
- 启动前后端服务

后续再次启动会更快。

## 9. 常见问题

### 无法打开页面

先确认：

- Docker Desktop 已经启动
- 容器已经成功启动
- 访问地址是否与 `.env` 中端口一致

### 需要重新拉取最新版本

在当前目录执行：

```powershell
docker compose pull
docker compose up -d
```

## 10. 当前部署特点

- 前端和后端已经打包为 Docker 镜像
- 页面、接口和情景推演都通过同一个入口访问
- 使用方不需要源码即可部署
