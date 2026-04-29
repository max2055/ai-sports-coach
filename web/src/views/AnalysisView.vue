<script setup lang="ts">
import { onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAnalysis } from '@/composables/useAnalysis'

const router = useRouter()
const route = useRoute()
const videoId = route.params.videoId as string
const { status, progress, error, isLoading, statusText, start, retry } = useAnalysis(videoId)

const isCompleted = computed(() => status.value === 'completed')
const isFailed = computed(() => status.value === 'failed')
const isProcessing = computed(() => !isCompleted.value && !isFailed.value)

watch(isCompleted, () => { setTimeout(() => router.push(`/report/${videoId}`), 1000) })
onMounted(() => start())
function handleRetry() { retry() }
function goBack() { router.push('/') }
</script>

<template>
  <div class="p-6 max-w-xl mx-auto">
    <div class="mb-6">
      <h1 class="text-xl font-bold text-zinc-900">视频分析</h1>
      <p class="text-sm text-zinc-500 mt-1">AI 正在分析您的网球动作</p>
    </div>

    <div class="bg-white rounded-xl shadow-sm border border-zinc-200">
      <div class="p-8">
        <!-- Processing -->
        <div v-if="isProcessing" class="text-center">
          <div class="inline-flex items-center justify-center w-14 h-14 rounded-full bg-tennis/10 mb-5">
            <svg class="w-7 h-7 text-tennis animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          </div>
          <h2 class="text-base font-semibold text-zinc-900 mb-1">{{ statusText }}</h2>
          <p class="text-xs text-zinc-400 mb-5">{{ videoId }}</p>
          <div class="w-full bg-zinc-100 rounded-full h-2 mb-3">
            <div class="bg-tennis h-2 rounded-full transition-all duration-300" :style="{ width: `${progress}%` }" />
          </div>
          <p class="text-xs text-zinc-400">{{ progress }}%</p>
        </div>

        <!-- Completed -->
        <div v-else-if="isCompleted" class="text-center">
          <div class="inline-flex items-center justify-center w-14 h-14 rounded-full bg-emerald-50 mb-5">
            <svg class="w-7 h-7 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" /></svg>
          </div>
          <h2 class="text-base font-semibold text-zinc-900 mb-1">分析完成！</h2>
          <p class="text-xs text-zinc-400">正在跳转到报告页面...</p>
        </div>

        <!-- Failed -->
        <div v-else class="text-center">
          <div class="inline-flex items-center justify-center w-14 h-14 rounded-full bg-red-50 mb-5">
            <svg class="w-7 h-7 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" /></svg>
          </div>
          <h2 class="text-base font-semibold text-red-600 mb-1">分析失败</h2>
          <p class="text-xs text-zinc-400 mb-5">{{ error || '分析过程中发生错误' }}</p>
          <div class="flex gap-3 justify-center">
            <button class="px-5 py-2 bg-tennis hover:bg-tennis-light text-white text-sm font-semibold rounded-lg disabled:opacity-50" :disabled="isLoading" @click="handleRetry">重新分析</button>
            <button class="px-5 py-2 bg-zinc-100 hover:bg-zinc-200 text-zinc-700 text-sm font-semibold rounded-lg" @click="goBack">返回</button>
          </div>
        </div>
      </div>
      <div class="px-8 py-3 bg-zinc-50 border-t border-zinc-100 text-center">
        <p class="text-xs text-zinc-400">通常需要 1–3 分钟</p>
      </div>
    </div>
  </div>
</template>
