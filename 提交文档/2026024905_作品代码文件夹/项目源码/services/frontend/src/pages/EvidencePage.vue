<template>
  <div class="page-shell page-shell--interactive evidence-page">
    <InteractiveBackdrop variant="evidence" />
    <SiteNavigation compact />

    <main class="page-section page-content-layer evidence-main">
      <section class="glass-card evidence-hero">
        <div>
          <span class="brand-chip">模型结果</span>
          <h1 class="section-title">查看当前平台结果的整体表现、稳定性和适用方式。</h1>
          <p class="section-lead">
            这一页帮助使用者快速了解平台当前结果的误差水平、整体稳定性，以及这些结果更适合用于哪些分析场景。
          </p>
        </div>
        <RouterLink class="primary-btn" to="/workspace">回到工作台</RouterLink>
      </section>

      <section class="metric-grid">
        <div class="metric-card">
          <span class="label">当前模型</span>
          <span class="value">{{ evidence?.current_result?.name || '加载中' }}</span>
          <span class="hint">工作台当前默认使用的结果来源</span>
        </div>
        <div class="metric-card">
          <span class="label">预测误差</span>
          <span class="value">{{ metricValue(evidence?.current_result?.metrics?.rmse) }}</span>
          <span class="hint">数值越低，预测偏差越小</span>
        </div>
        <div class="metric-card">
          <span class="label">平均误差</span>
          <span class="value">{{ metricValue(evidence?.current_result?.metrics?.mae) }}</span>
          <span class="hint">反映整体结果偏差</span>
        </div>
        <div class="metric-card">
          <span class="label">预测范围</span>
          <span class="value">{{ forecastWindow }}</span>
          <span class="hint">当前页面展示的季度范围</span>
        </div>
      </section>

      <section class="evidence-layout">
        <article class="glass-card evidence-panel">
          <div class="section-head">
            <strong>模型表现对比</strong>
            <small>用于说明当前平台结果的整体误差情况</small>
          </div>
          <div class="model-card-grid">
            <article v-for="item in evidence?.comparison_overview || []" :key="item.key" class="model-card">
              <div class="model-card__head">
                <div>
                  <strong>{{ item.name }}</strong>
                  <p>{{ item.role_label }}</p>
                </div>
                <span class="brand-chip brand-chip--small">RMSE {{ metricValue(item.metrics.rmse) }}</span>
              </div>
              <p class="model-card__desc">{{ item.role_description }}</p>
              <div class="model-card__metrics">
                <div>
                  <span>预测误差</span>
                  <strong>{{ metricValue(item.metrics.rmse) }}</strong>
                </div>
                <div>
                  <span>平均误差</span>
                  <strong>{{ metricValue(item.metrics.mae) }}</strong>
                </div>
              </div>
            </article>
          </div>
        </article>

        <article class="glass-card evidence-panel">
          <div class="section-head">
            <strong>结果稳定性</strong>
            <small>帮助判断当前结果是否足够稳定</small>
          </div>
          <ul class="summary-list">
            <li>
              <span>重复评估次数</span>
              <strong>{{ evidence?.stability_overview?.runs_evaluated ?? '--' }}</strong>
            </li>
            <li>
              <span>最佳误差</span>
              <strong>{{ metricValue(evidence?.stability_overview?.best_rmse) }}</strong>
            </li>
            <li>
              <span>平均误差</span>
              <strong>{{ metricValue(evidence?.stability_overview?.average_rmse) }}</strong>
            </li>
            <li>
              <span>误差波动</span>
              <strong>{{ metricValue(evidence?.stability_overview?.rmse_variation) }}</strong>
            </li>
          </ul>
          <p class="panel-note">{{ evidence?.stability_overview?.summary }}</p>
        </article>
      </section>

      <section class="evidence-layout">
        <article class="glass-card evidence-panel">
          <div class="section-head">
            <strong>如何理解这些结果</strong>
            <small>把页面中的误差信息转成可读结论</small>
          </div>
          <ul class="summary-list">
            <li>
              <span>预测误差</span>
              <strong>越低越好</strong>
            </li>
            <li>
              <span>平均误差</span>
              <strong>越低说明整体偏差越小</strong>
            </li>
            <li>
              <span>结果稳定性</span>
              <strong>波动越小，越适合作为长期展示结果</strong>
            </li>
            <li>
              <span>当前表现</span>
              <strong>{{ improvementText }}</strong>
            </li>
          </ul>
          <p class="panel-note">{{ evidence?.quality_overview?.summary }}</p>
        </article>

        <article class="glass-card evidence-panel evidence-panel--usage">
          <div class="section-head">
            <strong>这组结果适合做什么</strong>
            <small>帮助使用者判断当前结果更适合回答哪些问题</small>
          </div>
          <div class="usage-card-grid">
            <article
              v-for="(item, index) in evidence?.usage_guidance?.recommended_for || []"
              :key="item"
              class="usage-card"
            >
              <span class="usage-card__index">0{{ index + 1 }}</span>
              <strong>{{ item }}</strong>
              <p>{{ usageDescriptions[index] || defaultUsageDescription }}</p>
            </article>
          </div>

          <div class="usage-note-shell">
            <strong>查看结果时建议重点关注</strong>
            <ul class="tips-list">
              <li v-for="tip in evidence?.usage_guidance?.tips || []" :key="tip">{{ tip }}</li>
            </ul>
          </div>
        </article>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import InteractiveBackdrop from '../components/InteractiveBackdrop.vue'
