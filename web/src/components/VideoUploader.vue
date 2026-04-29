<script setup lang="ts">
import { ref, computed } from 'vue'
import type { UploadStatus, VideoInfo, AnalysisType } from '../types/upload'
import { useUpload } from '../composables/useUpload'

const props = defineProps<{ analysisType: AnalysisType }>()
const emit = defineEmits<{
  (e: 'uploadSuccess', result: { videoId: string; metadata: VideoInfo }): void
  (e: 'uploadError', error: string): void
}>()

const dragOver = ref(false)
const uploadStatus = ref<UploadStatus>('idle')
const { uploading, progress, error, upload, reset: resetUpload } = useUpload()

const ACCEPTED = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska', 'video/webm']
const isUploading = computed(() => uploading.value)
const hasError = computed(() => uploadStatus.value === 'error' || !!error.value)
const isSuccess = computed(() => uploadStatus.value === 'success')

function isValidVideo(file: File): boolean {
  const ext = '.' + file.name.split('.').pop()?.toLowerCase()
  return ACCEPTED.includes(file.type) || ['.mp4', '.mov', '.avi', '.mkv', '.webm'].includes(ext)
}

async function handleFile(file: File) {
  if (!isValidVideo(file)) {
    uploadStatus.value = 'error'
    emit('uploadError', '请选择有效的视频文件 (mp4, mov, avi, mkv, webm)')
    return
  }
  uploadStatus.value = 'idle'
  resetUpload()
  uploadStatus.value = 'uploading'
  try {
    const result = await upload(file, props.analysisType)
    if (result) {
      uploadStatus.value = 'success'
      emit('uploadSuccess', { videoId: result.video_id, metadata: { file, name: file.name, size: file.size } })
    } else {
      uploadStatus.value = 'error'
      emit('uploadError', error.value || '上传失败')
    }
  } catch {
    uploadStatus.value = 'error'
    emit('uploadError', '处理文件时出错')
  }
}

function handleDrop(e: DragEvent) {
  e.preventDefault()
  dragOver.value = false
  const files = e.dataTransfer?.files
  if (files?.length) handleFile(files[0])
}

function handleDragOver(e: DragEvent) { e.preventDefault(); dragOver.value = true }
function handleDragLeave(e: DragEvent) { e.preventDefault(); dragOver.value = false }

function handleFileInput(e: Event) {
  const files = (e.target as HTMLInputElement).files
  if (files?.length) handleFile(files[0])
}

function triggerFileInput() {
  (document.getElementById('video-input') as HTMLInputElement)?.click()
}
</script>

<template>
  <div class="relative w-full" @drop="handleDrop" @dragover="handleDragOver" @dragleave="handleDragLeave">
    <div
      class="border-2 border-dashed rounded-lg p-6 text-center transition-all cursor-pointer"
      :class="[
        dragOver ? 'border-tennis bg-tennis/5' : 'border-zinc-200 hover:border-zinc-300',
        hasError ? 'border-red-300 bg-red-50/50' : '',
        isSuccess ? 'border-emerald-300 bg-emerald-50/50' : '',
      ]"
      @click="triggerFileInput"
    >
      <input id="video-input" type="file" accept=".mp4,.mov,.avi,.mkv,.webm,video/*" class="hidden" @change="handleFileInput" />

      <!-- Icon -->
      <div class="mb-3">
        <svg v-if="isSuccess" class="mx-auto h-8 w-8 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" /></svg>
        <svg v-else-if="hasError" class="mx-auto h-8 w-8 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" /></svg>
        <svg v-else class="mx-auto h-8 w-8 text-zinc-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" /></svg>
      </div>

      <!-- Text -->
      <p class="text-sm font-medium text-zinc-700">
        <span v-if="isUploading">上传中...</span>
        <span v-else-if="isSuccess">上传成功</span>
        <span v-else-if="hasError">上传失败</span>
        <span v-else>拖拽视频到此处，或<span class="text-tennis underline">选择文件</span></span>
      </p>
      <p class="mt-1 text-xs text-zinc-400">支持 MP4, MOV, AVI, MKV, WebM</p>
      <p v-if="hasError && error" class="mt-2 text-xs text-red-500">{{ error }}</p>
    </div>

    <!-- Progress -->
    <div v-if="isUploading" class="mt-3">
      <div class="flex items-center justify-between mb-1">
        <span class="text-xs font-medium text-zinc-600">上传进度</span>
        <span class="text-xs font-medium text-zinc-500">{{ Math.round(progress) }}%</span>
      </div>
      <div class="w-full bg-zinc-100 rounded-full h-1.5">
        <div class="bg-tennis h-1.5 rounded-full transition-all duration-200" :style="{ width: progress + '%' }" />
      </div>
    </div>
  </div>
</template>
