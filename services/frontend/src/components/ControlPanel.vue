<template>
    <div class="control-panel">
      <button class="control-btn" @click="resetView" title="重置视图">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
          <path d="M3 3v5h5"/>
        </svg>
      </button>
      <button class="control-btn" @click="toggleFullscreen" title="全屏">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/>
        </svg>
      </button>
      <button class="control-btn" @click="toggleLayer" title="切换图层">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="12 2 2 7 12 12 22 7 12 2"/>
          <polyline points="2 17 12 22 22 17"/>
          <polyline points="2 12 12 17 22 12"/>
        </svg>
      </button>
    </div>
  </template>
  
  <script setup>
  const props = defineProps({
    viewer: Object
  })
  
  const emit = defineEmits(['reset-view', 'toggle-layer'])
  
  function resetView() {
    emit('reset-view')
  }
  
  function toggleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen()
    } else {
      document.exitFullscreen()
    }
  }
  
  function toggleLayer() {
    emit('toggle-layer')
  }
  </script>
  
  <style scoped>
  .control-panel {
    position: fixed;
    top: 100px;
    left: 20px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    z-index: 1000;
  }
  
  .control-btn {
    width: 40px;
    height: 40px;
    background: rgba(20, 25, 30, 0.9);
    border: 1px solid rgba(76, 175, 80, 0.3);
    border-radius: 8px;
    color: #4CAF50;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s;
  }
  
  .control-btn:hover {
    background: rgba(76, 175, 80, 0.2);
    transform: scale(1.05);
  }
  
  .control-btn:active {
    transform: scale(0.95);
  }
  </style>
  