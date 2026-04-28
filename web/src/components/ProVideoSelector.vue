<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { getProVideos } from '../api/pros'
import type { ProVideo, ProVideoType } from '../api/pros'

const props = defineProps<{
  analysisType: ProVideoType
  selectedProVideo?: ProVideo
}>()

const emit = defineEmits<{
  select: [video: ProVideo]
}>()

const proVideos = ref<ProVideo[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

async function loadVideos() {
  loading.value = true
  error.value = null
  try {
    proVideos.value = await getProVideos(props.analysisType)
  } catch (err) {
    console.error('Failed to load pro videos:', err)
    error.value = '加载视频列表失败'
  } finally {
    loading.value = false
  }
}

onMounted(loadVideos)
watch(() => props.analysisType, loadVideos)
</script>

<template>
  <div class="pro-selector">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">选择对比视频</h3>

    <!-- Loading state -->
    <div v-if="loading" class="flex justify-center py-8">
      <svg
        class="animate-spin h-8 w-8 text-blue-600"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          class="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          stroke-width="4"
        />
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="text-center py-4 text-red-600 dark:text-red-400">
      {{ error }}
      <button
        @click="loadVideos"
        class="ml-2 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        重试
      </button>
    </div>

    <!-- Video cards -->
    <div v-else-if="proVideos.length > 0" class="grid grid-cols-2 gap-4">
      <div
        v-for="video in proVideos"
        :key="video.id"
        class="pro-card cursor-pointer p-4 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        :class="{
          'border-blue-500 bg-blue-50 dark:bg-blue-900/20': selectedProVideo?.id === video.id,
          'border-gray-200 dark:border-gray-600': selectedProVideo?.id !== video.id
        }"
        @click="emit('select', video)"
      >
        <div class="font-medium text-gray-900 dark:text-white">{{ video.name }}</div>
        <div class="text-sm text-gray-500 dark:text-gray-400 mt-1">{{ video.description }}</div>
        <div v-if="video.duration" class="text-xs text-gray-400 dark:text-gray-500 mt-2">
          {{ video.duration.toFixed(1) }}s
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="text-center py-8 text-gray-500 dark:text-gray-400">
      没有找到该类型的职业选手视频
    </div>
  </div>
</template>