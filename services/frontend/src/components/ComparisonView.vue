<template>
  <div v-if="visible" class="comparison-view">
    <!-- 顶部控制栏 -->
    <div class="comparison-header">
      <div class="header-title">
        <span class="title-icon">📊</span>
        <span>情景推演对比</span>
      </div>
      <div class="header-controls">
        <button class="view-btn" :class="{ active: viewMode === 'split' }" @click="viewMode = 'split'">
          ⚛️ 分屏对比
        </button>
        <button class="view-btn" :class="{ active: viewMode === 'slider' }" @click="viewMode = 'slider'">
          🎚️ 滑块对比
        </button>
        <button class="view-btn" :class="{ active: viewMode === 'toggle' }" @click="viewMode = 'toggle'">
          🔀 切换对比
        </button>
      </div>
      <button class="close-btn" @click="close">×</button>
    </div>

    <!-- 分屏对比模式 -->
    <div v-if="viewMode === 'split'" class="split-view">
      <div class="split-panel left-panel">
        <div class="panel-label">
          <span class="label-badge original">原始</span>
          <span class="label-text">建设前</span>
        </div>
        <div class="cesium-container">
          <div ref="originalContainer" class="cesium-view"></div>
        </div>
        <div class="panel-stats">
          <div class="stat-item">
            <span class="stat-label">平均 GPP</span>
            <span class="stat-value">{{ originalStats.avgGPP }}</span>
          </div>
        </div>
      </div>

      <div class="split-divider">
        <span class="divider-text">VS</span>
      </div>

      <div class="split-panel right-panel">
        <div class="panel-label">
          <span class="label-badge scenario">情景</span>
          <span class="label-text">建设后</span>
        </div>
        <div class="cesium-container">
          <div ref="scenarioContainer" class="cesium-view"></div>
        </div>
        <div class="panel-stats">
          <div class="stat-item">
            <span class="stat-label">平均 GPP</span>
            <span class="stat-value" :class="gppChangeClass">{{ scenarioStats.avgGPP }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 滑块对比模式 -->
    <div v-else-if="viewMode === 'slider'" class="slider-view">
      <div class="slider-container">
        <div class="slider-layer original-layer" :style="{ width: sliderPosition + '%' }">
          <div ref="sliderOriginalContainer" class="cesium-view"></div>
          <div class="layer-label original-label">原始</div>
        </div>
        <div class="slider-layer scenario-layer">
          <div ref="sliderScenarioContainer" class="cesium-view"></div>
          <div class="layer-label scenario-label">情景</div>
        </div>
        <div class="slider-handle" :style="{ left: sliderPosition + '%' }" @mousedown="startDrag">
          <div class="handle-line"></div>
          <div class="handle-button">⟷</div>
        </div>
      </div>
      <div class="slider-hint">← 拖动滑块对比 →</div>
    </div>

    <!-- 切换对比模式 -->
    <div v-else-if="viewMode === 'toggle'" class="toggle-view">
      <div class="toggle-container">
        <div class="cesium-container">
          <div ref="toggleContainer" class="cesium-view"></div>
        </div>
        <div class="toggle-buttons">
          <button class="toggle-btn" :class="{ active: showOriginal }" @click="showOriginal = true">
            🌍 原始（建设前）
          </button>
          <button class="toggle-btn" :class="{ active: !showOriginal }" @click="showOriginal = false">
            🏭 情景（建设后）
          </button>
        </div>
      </div>
    </div>

    <!-- 底部统计面板 -->
    <div class="comparison-footer">
      <div class="footer-stats">
        <div class="footer-stat">
          <span class="stat-label">区域平均 GPP 变化</span>
          <span class="stat-value" :class="gppChangeClass">
            {{ resultData.gppChange >= 0 ? '+' : '' }}{{ resultData.gppChange }} gC/m²/year
          </span>
        </div>
        <div class="footer-stat">
          <span class="stat-label">碳汇影响</span>
          <span class="stat-value" :class="resultData.carbonImpact >= 0 ? 'positive' : 'negative'">
            {{ resultData.carbonImpact >= 0 ? '提升' : '下降' }} {{ Math.abs(resultData.carbonImpact) }}%
          </span>
        </div>
        <div class="footer-stat">
          <span class="stat-label">排放强度倍数</span>
          <span class="stat-value">×{{ resultData.emissionMultiplier }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as Cesium from 'cesium'

const TIANDITU_TOKEN = 'f7c661500b1d6f3873b1538c67d81ad8'

// 状态
const visible = ref(false)
const viewMode = ref('split') // split | slider | toggle
const sliderPosition = ref(50)
const showOriginal = ref(true)
const isDragging = ref(false)

// Cesium Viewers
let originalViewer = null
let scenarioViewer = null
let toggleViewer = null

// 结果数据
const resultData = ref({
  originalData: null,
  scenarioData: null,
  gppChange: 0,
  carbonImpact: 0,
  emissionMultiplier: 1
})

// DOM 引用
const originalContainer = ref(null)
const scenarioContainer = ref(null)
const sliderOriginalContainer = ref(null)
const sliderScenarioContainer = ref(null)
const toggleContainer = ref(null)

// 计算属性
const originalStats = computed(() => {
  if (!resultData.value.originalData || !resultData.value.originalData.grid) {
    return { avgGPP: '-' }
  }
  const grid = resultData.value.originalData.grid
  const avg = grid.reduce((sum, p) => sum + (p.gpp || 0), 0) / grid.length
  return { avgGPP: avg.toFixed(2) }
})

const scenarioStats = computed(() => {
  if (!resultData.value.scenarioData || !resultData.value.scenarioData.grid) {
    return { avgGPP: '-' }
  }
  const grid = resultData.value.scenarioData.grid
  const avg = grid.reduce((sum, p) => sum + (p.gpp || 0), 0) / grid.length
  return { avgGPP: avg.toFixed(2) }
})

const gppChangeClass = computed(() => {
  return resultData.value.gppChange >= 0 ? 'positive' : 'negative'
})

// 方法
function open(data) {
  resultData.value = data
  visible.value = true
  nextTick(() => {
    initViewers()
  })
}

function close() {
  visible.value = false
  cleanupViewers()
  // 通知退出对比模式
  window.dispatchEvent(new CustomEvent('exit-comparison'))
}

function createViewer(container, gridData, label) {
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
  })

  // 添加 OpenStreetMap 底图
  viewer.imageryLayers.addImageryProvider(
    new Cesium.OpenStreetMapImageryProvider({
      url: 'https://tile.openstreetmap.org/'
    })
  )

  // 添加热力图层（简化版）
  if (gridData && gridData.grid) {
    addHeatmapEntities(viewer, gridData.grid)
  }

  // 飞到南京
  viewer.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(118.8, 32.0, 80000),
    duration: 0
  })

  return viewer
}

