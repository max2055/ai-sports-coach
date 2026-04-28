<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import type { IssueFrame, IssueType } from '../api/frames'

const props = defineProps<{
  duration: number
  currentTime: number
  issueFrames: IssueFrame[]
}>()

const emit = defineEmits<{
  (e: 'seek', time: number): void
}>()

const timelineRef = ref<HTMLDivElement | null>(null)
const isDragging = ref(false)

// Compute progress percentage
const progress = computed(() => {
  if (props.duration <= 0) return 0
  return (props.currentTime / props.duration) * 100
})

// Format time as mm:ss
const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// Get marker color based on issue types
const getMarkerColor = (issueTypes: IssueType[]): string => {
  // If all are "GOOD_*" types, show green
  const allGood = issueTypes.every(t =>
    t.startsWith('GOOD') || t === 'GOOD FORM' || t === 'GOOD FOOTWORK' || t === 'GOOD TACTICS'
  )
  return allGood ? '#32DC50' : '#FF3232'
}

// Calculate marker position as percentage
const getMarkerPosition = (timeSeconds: number): number => {
  if (props.duration <= 0) return 0
  return (timeSeconds / props.duration) * 100
}

// Handle click on timeline
const handleTimelineClick = (event: MouseEvent) => {
  if (!timelineRef.value) return

  const rect = timelineRef.value.getBoundingClientRect()
  const clickX = event.clientX - rect.left
  const percentage = clickX / rect.width
  const time = percentage * props.duration

  emit('seek', Math.max(0, Math.min(time, props.duration)))
}

// Handle drag
const handleMouseDown = (event: MouseEvent) => {
  isDragging.value = true
  handleTimelineClick(event)
}

const handleMouseMove = (event: MouseEvent) => {
  if (!isDragging.value) return
  handleTimelineClick(event)
}

const handleMouseUp = () => {
  isDragging.value = false
}

// Lifecycle
onMounted(() => {
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
})

onUnmounted(() => {
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
})
</script>

<template>
  <div class="frame-timeline">
    <!-- Time display -->
    <div class="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
      <span>{{ formatTime(currentTime) }}</span>
      <span>{{ formatTime(duration) }}</span>
    </div>

    <!-- Timeline track -->
    <div
      ref="timelineRef"
      class="relative h-8 bg-gray-200 dark:bg-gray-700 rounded-lg cursor-pointer overflow-visible"
      @mousedown="handleMouseDown"
    >
      <!-- Progress bar -->
      <div
        class="absolute top-0 left-0 h-full bg-blue-500 rounded-l-lg transition-all"
        :style="{ width: `${progress}%` }"
      />

      <!-- Issue frame markers -->
      <div
        v-for="frame in issueFrames"
        :key="frame.frame_number"
        class="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full border-2 border-white shadow-sm cursor-pointer hover:scale-125 transition-transform"
        :style="{
          left: `${getMarkerPosition(frame.time_seconds)}%`,
          backgroundColor: getMarkerColor(frame.issue_types)
        }"
        :title="`${frame.issue_types.join(', ')} @ ${formatTime(frame.time_seconds)}`"
        @click.stop="emit('seek', frame.time_seconds)"
      />

      <!-- Current position indicator -->
      <div
        class="absolute top-0 w-1 h-full bg-white shadow-lg"
        :style="{ left: `${progress}%` }"
      />
    </div>

    <!-- Legend -->
    <div class="flex items-center gap-4 mt-2 text-xs text-gray-500 dark:text-gray-400">
      <div class="flex items-center gap-1">
        <div class="w-3 h-3 rounded-full bg-red-500" />
        <span>问题帧</span>
      </div>
      <div class="flex items-center gap-1">
        <div class="w-3 h-3 rounded-full bg-green-500" />
        <span>正确动作</span>
      </div>
      <div class="flex items-center gap-1">
        <div class="w-3 h-3 rounded-full bg-blue-500" />
        <span>当前进度</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.frame-timeline {
  user-select: none;
}
</style>