<template>
  <div :class="['platform-preview', `platform-preview--${mode}`, { 'platform-preview--compact': compact }]">
    <div class="platform-preview__ambient"></div>
    <div class="platform-preview__hud platform-preview__hud--top">
      <span class="platform-preview__brand">{{ headerLabel }}</span>
      <span class="platform-preview__status">{{ modeLabel }}</span>
    </div>

    <aside class="platform-preview__rail">
      <span></span>
      <span></span>
      <span></span>
    </aside>

    <div class="platform-preview__map-shell">
      <div class="platform-preview__map-grid"></div>
      <div class="platform-preview__cells">
        <span
          v-for="cell in cells"
          :key="cell.id"
          class="platform-preview__cell"
          :class="[`platform-preview__cell--${cell.tone}`, `platform-preview__cell--${cell.size}`]"
          :style="{ left: `${cell.x}%`, top: `${cell.y}%` }"
        ></span>
      </div>

      <div class="platform-preview__selection"></div>
      <div class="platform-preview__pulse"></div>
      <div class="platform-preview__focus-card glass-fake">
        <small>{{ focusLabel }}</small>
        <strong>{{ focusValue }}</strong>
        <span>{{ focusHint }}</span>
      </div>

      <div class="platform-preview__legend glass-fake">
        <div v-for="item in legendItems" :key="item.label" class="platform-preview__legend-item">
          <span :style="{ background: item.color }"></span>
          <small>{{ item.label }}</small>
        </div>
      </div>

      <div class="platform-preview__timeline glass-fake">
        <div class="platform-preview__timeline-head">
          <small>{{ timelineLabel }}</small>
          <strong>{{ timelineValue }}</strong>
        </div>
        <div class="platform-preview__timeline-track">
          <span></span>
        </div>
        <div class="platform-preview__timeline-scale">
          <small>{{ timelineStart }}</small>
          <small>{{ timelineEnd }}</small>
        </div>
      </div>
    </div>

    <div class="platform-preview__floating platform-preview__floating--left glass-fake">
      <small>{{ floatingLeftLabel }}</small>
      <strong>{{ floatingLeftValue }}</strong>
    </div>

    <div class="platform-preview__floating platform-preview__floating--right glass-fake">
      <small>{{ floatingRightLabel }}</small>
      <strong>{{ floatingRightValue }}</strong>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  mode: {
    type: String,
    default: 'workspace',
  },
  compact: {
    type: Boolean,
    default: false,
  },
})

const cells = [
  { id: 1, x: 16, y: 20, tone: 'soft', size: 'sm' },
  { id: 2, x: 22, y: 18, tone: 'warm', size: 'md' },
  { id: 3, x: 28, y: 24, tone: 'warm', size: 'sm' },
  { id: 4, x: 34, y: 21, tone: 'soft', size: 'md' },
  { id: 5, x: 40, y: 17, tone: 'cool', size: 'sm' },
  { id: 6, x: 46, y: 24, tone: 'warm', size: 'lg' },
  { id: 7, x: 52, y: 19, tone: 'soft', size: 'sm' },
  { id: 8, x: 59, y: 25, tone: 'warm', size: 'md' },
  { id: 9, x: 66, y: 22, tone: 'warm', size: 'sm' },
  { id: 10, x: 24, y: 35, tone: 'cool', size: 'sm' },
  { id: 11, x: 31, y: 39, tone: 'warm', size: 'md' },
  { id: 12, x: 39, y: 34, tone: 'soft', size: 'sm' },
  { id: 13, x: 47, y: 41, tone: 'warm', size: 'lg' },
  { id: 14, x: 55, y: 37, tone: 'soft', size: 'sm' },
  { id: 15, x: 62, y: 41, tone: 'warm', size: 'md' },
  { id: 16, x: 70, y: 36, tone: 'cool', size: 'sm' },
  { id: 17, x: 20, y: 55, tone: 'soft', size: 'sm' },
  { id: 18, x: 28, y: 60, tone: 'warm', size: 'md' },
  { id: 19, x: 36, y: 54, tone: 'soft', size: 'sm' },
  { id: 20, x: 45, y: 61, tone: 'warm', size: 'lg' },
  { id: 21, x: 54, y: 56, tone: 'warm', size: 'md' },
  { id: 22, x: 63, y: 60, tone: 'soft', size: 'sm' },
  { id: 23, x: 72, y: 55, tone: 'cool', size: 'sm' },
]

