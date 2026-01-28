import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Layout from '../layout/index.vue' // 我们稍后创建这个布局文件
import { useUserStore } from '../stores/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    // 主应用结构
    {
      path: '/',
      component: Layout,
      redirect: '/dashboard', // 默认跳这里，后面守卫会再次重定向
      children: [
        // --- 0级权限：学生页面 ---
        {
          path: 'student',
          name: 'Workspace',
          redirect: '/student/analysis',
          meta: { roles: [0] }, // 只有 0 能进
          children:[
            {
              path:'analysis',
              name:'StudentAnalysis',
              component:() => import('../views/student/Analysis.vue'),
              meta: {title:'学情分析'}
            },
            {
              path:'profile/manage',
              name:'StudentProfileManage',
              component:() =>import('../views/student/ProfileManage.vue'),
              meta:{title: '个人信息管理'}
            },
            {
              path: 'category/:id',
              name: 'ExperimentList',
              component:() => import('../views/student/ExperimentList.vue')
            },
            {
              path: 'submit',
              name: 'StudentSubmitFile',
              component:() => import('../views/student/Submit.vue')
            },
              // 新增：实验详情页 (在 category 之后)
            {
              path: 'experiment/:id',
              name: 'ExperimentDetail',
              component: () => import('../views/student/ExperimentDetail.vue'),
              meta: { title: '实验详情' }
            }
          ]
        },

        // --- 1, 2级权限：通用管理页面 ---
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('../views/admin/Dashboard.vue'), // 概览
          meta: { roles: [1, 2] }
        },
        {
          path: 'course-manage',
          name: 'CourseManage',
          component: () => import('../views/admin/CourseManage.vue'),
          meta: { roles: [1, 2] }
        },
        // --- 2级权限：管理员独有 ---
        {
          path: 'user-manage',
          name: 'UserManage',
          component: () => import('../views/admin/UserManage.vue'),
          meta: { roles: [2] } // 只有 2 能进
        }
      ]
    },
    // [新增] 独立的实训环境页面 (不在 Layout 里面)
    {
      path: '/lab/:id',
      name: 'ActiveLab',
      component: () => import('../views/student/ActiveLab.vue'),
      meta: { roles: [0, 1, 2] } // 权限控制
    },
  ]
})

// --- 全局路由守卫 ---
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const token = userStore.token
  const refresh_token = userStore.refresh_token
  const role = userStore.role
  // console.log("token是:")
  // console.log(token)
  // console.log("refresh_token是:")
  // console.log(refresh_token)
  // // 1. 如果去的是登录页，且已经有 token，直接根据角色跳转
  // if (to.path === '/login' && token) {
  //   if (role === 0) return next('/student/analysis')
  //   return next('/dashboard')
  // }
  //
  // // 2. 如果没有 token，且去的不是登录页 -> 强制去登录
  // if (to.path !== '/login' && !token) {
  //   return next('/login')
  // }
  //
  // // 3. 权限校验 (防止学生手动输入 URL 访问管理页)
  // if (to.meta.roles) {
  //   if (!to.meta.roles.includes(role)) {
  //     // 权限不足，根据角色踢回对应主页
  //     if (role === 0) return next('/student/analysis')
  //     return next('/dashboard')
  //   }
  // }
  //
  // // 4. 放行
  // next()
  //  登录校验完全重写
  // 调试日志 (可选)
  console.log("路由守卫检查:", { path: to.path, token: !!token, refresh: !!refresh_token, role })
  //这里处理去登录页的逻辑
  if (to.path === '/login'){
    // 如果token存在就跳转至主页，无需登录（这里不管是token还是refresh_token都可）
    if (token || refresh_token){
      if (role === 0){
        return next("/student/analysis")
      }
      return next("/dashboard")
    }
    // 没 Token，允许访问登录页
    return next()
  }
  //运行到这里表明用户不是去登录页，存在两种情况
  // 1、token和refresh_token均不存在
  // 2、token或refresh_token存在，那么要进行权限验证
  // 均不存在，老老实实去登录，重新刷新token
  if (!token&&!refresh_token){
    return next("/login")
  }
  //运行到这里说明token存在，那么对于需要特定权限的路径，需要进行权限验证，看用户是否有权限访问该路径
  // 如果该路径设定了权限
  if (to.meta.roles) {
    // 如果该路径不允许当前用户访问，那么跳转到默认主页
    if (!to.meta.roles.includes(role)){
      if (role === 0){
        // 学生跳转的默认主页
        return next('/student/analysis')
      }else {
        // 其它用户跳转的主页
        return next('/dashboard')
      }
    }
    //如果该路径允许当前用户访问，那么直接放行
    else{
      next()
    }
  }
  //允许到这里说明token存在并且路径没有特殊权限要求
  next()


})

export default router