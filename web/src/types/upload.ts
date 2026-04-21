export type UploadStatus = 'idle' | 'uploading' | 'success' | 'error'

export interface VideoInfo {
  file: File
  name: string
  size: number
  duration?: number
  width?: number
  height?: number
}

export type AnalysisType = 'forehand' | 'backhand' | 'serve' | 'volley' | 'full'

export interface AnalysisTypeOption {
  value: AnalysisType
  label: string
  icon: string
  description: string
}
