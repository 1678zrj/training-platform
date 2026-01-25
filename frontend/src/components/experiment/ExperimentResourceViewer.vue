<script setup>
import { computed, ref, defineAsyncComponent, watch, nextTick } from 'vue'
/* Element Plus Icons */
import {
  Document,
  Files,
  VideoCamera,
  Link as LinkIcon,
  Picture,
  ArrowDown
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

<!--<template>-->
<!--  <div class="resource-viewer">-->
<!--    &lt;!&ndash; Tabs &ndash;&gt;-->
<!--    <div class="tabs-header">-->
<!--      <span-->
<!--        v-for="(res, index) in sortedResources"-->
<!--        :key="res.id"-->
<!--        :class="['tab-item', { active: index === activeIndex }]"-->
<!--        @click="activeIndex = index"-->
<!--      >-->
<!--        {{ res.name }}-->
<!--      </span>-->
<!--    </div>-->

<!--    &lt;!&ndash; Content &ndash;&gt;-->
<!--    <div class="resource-content" v-if="activeResource">-->
<!--      <component-->
<!--        :is="viewerMap[activeResource.resource_type]"-->
<!--        :resource="activeResource"-->
<!--      />-->
<!--    </div>-->
<!--    <div v-else class="empty-placeholder">-->
<!--      当前实验暂无资源-->
<!--    </div>-->
<!--  </div>-->
<!--</template>-->
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
  <template v-if="overflowTabs.length">
    <el-tab-pane disabled name="__more">
      <template #label>
        <el-dropdown trigger="click">
          <span class="more-tab">
            更多
            <el-icon><arrow-down /></el-icon>
          </span>

          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item
                v-for="(res, idx) in overflowTabs"
                :key="res.id"
                @click="handleOverflowSelect(idx + maxVisibleTabs)"
              >
                <el-icon class="dropdown-icon">
                  <component :is="iconMap[res.resource_type]" />
                </el-icon>
                {{ res.name }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </template>
    </el-tab-pane>
  </template>

</el-tabs>

<!--<div class="resource-content" v-if="activeResource">-->
<!--  <component-->
<!--    :is="viewerMap[activeResource.resource_type]"-->
<!--    :resource="activeResource"-->
<!--  />-->
<!--</div>-->

<!--<div v-else class="empty-placeholder">-->
<!--  当前实验暂无资源-->
<!--</div>-->
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
</style>