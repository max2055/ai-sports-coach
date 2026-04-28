<script setup lang="ts">
import type { Strength } from '../api/report'

defineProps<{
  strengths: Strength[]
}>()
</script>

<template>
  <div class="strengths-list rounded-xl bg-white dark:bg-gray-800 p-6 shadow-lg">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
      <svg class="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
      </svg>
      亮点
    </h3>

    <ul v-if="strengths.length > 0" class="space-y-3">
      <li
        v-for="(strength, index) in strengths"
        :key="index"
        class="flex items-start gap-3 p-3 bg-green-50 dark:bg-green-900/10 rounded-lg"
      >
        <svg class="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        <div class="flex-1">
          <p class="text-gray-900 dark:text-white">{{ strength.text }}</p>
          <div v-if="strength.frame_refs.length > 0" class="flex gap-1 mt-2 flex-wrap">
            <span
              v-for="ref in strength.frame_refs"
              :key="ref"
              class="text-xs px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded"
            >
              {{ ref }}
            </span>
          </div>
        </div>
      </li>
    </ul>

    <p v-else class="text-gray-500 dark:text-gray-400 text-center py-4">
      暂无亮点记录
    </p>
  </div>
</template>