<template>
  <div class="page-shell page-shell--interactive home-page">
    <InteractiveBackdrop variant="home" />
    <SiteNavigation />

    <main class="page-content-layer">
      <section class="hero page-section">
        <div class="hero__copy hero__copy--assistant glass-card">
          <FaqAssistantCard />
          <div class="hero__scroll">
            <span class="hero__scroll-line"></span>
            <span>向下滚动，查看平台能力与使用入口</span>
          </div>
        </div>

        <div class="hero__stage">
          <div class="hero__preview-card glass-card">
            <div class="hero__panel-head">
              <strong>平台能力图谱</strong>
              <small>围绕历史分布、预测季度与情景推演组织同一套研究区分析入口</small>
            </div>
            <KnowledgeConstellation />
            <div class="hero__panel-foot">
              <div>
                <span>当前模型</span>
                <strong>{{ dashboard?.prediction_preview?.model_name || '加载中' }}</strong>
              </div>
              <div>
                <span>预测范围</span>
                <strong>{{ forecastWindow }}</strong>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="page-section section-block">
        <div class="section-headline">
          <span class="brand-chip">平台价值</span>
          <h2 class="section-title">把历史回看、季度预测和区域推演放在同一条分析链路中。</h2>
          <p class="section-lead">
            研究区内的碳汇变化并不是均匀发生的。平台通过季度尺度和规则网格视角，把空间差异、时间变化和区域干预影响放到同一张地图中展示，帮助用户更快识别重点区域与变化节点。
          </p>
        </div>
        <div class="problem-grid">
          <article class="glass-card problem-card">
            <strong>查看历史变化</strong>
            <p>支持切换历史季度，观察研究区内不同时段的空间分布变化。</p>
          </article>
          <article class="glass-card problem-card">
            <strong>关注未来趋势</strong>
            <p>在同一套工作台中查看当前接入的预测季度结果，理解后续变化方向。</p>
          </article>
          <article class="glass-card problem-card">
            <strong>比较干预影响</strong>
            <p>框选区域后运行情景推演，直接比较推演前后地图差异与受影响节点。</p>
          </article>
        </div>
      </section>

      <section class="page-section section-block">
        <div class="section-headline">
          <span class="brand-chip">核心功能</span>
          <h2 class="section-title">面向使用者的主要入口都集中在工作台中。</h2>
        </div>
        <div class="capability-grid">
          <article v-for="item in capabilities" :key="item.title" class="glass-card capability-card">
            <span class="capability-card__index">{{ item.index }}</span>
            <strong>{{ item.title }}</strong>
            <p>{{ item.desc }}</p>
          </article>
        </div>
      </section>

      <section class="page-section section-block overview-band glass-card">
        <div class="overview-band__copy">
          <span class="brand-chip">结果概览</span>
          <h2 class="section-title">当前平台已经接入历史季度、预测季度和情景推演入口。</h2>
          <p class="section-lead">
            可以直接从首页进入工作台查看研究区地图、切换季度结果，或进入模型结果页了解当前结果的整体误差与稳定性表现。
          </p>
        </div>
        <div class="metric-grid">
          <div class="metric-card" v-for="card in overviewCards" :key="card.label">
            <span class="label">{{ card.label }}</span>
            <span class="value">{{ card.value }}</span>
            <span class="hint">{{ card.hint }}</span>
          </div>
        </div>
      </section>

      <section class="page-section section-block quick-entry">
        <div class="quick-entry__copy">
          <span class="brand-chip">开始使用</span>
          <h2 class="section-title">如果你想直接查看地图、切换季度或运行情景推演，可以从这里进入。</h2>
          <p class="section-lead">
            工作台提供季度切换、热力图查看、节点详情、区域框选和情景推演对比；模型结果页则用于查看当前结果表现与使用建议。
          </p>
          <div class="hero__actions">
            <RouterLink class="secondary-btn quick-entry__primary" to="/workspace">打开工作台</RouterLink>
            <RouterLink class="ghost-btn quick-entry__secondary" to="/evidence">打开模型结果页</RouterLink>
          </div>
        </div>
        <div class="quick-entry__stats glass-card">
          <div>
            <span>研究区</span>
            <strong>{{ studyAreaName }}</strong>
          </div>
          <div>
            <span>历史季度</span>
            <strong>{{ historicalRange }}</strong>
          </div>
          <div>
            <span>预测季度</span>
            <strong>{{ forecastRange }}</strong>
          </div>
        </div>
      </section>
    </main>

    <RouterLink class="guide-fab" to="/guide" aria-label="打开平台使用引导">
      <span class="guide-fab__mark">?</span>
    </RouterLink>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import FaqAssistantCard from '../components/FaqAssistantCard.vue'
import InteractiveBackdrop from '../components/InteractiveBackdrop.vue'
import KnowledgeConstellation from '../components/KnowledgeConstellation.vue'
import SiteNavigation from '../components/SiteNavigation.vue'
import { getDashboard, getEvidenceSummary } from '../api/platform.js'

const dashboard = ref(null)
const evidence = ref(null)

