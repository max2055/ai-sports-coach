<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import VideoUploader from '../components/VideoUploader.vue'
import AnalysisTypeSelector from '../components/AnalysisTypeSelector.vue'
import { getHistory, type HistoryEntry } from '../api/history'
import type { VideoInfo, AnalysisType } from '../types/upload'

const router = useRouter()

const selectedVideo = ref<VideoInfo | null>(null)
const analysisType = ref<AnalysisType>('full')
const uploadError = ref<string | null>(null)
const uploadedVideoId = ref<string | null>(null)
const recentEntries = ref<HistoryEntry[]>([])
const recentLoading = ref(true)

const hasVideo = computed(() => selectedVideo.value !== null)

const ANALYSIS_TYPE_MAP: Record<string, string> = {
  forehand: '正手',
  backhand: '反手',
  serve: '发球',
  volley: '截击',
  full: '全场综合',
}

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

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return d.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

function scoreColorClass(score: number): string {
  if (score >= 7) return 'text-green-600 dark:text-green-400'
  if (score >= 5) return 'text-yellow-600 dark:text-yellow-400'
  return 'text-red-600 dark:text-red-400'
}

function handleSubmit() {
  if (!hasVideo.value || !uploadedVideoId.value) return
  router.push({ name: 'analysis', params: { videoId: uploadedVideoId.value } })
}

function handleReset() {
  selectedVideo.value = null
  uploadedVideoId.value = null
  uploadError.value = null
  analysisType.value = 'full'
}

function viewReport(videoId: string) {
  router.push(`/report/${videoId}`)
}

async function loadRecent() {
  try {
    const data = await getHistory()
    recentEntries.value = data.entries.slice(0, 5)
  } catch {
    // Silent fail — recent list is optional
  } finally {
    recentLoading.value = false
  }
}

onMounted(loadRecent)
</script>

<template>
  <div class="p-6 lg:p-8">
    <!-- Page header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">上传分析</h1>
      <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">上传训练视频，获取专业技术分析</p>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <!-- Upload card -->
      <div class="xl:col-span-2">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
          <!-- Upload Area -->
          <div class="p-6 border-b border-gray-200 dark:border-gray-700">
            <VideoUploader
              :analysis-type="analysisType"
              @upload-success="handleUploadSuccess"
              @upload-error="handleUploadError"
            />
          </div>

          <!-- Error Message -->
          <div
            v-if="uploadError"
            class="px-6 py-3 bg-red-50 dark:bg-red-900/20 border-b border-red-200 dark:border-red-800"
          >
            <span class="text-sm text-red-700 dark:text-red-400">{{ uploadError }}</span>
          </div>

          <!-- Video Info -->
          <div
            v-if="hasVideo"
            class="p-6 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50"
          >
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-sm font-semibold text-gray-900 dark:text-white">视频信息</h3>
              <button
                class="text-xs text-blue-600 dark:text-blue-400 hover:underline"
                @click="handleReset"
              >
                重新选择
              </button>
            </div>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div class="bg-white dark:bg-gray-700 rounded-lg px-3 py-2">
                <p class="text-xs text-gray-500 dark:text-gray-400">文件名</p>
                <p class="text-sm font-medium text-gray-900 dark:text-white truncate">{{ selectedVideo?.name }}</p>
              </div>
              <div class="bg-white dark:bg-gray-700 rounded-lg px-3 py-2">
                <p class="text-xs text-gray-500 dark:text-gray-400">时长</p>
                <p class="text-sm font-medium text-gray-900 dark:text-white">{{ formatDuration(selectedVideo?.duration) }}</p>
              </div>
              <div class="bg-white dark:bg-gray-700 rounded-lg px-3 py-2">
                <p class="text-xs text-gray-500 dark:text-gray-400">分辨率</p>
                <p class="text-sm font-medium text-gray-900 dark:text-white">{{ selectedVideo?.width }} × {{ selectedVideo?.height }}</p>
              </div>
              <div class="bg-white dark:bg-gray-700 rounded-lg px-3 py-2">
                <p class="text-xs text-gray-500 dark:text-gray-400">大小</p>
                <p class="text-sm font-medium text-gray-900 dark:text-white">{{ (selectedVideo?.size || 0 / 1048576).toFixed(1) }} MB</p>
              </div>
            </div>
          </div>

          <!-- Analysis Type -->
          <div
            v-if="hasVideo"
            class="p-6 border-b border-gray-200 dark:border-gray-700"
          >
            <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">分析类型</h3>
            <AnalysisTypeSelector v-model="analysisType" />
          </div>

          <!-- Submit -->
          <div v-if="hasVideo" class="p-6">
            <button
              class="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg shadow transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="!hasVideo || !uploadedVideoId"
              @click="handleSubmit"
            >
              开始分析 →
            </button>
          </div>
        </div>
      </div>

      <!-- Sidebar: Recent analyses -->
      <div class="xl:col-span-1">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
          <div class="px-5 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
            <h3 class="text-sm font-semibold text-gray-900 dark:text-white">最近分析</h3>
            <RouterLink
              to="/history"
              class="text-xs text-blue-600 dark:text-blue-400 hover:underline"
            >
              查看全部 →
            </RouterLink>
          </div>

          <!-- Loading -->
          <div v-if="recentLoading" class="p-6 text-center">
            <svg class="animate-spin h-6 w-6 text-blue-600 mx-auto mb-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            <p class="text-xs text-gray-500">加载中...</p>
          </div>

          <!-- Empty -->
          <div v-else-if="recentEntries.length === 0" class="p-8 text-center">
            <svg class="w-10 h-10 text-gray-300 dark:text-gray-600 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p class="text-sm text-gray-500 dark:text-gray-400">暂无分析记录</p>
            <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">上传第一个视频开始分析</p>
          </div>

          <!-- List -->
          <div v-else class="divide-y divide-gray-100 dark:divide-gray-700">
            <button
              v-for="entry in recentEntries"
              :key="entry.video_id"
              class="w-full text-left px-5 py-3 hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors"
              @click="viewReport(entry.video_id)"
            >
              <p class="text-sm font-medium text-gray-900 dark:text-white truncate">{{ entry.filename }}</p>
              <div class="flex items-center gap-2 mt-1 text-xs text-gray-500 dark:text-gray-400">
                <span>{{ formatDate(entry.created_at) }}</span>
                <span class="text-gray-300 dark:text-gray-600">·</span>
                <span>{{ ANALYSIS_TYPE_MAP[entry.analysis_type] || entry.analysis_type }}</span>
                <span v-if="entry.overall_score != null" :class="scoreColorClass(entry.overall_score)" class="ml-auto font-semibold">
                  {{ entry.overall_score }}
                </span>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
