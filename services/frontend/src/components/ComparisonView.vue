<template>
  <div v-if="visible" class="comparison-view">
    <div class="comparison-backdrop" @click="close"></div>
    <div class="comparison-dialog glass-card">
      <div class="comparison-dialog__header">
        <div>
          <strong>情景推演对比</strong>
          <small>{{ resultData.forecastHorizon || '最新预测窗' }}</small>
        </div>
        <button class="comparison-dialog__close" @click="close">×</button>
      </div>

      <div class="comparison-stats">
        <div class="comparison-stat">
          <span>区域平均变化</span>
          <strong :class="resultData.gppChange >= 0 ? 'positive' : 'negative'">
            {{ resultData.gppChange >= 0 ? '+' : '' }}{{ resultData.gppChange.toFixed(4) }}
          </strong>
        </div>
        <div class="comparison-stat">
          <span>碳汇影响比例</span>
          <strong :class="resultData.carbonImpact >= 0 ? 'positive' : 'negative'">
            {{ resultData.carbonImpact >= 0 ? '+' : '' }}{{ resultData.carbonImpact.toFixed(2) }}%
          </strong>
        </div>
        <div class="comparison-stat">
          <span>受影响节点</span>
          <strong>{{ changedNodes.length }}</strong>
        </div>
        <div class="comparison-stat">
          <span>情景参数</span>
          <strong>{{ resultData.emissionMultiplier?.toFixed?.(1) || resultData.emissionMultiplier }}x</strong>
        </div>
      </div>

      <div class="comparison-grid">
        <section class="map-panel glass-card">
          <div class="map-panel__head">
            <strong>基线预测</strong>
            <small>干预前</small>
          </div>
          <div ref="originalContainer" class="map-canvas"></div>
        </section>

        <section class="map-panel glass-card">
          <div class="map-panel__head">
            <strong>情景推演</strong>
            <small>干预后</small>
          </div>
          <div ref="scenarioContainer" class="map-canvas"></div>
        </section>
      </div>

      <div class="comparison-summary">
        <section class="summary-card glass-card">
          <div class="summary-card__head">
            <strong>影响排行</strong>
            <small>按绝对变化排序</small>
          </div>
          <ul>
            <li v-for="item in topChanges" :key="item.nodeId">
              <span>节点 {{ item.nodeId }}</span>
              <strong :class="item.delta >= 0 ? 'positive' : 'negative'">
                {{ item.delta >= 0 ? '+' : '' }}{{ item.delta.toFixed(4) }}
              </strong>
            </li>
          </ul>
        </section>

        <section class="summary-card glass-card">
          <div class="summary-card__head">
            <strong>解释摘要</strong>
            <small>与后端推演结果一致</small>
          </div>
          <ul>
            <li>
              <span>预测季度</span>
              <strong>{{ resultData.forecastHorizon || '最新' }}</strong>
            </li>
            <li>
              <span>影响节点</span>
              <strong>{{ changedNodes.join('、') || '未返回' }}</strong>
            </li>
            <li>
              <span>特征扰动</span>
              <strong>{{ featureDeltaText }}</strong>
            </li>
            <li>
              <span>结论</span>
              <strong>{{ conclusionText }}</strong>
            </li>
          </ul>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onUnmounted, ref } from 'vue'
import * as Cesium from 'cesium'

const visible = ref(false)
const resultData = ref({
  originalData: null,
  scenarioData: null,
  gppChange: 0,
  carbonImpact: 0,
  emissionMultiplier: 1,
  forecastHorizon: '',
  backendSummary: null,
})

const originalContainer = ref(null)
const scenarioContainer = ref(null)

let originalViewer = null
let scenarioViewer = null

const changedNodes = computed(() => resultData.value.backendSummary?.changed_nodes || [])
const featureDeltaText = computed(() => {
  const featureDeltas = resultData.value.backendSummary?.feature_deltas || {}
  const entries = Object.entries(featureDeltas)
    .slice(0, 3)
    .map(([key, value]) => `${key}: ${Number(value).toFixed(3)}`)
  return entries.join('；') || '以区域排放和地表覆盖扰动为主'
})

const topChanges = computed(() => {
  const baseline = resultData.value.originalData?.grid || []
  const scenario = resultData.value.scenarioData?.grid || []
  const scenarioMap = new Map(scenario.map((item) => [String(item.nodeId), item]))

  return baseline
    .map((item) => {
      const other = scenarioMap.get(String(item.nodeId))
      const delta = Number(other?.gpp || 0) - Number(item.gpp || 0)
      return {
        nodeId: item.nodeId,
        delta,
      }
    })
    .sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta))
    .slice(0, 5)
})

