<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import AnnotatedVideoPlayer from '../components/AnnotatedVideoPlayer.vue'
import FrameTimeline from '../components/FrameTimeline.vue'
import IssueFrameList from '../components/IssueFrameList.vue'
import ServeHeightChart from '../components/ServeHeightChart.vue'
import HitPointHeatmap from '../components/HitPointHeatmap.vue'
import ConsistencyRadar from '../components/ConsistencyRadar.vue'
import IssueStatsChart from '../components/IssueStatsChart.vue'
import ProVideoSelector from '../components/ProVideoSelector.vue'
import ComparisonPlayer from '../components/ComparisonPlayer.vue'
import KeyframeMarker from '../components/KeyframeMarker.vue'
import {
  getFrameAnnotations,
  getIssueFrames,
  getVideoUrl,
  type FrameAnnotation,
  type IssueFrame
} from '../api/frames'
import {
  getServeHeightData,
  getHitPointData,
  getRadarData,
  getIssueStats,
  type ServeHeightPoint,
  type HitPoint,
  type RadarDimension,
  type IssueStat
} from '../api/charts'
import { type ProVideo, type ProVideoType } from '../api/pros'
import { getCoachReport, type CoachReport } from '../api/report'
import ScoreCard from '../components/ScoreCard.vue'
import StrengthsList from '../components/StrengthsList.vue'
import IssueAnalysis from '../components/IssueAnalysis.vue'
import TrainingPlan from '../components/TrainingPlan.vue'
import CoachSummary from '../components/CoachSummary.vue'

const route = useRoute()
const videoId = route.params.videoId as string

// State
const annotations = ref<FrameAnnotation[]>([])
const issueFrames = ref<IssueFrame[]>([])
const currentTime = ref(0)
const duration = ref(0)
const isLoading = ref(true)
const error = ref<string | null>(null)

// Chart data state
const serveHeightPoints = ref<ServeHeightPoint[]>([])
const hitPoints = ref<HitPoint[]>([])
const radarDimensions = ref<RadarDimension[]>([])
const radarOverallScore = ref(0)
const issueStats = ref<IssueStat[]>([])
const chartsLoading = ref(true)

// Report data state
const coachReport = ref<CoachReport | null>(null)
const reportLoading = ref(true)

// Video player ref
const playerRef = ref<InstanceType<typeof AnnotatedVideoPlayer> | null>(null)

// Video URL
const videoUrl = computed(() => getVideoUrl(videoId))

// Load data on mount
onMounted(async () => {
  try {
    isLoading.value = true
    error.value = null

    // Load annotations and issue frames in parallel
    const [annotationsData, issuesData] = await Promise.all([
      getFrameAnnotations(videoId),
      getIssueFrames(videoId)
    ])

    annotations.value = annotationsData
    issueFrames.value = issuesData
  } catch (err) {
    console.error('Failed to load report data:', err)
    error.value = '加载报告数据失败，请稍后重试'
  } finally {
    isLoading.value = false
  }

  // Load chart data
  try {
    chartsLoading.value = true
    const [serveHeightData, hitPointData, radarData, issueStatsData] = await Promise.all([
      getServeHeightData(videoId).catch(() => ({ points: [] })),
      getHitPointData(videoId).catch(() => ({ points: [] })),
      getRadarData(videoId).catch(() => ({ dimensions: [], overall_score: 0 })),
      getIssueStats(videoId).catch(() => ({ stats: [], total_issues: 0, total_frames: 0 }))
    ])

    serveHeightPoints.value = serveHeightData.points
    hitPoints.value = hitPointData.points
    radarDimensions.value = radarData.dimensions
    radarOverallScore.value = radarData.overall_score
    issueStats.value = issueStatsData.stats
  } catch (err) {
    console.error('Failed to load chart data:', err)
  } finally {
    chartsLoading.value = false
  }

  // Load coach report
  try {
    reportLoading.value = true
    coachReport.value = await getCoachReport(videoId).catch(() => null)
  } catch (err) {
    console.error('Failed to load coach report:', err)
    coachReport.value = null
  } finally {
    reportLoading.value = false
  }
})

// Handle time update from player
const handleTimeUpdate = (time: number) => {
  currentTime.value = time
}

// Handle duration change from player
const handleDurationChange = (dur: number) => {
  duration.value = dur
}

// Handle seek from timeline
const handleSeek = (time: number) => {
  if (playerRef.value) {
    playerRef.value.seek(time)
  }
}

// Handle frame selection from issue list
const handleFrameSelect = (frameNumber: number, time: number) => {
  if (playerRef.value) {
    playerRef.value.seek(time)
  }
}

