<template>
  <div v-if="visible" class="scenario-panel">
    <div class="panel-header">
      <span class="panel-title">🔬 情景推演</span>
      <button class="close-btn" @click="close">×</button>
    </div>

    <div class="panel-content">
      <!-- 当前状态 -->
      <div class="status-section">
        <div class="status-label">当前状态</div>
        <div class="status-value" :class="statusClass">
          {{ statusText }}
        </div>
      </div>

      <!-- 操作步骤提示 -->
      <div v-if="step === 'draw'" class="instruction">
        <div class="step-number">1</div>
        <div class="step-text">在地图上框选新增工业区范围</div>
      </div>

      <!-- 已选择的区域信息 -->
      <div v-if="selectedArea" class="area-info">
        <div class="info-label">已选区域</div>
        <div class="info-value">
          中心: {{ selectedArea.center.lat.toFixed(3) }}°N, {{ selectedArea.center.lon.toFixed(3) }}°E
        </div>
        <div class="info-value">
          面积: ~{{ selectedArea.areaKm2 }} km²
        </div>
      </div>

      <!-- 情景参数设置 -->
      <div v-if="step === 'config'" class="params-section">
        <div class="param-group">
          <label class="param-label">排放强度倍数</label>
          <div class="param-control">
            <button @click="adjustEmission(-0.5)" class="param-btn">-</button>
            <span class="param-value">{{ emissionMultiplier }}x</span>
            <button @click="adjustEmission(0.5)" class="param-btn">+</button>
          </div>
          <div class="param-hint">相对于当前排放的倍数</div>
        </div>

        <div class="param-group">
          <label class="param-label">预测年限</label>
          <select v-model="predictionYears" class="param-select">
            <option :value="1">1 年后</option>
            <option :value="3">3 年后</option>
            <option :value="5">5 年后</option>
          </select>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <button
          v-if="step === 'idle' || step === 'result'"
          @click="startDrawing"
          class="btn btn-primary"
        >
          🖊️ 绘制新增工业区
        </button>

        <button
          v-if="step === 'draw'"
          @click="confirmArea"
          :disabled="!selectedArea"
          class="btn btn-success"
          :class="{ disabled: !selectedArea }"
        >
          ✓ 确认区域
        </button>

        <button
          v-if="step === 'draw'"
          @click="cancelDrawing"
          class="btn btn-secondary"
        >
          ✕ 取消
        </button>

        <button
          v-if="step === 'config'"
          @click="runScenario"
          :disabled="loading"
          class="btn btn-primary"
        >
          {{ loading ? '⏳ 推演中...' : '🚀 开始推演' }}
        </button>

        <button
          v-if="step === 'config'"
          @click="redrawArea"
          class="btn btn-secondary"
        >
          ← 重新绘制
        </button>

        <button
          v-if="step === 'result'"
          @click="reset"
          class="btn btn-secondary"
        >
          🔄 新建情景
        </button>
      </div>

      <!-- 推演结果摘要 -->
      <div v-if="result" class="result-summary">
        <div class="summary-title">推演结果</div>
        <div class="summary-item">
          <span class="summary-label">区域平均 GPP 变化</span>
          <span class="summary-value" :class="result.gppChange >= 0 ? 'positive' : 'negative'">
            {{ result.gppChange >= 0 ? '+' : '' }}{{ result.gppChange.toFixed(2) }} gC/m²/year
          </span>
        </div>
        <div class="summary-item">
          <span class="summary-label">碳汇影响</span>
          <span class="summary-value" :class="result.carbonImpact >= 0 ? 'positive' : 'negative'">
            {{ result.carbonImpact >= 0 ? '提升' : '下降' }} {{ Math.abs(result.carbonImpact).toFixed(1) }}%
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { getScenarioNodeIds, runScenarioRequest } from '../api/scenario.js'

// 组件状态
const visible = ref(false)
const step = ref('idle') // idle | draw | config | result
const loading = ref(false)