function addHeatmapEntities(viewer, gridData) {
  gridData.forEach(point => {
    const color = getGPPColor(point.gpp)
    viewer.entities.add({
      position: Cesium.Cartesian3.fromDegrees(point.lon, point.lat),
      point: {
        pixelSize: 8,
        color: color,
        outlineColor: Cesium.Color.WHITE.withAlpha(0.3),
        outlineWidth: 1
      }
    })
  })
}

function getGPPColor(gpp) {
  if (gpp >= 5) return Cesium.Color.fromCssColorString('#4CAF50').withAlpha(0.7)
  if (gpp >= 2) return Cesium.Color.fromCssColorString('#FFC107').withAlpha(0.7)
  return Cesium.Color.fromCssColorString('#FF5252').withAlpha(0.7)
}

function initViewers() {
  cleanupViewers()

  if (viewMode.value === 'split') {
    if (originalContainer.value && scenarioContainer.value) {
      originalViewer = createViewer(originalContainer.value, resultData.value.originalData)
      scenarioViewer = createViewer(scenarioContainer.value, resultData.value.scenarioData)
    }
  } else if (viewMode.value === 'slider') {
    if (sliderOriginalContainer.value && sliderScenarioContainer.value) {
      originalViewer = createViewer(sliderOriginalContainer.value, resultData.value.originalData)
      scenarioViewer = createViewer(sliderScenarioContainer.value, resultData.value.scenarioData)
    }
  } else if (viewMode.value === 'toggle') {
    if (toggleContainer.value) {
      toggleViewer = createViewer(toggleContainer.value, showOriginal.value ? resultData.value.originalData : resultData.value.scenarioData)
    }
  }
}

function cleanupViewers() {
  if (originalViewer) {
    originalViewer.destroy()
    originalViewer = null
  }
  if (scenarioViewer) {
    scenarioViewer.destroy()
    scenarioViewer = null
  }
  if (toggleViewer) {
    toggleViewer.destroy()
    toggleViewer = null
  }
}

function startDrag(e) {
  isDragging.value = true
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
}

