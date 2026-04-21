import { ref } from 'vue'
import { uploadVideo, type UploadResult } from '@/api/upload'
import type { AnalysisType } from '@/types/upload'

export function useUpload() {
  const uploading = ref(false)
  const progress = ref(0)
  const error = ref<string | null>(null)
  const result = ref<UploadResult | null>(null)

  async function upload(
    file: File,
    analysisType: AnalysisType
  ): Promise<UploadResult | null> {
    uploading.value = true
    progress.value = 0
    error.value = null
    result.value = null

    try {
      const data = await uploadVideo(file, analysisType, (percent) => {
        progress.value = percent
      })
      result.value = data
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Upload failed'
      return null
    } finally {
      uploading.value = false
    }
  }

  function reset() {
    uploading.value = false
    progress.value = 0
    error.value = null
    result.value = null
  }

  return {
    uploading,
    progress,
    error,
    result,
    upload,
    reset
  }
}
