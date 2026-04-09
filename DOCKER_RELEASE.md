# Docker 镜像发布版说明

## 1. 这套方案解决什么问题

这套方案用于把平台做成“使用方不需要下载源码”的交付方式。

完成后：

- 我们负责构建并发布 Docker 镜像到 Docker Hub
- 使用方只需要：
  - `docker-compose.release.yml`
  - `.env.release`
  - Docker Desktop

他们不需要：

- 下载完整源码仓库
- 安装 Python
- 安装 Node.js
- 安装 `uv`
- 安装 `npm`

## 2. 当前交付结构

镜像发布版包含两部分：

### 我们内部使用

- [scripts/docker/build_release_images.ps1](D:/4c/scripts/docker/build_release_images.ps1)
- [scripts/docker/push_release_images.ps1](D:/4c/scripts/docker/push_release_images.ps1)
- [scripts/docker/write_release_env.ps1](D:/4c/scripts/docker/write_release_env.ps1)

### 使用方使用

- [docker-compose.release.yml](D:/4c/docker-compose.release.yml)
- [`.env.release.example`](D:/4c/.env.release.example)

## 3. 先在 Docker Hub 创建镜像仓库

建议直接创建两个仓库：

- `spatio-eco-backend`
- `spatio-eco-frontend`

创建完成后，最终镜像名会像这样：

- `your-dockerhub-username/spatio-eco-backend:v1.0.0`
- `your-dockerhub-username/spatio-eco-frontend:v1.0.0`

## 4. 我们怎么发布镜像

### 第一步：登录 Docker Hub

```powershell
docker login
```

### 第二步：构建发布镜像

在仓库根目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/docker/build_release_images.ps1 -RegistryNamespace your-dockerhub-username -Tag v1.0.0
```

这会构建两个镜像：

- `your-dockerhub-username/spatio-eco-backend:v1.0.0`
- `your-dockerhub-username/spatio-eco-frontend:v1.0.0`

### 第三步：推送镜像

```powershell
powershell -ExecutionPolicy Bypass -File scripts/docker/push_release_images.ps1 -RegistryNamespace your-dockerhub-username -Tag v1.0.0
```

## 5. 怎么给使用方交付

给使用方一个精简目录即可，例如：

```text
spatio-eco-release/
  docker-compose.release.yml
  .env.release
  README.txt
```

其中：

- `docker-compose.release.yml` 直接来自仓库根目录
- `.env.release` 可以基于 [`.env.release.example`](D:/4c/.env.release.example) 生成

## 6. `.env.release` 应该怎么生成

### 方式一：手动写

```env
COMPOSE_PROJECT_NAME=spatio-eco
PLATFORM_PORT=8080
BACKEND_INTERNAL_PORT=8000
BACKEND_IMAGE=your-dockerhub-username/spatio-eco-backend:v1.0.0
FRONTEND_IMAGE=your-dockerhub-username/spatio-eco-frontend:v1.0.0
```

### 方式二：用脚本生成

```powershell
powershell -ExecutionPolicy Bypass -File scripts/docker/write_release_env.ps1 -RegistryNamespace your-dockerhub-username -Tag v1.0.0 -OutputPath .env.release
```

## 7. 使用方如何启动

使用方进入交付目录后执行：

```powershell
docker compose -f docker-compose.release.yml --env-file .env.release pull
docker compose -f docker-compose.release.yml --env-file .env.release up -d
```

启动完成后，访问：

```text
http://localhost:8080
```

## 8. 使用方如何停止

```powershell
docker compose -f docker-compose.release.yml --env-file .env.release down
```

## 9. 使用方如何查看日志

```powershell
docker compose -f docker-compose.release.yml --env-file .env.release logs -f
```

## 10. 版本升级方式

如果后续发布新版本，例如 `v1.0.1`：

1. 我们重新构建并推送新镜像
2. 使用方只需要把 `.env.release` 里的镜像 tag 改成新版本
3. 然后执行：

```powershell
docker compose -f docker-compose.release.yml --env-file .env.release pull
docker compose -f docker-compose.release.yml --env-file .env.release up -d
```

## 11. 当前方案的优点

- 使用方不需要源码
- 使用方不需要开发环境
- 更新版本时只需要拉新镜像
- 平台仍然保持单入口：`http://localhost:8080`

## 12. 当前方案的注意点

- 使用方第一次部署需要联网拉取镜像
- 我们需要维护 Docker Hub 中的镜像版本
- 如果镜像仓库是私有的，使用方需要先执行 `docker login`