import SiteNavigation from '../components/SiteNavigation.vue'
import { getDashboard, getEvidenceSummary } from '../api/platform.js'

const evidence = ref(null)
const dashboard = ref(null)
const usageDescriptions = [
  '适合沿着时间轴观察不同季度之间的空间分布变化。',
  '适合从地图热区、节点详情和局部差异中定位重点区域。',
  '适合在框选干预后比较区域变化，并快速识别受影响节点。',
]
const defaultUsageDescription = '适合结合工作台地图、季度切换和节点详情一起判断。'

function metricValue(value) {
  return Number.isFinite(Number(value)) ? Number(value).toFixed(4) : '--'
}

const forecastWindow = computed(() => {
  const preview = dashboard.value?.prediction_preview?.prediction_window
  if (!preview?.from && !preview?.to) return '--'
  return `${preview.from || '起点'} 至 ${preview.to || '终点'}`
})

const improvementText = computed(() => {
  const gain = Number(evidence.value?.quality_overview?.rmse_improvement_percent)
  if (!Number.isFinite(gain)) return '当前结果已经可以稳定支持平台展示'
  if (gain <= 0) return '当前结果已经接近本轮测试范围内的较优水平'
  return `在当前测试范围内，进一步优化最多可带来 ${gain.toFixed(2)}% 的误差改善`
})

onMounted(async () => {
  try {
    const [evidencePayload, dashboardPayload] = await Promise.all([getEvidenceSummary(), getDashboard()])
    evidence.value = evidencePayload
    dashboard.value = dashboardPayload
  } catch (error) {
    console.error('Failed to load evidence summary:', error)
  }
})
</script>

<style scoped>
.evidence-main {
  padding: 28px 0 72px;
  display: grid;
  gap: 22px;
}

.evidence-hero,
.evidence-layout {
  display: grid;
  gap: 18px;
}

.evidence-hero {
  padding: 28px;
  grid-template-columns: 1fr auto;
  align-items: center;
}

.evidence-layout {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.evidence-panel {
  padding: 22px;
}

.evidence-panel--usage {
  display: grid;
  gap: 18px;
}

.usage-card-grid {
  display: grid;
  gap: 14px;
}

.usage-card {
  padding: 18px;
  border-radius: 20px;
  background:
    radial-gradient(circle at 100% 0%, rgba(79, 191, 127, 0.1), transparent 28%),
    rgba(8, 22, 35, 0.82);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.usage-card__index {
  display: inline-flex;
  margin-bottom: 10px;
  color: var(--brand-amber);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.usage-card strong {
  display: block;
  font-size: 18px;
}

.usage-card p {
  margin-top: 10px;
  color: var(--text-secondary);
  line-height: 1.7;
}

.usage-note-shell {
  padding: 18px 20px;
  border-radius: 20px;
  background: rgba(5, 18, 30, 0.68);
  border: 1px solid rgba(95, 208, 209, 0.12);
}

.usage-note-shell strong {
  display: block;
  margin-bottom: 12px;
}

.model-card-grid {
  display: grid;
  gap: 14px;
}

.model-card {
  padding: 18px;
  border-radius: 18px;
  background: rgba(8, 22, 35, 0.82);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.model-card__head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.model-card__head p,
.model-card__desc,
.panel-note {
  color: var(--text-secondary);
}

.model-card__desc {
  margin-top: 12px;
  font-size: 14px;
}

.model-card__metrics {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-top: 16px;
}

.model-card__metrics span {
  display: block;
  color: var(--text-muted);
  font-size: 12px;
}

.model-card__metrics strong {
  display: block;
  margin-top: 6px;
  font-size: 22px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: baseline;
  margin-bottom: 14px;
}

.section-head small,
.summary-list span {
  color: var(--text-muted);
}

.summary-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 10px;
}

.summary-list li {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.summary-list li:last-child {
  border-bottom: none;
}

.brand-chip--small {
  padding: 6px 10px;
  font-size: 12px;
}

.panel-note {
  margin-top: 14px;
  font-size: 14px;
}

.tips-list {
  margin: 0;
  padding-left: 18px;
  color: var(--text-secondary);
  display: grid;
  gap: 10px;
}

@media (max-width: 980px) {
  .evidence-hero,
  .evidence-layout,
  .model-card__metrics {
    grid-template-columns: 1fr;
  }
}
</style>
