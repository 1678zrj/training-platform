<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, SwitchButton, Loading } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user.js'
import request from '@/utils/request.js'


const userStore = useUserStore() // 初始化 Store
const route = useRoute()
const router = useRouter()

const iframeUrl = ref('')
const isLoading = ref(true)
const expId = route.params.id
const experimentTitle = ref('正在加载实验环境...') // 可以从路由参数或 Store 获取，这里简化
const loadingText = ref('正在请求实验资源...') // 增加一个动态文案

// --- 核心优化 1: 心跳检测函数 ---
// 尝试连接 Jupyter，直到成功或超时
const waitForJupyter = async (url) => {
  const maxRetries = 50; // Jupyter 启动较慢，建议设大一点，50秒比较稳妥
  const interval = 1000;

  for (let i = 0; i < maxRetries; i++) {
    try {
      loadingText.value = `环境启动中 (${i + 1}s)...`;

      // 1. 去掉 no-cors，我们需要读取 status
      // 2. 如果你的 URL 是带 token 的，直接 fetch 即可
      const res = await fetch(url, {
        method: 'GET',
        credentials: 'omit', // 👈 就加这一行，保平安
        // 如果 Nginx 没有配 CORS 头，可能需要加上 credentials 或 mode，
        // 但通常 Nginx 代理后，前端视为同源，直接 fetch 没问题。
      });

      // 关键判断！
      // Nginx 返回 502 (Bad Gateway) 时，res.ok 为 false
      // 只有当 Jupyter 真正返回 200 OK 时，res.ok 才为 true
      if (res.ok) {
        return true; // 成功！
      }

      // 如果是 502/404/503，说明容器还没准备好，继续等待
      console.log(`Waiting... Status: ${res.status}`);

    } catch (e) {
      // 网络错误（比如 Nginx 还没起，或者断网），也继续等待
      console.log('Network error, retrying...');
    }

    // 等待 1 秒再试
    await new Promise(r => setTimeout(r, interval));
  }

  loadingText.value = "启动超时，请刷新重试";
  return false; // 超时
}
// 1. 初始化：加载容器
const initLab = async () => {
  try {
    // 调用 start 接口。因为后端写了 get_or_create，
    // 所以如果容器已经活着，它会直接返回 URL，不会重复创建，非常安全。
    const res = await request.post('/api/v1/containers/start', null, {
      params: {
        experiment_id: expId
      }
    })
    const containerInfo = res.data
    if (containerInfo.status === 'creating'){
      loadingText.value='排队中，资源分配中'
      await waitForToken(expId)
      return
    }

    const { url_token, base_url } = containerInfo
    // 拼接 Jupyter URL
    // 拼接最终 URL
    // 结果: /lab/u1_e101/?token=xxxx
    const targetUrl = `${base_url}/?token=${url_token}`
    // 2. 开始轮询，直到容器准备好
    const isReady = await waitForJupyter(targetUrl)

    if (isReady) {
      // 3. 只有准备好了，才把 URL 给 iframe，避免白屏或错误页
      iframeUrl.value = targetUrl
    } else {
      throw new Error('容器启动超时')
    }

  } catch (error) {
    console.error(error)
    ElMessage.error('无法连接到实验环境')
    router.back() // 失败直接退回
  } finally {
    isLoading.value = false
  }
}

const waitForToken = async (eid) => {
  const maxRetries = 10

  for (let i = 0; i < maxRetries; i++) {
    // 我们可以复用 /start 接口，或者专门写一个 /status 接口
    // 因为 /start 是 get_or_create，所以查也是它
    const res = await request.post('/api/v1/containers/start', null, {
      params: { experiment_id: eid }
    })

    if (res.data.status === 'running' && res.data.url_token) {
      // 拿到了！重新走正常初始化流程
      // 这里简单处理：直接刷新页面或递归调用
      // 为了代码简单，我们把获取到 Token 后的逻辑提取出来
      const { url_token, base_url } = res.data
      const targetUrl = `${base_url}/?token=${url_token}`
      const isReady = await waitForJupyter(targetUrl)
      if (isReady) {
      // 3. 只有准备好了，才把 URL 给 iframe，避免白屏或错误页
      iframeUrl.value = targetUrl
      } else {
        throw new Error('容器启动超时')
      }
      return
    }

    await new Promise(r => setTimeout(r, 1000))
  }

  throw new Error('获取资源超时')
}


// --- 核心优化 2: 显式跳转 ---
// 解决“点多次才能返回”的问题
const goBack = () => {
  // 不用 router.back()，而是直接指定去哪里
  // 这样无论 iframe 内部跳了多少次，都能一步退出来
  router.push({ name: 'ExperimentDetail', params: { id: expId } })
}

// 3. 结束实验 (关闭容器并返回)
const endLab = () => {
  ElMessageBox.confirm(
    '结束实验将删除当前的运行环境，未保存的数据可能会丢失。确定要结束吗？',
    '警告',
    {
      confirmButtonText: '确定结束',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    // 用户点击确定
    try {
      await request.post('/api/v1/containers/stop', null, {
        params: {
          experiment_id: expId
        }
      })
      ElMessage.success('实验已结束，环境已回收')
      // router.back()
      // 结束也显式跳转
      router.push({ name: 'ExperimentDetail', params: { id: expId } })
    } catch (error) {
      ElMessage.error('结束实验失败，请重试')
    }
  })
}

onMounted(() => {
  initLab()
})
</script>

<template>
  <div class="lab-wrapper">
    <header class="lab-header">
      <div class="left-action">
        <el-button link class="back-btn" @click="goBack">
          <el-icon :size="20"><ArrowLeft /></el-icon>
          <span class="btn-text">返回 (保持运行)</span>
        </el-button>
        <div class="divider"></div>
        <span class="lab-title">{{ experimentTitle }}</span>
      </div>

      <div class="right-action">
        <el-button type="danger" plain size="small" @click="endLab">
          <el-icon><SwitchButton /></el-icon>
          <span style="margin-left: 5px;">结束实验</span>
        </el-button>
      </div>
    </header>

    <div class="lab-body" v-loading="isLoading" element-loading-text="正在启动容器环境...">
      <iframe
        v-if="iframeUrl"
        :src="iframeUrl"
        class="lab-iframe"
        frameborder="0"
        allow="clipboard-read; clipboard-write"
      ></iframe>
    </div>
  </div>
</template>

<style scoped>
.lab-wrapper {
  display: flex;
  flex-direction: column;
  height: 100vh; /* 占满全屏 */
  background-color: #fff;
}

.lab-header {
  height: 50px;
  background-color: #2b2b2b; /* 深色顶栏，专注沉浸感 */
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  flex-shrink: 0;
}

.left-action {
  display: flex;
  align-items: center;
}

.back-btn {
  color: #bbb;
}
.back-btn:hover {
  color: #fff;
}
.btn-text { margin-left: 5px; font-size: 14px; }

.divider {
  width: 1px;
  height: 16px;
  background: #555;
  margin: 0 15px;
}

.lab-title {
  font-size: 14px;
  font-weight: 500;
  color: #fff;
}

.lab-body {
  flex: 1; /* 剩余空间全给 iframe */
  background-color: #f0f0f0;
  overflow: hidden;
  position: relative;
}

.lab-iframe {
  width: 100%;
  height: 100%;
  display: block;
}
</style>