<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { RadarDimension } from '../api/charts'

const props = defineProps<{
  dimensions: RadarDimension[]
  overallScore: number
}>()

const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value, undefined, { renderer: 'canvas' })
  updateChart()
}

const updateChart = () => {
  if (!chartInstance) return

  const option: echarts.EChartsOption = {
    title: {
      text: '动作一致性评分',
      left: 'center',
      textStyle: { fontSize: 16, fontWeight: 600 }
    },
    tooltip: {
      trigger: 'item'
    },
    radar: {
      indicator: props.dimensions.map(d => ({
        name: d.name,
        max: 10
      })),
      center: ['50%', '55%'],
      radius: '60%',
      axisName: {
        color: '#6b7280',
        fontSize: 12
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(59, 130, 246, 0.05)', 'rgba(59, 130, 246, 0.1)', 'rgba(59, 130, 246, 0.15)', 'rgba(59, 130, 246, 0.2)', 'rgba(59, 130, 246, 0.25)']
        }
      }
    },
    series: [{
      type: 'radar',
      data: [{
        value: props.dimensions.map(d => d.value),
        name: '当前表现',
        areaStyle: {
          color: 'rgba(59, 130, 246, 0.3)'
        },
        lineStyle: {
          color: '#3b82f6',
          width: 2
        },
        itemStyle: {
          color: '#3b82f6'
        }
      }, {
        value: Array(props.dimensions.length).fill(8),
        name: '目标标准',
        areaStyle: {
          color: 'rgba(34, 197, 94, 0.15)'
        },
        lineStyle: {
          color: '#22c55e',
          width: 1,
          type: 'dashed'
        },
        itemStyle: {
          color: '#22c55e'
        }
      }]
    }],
    legend: {
      bottom: 0,
      data: ['当前表现', '目标标准']
    }
  }

  chartInstance.setOption(option)
}

const handleResize = () => {
  chartInstance?.resize()
}

watch(() => props.dimensions, () => {
  updateChart()
}, { deep: true })

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})
</script>

<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4">
    <div ref="chartRef" class="w-full h-72" />
    <div class="text-center mt-2">
      <span class="text-lg font-semibold text-gray-700 dark:text-gray-300">综合评分: </span>
      <span class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ overallScore }}/10</span>
    </div>
  </div>
</template>