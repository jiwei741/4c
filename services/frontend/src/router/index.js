import { createRouter, createWebHistory } from 'vue-router'

import HomePage from '../pages/HomePage.vue'
import WorkspacePage from '../pages/WorkspacePage.vue'
import CasesPage from '../pages/CasesPage.vue'
import EvidencePage from '../pages/EvidencePage.vue'

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
      path: '/cases',
      name: 'cases',
      component: CasesPage,
      meta: { title: '案例推演 | 天穹智算' },
    },
    {
      path: '/evidence',
      name: 'evidence',
      component: EvidencePage,
      meta: { title: '模型证据 | 天穹智算' },
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
