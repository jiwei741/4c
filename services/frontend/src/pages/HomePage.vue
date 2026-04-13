<template>
  <div class="page-shell home-page">
    <SiteNavigation />

    <main>
      <section class="hero page-section">
        <div class="hero__copy">
          <span class="brand-chip">2026 竞赛展示版 · 南京季度研究区</span>
          <h1 class="section-title">在地图上直接干预区域，并看到未来季度碳汇变化。</h1>
          <p class="hero__lead">
            天穹智算围绕区域碳汇监测、图时序预测与情景推演构建可运行平台，将多源季度特征、正式模型产物与交互式工作台组织成面向答辩和推广的完整展示链路。
          </p>
          <div class="hero__actions">
            <RouterLink class="primary-btn" to="/workspace">进入研究区工作台</RouterLink>
            <RouterLink class="secondary-btn" to="/cases">查看案例推演</RouterLink>
            <RouterLink class="ghost-btn" to="/evidence">查看模型证据</RouterLink>
          </div>
          <div class="tag-list">
            <span class="data-tag">309 个规则网格节点</span>
            <span class="data-tag">2020-Q1 至 2024-Q4 季度数据装配</span>
            <span class="data-tag">ST-GNN / LSTM 正式模型产物</span>
            <span class="data-tag">Docker 一键交付</span>
          </div>
        </div>

        <div class="hero__panel glass-card">
          <div class="hero__panel-head">
            <strong>平台首屏预览</strong>
            <small>真实地图与热力层截图</small>
          </div>
          <img src="/images/workspace-preview.png" alt="平台工作台预览" class="hero__preview" />
          <div class="hero__panel-foot">
            <div>
              <span>默认模型</span>
              <strong>{{ dashboard?.prediction_preview?.model_name || '加载中' }}</strong>
            </div>
            <div>
              <span>当前预测窗</span>
              <strong>{{ forecastWindow }}</strong>
            </div>
          </div>
        </div>
      </section>

      <section class="page-section section-block">
        <div class="section-headline">
          <span class="brand-chip">问题场景</span>
          <h2 class="section-title">为什么需要区域碳汇时空分析，而不只是静态统计表？</h2>
          <p class="section-lead">
            南京样本区的地表覆盖、排放扰动和季节变化并不是同步发生的。单一年度统计无法解释空间差异，也难以直接支持“如果在某片区域发生工业扩张或生态修复，会带来什么影响”这一核心问题。
          </p>
        </div>
        <div class="problem-grid">
          <article class="glass-card problem-card">
            <strong>传统统计过粗</strong>
            <p>行政区平均值难以识别局部热点区，无法支撑网格级追踪与对比。</p>
          </article>
          <article class="glass-card problem-card">
            <strong>过程变化难解释</strong>
            <p>地表覆盖变化与季度尺度扰动需要统一到同一空间单元，才能形成连续判断。</p>
          </article>
          <article class="glass-card problem-card">
            <strong>决策需要推演</strong>
            <p>仅有预测还不够，平台需要能对不同区域策略的影响进行可视化对比。</p>
          </article>
        </div>
      </section>

      <section class="page-section section-block">
        <div class="section-headline">
          <span class="brand-chip">核心能力</span>
          <h2 class="section-title">从多源季度数据到工作台展示，形成完整闭环。</h2>
        </div>
        <div class="capability-grid">
          <article v-for="item in capabilities" :key="item.title" class="glass-card capability-card">
            <span class="capability-card__index">{{ item.index }}</span>
            <strong>{{ item.title }}</strong>
            <p>{{ item.desc }}</p>
          </article>
        </div>
      </section>

      <section class="page-section section-block">
        <div class="section-headline">
          <span class="brand-chip">证据预览</span>
          <h2 class="section-title">展示不止是页面，更要给出真实模型与实验结果。</h2>
          <p class="section-lead">本页仅展示摘要，完整结果请进入模型证据页查看正式模型、多 seed 与 adjacency sweep 结果。</p>
        </div>
        <div class="metric-grid">
          <div class="metric-card" v-for="card in evidenceCards" :key="card.label">
            <span class="label">{{ card.label }}</span>
            <span class="value">{{ card.value }}</span>
            <span class="hint">{{ card.hint }}</span>
          </div>
        </div>
      </section>

      <section class="page-section section-block case-highlight">
        <div class="case-highlight__copy">
          <span class="brand-chip">案例演示</span>
          <h2 class="section-title">围绕真实推演样例组织页面，而不是页面巡检。</h2>
          <p class="section-lead">
            当前平台已固化工业扩张扰动的示例情景，能够展示基线预测、情景扰动和区域变化排行，适合作为答辩中的完整故事线。
          </p>
          <div class="hero__actions">
            <RouterLink class="primary-btn" to="/cases">进入案例页</RouterLink>
            <RouterLink class="ghost-btn" to="/workspace">从工作台重新演示</RouterLink>
          </div>
        </div>
        <div class="case-highlight__stats glass-card">
          <div>
            <span>当前正式模型</span>
            <strong>{{ officialModelName }}</strong>
          </div>
          <div>
            <span>预测窗口</span>
            <strong>{{ forecastWindow }}</strong>
          </div>
          <div>
            <span>研究区范围</span>
            <strong>南京研究区 / 309 节点</strong>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import SiteNavigation from '../components/SiteNavigation.vue'
