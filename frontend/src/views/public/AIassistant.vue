<template>
  <div class="ai-assistant-container">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h3>🛠️ 工具箱 (Tools)</h3>
        <p class="subtitle">选择模型可调用的能力</p>
      </div>

      <div class="tools-list">
        <div
          v-for="tool in availableTools"
          :key="tool.id"
          class="tool-item"
          :class="{ active: selectedToolIds.includes(tool.id) }"
        >
          <label>
            <input
              type="checkbox"
              :value="tool.id"
              v-model="selectedToolIds"
            >
            <span class="tool-name">{{ tool.name }}</span>
          </label>
          <p class="tool-desc">{{ tool.description }}</p>
        </div>
      </div>

      <div class="status-panel">
        <p>当前已启用: <strong>{{ selectedToolIds.length }}</strong> 个工具</p>
      </div>
    </aside>

    <main class="chat-area">
      <div class="chat-header">
        <h2>AI 助手 (Streaming)</h2>
        <button @click="clearChat" class="clear-btn">清空对话</button>
      </div>

      <div class="messages-container" ref="messagesRef">
        <div
          v-for="(msg, index) in chatHistory"
          :key="index"
          class="message-wrapper"
          :class="msg.role"
        >
          <div class="avatar">{{ msg.role === 'user' ? '🧑‍💻' : '🤖' }}</div>
          <div class="message-content">
            <div v-if="msg.role === 'user'" class="text user-text">{{ msg.content }}</div>

            <div v-else class="text assistant-text">
              <div
                class="markdown-body"
                v-html="renderMarkdown(msg.content)"
              ></div>
              <span v-if="isLoading && index === chatHistory.length - 1" class="cursor"></span>
            </div>

            <div v-if="msg.toolCalls && msg.toolCalls.length" class="tool-usage-log">
              <span class="badge">🔧 调用工具: {{ msg.toolCalls.join(', ') }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="input-area">
        <textarea
          v-model="userInput"
          @keydown.enter.prevent="handleSend"
          placeholder="输入消息... (Shift + Enter 换行)"
          rows="3"
        ></textarea>
        <button
          @click="handleSend"
          :disabled="isLoading || !userInput.trim()"
          class="send-btn"
        >
          {{ isLoading ? '生成中...' : '发送' }}
        </button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick } from 'vue';
// 1. 引入 Markdown 解析器和高亮库
import MarkdownIt from 'markdown-it';
import hljs from 'highlight.js';
import 'highlight.js/styles/github-dark.css'; // 引入代码高亮样式

// 2. 配置 Markdown 解析器
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return '<pre class="hljs"><code>' +
               hljs.highlight(str, { language: lang, ignoreIllegals: true }).value +
               '</code></pre>';
      } catch (__) {}
    }
    return '<pre class="hljs"><code>' + md.utils.escapeHtml(str) + '</code></pre>';
  }
});

// 数据定义
const availableTools = reactive([
  { id: 'web_search', name: '联网搜索', description: '允许模型搜索实时互联网信息。' },
  { id: 'calculator', name: '计算器', description: '进行精确的数学计算。' },
  { id: 'database_query', name: '数据库查询', description: '访问项目内部知识库数据。' },
  { id: 'code_interpreter', name: 'Python解释器', description: '编写并运行 Python 代码进行分析。' }
]);

const selectedToolIds = ref(['web_search']);
const chatHistory = ref([
  { role: 'assistant', content: '你好！我是支持 **Markdown** 和 **流式输出** 的 AI 助手。\n\n你可以尝试让我写一段代码，例如：\n```python\nprint("Hello World")\n```' }
]);

const userInput = ref('');
const isLoading = ref(false);
const messagesRef = ref(null);

// 渲染 Markdown 辅助函数
const renderMarkdown = (text) => {
  return md.render(text || '');
};

const scrollToBottom = async () => {
  await nextTick();
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight;
  }
};

const clearChat = () => {
  chatHistory.value = [];
};

// --- 核心流式传输逻辑 ---

// 模拟后端流式响应生成器
// 在真实场景中，这里会被 fetch API 的 reader 替代
async function* mockStreamGenerator(userContent, tools) {
  // 模拟思考延迟
  await new Promise(r => setTimeout(r, 600));

  const responseText = `收到消息："${userContent}"。\n\n根据配置，已激活 **${tools.length}** 个工具。\n\n以下是一段流式生成的模拟代码：\n\n\`\`\`javascript\nconst stream = true;\nconsole.log("Streaming works!");\n\`\`\`\n\n希望这对你有帮助！`;

  const chunks = responseText.split(''); // 将文本拆分为字符模拟网络包

  for (const chunk of chunks) {
    // 模拟网络抖动 (10ms - 50ms)
    await new Promise(r => setTimeout(r, Math.random() * 40 + 10));
    yield chunk;
  }
}

const handleSend = async () => {
  const content = userInput.value.trim();
  if (!content || isLoading.value) return;

  // 1. 用户消息上屏
  chatHistory.value.push({ role: 'user', content });
  userInput.value = '';
  isLoading.value = true;
  await scrollToBottom();

  // 2. 创建一个空的 Assistant 消息用于接收流
  const assistantMsg = reactive({
    role: 'assistant',
    content: '',
    toolCalls: []
  });
  chatHistory.value.push(assistantMsg);

  try {
    // ---------------------------------------------------------
    // 场景 A: 模拟流式 (本地开发测试用)
    // ---------------------------------------------------------
    const stream = mockStreamGenerator(content, selectedToolIds.value);

    for await (const chunk of stream) {
      assistantMsg.content += chunk;
      scrollToBottom(); // 实时跟随滚动
    }

    // ---------------------------------------------------------
    // 场景 B: 真实后端对接代码 (参考用，解开注释即可使用)
    // ---------------------------------------------------------
    /*
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: chatHistory.value, stream: true })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const text = decoder.decode(value, { stream: true });
      // 假设后端返回格式为 SSE (data: "content")，需根据实际协议解析
      assistantMsg.content += text;
      scrollToBottom();
    }
    */

    // 模拟随机工具调用显示
    if (selectedToolIds.value.length > 0 && Math.random() > 0.7) {
      assistantMsg.toolCalls = [selectedToolIds.value[0]];
    }

  } catch (error) {
    console.error('Stream Error:', error);
    assistantMsg.content += '\n\n[出错了，请稍后再试]';
  } finally {
    isLoading.value = false;
    await scrollToBottom();
  }
};
</script>