// 情景参数
const selectedArea = ref(null)
const emissionMultiplier = ref(5.0) // 排放强度倍数
const predictionYears = ref(3) // 预测年限

// 推演结果
const result = ref(null)

// 计算属性
const statusText = computed(() => {
  switch (step.value) {
    case 'idle': return '等待操作'
    case 'draw': return '正在绘制...'
    case 'config': return '参数配置'
    case 'result': return '推演完成'
    default: return ''
  }
})

const statusClass = computed(() => {
  switch (step.value) {
    case 'idle': return 'status-idle'
    case 'draw': return 'status-drawing'
    case 'config': return 'status-config'
    case 'result': return 'status-result'
    default: return ''
  }
})

// 方法
function open() {
  visible.value = true
  reset()
}

function close() {
  visible.value = false
  exitDrawingMode()
}

function reset() {
  step.value = 'idle'
  selectedArea.value = null
  emissionMultiplier.value = 5.0
  predictionYears.value = 3
  result.value = null
  exitDrawingMode()
}

function startDrawing() {
  exitDrawingMode()
  step.value = 'draw'
  selectedArea.value = null
  // 通知 CesiumViewer 进入绘制模式
  window.dispatchEvent(new CustomEvent('enter-drawing-mode'))
}

function redrawArea() {
  startDrawing()
}

function cancelDrawing() {
  step.value = 'idle'
  exitDrawingMode()
}

function confirmArea() {
  if (selectedArea.value) {
    step.value = 'config'
    exitDrawingMode()
  }
}

function exitDrawingMode() {
  window.dispatchEvent(new CustomEvent('exit-drawing-mode'))
}

function adjustEmission(delta) {
  const newValue = emissionMultiplier.value + delta
  emissionMultiplier.value = Math.max(1, Math.min(20, newValue))
}

async function runScenario() {
  loading.value = true

  try {
    const nodeIds = await getScenarioNodeIds(selectedArea.value.bounds)
    if (nodeIds.length === 0) {
      throw new Error('No grid nodes found in the selected area.')
    }

    const scenarioPayload = {
      preset: 'industrial_expansion',
      intensity: Number(emissionMultiplier.value),
      node_ids: nodeIds,
      graph_propagation: {
        hops: 2,
        attenuation: 0.65,
        blend_mode: 'sum',
      },
      temporal_profile: predictionYears.value > 1
        ? {
            mode: 'linear',
            start_weight: 0.35,
            end_weight: 1.0,
          }
        : {
            mode: 'last',
          },
    }

    result.value = await runScenarioRequest(scenarioPayload, emissionMultiplier.value)

    // 通知主组件显示对比视图
    window.dispatchEvent(new CustomEvent('scenario-result', {
      detail: result.value
    }))

    step.value = 'result'
  } catch (error) {
    console.error('情景推演失败:', error)
    // 使用模拟结果（开发阶段）
    const mockOriginalData = generateMockGridData(1.0)
    const mockScenarioData = generateMockGridData(emissionMultiplier.value)

    result.value = {
      originalData: mockOriginalData,
      scenarioData: mockScenarioData,
      gppChange: -1.8,
      carbonImpact: -15.2,
      emissionMultiplier: emissionMultiplier.value
    }

    // 通知主组件显示对比视图
    window.dispatchEvent(new CustomEvent('scenario-result', {
      detail: result.value
    }))

    step.value = 'result'
  } finally {
    loading.value = false
  }
}

// 生成模拟网格数据
function generateMockGridData(multiplier) {
  const grid = []
  const latStart = 31.7
  const lonStart = 118.6
  const step = 0.02
  const rows = 25
  const cols = 25

  for (let i = 0; i < rows; i++) {
    for (let j = 0; j < cols; j++) {
      const lat = latStart + i * step
      const lon = lonStart + j * step

      // 基础 GPP
      let baseGPP = 3

      // 紫金山森林区
      if (i > 15 && j > 15 && i < 23 && j < 23) {
        baseGPP = 7
      }
      // 主城区
      else if (i >= 8 && i <= 18 && j >= 8 && j <= 18) {
        baseGPP = 1
      }
      // 长江和玄武湖
      else if (i < 8 || (i > 18 && j > 18)) {
        baseGPP = 0.5
      }
      // 其他郊区
      else {
        baseGPP = 4
      }

      // 根据倍数调整（倍数越高，GPP越低）
      const adjustedGPP = baseGPP / (1 + (multiplier - 1) * 0.15)

      grid.push({
        lat,
        lon,
        gpp: Math.round(adjustedGPP * 100) / 100
      })
    }
  }

  return { date: '2020-Q2', grid }
}

