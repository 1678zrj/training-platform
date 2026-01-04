<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, SwitchButton, Loading } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user.js'
const userStore = useUserStore() // 初始化 Store
const route = useRoute()
const router = useRouter()

const iframeUrl = ref('')
const isLoading = ref(true)
const expId = route.params.id
const experimentTitle = ref('正在加载实验环境...') // 可以从路由参数或 Store 获取，这里简化

// 1. 初始化：加载容器
const initLab = async () => {
  try {
    // 调用 start 接口。因为后端写了 get_or_create，
    // 所以如果容器已经活着，它会直接返回 URL，不会重复创建，非常安全。
    const res = await axios.post('/api/v1/containers/start', null, {
      params: {
        experiment_id: expId,
        user_id: userStore.id
      }
    })

    const { host_port, url_token } = res.data
    // 拼接 Jupyter URL
    iframeUrl.value = `http://${location.hostname}:${host_port}/?token=${url_token}`

  } catch (error) {
    console.error(error)
    ElMessage.error('无法连接到实验环境')
    router.back() // 失败直接退回
  } finally {
    isLoading.value = false
  }
}

// 2. 返回上一页 (不关闭容器)
const goBack = () => {
  router.back()
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
      await axios.post('/api/v1/containers/stop', null, {
        params: {
          experiment_id: expId,
          user_id: userStore.id
        }
      })
      ElMessage.success('实验已结束，环境已回收')
      router.back()
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