<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ trainingPlan: string }>()

const planItems = computed(() => {
  if (!props.trainingPlan) return []
  return props.trainingPlan.split('\n').filter(l => l.trim()).map(line => {
    const m = line.trim().match(/^(\d+)[.、]\s*(.*)/)
    return m ? { text: m[2], numbered: true } : { text: line.trim(), numbered: false }
  })
})
</script>

<template>
  <div class="rounded-xl bg-white p-5 shadow-sm border border-zinc-200">
    <h3 class="text-sm font-semibold text-zinc-900 mb-3 flex items-center gap-2">
      <svg class="w-4 h-4 text-tennis" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 011 1v3a1 1 0 11-2 0V8a1 1 0 011-1z" clip-rule="evenodd" />
      </svg>
      训练计划
    </h3>
    <div v-if="planItems.length > 0" class="space-y-2">
      <ol v-if="planItems.some(i => i.numbered)" class="space-y-2">
        <li v-for="(item, idx) in planItems" :key="idx" class="flex items-start gap-2">
          <span v-if="item.numbered" class="shrink-0 w-5 h-5 bg-tennis/10 text-tennis-dark rounded-full flex items-center justify-center text-xs font-semibold">{{ planItems.filter((j, k) => k <= idx && j.numbered).length }}</span>
          <p class="text-sm text-zinc-700">{{ item.text }}</p>
        </li>
      </ol>
      <div v-else class="space-y-1">
        <p v-for="(item, i) in planItems" :key="i" class="text-sm text-zinc-700">{{ item.text }}</p>
      </div>
    </div>
    <p v-else class="text-sm text-zinc-400 text-center py-3">暂无训练计划</p>
  </div>
</template>