// Format time as mm:ss
const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// Reload page
const reloadPage = () => {
  window.location.reload()
}

// Comparison state
const selectedProVideo = ref<ProVideo | null>(null)
const timeOffset = ref<number | undefined>(undefined)
const userCurrentTime = ref(0)
const proCurrentTime = ref(0)

// Analysis type mapping (default to forehand if unknown)
const analysisType = computed<ProVideoType>(() => {
  // Try to infer from video ID or default to forehand
  // In a real app, this would come from the analysis metadata
  const lowerId = videoId.toLowerCase()
  if (lowerId.includes('backhand')) return 'backhand'
  if (lowerId.includes('serve')) return 'serve'
  if (lowerId.includes('volley')) return 'volley'
  return 'forehand'
})

// Handle pro video selection
const onProVideoSelect = (video: ProVideo) => {
  selectedProVideo.value = video
  timeOffset.value = undefined
}

// Handle time updates from comparison player
const handleUserTimeUpdate = (time: number) => {
  userCurrentTime.value = time
}

const handleProTimeUpdate = (time: number) => {
  proCurrentTime.value = time
}

// Handle offset application
const onApplyOffset = (offset: number) => {
  timeOffset.value = offset
}
</script>

<template>
  <div class="p-6 max-w-7xl mx-auto">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-xl font-bold text-zinc-900">技术分析报告</h1>
        <p class="text-sm text-zinc-500 mt-1">视频ID: {{ videoId }}</p>
      </div>
      <router-link to="/" class="px-4 py-2 text-sm text-zinc-500 hover:text-zinc-700 border border-zinc-200 rounded-lg hover:bg-zinc-50 transition-colors">← 返回</router-link>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="flex items-center justify-center py-20">
      <svg class="animate-spin h-8 w-8 text-tennis" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 border border-red-100 rounded-xl p-8 text-center">
      <p class="text-red-600">{{ error }}</p>
      <button @click="reloadPage" class="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm">重试</button>
    </div>

    <!-- Main -->
    <div v-else>
      <!-- Report Section -->
      <div v-if="coachReport" class="space-y-5 mb-6">
        <!-- Score Card -->
        <ScoreCard
          :overall-score="coachReport.overall_score"
          :radar-scores="coachReport.radar_scores"
        />

        <!-- Strengths -->
        <StrengthsList :strengths="coachReport.strengths" />

        <!-- Issue Analysis -->
        <IssueAnalysis
          :issues="coachReport.issues"
          :improvement-suggestions="coachReport.improvement_suggestions"
        />

        <!-- Issue Summary Table -->
        <div v-if="coachReport.issue_summary.length > 0" class="rounded-xl bg-white p-5 shadow-sm border border-zinc-200">
          <h3 class="text-sm font-semibold text-zinc-900 mb-3">问题汇总表</h3>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-zinc-200">
                  <th class="text-left py-2 px-3 text-zinc-500 text-xs uppercase">帧</th>
                  <th class="text-left py-2 px-3 text-zinc-500 text-xs uppercase">类型</th>
                  <th class="text-left py-2 px-3 text-zinc-500 text-xs uppercase">部位</th>
                  <th class="text-left py-2 px-3 text-zinc-500 text-xs uppercase">描述</th>
                  <th class="text-left py-2 px-3 text-zinc-500 text-xs uppercase">优先级</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, i) in coachReport.issue_summary.slice(0, 20)" :key="i" class="border-b border-zinc-100">
                  <td class="py-2 px-3 text-zinc-900">{{ row.frame_number }}</td>
                  <td class="py-2 px-3 text-zinc-900">{{ row.issue_type }}</td>
                  <td class="py-2 px-3 text-zinc-500">{{ row.body_part }}</td>
                  <td class="py-2 px-3 text-zinc-500">{{ row.description }}</td>
                  <td class="py-2 px-3">
                    <span class="text-xs px-2 py-0.5 rounded font-medium" :class="{ 'bg-red-100 text-red-600': row.priority === 'high', 'bg-orange-100 text-orange-600': row.priority === 'medium', 'bg-yellow-100 text-yellow-600': row.priority === 'low' }">
                      {{ row.priority === 'high' ? '高' : row.priority === 'medium' ? '中' : '低' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Training Plan -->
        <TrainingPlan :training-plan="coachReport.training_plan" />

        <!-- Coach Summary -->
        <CoachSummary :summary="coachReport.coach_summary" />
      </div>

      <!-- Divider -->
      <div v-if="coachReport" class="border-t border-zinc-200 my-6" />

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <!-- Video -->
        <div class="lg:col-span-2 space-y-4">
          <div class="bg-white rounded-xl shadow-sm border border-zinc-200 overflow-hidden">
            <div class="p-3">
              <AnnotatedVideoPlayer
                ref="playerRef"
                :video-url="videoUrl"
                :video-id="videoId"
                :annotations="annotations"
                @timeupdate="handleTimeUpdate"
                @durationchange="handleDurationChange"
              />
            </div>
          </div>

          <!-- Timeline -->
          <div class="bg-white rounded-xl shadow-sm border border-zinc-200 p-4">
            <h3 class="text-sm font-semibold text-zinc-900 mb-3">时间轴</h3>
            <FrameTimeline
              :duration="duration"
              :current-time="currentTime"
              :issue-frames="issueFrames"
              @seek="handleSeek"
            />
          </div>

          <!-- Stats -->
          <div class="bg-white rounded-xl shadow-sm border border-zinc-200 p-4">
            <h3 class="text-sm font-semibold text-zinc-900 mb-3">分析统计</h3>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div class="text-center p-2.5 bg-zinc-50 rounded-lg">
                <div class="text-xl font-bold text-blue-600">{{ annotations.length }}</div>
                <div class="text-xs text-zinc-500">标注帧</div>
              </div>
              <div class="text-center p-2.5 bg-zinc-50 rounded-lg">
                <div class="text-xl font-bold text-red-600">{{ issueFrames.filter(f => f.issue_types.some(t => !t.startsWith('GOOD'))).length }}</div>
                <div class="text-xs text-zinc-500">问题帧</div>
              </div>
              <div class="text-center p-2.5 bg-zinc-50 rounded-lg">
                <div class="text-xl font-bold text-emerald-600">{{ issueFrames.filter(f => f.issue_types.some(t => t.startsWith('GOOD'))).length }}</div>
                <div class="text-xs text-zinc-500">正确动作</div>
              </div>
              <div class="text-center p-2.5 bg-zinc-50 rounded-lg">
                <div class="text-xl font-bold text-zinc-600">{{ duration > 0 ? formatTime(duration) : '--:--' }}</div>
                <div class="text-xs text-zinc-500">视频时长</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Issue frame list -->
        <div class="lg:col-span-1">
          <div class="bg-white rounded-xl shadow-sm border border-zinc-200 p-4 sticky top-4">
            <IssueFrameList
              :issue-frames="issueFrames"
              :video-id="videoId"
              @select="handleFrameSelect"
            />
          </div>
        </div>
      </div>

      <!-- Charts -->
      <div class="mt-6">
        <h2 class="text-base font-semibold text-zinc-900 mb-4">数据分析</h2>
        <div v-if="chartsLoading" class="flex justify-center py-8">
          <svg class="animate-spin h-6 w-6 text-tennis" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <!-- Serve Height Chart -->
          <ServeHeightChart
            v-if="serveHeightPoints.length > 0"
            :points="serveHeightPoints"
          />

          <!-- Hit Point Heatmap -->
          <HitPointHeatmap
            v-if="hitPoints.length > 0"
            :points="hitPoints"
          />

          <!-- Consistency Radar -->
          <ConsistencyRadar
            v-if="radarDimensions.length > 0"
            :dimensions="radarDimensions"
            :overall-score="radarOverallScore"
          />

          <!-- Issue Statistics -->
          <IssueStatsChart
            v-if="issueStats.length > 0"
            :stats="issueStats"
          />
        </div>
      </div>

      <!-- Comparison -->
      <div class="mt-6 border-t border-zinc-200 pt-6">
        <h2 class="text-base font-semibold text-zinc-900 mb-4">职业选手对比</h2>

        <!-- Pro video selector (shown when no video selected) -->
        <ProVideoSelector
          v-if="!selectedProVideo"
          :analysis-type="analysisType"
          @select="onProVideoSelect"
        />

        <!-- Comparison player (shown when video selected) -->
        <div v-else class="space-y-4">
          <ComparisonPlayer
            :user-video-url="videoUrl"
            :user-annotations="annotations"
            :pro-video="selectedProVideo"
            :time-offset="timeOffset"
            @user-time-update="handleUserTimeUpdate"
            @pro-time-update="handleProTimeUpdate"
          />

          <KeyframeMarker
            :user-current-time="userCurrentTime"
            :pro-current-time="proCurrentTime"
            @apply-offset="onApplyOffset"
          />

          <button @click="selectedProVideo = null" class="text-sm text-zinc-400 hover:text-zinc-600 transition-colors">← 更换对比视频</button>
        </div>
      </div>
    </div>
  </div>
</template>