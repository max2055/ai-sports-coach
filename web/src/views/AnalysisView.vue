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

// Auto-redirect to report page on completion
watch(isCompleted, (completed) => {
  if (completed) {
    setTimeout(() => {
      router.push({ name: 'report', params: { videoId } })
    }, 1000)
  }
})

onMounted(() => {
  start()
})

function handleRetry() {
  retry()
}

function goBack() {
  router.push({ name: 'upload' })
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-2xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-10">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          视频分析
        </h1>
        <p class="text-lg text-gray-600 dark:text-gray-400">
          AI 正在分析您的网球动作，请稍候...
        </p>
      </div>

      <!-- Main Card -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden">
        <!-- Status Section -->
        <div class="p-8">
          <!-- Processing State -->
          <div v-if="isProcessing" class="text-center">
            <!-- Animated Icon -->
            <div class="mb-6">
              <div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-blue-100 dark:bg-blue-900/30">
                <svg class="w-10 h-10 text-blue-600 dark:text-blue-400 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
            </div>

            <!-- Status Text -->
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              {{ statusText }}
            </h2>
            <p class="text-gray-500 dark:text-gray-400 mb-6">
              视频ID: {{ videoId }}
            </p>

            <!-- Progress Bar -->
            <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4 mb-4">
              <div
                class="bg-blue-600 h-4 rounded-full transition-all duration-300"
                :style="{ width: `${progress}%` }"
              ></div>
            </div>
            <p class="text-sm text-gray-500 dark:text-gray-400">
              {{ progress }}% 完成
            </p>
          </div>

          <!-- Completed State -->
          <div v-else-if="isCompleted" class="text-center">
            <div class="mb-6">
              <div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-green-100 dark:bg-green-900/30">
                <svg class="w-10 h-10 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              分析完成!
            </h2>
            <p class="text-gray-500 dark:text-gray-400">
              正在跳转到报告页面...
            </p>
          </div>

          <!-- Failed State -->
          <div v-else-if="isFailed" class="text-center">
            <div class="mb-6">
              <div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-red-100 dark:bg-red-900/30">
                <svg class="w-10 h-10 text-red-600 dark:text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <h2 class="text-xl font-semibold text-red-600 dark:text-red-400 mb-2">
              分析失败
            </h2>
            <p class="text-gray-500 dark:text-gray-400 mb-6">
              {{ error || '分析过程中发生错误，请重试' }}
            </p>

            <!-- Retry Buttons -->
            <div class="flex flex-col sm:flex-row gap-3 justify-center">
              <button
                class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl shadow-lg transition-all duration-200 disabled:opacity-50"
                :disabled="isLoading"
                @click="handleRetry"
              >
                <span v-if="isLoading" class="flex items-center justify-center">
                  <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  重试中...
                </span>
                <span v-else>重新分析</span>
              </button>
              <button
                class="px-6 py-3 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 font-semibold rounded-xl transition-all duration-200"
                @click="goBack"
              >
                返回上传
              </button>
            </div>
          </div>
        </div>

        <!-- Info Section -->
        <div class="px-8 py-4 bg-gray-50 dark:bg-gray-800/50 border-t border-gray-200 dark:border-gray-700">
          <p class="text-sm text-gray-500 dark:text-gray-400 text-center">
            分析过程通常需要 1-3 分钟，取决于视频长度
          </p>
        </div>
      </div>
    </div>
  </div>
</template>