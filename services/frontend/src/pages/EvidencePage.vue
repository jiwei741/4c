<template>
  <div class="page-shell evidence-page">
    <SiteNavigation compact />

    <main class="page-section evidence-main">
      <section class="glass-card evidence-hero">
        <div>
          <span class="brand-chip">模型证据</span>
          <h1 class="section-title">用正式产物、多 seed 和参数扫描结果支撑平台可信度。</h1>
          <p class="section-lead">
            本页只复用当前已有正式模型产物和实验结果，不新增训练、不扩展未落地能力，保证展示与真实工程状态一致。
          </p>
        </div>
        <RouterLink class="primary-btn" to="/workspace">回到工作台</RouterLink>
      </section>

      <section class="metric-grid">
        <div class="metric-card">
          <span class="label">正式模型</span>
          <span class="value">{{ evidence?.official_model?.name || '加载中' }}</span>
          <span class="hint">当前平台默认多步模型</span>
        </div>
        <div class="metric-card">
          <span class="label">正式 RMSE</span>
          <span class="value">{{ metricValue(evidence?.official_model?.metrics?.rmse) }}</span>
          <span class="hint">正式模型误差指标</span>
        </div>
        <div class="metric-card">
          <span class="label">最佳 Sweep</span>
          <span class="value">{{ evidence?.adjacency_sweep?.best_combo_id || '--' }}</span>
          <span class="hint">当前参数扫描最优组合</span>
        </div>
        <div class="metric-card">
          <span class="label">候选提升</span>
          <span class="value">{{ evidence?.candidate_upgrade ? `${evidence.candidate_upgrade.rmse_gain_percent.toFixed(2)}%` : '--' }}</span>
          <span class="hint">相对正式模型 RMSE 改善</span>
        </div>
      </section>

      <section class="evidence-layout">
        <article class="glass-card evidence-panel">
          <div class="section-head">
            <strong>模型对比</strong>
            <small>正式产物直接读取</small>
          </div>
          <div class="table-shell">
            <table class="data-table">
              <thead>
                <tr>
                  <th>模型</th>
                  <th>阶段</th>
                  <th>RMSE</th>
                  <th>MAE</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in evidence?.model_comparison || []" :key="item.key">
                  <td>{{ item.name }}</td>
                  <td>{{ item.stage }}</td>
                  <td>{{ metricValue(item.metrics.rmse) }}</td>
                  <td>{{ metricValue(item.metrics.mae) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>

        <article class="glass-card evidence-panel">
          <div class="section-head">
            <strong>多 Seed 复验</strong>
            <small>稳定性摘要</small>
          </div>
          <ul class="summary-list">
            <li>
              <span>Seed 数量</span>
              <strong>{{ evidence?.multi_seed?.num_runs || 0 }}</strong>
            </li>
            <li>
              <span>最佳 Seed</span>
              <strong>{{ evidence?.multi_seed?.best_seed || '--' }}</strong>
            </li>
            <li>
              <span>最佳 RMSE</span>
              <strong>{{ metricValue(evidence?.multi_seed?.best_run_rmse) }}</strong>
            </li>
            <li>
              <span>RMSE 均值</span>
              <strong>{{ metricValue(evidence?.multi_seed?.aggregate?.rmse_mean) }}</strong>
            </li>
            <li>
              <span>RMSE 标准差</span>
              <strong>{{ metricValue(evidence?.multi_seed?.aggregate?.rmse_std) }}</strong>
            </li>
          </ul>
        </article>
      </section>

      <section class="evidence-layout">
        <article class="glass-card evidence-panel">
          <div class="section-head">
            <strong>Adjacency Sweep</strong>
            <small>参数扫描最优组合</small>
          </div>
          <ul class="summary-list">
            <li>
              <span>组合编号</span>
              <strong>{{ evidence?.adjacency_sweep?.best_combo_id || '--' }}</strong>
            </li>
            <li>
              <span>radius_km</span>
              <strong>{{ evidence?.adjacency_sweep?.adjacency?.radius_km ?? '--' }}</strong>
            </li>
            <li>
              <span>k</span>
              <strong>{{ evidence?.adjacency_sweep?.adjacency?.k ?? '--' }}</strong>
            </li>
            <li>
              <span>wind_scale</span>
              <strong>{{ evidence?.adjacency_sweep?.adjacency?.wind_scale ?? '--' }}</strong>
            </li>
            <li>
              <span>similarity_weight</span>
              <strong>{{ evidence?.adjacency_sweep?.adjacency?.similarity_weight ?? '--' }}</strong>
            </li>
          </ul>
        </article>

        <article class="glass-card evidence-panel">
          <div class="section-head">
            <strong>候选升级判断</strong>
            <small>仅作为候选，不自动替换正式模型</small>
          </div>
          <p class="summary-paragraph">
            {{ candidateSummary }}
          </p>
          <img src="/images/workspace-preview.png" alt="工作台截图" class="evidence-preview" />
        </article>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import SiteNavigation from '../components/SiteNavigation.vue'
import { getEvidenceSummary } from '../api/platform.js'

const evidence = ref(null)

function metricValue(value) {
  return Number.isFinite(Number(value)) ? Number(value).toFixed(4) : '--'
}

const candidateSummary = computed(() => {
  const candidate = evidence.value?.candidate_upgrade
  if (!candidate) {
    return '正在加载候选升级说明。'
  }

  return `候选组合 ${candidate.combo_id} 相对当前正式模型带来 ${candidate.rmse_gain_percent.toFixed(2)}% 的 RMSE 改善，但在完成正式替换前仍作为候选升级配置保留。`
})

onMounted(async () => {
  try {
    evidence.value = await getEvidenceSummary()
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

.section-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: baseline;
  margin-bottom: 14px;
}

.section-head small,
.summary-list span,
.summary-paragraph {
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

.evidence-preview {
  margin-top: 18px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

@media (max-width: 980px) {
  .evidence-hero,
  .evidence-layout {
    grid-template-columns: 1fr;
  }
}
</style>
