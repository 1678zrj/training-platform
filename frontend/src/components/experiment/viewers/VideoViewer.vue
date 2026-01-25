<script setup>
import { ref, computed, watch, onDeactivated, onMounted } from 'vue'
import {
  VideoPause,
  VideoPlay,
  Download,
  Timer,
  RefreshLeft,
  ArrowDown
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  resource: {
    type: Object,
    required: true
  }
})

// --- 状态管理 ---
const videoRef = ref(null)
const isLoading = ref(true)
const isPlaying = ref(false)
const duration = ref(0)
const currentTime = ref(0)
const playbackRate = ref(1.0)
const hasError = ref(false)

const videoSource = computed(() => props.resource.file_path_or_url)

const formatTime = (seconds) => {
  if (!seconds || isNaN(seconds)) return '00:00'
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

// --- 事件监听 ---

// 1. 获取时长
const handleLoadedMetadata = () => {
  if (videoRef.value) {
    duration.value = videoRef.value.duration
  }
}

// 2. 【核心修复】首帧已加载
// loadeddata 比 canplay 更早触发，只要有画面了就关掉 Loading
const handleLoadedData = () => {
  isLoading.value = false
  hasError.value = false
}

// 3. 视频已就绪 (双重保险)
const handleCanPlay = () => {
  isLoading.value = false
}

// 4. 缓冲中
const handleWaiting = () => {
  isLoading.value = true
}

// 5. 开始播放
const handlePlaying = () => {
  isLoading.value = false
  isPlaying.value = true
}

// 6. 暂停
const handlePause = () => {
  isPlaying.value = false
}

const handleTimeUpdate = () => {
  if (videoRef.value) {
    currentTime.value = videoRef.value.currentTime
  }
}

const handleError = () => {
  isLoading.value = false
  hasError.value = true
  ElMessage.error('视频资源加载失败')
}

// --- 控制逻辑 ---
const togglePlay = () => {
  if (!videoRef.value) return
  if (videoRef.value.paused) {
    videoRef.value.play()
  } else {
    videoRef.value.pause()
  }
}

const handleSpeedCommand = (command) => {
  const rate = parseFloat(command)
  if (videoRef.value) {
    videoRef.value.playbackRate = rate
    playbackRate.value = rate
    ElMessage.success(`播放速度已切换为 ${rate}x`)
  }
}

const restartVideo = () => {
  if (videoRef.value) {
    videoRef.value.currentTime = 0
    videoRef.value.play()
  }
}

const downloadVideo = () => {
  window.open(props.resource.file_path_or_url, '_blank')
}

// --- 生命周期 ---
onDeactivated(() => {
  if (videoRef.value && !videoRef.value.paused) {
    videoRef.value.pause()
  }
})

// 【核心修复】挂载时主动检查状态
// 解决浏览器缓存视频时，事件早已触发导致一直 Loading 的问题
onMounted(() => {
  if (videoRef.value) {
    // readyState: 0=HAVE_NOTHING, 1=HAVE_METADATA, 2=HAVE_CURRENT_DATA, 3=HAVE_FUTURE_DATA, 4=HAVE_ENOUGH_DATA
    // 只要 >= 2 说明当前帧已有，可以取消 Loading 显示画面
    if (videoRef.value.readyState >= 2) {
      isLoading.value = false
      duration.value = videoRef.value.duration || 0
    }
  }
})

watch(() => props.resource.id, () => {
  isLoading.value = true
  hasError.value = false
  currentTime.value = 0
  duration.value = 0
  isPlaying.value = false
  playbackRate.value = 1.0
  if (videoRef.value) {
    videoRef.value.load()
    videoRef.value.playbackRate = 1.0
  }
})
</script>

<template>
  <div class="video-viewer">
    <div class="video-toolbar">
      <div class="toolbar-group">
        <el-button-group>
          <el-button
            :icon="isPlaying ? VideoPause : VideoPlay"
            @click="togglePlay"
            :disabled="hasError"
            size="small"
          >
            {{ isPlaying ? '暂停' : '播放' }}
          </el-button>
          <el-button :icon="RefreshLeft" @click="restartVideo" :disabled="hasError" size="small" title="重播"/>
        </el-button-group>

        <span class="time-display">
          {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
        </span>
      </div>

      <div class="toolbar-group">
        <el-dropdown @command="handleSpeedCommand" trigger="click">
          <el-button size="small">
            <el-icon class="el-icon--left"><Timer /></el-icon>
            {{ playbackRate }}x
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="2.0">2.0x (极速)</el-dropdown-item>
              <el-dropdown-item command="1.5">1.5x (快速)</el-dropdown-item>
              <el-dropdown-item command="1.25">1.25x (稍快)</el-dropdown-item>
              <el-dropdown-item command="1.0">1.0x (正常)</el-dropdown-item>
              <el-dropdown-item command="0.75">0.75x (稍慢)</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <el-divider direction="vertical" />

        <el-button :icon="Download" circle size="small" @click="downloadVideo" title="下载视频" />
      </div>
    </div>

    <div
      class="video-container"
      v-loading="isLoading"
      element-loading-text="正在缓冲视频..."
      element-loading-background="rgba(0, 0, 0, 0.8)"
    >
      <video
        v-if="!hasError"
        ref="videoRef"
        class="video-player"
        :src="videoSource"
        controls
        controlsList="nodownload"
        disablePictureInPicture
        @loadedmetadata="handleLoadedMetadata"
        @loadeddata="handleLoadedData"
        @canplay="handleCanPlay"
        @waiting="handleWaiting"
        @playing="handlePlaying"
        @pause="handlePause"
        @timeupdate="handleTimeUpdate"
        @error="handleError"
      >
        您的浏览器不支持 HTML5 视频播放。
      </video>

      <div v-else class="error-state">
        <el-empty description="视频加载失败" :image-size="100">
          <el-button type="primary" @click="downloadVideo">尝试直接下载</el-button>
        </el-empty>
      </div>
    </div>
  </div>
</template>

<style scoped>
.video-viewer {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 400px;
}

.video-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.time-display {
  font-size: 13px;
  color: #606266;
  font-feature-settings: "tnum";
  min-width: 90px;
  text-align: center;
}

.video-container {
  flex: 1;
  background-color: #000;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  position: relative;
}

.video-player {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  outline: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
}

.error-state {
  background: #fff;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-player:fullscreen {
  object-fit: contain;
}
</style>