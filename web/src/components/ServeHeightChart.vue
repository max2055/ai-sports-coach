<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { ServeHeightPoint } from '../api/charts'

const props = defineProps<{
  points: ServeHeightPoint[]
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
      text: '发球高度趋势',
      left: 'center',
      textStyle: { fontSize: 16, fontWeight: 600 }
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        if (!params || !params.length) return ''
        const data = params[0]
        const timeVal = data.value[0]
        const point = props.points.find(p => Math.abs(p.time_seconds - timeVal) < 0.001)
        if (point) {
          return `帧号: ${point.frame_number}<br/>时间: ${timeVal.toFixed(2)}s<br/>高度: ${(100 - data.value[1]).toFixed(1)}%`
        }
        return `时间: ${timeVal.toFixed(2)}s<br/>高度: ${(100 - data.value[1]).toFixed(1)}%`
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
      name: '时间 (秒)',
      nameLocation: 'middle',
      nameGap: 30
    },
    yAxis: {
      type: 'value',
      name: '高度 (%)',
      nameLocation: 'middle',
      nameGap: 40,
      min: 0,
      max: 100,
      inverse: true
    },
    series: [{
      type: 'line',
      data: props.points.map(p => [p.time_seconds, p.height_pct]),
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { width: 2, color: '#3b82f6' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
          { offset: 1, color: 'rgba(59, 130, 246, 0.05)' }
        ])
      }
    }]
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
  </div>
</template>