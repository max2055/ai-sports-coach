<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  trainingPlan: string
}>()

// Parse training plan into structured items
const planItems = computed(() => {
  if (!props.trainingPlan) return []

  const lines = props.trainingPlan.split('\n').filter(line => line.trim())
  const items: { text: string; isNumbered: boolean }[] = []

  for (const line of lines) {
    const trimmed = line.trim()
    // Check for numbered items: "1. xxx", "2. xxx"
    const numberMatch = trimmed.match(/^(\d+)[.、]\s*(.*)/)
    if (numberMatch) {
      items.push({
        text: numberMatch[2],
        isNumbered: true,
      })
    } else if (trimmed.startsWith('-') || trimmed.startsWith('*')) {
      items.push({
        text: trimmed.replace(/^[-*]\s*/, ''),
        isNumbered: false,
      })
    } else {
      // Plain paragraph
      items.push({
        text: trimmed,
        isNumbered: false,
      })
    }
  }

  return items
})
</script>

<template>
  <div class="training-plan rounded-xl bg-white dark:bg-gray-800 p-6 shadow-lg">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
      <svg class="w-5 h-5 text-purple-500" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 011 1v3a1 1 0 11-2 0V8a1 1 0 011-1z" clip-rule="evenodd" />
      </svg>
      专项训练计划
    </h3>

    <div v-if="planItems.length > 0" class="space-y-3">
      <ol v-if="planItems.some(item => item.isNumbered)" class="space-y-3">
        <li
          v-for="(item, index) in planItems"
          :key="index"
          class="flex items-start gap-3"
          :class="{
            'p-3 bg-purple-50 dark:bg-purple-900/10 rounded-lg': item.isNumbered,
            'text-gray-600 dark:text-gray-400 text-sm': !item.isNumbered,
          }"
        >
          <span
            v-if="item.isNumbered"
            class="flex-shrink-0 w-6 h-6 bg-purple-500 text-white rounded-full flex items-center justify-center text-sm font-medium"
          >
            {{ planItems.filter((i, idx) => idx <= index && i.isNumbered).length }}
          </span>
          <p class="text-gray-900 dark:text-white">{{ item.text }}</p>
        </li>
      </ol>
      <div v-else class="space-y-2">
        <p
          v-for="(item, index) in planItems"
          :key="index"
          class="text-gray-700 dark:text-gray-300"
        >
          {{ item.text }}
        </p>
      </div>
    </div>

    <p v-else class="text-gray-500 dark:text-gray-400 text-center py-4">
      暂无训练计划
    </p>
  </div>
</template>