<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  options: {
    type: Array,
    default: () => [],
  },
  label: {
    type: String,
    default: '历史与预测季度',
  },
  historicalOptions: {
    type: Array,
    default: () => [],
  },
  forecastOptions: {
    type: Array,
    default: () => [],
  },
  horizonType: {
    type: String,
    default: 'forecast',
  },
})

const emit = defineEmits(['update:modelValue'])

const currentIndex = computed(() => {
  const index = props.options.findIndex((item) => item === props.modelValue)
  return index >= 0 ? index : 0
})

const historyCount = computed(() => props.historicalOptions.length)
const forecastCount = computed(() => props.forecastOptions.length)
const splitPercent = computed(() => {
  const total = props.options.length
  if (total <= 1 || historyCount.value <= 0 || forecastCount.value <= 0) {
    return 100
  }
  return (historyCount.value / total) * 100
})
const progressPercent = computed(() => {
  const total = Math.max(props.options.length - 1, 1)
  return (currentIndex.value / total) * 100
})
const selectionTone = computed(() => (props.horizonType === 'historical' ? 'is-historical' : 'is-forecast'))

const trackStyle = computed(() => {
  const split = splitPercent.value
  return {
    background: `linear-gradient(90deg, rgba(79, 191, 127, 0.28) 0%, rgba(79, 191, 127, 0.28) ${split}%, rgba(240, 193, 107, 0.32) ${split}%, rgba(240, 193, 107, 0.32) 100%)`,
  }
})

const progressStyle = computed(() => {
  const accent =
    props.horizonType === 'historical'
      ? 'linear-gradient(90deg, rgba(79, 191, 127, 0.9), rgba(111, 230, 180, 0.95))'
      : 'linear-gradient(90deg, rgba(240, 193, 107, 0.92), rgba(255, 157, 123, 0.95))'

  return {
    width: `${progressPercent.value}%`,
    background: accent,
  }
})

function onInput(event) {
  const next = props.options[Number(event.target.value)]
  if (next) {
    emit('update:modelValue', next)
  }
}
</script>

<template>
  <div class="timeline-container glass-card">
    <div class="timeline-header">
      <span class="timeline-label">{{ label }}</span>
      <span class="timeline-value" :class="selectionTone">{{ modelValue || '未选择' }}</span>
    </div>

    <div class="timeline-legend">
      <span class="legend-chip legend-chip--history">
        历史季度
        <strong>{{ historicalOptions[0] || '起点' }} - {{ historicalOptions[historicalOptions.length - 1] || '终点' }}</strong>
      </span>
      <span class="legend-chip legend-chip--forecast">
        预测季度
        <strong>{{ forecastOptions[0] || '起点' }} - {{ forecastOptions[forecastOptions.length - 1] || '终点' }}</strong>
      </span>
    </div>

    <div class="timeline-track-shell">
      <div class="timeline-track timeline-track--zones" :style="trackStyle"></div>
      <div class="timeline-track timeline-track--progress" :style="progressStyle"></div>
      <input
        class="timeline-slider"
        type="range"
        :min="0"
        :max="Math.max(options.length - 1, 0)"
        :value="currentIndex"
        :disabled="options.length <= 1"
        @input="onInput"
      />
      <span
        v-if="historyCount > 0 && forecastCount > 0"
        class="timeline-divider"
        :style="{ left: `${splitPercent}%` }"
      ></span>
    </div>

    <div class="timeline-meta">
      <span>{{ options[0] || '起始季度' }}</span>
      <span>{{ options[options.length - 1] || '结束季度' }}</span>
    </div>
  </div>
</template>

<style scoped>
.timeline-container {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  width: min(680px, calc(100vw - 180px));
  padding: 18px 24px 16px;
  z-index: 18;
}

.timeline-header,
.timeline-meta,
.timeline-legend {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.timeline-label,
.timeline-meta {
  color: var(--text-muted);
  font-size: 13px;
}

.timeline-value {
  font-weight: 700;
}

.timeline-value.is-historical {
  color: var(--brand-eco);
}

.timeline-value.is-forecast {
  color: var(--brand-amber);
}

.timeline-legend {
  margin-top: 12px;
  flex-wrap: wrap;
}

.legend-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  font-size: 12px;
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.legend-chip strong {
  font-size: 12px;
  color: var(--text-primary);
}

.legend-chip--history {
  box-shadow: inset 0 0 0 1px rgba(79, 191, 127, 0.18);
}

.legend-chip--forecast {
  box-shadow: inset 0 0 0 1px rgba(240, 193, 107, 0.18);
}

.timeline-track-shell {
  position: relative;
  margin: 14px 0 12px;
  height: 22px;
  display: flex;
  align-items: center;
}

.timeline-track {
  position: absolute;
  left: 0;
  right: 0;
  height: 8px;
  border-radius: 999px;
  pointer-events: none;
}

.timeline-track--zones {
  background: rgba(255, 255, 255, 0.08);
}

.timeline-track--progress {
  right: auto;
  min-width: 8px;
  box-shadow: 0 0 18px rgba(79, 191, 127, 0.15);
}

.timeline-divider {
  position: absolute;
  top: 2px;
  bottom: 2px;
  width: 2px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.58);
  transform: translateX(-1px);
  pointer-events: none;
}

.timeline-slider {
  position: relative;
  z-index: 1;
  width: 100%;
  margin: 0;
  appearance: none;
  background: transparent;
}

.timeline-slider::-webkit-slider-runnable-track {
  height: 8px;
  background: transparent;
}

.timeline-slider::-webkit-slider-thumb {
  appearance: none;
  width: 18px;
  height: 18px;
  margin-top: -5px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.78);
  background: #ffffff;
  box-shadow: 0 0 0 4px rgba(79, 191, 127, 0.18);
  cursor: pointer;
}

.timeline-slider::-moz-range-track {
  height: 8px;
  background: transparent;
}

.timeline-slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.78);
  border-radius: 50%;
  background: #ffffff;
  box-shadow: 0 0 0 4px rgba(79, 191, 127, 0.18);
  cursor: pointer;
}

@media (max-width: 900px) {
  .timeline-container {
    width: calc(100vw - 32px);
  }
}
</style>
