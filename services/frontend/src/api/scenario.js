import { buildApiUrl } from './config.js'

let gridNodeMapPromise = null

function getForecastHorizon(payload) {
  if (payload?.summary?.forecast_horizon) {
    return payload.summary.forecast_horizon
  }

  if (Array.isArray(payload?.result?.forecast_timestamps) && payload.result.forecast_timestamps.length > 0) {
    return payload.result.forecast_timestamps[0]
  }

  const firstDeltaKey = Object.keys(payload?.result?.delta_by_horizon || {})[0]
  return firstDeltaKey || 'latest'
}

function toNumber(value) {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : 0
}

async function getGridNodeMap() {
  if (!gridNodeMapPromise) {
    gridNodeMapPromise = fetch(buildApiUrl('/api/v1/study-area/grid-nodes'))
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`Failed to load grid nodes: ${response.status}`)
        }

        const payload = await response.json()
        const items = Array.isArray(payload.items) ? payload.items : []
        return new Map(items.map((item) => [String(item.node_id), item]))
      })
  }

  return gridNodeMapPromise
}

function buildGrid(nodeMap, valueMap) {
  return Object.entries(valueMap || {})
    .map(([nodeId, value]) => {
      const node = nodeMap.get(String(nodeId))
      if (!node) {
        return null
      }

      return {
        nodeId: String(nodeId),
        lat: toNumber(node.latitude),
        lon: toNumber(node.longitude),
        minLat: toNumber(node.min_lat),
        maxLat: toNumber(node.max_lat),
        minLon: toNumber(node.min_lon),
        maxLon: toNumber(node.max_lon),
        gpp: toNumber(value),
      }
    })
    .filter(Boolean)
}

function buildScenarioResult(payload, nodeMap, emissionMultiplier) {
  const horizon = getForecastHorizon(payload)
  const baselineMap = payload?.result?.baseline_by_horizon?.[horizon] || payload?.result?.baseline || {}
  const scenarioMap = payload?.result?.scenario_by_horizon?.[horizon] || payload?.result?.scenario || {}

  const originalGrid = buildGrid(nodeMap, baselineMap)
  const scenarioGrid = buildGrid(nodeMap, scenarioMap)

  const originalAverage = originalGrid.length
    ? originalGrid.reduce((sum, item) => sum + item.gpp, 0) / originalGrid.length
    : 0
  const scenarioAverage = scenarioGrid.length
    ? scenarioGrid.reduce((sum, item) => sum + item.gpp, 0) / scenarioGrid.length
    : 0
  const gppChange = scenarioAverage - originalAverage
  const carbonImpact = originalAverage === 0 ? 0 : (gppChange / Math.abs(originalAverage)) * 100

  return {
    originalData: {
      date: horizon,
      grid: originalGrid,
    },
    scenarioData: {
      date: horizon,
      grid: scenarioGrid,
    },
    gppChange,
    carbonImpact,
    emissionMultiplier,
    forecastHorizon: horizon,
    backendSummary: payload?.summary || null,
  }
}

export async function getScenarioNodeIds(bounds) {
  console.log('[scenario.js] Getting node IDs for bounds:', bounds)
  const nodeMap = await getGridNodeMap()
  console.log('[scenario.js] Total nodes in map:', nodeMap.size)

  const selectedNodeIds = []

  for (const [nodeId, node] of nodeMap.entries()) {
    // 使用节点的边界范围来匹配，而不是中心点
    const nodeMinLon = toNumber(node.min_lon)
    const nodeMaxLon = toNumber(node.max_lon)
    const nodeMinLat = toNumber(node.min_lat)
    const nodeMaxLat = toNumber(node.max_lat)

    const boundsWest = toNumber(bounds.west)
    const boundsEast = toNumber(bounds.east)
    const boundsSouth = toNumber(bounds.south)
    const boundsNorth = toNumber(bounds.north)

    // 检查节点边界是否与框选区域有重叠
    const overlapLon = !(nodeMaxLon < boundsWest || nodeMinLon > boundsEast)
    const overlapLat = !(nodeMaxLat < boundsSouth || nodeMinLat > boundsNorth)

    if (overlapLon && overlapLat) {
      selectedNodeIds.push(nodeId)
    }
  }

  console.log('[scenario.js] Selected node IDs:', selectedNodeIds)
  return selectedNodeIds
}

export async function runScenarioRequest(payload, emissionMultiplier) {
  console.log('[scenario.js] Sending scenario request to:', buildApiUrl('/api/v1/scenarios/run'))
  console.log('[scenario.js] Request payload:', payload)

  const response = await fetch(buildApiUrl('/api/v1/scenarios/run'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  console.log('[scenario.js] Response status:', response.status)

  if (!response.ok) {
    const message = await response.text()
    console.error('[scenario.js] Request failed:', message)
    throw new Error(message || `Scenario request failed: ${response.status}`)
  }

  const data = await response.json()
  console.log('[scenario.js] Response data keys:', Object.keys(data))
  console.log('[scenario.js] Response data sample:', data)

  const nodeMap = await getGridNodeMap()
  const result = buildScenarioResult(data, nodeMap, emissionMultiplier)
  console.log('[scenario.js] Built result:', result)
  return result
}
