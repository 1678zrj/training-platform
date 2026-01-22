<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'
import MarkdownIt from 'markdown-it'

const props = defineProps({
  resource: {
    type: Object,
    required: true
  }
})

/* ---------------- 状态 ---------------- */
const loading = ref(false)
const error = ref(null)
const rawContent = ref('')

/* ---------------- Markdown 渲染 ---------------- */
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
})

const renderedHtml = ref('')

/* ---------------- 请求后端 ---------------- */
const fetchMarkdown = async () => {
  if (!props.resource?.id) return

  loading.value = true
  error.value = null

  try {
    const res = await axios.get(
      `/api/v1/experiment-resources/${props.resource.id}/content`,
      {
        headers: {
          Accept: 'text/plain'
        }
      }
    )

    rawContent.value = res.data
    renderedHtml.value = md.render(res.data)
  } catch (e) {
    error.value = 'Markdown 内容加载失败'
    renderedHtml.value = ''
  } finally {
    loading.value = false
  }
}

/* ---------------- 监听资源变化 ---------------- */
watch(
  () => props.resource.id,
  () => {
    fetchMarkdown()
  },
  { immediate: true }
)
</script>

<template>
  <div class="markdown-viewer">
    <div v-if="loading" class="loading">
      正在加载 Markdown 内容…
    </div>

    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <div
      v-else
      class="markdown-content"
      v-html="renderedHtml"
    />
  </div>
</template>

<style scoped>
.markdown-viewer {
  padding: 16px;
  line-height: 1.7;
}

.loading {
  color: #666;
}

.error {
  color: #d93026;
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3) {
  margin-top: 1.2em;
}

.markdown-content :deep(pre) {
  background: #f6f8fa;
  padding: 12px;
  overflow-x: auto;
  border-radius: 4px;
}

.markdown-content :deep(code) {
  background: #f6f8fa;
  padding: 2px 4px;
  border-radius: 3px;
}
</style>
