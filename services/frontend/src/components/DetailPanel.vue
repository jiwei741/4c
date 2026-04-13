<template>
  <div v-if="visible" class="detail-panel glass-card" :style="positionStyle">
    <div class="detail-panel__header">
      <div>
        <strong>节点详情</strong>
        <small>点击地图热区后显示</small>
      </div>
      <button class="detail-panel__close" @click="close">×</button>
    </div>

    <div class="detail-panel__body">
      <div class="detail-row">
        <span>节点编号</span>
        <strong>{{ data.nodeId || '未知' }}</strong>
      </div>
      <div class="detail-row">
        <span>经纬度</span>
        <strong>{{ formatCoord(data.lat) }}°N / {{ formatCoord(data.lon) }}°E</strong>
      </div>
      <div class="detail-row">
        <span>预测值</span>
        <strong :class="valueClass">{{ formatValue(data.gpp) }}</strong>
      </div>
      <div class="detail-row" v-if="data.riskLevel">
        <span>风险分级</span>
        <strong>{{ riskText }}</strong>
      </div>
      <div class="detail-row" v-if="data.comparisonGap !== undefined && data.comparisonGap !== null">
        <span>相对基线变化</span>
        <strong :class="data.comparisonGap >= 0 ? 'positive' : 'negative'">
          {{ data.comparisonGap >= 0 ? '+' : '' }}{{ data.comparisonGap.toFixed(4) }}
        </strong>
      </div>

      <div class="detail-meter">
        <div class="detail-meter__track">
          <div class="detail-meter__fill" :style="{ width: meterWidth }"></div>
        </div>
        <div class="detail-meter__labels">
          <span>低</span>
          <span>中</span>
          <span>高</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'

const visible = ref(false)
const x = ref(100)
const y = ref(100)
const data = ref({})

const positionStyle = computed(() => ({
  left: `${Math.max(16, x.value)}px`,
  top: `${Math.max(180, y.value)}px`,
}))

const valueClass = computed(() => {
  if ((data.value.gpp || 0) >= 0.2) return 'positive'
  if ((data.value.gpp || 0) <= 0.05) return 'negative'
  return 'neutral'
})

const meterWidth = computed(() => {
  const value = Number(data.value.riskScore ?? data.value.gpp ?? 0)
  const normalized = Math.max(0, Math.min(1, value))
  return `${Math.round(normalized * 100)}%`
})

const riskText = computed(() => {
  const mapping = {
    stable: '稳定区',
    elevated: '重点关注区',
    high: '高敏感区',
    critical: '关键热点区',
  }
  return mapping[data.value.riskLevel] || '未分级'
})

function formatCoord(value) {
  return Number.isFinite(Number(value)) ? Number(value).toFixed(4) : '--'
}

function formatValue(value) {
  return Number.isFinite(Number(value)) ? `${Number(value).toFixed(4)}` : '--'
}

function show(pointData, screenX, screenY) {
  data.value = pointData || {}
  x.value = screenX
  y.value = screenY
  visible.value = true
}

function close() {
  visible.value = false
}

function handlePointSelected(event) {
  const detail = event.detail || {}
  const { screenX = 320, screenY = 240, ...pointData } = detail
  show(pointData, screenX, screenY)
}

onMounted(() => {
  window.addEventListener('point-selected', handlePointSelected)
})

onUnmounted(() => {
  window.removeEventListener('point-selected', handlePointSelected)
})

defineExpose({ show, close })
</script>

<style scoped>
.detail-panel {
  position: fixed;
  width: 320px;
  padding: 18px;
  z-index: 40;
}

.detail-panel__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.detail-panel__header small {
  display: block;
  color: var(--text-muted);
  margin-top: 4px;
}

.detail-panel__close {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-primary);
  cursor: pointer;
}

.detail-panel__body {
  margin-top: 16px;
  display: grid;
  gap: 14px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: var(--text-secondary);
}

.detail-row strong {
  color: var(--text-primary);
}

.positive {
  color: #8ee0a4;
}

.negative {
  color: #ff9d7b;
}

.neutral {
  color: var(--brand-amber);
}

.detail-meter {
  display: grid;
  gap: 8px;
}

.detail-meter__track {
  height: 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  overflow: hidden;
}

.detail-meter__fill {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--brand-sea), var(--brand-amber), var(--brand-coral));
}

.detail-meter__labels {
  display: flex;
  justify-content: space-between;
  color: var(--text-muted);
  font-size: 12px;
}

@media (max-width: 900px) {
  .detail-panel {
    width: calc(100vw - 32px);
    left: 16px !important;
    top: auto !important;
    bottom: 24px;
  }
}
</style>
