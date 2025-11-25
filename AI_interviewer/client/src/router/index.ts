import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'


// 懒加载引入（推荐写法）
const Home = () => import('../views/Home.vue')
const Settings = () => import('../views/Settings.vue')
const Go = () => import('../views/Going.vue')
const Login = () => import('../views/Login.vue')
const MainLayout = () => import('../views/MainLayout.vue')

const routes: Array<RouteRecordRaw> = [
  { 
    path: '/', 
    redirect: '/login' 
  },
  { 
    path: '/login', 
    name: 'Login',
    component:Login // 默认跳转到首页
  },
  { 
    path: '/MainLayout', 
    name: 'MainLayout', 
    component: MainLayout, // 这里加载带有侧边栏的布局
    redirect: '{name: "Home"}', // 默认子路由
    children:[
      {
        path:'home',
        name:'Home',
        component:Home
      },
      { 
        path: 'settings', 
        name: 'Settings', 
        component: Settings 
      },
      { 
        path: 'Going', 
        name: 'Going', 
        component: Go
      },
    ]
  },
  
]

const router = createRouter({
  history: createWebHashHistory(), // 必须用 Hash 模式！
  routes
})

router.beforeEach((to, _from, next) => {
  // 1. 获取本地存储的 token
  const token = localStorage.getItem('token');

  // 2. 判断逻辑
  // 如果要去的地方不是登录页，且没有 token
  if (to.path !== '/login' && !token) {
    // 强制跳转回登录页
    next('/login');
  } else {
    // 否则放行
    next();
  }
});

export default router