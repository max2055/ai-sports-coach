import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export type ProVideoType = 'forehand' | 'backhand' | 'serve' | 'volley'

export interface ProVideo {
  id: string
  type: ProVideoType
  name: string
  description: string
  file: string
  duration?: number
}

export interface ProVideoList {
  videos: ProVideo[]
}

export async function getProVideos(type?: ProVideoType): Promise<ProVideo[]> {
  const url = type
    ? `${API_BASE}/api/pros?type=${type}`
    : `${API_BASE}/api/pros`
  const response = await axios.get<ProVideoList>(url)
  return response.data.videos
}

export async function getProVideo(videoId: string): Promise<ProVideo> {
  const response = await axios.get<ProVideo>(`${API_BASE}/api/pros/${videoId}`)
  return response.data
}

export function getProVideoFileUrl(videoId: string): string {
  return `${API_BASE}/api/pros/${videoId}/file`
}