const conclusionText = computed(() => {
  if (resultData.value.carbonImpact <= -10) {
    return '该干预情景会显著削弱研究区碳汇表现。'
  }
  if (resultData.value.carbonImpact < 0) {
    return '该干预情景会对区域碳汇产生温和负向影响。'
  }
  return '该干预情景有望提升区域碳汇表现。'
})

function open(data) {
  resultData.value = data
  visible.value = true
  nextTick(() => {
    initMaps()
  })
}

function close() {
  visible.value = false
  destroyMaps()
  window.dispatchEvent(new CustomEvent('exit-comparison'))
}

function createViewer(container, grid) {
  const viewer = new Cesium.Viewer(container, {
    animation: false,
    baseLayerPicker: false,
    fullscreenButton: false,
    geocoder: false,
    homeButton: false,
    infoBox: false,
    sceneModePicker: false,
    selectionIndicator: false,
    timeline: false,
    navigationHelpButton: false,
    orderIndependentTranslucency: false,
  })

  viewer.imageryLayers.removeAll()
  viewer.imageryLayers.addImageryProvider(
    new Cesium.OpenStreetMapImageryProvider({
      url: 'https://tile.openstreetmap.org/',
    }),
  )

  const maxValue = Math.max(...grid.map((item) => Number(item.gpp) || 0), 1e-6)
  grid.forEach((point) => {
    const ratio = Math.max(0, Math.min(1, Number(point.gpp) / maxValue))
    const color = ratio >= 0.8
      ? Cesium.Color.fromCssColorString('rgba(118, 219, 155, 0.75)')
      : ratio >= 0.55
        ? Cesium.Color.fromCssColorString('rgba(228, 178, 91, 0.68)')
        : Cesium.Color.fromCssColorString('rgba(239, 125, 87, 0.66)')

    viewer.entities.add({
      position: Cesium.Cartesian3.fromDegrees(Number(point.lon), Number(point.lat)),
      point: {
        pixelSize: 7,
        color,
        outlineWidth: 1,
        outlineColor: Cesium.Color.WHITE.withAlpha(0.25),
      },
    })
  })

  viewer.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(118.8, 32.0, 80000),
    duration: 0,
  })

  return viewer
}

function initMaps() {
  destroyMaps()

  const originalGrid = resultData.value.originalData?.grid || []
  const scenarioGrid = resultData.value.scenarioData?.grid || []

  if (originalContainer.value) {
    originalViewer = createViewer(originalContainer.value, originalGrid)
  }
  if (scenarioContainer.value) {
    scenarioViewer = createViewer(scenarioContainer.value, scenarioGrid)
  }
}

function destroyMaps() {
  if (originalViewer) originalViewer.destroy()
  if (scenarioViewer) scenarioViewer.destroy()
  originalViewer = null
  scenarioViewer = null
}

onUnmounted(() => {
  destroyMaps()
})

defineExpose({ open, close })
</script>

<style scoped>
.comparison-view {
  position: fixed;
  inset: 0;
  z-index: 80;
}

.comparison-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(1, 7, 12, 0.74);
  backdrop-filter: blur(10px);
}

.comparison-dialog {
  position: relative;
  z-index: 1;
  width: min(1380px, calc(100vw - 32px));
  max-height: calc(100vh - 32px);
  margin: 16px auto;
  padding: 24px;
  overflow: auto;
}

.comparison-dialog__header,
.comparison-stats,
.comparison-summary {
  display: grid;
  gap: 16px;
}

.comparison-dialog__header {
  grid-template-columns: 1fr auto;
  align-items: start;
}

.comparison-dialog__header small,
.comparison-stat span,
.summary-card__head small,
.summary-card li span {
  color: var(--text-muted);
}

.comparison-dialog__close {
  width: 38px;
  height: 38px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-primary);
  cursor: pointer;
}

.comparison-stats {
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin-top: 18px;
}

.comparison-stat,
.map-panel,
.summary-card {
  padding: 18px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.comparison-stat strong {
  display: block;
  margin-top: 8px;
  font-size: 26px;
}

.comparison-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
  margin-top: 20px;
}

.map-panel__head,
.summary-card__head,
.summary-card li {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.map-canvas {
  margin-top: 14px;
  height: 360px;
  overflow: hidden;
  border-radius: 18px;
}

.comparison-summary {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-top: 18px;
}

.summary-card ul {
  list-style: none;
  margin: 14px 0 0;
  padding: 0;
  display: grid;
  gap: 12px;
}

.summary-card li {
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.summary-card li:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.positive { color: #8ee0a4; }
.negative { color: #ff9d7b; }

@media (max-width: 1100px) {
  .comparison-stats,
  .comparison-grid,
  .comparison-summary {
    grid-template-columns: 1fr;
  }

  .map-canvas {
    height: 300px;
  }
}
</style>
