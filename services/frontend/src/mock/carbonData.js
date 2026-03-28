// 存储不同日期的数据缓存，避免每次随机变化
const dataCache = new Map()

// 生成南京地区的模拟碳通量网格数据
// date 参数支持格式：'2020-Q1'、'2021-06-01' 等
export function generateMockCarbonData(date = '2020-Q2') {
  // 如果已缓存该日期的数据，直接返回
  if (dataCache.has(date)) {
    return { date, grid: dataCache.get(date) }
  }

  const grid = []
  const latStart = 31.7
  const lonStart = 118.6
  const step = 0.02
  const rows = 25
  const cols = 25

  // 从日期中提取年份
  const year = parseInt(date.substring(0, 4))
  const yearOffset = (year - 2020) * 0.5  // 每年增加 0.5 的 GPP（模拟生态改善）

  // 根据季度或月份计算季节因子
  let seasonFactor = 0
  if (date.includes('-Q')) {
    // 季度格式：2020-Q1, Q2, Q3, Q4
    const quarter = date.split('-Q')[1]
    if (quarter === '1') seasonFactor = -1.5  // 冬季低
    else if (quarter === '2') seasonFactor = 0.5  // 春季
    else if (quarter === '3') seasonFactor = 1.5  // 夏季高
    else if (quarter === '4') seasonFactor = -0.5  // 秋季
  } else {
    // 日期格式：2020-06-01
    const month = parseInt(date.substring(5, 7))
    seasonFactor = Math.sin((month - 3) * Math.PI / 6) * 1.5
  }

  for (let i = 0; i < rows; i++) {
    for (let j = 0; j < cols; j++) {
      const lat = latStart + i * step
      const lon = lonStart + j * step

      // 模拟GPP分布（符合南京地理特点）
      let baseGPP = 3 + yearOffset + seasonFactor  // 加上年份和季节影响

      // 紫金山森林区（高GPP，且逐年增加）
      if (i > 15 && j > 15 && i < 23 && j < 23) {
        baseGPP = 7 + yearOffset + seasonFactor + Math.random() * 1
      }
      // 主城区（低GPP，变化较小）
      else if (i >= 8 && i <= 18 && j >= 8 && j <= 18) {
        baseGPP = 1 + seasonFactor * 0.3 + Math.random() * 0.5
      }
      // 长江和玄武湖（极低GPP，基本不变）
      else if (i < 8 || (i > 18 && j > 18)) {
        baseGPP = 0.5 + Math.random() * 0.3
      }
      // 其他郊区（中等GPP）
      else {
        baseGPP = 4 + yearOffset * 0.8 + seasonFactor + Math.random() * 1.5
      }

      const gpp = Math.max(0, baseGPP)
      grid.push({ lat, lon, gpp: Math.round(gpp * 100) / 100 })
    }
  }

  // 缓存数据
  dataCache.set(date, grid)

  return { date, grid }
}