const legendItems = [
  { label: '高值区', color: '#ff8a5b' },
  { label: '重点区', color: '#f4c15a' },
  { label: '稳态区', color: '#8ccf7a' },
  { label: '背景区', color: '#4bb0d6' },
]

const modeLabel = computed(() => (props.mode === 'evidence' ? '结果视图' : '工作台预览'))
const headerLabel = computed(() => (props.mode === 'evidence' ? '模型结果概览' : '研究区工作台'))
const focusLabel = computed(() => (props.mode === 'evidence' ? '结果摘要' : '当前季度'))
const focusValue = computed(() => (props.mode === 'evidence' ? '空间分布与结果概览' : '2025-Q1'))
const focusHint = computed(() => (props.mode === 'evidence' ? '结合误差与稳定性理解结果' : '历史与预测结果可统一切换'))
const timelineLabel = computed(() => (props.mode === 'evidence' ? '结果时间轴' : '季度时间轴'))
const timelineValue = computed(() => (props.mode === 'evidence' ? '历史季度 + 预测季度' : '2020-Q1 至 2025-Q2'))
const timelineStart = computed(() => '2020-Q1')
const timelineEnd = computed(() => (props.mode === 'evidence' ? '结果解读' : '2025-Q2'))
const floatingLeftLabel = computed(() => (props.mode === 'evidence' ? '地图联动' : '历史回看'))
const floatingLeftValue = computed(() => (props.mode === 'evidence' ? '按空间分布查看结果' : '季度分布切换'))
const floatingRightLabel = computed(() => (props.mode === 'evidence' ? '结果判断' : '情景推演'))
const floatingRightValue = computed(() => (props.mode === 'evidence' ? '误差、稳定性与使用建议' : '框选区域，对比变化'))
</script>

<style scoped>
.platform-preview {
  position: relative;
  aspect-ratio: 1.14;
  border-radius: 28px;
  overflow: hidden;
  background:
    radial-gradient(circle at 18% 18%, rgba(68, 184, 155, 0.28), transparent 28%),
    radial-gradient(circle at 78% 24%, rgba(46, 125, 206, 0.2), transparent 30%),
    linear-gradient(165deg, rgba(11, 32, 49, 0.95), rgba(6, 16, 27, 0.98));
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06), 0 28px 80px rgba(2, 8, 15, 0.38);
}

.platform-preview--compact {
  aspect-ratio: 1.32;
  border-radius: 24px;
}

.platform-preview__ambient {
  position: absolute;
  inset: -12%;
  background:
    radial-gradient(circle at 50% 50%, rgba(78, 191, 127, 0.08), transparent 34%),
    radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.05), transparent 62%);
  filter: blur(16px);
}

.platform-preview__hud,
.platform-preview__floating,
.platform-preview__focus-card,
.platform-preview__legend,
.platform-preview__timeline,
.platform-preview__rail {
  position: absolute;
  z-index: 2;
}

.platform-preview__hud--top {
  left: 18px;
  right: 18px;
  top: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: rgba(232, 242, 248, 0.86);
  font-size: 12px;
  letter-spacing: 0.08em;
}

.platform-preview__brand {
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(20, 54, 78, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.platform-preview__status {
  padding: 7px 11px;
  border-radius: 999px;
  background: rgba(83, 198, 132, 0.15);
  border: 1px solid rgba(125, 217, 161, 0.22);
}

.platform-preview__rail {
  left: 18px;
  top: 92px;
  display: grid;
  gap: 8px;
}

.platform-preview__rail span {
  width: 11px;
  height: 11px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(94, 225, 165, 0.88), rgba(67, 177, 217, 0.9));
  box-shadow: 0 0 18px rgba(70, 186, 179, 0.25);
}

.platform-preview__map-shell {
  position: absolute;
  inset: 58px 26px 26px 52px;
  border-radius: 24px;
  overflow: hidden;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.03), transparent 28%),
    radial-gradient(circle at 48% 46%, rgba(250, 199, 92, 0.08), transparent 26%),
    linear-gradient(180deg, rgba(12, 38, 54, 0.98), rgba(8, 20, 32, 0.98));
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.platform-preview__map-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
  background-size: 52px 52px, 52px 52px;
  mask-image: linear-gradient(180deg, rgba(255, 255, 255, 0.82), rgba(255, 255, 255, 0.25));
}

.platform-preview__cells {
  position: absolute;
  inset: 0;
}

.platform-preview__cell {
  position: absolute;
  transform: translate(-50%, -50%);
  border-radius: 16px;
  opacity: 0.92;
  filter: saturate(1.08);
}

.platform-preview__cell--sm {
  width: 24px;
  height: 24px;
}

