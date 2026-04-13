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
    default: '预测季度',
  },
})

const emit = defineEmits(['update:modelValue'])

const currentIndex = computed(() => {
  const index = props.options.findIndex((item) => item === props.modelValue)
  return index >= 0 ? index : 0
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
      <span class="timeline-value">{{ modelValue || '未选择' }}</span>
    </div>

    <input
      class="timeline-slider"
      type="range"
      :min="0"
      :max="Math.max(options.length - 1, 0)"
      :value="currentIndex"
      :disabled="options.length <= 1"
      @input="onInput"
    />

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
  width: min(560px, calc(100vw - 180px));
  padding: 18px 24px;
  z-index: 18;
}

.timeline-header,
.timeline-meta {
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
  color: var(--brand-eco);
  font-weight: 700;
}

.timeline-slider {
  width: 100%;
  margin: 14px 0 12px;
  accent-color: var(--brand-eco);
}

@media (max-width: 900px) {
  .timeline-container {
    width: calc(100vw - 32px);
  }
}
</style>
