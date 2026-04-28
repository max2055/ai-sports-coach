<script setup lang="ts">
import { ref, watch, computed, onMounted, onUnmounted } from 'vue'
import type { ProVideo } from '../api/pros'
import type { FrameAnnotation } from '../api/frames'
import { getProVideoFileUrl } from '../api/pros'

const props = defineProps<{
  userVideoUrl: string
  userAnnotations?: FrameAnnotation[]
  proVideo: ProVideo
  timeOffset?: number
}>()

const emit = defineEmits<{
  userTimeUpdate: [time: number]
  proTimeUpdate: [time: number]
}>()

const userVideoRef = ref<HTMLVideoElement>()
const proVideoRef = ref<HTMLVideoElement>()
const isPlaying = ref(false)
const playbackRate = ref(1)
const currentTime = ref(0)
const duration = ref(0)
const showAnnotations = ref(true)

const proVideoUrl = computed(() => getProVideoFileUrl(props.proVideo.id))

// Sync play/pause
function togglePlay() {
  if (isPlaying.value) {
    userVideoRef.value?.pause()
    proVideoRef.value?.pause()
    isPlaying.value = false
  } else {
    userVideoRef.value?.play()
    proVideoRef.value?.play()
    isPlaying.value = true
  }
}

// Sync speed adjustment
watch(playbackRate, (rate) => {
  if (userVideoRef.value) userVideoRef.value.playbackRate = rate
  if (proVideoRef.value) proVideoRef.value.playbackRate = rate
})

// Seek to specific time (sync both videos with offset)
function seek(time: number) {
  if (userVideoRef.value) {
    userVideoRef.value.currentTime = time
  }
  if (proVideoRef.value) {
    proVideoRef.value.currentTime = time + (props.timeOffset || 0)
  }
}

// Handle user video time update
function onUserTimeUpdate() {
  if (userVideoRef.value) {
    currentTime.value = userVideoRef.value.currentTime
    emit('userTimeUpdate', currentTime.value)
  }
}

// Handle pro video time update
function onProTimeUpdate() {
  if (proVideoRef.value) {
    emit('proTimeUpdate', proVideoRef.value.currentTime)
  }
}

// Handle video loaded
function onUserVideoLoaded() {
  if (userVideoRef.value) {
    duration.value = userVideoRef.value.duration
  }
}

// Reset when pro video changes
watch(() => props.proVideo, () => {
  isPlaying.value = false
  currentTime.value = 0
})

// Apply time offset when changed
watch(() => props.timeOffset, (offset) => {
  if (offset !== undefined && proVideoRef.value) {
    const userTime = userVideoRef.value?.currentTime || 0
    proVideoRef.value.currentTime = userTime + offset
  }
})

// Cleanup on unmount
onUnmounted(() => {
  isPlaying.value = false
})
</script>

<template>
  <div class="comparison-player">
    <!-- Split screen video containers -->
    <div class="split-screen grid grid-cols-2 gap-4">
      <!-- User video (left) -->
      <div class="user-video">
        <div class="relative bg-black rounded-lg overflow-hidden">
          <video
            ref="userVideoRef"
            :src="userVideoUrl"
            @timeupdate="onUserTimeUpdate"
            @loadedmetadata="onUserVideoLoaded"
            class="w-full aspect-video object-contain"
            muted
          />
          <!-- Annotation overlay indicator -->
          <div
            v-if="showAnnotations && userAnnotations && userAnnotations.length > 0"
            class="absolute top-2 right-2 bg-blue-500/80 text-white text-xs px-2 py-1 rounded"
          >
            标注已启用
          </div>
        </div>
        <div class="text-center mt-2 text-sm text-gray-600 dark:text-gray-400 font-medium">
          您的视频
        </div>
      </div>

      <!-- Pro video (right) -->
      <div class="pro-video">
        <div class="relative bg-black rounded-lg overflow-hidden">
          <video
            ref="proVideoRef"
            :src="proVideoUrl"
            @timeupdate="onProTimeUpdate"
            class="w-full aspect-video object-contain"
            muted
          />
        </div>
        <div class="text-center mt-2 text-sm text-gray-600 dark:text-gray-400 font-medium">
          {{ proVideo.name }}
        </div>
      </div>
    </div>

    <!-- Shared controls -->
    <div class="controls mt-4 bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
      <!-- Progress bar -->
      <div class="progress-section mb-4">
        <input
          type="range"
          :value="currentTime"
          :max="duration"
          min="0"
          step="0.1"
          class="w-full h-2 bg-gray-200 dark:bg-gray-600 rounded-lg appearance-none cursor-pointer"
          @input="seek(Number(($event.target as HTMLInputElement).value))"
        />
        <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
          <span>{{ currentTime.toFixed(1) }}s</span>
          <span>{{ duration.toFixed(1) }}s</span>
        </div>
      </div>

      <!-- Control buttons -->
      <div class="flex items-center justify-center gap-4">
        <!-- Play/Pause button -->
        <button
          @click="togglePlay"
          class="play-btn px-6 py-2 rounded-lg font-medium transition-colors"
          :class="isPlaying
            ? 'bg-yellow-500 hover:bg-yellow-600 text-white'
            : 'bg-blue-600 hover:bg-blue-700 text-white'"
        >
          {{ isPlaying ? '暂停' : '播放' }}
        </button>

        <!-- Speed control -->
        <div class="speed-control flex items-center gap-2">
          <span class="text-sm text-gray-600 dark:text-gray-400">速度:</span>
          <input
            type="range"
            v-model="playbackRate"
            min="0.25"
            max="2"
            step="0.25"
            class="w-20 h-2 bg-gray-200 dark:bg-gray-600 rounded-lg appearance-none cursor-pointer"
          />
          <span class="text-sm font-medium text-gray-900 dark:text-white">
            {{ playbackRate }}x
          </span>
        </div>

        <!-- Annotation toggle -->
        <button
          v-if="userAnnotations && userAnnotations.length > 0"
          @click="showAnnotations = !showAnnotations"
          class="annotation-btn px-4 py-2 rounded-lg text-sm transition-colors"
          :class="showAnnotations
            ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
            : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'"
        >
          {{ showAnnotations ? '隐藏标注' : '显示标注' }}
        </button>
      </div>

      <!-- Offset indicator -->
      <div v-if="timeOffset" class="mt-3 text-center text-sm text-gray-500 dark:text-gray-400">
        时间偏移: {{ timeOffset.toFixed(2) }}s
      </div>
    </div>
  </div>
</template>

<style scoped>
video {
  max-height: 400px;
}

input[type="range"]::-webkit-slider-thumb {
  appearance: none;
  width: 16px;
  height: 16px;
  background: #3b82f6;
  border-radius: 50%;
  cursor: pointer;
}

input[type="range"]::-moz-range-thumb {
  width: 16px;
  height: 16px;
  background: #3b82f6;
  border-radius: 50%;
  cursor: pointer;
}
</style>