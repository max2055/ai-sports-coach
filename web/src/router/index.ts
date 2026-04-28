import { createRouter, createWebHistory } from 'vue-router'
import UploadView from '../views/UploadView.vue'
import AnalysisView from '../views/AnalysisView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'upload',
      component: UploadView,
    },
    {
      path: '/analysis/:videoId',
      name: 'analysis',
      component: AnalysisView,
    },
    {
      path: '/report/:videoId',
      name: 'report',
      component: () => import('../views/ReportView.vue'),
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
  ],
})

export default router
