<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const props = defineProps<{
  userCurrentTime: number
  proCurrentTime: number
}>()

const emit = defineEmits<{
  applyOffset: [offset: number]
}>()

const userKeyframe = ref<number | null>(null)
const proKeyframe = ref<number | null>(null)

// Calculate offset when both frames are marked
const calculatedOffset = computed(() => {
  if (userKeyframe.value !== null && proKeyframe.value !== null) {
    return proKeyframe.value - userKeyframe.value
  }
  return null
})

// Status indicator
const alignmentStatus = computed(() => {
  if (userKeyframe.value === null && proKeyframe.value === null) {
    return '未标记'
  }
  if (userKeyframe.value === null) {
    return '请标记用户视频'
  }
  if (proKeyframe.value === null) {
    return '请标记职业视频'
  }
  return '已计算偏移'
})

function markUserFrame() {
  userKeyframe.value = props.userCurrentTime
}

function markProFrame() {
  proKeyframe.value = props.proCurrentTime
}

function applyOffset() {
  if (calculatedOffset.value !== null) {
    emit('applyOffset', calculatedOffset.value)
  }
}

function resetMarkers() {
  userKeyframe.value = null
  proKeyframe.value = null
}

// Reset markers when user explicitly changes selection
watch(() => props.userCurrentTime, () => {
  // Don't auto-reset, user manually controls
})
</script>

<template>
  <div class="keyframe-marker p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
    <div class="flex items-center justify-between mb-3">
      <h4 class="font-semibold text-gray-900 dark:text-white">关键帧对齐</h4>
      <span
        class="text-xs px-2 py-1 rounded"
        :class="{
          'bg-gray-200 dark:bg-gray-600 text-gray-600 dark:text-gray-300': alignmentStatus === '未标记',
          'bg-yellow-100 dark:bg-yellow-900 text-yellow-700 dark:text-yellow-300': alignmentStatus.includes('请标记'),
          'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300': alignmentStatus === '已计算偏移'
        }"
      >
        {{ alignmentStatus }}
      </span>
    </div>

    <!-- Marker controls -->
    <div class="flex gap-6 mb-3">
      <!-- User frame marker -->
      <div class="user-marker flex-1">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-gray-600 dark:text-gray-400">用户视频</span>
          <span class="text-sm font-medium text-gray-900 dark:text-white">
            {{ userCurrentTime.toFixed(2) }}s
          </span>
        </div>
        <button
          @click="markUserFrame"
          class="w-full px-3 py-2 rounded text-sm transition-colors"
          :class="userKeyframe !== null
            ? 'bg-green-500 text-white'
            : 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 hover:bg-blue-200 dark:hover:bg-blue-800'"
        >
          {{ userKeyframe !== null ? `已标记 ${userKeyframe.toFixed(2)}s` : '标记当前帧' }}
        </button>
      </div>

      <!-- Pro frame marker -->
      <div class="pro-marker flex-1">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-gray-600 dark:text-gray-400">职业视频</span>
          <span class="text-sm font-medium text-gray-900 dark:text-white">
            {{ proCurrentTime.toFixed(2) }}s
          </span>
        </div>
        <button
          @click="markProFrame"
          class="w-full px-3 py-2 rounded text-sm transition-colors"
          :class="proKeyframe !== null
            ? 'bg-green-500 text-white'
            : 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 hover:bg-blue-200 dark:hover:bg-blue-800'"
        >
          {{ proKeyframe !== null ? `已标记 ${proKeyframe.toFixed(2)}s` : '标记当前帧' }}
        </button>
      </div>
    </div>

    <!-- Offset display and apply -->
    <div v-if="calculatedOffset !== null" class="mt-3 p-3 bg-blue-50 dark:bg-blue-900/30 rounded">
      <div class="flex items-center justify-between">
        <div>
          <span class="text-sm text-gray-600 dark:text-gray-400">计算偏移: </span>
          <span class="text-lg font-semibold text-blue-600 dark:text-blue-400">
            {{ calculatedOffset.toFixed(2) }}s
          </span>
          <span class="text-sm text-gray-500 dark:text-gray-400 ml-2">
            ({{ calculatedOffset > 0 ? '职业视频在前' : '用户视频在前' }})
          </span>
        </div>
        <div class="flex gap-2">
          <button
            @click="applyOffset"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors"
          >
            应用偏移
          </button>
          <button
            @click="resetMarkers"
            class="px-3 py-2 bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg text-sm hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors"
          >
            重置
          </button>
        </div>
      </div>
    </div>

    <!-- Instructions -->
    <div v-else class="mt-3 text-sm text-gray-500 dark:text-gray-400">
      <p>提示: 分别播放两个视频到关键动作帧（如击球瞬间），点击"标记当前帧"按钮标记，系统将自动计算时间偏移以便同步播放。</p>
    </div>
  </div>
</template>