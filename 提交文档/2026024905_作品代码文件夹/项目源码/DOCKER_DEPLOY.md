# Docker 一键部署说明

## 1. 适用场景

这套方案适合两类交付方式：

- 我们自己在本机或服务器上快速启动平台
- 把项目交给使用方，由对方用 `Docker Desktop` 本地启动

使用方启动后，直接访问：

```text
http://localhost:8080
```

即可打开平台页面。

## 2. 当前方案是否需要下载源码

结论分两种情况：

- **按当前仓库这套方式部署：需要**
- **但不一定需要“开发源码使用方式”那样去安装开发环境**

原因是当前的 `docker-compose.yml` 使用的是本地构建方式：

- 前端镜像从仓库内的 [services/frontend/Dockerfile](D:/4c/services/frontend/Dockerfile) 构建
- 后端镜像从仓库内的 [infra/docker/backend-runtime.Dockerfile](D:/4c/infra/docker/backend-runtime.Dockerfile) 构建
- 构建时还会打包仓库中的模型产物、处理后数据和运行文件

所以，**使用方至少需要拿到完整的项目部署目录**，也就是：

- 整个仓库
- 或者我们后面单独整理好的“部署包”

但是他们**不需要**另外安装：

- Python
- Node.js
- `uv`
- `npm`

他们只需要安装 `Docker Desktop` 即可。

## 3. 环境要求

- 已安装 `Docker Desktop`
- 建议机器内存不少于 `8 GB`
- 建议磁盘保留一定空间，用于镜像、模型和数据文件

## 4. 启动方式

在项目根目录执行：

```powershell
docker compose --env-file .env.docker up -d --build
```

首次启动会比较慢，因为需要构建镜像。

启动完成后，访问：

```text
http://localhost:8080
```

## 5. 停止方式

```powershell
docker compose --env-file .env.docker down
```

## 6. 查看日志

```powershell
docker compose --env-file .env.docker logs -f
```

## 7. 端口说明

- 平台统一入口：`http://localhost:8080`
- 容器内部后端端口：`8000`

如果需要修改外部访问端口，可编辑 [`.env.docker`](D:/4c/.env.docker) 中的：

```env
PLATFORM_PORT=8080
```

例如改成：

```env
PLATFORM_PORT=9000
```

则访问地址变为：

```text
http://localhost:9000
```

## 8. 当前部署结构

- 前端静态页面由 `Caddy` 提供
- `/api/*` 请求自动反向代理到后端容器
- 后端容器内包含平台运行所需的模型产物和处理后数据
- 情景推演继续使用容器内打包好的本地模型产物执行

## 9. 对使用方最重要的一句话

**当前方案下，使用方不需要安装开发环境，但需要拿到我们的完整部署目录或部署包，不能只拿一个网址或一个单独的 compose 文件。**

## 10. 如果以后想做到“使用方不需要下载源码”

后续可以升级为下面这种交付方式：

- 我们预先构建并发布 Docker 镜像
- 使用方只拿：
  - `docker-compose.yml`
  - `.env`
  - 少量说明文档

那样他们就不需要下载完整仓库了。

不过当前这一步先保留本地构建方式，优点是：

- 最容易维护
- 最方便继续改代码和重新构建
- 不需要先搭镜像仓库发布流程
