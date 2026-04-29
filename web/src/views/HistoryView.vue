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
  } catch {
    error.value = '加载历史记录失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

function viewReport(videoId: string) {
  router.push(`/report/${videoId}`)
}

async function confirmDelete(videoId: string) {
  if (!window.confirm('确定要删除这条分析记录吗？此操作不可撤销。')) return
  try {
    await deleteHistoryEntry(videoId)
    entries.value = entries.value.filter((e) => e.video_id !== videoId)
  } catch {
    alert('删除失败，请稍后重试')
  }
}

onMounted(loadHistory)
</script>

<template>
  <div class="p-6 lg:p-8">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">分析历史</h1>
      <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">共 {{ entries.length }} 条记录</p>
    </div>

    <!-- Search and Filter -->
    <div class="mb-4 flex flex-col sm:flex-row gap-3">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="搜索视频名..."
        class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <select
        v-model="selectedType"
        class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="">全部类型</option>
        <option v-for="t in ANALYSIS_TYPES" :key="t.value" :value="t.value">{{ t.label }}</option>
      </select>
      <select
        v-model="selectedStatus"
        class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="">全部状态</option>
        <option v-for="s in STATUS_OPTIONS" :key="s.value" :value="s.value">{{ s.label }}</option>
      </select>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <svg class="animate-spin h-10 w-10 text-blue-600 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
      </svg>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
      <p class="text-red-600 dark:text-red-400">{{ error }}</p>
      <button @click="loadHistory" class="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">重试</button>
    </div>

    <!-- List -->
    <HistoryList v-else :entries="filteredEntries" @select="viewReport" @delete="confirmDelete" />
  </div>
</template>
