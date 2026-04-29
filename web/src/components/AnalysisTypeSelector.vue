<script setup lang="ts">
import { ref } from 'vue'
import type { AnalysisType, AnalysisTypeOption } from '../types/upload'

defineProps<{ modelValue: AnalysisType }>()
const emit = defineEmits<{ (e: 'update:modelValue', value: AnalysisType): void }>()

const options: AnalysisTypeOption[] = [
  { value: 'forehand', label: '正手', icon: '🎾', description: '正手击球动作、击球点和随挥' },
  { value: 'backhand', label: '反手', icon: '🎯', description: '反手击球动作（单反/双反）' },
  { value: 'serve', label: '发球', icon: '🚀', description: '发球动作、抛球高度和击球时机' },
  { value: 'volley', label: '截击', icon: '⚡', description: '网前截击动作和反应速度' },
  { value: 'full', label: '全场', icon: '🏆', description: '全面分析所有技术动作' },
]

const selectedType = ref<AnalysisType>(props.modelValue || 'full')

function selectType(type: AnalysisType) {
  selectedType.value = type
  emit('update:modelValue', type)
}
</script>

<template>
  <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
    <button
      v-for="type in options"
      :key="type.value"
      class="relative px-3 py-2.5 rounded-lg border text-left transition-all"
      :class="selectedType === type.value
        ? 'border-tennis bg-tennis/5 text-tennis-dark'
        : 'border-zinc-200 hover:border-zinc-300 text-zinc-600'"
      @click="selectType(type.value)"
    >
      <div class="text-base mb-1">{{ type.icon }}</div>
      <div class="text-xs font-semibold">{{ type.label }}</div>
      <div class="text-[10px] text-zinc-400 mt-0.5 hidden sm:block">{{ type.description }}</div>
      <div v-if="selectedType === type.value" class="absolute -top-1 -right-1 w-4 h-4 bg-tennis rounded-full flex items-center justify-center">
        <svg class="w-2.5 h-2.5 text-white" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg>
      </div>
    </button>
  </div>
</template>
