<script setup lang="ts">
import { computed } from 'vue'
import type { RadarScores } from '../api/report'

const props = defineProps<{
  overallScore: number
  radarScores: RadarScores
}>()

const dimensionLabels: { key: keyof RadarScores; label: string }[] = [
  { key: 'hitting_technique', label: '击球技术' },
  { key: 'footwork', label: '步法移动' },
  { key: 'body_rotation', label: '身体旋转' },
  { key: 'timing', label: '击球节奏' },
  { key: 'fitness', label: '体能分配' },
  { key: 'tactics', label: '战术执行' },
]

const scoreColor = computed(() => {
  if (props.overallScore >= 7) return 'text-green-600 dark:text-green-400'
  if (props.overallScore >= 5) return 'text-yellow-600 dark:text-yellow-400'
  return 'text-red-600 dark:text-red-400'
})

const scoreBg = computed(() => {
  if (props.overallScore >= 7) return 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
  if (props.overallScore >= 5) return 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800'
  return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
})

function scoreBarColor(score: number): string {
  if (score >= 7) return 'bg-green-500'
  if (score >= 5) return 'bg-yellow-500'
  return 'bg-red-500'
}
</script>

<template>
  <div class="score-card rounded-xl border p-6 shadow-lg" :class="scoreBg">
    <div class="flex flex-col md:flex-row gap-6 items-center">
      <!-- Overall score -->
      <div class="flex-shrink-0 text-center">
        <div class="text-6xl font-bold" :class="scoreColor">
          {{ overallScore }}
        </div>
        <div class="text-sm text-gray-500 dark:text-gray-400 mt-1">
          / 10 综合评分
        </div>
      </div>

      <!-- Dimension scores -->
      <div class="flex-1 w-full">
        <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
          维度评分
        </h3>
        <div class="space-y-3">
          <div
            v-for="dim in dimensionLabels"
            :key="dim.key"
            class="flex items-center gap-3"
          >
            <span class="text-sm text-gray-600 dark:text-gray-400 w-20">
              {{ dim.label }}
            </span>
            <div class="flex-1 h-2 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-500"
                :class="scoreBarColor(radarScores[dim.key])"
                :style="{ width: `${(radarScores[dim.key] / 10) * 100}%` }"
              />
            </div>
            <span class="text-sm font-medium text-gray-900 dark:text-white w-10 text-right">
              {{ radarScores[dim.key] }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>