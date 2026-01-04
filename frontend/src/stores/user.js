import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref(localStorage.getItem('token') || '')
  const role = ref(Number(localStorage.getItem('role')) || 0) // 0, 1, 2
  const username = ref(localStorage.getItem('username') || '')
  const id = ref(Number(localStorage.getItem("id")) || 0)
  // 动作：登录
  const login = async (loginForm) => {
    // 发送请求
    const res = await axios.post('/api/v1/auth/login', {
      username: loginForm.username,
      password: loginForm.password
    })

    // 更新状态
    token.value = res.data.access_token
    role.value = res.data.role
    username.value = res.data.username // 假设后端也返回了 username
    id.value =res.data.id
    // 持久化保存
    localStorage.setItem('token', token.value)
    localStorage.setItem('role', role.value)
    localStorage.setItem('username', username.value)
  }

  // 动作：登出
  const logout = () => {
    token.value = ''
    role.value = 0
    username.value = ''
    id.value = 0
    localStorage.clear()
  }

  return { token, role, username, id, login, logout }
})