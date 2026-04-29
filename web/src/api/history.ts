import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export interface HistoryEntry {
  video_id: string
  filename: string
  analysis_type: string
  status: 'completed' | 'failed' | 'pending'
  created_at: string
  completed_at?: string
  overall_score?: number
  duration?: number
}

export interface HistoryList {
  entries: HistoryEntry[]
  total: number
}

export async function getHistory(params?: {
  search?: string
  analysis_type?: string
  status_filter?: string
}): Promise<HistoryList> {
  const response = await axios.get<HistoryList>(`${API_BASE}/api/history`, { params })
  return response.data
}

export async function deleteHistoryEntry(videoId: string): Promise<void> {
  await axios.delete(`${API_BASE}/api/history/${videoId}`)
}
