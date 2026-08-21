import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import MainLayout from '../layouts/MainLayout.vue'
import ContractListView from '../views/ContractListView.vue'
import ContractUploadView from '../views/ContractUploadView.vue'
import ContractDetailView from '../views/ContractDetailView.vue'
import ContractReviewView from '../views/ContractReviewView.vue'
import AdminDashboardView from '../views/AdminDashboardView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: () => {
        if (!localStorage.getItem('user_id')) {
          return '/login'
        }

        return localStorage.getItem('role') === 'admin' ? '/admin' : '/contracts'
      },
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { public: true },
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { public: true },
    },
    {
      path: '/',
      component: MainLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: 'contracts',
          name: 'contracts',
          component: ContractListView,
        },
        {
          path: 'contracts/upload',
          name: 'contract-upload',
          component: ContractUploadView,
        },
        {
          path: 'contracts/:id',
          name: 'contract-detail',
          component: ContractDetailView,
        },
        {
          path: 'contracts/:id/review',
          name: 'contract-review',
          component: ContractReviewView,
        },
        {
          path: 'admin',
          name: 'admin',
          component: AdminDashboardView,
          meta: { requiresAdmin: true },
        },
      ],
    },
  ],
})

router.beforeEach((to) => {
  const isLoggedIn = Boolean(localStorage.getItem('user_id'))
  const role = localStorage.getItem('role') || 'user'

  if (to.meta.requiresAuth && !isLoggedIn) {
    return {
      path: '/login',
      query: { redirect: to.fullPath },
    }
  }

  if (to.meta.requiresAdmin && role !== 'admin') {
    return '/contracts'
  }

  if ((to.name === 'login' || to.name === 'register') && isLoggedIn) {
    return role === 'admin' ? '/admin' : '/contracts'
  }

  return true
})

export default router
