<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { IssueFrame, IssueType } from '../api/frames'
import { getAnnotatedImageUrl } from '../api/frames'

const props = defineProps<{
  issueFrames: IssueFrame[]
  videoId: string
}>()

const emit = defineEmits<{
  (e: 'select', frameNumber: number, time: number): void
}>()

// All unique issue types from the frames
const allIssueTypes = computed(() => {
  const types = new Set<IssueType>()
  for (const frame of props.issueFrames) {
    for (const type of frame.issue_types) {
      types.add(type)
    }
  }
  return Array.from(types).sort()
})

// Selected filter
const selectedIssueType = ref<string>('')

// Filtered frames
const filteredFrames = computed(() => {
  if (!selectedIssueType.value) {
    return props.issueFrames
  }
  return props.issueFrames.filter(frame =>
    frame.issue_types.includes(selectedIssueType.value as IssueType)
  )
})

// Format time as mm:ss
const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// Get issue type label in Chinese
const getIssueTypeLabel = (type: IssueType): string => {
  const labels: Record<string, string> = {
    'LATE BACKSWING': '引拍过晚',
    'WRONG GRIP': '握拍错误',
    'GRIP CHANGE ERR': '换握错误',
    'WRONG CONTACT': '击球点错误',
    'ELBOW DROP': '肘部下沉',
    'NO HIP ROT': '无转髋',
    'LATE SHOULDER': '转肩过晚',
    'NO FOLLOW-THRU': '无随挥',
    'POOR FOOTWORK': '步伐不佳',
    'NO SPLIT STEP': '无分腿垫步',
    'LATE WEIGHT': '重心转移晚',
    'WRONG STANCE': '站位错误',
    'WRONG POSITION': '位置错误',
    'BAD TOSS': '抛球不佳',
    'NO LEG DRIVE': '无蹬地',
    'OFF BALANCE': '失去平衡',
    'TELEGRAPH': '动作预判',
    'WRONG SPIN': '旋转错误',
    'GOOD FORM': '动作正确',
    'GOOD FOOTWORK': '步伐正确',
    'GOOD TACTICS': '战术正确',
  }
  return labels[type] || type
}

// Check if issue type is positive
const isPositiveIssue = (type: IssueType): boolean => {
  return type.startsWith('GOOD') || type === 'GOOD FORM' || type === 'GOOD FOOTWORK' || type === 'GOOD TACTICS'
}

// Handle frame selection
const handleFrameClick = (frame: IssueFrame) => {
  emit('select', frame.frame_number, frame.time_seconds)
}
</script>

<template>
  <div class="issue-frame-list">
    <!-- Header with filter -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
        问题帧列表
        <span class="text-sm font-normal text-gray-500 dark:text-gray-400 ml-2">
          ({{ filteredFrames.length }} 帧)
        </span>
      </h3>

      <!-- Issue type filter -->
      <select
        v-model="selectedIssueType"
        class="px-3 py-1.5 text-sm bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      >
        <option value="">全部类型</option>
        <option
          v-for="type in allIssueTypes"
          :key="type"
          :value="type"
        >
          {{ getIssueTypeLabel(type) }}
        </option>
      </select>
    </div>

    <!-- Frame grid -->
    <div
      v-if="filteredFrames.length > 0"
      class="grid grid-cols-2 sm:grid-cols-3 gap-3 max-h-[60vh] overflow-y-auto pr-2"
    >
      <div
        v-for="frame in filteredFrames"
        :key="frame.frame_number"
        class="relative bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden cursor-pointer hover:ring-2 hover:ring-blue-500 transition-all group"
        @click="handleFrameClick(frame)"
      >
        <!-- Thumbnail -->
        <div class="aspect-video bg-gray-100 dark:bg-gray-700 relative">
          <img
            :src="getAnnotatedImageUrl(videoId, frame.frame_number)"
            :alt="`Frame ${frame.frame_number}`"
            class="w-full h-full object-cover"
            loading="lazy"
          />

          <!-- Frame number overlay -->
          <div class="absolute bottom-1 left-1 px-1.5 py-0.5 bg-black/70 text-white text-xs rounded">
            帧 {{ frame.frame_number }}
          </div>

          <!-- Time overlay -->
          <div class="absolute bottom-1 right-1 px-1.5 py-0.5 bg-black/70 text-white text-xs rounded">
            {{ formatTime(frame.time_seconds) }}
          </div>
        </div>

        <!-- Issue tags -->
        <div class="p-2">
          <div class="flex flex-wrap gap-1">
            <span
              v-for="type in frame.issue_types"
              :key="type"
              class="px-1.5 py-0.5 text-xs rounded"
              :class="isPositiveIssue(type)
                ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'"
            >
              {{ getIssueTypeLabel(type) }}
            </span>
          </div>
        </div>

        <!-- Hover overlay -->
        <div class="absolute inset-0 bg-blue-500/10 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
      </div>
    </div>

    <!-- Empty state -->
    <div
      v-else
      class="flex flex-col items-center justify-center py-12 text-gray-500 dark:text-gray-400"
    >
      <svg
        class="w-12 h-12 mb-3"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
        />
      </svg>
      <p>没有找到问题帧</p>
      <p
        v-if="selectedIssueType"
        class="text-sm mt-1"
      >
        尝试选择其他筛选条件
      </p>
    </div>
  </div>
</template>

<style scoped>
.issue-frame-list {
  min-height: 200px;
}
</style>