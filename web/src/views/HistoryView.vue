<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getHistory, deleteHistoryEntry, type HistoryEntry } from '../api/history'
import HistoryList from '../components/HistoryList.vue'

const router = useRouter()

const entries = ref<HistoryEntry[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const searchQuery = ref('')
const selectedType = ref('')
const selectedStatus = ref('')

const ANALYSIS_TYPES = [
  { value: 'forehand', label: '正手' },
  { value: 'backhand', label: '反手' },
  { value: 'serve', label: '发球' },
  { value: 'volley', label: '截击' },
  { value: 'full', label: '全场综合' },
]

const STATUS_OPTIONS = [
  { value: 'completed', label: '已完成' },
  { value: 'failed', label: '失败' },
  { value: 'pending', label: '分析中' },
]

// Client-side filtering in addition to server-side
const filteredEntries = computed(() => {
  let result = entries.value

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter((e) => e.filename.toLowerCase().includes(q))
  }

  if (selectedType.value) {
    result = result.filter((e) => e.analysis_type === selectedType.value)
  }

  if (selectedStatus.value) {
    result = result.filter((e) => e.status === selectedStatus.value)
  }

  return result
})

async function loadHistory() {
  try {
    loading.value = true
    error.value = null
    const data = await getHistory()
    entries.value = data.entries
  } catch (err) {
    console.error('Failed to load history:', err)
    error.value = '加载历史记录失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

function viewReport(videoId: string) {
  router.push(`/report/${videoId}`)
}

async function confirmDelete(videoId: string) {
  if (!window.confirm('确定要删除这条分析记录吗？此操作不可撤销。')) {
    return
  }
  try {
    await deleteHistoryEntry(videoId)
    // Remove from local list
    entries.value = entries.value.filter((e) => e.video_id !== videoId)
  } catch (err) {
    console.error('Failed to delete history entry:', err)
    alert('删除失败，请稍后重试')
  }
}

onMounted(loadHistory)
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
              分析历史
            </h1>
            <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
              共 {{ entries.length }} 条记录
            </p>
          </div>
          <router-link
            to="/"
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
          >
            返回首页
          </router-link>
        </div>
      </div>
    </div>

    <!-- Search and Filter -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      <div class="flex flex-col sm:flex-row gap-3">
        <div class="flex-1">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索视频名..."
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow"
          />
        </div>
        <select
          v-model="selectedType"
          class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow"
        >
          <option value="">全部类型</option>
          <option v-for="t in ANALYSIS_TYPES" :key="t.value" :value="t.value">
            {{ t.label }}
          </option>
        </select>
        <select
          v-model="selectedStatus"
          class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow"
        >
          <option value="">全部状态</option>
          <option v-for="s in STATUS_OPTIONS" :key="s.value" :value="s.value">
            {{ s.label }}
          </option>
        </select>
      </div>
    </div>

    <!-- Loading state -->
    <div
      v-if="loading"
      class="flex items-center justify-center py-20"
    >
      <div class="flex flex-col items-center">
        <svg
          class="animate-spin h-10 w-10 text-blue-600 mb-4"
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
        <p class="text-gray-600 dark:text-gray-400">加载历史记录...</p>
      </div>
    </div>

    <!-- Error state -->
    <div
      v-else-if="error"
      class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
    >
      <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
        <svg
          class="w-12 h-12 text-red-500 mx-auto mb-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
        <h3 class="text-lg font-medium text-red-800 dark:text-red-200 mb-2">
          加载失败
        </h3>
        <p class="text-red-600 dark:text-red-400">{{ error }}</p>
        <button
          @click="loadHistory"
          class="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          重试
        </button>
      </div>
    </div>

    <!-- History List -->
    <div v-else>
      <HistoryList
        :entries="filteredEntries"
        @select="viewReport"
        @delete="confirmDelete"
      />
    </div>
  </div>
</template>
