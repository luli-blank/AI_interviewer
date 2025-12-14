import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'

// 懒加载引入（推荐写法）
const Home = () => import('../views/Home.vue')
const Settings = () => import('../views/Settings.vue')
const Interview_practice = () => import('../views/Interview_practice.vue')
const Login = () => import('../views/Login.vue')
const MainLayout = () => import('../views/MainLayout.vue')
const CreateJob_1 = () => import('../views/CreateJob_1.vue')
const CreateJob_2 = () => import('../views/CreateJob_2.vue')
const CreateJob_3 = () => import('../views/CreateJob_3.vue')
const Interview_Review = () => import('../views/Interview_Review.vue')
const Profile = () => import('../views/Profile.vue')
const Interview = () => import('../views/Interview.vue')
const CharacterTest = () => import('../views/Character_test.vue')
const CharacterTestWirte = () => import('../views/Character_test_write.vue')
const InterviewCharacter = () => import('../views/Character_test_video.vue')
const CharacterTestReport = () => import('../views/Character_test_report.vue')

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
    redirect: {name: "Home"}, // 默认子路由
    children:[
      {
        path:'Home',
        name:'Home',
        component:Home
      },
      { 
        path: 'Settings', 
        name: 'Settings', 
        component: Settings 
      },
      { 
        path: 'Interview_practice', 
        name: 'Interview_practice', 
        component: Interview_practice
      },
      { 
        path: 'CreateJob_1', 
        name: 'CreateJob_1', 
        component: CreateJob_1
      },
      { 
        path: 'CreateJob_2', 
        name: 'CreateJob_2', 
        component: CreateJob_2
      },
      { 
        path: 'CreateJob_3', 
        name: 'CreateJob_3', 
        component: CreateJob_3
      },
      { 
        path: 'Interview_Review', 
        name: 'Interview_Review', 
        component: Interview_Review
      },
      {
        path: 'Interview',
        name: 'Interview',
        component: Interview 
      },
      {
        path: '/Character_test',
        name : 'Character_test',
        component: CharacterTest// 懒加载引入
      },
      {
        path:'/Character_test_write',
        name:'Character_test_write',
        component:CharacterTestWirte
      },
      {
        path:'/Character_test_report',
        name:'Character_test_report',
        component:CharacterTestReport
      },
      {
        path:'/Interview_character',
        name:'Interview_character',
        component:InterviewCharacter
      }
    ]
  },
  {
    path: '/Profile',
    name : 'Profile',
    component: Profile
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