<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getHistory, deleteHistoryEntry, type HistoryEntry } from '../api/history'

const router = useRouter()
const entries = ref<HistoryEntry[]>([])
const loading = ref(true)
const searchQuery = ref('')
const selectedType = ref('')
const selectedStatus = ref('')

const TYPE_LABEL: Record<string, string> = { forehand: '正手', backhand: '反手', serve: '发球', volley: '截击', full: '全场' }
const STATUS_LABEL: Record<string, string> = { completed: '已完成', failed: '失败', pending: '分析中' }

const filteredEntries = computed(() => {
  let r = entries.value
  if (searchQuery.value) { const q = searchQuery.value.toLowerCase(); r = r.filter(e => e.filename.toLowerCase().includes(q)) }
  if (selectedType.value) r = r.filter(e => e.analysis_type === selectedType.value)
  if (selectedStatus.value) r = r.filter(e => e.status === selectedStatus.value)
  return r
})

async function load() {
  try { const d = await getHistory(); entries.value = d.entries } catch { /* */ }
  finally { loading.value = false }
}

function fmtDate(d: string) {
  const dt = new Date(d)
  return `${String(dt.getMonth()+1).padStart(2,'0')}-${String(dt.getDate()).padStart(2,'0')} ${String(dt.getHours()).padStart(2,'0')}:${String(dt.getMinutes()).padStart(2,'0')}`
}

function scoreColor(s: number) { return s >= 7 ? 'text-emerald-600' : s >= 5 ? 'text-amber-600' : 'text-red-600' }

function viewReport(id: string) { router.push(`/report/${id}`) }

async function confirmDelete(id: string) {
  if (!confirm('确定删除此记录？')) return
  try { await deleteHistoryEntry(id); entries.value = entries.value.filter(e => e.video_id !== id) } catch { alert('删除失败') }
}

onMounted(load)
</script>

<template>
  <div class="p-6 max-w-6xl mx-auto">
    <div class="mb-6">
      <h1 class="text-xl font-bold text-zinc-900">分析历史</h1>
      <p class="text-sm text-zinc-500 mt-1">共 {{ entries.length }} 条记录</p>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap gap-3 mb-4">
      <input v-model="searchQuery" placeholder="搜索视频名..." class="flex-1 min-w-48 px-3 py-2 border border-zinc-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-tennis/30 focus:border-tennis" />
      <select v-model="selectedType" class="px-3 py-2 border border-zinc-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-tennis/30">
        <option value="">全部类型</option>
        <option v-for="(l, v) in TYPE_LABEL" :key="v" :value="v">{{ l }}</option>
      </select>
      <select v-model="selectedStatus" class="px-3 py-2 border border-zinc-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-tennis/30">
        <option value="">全部状态</option>
        <option v-for="(l, v) in STATUS_LABEL" :key="v" :value="v">{{ l }}</option>
      </select>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <svg class="animate-spin h-6 w-6 text-tennis" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
    </div>

    <!-- Empty -->
    <div v-else-if="filteredEntries.length === 0" class="bg-white rounded-xl border border-zinc-200 p-12 text-center">
      <p class="text-sm text-zinc-400">暂无匹配的记录</p>
    </div>

    <!-- Table -->
    <div v-else class="bg-white rounded-xl shadow-sm border border-zinc-200 overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="bg-zinc-50 text-zinc-500 text-xs uppercase tracking-wider">
            <th class="text-left py-3 px-4 font-medium">视频名</th>
            <th class="text-left py-3 px-4 font-medium">日期</th>
            <th class="text-left py-3 px-4 font-medium">类型</th>
            <th class="text-left py-3 px-4 font-medium">评分</th>
            <th class="text-left py-3 px-4 font-medium">状态</th>
            <th class="text-right py-3 px-4 font-medium">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-zinc-100">
          <tr v-for="entry in filteredEntries" :key="entry.video_id" class="hover:bg-zinc-50 cursor-pointer transition-colors" @click="viewReport(entry.video_id)">
            <td class="py-3 px-4 font-medium text-zinc-900 truncate max-w-[200px]">{{ entry.filename }}</td>
            <td class="py-3 px-4 text-zinc-500">{{ fmtDate(entry.created_at) }}</td>
            <td class="py-3 px-4 text-zinc-500">{{ TYPE_LABEL[entry.analysis_type] || entry.analysis_type }}</td>
            <td class="py-3 px-4">
              <span v-if="entry.overall_score != null" class="font-bold" :class="scoreColor(entry.overall_score)">{{ entry.overall_score }}/10</span>
              <span v-else class="text-zinc-300">—</span>
            </td>
            <td class="py-3 px-4">
              <span class="inline-flex items-center gap-1.5 text-xs">
                <span class="w-1.5 h-1.5 rounded-full" :class="entry.status === 'completed' ? 'bg-emerald-400' : entry.status === 'failed' ? 'bg-red-400' : 'bg-blue-400 animate-pulse'" />
                {{ STATUS_LABEL[entry.status] || entry.status }}
              </span>
            </td>
            <td class="py-3 px-4 text-right">
              <button class="text-xs text-red-400 hover:text-red-600 transition-colors" @click.stop="confirmDelete(entry.video_id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
