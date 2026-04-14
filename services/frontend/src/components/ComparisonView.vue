<template>
  <div v-if="visible" class="comparison-view">
    <div class="comparison-backdrop" @click="close"></div>

    <div class="comparison-dialog glass-card">
      <div class="comparison-dialog__header">
        <div>
          <strong>情景推演对比</strong>
          <small>{{ resultData.forecastHorizon || '最新预测季度' }}</small>
        </div>
        <div class="comparison-dialog__actions">
          <span class="comparison-dialog__hint">地图支持滚轮缩放、拖拽平移与点击节点查看详情</span>
          <button class="comparison-dialog__close" @click="close">×</button>
        </div>
      </div>

      <div class="comparison-stage">
        <section class="map-panel glass-card">
          <div class="map-panel__badge">
            <strong>推演前</strong>
            <small>查看基线空间格局</small>
          </div>
          <div ref="originalContainer" class="map-canvas"></div>
        </section>

        <section class="map-panel glass-card">
          <div class="map-panel__badge map-panel__badge--highlight">
            <strong>推演后</strong>
            <small>受影响节点可直接点击查看</small>
          </div>
          <div ref="scenarioContainer" class="map-canvas"></div>
        </section>

        <div class="comparison-floating comparison-floating--top glass-card">
          <span>区域平均变化</span>
          <strong :class="resultData.gppChange >= 0 ? 'positive' : 'negative'">
            {{ resultData.gppChange >= 0 ? '+' : '' }}{{ resultData.gppChange.toFixed(4) }}
          </strong>
        </div>

        <div class="comparison-floating comparison-floating--bottom glass-card">
          <span>受影响节点</span>
          <strong>{{ changedNodes.length }}</strong>
        </div>

        <div class="comparison-toolbar glass-card">
          <button class="comparison-tool" :class="{ active: activePanel === 'summary' }" @click="togglePanel('summary')">
            推演摘要
          </button>
          <button class="comparison-tool" :class="{ active: activePanel === 'ranking' }" @click="togglePanel('ranking')">
            变化排行
          </button>
          <button
            class="comparison-tool"
            :class="{ active: activePanel === 'detail' }"
            :disabled="!selectedPoint"
            @click="togglePanel('detail')"
          >
            节点详情
          </button>
        </div>

        <transition name="drawer-slide">
          <aside v-if="activePanel" class="comparison-drawer glass-card">
            <div class="comparison-drawer__head">
              <strong>{{ drawerTitle }}</strong>
              <button class="comparison-drawer__close" @click="activePanel = null">×</button>
            </div>

            <div v-if="activePanel === 'summary'" class="drawer-content">
              <ul class="drawer-list">
                <li>
                  <span>预测季度</span>
                  <strong>{{ resultData.forecastHorizon || '最新' }}</strong>
                </li>
                <li>
                  <span>碳汇影响比例</span>
                  <strong :class="resultData.carbonImpact >= 0 ? 'positive' : 'negative'">
                    {{ resultData.carbonImpact >= 0 ? '+' : '' }}{{ resultData.carbonImpact.toFixed(2) }}%
                  </strong>
                </li>
                <li>
                  <span>排放强度倍数</span>
                  <strong>{{ resultData.emissionMultiplier?.toFixed?.(1) || resultData.emissionMultiplier }}x</strong>
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
            </div>

            <div v-else-if="activePanel === 'ranking'" class="drawer-content">
              <ul class="drawer-list">
                <li v-for="item in topChanges" :key="item.nodeId">
                  <span>节点 {{ item.nodeId }}</span>
                  <strong :class="item.delta >= 0 ? 'positive' : 'negative'">
                    {{ item.delta >= 0 ? '+' : '' }}{{ item.delta.toFixed(4) }}
                  </strong>
                </li>
              </ul>
            </div>

            <div v-else-if="activePanel === 'detail' && selectedPoint" class="drawer-content">
              <ul class="drawer-list">
                <li>
                  <span>节点编号</span>
                  <strong>{{ selectedPoint.nodeId }}</strong>
                </li>
                <li>
                  <span>研究区域</span>
                  <strong>南京研究区</strong>
                </li>
                <li>
                  <span>地理位置</span>
                  <strong>{{ selectedPoint.lat.toFixed(4) }}°N / {{ selectedPoint.lon.toFixed(4) }}°E</strong>
                </li>
                <li>
                  <span>当前结果</span>
                  <strong>{{ selectedPoint.gpp.toFixed(4) }}</strong>
                </li>
                <li v-if="selectedPoint.delta !== null">
                  <span>推演变化</span>
                  <strong :class="selectedPoint.delta >= 0 ? 'positive' : 'negative'">
                    {{ selectedPoint.delta >= 0 ? '+' : '' }}{{ selectedPoint.delta.toFixed(4) }}
                  </strong>
                </li>
                <li>
                  <span>是否受影响</span>
                  <strong>{{ selectedPoint.isChanged ? '是' : '否' }}</strong>
                </li>
                <li v-if="selectedPoint.landcoverLabel">
                  <span>主导地类</span>
                  <strong>{{ selectedPoint.landcoverLabel }}</strong>
                </li>
                <li>
                  <span>所在地图</span>
                  <strong>{{ selectedPoint.sourceLabel }}</strong>
                </li>
              </ul>
            </div>
          </aside>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onUnmounted, ref } from 'vue'
