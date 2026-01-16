import { createRouter, createWebHistory } from 'vue-router'
// 引入我们的两个页面
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import { useUserStore } from '../stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false } // 不需要登录就能看
  },
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true } // 重点：这个页面需要登录才能看！
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// === 路由守卫  ===
// 每次切换页面前，都会执行这个函数
router.beforeEach((to, from, next) => {
  //  获取仓库(UserStore)
  // 注意：必须在 beforeEach 内部获取，不能在外面，因为 Pinia 可能还没挂载
  const userStore = useUserStore()

  console.log('👮 保安开始检查:', to.path)
  console.log('🎫 是否需要权限:', to.meta.requiresAuth)
  console.log('🔑 当前Token:', userStore.accessToken)

  // 检查要去的地方是否需要权限
  if (to.meta.requiresAuth) {
    // 如果需要权限，且用户没 Token (没登录)
    const token = userStore.accessToken;
    if (!token || token.trim() === '' || token === 'null' || token === 'undefined') {
      // 踢回登录页
      console.log('🚫 没票，踢回登录页') // 调试
      next('/login')
    } else {
      // 有 Token，放行
      console.log('✅ 有票，放行') // 调试
      next()
    }
  } else {
    // 不需要权限的页面 (如登录页)，直接放行
    next()
  }
})

export default router