<template>
  <div v-if="visible" class="scenario-panel glass-card">
    <div class="scenario-panel__header">
      <div>
        <strong>情景推演</strong>
        <small>框选区域并模拟未来季度变化</small>
      </div>
      <button class="scenario-panel__close" @click="close">×</button>
    </div>

    <div class="scenario-panel__content">
      <div class="status-section">
        <span class="status-label">当前状态</span>
        <strong :class="statusClass">{{ statusText }}</strong>
      </div>

      <div v-if="step === 'draw'" class="instruction-card">
        <span class="instruction-step">01</span>
        <p>请在地图上拖拽框选待分析区域，系统将自动换算对应节点集合。</p>
      </div>

      <div v-if="selectedArea" class="area-card">
        <div>
          <span class="area-card__label">框选中心</span>
          <strong>{{ selectedArea.center.lat.toFixed(3) }}°N / {{ selectedArea.center.lon.toFixed(3) }}°E</strong>
        </div>
        <div>
          <span class="area-card__label">估算面积</span>
          <strong>{{ selectedArea.areaKm2 }} km²</strong>
        </div>
      </div>

      <div v-if="step === 'config'" class="param-section">
        <div class="param-card">
          <label>排放强度倍数</label>
          <div class="param-control">
            <button @click="adjustEmission(-0.5)">-</button>
            <strong>{{ emissionMultiplier.toFixed(1) }}x</strong>
            <button @click="adjustEmission(0.5)">+</button>
          </div>
          <small>用于模拟工业扩张或排放压力加剧带来的区域扰动。</small>
        </div>

        <div class="param-card">
          <label>时间配置</label>
          <select v-model="predictionYears">
            <option :value="1">短期演化（1 年）</option>
            <option :value="3">中期演化（3 年）</option>
            <option :value="5">长期演化（5 年）</option>
          </select>
          <small>时间越长，图结构扩散和特征扰动的累计影响越明显。</small>
        </div>
      </div>

      <div class="action-row">
        <button v-if="step === 'idle' || step === 'result'" class="primary-btn" @click="startDrawing">开始框选</button>
        <button v-if="step === 'draw'" class="primary-btn" :disabled="!selectedArea" @click="confirmArea">确认区域</button>
        <button v-if="step === 'draw'" class="ghost-btn" @click="cancelDrawing">取消</button>
        <button v-if="step === 'config'" class="primary-btn" :disabled="loading" @click="runScenario">
          {{ loading ? '推演中...' : '运行推演' }}
        </button>
        <button v-if="step === 'config'" class="ghost-btn" @click="redrawArea">重新框选</button>
        <button v-if="step === 'result'" class="ghost-btn" @click="reset">新建情景</button>
      </div>

      <div v-if="result" class="result-card">
        <div class="result-card__head">
          <strong>推演摘要</strong>
          <small>{{ result.forecastHorizon || '最新预测窗' }}</small>
        </div>
        <div class="result-item">
          <span>区域平均变化</span>
          <strong :class="result.gppChange >= 0 ? 'positive' : 'negative'">
            {{ result.gppChange >= 0 ? '+' : '' }}{{ result.gppChange.toFixed(4) }}
          </strong>
        </div>
        <div class="result-item">
          <span>碳汇影响比例</span>
          <strong :class="result.carbonImpact >= 0 ? 'positive' : 'negative'">
            {{ result.carbonImpact >= 0 ? '+' : '' }}{{ result.carbonImpact.toFixed(2) }}%
          </strong>
        </div>
        <div class="result-item">
          <span>受影响节点</span>
          <strong>{{ result.backendSummary?.changed_nodes?.length || 0 }}</strong>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { getScenarioNodeIds, runScenarioRequest } from '../api/scenario.js'

const visible = ref(false)
const step = ref('idle')
const loading = ref(false)
const selectedArea = ref(null)
const emissionMultiplier = ref(5.0)
const predictionYears = ref(3)
const result = ref(null)

const statusText = computed(() => {
  const mapping = {
    idle: '等待操作',
    draw: '框选区域中',
    config: '配置参数中',
    result: '推演完成',
  }
  return mapping[step.value] || '等待操作'
})

const statusClass = computed(() => ({
  'status-idle': step.value === 'idle',
  'status-draw': step.value === 'draw',
  'status-config': step.value === 'config',
  'status-result': step.value === 'result',
}))

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
  window.dispatchEvent(new CustomEvent('scenario-cleared'))
  exitDrawingMode()
}

function startDrawing() {
  window.dispatchEvent(new CustomEvent('scenario-cleared'))
  exitDrawingMode()
  step.value = 'draw'
  selectedArea.value = null
  window.dispatchEvent(new CustomEvent('enter-drawing-mode'))
}

