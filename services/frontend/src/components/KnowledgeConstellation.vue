<template>
  <div class="knowledge-graph">
    <div class="knowledge-graph__head">
      <span class="brand-chip">动态知识谱系</span>
      <small>围绕研究区碳汇监测、季度预测与情景推演组织一体化分析链路</small>
    </div>

    <div class="knowledge-graph__canvas-shell">
      <div ref="chartRef" class="knowledge-graph__canvas"></div>
    </div>

    <div class="knowledge-graph__metrics">
      <div v-for="item in metrics" :key="item.label" class="knowledge-graph__metric">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { GraphChart } from 'echarts/charts'
import { TooltipComponent } from 'echarts/components'
import { init, use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'

use([GraphChart, TooltipComponent, CanvasRenderer])

const chartRef = ref(null)
let chart = null

const metrics = [
  { label: '历史季度', value: '2020-Q1 至 2024-Q4' },
  { label: '预测季度', value: '2025-Q1 至 2025-Q2' },
  { label: '分析方式', value: '地图 · 节点 · 情景对比' },
]

const palette = {
  core: '#5fd0d1',
  data: '#4bb0d6',
  history: '#7bd89b',
  prediction: '#f0c162',
  scenario: '#ff8a5b',
  result: '#8cb6ff',
}

function buildNodes(width, height) {
  const cx = width * 0.54
  const cy = height * 0.5

  return [
    {
      id: 'core',
      x: cx,
      y: cy,
      fixed: true,
      draggable: true,
      symbolSize: 148,
      itemStyle: {
        color: palette.core,
        shadowBlur: 42,
        shadowColor: 'rgba(95, 208, 209, 0.52)',
      },
      label: {
        show: true,
        formatter: '{title|区域碳汇}\n{title|时空分析}\n{caption|天穹智算}',
        rich: richLabel('#031018', '#0d4d66', 18, 12),
      },
      tooltip: {
        formatter: '系统核心：将历史分布、预测季度与情景推演统一到研究区工作台中。',
      },
    },
    node('data', '多源季度数据', '遥感 / 气象 / 排放代理', width * 0.2, height * 0.18, palette.data, 96),
    node('history', '历史分布回看', '按季度回看空间变化', width * 0.82, height * 0.18, palette.history, 96),
    node('scenario', '情景推演对比', '框选区域，比较前后差异', width * 0.15, height * 0.72, palette.scenario, 96),
    node('prediction', '预测季度切换', '统一查看未来季度结果', width * 0.86, height * 0.66, palette.prediction, 96),
    node('result', '模型结果理解', '误差、稳定性与使用建议', width * 0.46, height * 0.9, palette.result, 92),
  ]
}

function node(id, title, caption, x, y, color, size = 92) {
  return {
    id,
    x,
    y,
    draggable: true,
    symbolSize: size,
    itemStyle: {
      color,
      shadowBlur: 28,
      shadowColor: `${color}88`,
      borderColor: '#f8fbff',
      borderWidth: 1,
    },
    label: {
      show: true,
      formatter: `{title|${title}}\n{caption|${caption}}`,
      rich: richLabel('#061520', '#e2edf2', 15, 11),
    },
    tooltip: {
      formatter: `${title}<br/>${caption}`,
    },
  }
}

function richLabel(titleColor, captionColor, titleSize, captionSize) {
  return {
    title: {
      color: titleColor,
      fontSize: titleSize,
      fontWeight: 700,
      lineHeight: titleSize + 8,
      align: 'center',
      fontFamily: 'Microsoft YaHei',
    },
    caption: {
      color: captionColor,
      fontSize: captionSize,
      lineHeight: captionSize + 7,
      align: 'center',
      fontFamily: 'Microsoft YaHei',
    },
  }
}

function buildEdges() {
  return [
    edge('data', 'core', '#4bb0d6', 0.14),
    edge('history', 'core', '#7bd89b', -0.12),
    edge('scenario', 'core', '#ff8a5b', 0.18),
    edge('prediction', 'core', '#f0c162', -0.18),
    edge('result', 'core', '#8cb6ff', 0.06),
  ]
}

function edge(source, target, color, curveness) {
  return {
    source,
    target,
    lineStyle: {
      color,
      width: 2.6,
      curveness,
      opacity: 0.7,
    },
    emphasis: {
      lineStyle: {
        width: 4,
        opacity: 0.95,
      },
    },
  }
}

function renderChart() {
  if (!chartRef.value) return
  if (!chart) chart = init(chartRef.value)

  const width = chartRef.value.clientWidth
  const height = chartRef.value.clientHeight

  chart.setOption({
    animationDuration: 1400,
    animationDurationUpdate: 900,
    animationEasing: 'elasticOut',
    animationEasingUpdate: 'elasticOut',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(6, 19, 31, 0.94)',
      borderColor: 'rgba(255,255,255,0.08)',
      borderWidth: 1,
      textStyle: {
        color: '#edf4f8',
        fontSize: 13,
      },
    },
    series: [
      {
        type: 'graph',
        layout: 'force',
        roam: true,
        draggable: true,
        data: buildNodes(width, height),
        links: buildEdges(),
        edgeSymbol: ['none', 'arrow'],
        edgeSymbolSize: [0, 11],
        force: {
          repulsion: 360,
          edgeLength: [160, 240],
          gravity: 0.03,
          friction: 0.28,
          layoutAnimation: true,
        },
        lineStyle: {
          width: 2.6,
          opacity: 0.7,
        },
        label: {
          show: true,
          position: 'inside',
        },
        emphasis: {
          focus: 'adjacency',
          scale: 1.1,
          lineStyle: {
            width: 4,
            opacity: 0.95,
          },
        },
      },
    ],
  })
}

