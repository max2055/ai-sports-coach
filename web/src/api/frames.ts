import axios from 'axios'
import type { AnalysisType } from '../types/upload'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Issue types matching backend
export type IssueType =
  | 'LATE BACKSWING'
  | 'WRONG GRIP'
  | 'GRIP CHANGE ERR'
  | 'WRONG CONTACT'
  | 'ELBOW DROP'
  | 'NO HIP ROT'
  | 'LATE SHOULDER'
  | 'NO FOLLOW-THRU'
  | 'POOR FOOTWORK'
  | 'NO SPLIT STEP'
  | 'LATE WEIGHT'
  | 'WRONG STANCE'
  | 'WRONG POSITION'
  | 'BAD TOSS'
  | 'NO LEG DRIVE'
  | 'OFF BALANCE'
  | 'TELEGRAPH'
  | 'WRONG SPIN'
  | 'GOOD FORM'
  | 'GOOD FOOTWORK'
  | 'GOOD TACTICS'

export interface BodyPartAnnotation {
  x_pct: number
  y_pct: number
  radius_pct: number
  issue_type?: IssueType
  issue_note?: string
}

export interface PlayerAnnotation {
  id?: string
  body: BodyPartAnnotation
  hand_l: BodyPartAnnotation  // Racket hand (dominant hand)
  hand_r: BodyPartAnnotation  // Off hand (non-dominant hand)
  foot_l: BodyPartAnnotation  // Front/lead foot
  foot_r: BodyPartAnnotation  // Back foot
}

export interface FrameAnnotation {
  frame_number: number
  players: PlayerAnnotation[]
  frame_summary?: string
}

export interface IssueFrame {
  frame_number: number
  issue_types: IssueType[]
  thumbnail_url: string
  time_seconds: number
}

/**
 * Get frame annotations for a video
 */
export async function getFrameAnnotations(videoId: string): Promise<FrameAnnotation[]> {
  const response = await axios.get<FrameAnnotation[]>(`${API_BASE}/api/frames/${videoId}`)
  return response.data
}

/**
 * Get issue frames for a video, optionally filtered by issue type
 */
export async function getIssueFrames(videoId: string, issueType?: string): Promise<IssueFrame[]> {
  const url = issueType
    ? `${API_BASE}/api/issues/${videoId}?issue_type=${encodeURIComponent(issueType)}`
    : `${API_BASE}/api/issues/${videoId}`
  const response = await axios.get<IssueFrame[]>(url)
  return response.data
}

/**
 * Get URL for annotated frame image
 */
export function getAnnotatedImageUrl(videoId: string, frameNumber: number): string {
  return `${API_BASE}/api/annotated/${videoId}/${frameNumber}`
}

/**
 * Get URL for original video file
 */
export function getVideoUrl(videoId: string): string {
  return `${API_BASE}/api/video/${videoId}`
}