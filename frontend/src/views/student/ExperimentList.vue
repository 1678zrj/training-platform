<script setup>
import { ref, watch, onMounted, computed } from 'vue' // 1. 引入 computed
import { useRoute } from 'vue-router'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useCategoryStore } from '@/stores/category.js' // 2. 引入 Category Store
const route = useRoute()
const router = useRouter()
const categoryStore = useCategoryStore() // 3. 初始化 Store
const experiments = ref([])
// const imgBaseUrl = import.meta.env.VITE_DATA_BASE_URL || 'http://127.0.0.1:8000/media'
const imgBaseUrl = import.meta.env.VITE_DATA_BASE_URL || '/media'

// 4. 使用 computed 自动计算标题
// 逻辑：拿着当前路由的 id，去 store 的 categories 数组里找对应的名字
const categoryTitle = computed(() => {
  const currentId = Number(route.params.id) // 路由参数是字符串，需转数字
  const target = categoryStore.categories.find(c => c.id === currentId)
  return target ? target.name : '加载中...'
})
const fetchExperiments = async (categoryId) => {
   try {
     const res = await axios.get(`/api/v1/experiments/?category_id=${categoryId}`)
     experiments.value = res.data
     // 如果你需要分类标题，可以再发一个请求查 category 详情，或者从 store 里找
   } catch (e) {
     console.error(e)
   }
}

// 1. 组件挂载时加载数据
onMounted(() => {
  if (categoryStore.categories.length === 0) {
    categoryStore.fetchCategories()
  }
  fetchExperiments(route.params.id)
})

// 2. [关键] 监听路由参数变化
// 当用户从 "人工智能原理" 点到 "人工智能通讯" 时，组件不会销毁重建，
// 只是路由参数变了，所以必须 watch
watch(
  () => route.params.id,
  (newId) => {
    fetchExperiments(newId)
  }
)

const startLab = (expId) => {
  console.log('进入实训:', expId)
  // 这里以后写 router.push 去具体的实验操作台
  router.push(`/student/experiment/${expId}`)
}
</script>

<template>
  <div class="exp-list-container">
    <div class="page-header">
      <span class="sub-title">教学资源 / </span>
      <span class="main-title">{{ categoryTitle }}</span>
    </div>



    <div class="card-list">
      <div v-for="exp in experiments" :key="exp.id" class="exp-card">
        <div class="card-img">
          <img :src="`${imgBaseUrl}${exp.image_path}`" alt="cover" style="width: 100%; height: 100%; object-fit: cover;" />
        </div>

        <div class="card-info">
          <h3 class="exp-title">{{ exp.title }}</h3>

          <p class="exp-desc">简介：{{ exp.description }}</p>
        </div>

        <div class="card-action">
          <el-tag size="small" type="info" class="status-tag">{{ exp.status }}</el-tag>
          <el-button type="primary" link @click="startLab(exp.id)">进入实训</el-button>
        </div>
      </div>
    </div>

    <el-empty v-if="experiments.length === 0" description="暂无实验项目" />
  </div>
</template>

<style scoped>
/* 还原截图中的卡片样式 */
.page-header {
  margin-bottom: 20px;
  font-size: 14px;
  color: #666;
}
.main-title { font-weight: bold; color: #333; }

.section-title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 20px;
}

.exp-card {
  display: flex;
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  /* 简单的阴影 */
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.exp-card:hover {
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.1);
}

.card-img {
  width: 200px;
  height: 120px;
  background-color: #eee;
  border-radius: 4px;
  overflow: hidden;
  margin-right: 20px;
  flex-shrink: 0;
}

.card-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.exp-title {
  font-size: 18px;
  font-weight: bold;
  margin: 0 0 10px 0;
}

.exp-meta {
  font-size: 13px;
  color: #666;
  margin: 2px 0;
}

.exp-desc {
  font-size: 13px;
  color: #888;
  margin-top: 8px;
  /* 超过两行显示省略号 */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-action {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-end;
  min-width: 100px;
  padding-left: 20px;
}

.status-tag { margin-bottom: 10px; }
</style>