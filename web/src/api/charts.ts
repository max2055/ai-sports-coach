import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export interface ServeHeightPoint {
  frame_number: number
  time_seconds: number
  height_pct: number
}

export interface HitPoint {
  frame_number: number
  x_pct: number
  y_pct: number
  issue_type?: string
}

export interface RadarDimension {
  name: string
  value: number
}

export interface IssueStat {
  issue_type: string
  count: number
  severity: 'high' | 'medium' | 'low'
}

export async function getServeHeightData(videoId: string): Promise<{ points: ServeHeightPoint[] }> {
  try {
    const res = await axios.get(`${API_BASE}/api/charts/${videoId}/serve-height`)
    return res.data
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(`Failed to load serve height data: ${error.response?.status} ${error.response?.data?.detail || error.message}`)
    }
    throw error
  }
}

export async function getHitPointData(videoId: string): Promise<{ points: HitPoint[] }> {
  try {
    const res = await axios.get(`${API_BASE}/api/charts/${videoId}/hit-points`)
    return res.data
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(`Failed to load hit point data: ${error.response?.status} ${error.response?.data?.detail || error.message}`)
    }
    throw error
  }
}

export async function getRadarData(videoId: string): Promise<{ dimensions: RadarDimension[]; overall_score: number }> {
  try {
    const res = await axios.get(`${API_BASE}/api/charts/${videoId}/radar`)
    return res.data
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(`Failed to load radar data: ${error.response?.status} ${error.response?.data?.detail || error.message}`)
    }
    throw error
  }
}

export async function getIssueStats(videoId: string): Promise<{ stats: IssueStat[]; total_issues: number; total_frames: number }> {
  try {
    const res = await axios.get(`${API_BASE}/api/charts/${videoId}/issues`)
    return res.data
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(`Failed to load issue stats: ${error.response?.status} ${error.response?.data?.detail || error.message}`)
    }
    throw error
  }
}