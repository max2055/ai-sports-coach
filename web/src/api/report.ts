import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export interface Strength {
  text: string
  frame_refs: string[]
}

export interface Issue {
  text: string
  frame_refs: string[]
  severity: 'high' | 'medium' | 'low'
}

export interface ImprovementSuggestion {
  text: string
  number: number
}

export interface IssueSummaryRow {
  frame_number: number
  issue_type: string
  body_part: string
  description: string
  priority: 'high' | 'medium' | 'low'
}

export interface RadarScores {
  hitting_technique: number
  footwork: number
  body_rotation: number
  timing: number
  fitness: number
  tactics: number
}

export interface CoachReport {
  video_id: string
  overall_score: number
  radar_scores: RadarScores
  strengths: Strength[]
  issues: Issue[]
  improvement_suggestions: ImprovementSuggestion[]
  issue_summary: IssueSummaryRow[]
  coach_summary: string
  training_plan: string
}

export async function getCoachReport(videoId: string): Promise<CoachReport> {
  const response = await axios.get<CoachReport>(`${API_BASE}/api/report/${videoId}`)
  return response.data
}