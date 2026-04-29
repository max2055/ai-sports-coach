<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import * as echarts from 'echarts'
import type { IssueStat } from '../api/charts'

const props = defineProps<{
  stats: IssueStat[]
}>()

const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const severityColor = (severity: string) => {
  switch (severity) {
    case 'high': return '#ef4444'
    case 'medium': return '#f97316'
    case 'low': return '#eab308'
    default: return '#6b7280'
  }
}

const chartData = computed(() => {
  return props.stats.map(s => ({
    value: s.count,
    itemStyle: { color: severityColor(s.severity) },
    name: s.issue_type
  }))
})

const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value, undefined, { renderer: 'canvas' })
  updateChart()
}

const updateChart = () => {
  if (!chartInstance) return

  const option: echarts.EChartsOption = {
    title: {
      text: '问题类型统计',
      left: 'center',
      textStyle: { fontSize: 16, fontWeight: 600 }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        if (!params || !params.length) return ''
        const data = params[0]
        return `${data.name}<br/>次数: ${data.value}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: props.stats.map(s => s.issue_type),
      axisLabel: {
        rotate: 45,
        interval: 0,
        fontSize: 10
      }
    },
    yAxis: {
      type: 'value',
      name: '出现次数',
      minInterval: 1
    },
    series: [{
      type: 'bar',
      data: chartData.value,
      barMaxWidth: 40,
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }

  chartInstance.setOption(option)
}

const handleResize = () => {
  chartInstance?.resize()
}

watch(() => props.stats, () => {
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
    <div ref="chartRef" class="w-full h-64" />
    <div v-if="stats.length === 0" class="text-center text-gray-500 dark:text-gray-400 py-8">
      暂无问题统计数据
    </div>
    <div v-else class="flex justify-center gap-4 mt-2 text-sm flex-wrap">
      <span class="flex items-center gap-1">
        <span class="w-3 h-3 rounded bg-red-500" />
        高严重度
      </span>
      <span class="flex items-center gap-1">
        <span class="w-3 h-3 rounded bg-orange-500" />
        中严重度
      </span>
      <span class="flex items-center gap-1">
        <span class="w-3 h-3 rounded bg-yellow-500" />
        低严重度
      </span>
    </div>
  </div>
</template>