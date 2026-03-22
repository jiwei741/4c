# 外部账号与 API 申请清单

这份清单只列“必须你亲自完成”的部分。我会默认你完成后，把凭证接入代码和下载脚本。

## 0. 先做的事

先准备一个固定邮箱，统一注册以下服务。建议单独建一个比赛邮箱，避免后续多人协作时凭证散落。

建议你完成后，把以下信息汇总到一个本地安全文档里，不要发到群里：

- 账号邮箱
- 登录用户名
- 密码
- API Key / Personal Access Token
- 是否已经接受数据许可协议

## 0.5 你还需要确定研究区

原方案必须先定研究区，否则我没法写下载脚本和数据库初始化。

你要做的步骤：

1. 在老师或团队内部先定一个首版研究区。
2. 建议直接选一个城市级区域，不要选整省。
3. 如果你没有明确偏好，优先考虑：
   - `湖州市`
   - `雅安市`
   - `绍兴市`
4. 确认后把研究区名称发我。

你最终需要给我的内容：

- `PROJECT_AREA_NAME`
- 如果你已经知道边界框，也一并给我：`PROJECT_AREA_BBOX`

## 1. Copernicus Data Space Ecosystem

用途：

- 下载 `Sentinel-2 L2A`
- 用 OData / STAC / 下载接口做程序化检索与拉取

官方入口：

- 官网：<https://dataspace.copernicus.eu/>
- 注册与认证文档：<https://documentation.dataspace.copernicus.eu/Registration.html>
- OData 文档：<https://documentation.dataspace.copernicus.eu/APIs/OData.html>
- Token 文档：<https://documentation.dataspace.copernicus.eu/APIs/Token.html>

你要做的步骤：

1. 打开官网，点击右上角头像或 `REGISTER`。
2. 填完整必填信息并提交。
3. 去邮箱点击验证链接，完成邮箱验证。
4. 用注册邮箱和密码重新登录一次，确认账号可用。

注意：

- 原方案文档里写的是 `Copernicus Open Access Hub`，现在官方主通道已经是 `Copernicus Data Space Ecosystem`，后续我会按新接口开发。
- 这里不需要额外“申请 API 审批”；注册账号后即可通过用户名密码换取访问 token。

你最终需要给我的内容：

- `COPERNICUS_USERNAME`
- `COPERNICUS_PASSWORD`

## 2. Copernicus Climate Data Store (ERA5)

用途：

- 下载 `ERA5` 气象数据
- 提取 `10m u/v wind`, `2m temperature`, `total precipitation` 等变量

官方入口：

- 主页：<https://cds.climate.copernicus.eu/>
- API 使用文档：<https://cds.climate.copernicus.eu/how-to-api>
- 个人资料/API Key：<https://cds.climate.copernicus.eu/profile>
- ERA5 单层数据集：<https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=download>

你要做的步骤：

1. 打开 CDS 首页并注册账号。
2. 登录后进入 `Profile` 页面。
3. 补齐个人资料中的必填字段。
4. 在 `API key` 区域复制你的 `Personal Access Token`。
5. 打开 `ERA5 hourly data on single levels` 数据集页面。
6. 在下载页底部手动同意该数据集的 `Terms of Use`。

注意：

- 官方文档明确要求：每个数据集第一次下载前，必须在数据集页面手动接受许可协议。
- 后续我会把这个 token 写入 `.env` 或 `.cdsapirc`，并接下载脚本。

你最终需要给我的内容：

- `CDSAPI_KEY`
- 确认你已经接受过 `reanalysis-era5-single-levels` 的使用协议

## 3. 天地图 Key

用途：

- 作为项目前端合规底图
- 替代不合规或比赛风险较高的国外默认底图

官方入口：

- 首页：<https://lbs.tianditu.gov.cn/home.html>
- 开发许可说明：<https://lbs.tianditu.gov.cn/authorization/authorization.html>
- 地图服务说明：<https://lbs.tianditu.gov.cn/server/MapService.html>

你要做的步骤：

1. 打开天地图 API 网站。
2. 注册普通用户。
3. 申请成为开发者。
4. 进入控制台，创建一个新应用。
5. 应用类型建议填 `Web` 或 `浏览器端地图应用`。
6. 拿到 `Key` 后保存。

注意：

- 前端接入天地图时，接口调用需要带 `tk=你的密钥`。
- 后续答辩界面要保留审图号和底图来源标注。

你最终需要给我的内容：

- `TIANDITU_KEY`

## 4. EDGAR

用途：

- 获取全球 / 国家 / 栅格温室气体排放数据

官方入口：

- 首页：<https://edgar.jrc.ec.europa.eu/>
- GHG v8.0 数据集：<https://edgar.jrc.ec.europa.eu/dataset_ghg80>

你要做的步骤：

1. 打开 `dataset_ghg80` 页面。
2. 确认可下载的格式和目标年份覆盖范围。
3. 不需要单独申请 API Key。

说明：

- 这部分通常不需要额外注册。
- 我会优先从公开下载链接和网页导出的方式接入。

## 5. NOAA GML

用途：

- 获取 CO2 观测数据，用于时序对标和模型校验

官方入口：

- CCGG 首页：<https://gml.noaa.gov/ccgg/>
- CO2 趋势与数据：<https://gml.noaa.gov/ccgg/trends/>
- 全球平均 CO2 数据下载页：<https://gml.noaa.gov/ccgg/trends/gl_data.html>

你要做的步骤：

1. 这部分通常不需要注册。
2. 不需要单独申请 API Key。

说明：

- 我会直接接 CSV / 文本下载。

## 6. ESA CCI Land Cover

用途：

- 作为地表覆被基准数据
- 为 SAM-2 分割结果补语义类别

官方入口：

- 官网：<https://www.esa-landcover-cci.org/>
- 下载页：<https://www.esa-landcover-cci.org/?q=node/190>
- 联系方式：<https://www.esa-landcover-cci.org/?q=contact+points>

你要做的步骤：

1. 先打开下载页确认是否能直接下载。
2. 如果下载页要求登录，但没有明确注册入口，先不要卡在这里。
3. 记录是否遇到登录门槛。

说明：

- 官方下载页当前能看到 `User login`，但公开页面没有明确的自助注册说明。
- 如果它阻塞，我们会先用可获得的公开土地覆被产品完成开发，再补回 ESA CCI。
- 这一步优先级低于 `Copernicus Data Space`、`CDS`、`天地图`。

## 7. 可选：Cesium ion

用途：

- 仅当我们后面需要官方全球地形、3D Tiles 托管或部分在线资源时使用

官方入口：

- <https://cesium.com/ion/>

说明：

- 不是原方案的硬前置。
- 如果只接天地图底图并使用本地数据层，可以先不申请。

## 你完成后请回复我这几项状态

按下面格式直接回我就行：

```text
1. Copernicus Data Space：已完成 / 未完成
2. CDS ERA5：已完成 / 未完成
3. 天地图 Key：已完成 / 未完成
4. EDGAR：已确认下载入口 / 未确认
5. ESA CCI：可直接下载 / 需要登录 / 还没看
```

如果你愿意，也可以只回复：

```text
已完成 1、2、3；4 已确认；5 需要登录
```
