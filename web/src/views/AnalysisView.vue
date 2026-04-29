<script setup lang="ts">
import { onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAnalysis } from '@/composables/useAnalysis'

const router = useRouter()
const route = useRoute()
const videoId = route.params.videoId as string

const {
  status,
  progress,
  error,
  isLoading,
  statusText,
  start,
  retry
} = useAnalysis(videoId)

const isCompleted = computed(() => status.value === 'completed')
const isFailed = computed(() => status.value === 'failed')
const isProcessing = computed(() => !isCompleted.value && !isFailed.value)

watch(isCompleted, (completed) => {
  if (completed) {
    setTimeout(() => router.push({ name: 'report', params: { videoId } }), 1000)
  }
})

onMounted(() => start())

function handleRetry() { retry() }
function goBack() { router.push('/') }
</script>

<template>
  <div class="p-6 lg:p-8">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">视频分析</h1>
      <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">AI 正在分析您的网球动作，请稍候...</p>
    </div>

    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 max-w-2xl">
      <div class="p-8">
        <!-- Processing -->
        <div v-if="isProcessing" class="text-center">
          <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 dark:bg-blue-900/30 mb-5">
            <svg class="w-8 h-8 text-blue-600 dark:text-blue-400 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          </div>
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">{{ statusText }}</h2>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-5">视频ID: {{ videoId }}</p>
          <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 mb-3">
            <div class="bg-blue-600 h-3 rounded-full transition-all duration-300" :style="{ width: `${progress}%` }" />
          </div>
          <p class="text-sm text-gray-500">{{ progress }}% 完成</p>
        </div>

        <!-- Completed -->
        <div v-else-if="isCompleted" class="text-center">
          <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 dark:bg-green-900/30 mb-5">
            <svg class="w-8 h-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">分析完成！</h2>
          <p class="text-sm text-gray-500">正在跳转到报告页面...</p>
        </div>

        <!-- Failed -->
        <div v-else class="text-center">
          <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-100 dark:bg-red-900/30 mb-5">
            <svg class="w-8 h-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 class="text-lg font-semibold text-red-600 mb-1">分析失败</h2>
          <p class="text-sm text-gray-500 mb-5">{{ error || '分析过程中发生错误，请重试' }}</p>
          <div class="flex gap-3 justify-center">
            <button
              class="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg disabled:opacity-50"
              :disabled="isLoading"
              @click="handleRetry"
            >
              重新分析
            </button>
            <button
              class="px-5 py-2.5 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 text-sm font-semibold rounded-lg"
              @click="goBack"
            >
              返回上传
            </button>
          </div>
        </div>
      </div>

      <div class="px-8 py-3 bg-gray-50 dark:bg-gray-800/50 border-t border-gray-200 dark:border-gray-700">
        <p class="text-xs text-gray-500 text-center">分析过程通常需要 1-3 分钟</p>
      </div>
    </div>
  </div>
</template>
