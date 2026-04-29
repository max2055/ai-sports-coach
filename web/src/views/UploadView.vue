<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
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

const TYPE_LABEL: Record<string, string> = {
  forehand: '正手',
  backhand: '反手',
  serve: '发球',
  volley: '截击',
  full: '全场',
}

function handleUploadSuccess(result: { videoId: string; metadata: VideoInfo }) {
  selectedVideo.value = result.metadata
  uploadedVideoId.value = result.videoId
  uploadError.value = null
}

function handleUploadError(msg: string) {
  uploadError.value = msg
}

function formatTime(s?: number): string {
  if (!s || isNaN(s)) return '—'
  const m = Math.floor(s / 60)
  const sec = Math.floor(s % 60)
  return `${m}:${String(sec).padStart(2, '0')}`
}

function fmtDate(d: string): string {
  const date = new Date(d)
  const mm = String(date.getMonth() + 1).padStart(2, '0')
  const dd = String(date.getDate()).padStart(2, '0')
  const hh = String(date.getHours()).padStart(2, '0')
  const mi = String(date.getMinutes()).padStart(2, '0')
  return `${mm}-${dd} ${hh}:${mi}`
}

function scoreColor(s: number): string {
  return s >= 7 ? 'text-emerald-500' : s >= 5 ? 'text-amber-500' : 'text-red-500'
}

function statusLabel(s: string): string {
  return s === 'completed' ? '已完成' : s === 'failed' ? '失败' : '分析中'
}

function statusDot(s: string): string {
  return s === 'completed' ? 'bg-emerald-400' : s === 'failed' ? 'bg-red-400' : 'bg-blue-400 animate-pulse'
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

function viewReport(id: string) { router.push(`/report/${id}`) }

async function loadRecent() {
  try {
    const data = await getHistory()
    recentEntries.value = data.entries.slice(0, 5)
  } catch { /* ignore */ }
  finally { recentLoading.value = false }
}

onMounted(loadRecent)
</script>

<template>
  <div class="p-6 max-w-6xl mx-auto">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-xl font-bold text-zinc-900">上传分析</h1>
      <p class="text-sm text-zinc-500 mt-1">上传训练视频，AI 将自动分析您的网球动作</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Upload Card -->
      <div class="lg:col-span-2">
        <div class="bg-white rounded-xl shadow-sm border border-zinc-200">
          <div class="p-5 border-b border-zinc-100">
            <VideoUploader
              :analysis-type="analysisType"
              @upload-success="handleUploadSuccess"
              @upload-error="handleUploadError"
            />
          </div>

          <!-- Error -->
          <div v-if="uploadError" class="px-5 py-3 bg-red-50 border-b border-red-100">
            <span class="text-sm text-red-600">{{ uploadError }}</span>
          </div>

          <!-- Video Info -->
          <div v-if="hasVideo" class="p-5 border-b border-zinc-100 bg-zinc-50">
            <div class="flex items-center justify-between mb-3">
              <h3 class="text-xs font-semibold text-zinc-500 uppercase tracking-wider">视频信息</h3>
              <button class="text-xs text-tennis hover:underline" @click="handleReset">更换文件</button>
            </div>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div class="bg-white rounded-lg px-3 py-2.5">
                <p class="text-[10px] text-zinc-400 mb-0.5">文件名</p>
                <p class="text-sm font-medium text-zinc-900 truncate">{{ selectedVideo?.name }}</p>
              </div>
              <div class="bg-white rounded-lg px-3 py-2.5">
                <p class="text-[10px] text-zinc-400 mb-0.5">时长</p>
                <p class="text-sm font-medium text-zinc-900">{{ formatTime(selectedVideo?.duration) }}</p>
              </div>
              <div class="bg-white rounded-lg px-3 py-2.5">
                <p class="text-[10px] text-zinc-400 mb-0.5">分辨率</p>
                <p class="text-sm font-medium text-zinc-900">{{ selectedVideo?.width }}×{{ selectedVideo?.height }}</p>
              </div>
              <div class="bg-white rounded-lg px-3 py-2.5">
                <p class="text-[10px] text-zinc-400 mb-0.5">大小</p>
                <p class="text-sm font-medium text-zinc-900">{{ ((selectedVideo?.size || 0) / 1048576).toFixed(1) }} MB</p>
              </div>
            </div>
          </div>

          <!-- Analysis Type -->
          <div v-if="hasVideo" class="p-5 border-b border-zinc-100">
            <h3 class="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-3">分析类型</h3>
            <AnalysisTypeSelector v-model="analysisType" />
          </div>

          <!-- Submit -->
          <div v-if="hasVideo" class="p-5">
            <button
              class="px-6 py-2.5 bg-tennis hover:bg-tennis-light text-white text-sm font-semibold rounded-lg shadow-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="!hasVideo || !uploadedVideoId"
              @click="handleSubmit"
            >
              开始分析 →
            </button>
          </div>
        </div>
      </div>

      <!-- Recent Analyses -->
      <div class="lg:col-span-1">
        <div class="bg-white rounded-xl shadow-sm border border-zinc-200">
          <div class="px-5 py-4 border-b border-zinc-100 flex items-center justify-between">
            <h3 class="text-sm font-semibold text-zinc-900">最近分析</h3>
            <RouterLink to="/history" class="text-xs text-tennis hover:underline">全部 →</RouterLink>
          </div>

          <!-- Loading -->
          <div v-if="recentLoading" class="p-8 text-center">
            <svg class="animate-spin h-5 w-5 text-tennis mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          </div>

          <!-- Empty -->
          <div v-else-if="recentEntries.length === 0" class="p-8 text-center">
            <p class="text-sm text-zinc-400">暂无分析记录</p>
            <p class="text-xs text-zinc-300 mt-1">上传第一个视频开始吧</p>
          </div>

          <!-- List -->
          <div v-else class="divide-y divide-zinc-50">
            <button
              v-for="entry in recentEntries"
              :key="entry.video_id"
              class="w-full text-left px-5 py-3.5 hover:bg-zinc-50 transition-colors group"
              @click="viewReport(entry.video_id)"
            >
              <div class="flex items-start gap-2">
                <span class="mt-1.5 w-1.5 h-1.5 rounded-full flex-shrink-0" :class="statusDot(entry.status)" />
                <div class="min-w-0 flex-1">
                  <p class="text-sm font-medium text-zinc-900 truncate">{{ entry.filename }}</p>
                  <div class="flex items-center gap-2 mt-1 text-xs text-zinc-400">
                    <span>{{ fmtDate(entry.created_at) }}</span>
                    <span class="text-zinc-200">·</span>
                    <span>{{ TYPE_LABEL[entry.analysis_type] }}</span>
                  </div>
                </div>
                <span v-if="entry.overall_score != null" class="text-xs font-bold mt-0.5" :class="scoreColor(entry.overall_score)">
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
