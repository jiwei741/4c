<template>
  <div class="control-panel glass-card">
    <button class="control-btn" @click="emit('reset-view')">
      <span>重置视图</span>
      <small>返回研究区全域</small>
    </button>
    <button class="control-btn" @click="toggleFullscreen">
      <span>全屏演示</span>
      <small>适合答辩投屏</small>
    </button>
    <button class="control-btn" @click="emit('toggle-layer')">
      <span>切换图层</span>
      <small>显示或隐藏预测强度层</small>
    </button>
  </div>
</template>

<script setup>
const emit = defineEmits(['reset-view', 'toggle-layer'])

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
    return
  }

  document.exitFullscreen()
}
</script>

<style scoped>
.control-panel {
  position: fixed;
  left: 20px;
  bottom: 124px;
  width: 240px;
  padding: 14px;
  display: grid;
  gap: 10px;
  z-index: 16;
}

.control-btn {
  text-align: left;
  padding: 14px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-primary);
  cursor: pointer;
}

.control-btn span,
.control-btn small {
  display: block;
}

.control-btn small {
  color: var(--text-muted);
  margin-top: 4px;
}

@media (max-width: 1100px) {
  .control-panel {
    position: fixed;
    left: 16px;
    bottom: 110px;
    width: calc(100vw - 32px);
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 780px) {
  .control-panel {
    grid-template-columns: 1fr;
  }
}
</style>
