/**
 * 真实遥感数据加载器
 * 从遥感同学提供的 CSV 文件加载南京地区碳汇数据
 */

// 缓存已加载的数据
let gridNodesData = null
let featuresTimeSeriesData = null
let dataByTimestamp = null

/**
 * 加载网格节点数据
 */
export async function loadGridNodes() {
  if (gridNodesData) return gridNodesData

  try {
    const response = await fetch('/remote_sensing_output_ver.03.20/grid_nodes.csv')
    const text = await response.text()

    // 解析 CSV
    const lines = text.trim().split('\n')
    const headers = lines[0].split(',')

    gridNodesData = lines.slice(1).map(line => {
      const values = line.split(',')
      const node = {}
      headers.forEach((header, index) => {
        if (header === 'node_id') {
          node[header] = parseInt(values[index])
        } else {
          node[header] = parseFloat(values[index])
        }
      })
      return node
    })

    return gridNodesData
  } catch (error) {
    console.error('加载网格节点数据失败:', error)
    return []
  }
}

/**
 * 加载时序特征数据
 */
export async function loadFeaturesTimeSeries() {
  if (featuresTimeSeriesData) return featuresTimeSeriesData

  try {
    const response = await fetch('/remote_sensing_output_ver.03.20/nanjing_sentinel2_features_quarterly_2020_2024.csv')
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const text = await response.text()

    // 解析 CSV - 处理可能的 Windows 行尾符 \r\n
    const lines = text.trim().split(/[\r\n]+/)
    const headers = lines[0].split(',').map(h => h.trim())

    featuresTimeSeriesData = lines.slice(1).map(line => {
      const values = line.split(',').map(v => v.trim())
      const record = {}
      headers.forEach((header, index) => {
        const value = values[index]
        if (header === 'timestamp') {
          record[header] = value // 保持字符串类型
        } else if (header === 'node_id') {
          record[header] = parseInt(value)
        } else {
          record[header] = parseFloat(value)
        }
      })
      return record
    })

    console.log(`加载了 ${featuresTimeSeriesData.length} 条时序记录`)

    // 按时间戳分组数据
    dataByTimestamp = {}
    featuresTimeSeriesData.forEach(record => {
      if (!dataByTimestamp[record.timestamp]) {
        dataByTimestamp[record.timestamp] = []
      }
      dataByTimestamp[record.timestamp].push(record)
    })

    console.log('可用时间戳:', Object.keys(dataByTimestamp).sort())

    return featuresTimeSeriesData
  } catch (error) {
    console.error('加载时序特征数据失败:', error)
    return []
  }
}

/**
 * 获取指定时间的碳通量网格数据
 * @param {string} timestamp - 时间戳格式: '2020-Q1', '2021-Q2', 等
 * @returns {Object} { date, grid: [{ lat, lon, gpp, ... }] }
 */
export async function getRealCarbonData(timestamp = '2020-Q2') {
  // 如果数据还没加载，先加载
  if (!dataByTimestamp) {
    await loadFeaturesTimeSeries()
  }

  // 获取网格节点位置信息
  const nodes = await loadGridNodes()

  // 获取指定时间的数据
  const timeData = dataByTimestamp[timestamp] || []

  // 合并位置和特征数据
  const grid = timeData.map(record => {
    const node = nodes.find(n => n.node_id === record.node_id)
    if (!node) return null

    // 使用 ndvi_mean 作为 GPP 的代理（碳汇指标）
    // ndvi 范围通常在 -1 到 1 之间，植被越高值越大
    // 这里将其转换为更直观的碳汇单位
    const gpp = Math.max(0, record.ndvi_mean * 10) // 简单转换，可根据实际情况调整

    return {
      lat: node.latitude,
      lon: node.longitude,
      gpp: parseFloat(gpp.toFixed(2)),
      nodeId: record.node_id,
      // 额外的特征数据，可用于详情面板显示
      ndvi: parseFloat(record.ndvi_mean.toFixed(3)),
      vegetationRatio: parseFloat((record.vegetation_area_ratio * 100).toFixed(1)),
      waterRatio: parseFloat((record.water_ratio * 100).toFixed(1)),
      builtRatio: parseFloat((record.built_ratio * 100).toFixed(1))
    }
  }).filter(item => item !== null)

  return { date: timestamp, grid }
}

/**
 * 获取所有可用的时间戳列表
 */
export async function getAvailableTimestamps() {
  if (!dataByTimestamp) {
    await loadFeaturesTimeSeries()
  }
  return Object.keys(dataByTimestamp).sort()
}

/**
 * 获取指定网格的时序数据
 */
export async function getNodeTimeSeries(nodeId) {
  if (!featuresTimeSeriesData) {
    await loadFeaturesTimeSeries()
  }

  const nodeData = featuresTimeSeriesData
    .filter(record => record.node_id === nodeId)
    .sort((a, b) => a.timestamp.localeCompare(b.timestamp))

  return nodeData.map(record => ({
    timestamp: record.timestamp,
    ndvi: record.ndvi_mean,
    gpp: record.ndvi_mean * 10
  }))
}

/**
 * 初始化数据加载（在应用启动时调用）
 */
export async function initRealData() {
  await Promise.all([
    loadGridNodes(),
    loadFeaturesTimeSeries()
  ])
  console.log('真实遥感数据加载完成')
  console.log('可用时间戳:', await getAvailableTimestamps())
}
