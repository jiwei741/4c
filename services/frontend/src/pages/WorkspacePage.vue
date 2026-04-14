<template>
  <div class="workspace-page" :style="{ '--workspace-header-offset': `${headerOffset}px` }">
    <Header
      :current-date="selectedHorizon"
      :study-area="studyAreaName"
      :default-model="defaultModelName"
      :forecast-window="forecastWindow"
      @open-scenario="openScenario"
    />

    <main class="workspace-layout">
      <section class="workspace-stage" id="overview">
        <CesiumViewer :horizon="selectedHorizon" :scenario-result="scenarioResult" />
        <LegendPanel />
        <ControlPanel @reset-view="handleResetView" @toggle-layer="handleToggleLayer" />
        <WorkspaceInsights
          :analytics="analytics"
          :dashboard="dashboard"
          :selected-horizon="selectedHorizon"
          :selected-horizon-type="selectedHorizonType"
          :scenario-result="scenarioResult"
        />
        <TimelineSlider
          id="signals"
          v-model="selectedHorizon"
          :options="timelineOptions"
          :historical-options="historicalTimelineOptions"
          :forecast-options="forecastTimelineOptions"
          :horizon-type="selectedHorizonType"
          label="历史与预测季度"
        />
        <DetailPanel />
        <ScenarioPanel ref="scenarioPanel" />
        <ComparisonView ref="comparisonView" />
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import Header from '../components/Header.vue'
import CesiumViewer from '../components/CesiumViewer.vue'
import TimelineSlider from '../components/TimelineSlider.vue'
import DetailPanel from '../components/DetailPanel.vue'
import LegendPanel from '../components/LegendPanel.vue'
import ControlPanel from '../components/ControlPanel.vue'
import ScenarioPanel from '../components/ScenarioPanel.vue'
import ComparisonView from '../components/ComparisonView.vue'
import WorkspaceInsights from '../components/WorkspaceInsights.vue'
import { getDashboard, getPredictionAnalytics } from '../api/platform.js'

const dashboard = ref(null)
const analytics = ref(null)
const selectedHorizon = ref('2025-Q1')
const scenarioResult = ref(null)
const scenarioPanel = ref(null)
const comparisonView = ref(null)
const headerOffset = ref(220)
const route = useRoute()
const router = useRouter()

let headerResizeObserver = null

const timelineOptions = computed(() => dashboard.value?.prediction_preview?.timeline_timestamps || ['2020-Q1', '2025-Q1', '2025-Q2'])
const historicalTimelineOptions = computed(() => dashboard.value?.prediction_preview?.historical_timestamps || ['2020-Q1'])
const forecastTimelineOptions = computed(() => dashboard.value?.prediction_preview?.forecast_timestamps || ['2025-Q1', '2025-Q2'])
const forecastWindow = computed(() => {
  const window = dashboard.value?.prediction_preview?.prediction_window
  if (!window) return '2024-Q1 至 2024-Q4'
  return `${window.from || '起点'} 至 ${window.to || '终点'}`
})
const studyAreaName = computed(() => dashboard.value?.project?.study_area?.name || '南京研究区')
const defaultModelName = computed(() => dashboard.value?.prediction_preview?.model_name || 'ST-GNN Multi-Step')
const selectedHorizonType = computed(() => analytics.value?.horizon_type || 'forecast')

function handleResetView() {
  window.dispatchEvent(new CustomEvent('reset-view'))
}

function handleToggleLayer() {
  window.dispatchEvent(new CustomEvent('toggle-layer'))
}

function openScenario() {
  scenarioPanel.value?.open()
}

async function handleRouteIntent() {
  if (route.query.intent !== 'scenario') return
  await nextTick()
  openScenario()
  const nextQuery = { ...route.query }
  delete nextQuery.intent
  router.replace({ path: route.path, query: nextQuery })
}

function updateHeaderOffset() {
  const headerElement = document.querySelector('.workspace-header')
  if (!headerElement) return

  headerOffset.value = Math.ceil(headerElement.getBoundingClientRect().height) + 10
}

async function loadAnalytics() {
  try {
    analytics.value = await getPredictionAnalytics({ horizon: selectedHorizon.value })
  } catch (error) {
    console.error('Failed to load workspace analytics:', error)
  }
}

watch(selectedHorizon, () => {
  loadAnalytics()
})

watch(
  () => route.query.intent,
  async () => {
    await handleRouteIntent()
  },
)

function handleScenarioResult(event) {
  scenarioResult.value = event.detail
  if (event.detail?.forecastHorizon) {
    selectedHorizon.value = event.detail.forecastHorizon
  }
  comparisonView.value?.open(event.detail)
}

function handleScenarioCleared() {
  scenarioResult.value = null
}

onMounted(async () => {
  window.addEventListener('scenario-result', handleScenarioResult)
  window.addEventListener('scenario-cleared', handleScenarioCleared)
  window.addEventListener('resize', updateHeaderOffset)

  await nextTick()
  updateHeaderOffset()

  const headerElement = document.querySelector('.workspace-header')
  if (headerElement && 'ResizeObserver' in window) {
    headerResizeObserver = new ResizeObserver(() => {
      updateHeaderOffset()
    })
    headerResizeObserver.observe(headerElement)
  }

  try {
    dashboard.value = await getDashboard()
    const defaultForecast = dashboard.value?.prediction_preview?.forecast_timestamps?.[0]
    selectedHorizon.value = defaultForecast || timelineOptions.value[timelineOptions.value.length - 1] || '2025-Q1'
  } catch (error) {
    console.error('Failed to load workspace dashboard:', error)
  }

  await loadAnalytics()
  await handleRouteIntent()
  await nextTick()
  updateHeaderOffset()
})

onUnmounted(() => {
  window.removeEventListener('scenario-result', handleScenarioResult)
  window.removeEventListener('scenario-cleared', handleScenarioCleared)
  window.removeEventListener('resize', updateHeaderOffset)

  if (headerResizeObserver) {
    headerResizeObserver.disconnect()
    headerResizeObserver = null
  }
})
</script>

<style scoped>
.workspace-page {
  min-height: 100vh;
  background: #040d16;
  --workspace-header-offset: 296px;
}

.workspace-layout {
  position: relative;
  min-height: 100vh;
  padding-top: var(--workspace-header-offset);
}

.workspace-stage {
  position: relative;
  width: 100%;
  height: calc(100vh - var(--workspace-header-offset));
}

:deep(.cesium-container) {
  width: 100%;
  height: 100%;
}
</style>
