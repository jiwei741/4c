# Spatio-Eco v1.0.0

## 适用对象

本次 Release 面向平台使用方，而不是二次开发者。

如果你只是想部署并使用平台，请下载下方附件：

- `spatio-eco-release-v1.0.0.zip`

请不要下载 GitHub 自动生成的：

- `Source code (zip)`
- `Source code (tar.gz)`

这两个文件是源码归档，面向开发用途，不是给最终使用方直接部署的平台包。

## 本次发布内容

- 提供可直接交付给使用方的精简部署目录 `spatio-eco-release/`
- 使用方不需要下载源码
- 使用方不需要安装 Python、Node.js、uv、npm
- 只需要 `Docker Desktop` 即可启动平台
- 前端 Cesium 生产构建渲染问题已修复

## Docker 镜像

- `jiwei741/spatio-eco-backend:v1.0.0`
- `jiwei741/spatio-eco-frontend:v1.0.0`

## 使用步骤

1. 下载附件 `spatio-eco-release-v1.0.0.zip`
2. 解压后进入目录
3. 双击 `start.cmd`，或执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

4. 在浏览器打开：

```text
http://localhost:8080
```

## 交付包内容

交付包中包含：

- `docker-compose.yml`
- `.env`
- `README.md`
- `start.cmd`
- `stop.cmd`
- `start.ps1`
- `stop.ps1`

## 备注

GitHub Release 页面中的 `Source code (zip/tar.gz)` 是 GitHub 基于 tag 自动生成的源码压缩包。根据 GitHub 官方文档，Release 页面会自动附带仓库内容的 zip 和 tarball 下载链接。
