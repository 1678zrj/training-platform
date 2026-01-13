import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 1. 创建 axios 实例
const service = axios.create({
  // 这里的 '/api' 配合 vite.config.js 的 proxy 使用
  // 如果是生产环境，这里通常会换成真实域名
  baseURL: '',
  timeout: 25000 // 请求超时时间：25秒
})

// 2. 请求拦截器 (Request Interceptor)
// 作用：在请求发送前，把 Token 塞进去
service.interceptors.request.use(
  (config) => {
    // 每次请求都获取最新的 store
    const userStore = useUserStore()

    // 如果 store 里有 token，就加到 header 里
    if (userStore.token) {
      // 注意：后端 FastAPI OAuth2PasswordBearer 默认要求的格式是 "Bearer <token>"
      // 中间有个空格，千万别漏了
      config.headers.Authorization = `Bearer ${userStore.token}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 3. 响应拦截器 (Response Interceptor)
// 作用：统一处理错误，比如 Token 过期
service.interceptors.response.use(
  (response) => {
    // 如果后端返回 2xx，直接把 data 拿出来
    // 这样你在 .vue 里就不用写 res.data.data 了，直接 res.data
    return response
  },
  (error) => {
    // 处理 HTTP 错误状态码
    const { response } = error

    if (response) {
      switch (response.status) {
        // 401 = 1、账号或密码错误    2、Token 过期或无效
        case 401:

          // 如果是登录接口，直接放行给页面处理
          if (response.config.url.includes('/login')) {
            return Promise.reject(error)
          }


          ElMessage.error('登录已过期，请重新登录')

          // 清理用户信息
          const userStore = useUserStore()
          userStore.logout()

          // 强制跳转登录页
          router.push('/login')
          break

        case 403:
          ElMessage.error('权限不足，无法访问')
          break

        case 404:
          ElMessage.error('请求的资源不存在')
          break

        case 500:
          ElMessage.error('服务器内部错误，请联系管理员')
          break

        default:
          ElMessage.error(response.data.detail || '网络连接异常')
      }
    } else {
      // 没网了，或者超时
      ElMessage.error('网络连接超时或服务器异常')
    }

    return Promise.reject(error)
  }
)

// 导出这个封装好的实例
export default service