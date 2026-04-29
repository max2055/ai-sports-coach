<script setup lang="ts">
import type { HistoryEntry } from '../api/history'

defineProps<{
  entries: HistoryEntry[]
}>()

const emit = defineEmits<{
  select: [videoId: string]
  delete: [videoId: string]
}>()

const ANALYSIS_TYPE_MAP: Record<string, string> = {
  forehand: '正手',
  backhand: '反手',
  serve: '发球',
  volley: '截击',
  full: '全场综合',
}

const STATUS_MAP: Record<string, string> = {
  completed: '已完成',
  failed: '失败',
  pending: '分析中',
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return d.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function scoreColorClass(score: number): string {
  if (score >= 7) return 'text-green-600 dark:text-green-400'
  if (score >= 5) return 'text-yellow-600 dark:text-yellow-400'
  return 'text-red-600 dark:text-red-400'
}

function statusClass(status: string): string {
  const base = 'text-xs px-2 py-0.5 rounded font-medium'
  switch (status) {
    case 'completed':
      return `${base} bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400`
    case 'failed':
      return `${base} bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400`
    case 'pending':
      return `${base} bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400`
    default:
      return `${base} bg-gray-100 text-gray-700`
  }
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
    <!-- Empty state -->
    <div
      v-if="entries.length === 0"
      class="text-center py-16"
    >
      <svg
        class="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="1.5"
          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <p class="text-gray-500 dark:text-gray-400">暂无分析记录</p>
    </div>

    <!-- Table (desktop) -->
    <div v-else class="hidden sm:block bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 dark:bg-gray-700/50">
          <tr>
            <th class="text-left py-3 px-4 text-gray-600 dark:text-gray-400 font-medium">日期</th>
            <th class="text-left py-3 px-4 text-gray-600 dark:text-gray-400 font-medium">视频名</th>
            <th class="text-left py-3 px-4 text-gray-600 dark:text-gray-400 font-medium">分析类型</th>
            <th class="text-left py-3 px-4 text-gray-600 dark:text-gray-400 font-medium">评分</th>
            <th class="text-left py-3 px-4 text-gray-600 dark:text-gray-400 font-medium">状态</th>
            <th class="text-right py-3 px-4 text-gray-600 dark:text-gray-400 font-medium">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="entry in entries"
            :key="entry.video_id"
            class="border-t border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors cursor-pointer"
            @click="emit('select', entry.video_id)"
          >
            <td class="py-3 px-4 text-gray-600 dark:text-gray-400 whitespace-nowrap">
              {{ formatDate(entry.created_at) }}
            </td>
            <td class="py-3 px-4 text-gray-900 dark:text-white font-medium truncate max-w-xs">
              {{ entry.filename }}
            </td>
            <td class="py-3 px-4 text-gray-600 dark:text-gray-400">
              {{ ANALYSIS_TYPE_MAP[entry.analysis_type] || entry.analysis_type }}
            </td>
            <td class="py-3 px-4">
              <span
                v-if="entry.overall_score != null"
                class="font-semibold"
                :class="scoreColorClass(entry.overall_score)"
              >
                {{ entry.overall_score }}/10
              </span>
              <span v-else class="text-gray-400">—</span>
            </td>
            <td class="py-3 px-4">
              <span :class="statusClass(entry.status)">
                {{ STATUS_MAP[entry.status] || entry.status }}
              </span>
            </td>
            <td class="py-3 px-4 text-right">
              <button
                class="text-red-500 hover:text-red-700 dark:hover:text-red-400 transition-colors px-2 py-1 text-xs font-medium"
                @click.stop="emit('delete', entry.video_id)"
              >
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Cards (mobile) -->
    <div v-else class="sm:hidden space-y-3">
      <div
        v-for="entry in entries"
        :key="entry.video_id"
        class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4"
        @click="emit('select', entry.video_id)"
      >
        <div class="flex items-start justify-between mb-2">
          <span class="text-sm font-medium text-gray-900 dark:text-white truncate flex-1">
            {{ entry.filename }}
          </span>
          <button
            class="text-red-500 hover:text-red-700 text-xs font-medium ml-2 flex-shrink-0"
            @click.stop="emit('delete', entry.video_id)"
          >
            删除
          </button>
        </div>
        <div class="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
          <span>{{ formatDate(entry.created_at) }}</span>
          <span>{{ ANALYSIS_TYPE_MAP[entry.analysis_type] || entry.analysis_type }}</span>
          <span v-if="entry.overall_score != null" :class="scoreColorClass(entry.overall_score)">
            {{ entry.overall_score }}/10
          </span>
          <span :class="statusClass(entry.status)">
            {{ STATUS_MAP[entry.status] || entry.status }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
