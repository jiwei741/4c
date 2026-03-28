import { API_BASE_URL } from './config.js'

// 后端 API 基础地址（开发时指向成员D的Mock服务）
const BASE_URL = API_BASE_URL

// 获取指定日期的碳通量网格数据
export async function getCarbonData(date) {
  const res = await fetch(`${BASE_URL}/api/carbon/${date}`)
  return res.json()
}

// 获取指定日期的地物分类数据
export async function getLandcoverData(date) {
  const res = await fetch(`${BASE_URL}/api/landcover/${date}`)
  return res.json()
}

// 提交预测请求
export async function predict(params) {
  const res = await fetch(`${BASE_URL}/api/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
  return res.json()
}

// 提交情景推演请求
export async function runScenario(params) {
  const res = await fetch(`${BASE_URL}/api/v1/scenarios/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
  return res.json()
}

// 获取指定坐标的时序数据
export async function getTimeseries(lat, lon) {
  const res = await fetch(`${BASE_URL}/api/timeseries/${lat}/${lon}`)
  return res.json()
}
