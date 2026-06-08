import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'MatchSetup',
      component: () => import('../views/MatchSetup.vue')
    },
    {
      path: '/draft',
      name: 'DraftArena',
      component: () => import('../views/DraftArena.vue')
    },
    {
      path: '/results',
      name: 'OptimizationResults',
      component: () => import('../views/OptimizationResults.vue')
    }
  ]
})

export default router
