<!--<script setup>-->
<!--import { onMounted, computed } from 'vue'-->
<!--import { useUserStore } from '../stores/user'-->
<!--import { useCategoryStore } from '../stores/category'-->
<!--import { useRouter, useRoute } from 'vue-router'-->
<!--import {-->
<!--  Odometer, User, Reading, Document, Key, Upload, ChatDotRound-->
<!--} from '@element-plus/icons-vue'-->

<!--const userStore = useUserStore()-->
<!--const categoryStore = useCategoryStore()-->
<!--const router = useRouter()-->
<!--const route = useRoute()-->

<!--const role = userStore.role-->

<!--// 初始化时获取分类数据-->
<!--onMounted(() => {-->

<!--    categoryStore.fetchCategories()-->

<!--})-->

<!--const handleLogout = async () => {-->
<!--  // 1. 等待 Pinia 中的 logout 动作彻底完成（包括 finally 里的清空操作）-->
<!--  await userStore.logout()-->

<!--  // 2. 只有 token 清空后，才进行跳转-->
<!--  router.push('/login')-->
<!--}-->

<!--// 侧边栏当前激活项-->
<!--const activeMenu = computed(() => route.path)-->
<!--</script>-->

<!--<template>-->
<!--  <div class="app-layout">-->
<!--    <el-aside width="240px" class="sidebar">-->
<!--      <div class="sidebar-header">-->
<!--        <img src="@/assets/logo.svg" alt="logo" class="logo-img" />-->
<!--        <span class="app-name">实训平台</span>-->
<!--      </div>-->

<!--      <el-menu-->
<!--        :default-active="activeMenu"-->
<!--        class="el-menu-vertical"-->
<!--        router-->
<!--        unique-opened-->
<!--      >-->
<!--        <template v-if="role === 1 || role === 2">-->
<!--           <el-menu-item index="/dashboard">-->
<!--             <el-icon><Odometer /></el-icon>-->
<!--             <span>概览统计</span>-->
<!--           </el-menu-item>-->
<!--        </template>-->
<!--         <el-sub-menu index="resources">-->
<!--            <template #title>-->
<!--              <el-icon><Reading /></el-icon>-->
<!--              <span>教学资源</span>-->
<!--            </template>-->

<!--            <el-menu-item-->
<!--              v-for="cat in categoryStore.categories"-->
<!--              :key="cat.id"-->
<!--              :index="`/category/${cat.id}`"-->
<!--            >-->
<!--              {{ cat.name }}-->
<!--            </el-menu-item>-->
<!--        </el-sub-menu>-->
<!--        <template v-if="role === 0">-->

<!--          <el-menu-item index="/student/analysis">-->
<!--            <el-icon><Odometer /></el-icon>-->
<!--            <span>学情分析</span>-->
<!--          </el-menu-item>-->
<!--          <el-menu-item index="/student/submit">-->
<!--            <el-icon><Upload /></el-icon>-->
<!--            <span>报告提交</span>-->
<!--          </el-menu-item>-->

<!--        </template>-->


<!--        <el-sub-menu index="personal">-->
<!--          <template #title>-->
<!--            <el-icon><User /></el-icon>-->
<!--            <span>个人中心</span>-->
<!--          </template>-->
<!--          <el-menu-item index="/profile/manage">个人信息管理</el-menu-item>-->
<!--        </el-sub-menu>-->

<!--        <el-sub-menu index="ai">-->
<!--          <template #title>-->
<!--            <el-icon><ChatDotRound /></el-icon>-->
<!--            <span>大模型</span>-->
<!--          </template>-->
<!--          <el-menu-item index="/llm/assistant">AI助手</el-menu-item>-->
<!--        </el-sub-menu>-->

<!--      </el-menu>-->
<!--    </el-aside>-->

<!--    <el-container class="main-container">-->
<!--      <el-header class="header">-->
<!--        <div class="breadcrumb">-->
<!--          </div>-->
<!--        <div class="user-info">-->
<!--          <el-avatar :size="32" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />-->
<!--          <span class="username">{{ userStore.username }}</span>-->
<!--          <el-button link type="info" @click="handleLogout">退出</el-button>-->
<!--        </div>-->
<!--      </el-header>-->

<!--      <el-main class="content-wrapper">-->
<!--        <router-view />-->
<!--      </el-main>-->
<!--    </el-container>-->
<!--  </div>-->
<!--</template>-->

<!--<style scoped>-->
<!--.app-layout {-->
<!--  display: flex;-->
<!--  height: 100vh;-->
<!--  background-color: #f5f7fa; /* 整体背景微灰，突出卡片 */-->
<!--}-->

<!--/* 侧边栏样式重置：还原截图的清爽风格 */-->
<!--.sidebar {-->
<!--  background-color: #ffffff;-->
<!--  border-right: 1px solid #e6e6e6;-->
<!--  display: flex;-->
<!--  flex-direction: column;-->
<!--}-->

