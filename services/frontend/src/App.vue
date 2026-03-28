<script setup>
import { ref } from 'vue'
import CesiumViewer from './components/CesiumViewer.vue'
import TimelineSlider from './components/TimelineSlider.vue'
import Header from './components/Header.vue'
import DetailPanel from './components/DetailPanel.vue'
import LegendPanel from './components/LegendPanel.vue'
import ControlPanel from './components/ControlPanel.vue'
import ScenarioPanel from './components/ScenarioPanel.vue'
import ComparisonView from './components/ComparisonView.vue'

const selectedDate = ref('2020-Q2')
const scenarioResult = ref(null)
const scenarioPanel = ref(null)
const comparisonView = ref(null)

function handleResetView() {
  window.dispatchEvent(new CustomEvent('reset-view'))
}

function handleToggleLayer() {
  window.dispatchEvent(new CustomEvent('toggle-layer'))
}

function openScenario() {
  scenarioPanel.value?.open()
}

// 监听情景推演结果
window.addEventListener('scenario-result', (event) => {
  scenarioResult.value = event.detail
  // 打开对比视图
  comparisonView.value?.open(event.detail)
})
</script>

<template>
  <Header :currentDate="selectedDate" @open-scenario="openScenario" />
  <CesiumViewer :date="selectedDate" :scenarioResult="scenarioResult" />
  <TimelineSlider v-model="selectedDate" />
  <DetailPanel />
  <LegendPanel />
  <ControlPanel @reset-view="handleResetView" @toggle-layer="handleToggleLayer" />
  <ScenarioPanel ref="scenarioPanel" />
  <ComparisonView ref="comparisonView" />
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
</style>
