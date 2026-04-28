<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import type { FrameAnnotation, PlayerAnnotation, BodyPartAnnotation, IssueType } from '../api/frames'

const props = defineProps<{
  videoUrl: string
  videoId: string
  annotations: FrameAnnotation[]
  fps?: number
}>()

const emit = defineEmits<{
  (e: 'timeupdate', time: number): void
  (e: 'framechange', frameNumber: number): void
  (e: 'durationchange', duration: number): void
}>()

// Refs
const videoRef = ref<HTMLVideoElement | null>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)
const containerRef = ref<HTMLDivElement | null>(null)

// State
const showAnnotations = ref(true)
const currentTime = ref(0)
const duration = ref(0)
const currentFrame = ref(0)
const isPlaying = ref(false)
const videoFps = ref(30)

// Colors matching tennis_annotate.py
const COLORS = {
  body: '#1E90FF',      // Dodger Blue
  hand_l: '#32C850',    // Green (racket hand)
  hand_r: '#148A32',    // Dark Green (off hand)
  foot_l: '#FF8C00',    // Orange (front foot)
  foot_r: '#DC6400',    // Dark Orange (back foot)
  issue_ring: '#FF3232', // Red (issue highlight)
  good_ring: '#32DC50', // Green (correct marker)
}

/**
 * Get current frame number from video time
 */
const getFrameNumber = (time: number): number => {
  return Math.floor(time * videoFps.value)
}

/**
 * Find annotation for current frame
 */
const findFrameAnnotation = (frameNumber: number): FrameAnnotation | undefined => {
  return props.annotations.find(a => a.frame_number === frameNumber)
}

/**
 * Draw a body part circle on canvas
 */
const drawBodyPart = (
  ctx: CanvasRenderingContext2D,
  part: BodyPartAnnotation,
  color: string,
  canvasWidth: number,
  canvasHeight: number,
  label?: string
) => {
  const x = part.x_pct * canvasWidth
  const y = part.y_pct * canvasHeight
  const radius = part.radius_pct * canvasWidth

  // Draw main circle
  ctx.beginPath()
  ctx.arc(x, y, radius, 0, Math.PI * 2)
  ctx.fillStyle = color
  ctx.fill()

  // Draw issue ring if there's an issue
  if (part.issue_type) {
    ctx.beginPath()
    ctx.arc(x, y, radius + 4, 0, Math.PI * 2)
    ctx.strokeStyle = COLORS.issue_ring
    ctx.lineWidth = 3
    ctx.stroke()

    // Draw issue label
    if (part.issue_note || label) {
      ctx.font = 'bold 12px Arial'
      ctx.fillStyle = '#FF3232'
      ctx.textAlign = 'center'
      ctx.fillText(part.issue_note || label || '', x, y - radius - 10)
    }
  }
}

/**
 * Draw player annotation
 */
const drawPlayer = (
  ctx: CanvasRenderingContext2D,
  player: PlayerAnnotation,
  canvasWidth: number,
  canvasHeight: number
) => {
  // Draw body parts with their respective colors
  drawBodyPart(ctx, player.body, COLORS.body, canvasWidth, canvasHeight, 'Body')
  drawBodyPart(ctx, player.hand_l, COLORS.hand_l, canvasWidth, canvasHeight, 'Racket Hand')
  drawBodyPart(ctx, player.hand_r, COLORS.hand_r, canvasWidth, canvasHeight, 'Off Hand')
  drawBodyPart(ctx, player.foot_l, COLORS.foot_l, canvasWidth, canvasHeight, 'Front Foot')
  drawBodyPart(ctx, player.foot_r, COLORS.foot_r, canvasWidth, canvasHeight, 'Back Foot')

  // Draw player ID if available
  if (player.id) {
    ctx.font = 'bold 14px Arial'
    ctx.fillStyle = '#FFFFFF'
    ctx.textAlign = 'center'
    ctx.fillText(player.id, player.body.x_pct * canvasWidth, player.body.y_pct * canvasHeight - 30)
  }
}

/**
 * Draw all annotations for current frame
 */
const drawAnnotations = () => {
  const video = videoRef.value
  const canvas = canvasRef.value
  if (!video || !canvas) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height)

  if (!showAnnotations.value) return

  const frameAnnotation = findFrameAnnotation(currentFrame.value)
  if (!frameAnnotation) return

  // Draw all players
  for (const player of frameAnnotation.players) {
    drawPlayer(ctx, player, canvas.width, canvas.height)
  }

  // Draw frame summary if available
  if (frameAnnotation.frame_summary) {
    ctx.font = 'bold 14px Arial'
    ctx.fillStyle = '#FFFFFF'
    ctx.textAlign = 'left'
    ctx.fillText(frameAnnotation.frame_summary, 10, 20)
  }
}

/**
 * Resize canvas to match video dimensions
 */