// 处理区域选择事件
function handleAreaSelected(event) {
  selectedArea.value = event.detail
}

onMounted(() => {
  window.addEventListener('area-selected', handleAreaSelected)
})

onUnmounted(() => {
  window.removeEventListener('area-selected', handleAreaSelected)
})

defineExpose({ open, close })
</script>

<style scoped>
.scenario-panel {
  position: fixed;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  width: 320px;
  background: rgba(20, 25, 30, 0.95);
  backdrop-filter: blur(15px);
  border-radius: 12px;
  border: 1px solid rgba(76, 175, 80, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  z-index: 1500;
  color: white;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.panel-title {
  font-weight: 600;
  font-size: 16px;
}

.close-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.panel-content {
  padding: 20px;
}

/* 状态显示 */
.status-section {
  margin-bottom: 20px;
}

.status-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 8px;
}

.status-value {
  padding: 10px 15px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  text-align: center;
}

.status-idle {
  background: rgba(255, 255, 255, 0.1);
}

.status-drawing {
  background: rgba(33, 150, 243, 0.2);
  color: #64B5F6;
}

.status-config {
  background: rgba(255, 193, 7, 0.2);
  color: #FFC107;
}

.status-result {
  background: rgba(76, 175, 80, 0.2);
  color: #4CAF50;
}

/* 操作提示 */
.instruction {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px;
  background: rgba(33, 150, 243, 0.1);
  border: 1px solid rgba(33, 150, 243, 0.3);
  border-radius: 8px;
  margin-bottom: 20px;
}

.step-number {
  width: 28px;
  height: 28px;
  background: #2196F3;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
  flex-shrink: 0;
}

.step-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
}

/* 区域信息 */
.area-info {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
}

.info-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 10px;
}

.info-value {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 5px;
}

/* 参数设置 */
.params-section {
  margin-bottom: 20px;
}

.param-group {
  margin-bottom: 20px;
}

.param-label {
  display: block;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 10px;
}

.param-control {
  display: flex;
  align-items: center;
  gap: 15px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  padding: 10px 15px;
}

.param-btn {
  width: 32px;
  height: 32px;
  background: rgba(76, 175, 80, 0.2);
  border: 1px solid rgba(76, 175, 80, 0.5);
  border-radius: 6px;
  color: #4CAF50;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.param-btn:hover {
  background: rgba(76, 175, 80, 0.3);
}

.param-value {
  flex: 1;
  text-align: center;
  font-size: 18px;
  font-weight: 600;
  color: #4CAF50;
}

.param-hint {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  margin-top: 8px;
}

.param-select {
  width: 100%;
  padding: 12px 15px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  font-size: 14px;
  cursor: pointer;
}

.param-select:focus {
  outline: none;
  border-color: #4CAF50;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.btn {
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #45a049, #3d8b40);
  transform: translateY(-1px);
}

.btn-success {
  background: linear-gradient(135deg, #2196F3, #1976D2);
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: linear-gradient(135deg, #1976D2, #1565C0);
  transform: translateY(-1px);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.15);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 推演结果 */
.result-summary {
  margin-top: 20px;
  padding: 15px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
}

.summary-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 15px;
  color: rgba(255, 255, 255, 0.9);
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 13px;
}

.summary-label {
  color: rgba(255, 255, 255, 0.6);
}

.summary-value {
  font-weight: 600;
}

.summary-value.positive {
  color: #4CAF50;
}

.summary-value.negative {
  color: #FF5252;
}
</style>
