<template>
  <div class="page-shell page-shell--interactive usage-guide-page">
    <InteractiveBackdrop variant="evidence" />
    <SiteNavigation compact />

    <main class="page-section page-content-layer usage-guide-main">
      <section class="glass-card usage-guide-hero">
        <div class="usage-guide-hero__copy">
          <span class="brand-chip">平台使用引导</span>
          <h1 class="section-title">按“看地图、切季度、查节点、做推演、读结果”这条路径使用平台就够了。</h1>
          <p class="section-lead">
            这份引导页只介绍平台的实际使用方法，不讲内部实现。第一次进入平台时，建议先看工作台地图，再根据需要切换季度、查看节点详情、发起情景推演，最后到模型结果页理解当前结果表现。
          </p>
        </div>
        <div class="usage-guide-hero__actions">
          <RouterLink class="primary-btn" to="/workspace">进入工作台</RouterLink>
          <RouterLink class="ghost-btn" to="/evidence">查看模型结果</RouterLink>
        </div>
      </section>

      <section class="usage-guide-flow">
        <article v-for="item in flowItems" :key="item.step" class="glass-card flow-card">
          <span class="flow-card__step">{{ item.step }}</span>
          <strong>{{ item.title }}</strong>
          <p>{{ item.desc }}</p>
        </article>
      </section>

      <section class="usage-guide-layout">
        <article class="glass-card usage-panel">
          <div class="usage-panel__head">
            <strong>1. 首页怎么用</strong>
            <small>快速理解入口，再进入工作台</small>
          </div>
          <ul class="usage-list">
            <li>首页右侧的知识谱系用于快速理解平台能力结构，不需要逐个点开才能使用。</li>
            <li>如果你不确定从哪里开始，可以直接使用首页左侧的 FAQ 助手提问。</li>
            <li>如果你已经明确要看地图或做推演，建议直接进入工作台。</li>
          </ul>
        </article>

        <article class="glass-card usage-panel">
          <div class="usage-panel__head">
            <strong>2. 工作台怎么用</strong>
            <small>地图、季度切换与节点查看都在这里</small>
          </div>
          <ul class="usage-list">
            <li>进入工作台后，主地图会展示研究区的空间分布结果。</li>
            <li>底部时间轴支持统一切换历史季度和预测季度。</li>
            <li>点击地图中的网格节点后，可以查看该位置的详细信息和主导地类。</li>
            <li>右侧信息栏用于辅助理解当前季度的热点区域、重点节点和整体变化。</li>
          </ul>
        </article>
      </section>

      <section class="usage-guide-layout">
        <article class="glass-card usage-panel">
          <div class="usage-panel__head">
            <strong>3. 情景推演怎么做</strong>
            <small>按区域框选后比较推演前后差异</small>
          </div>
          <ol class="usage-steps">
            <li>在工作台顶部点击“启动情景推演”。</li>
            <li>在地图上拖拽框选待分析区域，并确认选区。</li>
            <li>调整推演参数后运行推演，等待生成对比结果。</li>
            <li>在对比视图中查看推演前后地图差异、受影响节点和变化摘要。</li>
          </ol>
        </article>

        <article class="glass-card usage-panel">
          <div class="usage-panel__head">
            <strong>4. 模型结果页怎么看</strong>
            <small>主要看结果表现、稳定性和适用方式</small>
          </div>
          <ul class="usage-list">
            <li>模型结果页用于说明当前平台结果的整体表现，不需要把它当作训练页理解。</li>
            <li>预测误差越低，说明当前结果和测试数据之间的偏差越小。</li>
            <li>稳定性越好，说明当前结果更适合长期用于地图展示和推演分析。</li>
            <li>建议结合工作台地图和节点详情一起看，不要只盯着单个数值。</li>
          </ul>
        </article>
      </section>

      <section class="glass-card usage-summary">
        <div class="usage-panel__head">
          <strong>推荐使用顺序</strong>
          <small>第一次使用时最省力的路径</small>
        </div>
        <div class="usage-summary__grid">
          <div>
            <span>01</span>
            <strong>先进入工作台</strong>
            <p>先从地图和时间轴理解研究区的历史与预测分布。</p>
          </div>
          <div>
            <span>02</span>
            <strong>再查看节点详情</strong>
            <p>点击重点区域，观察局部位置的详细信息和主导地类。</p>
          </div>
          <div>
            <span>03</span>
            <strong>然后做情景推演</strong>
            <p>对指定区域施加干预，比较前后地图差异与受影响节点。</p>
          </div>
          <div>
            <span>04</span>
            <strong>最后回看模型结果</strong>
            <p>理解当前平台结果表现，帮助判断展示结果的适用范围。</p>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'

import InteractiveBackdrop from '../components/InteractiveBackdrop.vue'
import SiteNavigation from '../components/SiteNavigation.vue'

const flowItems = [
  { step: '01', title: '进入工作台', desc: '查看研究区地图、切换季度并识别空间热点。' },
  { step: '02', title: '切换季度', desc: '从历史季度与预测季度之间切换，观察空间变化。' },
  { step: '03', title: '查看节点', desc: '点击网格节点，了解局部位置的详细信息。' },
  { step: '04', title: '发起推演', desc: '框选区域并运行情景推演，对比干预前后差异。' },
  { step: '05', title: '理解结果', desc: '到模型结果页查看当前结果表现与使用建议。' },
]
</script>

<style scoped>
.usage-guide-main {
  display: grid;
  gap: 24px;
  padding: 28px 0 72px;
}

.usage-guide-hero,
.usage-guide-layout,
.usage-guide-flow {
  display: grid;
  gap: 18px;
}

.usage-guide-hero {
  grid-template-columns: 1fr auto;
  align-items: center;
  padding: 28px;
}

.usage-guide-hero__copy {
  display: grid;
  gap: 16px;
}

.usage-guide-hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.usage-guide-flow {
  grid-template-columns: repeat(5, minmax(0, 1fr));
}

.flow-card,
.usage-panel,
.usage-summary {
  padding: 22px;
}

.flow-card__step,
.usage-summary__grid span {
  color: var(--brand-amber);
  font-size: 24px;
  font-weight: 700;
}

.flow-card strong {
  display: block;
  margin-top: 14px;
  font-size: 18px;
}

.flow-card p,
.usage-list li,
.usage-steps li,
.usage-summary__grid p {
  color: var(--text-secondary);
}

.flow-card p {
  margin-top: 12px;
}

.usage-guide-layout {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.usage-panel__head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: baseline;
  margin-bottom: 14px;
}

.usage-panel__head small {
  color: var(--text-muted);
}

.usage-list,
.usage-steps {
  display: grid;
  gap: 12px;
  margin: 0;
  padding-left: 20px;
}

.usage-summary__grid {
  display: grid;
  gap: 18px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin-top: 14px;
}

.usage-summary__grid strong {
  display: block;
  margin-top: 10px;
  font-size: 18px;
}

.usage-summary__grid p {
  margin-top: 10px;
}

@media (max-width: 1100px) {
  .usage-guide-flow,
  .usage-summary__grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .usage-guide-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .usage-guide-hero,
  .usage-guide-flow,
  .usage-summary__grid {
    grid-template-columns: 1fr;
  }

  .usage-guide-hero__actions {
    width: 100%;
  }
}
</style>
