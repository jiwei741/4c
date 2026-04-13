<template>
  <div class="legend-panel glass-card">
    <div class="legend-header">
      <span>碳汇强度分级</span>
      <small>单位：净碳通量预测值</small>
    </div>
    <div class="legend-items">
      <div v-for="item in items" :key="item.label" class="legend-item">
        <span class="legend-color" :style="{ background: item.color }"></span>
        <div>
          <strong>{{ item.label }}</strong>
          <small>{{ item.hint }}</small>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const items = [
  { label: '高潜力', hint: '区域碳汇能力相对较强', color: 'linear-gradient(135deg, #76db9b, #1c7d56)' },
  { label: '重点关注', hint: '处于中高水平但存在波动', color: 'linear-gradient(135deg, #a8d672, #d2a739)' },
  { label: '承压区', hint: '受建成区或排放扰动影响明显', color: 'linear-gradient(135deg, #e2a554, #ba6d39)' },
  { label: '脆弱区', hint: '需优先评估生态修复或减排策略', color: 'linear-gradient(135deg, #f19473, #b74739)' },
]
</script>

<style scoped>
.legend-panel {
  position: fixed;
  right: 20px;
  bottom: 126px;
  width: 260px;
  padding: 18px;
  z-index: 16;
}

.legend-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 14px;
}

.legend-header small,
.legend-item small {
  color: var(--text-muted);
}

.legend-items {
  display: grid;
  gap: 12px;
}

.legend-item {
  display: grid;
  grid-template-columns: 20px 1fr;
  gap: 12px;
  align-items: center;
}

.legend-color {
  width: 20px;
  height: 54px;
  border-radius: 999px;
}

.legend-item strong {
  display: block;
  font-size: 14px;
}

@media (max-width: 1100px) {
  .legend-panel {
    display: none;
  }
}
</style>
