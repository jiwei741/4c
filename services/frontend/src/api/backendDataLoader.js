/**
 * 后端API数据加载器
 * 从后端同学的接口获取真实数据
 */

import { getCarbonData } from './index.js'

// 缓存已加载的数据
const dataCache = new Map()

/**
 * 获取指定日期的碳通量网格数据
 * @param {string} date - 日期格式: '2023-06-01' 或 '2023-Q2'
 * @returns {Object} { date, grid: [{ lat, lon, gpp, ... }] }
 */
export async function getBackendCarbonData(date) {
  // 如果已缓存该日期的数据，直接返回
  if (dataCache.has(date)) {
    return { date, grid: dataCache.get(date) }
  }

  try {
    const data = await getCarbonData(date)

    // 转换数据格式以适配前端热力图
    const grid = (data.grid || []).map(point => ({
      lat: point.lat,
      lon: point.lon,
      gpp: point.gpp || point.ndvi * 10 || 0,
      // 额外的特征数据，可用于详情面板显示
      ndvi: point.ndvi,
      carbonFlux: point.carbon_flux,
      vegetationRatio: point.vegetation_ratio || point.vegetationRatio,
      waterRatio: point.water_ratio || point.waterRatio,
      builtRatio: point.built_ratio || point.builtRatio
    }))

    // 缓存数据
    dataCache.set(date, grid)

    console.log(`从后端加载数据: ${date}, 网格数: ${grid.length}`)

    return { date, grid }
  } catch (error) {
    console.error('从后端加载数据失败:', error)
    throw error
  }
}

/**
 * 清除指定日期的缓存
 */
export function clearCache(date) {
  if (date) {
    dataCache.delete(date)
  } else {
    dataCache.clear()
  }
}

/**
 * 获取缓存的日期列表
 */
export function getCachedDates() {
  return Array.from(dataCache.keys())
}