import * as Cesium from 'cesium'

const visible = ref(false)
const activePanel = ref(null)
const resultData = ref({
  originalData: null,
  scenarioData: null,
  gppChange: 0,
  carbonImpact: 0,
  emissionMultiplier: 1,
  forecastHorizon: '',
  backendSummary: null,
})
const selectedPoint = ref(null)

const originalContainer = ref(null)
const scenarioContainer = ref(null)

let originalViewer = null
let scenarioViewer = null
let originalClickHandler = null
let scenarioClickHandler = null

const changedNodes = computed(() => (resultData.value.backendSummary?.changed_nodes || []).map((item) => String(item)))
const changedNodeSet = computed(() => new Set(changedNodes.value))

const drawerTitle = computed(() => {
  if (activePanel.value === 'summary') return '推演摘要'
  if (activePanel.value === 'ranking') return '变化排行'
  if (activePanel.value === 'detail') return '节点详情'
  return ''
})

const featureDeltaText = computed(() => {
  const featureDeltas = resultData.value.backendSummary?.feature_deltas || {}
  const entries = Object.entries(featureDeltas)
    .slice(0, 3)
    .map(([key, value]) => `${key}: ${Number(value).toFixed(3)}`)
  return entries.join('；') || '以区域排放与地表覆盖扰动为主'
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
        nodeId: String(item.nodeId),
        delta,
      }
    })
    .sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta))
    .slice(0, 8)
})

const conclusionText = computed(() => {
  if (resultData.value.carbonImpact <= -10) {
    return '该情景会明显削弱研究区碳汇表现。'
  }
  if (resultData.value.carbonImpact < 0) {
    return '该情景会对区域碳汇产生温和负向影响。'
  }
  if (resultData.value.carbonImpact > 0) {
    return '该情景有望提升研究区碳汇表现。'
  }
  return '该情景对当前区域结果影响有限。'
})

function open(data) {
  resultData.value = data
  selectedPoint.value = null
  activePanel.value = null
  visible.value = true
  nextTick(() => {
    initMaps()
  })
}

function close() {
  visible.value = false
  destroyMaps()
  selectedPoint.value = null
  activePanel.value = null
  window.dispatchEvent(new CustomEvent('exit-comparison'))
}

function togglePanel(panel) {
  if (panel === 'detail' && !selectedPoint.value) return
  activePanel.value = activePanel.value === panel ? null : panel
}

function colorByScore(value, maxValue) {
  const safeMax = Math.max(Math.abs(Number(maxValue)) || 0, 1e-6)
  const ratio = Math.max(0, Math.min(1, Math.abs(Number(value)) / safeMax))

  if (ratio >= 0.8) return Cesium.Color.fromCssColorString('rgba(118, 219, 155, 0.72)')
  if (ratio >= 0.55) return Cesium.Color.fromCssColorString('rgba(228, 178, 91, 0.66)')
  return Cesium.Color.fromCssColorString('rgba(239, 125, 87, 0.62)')
}

function defaultCamera(viewer) {
  viewer.camera.setView({
    destination: Cesium.Cartesian3.fromDegrees(118.8, 32.0, 145000),
  })
}

function buildDetail(point, source) {
  const baseline = (resultData.value.originalData?.grid || []).find((item) => String(item.nodeId) === String(point.nodeId))
  const scenario = (resultData.value.scenarioData?.grid || []).find((item) => String(item.nodeId) === String(point.nodeId))
  const delta = baseline && scenario ? Number(scenario.gpp) - Number(baseline.gpp) : null

  return {
    source,
    sourceLabel: source === 'scenario' ? '推演后地图' : '推演前地图',
    nodeId: String(point.nodeId),
    lat: Number(point.lat),
    lon: Number(point.lon),
    gpp: Number(point.gpp),
    delta,
    isChanged: changedNodeSet.value.has(String(point.nodeId)),
    landcoverLabel: point.landcoverLabel || null,
  }
}

