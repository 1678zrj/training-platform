<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import VuePdfEmbed from 'vue-pdf-embed'
import {
  ArrowLeft, ArrowRight, ZoomIn, ZoomOut, Download, Refresh
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  resource: {
    type: Object,
    required: true
  }
})

// --- 状态管理 ---
const pdfSource = computed(() => props.resource.file_path_or_url)
const currentPage = ref(1)
const pageCount = ref(0)
const scale = ref(1.0)
const isLoading = ref(true)

// 新增：容器宽度监听，解决初始化不显示的问题
const containerRef = ref(null)
const pdfWidth = ref(null) // 动态绑定宽度
let resizeObserver = null

// --- 事件处理 ---

const handleLoaded = (pdfDocument) => {
  pageCount.value = pdfDocument.numPages
  // 此时不要关闭 loading，等待 rendered
}

const handlePageRendered = () => {
  isLoading.value = false
}

const handleError = (error) => {
  isLoading.value = false
  console.error('PDF Error:', error)
  ElMessage.error('PDF 加载失败')
}

// --- 尺寸监听 (核心修复代码) ---
onMounted(() => {
  if (!containerRef.value) return

  // 创建观察者，监听容器大小变化
  resizeObserver = new ResizeObserver((entries) => {
    for (const entry of entries) {
      const { width } = entry.contentRect
      // 只有当宽度有效且发生变化时才更新
      if (width > 0 && Math.abs(width - pdfWidth.value) > 2) {
        // 使用 nextTick 确保在下一次 DOM 更新周期应用宽度
        nextTick(() => {
            pdfWidth.value = width
            // 如果宽度变化了，且之前卡在 loading，尝试强制重绘
            if(isLoading.value) {
                // 这是一个小技巧：轻微改变 scale 触发重绘，或者什么都不做，
                // 只要 :width 变了，vue-pdf-embed 内部通常会自动重绘
            }
        })
      }
    }
  })

  resizeObserver.observe(containerRef.value)
})

onBeforeUnmount(() => {
  if (resizeObserver) resizeObserver.disconnect()
})

// --- 操作逻辑 ---
const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    isLoading.value = true
  }
}

const nextPage = () => {
  if (currentPage.value < pageCount.value) {
    currentPage.value++
    isLoading.value = true
  }
}

const zoomIn = () => { if (scale.value < 2.5) scale.value += 0.1 }
const zoomOut = () => { if (scale.value > 0.5) scale.value -= 0.1 }
const resetZoom = () => { scale.value = 1.0 }
const downloadPdf = () => { window.open(props.resource.file_path_or_url, '_blank') }

// 监听资源切换
watch(() => props.resource.id, () => {
  isLoading.value = true
  currentPage.value = 1
  scale.value = 1.0
  pageCount.value = 0
})
</script>

<template>
  <div class="pdf-viewer">
    <div class="pdf-toolbar">
      <div class="toolbar-group">
        <el-button-group>
          <el-button :icon="ArrowLeft" :disabled="currentPage <= 1" @click="prevPage" size="small"/>
          <el-button size="small" class="page-indicator">
            {{ currentPage }} / {{ pageCount || '--' }}
          </el-button>
          <el-button :icon="ArrowRight" :disabled="currentPage >= pageCount" @click="nextPage" size="small"/>
        </el-button-group>
      </div>

      <div class="toolbar-group">
        <el-button-group>
          <el-button :icon="ZoomOut" @click="zoomOut" size="small" />
          <el-button @click="resetZoom" size="small" class="zoom-text">
            {{ Math.round(scale * 100) }}%
          </el-button>
          <el-button :icon="ZoomIn" @click="zoomIn" size="small" />
        </el-button-group>
        <el-divider direction="vertical" />
        <el-button :icon="Download" circle size="small" @click="downloadPdf" />
      </div>
    </div>

    <div
      class="pdf-container"
      ref="containerRef"
      v-loading="isLoading"
      element-loading-text="正在加载文档..."
    >
      <div class="pdf-wrapper" :style="{ transform: `scale(${scale})` }">
        <VuePdfEmbed
          v-if="pdfSource && pdfWidth"
          :source="pdfSource"
          :page="currentPage"
          :width="pdfWidth"
          @loaded="handleLoaded"
          @rendered="handlePageRendered"
          @loading-failed="handleError"
          class="vue-pdf-content"
        />
        </div>
    </div>
  </div>
</template>

<style scoped>
.pdf-viewer {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 400px;
}

.pdf-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  z-index: 10;
}

.pdf-container {
  flex: 1;
  background-color: #525659;
  overflow: auto;
  display: flex;
  justify-content: center;
  padding: 20px;
  position: relative;
}

.pdf-wrapper {
  transform-origin: top center;
  transition: transform 0.1s ease; /* 缩短过渡时间，防止缩放延迟 */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  background: #fff;
}

.vue-pdf-content {
    display: block;
}
</style>