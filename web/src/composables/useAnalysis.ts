import { ref, onUnmounted } from 'vue'
import { startAnalysis, getAnalysisStatus, retryAnalysis, type AnalysisState } from '@/api/analysis'

export type AnalysisStatus = AnalysisState['status']

const STATUS_TEXT: Record<AnalysisStatus, string> = {
  pending: '等待中',
  extracting: '提取帧',
  analyzing: 'AI分析中',
  annotating: '标注帧',
  completed: '完成',
  failed: '失败'
}

export function useAnalysis(videoId: string) {
  const status = ref<AnalysisStatus>('pending')
  const progress = ref(0)
  const error = ref<string | null>(null)
  const resultPath = ref<string | null>(null)
  const isLoading = ref(false)
  const statusText = ref('准备开始')

  let pollInterval: ReturnType<typeof setInterval> | null = null

  function getStatusText(s: AnalysisStatus): string {
    return STATUS_TEXT[s] || s
  }

  function clearPolling() {
    if (pollInterval) {
      clearInterval(pollInterval)
      pollInterval = null
    }
  }

  async function pollStatus() {
    try {
      const state = await getAnalysisStatus(videoId)
      status.value = state.status
      progress.value = state.progress
      statusText.value = getStatusText(state.status)

      if (state.error) {
        error.value = state.error
      }

      if (state.result_path) {
        resultPath.value = state.result_path
      }

      if (state.status === 'completed' || state.status === 'failed') {
        clearPolling()
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取状态失败'
      clearPolling()
    }
  }

  async function start() {
    isLoading.value = true
    error.value = null

    try {
      const result = await startAnalysis(videoId)
      status.value = result.status as AnalysisStatus
      statusText.value = getStatusText(status.value)

      // Start polling every 2 seconds
      pollInterval = setInterval(pollStatus, 2000)

      // Delay first poll to give background task time to initialize
      setTimeout(async () => await pollStatus(), 1000)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '启动分析失败'
      status.value = 'failed'
      statusText.value = getStatusText('failed')
    } finally {
      isLoading.value = false
    }
  }

  async function retry() {
    isLoading.value = true
    error.value = null
    status.value = 'pending'
    progress.value = 0
    statusText.value = '准备重试'

    try {
      const result = await retryAnalysis(videoId)
      status.value = result.status as AnalysisStatus
      statusText.value = getStatusText(status.value)

      // Start polling
      pollInterval = setInterval(pollStatus, 2000)
      setTimeout(async () => await pollStatus(), 1000)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '重试失败'
      status.value = 'failed'
      statusText.value = getStatusText('failed')
    } finally {
      isLoading.value = false
    }
  }

  // Cleanup on unmount
  onUnmounted(() => {
    clearPolling()
  })

  return {
    status,
    progress,
    error,
    resultPath,
    isLoading,
    statusText,
    start,
    retry,
    getStatusText
  }
}