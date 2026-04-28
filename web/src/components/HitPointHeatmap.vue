<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import * as echarts from 'echarts'
import type { HitPoint } from '../api/charts'

const props = defineProps<{
  points: HitPoint[]
}>()

const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const hasIssue = (issueType?: string) => {
  return issueType && !issueType.startsWith('GOOD')
}

const chartData = computed(() => {
  return props.points.map(p => ({
    value: [p.x_pct, p.y_pct],
    itemStyle: {
      color: hasIssue(p.issue_type) ? '#ef4444' : '#3b82f6'
    },
    frame: p.frame_number,
    issue: p.issue_type
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
      text: '击球点分布',
      left: 'center',
      textStyle: { fontSize: 16, fontWeight: 600 }
    },
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const data = params.data
        return `帧号: ${data.frame}<br/>X: ${data.value[0].toFixed(1)}%<br/>Y: ${data.value[1].toFixed(1)}%<br/>状态: ${data.issue || '正常'}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: 'X 位置 (%)',
      nameLocation: 'middle',
      nameGap: 30,
      min: 0,
      max: 100
    },
    yAxis: {
      type: 'value',
      name: 'Y 位置 (%)',
      nameLocation: 'middle',
      nameGap: 40,
      min: 0,
      max: 100
    },
    series: [{
      type: 'scatter',
      data: chartData.value,
      symbolSize: 12,
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }],
    legend: {
      bottom: 0,
      data: ['正常', '问题'],
      formatter: (name: string) => name
    }
  }

  chartInstance.setOption(option)
}

const handleResize = () => {
  chartInstance?.resize()
}

watch(() => props.points, () => {
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
    <div class="flex justify-center gap-4 mt-2 text-sm">
      <span class="flex items-center gap-1">
        <span class="w-3 h-3 rounded-full bg-blue-500" />
        正常
      </span>
      <span class="flex items-center gap-1">
        <span class="w-3 h-3 rounded-full bg-red-500" />
        问题
      </span>
    </div>
  </div>
</template>