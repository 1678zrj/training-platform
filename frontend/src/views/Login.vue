<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue' // 引入图标
import { ElMessage } from 'element-plus'
import axios from 'axios' // 记得在 script 顶部引入
// 1. 初始化路由工具（用于跳转）
const router = useRouter()

// 2. 定义表单数据
const loginForm = reactive({
  username: '',
  password: ''
})

const isLoading = ref(false) // 按钮加载状态

// 3. 登录逻辑
// 修改 handleLogin 函数
const handleLogin = async () => {
  if (!loginForm.username || !loginForm.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  isLoading.value = true

  try {
    // 发送真实请求
    const res = await axios.post('/api/v1/auth/login', {
      username: loginForm.username,
      password: loginForm.password
    })

    // 登录成功
    ElMessage.success('登录成功')

    // --- 重点：保存 Token ---
    // 以后所有请求都要带上这个 token，后端才知道你是谁
    localStorage.setItem('token', res.data.access_token)
    localStorage.setItem('role', res.data.role)

    router.push('/workspace')

  } catch (error) {
    // 登录失败
    console.error(error)
    const msg = error.response?.data?.detail || '登录失败，请检查网络'
    ElMessage.error(msg)
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="login-container">
    <div class="login-content">
      <div class="login-header">
        <img src="@/assets/logo.svg" alt="logo" class="logo" />
        <h1 class="title">多任务AI全景态势推演实训平台</h1>
        <p class="subtitle">CUP 为了学生更好地学习</p>
      </div>

      <div class="login-card">
        <div class="card-header">
          <span class="active-tab">账户密码登录</span>
        </div>

        <el-form :model="loginForm" class="login-form">
          <el-form-item>
            <el-input
              v-model="loginForm.username"
              placeholder="用户名"
              size="large"
              :prefix-icon="User"
            />
          </el-form-item>

          <el-form-item>
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="密码"
              size="large"
              :prefix-icon="Lock"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <el-button
            type="primary"
            class="login-button"
            :loading="isLoading"
            @click="handleLogin"
            size="large"
          >
            登录
          </el-button>
        </el-form>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 1. 整体背景容器 - 还原那种柔和的渐变背景 */
.login-container {
  height: 100vh;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  /* 这是一个类似于图中的淡紫色/蓝色渐变 */
  background: radial-gradient(circle at 50% 30%, #f0f4ff, #eef1f5);
}

.login-content {
  text-align: center;
  width: 100%;
  max-width: 480px;
  padding: 20px;
  /* --- 新增下面这一行 --- */
  /* 使用 vh (视口高度百分比) 能更好地适配不同屏幕 */
  /* 数值越大，整体越往上移。建议尝试 10vh 到 20vh 之间 */
  margin-bottom: 25vh;
}

/* 2. 头部样式 */
.login-header {
  margin-bottom: 40px;
}

.logo {
  height: 60px; /* 根据实际 Logo 大小调整 */
  margin-bottom: 10px;
}

.title {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin: 10px 0;
  letter-spacing: 1px;
}

.subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

/* 3. 登录框卡片样式 - 悬浮感 */
.login-card {
  background: white;
  padding: 40px;
  border-radius: 8px;
  /* 加上一点阴影，让它浮起来 */
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.card-header {
  margin-bottom: 30px;
  text-align: center;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.active-tab {
  font-size: 16px;
  color: #409EFF; /* Element Plus 的主色蓝 */
  font-weight: 500;
  border-bottom: 2px solid #409EFF;
  padding-bottom: 10px;
  display: inline-block;
  margin-bottom: -11px; /* 让线正好压在边框上 */
}

/* 4. 表单微调 */
.login-form .el-input {
  --el-input-height: 48px; /* 让输入框稍微高一点，更大气 */
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  margin-top: 10px;
  border-radius: 4px;
}
</style>