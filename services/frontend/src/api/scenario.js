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
  const nodeMap = await getGridNodeMap()
  const selectedNodeIds = []

  for (const [nodeId, node] of nodeMap.entries()) {
    const latitude = toNumber(node.latitude)
    const longitude = toNumber(node.longitude)
    const withinLatitude = latitude >= toNumber(bounds.south) && latitude <= toNumber(bounds.north)
    const withinLongitude = longitude >= toNumber(bounds.west) && longitude <= toNumber(bounds.east)

    if (withinLatitude && withinLongitude) {
      selectedNodeIds.push(nodeId)
    }
  }

  return selectedNodeIds
}

export async function runScenarioRequest(payload, emissionMultiplier) {
  const response = await fetch(buildApiUrl('/api/v1/scenarios/run'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || `Scenario request failed: ${response.status}`)
  }

  const data = await response.json()
  const nodeMap = await getGridNodeMap()
  return buildScenarioResult(data, nodeMap, emissionMultiplier)
}