import { getDashboard, getEvidenceSummary } from '../api/platform.js'

const dashboard = ref(null)
const evidence = ref(null)

const capabilities = [
  { index: '01', title: '多源季度数据装配', desc: '将遥感、气象与排放代理统一到规则网格与季度尺度，形成稳定训练底座。' },
  { index: '02', title: '高精度特征重建', desc: '以高精度季度 Sentinel-2 特征为正式训练源，保证地图与模型口径一致。' },
  { index: '03', title: '图时序碳汇预测', desc: '当前默认正式模型为多步 ST-GNN，用于未来季度碳汇趋势判断。' },
  { index: '04', title: '区域情景推演', desc: '支持地图框选区域后直接施加扰动，并查看未来季度变化。' },
  { index: '05', title: '案例与证据展示', desc: '将正式模型指标、多 seed 与参数扫描结果收束成可答辩的证据链。' },
  { index: '06', title: '标准化交付部署', desc: '已支持 Docker 镜像发布和精简交付目录，便于后续域名上线。' },
]

const forecastWindow = computed(() => {
  const preview = dashboard.value?.prediction_preview?.prediction_window
  if (!preview?.from && !preview?.to) return '2025-Q1 至 2025-Q2'
  return `${preview.from || '起点'} 至 ${preview.to || '终点'}`
})

const officialModelName = computed(() => evidence.value?.official_model?.name || dashboard.value?.prediction_preview?.model_name || 'ST-GNN Multi-Step')
const evidenceCards = computed(() => {
  const official = evidence.value?.official_model
  const multiSeed = evidence.value?.multi_seed
  const sweep = evidence.value?.adjacency_sweep
  const combo = evidence.value?.candidate_upgrade

  return [
    {
      label: '正式模型 RMSE',
      value: official ? Number(official.metrics.rmse).toFixed(4) : '--',
      hint: official ? `${official.name} 当前正式结果` : '读取中',
    },
    {
      label: '多 Seed 最优',
      value: multiSeed ? Number(multiSeed.best_run_rmse).toFixed(4) : '--',
      hint: multiSeed ? `最佳 seed：${multiSeed.best_seed}` : '读取中',
    },
    {
      label: 'Sweep 最优组合',
      value: sweep ? sweep.best_combo_id : '--',
      hint: sweep ? `RMSE ${Number(sweep.best_rmse).toFixed(4)}` : '读取中',
    },
    {
      label: '候选升级效果',
      value: combo ? `${combo.rmse_gain_percent.toFixed(2)}%` : '--',
      hint: combo ? '相对正式模型 RMSE 改善' : '读取中',
    },
  ]
})

onMounted(async () => {
  try {
    const [dashboardPayload, evidencePayload] = await Promise.all([getDashboard(), getEvidenceSummary()])
    dashboard.value = dashboardPayload
    evidence.value = evidencePayload
  } catch (error) {
    console.error('Failed to load home page data:', error)
  }
})
</script>

<style scoped>
.hero,
.case-highlight {
  display: grid;
  gap: 28px;
  grid-template-columns: 1.1fr 0.9fr;
  align-items: center;
}

.hero {
  padding: 52px 0 38px;
}

.hero__copy,
.hero__panel,
.case-highlight__stats {
  padding: 30px;
}

.hero__lead {
  margin-top: 18px;
  font-size: 18px;
  color: var(--text-secondary);
  max-width: 760px;
}

.hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin: 24px 0 18px;
}

.hero__panel-head,
.hero__panel-foot,
.case-highlight__stats {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.hero__panel-head small,
.hero__panel-foot span,
.case-highlight__stats span {
  color: var(--text-muted);
}

.hero__preview {
  margin: 18px 0;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.hero__panel-foot > div,
.case-highlight__stats > div {
  display: grid;
  gap: 8px;
}

.section-block {
  padding: 38px 0;
}

.section-headline {
  display: grid;
  gap: 16px;
  margin-bottom: 22px;
}

.problem-grid,
.capability-grid {
  display: grid;
  gap: 18px;
}

.problem-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.capability-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.problem-card,
.capability-card {
  padding: 22px;
}

.problem-card p,
.capability-card p {
  margin-top: 12px;
  color: var(--text-secondary);
}

.capability-card__index {
  display: inline-flex;
  margin-bottom: 18px;
  color: var(--brand-amber);
  font-size: 24px;
  font-weight: 700;
}

.case-highlight {
  padding-bottom: 72px;
}

.case-highlight__stats {
  display: grid;
}

@media (max-width: 980px) {
  .hero,
  .case-highlight,
  .problem-grid,
  .capability-grid {
    grid-template-columns: 1fr;
  }
}
</style>
