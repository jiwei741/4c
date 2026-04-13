<template>
  <div class="page-shell cases-page">
    <SiteNavigation compact />

    <main class="page-section cases-main">
      <section class="cases-hero glass-card">
        <div>
          <span class="brand-chip">案例推演</span>
          <h1 class="section-title">把真实情景结果组织成完整故事，而不是单纯切页面。</h1>
          <p class="section-lead">
            当前页面优先围绕已有的工业扩张扰动样例展开，展示影响节点、特征扰动与空间变化结果，便于答辩时形成问题—干预—结果—解释的闭环。
          </p>
        </div>
        <RouterLink class="primary-btn" to="/workspace">返回工作台重新演示</RouterLink>
      </section>

      <section class="cases-grid">
        <article class="glass-card cases-sidebar">
          <div class="section-head">
            <strong>示例情景</strong>
            <small>后端已有正式样例</small>
          </div>
          <button
            v-for="item in scenarioItems"
            :key="item.key"
            class="scenario-link"
            :class="{ active: item.key === selectedScenarioKey }"
            @click="selectScenario(item.key)"
          >
            <span>{{ item.name }}</span>
            <small>{{ item.forecast_horizon }}</small>
          </button>
        </article>

        <article class="glass-card case-detail">
          <div class="section-head">
            <div>
              <strong>{{ selectedScenario?.name || '加载中' }}</strong>
              <small>{{ selectedScenario?.summary?.forecast_horizon || '最新预测窗' }}</small>
            </div>
            <span class="brand-chip">案例结果</span>
          </div>

          <div class="metric-grid">
            <div class="metric-card">
              <span class="label">受影响节点</span>
              <span class="value">{{ selectedScenario?.summary?.changed_nodes?.length || 0 }}</span>
              <span class="hint">用于说明空间干预范围</span>
            </div>
            <div class="metric-card">
              <span class="label">影响最大节点</span>
              <span class="value">{{ topImpactValue }}</span>
              <span class="hint">取自后端样例输出</span>
            </div>
            <div class="metric-card">
              <span class="label">特征扰动数</span>
              <span class="value">{{ featureDeltaCount }}</span>
              <span class="hint">包括排放与地表覆盖扰动</span>
            </div>
          </div>

          <div class="case-summary-grid">
            <section class="glass-card summary-tile">
              <div class="section-head">
                <strong>推演摘要</strong>
                <small>推荐答辩口径</small>
              </div>
              <p class="summary-paragraph">
                该样例通过对局部区域施加工业扩张扰动，模拟排放压力上升与地表覆盖变化对未来季度净碳通量预测的影响。页面优先展示影响节点、关键特征变化与变化排行，便于将案例解释为“区域扰动如何改变未来碳汇格局”。
              </p>
            </section>

            <section class="glass-card summary-tile">
              <div class="section-head">
                <strong>主要特征扰动</strong>
                <small>来自正式情景结果</small>
              </div>
              <ul class="summary-list">
                <li v-for="item in featureDeltaEntries" :key="item.label">
                  <span>{{ item.label }}</span>
                  <strong :class="item.value >= 0 ? 'positive' : 'negative'">
                    {{ item.value >= 0 ? '+' : '' }}{{ item.value.toFixed(3) }}
                  </strong>
                </li>
              </ul>
            </section>
          </div>

          <section class="glass-card">
            <div class="section-head">
              <strong>空间影响排行</strong>
              <small>Top 5 节点</small>
            </div>
            <ul class="summary-list">
              <li v-for="item in topImpacts" :key="item.node_id">
                <span>节点 {{ item.node_id }}</span>
                <strong>{{ Number(item.value).toFixed(4) }}</strong>
              </li>
            </ul>
          </section>
        </article>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import SiteNavigation from '../components/SiteNavigation.vue'
import { getScenarioExample, getScenarioExamples } from '../api/platform.js'

const scenarioItems = ref([])
const selectedScenarioKey = ref('')
const selectedScenario = ref(null)

const topImpacts = computed(() => selectedScenario.value?.summary?.top_impacts?.slice(0, 5) || [])
const featureDeltaEntries = computed(() => {
  const values = selectedScenario.value?.summary?.feature_deltas || {}
  return Object.entries(values).map(([label, value]) => ({ label, value: Number(value) }))
})
const featureDeltaCount = computed(() => featureDeltaEntries.value.length)
const topImpactValue = computed(() => {
  const top = topImpacts.value[0]
  return top ? Number(top.value).toFixed(4) : '--'
})

async function selectScenario(key) {
  selectedScenarioKey.value = key
  try {
    selectedScenario.value = await getScenarioExample(key)
  } catch (error) {
    console.error('Failed to load scenario detail:', error)
  }
}

onMounted(async () => {
  try {
    const payload = await getScenarioExamples()
    scenarioItems.value = payload.items || []
    const firstKey = scenarioItems.value[0]?.key
    if (firstKey) {
      await selectScenario(firstKey)
    }
  } catch (error) {
    console.error('Failed to load scenario examples:', error)
  }
})
</script>

<style scoped>
.cases-main {
  padding: 28px 0 72px;
  display: grid;
  gap: 22px;
}

.cases-hero,
.cases-grid {
  display: grid;
  gap: 18px;
}

.cases-hero {
  padding: 28px;
  grid-template-columns: 1fr auto;
  align-items: center;
}

.cases-grid {
  grid-template-columns: 320px 1fr;
}

.cases-sidebar,
.case-detail,
.summary-tile {
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
.summary-paragraph,
.summary-list span,
.scenario-link small {
  color: var(--text-muted);
}

.scenario-link {
  width: 100%;
  text-align: left;
  padding: 16px;
  margin-top: 10px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-primary);
  cursor: pointer;
}

.scenario-link span,
.scenario-link small {
  display: block;
}

.scenario-link.active {
  border-color: rgba(79, 191, 127, 0.4);
  background: rgba(79, 191, 127, 0.12);
}

.case-summary-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
  margin: 20px 0;
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
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.summary-list li:last-child {
  border-bottom: none;
}

.positive { color: #8ee0a4; }
.negative { color: #ff9d7b; }

@media (max-width: 980px) {
  .cases-hero,
  .cases-grid,
  .case-summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
