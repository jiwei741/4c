<template>
  <div class="workspace-header">
    <div class="workspace-header__brand">
      <div>
        <p class="workspace-header__eyebrow">区域碳汇监测、预测与情景推演决策支持平台</p>
        <h1>天穹智算 <span>Spatio-Eco</span></h1>
      </div>
      <p class="workspace-header__lead">
        以南京研究区为样本，组织多源季度数据、图时序预测与区域干预推演，形成可迁移的研究区工作台。
      </p>
    </div>

    <div class="workspace-header__actions">
      <RouterLink class="workspace-link" to="/">首页总览</RouterLink>
      <RouterLink class="workspace-link" to="/evidence">模型结果</RouterLink>
      <button class="workspace-scenario-btn" @click="$emit('open-scenario')">启动情景推演</button>
    </div>

    <div class="workspace-header__status">
      <div class="status-pill">
        <span class="label">研究区</span>
        <span class="value">{{ studyArea }}</span>
      </div>
      <div class="status-pill">
        <span class="label">当前季度</span>
        <span class="value">{{ currentDate }}</span>
      </div>
      <div class="status-pill">
        <span class="label">默认模型</span>
        <span class="value">{{ defaultModel }}</span>
      </div>
      <div class="status-pill">
        <span class="label">预测窗口</span>
        <span class="value">{{ forecastWindow }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'

defineProps({
  currentDate: {
    type: String,
    default: '2025-Q1',
  },
  studyArea: {
    type: String,
    default: '南京研究区',
  },
  defaultModel: {
    type: String,
    default: 'ST-GNN Multi-Step',
  },
  forecastWindow: {
    type: String,
    default: '2025-Q1 至 2025-Q2',
  },
})

defineEmits(['open-scenario'])
</script>

<style scoped>
.workspace-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 30;
  display: grid;
  grid-template-columns: 1.3fr auto;
  gap: 14px;
  padding: 14px 24px 12px;
  background: linear-gradient(180deg, rgba(4, 14, 23, 0.94), rgba(4, 14, 23, 0.66));
  backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.workspace-header__brand {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.workspace-header__eyebrow {
  color: var(--brand-amber);
  font-size: 11px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.workspace-header h1 {
  font-size: 24px;
  line-height: 1.15;
}

.workspace-header h1 span {
  color: var(--brand-sea);
  font-size: 15px;
  margin-left: 10px;
}

.workspace-header__lead {
  max-width: 620px;
  color: var(--text-secondary);
  font-size: 13px;
}

.workspace-header__actions {
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  gap: 10px;
  flex-wrap: wrap;
}

.workspace-link,
.workspace-scenario-btn {
  min-height: 42px;
  padding: 0 16px;
  border-radius: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border-soft);
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-primary);
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
}

.workspace-scenario-btn {
  background: linear-gradient(135deg, var(--brand-eco), #84daa8);
  color: #082216;
  font-weight: 700;
  border: none;
}

.workspace-header__status {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.status-pill {
  padding: 10px 12px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.status-pill .label {
  display: block;
  font-size: 11px;
  color: var(--text-muted);
}

.status-pill .value {
  display: block;
  margin-top: 6px;
  font-size: 14px;
  font-weight: 600;
}

@media (max-width: 1024px) {
  .workspace-header {
    grid-template-columns: 1fr;
    padding: 14px 16px 12px;
  }

  .workspace-header__actions {
    justify-content: flex-start;
  }

  .workspace-header__status {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .workspace-header__status {
    grid-template-columns: 1fr;
  }
}
</style>
