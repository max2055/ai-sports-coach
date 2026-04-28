<script setup lang="ts">
import { computed } from 'vue'
import type { Issue, ImprovementSuggestion } from '../api/report'

const props = defineProps<{
  issues: Issue[]
  improvementSuggestions?: ImprovementSuggestion[]
}>()

// Sort issues by severity: high first, then medium, then low
const sortedIssues = computed(() => {
  const severityOrder = { high: 0, medium: 1, low: 2 }
  return [...props.issues].sort(
    (a, b) => severityOrder[a.severity] - severityOrder[b.severity]
  )
})

function severityColor(severity: string): string {
  switch (severity) {
    case 'high': return 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'
    case 'medium': return 'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300'
    default: return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300'
  }
}

function severityLabel(severity: string): string {
  switch (severity) {
    case 'high': return '严重'
    case 'medium': return '中等'
    default: return '轻微'
  }
}
</script>

<template>
  <div class="issue-analysis rounded-xl bg-white dark:bg-gray-800 p-6 shadow-lg">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
      <svg class="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
      </svg>
      问题分析
      <span class="text-sm font-normal text-gray-500 dark:text-gray-400">
        ({{ issues.length }} 个问题)
      </span>
    </h3>

    <!-- Issues list -->
    <div v-if="sortedIssues.length > 0" class="space-y-3">
      <details
        v-for="(issue, index) in sortedIssues"
        :key="index"
        class="group border border-gray-200 dark:border-gray-700 rounded-lg"
        :open="index === 0"
      >
        <summary class="flex items-center gap-3 p-4 cursor-pointer list-none hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-lg transition-colors">
          <svg class="w-5 h-5 text-red-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
          <span class="flex-1 text-gray-900 dark:text-white">{{ issue.text }}</span>
          <span
            class="text-xs px-2 py-1 rounded font-medium"
            :class="severityColor(issue.severity)"
          >
            {{ severityLabel(issue.severity) }}
          </span>
          <svg class="w-4 h-4 text-gray-400 transition-transform group-open:rotate-180" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </summary>

        <!-- Expanded content -->
        <div class="px-4 pb-4 border-t border-gray-100 dark:border-gray-700 pt-3">
          <div v-if="issue.frame_refs.length > 0" class="mb-3">
            <span class="text-sm text-gray-500 dark:text-gray-400">相关帧: </span>
            <div class="flex gap-1 mt-1 flex-wrap">
              <span
                v-for="ref in issue.frame_refs"
                :key="ref"
                class="text-xs px-2 py-0.5 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded"
              >
                {{ ref }}
              </span>
            </div>
          </div>
        </div>
      </details>
    </div>

    <p v-else class="text-gray-500 dark:text-gray-400 text-center py-4">
      未发现问题
    </p>

    <!-- Improvement suggestions -->
    <div
      v-if="improvementSuggestions && improvementSuggestions.length > 0"
      class="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700"
    >
      <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
        <svg class="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd" />
        </svg>
        改进建议
      </h4>
      <ol class="space-y-2">
        <li
          v-for="suggestion in improvementSuggestions"
          :key="suggestion.number"
          class="flex items-start gap-3 p-3 bg-blue-50 dark:bg-blue-900/10 rounded-lg"
        >
          <span class="flex-shrink-0 w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-medium">
            {{ suggestion.number }}
          </span>
          <p class="text-gray-900 dark:text-white">{{ suggestion.text }}</p>
        </li>
      </ol>
    </div>
  </div>
</template>