<!--.sidebar-header {-->
<!--  height: 60px;-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  padding-left: 20px;-->
<!--  border-bottom: 1px solid #f0f0f0;-->
<!--}-->
<!--.logo-img { width: 24px; height: 24px; margin-right: 10px; }-->
<!--.app-name { font-weight: bold; font-size: 16px; color: #333; }-->

<!--/* 去除 Element Menu 默认的右边框 */-->
<!--.el-menu-vertical {-->
<!--  border-right: none;-->
<!--}-->

<!--/* 顶部 Header */-->
<!--.header {-->
<!--  background-color: #fff;-->
<!--  border-bottom: 1px solid #e6e6e6;-->
<!--  display: flex;-->
<!--  justify-content: flex-end; /* 用户信息靠右 */-->
<!--  align-items: center;-->
<!--  padding: 0 20px;-->
<!--  height: 60px;-->
<!--}-->
<!--.user-info { display: flex; align-items: center; gap: 10px; font-size: 14px; }-->

<!--.content-wrapper {-->
<!--  padding: 20px;-->
<!--  /* 这里的背景色决定了右侧内容区的底色 */-->
<!--  background-color: #f5f7fa;-->
<!--}-->
<!--</style>-->
<script setup>
import { onMounted, computed, ref } from 'vue' // 1. 引入 ref
import { useUserStore } from '../stores/user'
import { useCategoryStore } from '../stores/category'
import { useRouter, useRoute } from 'vue-router'
import {
  Odometer, User, Reading, Document, Key, Upload, ChatDotRound,
  Fold, Expand // 2. 引入折叠/展开图标
} from '@element-plus/icons-vue'

const userStore = useUserStore()
const categoryStore = useCategoryStore()
const router = useRouter()
const route = useRoute()

const role = userStore.role

// 3. 定义折叠状态
const isCollapse = ref(false)

// 4. 切换折叠状态的方法
const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

// 初始化时获取分类数据
onMounted(() => {
    categoryStore.fetchCategories()
})

const handleLogout = async () => {
  await userStore.logout()
  router.push('/login')
}

const activeMenu = computed(() => route.path)
</script>

<template>
  <div class="app-layout">
    <el-aside
      :width="isCollapse ? '64px' : '240px'"
      class="sidebar"
    >
      <div class="sidebar-header" :class="{ 'collapsed': isCollapse }">
        <img src="@/assets/logo.svg" alt="logo" class="logo-img" />
        <span class="app-name" v-show="!isCollapse">实训平台</span>
      </div>

      <el-menu
        :default-active="activeMenu"
        class="el-menu-vertical"
        router
        unique-opened
        :collapse="isCollapse"
        :collapse-transition="false"
      >
        <template v-if="role === 1 || role === 2">
           <el-menu-item index="/dashboard">
             <el-icon><Odometer /></el-icon>
             <template #title><span>概览统计</span></template>
           </el-menu-item>
        </template>

         <el-sub-menu index="resources">
            <template #title>
              <el-icon><Reading /></el-icon>
              <span>教学资源</span>
            </template>
            <el-menu-item
              v-for="cat in categoryStore.categories"
              :key="cat.id"
              :index="`/category/${cat.id}`"
            >
              {{ cat.name }}
            </el-menu-item>
        </el-sub-menu>

        <template v-if="role === 0">
          <el-menu-item index="/student/analysis">
            <el-icon><Odometer /></el-icon>
            <template #title><span>学情分析</span></template>
          </el-menu-item>
          <el-menu-item index="/student/submit">
            <el-icon><Upload /></el-icon>
            <template #title><span>报告提交</span></template>
          </el-menu-item>
        </template>

        <el-sub-menu index="personal">
          <template #title>
            <el-icon><User /></el-icon>
            <span>个人中心</span>
          </template>
          <el-menu-item index="/profile/manage">个人信息管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="ai">
          <template #title>
            <el-icon><ChatDotRound /></el-icon>
            <span>大模型</span>
          </template>
          <el-menu-item index="/llm/assistant">AI助手</el-menu-item>
        </el-sub-menu>

      </el-menu>
    </el-aside>

    <el-container class="main-container">
<el-header class="header">
  <div class="header-left">
    <el-icon
      class="trigger-icon"
      @click="toggleSidebar"
      size="22"
    >
      <Expand v-if="isCollapse" />
      <Fold v-else />
    </el-icon>

    <div class="breadcrumb">
      </div>
  </div>

  <div class="user-info">
    <el-avatar :size="32" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
    <span class="username">{{ userStore.username }}</span>
    <el-button link type="info" @click="handleLogout">退出</el-button>
  </div>
</el-header>

      <el-main class="content-wrapper">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  background-color: #f5f7fa;
}

/* Sidebar 增加过渡效果 */
.sidebar {
  background-color: #ffffff;
  border-right: 1px solid #e6e6e6;
  display: flex;
  flex-direction: column;
  transition: width 0.3s; /* 关键：平滑过渡宽度 */
  overflow-x: hidden;     /* 防止折叠过程出现滚动条 */
}

.sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  padding-left: 20px;
  border-bottom: 1px solid #f0f0f0;
  /* 保持 logo 不被压缩 */
  white-space: nowrap;
  overflow: hidden;
}

/* 折叠时 logo 居中 */
.sidebar-header.collapsed {
  padding-left: 0;
  justify-content: center;
}

.logo-img { width: 24px; height: 24px; margin-right: 10px; }
/* 折叠时移除 margin */
.sidebar-header.collapsed .logo-img { margin-right: 0; }

.app-name { font-weight: bold; font-size: 16px; color: #333; }

.el-menu-vertical {
  border-right: none;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  justify-content: space-between; /* 改为两端对齐 */
  align-items: center;
  padding: 0 20px;
  height: 60px;
}

/* 新增 Header 左侧样式 */
.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.trigger-icon {
  cursor: pointer;
  color: #606266;
  transition: color 0.3s;
}
.trigger-icon:hover {
  color: #409EFF;
}

.user-info { display: flex; align-items: center; gap: 10px; font-size: 14px; }

.content-wrapper {
  padding: 20px;
  background-color: #f5f7fa;
}
</style>