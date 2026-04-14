<template>
  <aside class="insights-panel glass-card">
    <section>
      <div class="insights-panel__title">
        <strong>{{ panelTitle }}</strong>
        <small>{{ selectedHorizon || '加载中' }}</small>
      </div>
      <p class="insights-panel__lead">
        {{ leadText }}
      </p>
    </section>

    <section class="insights-panel__stats" v-if="displayStats.length">
      <div v-for="item in displayStats" :key="item.label" class="insight-block">
        <span>{{ item.label }}</span>
        <strong :class="item.tone || ''">{{ item.value }}</strong>
      </div>
    </section>

    <section>
      <div class="section-head">
        <strong>{{ primaryListTitle }}</strong>
        <small>{{ primaryListHint }}</small>
      </div>
      <ul class="rank-list">
        <li v-for="item in primaryList" :key="item.key">
          <span>{{ item.label }}</span>
          <strong :class="item.tone || ''">{{ item.value }}</strong>
        </li>
      </ul>
    </section>

    <section>
      <div class="section-head">
        <strong>{{ summaryTitle }}</strong>
        <small>{{ summaryHint }}</small>
      </div>
      <ul class="summary-list">
        <li v-for="item in summaryItems" :key="item.label">
          <span>{{ item.label }}</span>
          <strong :class="item.tone || ''">{{ item.value }}</strong>
        </li>
      </ul>
    </section>
  </aside>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  analytics: {
    type: Object,
    default: null,
  },
  dashboard: {
    type: Object,
    default: null,
  },
  selectedHorizon: {
    type: String,
    default: '',
  },
  selectedHorizonType: {
    type: String,
    default: 'forecast',
  },
  scenarioResult: {
    type: Object,
    default: null,
  },
})

const analyticsSummary = computed(() => props.analytics?.summary || null)
const hotspots = computed(() => analyticsSummary.value?.top_hotspots?.slice(0, 5) || [])
const modelName = computed(() => props.dashboard?.prediction_preview?.model_name || 'ST-GNN Multi-Step')
const modelMetrics = computed(() => {
  const models = props.dashboard?.models || []
  return models.find((item) => item.key === props.dashboard?.default_models?.multi_step)?.metrics || null
})
const nodeCount = computed(() => props.dashboard?.project?.study_area?.node_count || 309)
const isScenarioView = computed(() => {
  return Boolean(props.scenarioResult?.forecastHorizon) && props.scenarioResult.forecastHorizon === props.selectedHorizon
})

const scenarioTopImpacts = computed(() => {
  const items = props.scenarioResult?.backendSummary?.top_impacts || []
  return items.slice(0, 5).map((item) => ({
    key: `impact-${item.node_id}`,
    label: `节点 ${item.node_id}`,
    value: formatMetric(item.value),
    tone: Number(item.value) >= 0 ? 'positive' : 'negative',
  }))
})

const scenarioFeatureDeltas = computed(() => {
  const values = props.scenarioResult?.backendSummary?.feature_deltas || {}
  return Object.entries(values)
    .slice(0, 4)
    .map(([label, value]) => ({
      label,
      value: `${Number(value) >= 0 ? '+' : ''}${Number(value).toFixed(3)}`,
      tone: Number(value) >= 0 ? 'positive' : 'negative',
    }))
})

const panelTitle = computed(() => (isScenarioView.value ? '情景结果摘要' : '工作台解释栏'))

const leadText = computed(() => {
  if (isScenarioView.value) {
    return '当前视图已经切换到推演后的地图结果，右侧展示的是本次干预对目标季度空间分布、受影响节点和关键特征扰动的摘要。'
  }

  if (props.selectedHorizonType === 'historical') {
    return '当前视图展示的是历史季度标签结果，用于回看研究区在既有季度中的空间分布和热点变化。'
  }

  return '当前视图展示的是正式多步模型预测结果，结合对比模型差异，用于识别热点区、稳态区与重点干预区。'
})