const capabilities = [
  { index: '01', title: '季度地图回看', desc: '按季度切换历史与预测结果，在地图上直接查看研究区空间分布。' },
  { index: '02', title: '热点区域识别', desc: '结合颜色层和节点详情，更快识别当前季度的重点区域。' },
  { index: '03', title: '趋势结果查看', desc: '在工作台中浏览当前已接入的预测季度结果，观察区域变化方向。' },
  { index: '04', title: '情景推演对比', desc: '对指定区域施加干预后，比较推演前后的地图结果与变化节点。' },
  { index: '05', title: '模型结果概览', desc: '在模型结果页查看平台当前结果表现、稳定性和使用建议。' },
]

const studyAreaName = computed(() => dashboard.value?.project?.study_area?.name || '南京研究区')
const forecastWindow = computed(() => {
  const preview = dashboard.value?.prediction_preview?.prediction_window
  if (!preview?.from && !preview?.to) return '2025-Q1 至 2025-Q2'
  return `${preview.from || '起点'} 至 ${preview.to || '终点'}`
})

const historicalRange = computed(() => {
  const items = dashboard.value?.prediction_preview?.historical_timestamps || []
  if (!items.length) return '--'
  return `${items[0]} 至 ${items[items.length - 1]}`
})

const forecastRange = computed(() => {
  const items = dashboard.value?.prediction_preview?.forecast_timestamps || []
  if (!items.length) return '--'
  return `${items[0]} 至 ${items[items.length - 1]}`
})

const overviewCards = computed(() => [
  {
    label: '研究区范围',
    value: studyAreaName.value,
    hint: '当前平台样本区域',
  },
  {
    label: '历史季度',
    value: historicalRange.value,
    hint: '支持回看历史分布',
  },
  {
    label: '预测季度',
    value: forecastRange.value,
    hint: '支持查看当前预测结果',
  },
  {
    label: '当前模型',
    value: evidence.value?.current_result?.name || dashboard.value?.prediction_preview?.model_name || '加载中',
    hint: '用于地图展示与推演分析',
  },
])

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
.quick-entry {
  display: grid;
  gap: 28px;
  grid-template-columns: minmax(360px, 0.78fr) minmax(620px, 1.22fr);
  align-items: center;
}

.hero {
  padding: 34px 0 36px;
  min-height: calc(100vh - 120px);
}

.hero__copy,
.hero__preview-card,
.quick-entry__stats,
.overview-band {
  padding: 28px;
}

.hero__copy {
  display: grid;
  gap: 20px;
  align-self: stretch;
  padding: 34px;
}

.hero__copy--assistant {
  align-content: center;
}

.hero :deep(.faq-assistant) {
  margin-top: 4px;
}

.hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
}

.hero__scroll {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  margin-top: 18px;
  color: var(--text-muted);
  font-size: 13px;
}

.hero__scroll-line {
  width: 46px;
  height: 1px;
  background: linear-gradient(90deg, var(--brand-sea), transparent);
}

.hero__stage {
  position: relative;
  min-height: 700px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero__preview-card {
  width: min(100%, 820px);
  position: relative;
  z-index: 2;
  display: grid;
  gap: 16px;
  padding: 24px;
}

.hero__panel-foot {
  align-items: center;
}

.hero__panel-head,
.hero__panel-foot,
.quick-entry__stats {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.hero__panel-head small,
.hero__panel-foot span,
.quick-entry__stats span,
.hero__floating span,
.hero__floating small {
  color: var(--text-muted);
}

.hero__panel-foot > div,
.quick-entry__stats > div {
  display: grid;
  gap: 8px;
}

.hero__panel-foot strong {
  font-size: 18px;
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

.problem-grid,
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

.overview-band {
  display: grid;
  gap: 22px;
}

.quick-entry {
  padding-bottom: 72px;
}

.quick-entry__stats {
  display: grid;
}

.quick-entry__primary {
  min-height: 48px;
  padding: 0 24px;
}

.quick-entry__secondary {
  min-height: 44px;
  padding: 0 18px;
}

.guide-fab {
  position: fixed;
  right: 28px;
  bottom: 28px;
  z-index: 22;
  width: 62px;
  height: 62px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background:
    linear-gradient(145deg, rgba(31, 143, 188, 0.96), rgba(79, 191, 127, 0.94));
  color: #04131d;
  box-shadow:
    0 24px 44px rgba(6, 19, 31, 0.34),
    0 0 0 1px rgba(255, 255, 255, 0.08);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.guide-fab::before {
  content: '';
  position: absolute;
  inset: 4px;
  border-radius: 50%;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.18), transparent 34%);
  opacity: 0.8;
}

.guide-fab:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow:
    0 30px 52px rgba(6, 19, 31, 0.42),
    0 0 0 1px rgba(255, 255, 255, 0.12);
}

.guide-fab__mark {
  position: relative;
  z-index: 1;
  font-size: 28px;
  font-weight: 800;
  line-height: 1;
}

@media (max-width: 1120px) {
  .hero,
  .quick-entry,
  .problem-grid,
  .capability-grid {
    grid-template-columns: 1fr;
  }

  .hero {
    min-height: auto;
  }

  .hero__stage {
    min-height: 520px;
  }
}

@media (max-width: 760px) {
  .guide-fab {
    right: 18px;
    bottom: 18px;
    width: 56px;
    height: 56px;
  }
}
</style>
