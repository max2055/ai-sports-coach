<script setup lang="ts">
import { RouterLink, useRoute } from 'vue-router'

const route = useRoute()

const navItems = [
  { name: '首页', path: '/', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
  { name: '上传分析', path: '/upload', icon: 'M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12' },
  { name: '历史', path: '/history', icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' },
]

function isActive(path: string): boolean {
  return route.path === path || (path !== '/' && route.path.startsWith(path))
}
</script>

<template>
  <div class="flex min-h-screen bg-zinc-50">
    <!-- Sidebar -->
    <aside class="w-56 bg-tennis-dark text-white flex flex-col flex-shrink-0">
      <!-- Logo -->
      <div class="px-5 py-5 border-b border-white/10">
        <div class="flex items-center gap-2">
          <span class="text-xl">🎾</span>
          <div>
            <h1 class="text-sm font-bold leading-tight">AI 网球教练</h1>
            <p class="text-[10px] text-white/50">Tennis Coach</p>
          </div>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 px-3 py-4 space-y-1">
        <RouterLink
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all"
          :class="isActive(item.path)
            ? 'bg-white/15 text-white'
            : 'text-white/60 hover:bg-white/10 hover:text-white'"
        >
          <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" :d="item.icon" />
          </svg>
          <span class="whitespace-nowrap">{{ item.name }}</span>
        </RouterLink>
      </nav>

      <!-- Footer -->
      <div class="px-5 py-4 border-t border-white/10">
        <p class="text-[10px] text-white/40">v1.0</p>
      </div>
    </aside>

    <!-- Main content -->
    <main class="flex-1 overflow-auto min-w-0">
      <slot />
    </main>
  </div>
</template>
