import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
    },
    {
      path: '/adminboard',
      name: 'admindashboard',
      component: () => import('../views/AdminView.vue'),
    },
    {
      path: '/adminboard/users',
      name: 'adminusersboard',
      component: () => import('../views/AdminUsersView.vue'),
    },
    {
      path: '/userboard',
      name: 'userdashboard',
      component: () => import('../views/UserView.vue'),
    },
    {
      path: '/profile',
      name: 'userprofile',
      component: () => import('../views/ProfileView.vue'),
    },
    {
      path: '/summary',
      name: 'summary',
      component: () => import('../views/SummaryView.vue'),
    },    
  ],
})

export default router
