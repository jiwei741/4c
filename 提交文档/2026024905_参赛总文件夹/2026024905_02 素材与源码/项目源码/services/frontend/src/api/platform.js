import { buildApiUrl } from './config.js'

function buildQuery(params = {}) {
  const search = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      search.set(key, value)
    }
  })

  const query = search.toString()
  return query ? `?${query}` : ''
}

async function fetchJson(path, params) {
  const response = await fetch(`${buildApiUrl(path)}${buildQuery(params)}`)

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || `Request failed: ${response.status}`)
  }

  return response.json()
}

async function postJson(path, payload = {}) {
  const response = await fetch(buildApiUrl(path), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || `Request failed: ${response.status}`)
  }

  return response.json()
}

export function getDashboard() {
  return fetchJson('/api/v1/dashboard')
}

export function getModels() {
  return fetchJson('/api/v1/models')
}

export function getEvidenceSummary() {
  return fetchJson('/api/v1/evidence/summary')
}

export function getPredictionLayer(params = {}) {
  return fetchJson('/api/v1/map/predictions', params)
}

export function getPredictionAnalytics(params = {}) {
  return fetchJson('/api/v1/map/analytics', params)
}

export function getLatestPrediction(params = {}) {
  return fetchJson('/api/v1/predictions/latest', params)
}

export function getScenarioExamples() {
  return fetchJson('/api/v1/scenarios/examples')
}

export function getScenarioExample(scenarioKey) {
  return fetchJson(`/api/v1/scenarios/examples/${scenarioKey}`)
}

export function getGridNodes() {
  return fetchJson('/api/v1/study-area/grid-nodes')
}

export function askFaqAssistant(message, history = []) {
  return postJson('/api/v1/assistant/faq', { message, history })
}
