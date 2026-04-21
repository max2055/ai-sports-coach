<script setup lang="ts">
import { ref, computed } from 'vue'
import type { UploadStatus, VideoInfo, AnalysisType } from '../types/upload'
import { useUpload } from '../composables/useUpload'

const props = defineProps<{
  analysisType: AnalysisType
}>()

const emit = defineEmits<{
  (e: 'uploadSuccess', result: { videoId: string; metadata: VideoInfo }): void
  (e: 'uploadError', error: string): void
}>()

const dragOver = ref(false)
const uploadStatus = ref<UploadStatus>('idle')
const selectedFile = ref<File | null>(null)
const videoInfo = ref<Partial<VideoInfo>>({})

const { uploading, progress, error, result, upload, reset: resetUpload } = useUpload()

const ACCEPTED_TYPES = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska', 'video/webm']
const ACCEPTED_EXTENSIONS = ['.mp4', '.mov', '.avi', '.mkv', '.webm']

const isUploading = computed(() => uploading.value)
const hasError = computed(() => uploadStatus.value === 'error' || !!error.value)
const errorMessage = computed(() => error.value || '')
const isSuccess = computed(() => uploadStatus.value === 'success')

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

function isValidVideoFile(file: File): boolean {
  const extension = '.' + file.name.split('.').pop()?.toLowerCase()
  return ACCEPTED_TYPES.includes(file.type) || ACCEPTED_EXTENSIONS.includes(extension)
}

function extractVideoMetadata(file: File): Promise<Partial<VideoInfo>> {
  return new Promise((resolve) => {
    const video = document.createElement('video')
    video.preload = 'metadata'
    video.onloadedmetadata = () => {
      resolve({
        duration: video.duration,
        width: video.videoWidth,
        height: video.videoHeight,
      })
      URL.revokeObjectURL(video.src)
    }
    video.onerror = () => {
      resolve({})
      URL.revokeObjectURL(video.src)
    }
    video.src = URL.createObjectURL(file)
  })
}

async function handleFile(file: File) {
  if (!isValidVideoFile(file)) {
    uploadStatus.value = 'error'
    emit('uploadError', '请选择有效的视频文件 (mp4, mov, avi, mkv, webm)')
    return
  }

  selectedFile.value = file
  uploadStatus.value = 'uploading'
  resetUpload()

  try {
    const metadata = await extractVideoMetadata(file)
    videoInfo.value = metadata

    // Upload to backend API
    const uploadResult = await upload(file, props.analysisType)

    if (uploadResult) {
      uploadStatus.value = 'success'
      const fullVideoInfo: VideoInfo = {
        file,
        name: file.name,
        size: file.size,
        duration: metadata.duration,
        width: metadata.width,
        height: metadata.height,
      }
      emit('uploadSuccess', {
        videoId: uploadResult.video_id,
        metadata: fullVideoInfo
      })
    } else {
      uploadStatus.value = 'error'
      emit('uploadError', error.value || '上传失败')
    }
  } catch (err) {
    uploadStatus.value = 'error'
    emit('uploadError', err instanceof Error ? err.message : '处理视频文件时出错')
  }
}

function handleDrop(e: DragEvent) {
  e.preventDefault()
  dragOver.value = false
  const files = e.dataTransfer?.files
  if (files && files.length > 0 && files[0]) {
    handleFile(files[0])
  }
}

function handleDragOver(e: DragEvent) {
  e.preventDefault()
  dragOver.value = true
}

function handleDragLeave(e: DragEvent) {
  e.preventDefault()
  dragOver.value = false
}

function handleFileInput(e: Event) {
  const input = e.target as HTMLInputElement
  const files = input.files
  if (files && files.length > 0 && files[0]) {
    handleFile(files[0])
  }
}

function triggerFileInput() {
  const input = document.getElementById('video-input') as HTMLInputElement
  input?.click()
}
</script>

<template>
  <div
    class="relative w-full"
    @drop="handleDrop"
    @dragover="handleDragOver"
    @dragleave="handleDragLeave"
  >
    <!-- Upload Area -->
    <div
      class="border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 cursor-pointer"
      :class="[
        dragOver
          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
          : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500',
        hasError ? 'border-red-500 bg-red-50 dark:bg-red-900/20' : '',
        isSuccess ? 'border-green-500 bg-green-50 dark:bg-green-900/20' : '',
      ]"
      @click="triggerFileInput"
    >
      <input
        id="video-input"
        type="file"
        accept=".mp4,.mov,.avi,.mkv,.webm,video/*"
        class="hidden"
        @change="handleFileInput"
      />

      <!-- Icon -->
      <div class="mb-4">
        <svg
          v-if="isSuccess"
          class="mx-auto h-12 w-12 text-green-500"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M5 13l4 4L19 7"
          />
        </svg>
        <svg
          v-else-if="hasError"
          class="mx-auto h-12 w-12 text-red-500"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <svg
          v-else
          class="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>
      </div>

      <!-- Text -->
      <p class="text-lg font-medium text-gray-700 dark:text-gray-300">
        <span v-if="isUploading">正在上传...</span>
        <span v-else-if="isSuccess">上传成功</span>
        <span v-else-if="hasError">上传失败</span>
        <span v-else>拖拽视频文件到此处，或点击选择</span>
      </p>
      <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
        支持格式: MP4, MOV, AVI, MKV, WebM
      </p>

      <!-- Error Message -->
      <p v-if="hasError && errorMessage" class="mt-2 text-sm text-red-500">
        {{ errorMessage }}
      </p>
    </div>

    <!-- Progress Bar -->
    <div v-if="isUploading" class="mt-4">
      <div class="flex items-center justify-between mb-1">
        <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
          上传进度
        </span>
        <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
          {{ Math.round(progress) }}%
        </span>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
        <div
          class="bg-blue-600 h-2.5 rounded-full transition-all duration-200"
          :style="{ width: progress + '%' }"
        ></div>
      </div>
    </div>
  </div>
</template>
