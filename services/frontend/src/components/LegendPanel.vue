<template>
    <div class="legend-panel">
      <div class="legend-header">🌍 碳汇强度</div>
      <div class="legend-items">
        <div class="legend-item">
          <div class="legend-color high"></div>
          <span class="legend-label">8+ 高碳汇</span>
        </div>
        <div class="legend-item">
          <div class="legend-color medium-high"></div>
          <span class="legend-label">5-8 中高碳汇</span>
        </div>
        <div class="legend-item">
          <div class="legend-color medium"></div>
          <span class="legend-label">2-5 中等碳汇</span>
        </div>
        <div class="legend-item">
          <div class="legend-color low"></div>
          <span class="legend-label">0-2 低碳汇</span>
        </div>
      </div>
      <div class="legend-unit">单位: gC/m²/year</div>
    </div>
  </template>
  
  <style scoped>
  .legend-panel {
    position: fixed;
    top: 100px;
    right: 20px;
    background: rgba(20, 25, 30, 0.9);
    backdrop-filter: blur(10px);
    border-radius: 10px;
    border: 1px solid rgba(76, 175, 80, 0.3);
    padding: 15px;
    min-width: 150px;
    z-index: 1000;
    color: white;
  }
  
  .legend-header {
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 12px;
    text-align: center;
    opacity: 0.9;
  }
  
  .legend-items {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .legend-item {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  
  .legend-color {
    width: 24px;
    height: 16px;
    border-radius: 3px;
  }
  
  .high {
    background: linear-gradient(90deg, #4CAF50, #81C784);
  }
  
  .medium-high {
    background: linear-gradient(90deg, #CDDC39, #FFEB3B);
  }
  
  .medium {
    background: linear-gradient(90deg, #FF9800, #FFC107);
  }
  
  .low {
    background: linear-gradient(90deg, #F44336, #FF5722);
  }
  
  .legend-label {
    font-size: 12px;
    opacity: 0.8;
  }
  
  .legend-unit {
    margin-top: 10px;
    font-size: 10px;
    text-align: center;
    opacity: 0.5;
    border-top: 1px solid rgba(255,255,255,0.1);
    padding-top: 8px;
  }
  </style>
  