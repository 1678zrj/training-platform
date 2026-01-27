<script setup>
import { computed, ref, defineAsyncComponent, watch, nextTick } from 'vue'
/* Element Plus Icons */
import {
  Document,
  Files,
  VideoCamera,
  Link as LinkIcon,
  Picture,
  ArrowDown,
  Check
} from '@element-plus/icons-vue'
import MarkdownViewer from './viewers/MarkdownViewer.vue'
import LinkViewer from './viewers/LinkViewer.vue'
const PdfViewer = defineAsyncComponent(() =>
  import('./viewers/PdfViewer.vue')
)

const VideoViewer = defineAsyncComponent(() =>
  import('./viewers/VideoViewer.vue')
)

const ImageViewer = defineAsyncComponent(() =>
  import('./viewers/ImageViewer.vue')
)
const activeName = ref('0')
const props = defineProps({
  resources: {
    type: Array,
    required: true
  }
})

const sortedResources = computed(() =>
  [...props.resources].sort((a, b) => a.sort_order - b.sort_order)
)
const isOverflowActive = computed(() => {
  const current = Number(activeName.value)
  return current >= maxVisibleTabs
})


const activeIndex = ref(0)

// const activeResource = computed(() => sortedResources.value[activeIndex.value])
const activeResource = computed(() => {
  return sortedResources.value[Number(activeName.value)]
})
const viewerMap = {
  markdown: MarkdownViewer, // 同步（体积小）
  pdf: PdfViewer,           // 异步
  video: VideoViewer,       // 异步
  link: LinkViewer,         // 同步
  image: ImageViewer        // 异步
}

/* resource_type -> icon 组件 */
const iconMap = {
  markdown: Files,
  pdf: Document,
  video: VideoCamera,
  link: LinkIcon,
  image: Picture
}

const typeLabelMap = {
  markdown: 'Markdown 文档',
  pdf: 'PDF 文档',
  video: '视频资源',
  link: '外部链接',
  image: '图片资源'
}

const contentRef = ref(null)
/* 最多显示的 Tab 数 */
const maxVisibleTabs = 5

const visibleTabs = computed(() =>
  sortedResources.value.slice(0, maxVisibleTabs)
)

const overflowTabs = computed(() =>
  sortedResources.value.slice(maxVisibleTabs)
)

/* 下拉菜单点击 */
const handleOverflowSelect = (index) => {
  activeName.value = String(index)
}

// 监听资源列表的变化
watch(
  () => props.resources,
  (newVal) => {
    // 只要资源列表变了，就重置回第一个 Tab
    // 这里也可以加个判断，只有当当前索引超出新列表长度时才重置，
    // 但通常切换实验后直接回到第一个资源体验更好。
    activeName.value = '0'
  }
)

/* Tab 切换后滚动到顶部 */
watch(activeName, async () => {
  await nextTick()

  if (contentRef.value) {
    contentRef.value.scrollTo({
      top: 0,
      behavior: 'smooth'
    })
  } else {
    /* 兜底：如果内容区没滚动条 */
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    })
  }
})

</script>


<template>
<el-tabs
  v-model="activeName"
  type="card"
  class="resource-tabs"
>
  <el-tab-pane
    v-for="(res, index) in visibleTabs"
    :key="res.id"
    :name="String(index)"
  >
  <!-- 正常显示的 Tabs -->
    <template #label>
      <el-tooltip
        :content="typeLabelMap[res.resource_type]"
        placement="top"
        effect="dark"
      >
        <span class="tab-label">
          <el-icon class="tab-icon">
            <component :is="iconMap[res.resource_type]" />
          </el-icon>
          <span class="tab-text">{{ res.name }}</span>
        </span>
      </el-tooltip>
    </template>

  </el-tab-pane>
<!-- More 下拉 Tab（仅当溢出时显示） -->
<!--  <template v-if="overflowTabs.length">-->
<!--    <el-tab-pane disabled name="__more">-->
<!--      <template #label>-->
<!--        <el-dropdown trigger="click">-->
<!--          <span-->
<!--              class="more-tab"-->
<!--              :class="{ 'is-active': isOverflowActive }"-->
<!--          >-->
<!--            更多-->
<!--            <el-icon><arrow-down /></el-icon>-->
<!--          </span>-->

<!--          <template #dropdown>-->
<!--            <el-dropdown-menu>-->
<!--              <el-dropdown-item-->
<!--                v-for="(res, idx) in overflowTabs"-->
<!--                :key="res.id"-->
<!--                @click="handleOverflowSelect(idx + maxVisibleTabs)"-->
<!--                class="resource-dropdown-item"-->
<!--                :class="{ 'is-selected': activeName === String(idx + maxVisibleTabs) }"-->