const resizeCanvas = () => {
  const video = videoRef.value
  const canvas = canvasRef.value
  if (!video || !canvas) return

  canvas.width = video.videoWidth || video.clientWidth
  canvas.height = video.videoHeight || video.clientHeight

  drawAnnotations()
}

/**
 * Handle video time update
 */
const handleTimeUpdate = () => {
  const video = videoRef.value
  if (!video) return

  currentTime.value = video.currentTime
  const frameNum = getFrameNumber(video.currentTime)

  if (frameNum !== currentFrame.value) {
    currentFrame.value = frameNum
    emit('framechange', frameNum)
    drawAnnotations()
  }

  emit('timeupdate', video.currentTime)
}

/**
 * Handle video loaded metadata
 */
const handleLoadedMetadata = () => {
  const video = videoRef.value
  if (!video) return

  duration.value = video.duration
  videoFps.value = props.fps || 30
  emit('durationchange', video.duration)
  resizeCanvas()
}

/**
 * Toggle play/pause
 */
const togglePlay = () => {
  const video = videoRef.value
  if (!video) return

  if (video.paused) {
    video.play()
    isPlaying.value = true
  } else {
    video.pause()
    isPlaying.value = false
  }
}

/**
 * Seek to specific time
 */
const seek = (time: number) => {
  const video = videoRef.value
  if (!video) return

  video.currentTime = time
}

/**
 * Seek to specific frame
 */
const seekToFrame = (frameNumber: number) => {
  const time = frameNumber / videoFps.value
  seek(time)
}

// Expose methods for parent component
defineExpose({
  seek,
  seekToFrame,
  togglePlay,
  get currentTime() { return currentTime.value },
  get duration() { return duration.value },
  get currentFrame() { return currentFrame.value },
  get isPlaying() { return isPlaying.value }
})

// Event handlers
const handlePlay = () => { isPlaying.value = true }
const handlePause = () => { isPlaying.value = false }
const handleEnded = () => { isPlaying.value = false }

// Lifecycle
onMounted(() => {
  const video = videoRef.value
  if (video) {
    video.addEventListener('loadedmetadata', handleLoadedMetadata)
    video.addEventListener('timeupdate', handleTimeUpdate)
    video.addEventListener('play', handlePlay)
    video.addEventListener('pause', handlePause)
    video.addEventListener('ended', handleEnded)
    video.addEventListener('resize', resizeCanvas)
  }

  window.addEventListener('resize', resizeCanvas)
})

onUnmounted(() => {
  const video = videoRef.value
  if (video) {
    video.removeEventListener('loadedmetadata', handleLoadedMetadata)
    video.removeEventListener('timeupdate', handleTimeUpdate)
    video.removeEventListener('play', handlePlay)
    video.removeEventListener('pause', handlePause)
    video.removeEventListener('ended', handleEnded)
    video.removeEventListener('resize', resizeCanvas)
  }

  window.removeEventListener('resize', resizeCanvas)
})

// Watch for annotation changes
watch(() => props.annotations, () => {
  nextTick(() => drawAnnotations())
}, { deep: true })

// Watch for showAnnotations toggle
watch(showAnnotations, () => {
  drawAnnotations()
})
</script>

<template>
  <div ref="containerRef" class="annotated-video-player relative w-full">
    <!-- Video Container -->
    <div class="relative bg-black rounded-lg overflow-hidden">
      <video
        ref="videoRef"
        :src="videoUrl"
        class="w-full h-auto"
        preload="metadata"
        playsinline
      />

      <!-- Canvas Overlay -->
      <canvas
        ref="canvasRef"
        class="absolute top-0 left-0 w-full h-full pointer-events-none"
      />

      <!-- Play/Pause Overlay -->
      <div
        class="absolute inset-0 flex items-center justify-center cursor-pointer group"
        @click="togglePlay"
      >
        <div
          class="w-16 h-16 bg-black/50 rounded-full flex items-center justify-center transition-opacity"
          :class="{ 'opacity-0 group-hover:opacity-100': isPlaying }"
        >
          <svg
            v-if="!isPlaying"
            class="w-8 h-8 text-white ml-1"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path d="M8 5v14l11-7z" />
          </svg>
          <svg
            v-else
            class="w-8 h-8 text-white"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" />
          </svg>
        </div>
      </div>
    </div>

    <!-- Controls -->
    <div class="mt-3 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <!-- Toggle Annotations -->
        <button
          @click="showAnnotations = !showAnnotations"
          class="px-3 py-1.5 text-sm rounded-md transition-colors"
          :class="showAnnotations
            ? 'bg-blue-600 text-white hover:bg-blue-700'
            : 'bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'"
        >
          {{ showAnnotations ? '隐藏标注' : '显示标注' }}
        </button>

        <!-- Frame Info -->
        <span class="text-sm text-gray-600 dark:text-gray-400">
          帧: {{ currentFrame }} | 时间: {{ currentTime.toFixed(2) }}s
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.annotated-video-player video {
  max-height: 70vh;
}
</style>