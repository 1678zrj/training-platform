<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/preview.css' // 引入预览样式
import { ElMessage } from 'element-plus'

const props = defineProps({
  resource: {
    type: Object,
    required: true
  }
})

const textContent = ref('')
const loading = ref(false)
const id = 'preview-only' // 必须提供一个 id

const fetchMarkdown = async () => {
  if (!props.resource?.id) return
  loading.value = true
  textContent.value = '' // 清空

  try {
    const res = await axios.get(
      `/api/v1/experiment-resources/${props.resource.id}/content`,
      { headers: { Accept: 'text/plain' } }
    )
    textContent.value = res.data || ''
  } catch (e) {
    console.error(e)
    ElMessage.error('文档资源加载失败')
    textContent.value = '> 文档加载失败'
  } finally {
    loading.value = false
  }
}

watch(() => props.resource.id, () => fetchMarkdown(), { immediate: true })
</script>

<template>
  <div class="markdown-viewer-container">
    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="10" animated />
    </div>

    <MdPreview
      v-else
      :editorId="id"
      :modelValue="textContent"
      class="preview-wrapper"
      codeTheme="atom"
      :showCodeRowNumber="true"
    />
  </div>
</template>

<style scoped>
.markdown-viewer-container {
  background-color: #fff;
  min-height: 400px;
}
.loading-state {
  padding: 24px;
}
/* 微调 md-editor-v3 的背景，使其融入你的卡片 */
.preview-wrapper {
  padding: 24px 32px;
}
</style>