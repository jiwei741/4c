# Sentinel-2 原始产品下载前置条件

现在开始下载 `Sentinel-2 SAFE` 原始产品前，你需要补一组 `CDSE S3` 凭证。

## 为什么现在需要它

目前项目已经能：

- 检索 `Sentinel-2 L2A` 产品清单
- 生成南京市的首轮下载计划

但真正下载 `SAFE` 产品目录，需要走官方 `S3 Access`，不能只靠当前的目录检索结果。

## 你要提供给我的内容

填进本地 `.env`：

```env
CDSE_S3_ENDPOINT_URL=https://eodata.dataspace.copernicus.eu
CDSE_S3_REGION=default
CDSE_S3_ACCESS_KEY=
CDSE_S3_SECRET_KEY=
```

## 推荐做法 1：网页生成

官方 S3 文档说明，访问以下页面并用 `Copernicus Data Space Ecosystem` 账号登录，生成 `access key` 和 `secret key`：

- 官方文档：<https://documentation.dataspace.copernicus.eu/APIs/S3.html>
- 凭证页面：<https://eodata-s3keysmanager.dataspace.copernicus.eu/>

生成后，把两项填进 `.env`：

- `CDSE_S3_ACCESS_KEY`
- `CDSE_S3_SECRET_KEY`

## 推荐做法 2：脚本生成

如果当前网络能打通 `s3-keys-manager.cloudferro.com`，可以直接运行：

```powershell
python scripts\create_cdse_s3_credentials.py
```

成功时会打印：

- `access_id=...`
- `secret=...`

然后把它们写进 `.env`。

## 后续怎么用

生成凭证后，可以直接按下载计划抓首轮产品，例如：

```powershell
python scripts\sentinel2_download.py --plan-json data\raw\sentinel2\nanjing\catalog\sentinel2_download_plan_nanjing_2025-01-01_to_2025-01-31.json --priority 1
```

或者直接下载某个 `s3://...` 路径：

```powershell
python scripts\sentinel2_download.py --s3-uri "s3://EODATA/Sentinel-2/MSI/L2A/2025/01/30/S2C_MSIL2A_20250130T025011_N0511_R132_T50SPA_20250130T060315.SAFE"
```
