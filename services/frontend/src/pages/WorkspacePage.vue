<template>
  <div class="workspace-page">
    <Header
      :current-date="selectedHorizon"
      :study-area="studyAreaName"
      :default-model="defaultModelName"
      :forecast-window="forecastWindow"
      @open-scenario="openScenario"
    />

    <main class="workspace-layout">
      <aside class="workspace-rail glass-card">
        <div>
          <span class="rail-label">分析任务</span>
          <h2>研究区工作台</h2>
        </div>
        <div class="rail-actions">
          <a href="#overview">总览</a>
          <a href="#signals">时序切换</a>
          <a href="#model">模型结果</a>
          <button @click="openScenario">情景推演</button>
          <RouterLink to="/cases">案例回放</RouterLink>
        </div>
        <div class="rail-tip">
          <strong>当前说明</strong>
          <p>主地图已切换为真实后端预测图层，底图、热力层与情景推演在同一工作台中联动。</p>
        </div>
      </aside>

      <section class="workspace-stage" id="overview">
        <CesiumViewer :horizon="selectedHorizon" :scenario-result="scenarioResult" />
        <LegendPanel />
        <ControlPanel @reset-view="handleResetView" @toggle-layer="handleToggleLayer" />
        <WorkspaceInsights :analytics="analytics" :dashboard="dashboard" :selected-horizon="selectedHorizon" />
        <TimelineSlider id="signals" v-model="selectedHorizon" :options="forecastOptions" label="预测季度" />
        <DetailPanel />
        <ScenarioPanel ref="scenarioPanel" />
        <ComparisonView ref="comparisonView" />
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'

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

const forecastOptions = computed(() => dashboard.value?.prediction_preview?.forecast_timestamps || ['2025-Q1', '2025-Q2'])
const forecastWindow = computed(() => {
  const window = dashboard.value?.prediction_preview?.prediction_window
  if (!window) return '2025-Q1 至 2025-Q2'
  return `${window.from || '起点'} 至 ${window.to || '终点'}`
})
const studyAreaName = computed(() => dashboard.value?.project?.study_area?.name || '南京研究区')
const defaultModelName = computed(() => dashboard.value?.prediction_preview?.model_name || 'ST-GNN Multi-Step')

function handleResetView() {
  window.dispatchEvent(new CustomEvent('reset-view'))
}

function handleToggleLayer() {
  window.dispatchEvent(new CustomEvent('toggle-layer'))
}

function openScenario() {
  scenarioPanel.value?.open()
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

function handleScenarioResult(event) {
  scenarioResult.value = event.detail
  comparisonView.value?.open(event.detail)
}

onMounted(async () => {
  window.addEventListener('scenario-result', handleScenarioResult)

  try {
    dashboard.value = await getDashboard()
    if (forecastOptions.value.length > 0) {
      selectedHorizon.value = forecastOptions.value[0]
    }
  } catch (error) {
    console.error('Failed to load workspace dashboard:', error)
  }

  await loadAnalytics()
})

onUnmounted(() => {
  window.removeEventListener('scenario-result', handleScenarioResult)
})
</script>

<style scoped>
.workspace-page {
  min-height: 100vh;
  background: #040d16;
}

.workspace-layout {
  position: relative;
  min-height: 100vh;
  padding-top: 168px;
}

.workspace-rail {
  position: fixed;
  top: 204px;
  left: 20px;
  z-index: 17;
  width: 240px;
  padding: 18px;
  display: grid;
  gap: 18px;
}

.rail-label {
  color: var(--brand-amber);
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.workspace-rail h2 {
  margin-top: 8px;
  font-size: 24px;
}

.rail-actions {
  display: grid;
  gap: 10px;
}

.rail-actions a,
.rail-actions button {
  min-height: 42px;
  display: inline-flex;
  align-items: center;
  justify-content: flex-start;
  padding: 0 14px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-primary);
  cursor: pointer;
}

.rail-tip {
  padding: 14px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-secondary);
  font-size: 13px;
}

.rail-tip strong {
  display: block;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.workspace-stage {
  position: relative;
  width: 100%;
  height: calc(100vh - 168px);
}

:deep(.cesium-container) {
  width: 100%;
  height: 100%;
}

@media (max-width: 1100px) {
  .workspace-rail {
    display: none;
  }

  .workspace-layout {
    padding-top: 212px;
  }

  .workspace-stage {
    height: calc(100vh - 212px);
  }
}
</style>
