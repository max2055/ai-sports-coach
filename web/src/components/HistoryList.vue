<script setup lang="ts">
import type { HistoryEntry } from '../api/history'

defineProps<{ entries: HistoryEntry[] }>()
const emit = defineEmits<{ select: [videoId: string]; delete: [videoId: string] }>()

const TYPE_LABEL: Record<string, string> = { forehand: '正手', backhand: '反手', serve: '发球', volley: '截击', full: '全场' }
const STATUS_LABEL: Record<string, string> = { completed: '已完成', failed: '失败', pending: '分析中' }

function fmtDate(d: string) {
  const dt = new Date(d)
  return `${String(dt.getMonth()+1).padStart(2,'0')}-${String(dt.getDate()).padStart(2,'0')} ${String(dt.getHours()).padStart(2,'0')}:${String(dt.getMinutes()).padStart(2,'0')}`
}

function scoreColor(s: number) { return s >= 7 ? 'text-emerald-600' : s >= 5 ? 'text-amber-600' : 'text-red-600' }
function statusDot(s: string) { return s === 'completed' ? 'bg-emerald-400' : s === 'failed' ? 'bg-red-400' : 'bg-blue-400 animate-pulse' }
</script>

<template>
  <div>
    <!-- Empty -->
    <div v-if="entries.length === 0" class="text-center py-16">
      <svg class="w-12 h-12 text-zinc-300 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <p class="text-sm text-zinc-400">暂无分析记录</p>
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
          <tr v-for="entry in entries" :key="entry.video_id" class="hover:bg-zinc-50 cursor-pointer transition-colors" @click="emit('select', entry.video_id)">
            <td class="py-3 px-4 font-medium text-zinc-900 truncate max-w-[200px]">{{ entry.filename }}</td>
            <td class="py-3 px-4 text-zinc-500">{{ fmtDate(entry.created_at) }}</td>
            <td class="py-3 px-4 text-zinc-500">{{ TYPE_LABEL[entry.analysis_type] || entry.analysis_type }}</td>
            <td class="py-3 px-4">
              <span v-if="entry.overall_score != null" class="font-bold" :class="scoreColor(entry.overall_score)">{{ entry.overall_score }}/10</span>
              <span v-else class="text-zinc-300">—</span>
            </td>
            <td class="py-3 px-4">
              <span class="inline-flex items-center gap-1.5 text-xs">
                <span class="w-1.5 h-1.5 rounded-full" :class="statusDot(entry.status)" />
                {{ STATUS_LABEL[entry.status] || entry.status }}
              </span>
            </td>
            <td class="py-3 px-4 text-right">
              <button class="text-xs text-red-400 hover:text-red-600 transition-colors" @click.stop="emit('delete', entry.video_id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