function attachClickHandler(viewer, source) {
  const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas)
  handler.setInputAction((movement) => {
    const picked = viewer.scene.pick(movement.position)
    const pointData = picked?.id?.properties?.pointData?.getValue?.()
    if (!pointData) return
    selectedPoint.value = buildDetail(pointData, source)
    activePanel.value = 'detail'
  }, Cesium.ScreenSpaceEventType.LEFT_CLICK)
  return handler
}

function createViewer(container) {
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
    requestRenderMode: true,
  })

  viewer.imageryLayers.removeAll()
  viewer.imageryLayers.addImageryProvider(
    new Cesium.OpenStreetMapImageryProvider({
      url: 'https://tile.openstreetmap.org/',
    }),
  )

  defaultCamera(viewer)
  return viewer
}

function addGridToViewer(viewer, grid, source) {
  const maxValue = Math.max(...grid.map((item) => Math.abs(Number(item.gpp) || 0)), 1e-6)

  grid.forEach((point) => {
    const pointData = {
      nodeId: String(point.nodeId),
      lat: Number(point.lat),
      lon: Number(point.lon),
      gpp: Number(point.gpp),
      landcoverLabel: point.landcoverLabel || null,
    }

    viewer.entities.add({
      rectangle: {
        coordinates: Cesium.Rectangle.fromDegrees(
          Number(point.minLon ?? point.lon) - 0.002,
          Number(point.minLat ?? point.lat) - 0.002,
          Number(point.maxLon ?? point.lon) + 0.002,
          Number(point.maxLat ?? point.lat) + 0.002,
        ),
        material: colorByScore(point.gpp, maxValue),
        outline: true,
        outlineColor: Cesium.Color.fromCssColorString('rgba(255,255,255,0.10)'),
        outlineWidth: 1,
      },
      properties: {
        pointData,
      },
    })

    viewer.entities.add({
      position: Cesium.Cartesian3.fromDegrees(Number(point.lon), Number(point.lat)),
      point: {
        pixelSize: 6,
        color: Cesium.Color.WHITE.withAlpha(0.82),
        outlineWidth: 1,
        outlineColor: Cesium.Color.fromCssColorString('#08131d').withAlpha(0.55),
        disableDepthTestDistance: Number.POSITIVE_INFINITY,
      },
      properties: {
        pointData,
      },
    })

    if (source === 'scenario' && changedNodeSet.value.has(String(point.nodeId))) {
      viewer.entities.add({
        position: Cesium.Cartesian3.fromDegrees(Number(point.lon), Number(point.lat)),
        billboard: {
          image: createMarkerCanvas(point.nodeId),
          verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
          disableDepthTestDistance: Number.POSITIVE_INFINITY,
          scale: 1,
        },
        properties: {
          pointData,
        },
      })
    }
  })

  viewer.scene.requestRender()
}

function createMarkerCanvas(nodeId) {
  const canvas = document.createElement('canvas')
  canvas.width = 164
  canvas.height = 66
  const ctx = canvas.getContext('2d')

  ctx.fillStyle = 'rgba(8, 19, 29, 0.88)'
  ctx.strokeStyle = '#f0c16b'
  ctx.lineWidth = 2
  roundRect(ctx, 8, 8, 148, 42, 18)
  ctx.fill()
  ctx.stroke()

  ctx.beginPath()
  ctx.moveTo(62, 50)
  ctx.lineTo(74, 62)
  ctx.lineTo(86, 50)
  ctx.closePath()
  ctx.fillStyle = 'rgba(8, 19, 29, 0.88)'
  ctx.fill()
  ctx.strokeStyle = '#f0c16b'
  ctx.stroke()

  ctx.fillStyle = '#f0c16b'
  ctx.font = '600 20px Microsoft YaHei'
  ctx.fillText(`节点 ${nodeId}`, 26, 35)
  return canvas
}

function roundRect(ctx, x, y, width, height, radius) {
  ctx.beginPath()
  ctx.moveTo(x + radius, y)
  ctx.lineTo(x + width - radius, y)
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius)
  ctx.lineTo(x + width, y + height - radius)
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height)
  ctx.lineTo(x + radius, y + height)
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius)
  ctx.lineTo(x, y + radius)
  ctx.quadraticCurveTo(x, y, x + radius, y)
  ctx.closePath()
}

function initMaps() {
  destroyMaps()

  const originalGrid = resultData.value.originalData?.grid || []
  const scenarioGrid = resultData.value.scenarioData?.grid || []

  if (originalContainer.value) {
    originalViewer = createViewer(originalContainer.value)
    addGridToViewer(originalViewer, originalGrid, 'baseline')
    originalClickHandler = attachClickHandler(originalViewer, 'baseline')
  }

  if (scenarioContainer.value) {
    scenarioViewer = createViewer(scenarioContainer.value)
    addGridToViewer(scenarioViewer, scenarioGrid, 'scenario')
    scenarioClickHandler = attachClickHandler(scenarioViewer, 'scenario')
  }
}