function redrawArea() {
  startDrawing()
}

function cancelDrawing() {
  step.value = 'idle'
  window.dispatchEvent(new CustomEvent('scenario-cleared'))
  exitDrawingMode()
}

function confirmArea() {
  if (!selectedArea.value) return
  step.value = 'config'
  exitDrawingMode()
}

function exitDrawingMode() {
  window.dispatchEvent(new CustomEvent('exit-drawing-mode'))
}

function adjustEmission(delta) {
  const next = emissionMultiplier.value + delta
  emissionMultiplier.value = Math.max(1, Math.min(20, next))
}

async function runScenario() {
  if (!selectedArea.value) return

  loading.value = true
  try {
    console.log('[ScenarioPanel] Getting node IDs for bounds:', selectedArea.value.bounds)
    const nodeIds = await getScenarioNodeIds(selectedArea.value.bounds)
    console.log('[ScenarioPanel] Got node IDs:', nodeIds)

    if (nodeIds.length === 0) {
      throw new Error('Selected area does not contain mapped grid nodes.')
    }

    const scenarioPayload = {
      model_key: 'stgnn_multistep_hybrid',
      preset: 'industrial_expansion',
      intensity: Number(emissionMultiplier.value),
      node_ids: nodeIds,
      graph_propagation: {
        hops: 2,
        attenuation: 0.65,
        blend_mode: 'sum',
      },
      temporal_profile:
        predictionYears.value > 1
          ? {
              mode: 'linear',
              start_weight: 0.35,
              end_weight: 1.0,
            }
          : {
              mode: 'last',
            },
    }
    console.log('[ScenarioPanel] Scenario payload:', scenarioPayload)

    result.value = await runScenarioRequest(scenarioPayload, emissionMultiplier.value)
    console.log('[ScenarioPanel] Scenario result:', result.value)

    window.dispatchEvent(new CustomEvent('scenario-result', { detail: result.value }))
    step.value = 'result'
  } catch (error) {
    console.error('[ScenarioPanel] Scenario run failed:', error)
    step.value = 'config'
  } finally {
    loading.value = false
  }
}

function handleAreaSelected(event) {
  console.log('[ScenarioPanel] area-selected event received:', event.detail)
  selectedArea.value = event.detail
}

onMounted(() => {
  console.log('[ScenarioPanel] Mounted, adding area-selected event listener')
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
  top: calc(var(--workspace-header-offset, 296px) + 16px);
  width: 350px;
  max-height: calc(100vh - var(--workspace-header-offset, 296px) - 32px);
  overflow: auto;
  padding: 20px;
  z-index: 35;
}

.scenario-panel__header,
.result-card__head,
.status-section,
.result-item,
.param-control,
.area-card,
.action-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.scenario-panel__header {
  align-items: flex-start;
}

.scenario-panel__header small,
.status-label,
.area-card__label,
.param-card small,
.result-card__head small {
  color: var(--text-muted);
}

.scenario-panel__close {
  width: 34px;
  height: 34px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-primary);
  cursor: pointer;
}

.scenario-panel__content {
  margin-top: 18px;
  display: grid;
  gap: 16px;
}

.status-section {
  align-items: center;
}

.status-idle { color: var(--text-secondary); }
.status-draw { color: var(--brand-amber); }
.status-config { color: var(--brand-sea); }
.status-result { color: var(--brand-eco); }

.instruction-card,
.area-card,
.param-card,
.result-card {
  padding: 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.instruction-card {
  display: grid;
  grid-template-columns: 40px 1fr;
  gap: 14px;
}

.instruction-step {
  font-size: 22px;
  font-weight: 700;
  color: var(--brand-amber);
}

.area-card,
.action-row,
.result-item {
  align-items: center;
}

.area-card {
  flex-direction: column;
  align-items: stretch;
}

.area-card strong,
.param-card label,
.result-card strong {
  display: block;
}

.param-section {
  display: grid;
  gap: 14px;
}

.param-card label {
  margin-bottom: 12px;
  font-weight: 700;
}

.param-card button,
.param-card select {
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-primary);
  min-height: 40px;
  padding: 0 14px;
}

.param-control {
  align-items: center;
  margin-bottom: 10px;
}

.action-row {
  flex-wrap: wrap;
}

.result-card {
  display: grid;
  gap: 12px;
}

@media (max-width: 900px) {
  .scenario-panel {
    left: 16px;
    top: auto;
    bottom: 16px;
    transform: none;
    width: calc(100vw - 32px);
  }
}
</style>
