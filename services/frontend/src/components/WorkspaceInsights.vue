<template>
  <aside class="insights-panel glass-card">
    <section>
      <div class="insights-panel__title">
        <strong>工作台解释栏</strong>
        <small>{{ selectedHorizon || '加载中' }}</small>
      </div>
      <p class="insights-panel__lead">
        当前视图基于正式多步模型预测结果，结合对比模型差异，用于识别热点区、稳态区与重点干预区。
      </p>
    </section>

    <section class="insights-panel__stats" v-if="analyticsSummary">
      <div class="insight-block">
        <span>稳定区</span>
        <strong>{{ analyticsSummary.category_counts?.stable ?? 0 }}</strong>
      </div>
      <div class="insight-block">
        <span>重点关注</span>
        <strong>{{ analyticsSummary.category_counts?.elevated ?? 0 }}</strong>
      </div>
      <div class="insight-block">
        <span>高敏感区</span>
        <strong>{{ analyticsSummary.category_counts?.high ?? 0 }}</strong>
      </div>
      <div class="insight-block">
        <span>关键热点</span>
        <strong>{{ analyticsSummary.category_counts?.critical ?? 0 }}</strong>
      </div>
    </section>

    <section>
      <div class="section-head">
        <strong>热点节点</strong>
        <small>优先分析与展示</small>
      </div>
      <ul class="rank-list">
        <li v-for="item in hotspots" :key="item.node_id">
          <span>节点 {{ item.node_id }}</span>
          <strong>{{ Number(item.value).toFixed(4) }}</strong>
        </li>
      </ul>
    </section>

    <section>
      <div class="section-head">
        <strong>模型摘要</strong>
        <small>当前默认多步模型</small>
      </div>
      <ul class="summary-list">
        <li>
          <span>模型名称</span>
          <strong>{{ modelName }}</strong>
        </li>
        <li>
          <span>RMSE</span>
          <strong>{{ formatMetric(modelMetrics?.rmse) }}</strong>
        </li>
        <li>
          <span>MAE</span>
          <strong>{{ formatMetric(modelMetrics?.mae) }}</strong>
        </li>
        <li>
          <span>研究区节点</span>
          <strong>{{ nodeCount }}</strong>
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
})

const analyticsSummary = computed(() => props.analytics?.summary || null)
const hotspots = computed(() => analyticsSummary.value?.top_hotspots?.slice(0, 5) || [])
const modelName = computed(() => props.dashboard?.prediction_preview?.model_name || 'ST-GNN Multi-Step')
const modelMetrics = computed(() => {
  const models = props.dashboard?.models || []
  return models.find((item) => item.key === props.dashboard?.default_models?.multi_step)?.metrics || null
})
const nodeCount = computed(() => props.dashboard?.project?.study_area?.node_count || 309)

function formatMetric(value) {
  return Number.isFinite(Number(value)) ? Number(value).toFixed(4) : '--'
}
</script>

<style scoped>
.insights-panel {
  position: fixed;
  top: 204px;
  right: 20px;
  width: 300px;
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

@media (max-width: 1100px) {
  .insights-panel {
    display: none;
  }
}
</style>
