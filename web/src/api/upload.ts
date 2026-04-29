import axios from 'axios'
import type { AnalysisType } from '@/types/upload'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export interface UploadResult {
  video_id: string
  filename: string
  analysis_type: AnalysisType
  metadata: {
    duration: number
    width: number
    height: number
    size: number
    format: string
  }
  message: string
}

export async function uploadVideo(
  file: File,
  analysisType: AnalysisType,
  onProgress: (percent: number) => void
): Promise<UploadResult> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('analysis_type', analysisType)

  const response = await axios.post<UploadResult>(`${API_BASE}/api/upload`, formData, {
    onUploadProgress: (progressEvent) => {
      const percent = progressEvent.total
        ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
        : 0
      onProgress(percent)
    }
  })

  return response.data
}
