<script setup lang="ts">
import { computed } from 'vue'
import type { RadarScores } from '../api/report'

const props = defineProps<{ overallScore: number; radarScores: RadarScores }>()

const dimensions: { key: keyof RadarScores; label: string }[] = [
  { key: 'hitting_technique', label: '击球技术' },
  { key: 'footwork', label: '步法移动' },
  { key: 'body_rotation', label: '身体旋转' },
  { key: 'timing', label: '击球节奏' },
  { key: 'fitness', label: '体能分配' },
  { key: 'tactics', label: '战术执行' },
]

const scoreColor = computed(() => props.overallScore >= 7 ? 'text-emerald-600' : props.overallScore >= 5 ? 'text-amber-600' : 'text-red-600')
const scoreRing = computed(() => props.overallScore >= 7 ? 'border-emerald-200 bg-emerald-50' : props.overallScore >= 5 ? 'border-amber-200 bg-amber-50' : 'border-red-200 bg-red-50')
function barColor(v: number) { return v >= 7 ? 'bg-emerald-500' : v >= 5 ? 'bg-amber-500' : 'bg-red-500' }
</script>

<template>
  <div class="rounded-xl bg-white p-5 shadow-sm border border-zinc-200">
    <div class="flex flex-col sm:flex-row items-start gap-5">
      <div class="flex items-center justify-center w-20 h-20 rounded-full border-4 shrink-0" :class="scoreRing">
        <div class="text-center">
          <div class="text-3xl font-bold leading-none" :class="scoreColor">{{ overallScore }}</div>
          <div class="text-[10px] text-zinc-400 mt-0.5">/ 10</div>
        </div>
      </div>
      <div class="flex-1 w-full">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-y-2 gap-x-4">
          <div v-for="d in dimensions" :key="d.key" class="flex items-center gap-2">
            <span class="text-xs text-zinc-500 w-16 shrink-0">{{ d.label }}</span>
            <div class="flex-1 h-1.5 bg-zinc-100 rounded-full overflow-hidden">
              <div class="h-full rounded-full transition-all" :class="barColor(radarScores[d.key])" :style="{ width: `${(radarScores[d.key] / 10) * 100}%` }" />
            </div>
            <span class="text-xs font-semibold text-zinc-600 w-5 text-right">{{ radarScores[d.key] }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
