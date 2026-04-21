<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import VideoUploader from '../components/VideoUploader.vue'
import AnalysisTypeSelector from '../components/AnalysisTypeSelector.vue'
import type { VideoInfo, AnalysisType } from '../types/upload'

const router = useRouter()
const selectedVideo = ref<VideoInfo | null>(null)
const analysisType = ref<AnalysisType>('full')
const uploadError = ref<string | null>(null)
const uploadedVideoId = ref<string | null>(null)

const hasVideo = computed(() => selectedVideo.value !== null)

function handleUploadSuccess(result: { videoId: string; metadata: VideoInfo }) {
  selectedVideo.value = result.metadata
  uploadedVideoId.value = result.videoId
  uploadError.value = null
}

function handleUploadError(error: string) {
  uploadError.value = error
}

function formatDuration(seconds?: number): string {
  if (!seconds || isNaN(seconds)) return '未知'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

function formatResolution(width?: number, height?: number): string {
  if (!width || !height) return '未知'
  return `${width} × ${height}`
}

function handleSubmit() {
  if (!hasVideo.value || !uploadedVideoId.value) return

  // Navigate to analysis page with video ID
  router.push({
    name: 'analysis',
    params: { videoId: uploadedVideoId.value }
  })
}

function handleReset() {
  selectedVideo.value = null
  uploadedVideoId.value = null
  uploadError.value = null
  analysisType.value = 'full'
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-10">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          AI 网球教练
        </h1>
        <p class="text-lg text-gray-600 dark:text-gray-400">
          上传训练视频，获取专业的技术分析
        </p>
      </div>

      <!-- Main Content -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden">
        <!-- Upload Section -->
        <div class="p-8 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            1. 选择视频文件
          </h2>
          <VideoUploader
            :analysis-type="analysisType"
            @upload-success="handleUploadSuccess"
            @upload-error="handleUploadError"
          />
        </div>

        <!-- Error Message -->
        <div
          v-if="uploadError"
          class="p-4 bg-red-50 dark:bg-red-900/20 border-b border-red-200 dark:border-red-800"
        >
          <div class="flex items-center">
            <svg class="w-5 h-5 text-red-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="text-red-700 dark:text-red-400">{{ uploadError }}</span>
          </div>
        </div>

        <!-- Video Info Section -->
        <div
          v-if="hasVideo"
          class="p-8 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50"
        >
          <div class="flex items-start justify-between mb-4">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
              视频信息
            </h2>
            <button
              class="text-sm text-blue-600 hover:text-blue-500 dark:text-blue-400"
              @click="handleReset"
            >
              重新选择
            </button>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <!-- File Name -->
            <div class="bg-white dark:bg-gray-700 rounded-lg p-4">
              <p class="text-sm text-gray-500 dark:text-gray-400">文件名</p>
              <p class="font-medium text-gray-900 dark:text-white truncate" :title="selectedVideo?.name">
                {{ selectedVideo?.name }}
              </p>
            </div>

            <!-- Duration -->
            <div class="bg-white dark:bg-gray-700 rounded-lg p-4">
              <p class="text-sm text-gray-500 dark:text-gray-400">时长</p>
              <p class="font-medium text-gray-900 dark:text-white">
                {{ formatDuration(selectedVideo?.duration) }}
              </p>
            </div>

            <!-- Resolution -->
            <div class="bg-white dark:bg-gray-700 rounded-lg p-4">
              <p class="text-sm text-gray-500 dark:text-gray-400">分辨率</p>
              <p class="font-medium text-gray-900 dark:text-white">
                {{ formatResolution(selectedVideo?.width, selectedVideo?.height) }}
              </p>
            </div>

            <!-- File Size -->
            <div class="bg-white dark:bg-gray-700 rounded-lg p-4">
              <p class="text-sm text-gray-500 dark:text-gray-400">文件大小</p>
              <p class="font-medium text-gray-900 dark:text-white">
                {{ formatFileSize(selectedVideo?.size || 0) }}
              </p>
            </div>
          </div>
        </div>

        <!-- Analysis Type Section -->
        <div
          v-if="hasVideo"
          class="p-8 border-b border-gray-200 dark:border-gray-700"
        >
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            2. 选择分析类型
          </h2>
          <AnalysisTypeSelector v-model="analysisType" />
        </div>

        <!-- Submit Section -->
        <div v-if="hasVideo" class="p-8">
          <button
            class="w-full sm:w-auto px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl shadow-lg transition-all duration-200 hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="!hasVideo || !uploadedVideoId"
            @click="handleSubmit"
          >
            开始分析
          </button>
        </div>
      </div>

      <!-- Tips -->
      <div class="mt-8 text-center">
        <p class="text-sm text-gray-500 dark:text-gray-400">
          提示：为了获得最佳分析效果，请确保视频清晰，拍摄角度稳定，能完整看到球员动作。
        </p>
      </div>
    </div>
  </div>
</template>
