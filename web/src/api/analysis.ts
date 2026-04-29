import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export interface AnalysisState {
  video_id: string
  status: 'pending' | 'extracting' | 'analyzing' | 'annotating' | 'completed' | 'failed'
  progress: number
  error?: string
  result_path?: string
}

export async function startAnalysis(videoId: string): Promise<{ video_id: string; status: AnalysisState['status'] }> {
  const response = await axios.post(`${API_BASE}/api/analyze/${videoId}`)
  return response.data
}

export async function getAnalysisStatus(videoId: string): Promise<AnalysisState> {
  const response = await axios.get(`${API_BASE}/api/status/${videoId}`)
  return response.data
}

export async function retryAnalysis(videoId: string): Promise<{ video_id: string; status: AnalysisState['status'] }> {
  const response = await axios.post(`${API_BASE}/api/retry/${videoId}`)
  return response.data
}