function destroyMaps() {
  if (originalClickHandler) originalClickHandler.destroy()
  if (scenarioClickHandler) scenarioClickHandler.destroy()
  if (originalViewer) originalViewer.destroy()
  if (scenarioViewer) scenarioViewer.destroy()
  originalClickHandler = null
  scenarioClickHandler = null
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
  background: rgba(1, 7, 12, 0.8);
  backdrop-filter: blur(10px);
}

.comparison-dialog {
  position: relative;
  z-index: 1;
  width: calc(100vw - 18px);
  height: calc(100vh - 18px);
  max-width: 1600px;
  margin: 9px auto;
  padding: 18px;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  gap: 16px;
}

.comparison-dialog__header,
.comparison-dialog__actions,
.comparison-toolbar,
.comparison-drawer__head,
.drawer-list li {
  display: flex;
  gap: 12px;
}

.comparison-dialog__header {
  align-items: center;
  justify-content: space-between;
}

.comparison-dialog__actions {
  align-items: center;
}

.comparison-dialog__hint {
  color: var(--text-muted);
  font-size: 13px;
}

.comparison-dialog__close,
.comparison-drawer__close {
  width: 38px;
  height: 38px;
  border: none;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-primary);
  cursor: pointer;
  font-size: 20px;
}

.comparison-stage {
  position: relative;
  min-height: 0;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.map-panel {
  position: relative;
  overflow: hidden;
}

.map-panel__badge {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 2;
  display: grid;
  gap: 2px;
  padding: 12px 16px;
  border-radius: 16px;
  background: rgba(8, 19, 29, 0.78);
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(14px);
}

.map-panel__badge small,
.comparison-floating span,
.drawer-list span {
  color: var(--text-muted);
}

.map-panel__badge--highlight {
  border-color: rgba(240, 193, 107, 0.42);
}

.map-canvas {
  width: 100%;
  height: 100%;
  min-height: 0;
}

.comparison-floating {
  position: absolute;
  z-index: 3;
  display: grid;
  gap: 4px;
  min-width: 170px;
  padding: 12px 14px;
}

.comparison-floating strong {
  font-size: 22px;
}

.comparison-floating--top {
  right: 18px;
  top: 18px;
}

.comparison-floating--bottom {
  left: calc(50% - 96px);
  bottom: 18px;
}

.comparison-toolbar {
  position: absolute;
  left: 18px;
  bottom: 18px;
  z-index: 4;
  padding: 10px;
  border-radius: 20px;
  background: rgba(8, 19, 29, 0.82);
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(14px);
}

.comparison-tool {
  min-height: 42px;
  padding: 0 16px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-primary);
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
}

.comparison-tool.active {
  background: linear-gradient(135deg, rgba(31, 143, 188, 0.28), rgba(79, 191, 127, 0.24));
  border-color: rgba(79, 191, 127, 0.32);
}

.comparison-tool:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.comparison-drawer {
  position: absolute;
  right: 18px;
  bottom: 74px;
  z-index: 5;
  width: min(360px, calc(100vw - 36px));
  max-height: calc(100% - 140px);
  padding: 16px 18px;
  overflow: auto;
}

.comparison-drawer__head {
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.drawer-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.drawer-list li {
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.drawer-list li:last-child {
  border-bottom: none;
}

.positive {
  color: #8ee0a4;
}

.negative {
  color: #ff9d7b;
}

.drawer-slide-enter-active,
.drawer-slide-leave-active {
  transition: transform 0.22s ease, opacity 0.22s ease;
}

.drawer-slide-enter-from,
.drawer-slide-leave-to {
  transform: translateX(16px);
  opacity: 0;
}

@media (max-width: 1100px) {
  .comparison-dialog {
    padding: 14px;
  }

  .comparison-stage {
    grid-template-columns: 1fr;
    overflow: auto;
  }

  .map-panel {
    min-height: 420px;
  }

  .comparison-toolbar {
    left: 14px;
    right: 14px;
    bottom: 14px;
    justify-content: space-between;
  }

  .comparison-floating--bottom {
    left: 14px;
    bottom: 76px;
  }

  .comparison-drawer {
    right: 14px;
    left: 14px;
    width: auto;
    bottom: 134px;
    max-height: 34vh;
  }

  .comparison-dialog__header {
    align-items: flex-start;
    flex-direction: column;
  }

  .comparison-dialog__actions {
    justify-content: space-between;
    width: 100%;
  }
}
</style>
