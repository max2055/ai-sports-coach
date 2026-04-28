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
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
              技术分析报告
            </h1>
            <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
              视频ID: {{ videoId }}
            </p>
          </div>
          <router-link
            to="/"
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
          >
            返回首页
          </router-link>
        </div>
      </div>
    </div>

    <!-- Loading state -->
    <div
      v-if="isLoading"
      class="flex items-center justify-center py-20"
    >
      <div class="flex flex-col items-center">
        <svg
          class="animate-spin h-10 w-10 text-blue-600 mb-4"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            class="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="4"
          />
          <path
            class="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
        <p class="text-gray-600 dark:text-gray-400">加载中...</p>
      </div>
    </div>

    <!-- Error state -->
    <div
      v-else-if="error"
      class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
    >
      <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
        <svg
          class="w-12 h-12 text-red-500 mx-auto mb-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
        <h3 class="text-lg font-medium text-red-800 dark:text-red-200 mb-2">
          加载失败
        </h3>
        <p class="text-red-600 dark:text-red-400">{{ error }}</p>
        <button
          @click="reloadPage"
          class="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          重试
        </button>
      </div>
    </div>

    <!-- Main content -->
    <div
      v-else
      class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
    >
      <!-- Report Section (top) -->
      <div v-if="coachReport" class="report-section space-y-6 mb-8">
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
        <div
          v-if="coachReport.issue_summary.length > 0"
          class="issue-summary rounded-xl bg-white dark:bg-gray-800 p-6 shadow-lg"
        >
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            问题汇总表
          </h3>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-gray-200 dark:border-gray-700">
                  <th class="text-left py-2 px-3 text-gray-600 dark:text-gray-400">帧</th>
                  <th class="text-left py-2 px-3 text-gray-600 dark:text-gray-400">问题类型</th>
                  <th class="text-left py-2 px-3 text-gray-600 dark:text-gray-400">部位</th>
                  <th class="text-left py-2 px-3 text-gray-600 dark:text-gray-400">描述</th>
                  <th class="text-left py-2 px-3 text-gray-600 dark:text-gray-400">优先级</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(row, index) in coachReport.issue_summary.slice(0, 20)"
                  :key="index"
                  class="border-b border-gray-100 dark:border-gray-700"
                >
                  <td class="py-2 px-3 text-gray-900 dark:text-white">{{ row.frame_number }}</td>
                  <td class="py-2 px-3 text-gray-900 dark:text-white">{{ row.issue_type }}</td>
                  <td class="py-2 px-3 text-gray-600 dark:text-gray-400">{{ row.body_part }}</td>
                  <td class="py-2 px-3 text-gray-600 dark:text-gray-400">{{ row.description }}</td>
                  <td class="py-2 px-3">
                    <span
                      class="text-xs px-2 py-0.5 rounded"
                      :class="{
                        'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300': row.priority === 'high',
                        'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300': row.priority === 'medium',
                        'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300': row.priority === 'low',
                      }"
                    >
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

      <!-- Divider between report and video -->
      <div v-if="coachReport" class="border-t border-gray-200 dark:border-gray-700 my-8"></div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Video player section -->
        <div class="lg:col-span-2 space-y-4">
          <!-- Video player -->
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
            <div class="p-4">
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
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              时间轴
            </h3>
            <FrameTimeline
              :duration="duration"
              :current-time="currentTime"
              :issue-frames="issueFrames"
              @seek="handleSeek"
            />
          </div>

          <!-- Stats summary -->
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              分析统计
            </h3>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div class="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  {{ annotations.length }}
                </div>
                <div class="text-sm text-gray-600 dark:text-gray-400">标注帧</div>
              </div>
              <div class="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div class="text-2xl font-bold text-red-600 dark:text-red-400">
                  {{ issueFrames.filter(f => f.issue_types.some(t => !t.startsWith('GOOD'))).length }}
                </div>
                <div class="text-sm text-gray-600 dark:text-gray-400">问题帧</div>
              </div>
              <div class="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div class="text-2xl font-bold text-green-600 dark:text-green-400">
                  {{ issueFrames.filter(f => f.issue_types.some(t => t.startsWith('GOOD'))).length }}
                </div>
                <div class="text-sm text-gray-600 dark:text-gray-400">正确动作</div>
              </div>
              <div class="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div class="text-2xl font-bold text-gray-600 dark:text-gray-400">
                  {{ duration > 0 ? formatTime(duration) : '--:--' }}
                </div>
                <div class="text-sm text-gray-600 dark:text-gray-400">视频时长</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Issue frame list section -->
        <div class="lg:col-span-1">
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 sticky top-4">
            <IssueFrameList
              :issue-frames="issueFrames"
              :video-id="videoId"
              @select="handleFrameSelect"
            />
          </div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="charts-section mt-8">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          数据分析
        </h2>

        <div v-if="chartsLoading" class="flex justify-center py-8">
          <svg
            class="animate-spin h-8 w-8 text-blue-600"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              class="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="4"
            />
            <path
              class="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
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

      <!-- Comparison Section -->
      <div class="comparison-section mt-8 border-t border-gray-200 dark:border-gray-700 pt-6">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          职业选手对比
        </h2>

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

          <button
            @click="selectedProVideo = null"
            class="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
          >
            ← 更换对比视频
          </button>
        </div>
      </div>
    </div>
  </div>
</template>