function onDrag(e) {
  if (!isDragging.value) return
  const container = e.currentTarget.closest('.slider-container')
  if (container) {
    const rect = container.getBoundingClientRect()
    const percent = ((e.clientX - rect.left) / rect.width) * 100
    sliderPosition.value = Math.max(10, Math.min(90, percent))
  }
}

function stopDrag() {
  isDragging.value = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
}

// 监听模式切换
watch(viewMode, () => {
  nextTick(() => {
    initViewers()
  })
})

// 监听切换模式的数据变化
watch(showOriginal, () => {
  if (toggleViewer && toggleContainer.value) {
    toggleViewer.destroy()
    toggleViewer = createViewer(toggleContainer.value, showOriginal.value ? resultData.value.originalData : resultData.value.scenarioData)
  }
})

onUnmounted(() => {
  cleanupViewers()
})

defineExpose({ open, close })
</script>

<style scoped>
.comparison-view {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.95);
  z-index: 2000;
  display: flex;
  flex-direction: column;
}

/* 顶部控制栏 */
.comparison-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 25px;
  background: rgba(20, 25, 30, 0.98);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: white;
}

.title-icon {
  font-size: 24px;
}

.header-controls {
  display: flex;
  gap: 10px;
}

.view-btn {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.3s;
  font-size: 13px;
}

.view-btn:hover {
  background: rgba(255, 255, 255, 0.15);
}

.view-btn.active {
  background: rgba(76, 175, 80, 0.3);
  border-color: #4CAF50;
  color: #4CAF50;
}

.close-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  font-size: 32px;
  cursor: pointer;
  padding: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

/* 分屏对比 */
.split-view {
  flex: 1;
  display: flex;
  gap: 0;
  overflow: hidden;
}

.split-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
}

.panel-label {
  position: absolute;
  top: 15px;
  left: 15px;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(0, 0, 0, 0.7);
  padding: 8px 15px;
  border-radius: 8px;
}

.label-badge {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
}

.label-badge.original {
  background: rgba(100, 181, 246, 0.3);
  color: #64B5F6;
}

.label-badge.scenario {
  background: rgba(255, 82, 82, 0.3);
  color: #FF5252;
}

.label-text {
  font-size: 13px;
  color: white;
  font-weight: 500;
}

.cesium-container {
  flex: 1;
  position: relative;
}

.cesium-view {
  width: 100%;
  height: 100%;
}

.split-divider {
  width: 2px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.divider-text {
  background: rgba(20, 25, 30, 0.9);
  padding: 8px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.5);
}

.panel-stats {
  position: absolute;
  bottom: 15px;
  left: 15px;
  z-index: 10;
  background: rgba(0, 0, 0, 0.7);
  padding: 10px 15px;
  border-radius: 8px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: white;
}

/* 滑块对比 */
.slider-view {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.slider-container {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.slider-layer {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
}

.original-layer {
  z-index: 1;
}

.scenario-layer {
  right: 0;
  z-index: 0;
}

.layer-label {
  position: absolute;
  bottom: 20px;
  padding: 8px 15px;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 8px;
  font-size: 13px;
  color: white;
  z-index: 10;
}

.original-label {
  left: 20px;
}

.scenario-label {
  right: 20px;
}

.slider-handle {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 4px;
  background: #4CAF50;
  cursor: ew-resize;
  z-index: 100;
  transform: translateX(-50%);
}

.handle-line {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #4CAF50;
}

.handle-button {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
  height: 40px;
  background: #4CAF50;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.slider-hint {
  text-align: center;
  padding: 10px;
  background: rgba(20, 25, 30, 0.98);
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
}

/* 切换对比 */
.toggle-view {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.toggle-container {
  flex: 1;
  position: relative;
}

.toggle-buttons {
  position: absolute;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 15px;
  z-index: 10;
}

.toggle-btn {
  padding: 12px 24px;
  background: rgba(0, 0, 0, 0.8);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.toggle-btn:hover {
  background: rgba(0, 0, 0, 0.9);
}

.toggle-btn.active {
  background: rgba(76, 175, 80, 0.3);
  border-color: #4CAF50;
  color: #4CAF50;
}

/* 底部统计 */
.comparison-footer {
  background: rgba(20, 25, 30, 0.98);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding: 20px 30px;
}

.footer-stats {
  display: flex;
  justify-content: center;
  gap: 50px;
}

.footer-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.footer-stat .stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.footer-stat .stat-value {
  font-size: 20px;
  font-weight: 600;
  color: white;
}

.stat-value.positive {
  color: #4CAF50;
}

.stat-value.negative {
  color: #FF5252;
}
</style>
