<script setup lang="ts">
import { ref } from 'vue'
import type { AnalysisType, AnalysisTypeOption } from '../types/upload'

const props = defineProps<{
  modelValue: AnalysisType
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: AnalysisType): void
}>()

const analysisTypes: AnalysisTypeOption[] = [
  {
    value: 'forehand',
    label: '正手击球',
    icon: '🎾',
    description: '分析正手击球动作、击球点和随挥',
  },
  {
    value: 'backhand',
    label: '反手击球',
    icon: '🎯',
    description: '分析反手击球动作，包括单反和双反',
  },
  {
    value: 'serve',
    label: '发球',
    icon: '🚀',
    description: '分析发球动作、抛球高度和击球时机',
  },
  {
    value: 'volley',
    label: '截击',
    icon: '⚡',
    description: '分析网前截击动作和反应速度',
  },
  {
    value: 'full',
    label: '全场综合',
    icon: '🏆',
    description: '全面分析所有技术动作',
  },
]

const selectedType = ref<AnalysisType>(props.modelValue || 'full')

function selectType(type: AnalysisType) {
  selectedType.value = type
  emit('update:modelValue', type)
}
</script>

<template>
  <div class="space-y-4">
    <h3 class="text-lg font-medium text-gray-900 dark:text-white">
      选择分析类型
    </h3>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <button
        v-for="type in analysisTypes"
        :key="type.value"
        class="relative p-4 rounded-xl border-2 text-left transition-all duration-200 hover:shadow-md"
        :class="[
          selectedType === type.value
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30'
            : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600',
        ]"
        @click="selectType(type.value)"
      >
        <!-- Selection Indicator -->
        <div
          v-if="selectedType === type.value"
          class="absolute top-3 right-3 w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center"
        >
          <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path
              fill-rule="evenodd"
              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
              clip-rule="evenodd"
            />
          </svg>
        </div>

        <!-- Icon -->
        <div class="text-3xl mb-2">{{ type.icon }}</div>

        <!-- Label -->
        <h4
          class="font-semibold text-gray-900 dark:text-white"
          :class="selectedType === type.value ? 'text-blue-700 dark:text-blue-400' : ''"
        >
          {{ type.label }}
        </h4>

        <!-- Description -->
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          {{ type.description }}
        </p>
      </button>
    </div>

    <!-- Selected Type Summary -->
    <div class="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
      <p class="text-sm text-gray-600 dark:text-gray-400">
        <span class="font-medium">已选择：</span>
        {{ analysisTypes.find(t => t.value === selectedType)?.label }}
      </p>
    </div>
  </div>
</template>
