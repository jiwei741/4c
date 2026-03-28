<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: '2020-Q2'
  }
})

const emit = defineEmits(['update:modelValue'])

// 当前滑块位置（索引）
const currentIndex = ref(0)

// 定义可用的时间列表（2020-2024年，按季度）
const availableDates = [
  '2020-Q1', '2020-Q2', '2020-Q3', '2020-Q4',
  '2021-Q1', '2021-Q2', '2021-Q3', '2021-Q4',
  '2022-Q1', '2022-Q2', '2022-Q3', '2022-Q4',
  '2023-Q1', '2023-Q2', '2023-Q3', '2023-Q4',
  '2024-Q1', '2024-Q2', '2024-Q3', '2024-Q4'
]

// 组件挂载时设置初始索引
onMounted(() => {
  const index = availableDates.findIndex(d => d === props.modelValue)
  currentIndex.value = index >= 0 ? index : Math.floor(availableDates.length / 2)
  if (index < 0) {
    emit('update:modelValue', availableDates[currentIndex.value])
  }
})

// 滑块拖动事件
function onInput(event) {
  const newIndex = parseInt(event.target.value)
  currentIndex.value = newIndex
  emit('update:modelValue', availableDates[newIndex])
}
</script>

<template>
  <div class="timeline-container">
    <div class="timeline-header">
      <span class="date-label">时间:</span>
      <span class="date-value">{{ modelValue }}</span>
    </div>

    <input
      type="range"
      :min="0"
      :max="availableDates.length - 1"
      :value="currentIndex"
      @input="onInput"
      class="timeline-slider"
    />

    <div class="timeline-labels">
      <span>{{ availableDates[0] }}</span>
      <span>{{ availableDates[availableDates.length - 1] }}</span>
    </div>
  </div>
</template>

<style scoped>
.timeline-container {
  position: fixed;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.7);
  padding: 15px 25px;
  border-radius: 10px;
  color: white;
  min-width: 350px;
}

.timeline-header {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 10px;
}

.date-label {
  opacity: 0.7;
}

.date-value {
  font-weight: bold;
  color: #4CAF50;
}

.timeline-slider {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: #444;
  outline: none;
  -webkit-appearance: none;
}

.timeline-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #4CAF50;
  cursor: pointer;
}

.timeline-slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #4CAF50;
  cursor: pointer;
  border: none;
}

.timeline-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  opacity: 0.6;
}
</style>
