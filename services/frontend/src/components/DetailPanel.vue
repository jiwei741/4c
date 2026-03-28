<template>
    <div v-if="visible" class="detail-panel" :style="{ left: x + 'px', top: y + 'px' }">
      <div class="panel-header">
        <span class="panel-title">📍 碳汇详情</span>
        <button class="close-btn" @click="close">×</button>
      </div>
      <div class="panel-content">
        <div class="info-row">
          <span class="label">经纬度</span>
          <span class="value">{{ data.lat?.toFixed(4) }}°N, {{ data.lon?.toFixed(4) }}°E</span>
        </div>
        <div class="info-row">
          <span class="label">GPP 值</span>
          <span class="value" :class="getGppClass(data.gpp)">{{ data.gpp }} gC/m²/year</span>
        </div>
        <div class="info-row">
          <span class="label">植被类型</span>
          <span class="value">{{ getVegetationType(data.gpp) }}</span>
        </div>
        <div class="chart-container">
          <div class="chart-title">NDVI 时序变化</div>
          <div class="chart-placeholder">
            <div class="chart-bars">
              <div v-for="i in 12" :key="i" class="bar" :style="{ height: getBarHeight(i) }"></div>
            </div>
            <div class="chart-labels">
              <span>1月</span>
              <span>6月</span>
              <span>12月</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, onUnmounted } from 'vue'
  
  const visible = ref(false)
  const x = ref(100)
  const y = ref(100)
  const data = ref({})
  
  function show(pointData, screenX, screenY) {
    data.value = pointData
    x.value = screenX
    y.value = screenY
    visible.value = true
  }
  
  function close() {
    visible.value = false
  }
  
  function getGppClass(gpp) {
    if (gpp >= 6) return 'gpp-high'
    if (gpp >= 3) return 'gpp-medium'
    return 'gpp-low'
  }
  
  function getVegetationType(gpp) {
    if (gpp >= 6) return '🌲 森林（高碳汇）'
    if (gpp >= 3) return '🌾 农田/草地（中等碳汇）'
    if (gpp >= 1) return '🏢 城镇（低碳汇）'
    return '💧 水体（极低碳汇）'
  }
  
  function getBarHeight(month) {
    // 模拟季节变化：夏季高，冬季低
    const baseHeight = 30 + Math.sin((month - 3) * Math.PI / 6) * 50 + Math.random() * 20
    return baseHeight + '%'
  }
  
  onMounted(() => {
    window.addEventListener('point-selected', handlePointSelected)
  })
  
  onUnmounted(() => {
    window.removeEventListener('point-selected', handlePointSelected)
  })
  
  function handlePointSelected(event) {
    show(event.detail, event.clientX || 300, event.clientY || 200)
  }
  
  defineExpose({ show, close })
  </script>
  
  <style scoped>
  .detail-panel {
    position: fixed;
    background: rgba(20, 25, 30, 0.95);
    backdrop-filter: blur(15px);
    border-radius: 12px;
    border: 1px solid rgba(76, 175, 80, 0.3);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    min-width: 280px;
    z-index: 2000;
    color: white;
  }
  
  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .panel-title {
    font-weight: 600;
    font-size: 15px;
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
    padding: 16px;
  }
  
  .info-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 12px;
    font-size: 13px;
  }
  
  .label {
    color: rgba(255, 255, 255, 0.6);
  }
  
  .value {
    font-weight: 500;
  }
  
  .gpp-high { color: #4CAF50; }
  .gpp-medium { color: #FFC107; }
  .gpp-low { color: #FF5722; }
  
  .chart-container {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .chart-title {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.6);
    margin-bottom: 12px;
  }
  
  .chart-placeholder {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 8px;
    padding: 12px;
  }
  
  .chart-bars {
    display: flex;
    gap: 4px;
    align-items: flex-end;
    height: 60px;
  }
  
  .bar {
    flex: 1;
    background: linear-gradient(to top, #4CAF50, #81C784);
    border-radius: 3px 3px 0 0;
    min-height: 20%;
    transition: height 0.3s;
  }
  
  .chart-labels {
    display: flex;
    justify-content: space-between;
    margin-top: 8px;
    font-size: 10px;
    color: rgba(255, 255, 255, 0.4);
  }
  </style>
  