function handleResize() {
  chart?.resize()
  renderChart()
}

onMounted(() => {
  renderChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
  chart = null
})
</script>

<style scoped>
.knowledge-graph {
  display: grid;
  gap: 12px;
}

.knowledge-graph__head {
  display: grid;
  gap: 6px;
}

.knowledge-graph__head small {
  color: var(--text-muted);
  line-height: 1.6;
}

.knowledge-graph__canvas-shell {
  position: relative;
  min-height: 390px;
  overflow: hidden;
  border-radius: 32px;
  background:
    radial-gradient(circle at 20% 18%, rgba(75, 176, 214, 0.18), transparent 22%),
    radial-gradient(circle at 80% 22%, rgba(240, 193, 98, 0.12), transparent 24%),
    linear-gradient(165deg, rgba(8, 26, 40, 0.96), rgba(4, 14, 24, 0.98));
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.knowledge-graph__canvas-shell::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.04) 1px, transparent 1px);
  background-size: 46px 46px;
  mask-image: linear-gradient(180deg, rgba(255, 255, 255, 0.82), rgba(255, 255, 255, 0.24));
  pointer-events: none;
}

.knowledge-graph__canvas {
  position: relative;
  z-index: 1;
  width: 100%;
  min-height: 390px;
}

.knowledge-graph__metrics {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.knowledge-graph__metric {
  padding: 12px 14px;
  border-radius: 18px;
  background: rgba(7, 22, 35, 0.72);
  border: 1px solid rgba(255, 255, 255, 0.07);
}

.knowledge-graph__metric span {
  display: block;
  color: var(--text-muted);
  font-size: 12px;
}

.knowledge-graph__metric strong {
  display: block;
  margin-top: 6px;
  font-size: 16px;
}

@media (max-width: 980px) {
  .knowledge-graph__canvas-shell,
  .knowledge-graph__canvas {
    min-height: 380px;
  }
}

@media (max-width: 760px) {
  .knowledge-graph__canvas-shell,
  .knowledge-graph__canvas {
    min-height: 660px;
  }

  .knowledge-graph__metrics {
    grid-template-columns: 1fr;
  }
}
</style>
