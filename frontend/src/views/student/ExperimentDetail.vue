<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import MarkdownIt from 'markdown-it'
import { RefreshLeft,ArrowLeft } from '@element-plus/icons-vue'
// 引入 github 风格的代码样式
import 'github-markdown-css/github-markdown.css'
import { ElMessageBox,ElMessage } from 'element-plus' // 引入 Loading 服务
import { useUserStore } from '@/stores/user.js'
import request from '@/utils/request.js'

const route = useRoute()
const router = useRouter()
const md = new MarkdownIt() // 初始化解析器
const userStore = useUserStore() // 初始化 Store
const experiment = ref({})
const htmlContent = ref('')
const isLoading = ref(true)

const fetchDetail = async () => {
  try {
    const id = route.params.id
    // 请求后端刚才写的详情接口
    const res = await axios.get(`/api/v1/experiments/${id}`)
    experiment.value = res.data

    // 将 Markdown 转换为 HTML
    htmlContent.value = md.render(res.data.content || '')
  } catch (error) {
    console.error(error)
    htmlContent.value = '<h1>加载失败</h1><p>无法获取实验文档</p>'
  } finally {
    isLoading.value = false
  }
}
// 重置环境逻辑
const resetEnv = async () => {
  try {
    // 二次确认，防止手滑
    await ElMessageBox.confirm(
      '此操作将永久删除您在该实验中保存的所有代码和数据，并恢复到初始状态。是否继续？',
      '危险操作警告',
      {
        confirmButtonText: '确定重置',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    // 发送请求
    await request.post('/api/v1/containers/reset', null, {
      params: { experiment_id: route.params.id }
    })

    ElMessage.success('环境已重置成功，请点击“开始实验”')

  } catch (error) {
    if (error !== 'cancel') {
       // 如果是后端返回 400 (容器正在运行)，拦截器会报错，这里不用额外处理
       console.error(error)
    }
  }
}


// 按钮点击事件
// const startExp = async () => {
//   // 1. 开启全屏 Loading (因为启动容器可能需要 1-3 秒)
//   const loadingInstance = ElLoading.service({
//     lock: true,
//     text: '正在初始化实验环境（分配资源、挂载数据）...',
//     background: 'rgba(0, 0, 0, 0.7)',
//   })
//
//   try {
//     const expId = route.params.id
//     // 2. 请求后端启动容器
//     const res = await axios.post('/api/v1/containers/start', null, {
//       params: {
//         experiment_id: expId,
//         user_id: userStore.id
//       } // 根据 FastAPI 定义，这里用 Query 参数
//     })
//
//     const containerInfo = res.data
//
//     // 3. 拼接跳转 URL
//     // 假设你的服务器 IP 是 localhost (或者从环境变量读)
//     // Jupyter 默认 URL 格式: http://ip:port/?token=xxx
//     const targetUrl = `http://${location.hostname}:${containerInfo.host_port}/?token=${containerInfo.url_token}`
//
//     // 4. 打开新窗口
//     window.open(targetUrl, '_blank')
//
//   } catch (error) {
//     console.error(error)
//     ElMessage.error('环境启动失败，请联系管理员')
//   } finally {
//     loadingInstance.close()
//   }
// }
const startExp = () => {
  // 不再直接发请求，而是跳到 ActiveLab 页面，由那个页面去负责发请求
  // 这样用户体验更好，能看到页面切换
  router.push(`/lab/${route.params.id}`)
}
onMounted(() => {
  fetchDetail()
})

const goBack = () => {
  // router.back()
  // 明确指定要去哪里，不要依赖历史记录
    router.push({ name: 'ExperimentList', params: { id: experiment.category_id || 1 } })
}
</script>

<template>
  <div class="detail-container" v-loading="isLoading">
    <div class="top-bar">
      <el-button link @click="goBack" class="back-btn">
        <el-icon :size="20"><ArrowLeft /></el-icon>
        <span style="margin-left: 4px; font-size: 16px;">返回</span>
      </el-button>
      <div class="divider"></div>
      <span class="page-title">{{ experiment.title }}</span>
    </div>

    <div class="main-layout">
      <div class="content-card">
        <div class="tabs-header">
          <span class="tab-item active">实验内容</span>
          </div>

        <div class="markdown-body" v-html="htmlContent"></div>
      </div>

      <div class="right-sidebar">
        <div class="sidebar-card">
<!--          <h3 class="card-title">学习进度</h3>-->
<!--          <div class="progress-box">-->
<!--            <span class="status-text">未完成</span>-->
<!--            <el-progress :percentage="0" :show-text="false" class="progress-bar"/>-->
<!--            <div class="percent-num">0%</div>-->
<!--          </div>-->
          <el-button type="primary" class="action-btn" @click="startExp()">开始实验 (Docker)</el-button>
          <el-button
          type="warning"
          link
          class="reset-btn"
          @click="resetEnv"
        >
          <el-icon><RefreshLeft /></el-icon>
          <span style="margin-left: 4px">重置环境</span>
        </el-button>
        </div>

<!--        <div class="sidebar-card">-->
<!--          <h3 class="card-title">相关推荐</h3>-->
<!--          <div class="empty-placeholder">暂无推荐</div>-->
<!--        </div>-->
      </div>
    </div>
  </div>
</template>

<style scoped>
.detail-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 顶部栏 */
.top-bar {
  height: 50px;
  background: #fff;
  display: flex;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid #eee;
  margin-bottom: 20px;
  border-radius: 4px;
}

.back-btn { color: #333; }
.back-btn:hover { color: #409EFF; }

.divider {
  width: 1px;
  height: 20px;
  background: #ddd;
  margin: 0 15px;
}

.page-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

/* 主布局：左右结构 */
.main-layout {
  display: flex;
  gap: 20px;
  align-items: flex-start; /* 顶部对齐 */
}

/* 左侧内容卡片 */
.content-card {
  flex: 1; /* 占据剩余空间 */
  background: #fff;
  border-radius: 8px;
  min-height: 500px;
  padding: 0;
  overflow: hidden; /* 防止内容溢出 */
}

.tabs-header {
  padding: 0 30px;
  border-bottom: 1px solid #eee;
  height: 50px;
  display: flex;
  align-items: center;
}

.tab-item {
  margin-right: 30px;
  font-size: 15px;
  cursor: pointer;
  color: #666;
  height: 50px;
  line-height: 50px;
  position: relative;
}

.tab-item.active {
  color: #409EFF;
  font-weight: bold;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: #409EFF;
}

/* Markdown 内容区样式 */
.markdown-body {
  box-sizing: border-box;
  min-width: 200px;
  max-width: 980px;
  margin: 0 auto;
  padding: 45px;
}

/* 右侧侧边栏 */
.right-sidebar {
  width: 300px;
  flex-shrink: 0;
}

.sidebar-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.card-title {
  font-size: 16px;
  font-weight: bold;
  margin: 0 0 15px 0;
  color: #333;
}

.status-text {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
  display: block;
}

.progress-box { margin-bottom: 20px; }
.progress-bar { margin: 10px 0; }
.percent-num { text-align: right; color: #999; font-size: 12px; }

.action-area {
  display: flex;
  flex-direction: column;
  gap: 10px; /* 按钮之间的间距 */
}

.action-btn {
  width: 100%;
  //margin: 0;
}
.reset-btn {
  width: 100%;
  margin: 0;
  color: #E6A23C;
}
.reset-btn:hover {
  color: #b88230;
}


.empty-placeholder { color: #999; font-size: 13px; text-align: center; padding: 20px 0; }
</style>