<!--              >-->
<!--                <div class="dropdown-item-content">-->
<!--                  <div class="left-col">-->
<!--                    <el-icon class="dropdown-icon">-->
<!--                      <component :is="iconMap[res.resource_type]"-->
<!--                      />-->
<!--                    </el-icon>-->
<!--                    <span>{{ res.name }}</span>-->
<!--                  </div>-->
<!--                  <el-icon v-if="activeName === String(idx + maxVisibleTabs)" class="check-icon">-->
<!--                    <Check />-->
<!--                  </el-icon>-->
<!--                </div>-->
<!--              </el-dropdown-item>-->
<!--            </el-dropdown-menu>-->
<!--          </template>-->
<!--        </el-dropdown>-->
<!--      </template>-->
<!--    </el-tab-pane>-->
<!--  </template>-->
<template v-if="overflowTabs.length">
  <el-tab-pane disabled name="__more">
    <template #label>
      <el-dropdown trigger="click">
        <span class="more-tab" :class="{ 'is-active': isOverflowActive }">
          更多
          <el-icon><arrow-down /></el-icon>
        </span>

        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item
              v-for="(res, idx) in overflowTabs"
              :key="res.id"
              @click="handleOverflowSelect(idx + maxVisibleTabs)"
              class="resource-dropdown-item"
              :class="{ 'is-selected': activeName === String(idx + maxVisibleTabs) }"
            >
              <el-tooltip
                :content="typeLabelMap[res.resource_type]"
                placement="left"
                effect="dark"
                :enterable="false"
              >
                <div class="dropdown-item-content">
                  <div class="left-col">
                    <el-icon class="dropdown-icon">
                      <component :is="iconMap[res.resource_type]" />
                    </el-icon>
                    <span>{{ res.name }}</span>
                  </div>
                  <el-icon v-if="activeName === String(idx + maxVisibleTabs)" class="check-icon">
                    <Check />
                  </el-icon>
                </div>
              </el-tooltip>

            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </template>
  </el-tab-pane>
</template>
</el-tabs>

  <!-- 内容区域 -->
<div
    class="resource-content"
    v-if="activeResource"
    ref = "contentRef"
>
  <Transition name="fade-slide" mode="out-in">
    <KeepAlive>
      <Suspense>
        <component
          :is="viewerMap[activeResource.resource_type]"
          :key="activeResource.id"
          :resource="activeResource"
        />

        <!-- loading fallback -->
        <template #fallback>
          <div class="viewer-loading">
            正在加载资源...
          </div>
        </template>
      </Suspense>
    </KeepAlive>
  </Transition>
</div>

</template>


<style scoped>
.resource-tabs {
  --el-tabs-header-height: 40px;
}

.resource-content {
  padding: 16px;
  background-color: #ffffff;
  border: 1px solid var(--el-border-color-light);
  border-top: none;
  border-radius: 0 0 6px 6px;
  max-height: 600px;
  overflow-y: auto;
}

.resource-tabs {
  --el-tabs-header-height: 40px;
}

/* Tab label 布局 */
.tab-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

/* 图标尺寸 */
.tab-icon {
  font-size: 16px;
}

/* 内容区域 */
.resource-content {
  padding: 16px;
  background-color: #ffffff;
  border: 1px solid var(--el-border-color-light);
  border-top: none;
  border-radius: 0 0 6px 6px;
  min-height: 200px;
}

/* 空状态 */
.empty-placeholder {
  padding: 40px 0;
  text-align: center;
  color: #909399;
}
.tab-label {
  cursor: pointer;
}
/* 淡入 + 轻微位移 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.2s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(6px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* loading 占位 */
.viewer-loading {
  padding: 40px 0;
  text-align: center;
  color: #909399;
  font-size: 14px;
}

.more-tab {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 0 4px;
  cursor: pointer;
  color: var(--el-text-color-regular);
}

.more-tab:hover {
  color: var(--el-color-primary);
}

.dropdown-icon {
  margin-right: 6px;
}
/* More 标签高亮状态 */
.more-tab.is-active {
  color: var(--el-color-primary);
  font-weight: 600;
}

/* 下拉菜单项布局调整 */
.resource-dropdown-item {
  /* 确保 item 能够撑开布局 */
  min-width: 150px;
  padding: 0 !important; /* 清除默认 padding，由内部 content 控制 */
}

/* 使用 Flex 布局让图标和对勾对齐 */
.dropdown-item-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 5px 16px; /* 恢复 Element Plus 默认的 padding */
  box-sizing: border-box;
  min-width: 160px; /* 稍微宽一点，防止 Tooltip 闪烁 */
}

.left-col {
  display: flex;
  align-items: center;
}

/* 下拉菜单选中状态 */
:deep(.el-dropdown-menu__item.is-selected) {
  color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9); /* 浅色背景更明显 */
}

.check-icon {
  margin-left: 12px;
  font-size: 14px;
}
</style>