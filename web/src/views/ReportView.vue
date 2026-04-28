<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
const videoId = route.params.videoId as string
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-10">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          分析报告
        </h1>
        <p class="text-lg text-gray-600 dark:text-gray-400">
          视频ID: {{ videoId }}
        </p>
      </div>

      <!-- Placeholder Content -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
        <div class="text-center py-12">
          <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 dark:bg-blue-900/30 mb-4">
            <svg class="w-8 h-8 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            报告生成中
          </h2>
          <p class="text-gray-500 dark:text-gray-400">
            完整的分析报告功能将在后续版本中实现
          </p>
        </div>
      </div>
    </div>
  </div>
</template>