<style scoped>
/* 保持原有布局样式不变，新增 Markdown 相关样式 */

/* ... (原有 .ai-assistant-container, .sidebar 等样式请保留，此处省略以节省篇幅) ... */

.ai-assistant-container {
  display: flex;
  height: 80vh;
  width: 100%;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background-color: #f9fafb;
}
/* 侧边栏样式 */
.sidebar { width: 280px; background-color: #ffffff; border-right: 1px solid #e5e7eb; display: flex; flex-direction: column; padding: 20px; }
.sidebar-header h3 { margin: 0; font-size: 1.1rem; color: #1f2937; }
.subtitle { font-size: 0.85rem; color: #6b7280; margin-top: 4px; }
.tools-list { flex: 1; overflow-y: auto; margin-top: 20px; }
.tool-item { padding: 12px; margin-bottom: 10px; border: 1px solid #f3f4f6; border-radius: 8px; transition: all 0.2s; }
.tool-item:hover { background-color: #f9fafb; }
.tool-item.active { border-color: #3b82f6; background-color: #eff6ff; }
.tool-item label { display: flex; align-items: center; cursor: pointer; font-weight: 600; font-size: 0.95rem; color: #374151; }
.tool-item input { margin-right: 10px; }
.tool-desc { margin: 6px 0 0 24px; font-size: 0.8rem; color: #6b7280; line-height: 1.4; }
.status-panel { margin-top: auto; padding-top: 15px; border-top: 1px solid #e5e7eb; font-size: 0.85rem; color: #4b5563; }

/* 聊天区域 */
.chat-area { flex: 1; display: flex; flex-direction: column; background-color: #fff; }
.chat-header { padding: 15px 20px; border-bottom: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center; }
.chat-header h2 { margin: 0; font-size: 1.2rem; }
.clear-btn { background: none; border: none; color: #ef4444; cursor: pointer; }
.messages-container { flex: 1; padding: 20px; overflow-y: auto; background-color: #f3f4f6; }
.message-wrapper { display: flex; margin-bottom: 20px; align-items: flex-start; }
.message-wrapper.user { flex-direction: row-reverse; }
.avatar { width: 36px; height: 36px; border-radius: 50%; background-color: #e5e7eb; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; flex-shrink: 0; }
.message-wrapper.user .avatar { margin-left: 10px; background-color: #dbeafe; }
.message-wrapper.assistant .avatar { margin-right: 10px; background-color: #10b981; color: white; }
.message-content { max-width: 75%; display: flex; flex-direction: column; } /* 稍微加宽以适应代码块 */
.message-wrapper.user .message-content { align-items: flex-end; }

/* 文本气泡样式调整 */
.text {
  padding: 12px 16px;
  border-radius: 12px;
  background-color: white;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  line-height: 1.6;
  color: #374151;
  word-wrap: break-word;
  min-height: 20px;
}

.user-text {
  background-color: #3b82f6;
  color: white;
  border-bottom-right-radius: 2px;
}

.assistant-text {
  border-top-left-radius: 2px;
  background-color: #ffffff;
}

/* --- 新增：Markdown 内容样式 (模拟 GitHub 风格) --- */
.markdown-body :deep(h1), .markdown-body :deep(h2), .markdown-body :deep(h3) { margin-top: 10px; margin-bottom: 5px; font-weight: 600; }
.markdown-body :deep(p) { margin: 5px 0; }
.markdown-body :deep(ul), .markdown-body :deep(ol) { margin-left: 20px; padding-left: 0; }
.markdown-body :deep(code) { background-color: #f3f4f6; padding: 2px 4px; border-radius: 4px; font-family: monospace; color: #e11d48; }
.markdown-body :deep(pre) { background-color: #0d1117; padding: 12px; border-radius: 8px; overflow-x: auto; margin: 10px 0; }
.markdown-body :deep(pre code) { background-color: transparent; color: #e6edf3; padding: 0; }
.markdown-body :deep(a) { color: #3b82f6; text-decoration: underline; }

/* --- 新增：打字机光标效果 --- */
.cursor {
  display: inline-block;
  width: 6px;
  height: 16px;
  background-color: #10b981;
  margin-left: 2px;
  vertical-align: middle;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* 输入框 */
.input-area { padding: 20px; background-color: white; border-top: 1px solid #e5e7eb; display: flex; gap: 10px; }
textarea { flex: 1; padding: 12px; border: 1px solid #d1d5db; border-radius: 8px; resize: none; outline: none; }
textarea:focus { border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2); }
.send-btn { padding: 0 24px; background-color: #3b82f6; color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }
.send-btn:disabled { background-color: #9ca3af; cursor: not-allowed; }
.tool-usage-log { margin-top: 5px; font-size: 0.8rem; }
.badge { background-color: #fef3c7; color: #92400e; padding: 2px 8px; border-radius: 4px; border: 1px solid #fcd34d; }
</style>