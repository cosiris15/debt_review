<script setup lang="ts">
/**
 * Main Application Layout
 *
 * Provides consistent header, sidebar, and content area.
 */
import { ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

const route = useRoute()
const isSidebarOpen = ref(true)

const navItems = [
  { path: '/', label: '首页', icon: 'home' },
  { path: '/projects', label: '项目管理', icon: 'folder' },
  { path: '/calculator', label: '利息计算器', icon: 'calculator' },
]

function isActive(path: string): boolean {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex">
    <!-- Sidebar -->
    <aside
      :class="[
        'fixed inset-y-0 left-0 z-30 bg-white shadow-lg transition-all duration-300',
        isSidebarOpen ? 'w-64' : 'w-16'
      ]"
    >
      <!-- Logo -->
      <div class="h-16 flex items-center justify-center border-b">
        <h1
          v-if="isSidebarOpen"
          class="text-xl font-bold text-primary-600"
        >
          债权审查系统
        </h1>
        <span v-else class="text-2xl">📋</span>
      </div>

      <!-- Navigation -->
      <nav class="p-4">
        <RouterLink
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          :class="[
            'flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition-colors',
            isActive(item.path)
              ? 'bg-primary-50 text-primary-700'
              : 'text-gray-600 hover:bg-gray-100'
          ]"
        >
          <!-- Icons (simplified) -->
          <span class="text-xl">
            {{ item.icon === 'home' ? '🏠' : item.icon === 'folder' ? '📁' : '🧮' }}
          </span>
          <span v-if="isSidebarOpen">{{ item.label }}</span>
        </RouterLink>
      </nav>

      <!-- Toggle button -->
      <button
        @click="isSidebarOpen = !isSidebarOpen"
        class="absolute bottom-4 right-4 p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
      >
        <svg
          class="w-5 h-5 text-gray-600 transition-transform"
          :class="{ 'rotate-180': !isSidebarOpen }"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
        </svg>
      </button>
    </aside>

    <!-- Main content -->
    <main
      :class="[
        'flex-1 transition-all duration-300',
        isSidebarOpen ? 'ml-64' : 'ml-16'
      ]"
    >
      <!-- Header -->
      <header class="h-16 bg-white shadow-sm flex items-center px-6 sticky top-0 z-20">
        <div class="flex-1">
          <slot name="header">
            <h2 class="text-lg font-semibold text-gray-800">
              {{ route.meta.title || '债权审查系统' }}
            </h2>
          </slot>
        </div>
        <div class="flex items-center gap-4">
          <slot name="header-actions" />
        </div>
      </header>

      <!-- Content -->
      <div class="p-6">
        <slot />
      </div>
    </main>
  </div>
</template>
