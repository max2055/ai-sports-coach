<script setup lang="ts">
import { computed } from 'vue'
import type { Issue, ImprovementSuggestion } from '../api/report'

const props = defineProps<{ issues: Issue[]; improvementSuggestions?: ImprovementSuggestion[] }>()

const sortedIssues = computed(() => {
  const order = { high: 0, medium: 1, low: 2 }
  return [...props.issues].sort((a, b) => order[a.severity] - order[b.severity])
})

function sevColor(s: string) {
  return s === 'high' ? 'bg-red-100 text-red-600' : s === 'medium' ? 'bg-orange-100 text-orange-600' : 'bg-yellow-100 text-yellow-600'
}
function sevLabel(s: string) { return s === 'high' ? '严重' : s === 'medium' ? '中等' : '轻微' }
</script>

<template>
  <div class="rounded-xl bg-white p-5 shadow-sm border border-zinc-200">
    <h3 class="text-sm font-semibold text-zinc-900 mb-3 flex items-center gap-2">
      <svg class="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
      </svg>
      问题分析 <span class="text-xs font-normal text-zinc-400">({{ issues.length }})</span>
    </h3>

    <div v-if="sortedIssues.length > 0" class="space-y-2">
      <details v-for="(issue, i) in sortedIssues" :key="i" class="group border border-zinc-200 rounded-lg" :open="i === 0">
        <summary class="flex items-center gap-3 p-3 cursor-pointer list-none hover:bg-zinc-50 rounded-lg transition-colors">
          <svg class="w-4 h-4 text-red-400 shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
          <span class="flex-1 text-sm text-zinc-900">{{ issue.text }}</span>
          <span class="text-[10px] px-2 py-0.5 rounded font-medium" :class="sevColor(issue.severity)">{{ sevLabel(issue.severity) }}</span>
          <svg class="w-3.5 h-3.5 text-zinc-400 transition-transform group-open:rotate-180" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
        </summary>
        <div v-if="issue.frame_refs.length > 0" class="px-3 pb-3 border-t border-zinc-100 pt-2">
          <span class="text-[10px] text-zinc-400">相关帧: </span>
          <div class="flex gap-1 mt-1 flex-wrap">
            <span v-for="ref in issue.frame_refs" :key="ref" class="text-[10px] px-1.5 py-0.5 bg-red-50 text-red-600 rounded">{{ ref }}</span>
          </div>
        </div>
      </details>
    </div>
    <p v-else class="text-sm text-zinc-400 text-center py-3">未发现问题</p>

    <!-- Improvement suggestions -->
    <div v-if="improvementSuggestions && improvementSuggestions.length > 0" class="mt-4 pt-4 border-t border-zinc-100">
      <h4 class="text-sm font-semibold text-zinc-900 mb-3 flex items-center gap-2">
        <svg class="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd" />
        </svg>
        改进建议
      </h4>
      <ol class="space-y-2">
        <li v-for="s in improvementSuggestions" :key="s.number" class="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
          <span class="shrink-0 w-5 h-5 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs font-medium">{{ s.number }}</span>
          <p class="text-sm text-zinc-900">{{ s.text }}</p>
        </li>
      </ol>
    </div>
  </div>
</template>
