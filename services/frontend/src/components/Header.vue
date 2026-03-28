<template>
  <div class="header">
    <div class="header-content">
      <div class="title-section">
        <h1 class="project-name">天穹智算 <span class="english-name">Spatio-Eco</span></h1>
        <p class="project-subtitle">区域碳汇时空溯源与演化流式计算平台</p>
      </div>
      <div class="info-section">
        <span class="info-item">研究区域：南京市</span>
        <span class="info-item" id="current-date-display">当前：{{ currentDate }}</span>
        <button class="scenario-btn" @click="$emit('open-scenario')">
          🔬 情景推演
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  currentDate: {
    type: String,
    default: '2023-06-01'
  }
})

defineEmits(['open-scenario'])
</script>

<style scoped>
.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: linear-gradient(135deg, rgba(0,0,0,0.85) 0%, rgba(20,40,20,0.85) 100%);
  backdrop-filter: blur(10px);
  padding: 15px 30px;
  z-index: 1000;
  border-bottom: 1px solid rgba(76, 175, 80, 0.3);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.project-name {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: 2px;
}

.english-name {
  font-size: 18px;
  font-weight: 400;
  color: #4CAF50;
  margin-left: 10px;
}

.project-subtitle {
  margin: 0;
  font-size: 13px;
  color: rgba(255,255,255,0.7);
}

.info-section {
  display: flex;
  gap: 20px;
  align-items: center;
}

.info-item {
  font-size: 14px;
  color: rgba(255,255,255,0.8);
  background: rgba(76, 175, 80, 0.15);
  padding: 6px 15px;
  border-radius: 20px;
  border: 1px solid rgba(76, 175, 80, 0.3);
}

.scenario-btn {
  font-size: 14px;
  color: white;
  background: linear-gradient(135deg, #4CAF50, #45a049);
  padding: 8px 20px;
  border-radius: 20px;
  border: none;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.scenario-btn:hover {
  background: linear-gradient(135deg, #45a049, #3d8b40);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
}
</style>
