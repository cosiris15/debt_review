<script setup lang="ts">
/**
 * Main Application Layout
 *
 * 简化的侧边栏布局：
 * - 产品名称：债权审查方案
 * - 主入口：破产案件（将来可扩展"不良案件"等）
 * - 底部设置菜单
 */
import { ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import UserButton from '@/components/UserButton.vue'
import { Building2, Settings, Calculator, ChevronDown } from 'lucide-vue-next'

const route = useRoute()
const isSidebarOpen = ref(true)
const showSettingsDropdown = ref(false)

// 主产品线入口（将来可扩展更多子产品）
const productItems = [
  { path: '/bankruptcy', label: '破产案件', icon: 'building', description: '破产项目债权审查' },
  // 将来可添加：{ path: '/npl', label: '不良案件', icon: 'alert', description: '不良资产债权审查' },
]

// 设置/工具菜单项
const settingsItems = [
  { path: '/calculator', label: '利息计算器', icon: 'calculator', description: '独立计算利息工具' },
]

function isActive(path: string): boolean {
  if (path === '/bankruptcy') {
    // /bankruptcy 及其子路由 (/bankruptcy/xxx) 和项目路由 (/projects/xxx) 都算激活
    return route.path === '/bankruptcy' || route.path.startsWith('/projects')
  }
  return route.path.startsWith(path)
}

function isSettingsActive(): boolean {
  return settingsItems.some(item => route.path.startsWith(item.path))
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
          债权审查方案
        </h1>
        <span v-else class="text-2xl">📋</span>
      </div>

      <!-- Navigation -->
      <nav class="p-4 flex flex-col h-[calc(100%-4rem)]">
        <!-- 产品线入口 -->
        <div class="flex-1">
          <RouterLink
            v-for="item in productItems"
            :key="item.path"
            :to="item.path"
            :class="[
              'flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition-colors',
              isActive(item.path)
                ? 'bg-primary-50 text-primary-700'
                : 'text-gray-600 hover:bg-gray-100'
            ]"
          >
            <Building2 class="w-5 h-5" />
            <span v-if="isSidebarOpen">{{ item.label }}</span>
          </RouterLink>
        </div>

        <!-- 设置菜单（底部） -->
        <div class="relative border-t pt-4 mt-4">
          <button
            @click="showSettingsDropdown = !showSettingsDropdown"
            :class="[
              'flex items-center gap-3 px-4 py-3 rounded-lg w-full transition-colors',
              isSettingsActive()
                ? 'bg-primary-50 text-primary-700'
                : 'text-gray-600 hover:bg-gray-100'
            ]"
          >
            <Settings class="w-5 h-5" />
            <span v-if="isSidebarOpen">设置</span>
            <ChevronDown
              v-if="isSidebarOpen"
              class="w-4 h-4 ml-auto transition-transform"
              :class="{ 'rotate-180': showSettingsDropdown }"
            />
          </button>

          <!-- 设置下拉菜单 -->
          <div
            v-if="showSettingsDropdown && isSidebarOpen"
            class="mt-1 bg-white rounded-lg border shadow-lg overflow-hidden"
          >
            <RouterLink
              v-for="item in settingsItems"
              :key="item.path"
              :to="item.path"
              @click="showSettingsDropdown = false"
              :class="[
                'block px-4 py-3 hover:bg-gray-50 transition-colors',
                isActive(item.path) ? 'bg-primary-50' : ''
              ]"
            >
              <div class="flex items-center gap-2">
                <Calculator class="w-4 h-4 text-gray-500" />
                <span class="font-medium text-gray-800">{{ item.label }}</span>
              </div>
              <div class="text-xs text-gray-500 mt-1 ml-6">{{ item.description }}</div>
            </RouterLink>
          </div>
        </div>
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
          <UserButton />
        </div>
      </header>

      <!-- Content -->
      <div class="p-6">
        <slot />
      </div>
    </main>
  </div>
</template>
