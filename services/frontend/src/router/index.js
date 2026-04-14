import { createRouter, createWebHistory } from 'vue-router'

import HomePage from '../pages/HomePage.vue'
import WorkspacePage from '../pages/WorkspacePage.vue'
import EvidencePage from '../pages/EvidencePage.vue'
import UsageGuidePage from '../pages/UsageGuidePage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage,
      meta: { title: '天穹智算 | 区域碳汇监测与情景推演平台' },
    },
    {
      path: '/workspace',
      name: 'workspace',
      component: WorkspacePage,
      meta: { title: '研究区工作台 | 天穹智算' },
    },
    {
      path: '/evidence',
      name: 'evidence',
      component: EvidencePage,
      meta: { title: '模型结果 | 天穹智算' },
    },
    {
      path: '/guide',
      name: 'guide',
      component: UsageGuidePage,
      meta: { title: '平台使用引导 | 天穹智算' },
    },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

router.afterEach((to) => {
  if (to.meta?.title) {
    document.title = String(to.meta.title)
  }
})

export default router
