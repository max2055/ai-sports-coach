<script setup lang="ts">
import type { Strength } from '../api/report'

defineProps<{ strengths: Strength[] }>()
</script>

<template>
  <div class="rounded-xl bg-white p-5 shadow-sm border border-zinc-200">
    <h3 class="text-sm font-semibold text-zinc-900 mb-3 flex items-center gap-2">
      <svg class="w-4 h-4 text-emerald-500" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
      </svg>
      亮点
    </h3>
    <ul v-if="strengths.length > 0" class="space-y-2">
      <li v-for="(s, i) in strengths" :key="i" class="flex items-start gap-3 p-3 bg-emerald-50 rounded-lg">
        <svg class="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        <div class="flex-1">
          <p class="text-sm text-zinc-900">{{ s.text }}</p>
          <div v-if="s.frame_refs.length > 0" class="flex gap-1 mt-1 flex-wrap">
            <span v-for="ref in s.frame_refs" :key="ref" class="text-[10px] px-1.5 py-0.5 bg-emerald-100 text-emerald-600 rounded">{{ ref }}</span>
          </div>
        </div>
      </li>
    </ul>
    <p v-else class="text-sm text-zinc-400 text-center py-3">暂无亮点记录</p>
  </div>
</template>
