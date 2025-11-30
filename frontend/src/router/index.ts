/**
 * Vue Router Configuration with Clerk Auth Guards
 *
 * 路由结构：
 * - / → 重定向到 /bankruptcy
 * - /bankruptcy → 破产案件主页（项目列表）
 * - /projects/new → 创建项目
 * - /projects/:id → 项目详情
 * - /projects/:projectId/creditors/:creditorId → 债权人详情
 * - /calculator → 利息计算器
 */
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // Public routes (no auth required)
    {
      path: '/sign-in',
      name: 'sign-in',
      component: () => import('@/pages/SignInPage.vue'),
      meta: { title: '登录', public: true }
    },
    {
      path: '/sign-up',
      name: 'sign-up',
      component: () => import('@/pages/SignUpPage.vue'),
      meta: { title: '注册', public: true }
    },

    // Protected routes (auth required)
    {
      path: '/',
      redirect: '/bankruptcy'
    },
    {
      path: '/bankruptcy',
      name: 'bankruptcy',
      component: () => import('@/pages/BankruptcyPage.vue'),
      meta: { title: '破产案件' }
    },
    {
      // 保留旧路由兼容性
      path: '/projects',
      redirect: '/bankruptcy'
    },
    {
      path: '/projects/new',
      name: 'new-project',
      component: () => import('@/pages/NewProjectPage.vue'),
      meta: { title: '创建项目' }
    },
    {
      path: '/projects/:id',
      name: 'project-detail',
      component: () => import('@/pages/ProjectDetailPage.vue'),
      meta: { title: '项目详情' }
    },
    {
      path: '/projects/:projectId/creditors/:creditorId',
      name: 'creditor-detail',
      component: () => import('@/pages/CreditorDetailPage.vue'),
      meta: { title: '债权人详情' }
    },
    {
      path: '/calculator',
      name: 'calculator',
      component: () => import('@/pages/CalculatorPage.vue'),
      meta: { title: '利息计算器' }
    }
  ]
})

// Update document title on navigation
router.beforeEach((to, _from, next) => {
  document.title = `${to.meta.title || '债权审查系统'} - 债权审查系统`
  next()
})

export default router
