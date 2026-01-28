// import axios from 'axios'
// import { useUserStore } from '@/stores/user'
// import { ElMessage } from 'element-plus'
// import router from '@/router'
//
// // 1. 创建 axios 实例
// const service = axios.create({
//   // 这里的 '/api' 配合 vite.config.js 的 proxy 使用
//   // 如果是生产环境，这里通常会换成真实域名
//   baseURL: '/api/v1',
//   timeout: 25000 // 请求超时时间：25秒
// })
//
// // 2. 请求拦截器 (Request Interceptor)
// // 作用：在请求发送前，把 Token 塞进去
// service.interceptors.request.use(
//   (config) => {
//     // 每次请求都获取最新的 store
//     const userStore = useUserStore()
//
//     // 如果 store 里有 token，就加到 header 里
//     if (userStore.token) {
//       // 注意：后端 FastAPI OAuth2PasswordBearer 默认要求的格式是 "Bearer <token>"
//       // 中间有个空格，千万别漏了
//       config.headers.Authorization = `Bearer ${userStore.token}`
//     }
//
//     return config
//   },
//   (error) => {
//     return Promise.reject(error)
//   }
// )
//
// // 3. 响应拦截器 (Response Interceptor)
// // 作用：统一处理错误，比如 Token 过期
// service.interceptors.response.use(
//   (response) => {
//     // 如果后端返回 2xx，直接把 data 拿出来
//     // 这样你在 .vue 里就不用写 res.data.data 了，直接 res.data
//     return response
//   },
//   (error) => {
//     // 处理 HTTP 错误状态码
//     const { response } = error
//
//     if (response) {
//       switch (response.status) {
//         // 401 = 1、账号或密码错误    2、Token 过期或无效
//         case 401:
//
//           // 如果是登录接口，直接放行给页面处理
//           if (response.config.url.includes('/login')) {
//             return Promise.reject(error)
//           }
//
//
//           ElMessage.error('登录已过期，请重新登录')
//
//           // 清理用户信息
//           const userStore = useUserStore()
//           userStore.logout()
//
//           // 强制跳转登录页
//           router.push('/login')
//           break
//
//         case 403:
//           ElMessage.error('权限不足，无法访问')
//           break
//
//         case 404:
//           ElMessage.error('请求的资源不存在')
//           break
//
//         case 500:
//           ElMessage.error('服务器内部错误，请联系管理员')
//           break
//
//         default:
//           ElMessage.error(response.data.detail || '网络连接异常')
//       }
//     } else {
//       // 没网了，或者超时
//       ElMessage.error('网络连接超时或服务器异常')
//     }
//
//     return Promise.reject(error)
//   }
// )
//
// // 导出这个封装好的实例
// export default service
import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 1. 创建 axios 实例
const service = axios.create({
  baseURL: '/api/v1', // 你的基础路径
  timeout: 25000
})

// --- 并发锁变量 ---
let isRefreshing = false
let requests = []

// 2. 请求拦截器
service.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()

    // 排除刷新 Token 的接口，避免死循环 (防止 headers 里带上过期的 access_token)
    if (userStore.token && !config.url.includes('/auth/refresh')) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 3. 响应拦截器
service.interceptors.response.use(
  (response) => {
    // 2xx 正常响应直接返回 data，保留你原来的习惯
    return response
  },
  async (error) => {
    const { response } = error
    const originalRequest = error.config
    const userStore = useUserStore()

    if (response) {
      switch (response.status) {
        case 401:
          // A. 如果是登录接口本身的 401，直接报错，不走刷新逻辑
          if (originalRequest.url.includes('/login')) {
            ElMessage.error('用户名或密码错误')
            return Promise.reject(error)
          }

          // B. 如果是“刷新 Token”接口本身的 401 (说明 Refresh Token 也过期了)
          if (originalRequest.url.includes('/auth/refresh')) {
            userStore.logout()
            router.push('/login')
            ElMessage.error('登录凭证已失效，请重新登录')
            return Promise.reject(error)
          }

          // C. 核心逻辑：Access Token 过期，自动刷新
          // 如果当前没有在刷新，且不是重试过的请求
          if (!originalRequest._retry) {

            if (isRefreshing) {
              // 如果正在刷新，将请求挂起放入队列
              return new Promise((resolve) => {
                requests.push((token) => {
                  originalRequest.headers.Authorization = `Bearer ${token}`
                  resolve(service(originalRequest))
                })
              })
            }

            // 开启刷新状态
            originalRequest._retry = true
            isRefreshing = true

            try {
              // 发起刷新请求
              // 注意：这里我们使用 refresh_token 去后端换新 access_token
              const { data } = await axios.post('/api/v1/auth/refresh', {
                refresh_token: userStore.refresh_token
              })

              // 假设后端返回结构是 { accessToken: "..." }，根据你之前的 Python 代码调整
              const newAccessToken = data.access_token

              // 更新 Pinia 和 LocalStorage
              userStore.setToken(newAccessToken)

              // 执行队列中的请求
              requests.forEach((cb) => cb(newAccessToken))
              requests = []

              // 重发当前失败的请求
              originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
              return service(originalRequest)

            } catch (refreshError) {
              // 刷新失败（Refresh Token 过期或无效）
              userStore.logout()
              router.push('/login')
              ElMessage.error('登录已过期，请重新登录')

              // 清空队列
              requests.forEach(cb => cb(null))
              requests = []

              return Promise.reject(refreshError)
            } finally {
              isRefreshing = false
            }
          }
          break

        case 403:
          ElMessage.error('权限不足，无法访问')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(response.data.detail || '系统异常')
      }
    } else {
      ElMessage.error('网络连接超时或服务器异常')
    }

    return Promise.reject(error)
  }
)

export default service