.platform-preview__cell--md {
  width: 34px;
  height: 34px;
}

.platform-preview__cell--lg {
  width: 48px;
  height: 48px;
}

.platform-preview__cell--warm {
  background: radial-gradient(circle at 35% 35%, rgba(255, 248, 222, 0.9), rgba(255, 136, 91, 0.94));
  box-shadow: 0 0 20px rgba(255, 138, 91, 0.24);
}

.platform-preview__cell--soft {
  background: radial-gradient(circle at 35% 35%, rgba(246, 255, 244, 0.9), rgba(143, 213, 123, 0.92));
  box-shadow: 0 0 20px rgba(102, 198, 131, 0.2);
}

.platform-preview__cell--cool {
  background: radial-gradient(circle at 35% 35%, rgba(235, 252, 255, 0.9), rgba(77, 179, 214, 0.9));
  box-shadow: 0 0 18px rgba(77, 179, 214, 0.18);
}

.platform-preview__selection {
  position: absolute;
  left: 42%;
  top: 28%;
  width: 28%;
  height: 34%;
  border: 2px solid rgba(111, 235, 170, 0.9);
  border-radius: 24px;
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.08), 0 0 42px rgba(111, 235, 170, 0.18);
  background: linear-gradient(180deg, rgba(111, 235, 170, 0.08), rgba(111, 235, 170, 0.03));
}

.platform-preview__selection::before,
.platform-preview__selection::after {
  content: '';
  position: absolute;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 0 12px rgba(255, 255, 255, 0.2);
}

.platform-preview__selection::before {
  left: -5px;
  top: -5px;
}

.platform-preview__selection::after {
  right: -5px;
  bottom: -5px;
}

.platform-preview__pulse {
  position: absolute;
  left: 52%;
  top: 46%;
  width: 96px;
  height: 96px;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  border: 2px solid rgba(255, 173, 92, 0.68);
  box-shadow: 0 0 0 16px rgba(255, 173, 92, 0.06), 0 0 44px rgba(255, 173, 92, 0.12);
}

.platform-preview__focus-card {
  left: 18px;
  bottom: 18px;
  max-width: 190px;
}

.platform-preview__legend {
  top: 18px;
  right: 18px;
  min-width: 132px;
}

.platform-preview__timeline {
  left: 50%;
  bottom: 18px;
  transform: translateX(-50%);
  width: min(58%, 320px);
}

.platform-preview__floating--left {
  left: 6px;
  bottom: 74px;
  max-width: 170px;
}

.platform-preview__floating--right {
  right: 6px;
  top: 88px;
  max-width: 180px;
}

.glass-fake {
  display: grid;
  gap: 8px;
  padding: 14px 16px;
  border-radius: 20px;
  background: rgba(8, 24, 38, 0.78);
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(18px);
  box-shadow: 0 16px 38px rgba(1, 7, 14, 0.28);
}

.glass-fake small {
  color: rgba(211, 225, 233, 0.68);
  font-size: 11px;
  letter-spacing: 0.04em;
}

.glass-fake strong {
  color: #f4f7fb;
  font-size: 16px;
  line-height: 1.35;
}

.glass-fake span {
  color: rgba(215, 225, 232, 0.8);
  font-size: 12px;
  line-height: 1.45;
}

.platform-preview__legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.platform-preview__legend-item span {
  width: 10px;
  height: 10px;
  border-radius: 3px;
  flex: none;
}

.platform-preview__timeline-head,
.platform-preview__timeline-scale {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.platform-preview__timeline-track {
  position: relative;
  height: 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  overflow: hidden;
}

.platform-preview__timeline-track span {
  position: absolute;
  inset: 0 22% 0 0;
  border-radius: inherit;
  background: linear-gradient(90deg, rgba(90, 196, 219, 0.88), rgba(123, 220, 161, 0.92));
  box-shadow: 0 0 16px rgba(95, 203, 179, 0.2);
}

.platform-preview--compact .platform-preview__floating,
.platform-preview--compact .platform-preview__rail {
  display: none;
}

.platform-preview--compact .platform-preview__map-shell {
  inset: 54px 20px 20px 22px;
}

.platform-preview--compact .platform-preview__timeline {
  width: min(66%, 280px);
}

@media (max-width: 900px) {
  .platform-preview {
    aspect-ratio: 1.02;
  }

  .platform-preview__floating--right {
    top: auto;
    bottom: 120px;
  }

  .platform-preview__timeline {
    width: min(70%, 260px);
  }
}
</style>