const displayStats = computed(() => {
  if (isScenarioView.value) {
    const result = props.scenarioResult || {}
    const changedNodeCount = result.backendSummary?.changed_nodes?.length || 0
    return [
      { label: '区域平均变化', value: signedMetric(result.gppChange), tone: Number(result.gppChange) >= 0 ? 'positive' : 'negative' },
      { label: '碳汇影响比例', value: `${signedMetric(result.carbonImpact, 2)}%`, tone: Number(result.carbonImpact) >= 0 ? 'positive' : 'negative' },
      { label: '受影响节点', value: String(changedNodeCount) },
      { label: '干预倍数', value: `${Number(result.emissionMultiplier || 0).toFixed(1)}x` },
    ]
  }

  if (!analyticsSummary.value) return []
  return [
    { label: '稳定区', value: String(analyticsSummary.value.category_counts?.stable ?? 0) },
    { label: '重点关注', value: String(analyticsSummary.value.category_counts?.elevated ?? 0) },
    { label: '高敏感区', value: String(analyticsSummary.value.category_counts?.high ?? 0) },
    { label: '关键热点', value: String(analyticsSummary.value.category_counts?.critical ?? 0) },
  ]
})

const primaryListTitle = computed(() => (isScenarioView.value ? '变化最强节点' : '热点节点'))
const primaryListHint = computed(() => (isScenarioView.value ? '按绝对影响排序' : '优先分析与展示'))

const primaryList = computed(() => {
  if (isScenarioView.value) {
    return scenarioTopImpacts.value
  }

  return hotspots.value.map((item) => ({
    key: `hotspot-${item.node_id}`,
    label: `节点 ${item.node_id}`,
    value: formatMetric(item.value),
  }))
})

const summaryTitle = computed(() => (isScenarioView.value ? '关键特征扰动' : '模型摘要'))
const summaryHint = computed(() => (isScenarioView.value ? '来自正式推演结果' : '当前默认多步模型'))

const summaryItems = computed(() => {
  if (isScenarioView.value) {
    const forecastHorizon = props.scenarioResult?.forecastHorizon || '最新预测窗'
    const changedNodes = props.scenarioResult?.backendSummary?.changed_nodes || []
    const featureItems = scenarioFeatureDeltas.value

    return [
      { label: '推演季度', value: forecastHorizon },
      { label: '受影响节点', value: changedNodes.length ? changedNodes.join('、') : '未返回' },
      ...featureItems,
    ]
  }

  return [
    { label: '模型名称', value: modelName.value },
    { label: 'RMSE', value: formatMetric(modelMetrics.value?.rmse) },
    { label: 'MAE', value: formatMetric(modelMetrics.value?.mae) },
    { label: '研究区节点', value: String(nodeCount.value) },
  ]
})

function formatMetric(value) {
  return Number.isFinite(Number(value)) ? Number(value).toFixed(4) : '--'
}

function signedMetric(value, digits = 4) {
  if (!Number.isFinite(Number(value))) return '--'
  const numeric = Number(value)
  return `${numeric >= 0 ? '+' : ''}${numeric.toFixed(digits)}`
}
</script>

<style scoped>
.insights-panel {
  position: fixed;
  top: calc(var(--workspace-header-offset, 296px) + 16px);
  right: 20px;
  width: 320px;
  max-height: calc(100vh - var(--workspace-header-offset, 296px) - 32px);
  overflow: auto;
  padding: 18px;
  z-index: 17;
  display: grid;
  gap: 18px;
}

.insights-panel__title {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.insights-panel__title small,
.section-head small,
.insights-panel__lead,
.summary-list span,
.rank-list span {
  color: var(--text-muted);
}

.insights-panel__lead {
  margin-top: 10px;
  font-size: 13px;
}

.insights-panel__stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.insight-block {
  padding: 12px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.insight-block span {
  display: block;
  color: var(--text-muted);
  font-size: 12px;
}

.insight-block strong {
  display: block;
  margin-top: 6px;
  font-size: 24px;
}

.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.rank-list,
.summary-list {
  display: grid;
  gap: 10px;
  list-style: none;
  padding: 0;
  margin: 0;
}

.rank-list li,
.summary-list li {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.rank-list li:last-child,
.summary-list li:last-child {
  border-bottom: none;
}

.positive {
  color: #8ee0a4;
}

.negative {
  color: #ff9d7b;
}

@media (max-width: 1100px) {
  .insights-panel {
    display: none;
  }
}
</style>
