<script setup lang="ts">
/**
 * Main Application Layout
 *
 * 简洁专业的侧边栏布局：
 * - 左上角：十行法务 Logo + 产品名称
 * - 主导航：破产案件（将来可扩展）
 * - 底部：工具菜单
 */
import { ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import UserButton from '@/components/UserButton.vue'
import { Building2, Settings, Calculator, ChevronDown, ChevronLeft, ChevronRight } from 'lucide-vue-next'
import LogoImg from '@/assets/Logo.png'

const route = useRoute()
const isSidebarOpen = ref(true)
const showSettingsDropdown = ref(false)

// 主产品线入口
const productItems = [
  { path: '/bankruptcy', label: '破产案件', description: '破产项目债权审查' },
]

// 工具菜单项
const toolItems = [
  { path: '/calculator', label: '利息计算器', description: '独立计算利息工具' },
]

function isActive(path: string): boolean {
  if (path === '/bankruptcy') {
    return route.path === '/bankruptcy' || route.path.startsWith('/projects')
  }
  return route.path.startsWith(path)
}

function isToolsActive(): boolean {
  return toolItems.some(item => route.path.startsWith(item.path))
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex">
    <!-- Sidebar -->
    <aside
      :class="[
        'fixed inset-y-0 left-0 z-30 bg-white border-r border-slate-200 transition-all duration-300 flex flex-col',
        isSidebarOpen ? 'w-60' : 'w-[72px]'
      ]"
    >
      <!-- Logo Area -->
      <div class="h-16 flex items-center px-4 border-b border-slate-100">
        <RouterLink to="/bankruptcy" class="flex items-center gap-3 min-w-0">
          <img
            :src="LogoImg"
            alt="十行法务"
            class="h-9 w-auto flex-shrink-0"
          />
          <div v-if="isSidebarOpen" class="min-w-0">
            <div class="text-sm font-semibold text-slate-800 truncate">债权审查方案</div>
            <div class="text-xs text-slate-400">Paralaw</div>
          </div>
        </RouterLink>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 p-3 overflow-y-auto">
        <!-- 产品入口 -->
        <div class="mb-2">
          <div v-if="isSidebarOpen" class="px-3 py-2 text-xs font-medium text-slate-400 uppercase tracking-wider">
            产品
          </div>
          <RouterLink
            v-for="item in productItems"
            :key="item.path"
            :to="item.path"
            :class="[
              'flex items-center gap-3 px-3 py-2.5 rounded-lg mb-1 transition-all group',
              isActive(item.path)
                ? 'bg-blue-50 text-blue-700 font-medium'
                : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
            ]"
          >
            <div :class="[
              'w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 transition-colors',
              isActive(item.path)
                ? 'bg-blue-100'
                : 'bg-slate-100 group-hover:bg-slate-200'
            ]">
              <Building2 :class="['w-5 h-5', isActive(item.path) ? 'text-blue-600' : 'text-slate-500']" />
            </div>
            <div v-if="isSidebarOpen" class="min-w-0">
              <div class="truncate">{{ item.label }}</div>
              <div class="text-xs text-slate-400 truncate">{{ item.description }}</div>
            </div>
          </RouterLink>
        </div>
      </nav>

      <!-- Tools Section -->
      <div class="p-3 border-t border-slate-100">
        <button
          @click="showSettingsDropdown = !showSettingsDropdown"
          :class="[
            'flex items-center gap-3 px-3 py-2.5 rounded-lg w-full transition-all group',
            isToolsActive()
              ? 'bg-blue-50 text-blue-700'
              : 'text-slate-600 hover:bg-slate-50'
          ]"
        >
          <div :class="[
            'w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 transition-colors',
            isToolsActive()
              ? 'bg-blue-100'
              : 'bg-slate-100 group-hover:bg-slate-200'
          ]">
            <Settings :class="['w-5 h-5', isToolsActive() ? 'text-blue-600' : 'text-slate-500']" />
          </div>
          <span v-if="isSidebarOpen" class="flex-1 text-left">工具</span>
          <ChevronDown
            v-if="isSidebarOpen"
            class="w-4 h-4 text-slate-400 transition-transform"
            :class="{ 'rotate-180': showSettingsDropdown }"
          />
        </button>

        <!-- Tools Dropdown -->
        <div
          v-if="showSettingsDropdown && isSidebarOpen"
          class="mt-1 bg-slate-50 rounded-lg overflow-hidden"
        >
          <RouterLink
            v-for="item in toolItems"
            :key="item.path"
            :to="item.path"
            @click="showSettingsDropdown = false"
            :class="[
              'flex items-center gap-3 px-3 py-2.5 transition-colors',
              isActive(item.path)
                ? 'bg-blue-50 text-blue-700'
                : 'text-slate-600 hover:bg-slate-100'
            ]"
          >
            <Calculator class="w-4 h-4" />
            <span class="text-sm">{{ item.label }}</span>
          </RouterLink>
        </div>
      </div>

      <!-- Collapse Toggle -->
      <button
        @click="isSidebarOpen = !isSidebarOpen"
        class="absolute -right-3 top-20 w-6 h-6 bg-white border border-slate-200 rounded-full shadow-sm flex items-center justify-center hover:bg-slate-50 transition-colors"
      >
        <ChevronLeft v-if="isSidebarOpen" class="w-4 h-4 text-slate-400" />
        <ChevronRight v-else class="w-4 h-4 text-slate-400" />
      </button>
    </aside>

    <!-- Main Content -->
    <main
      :class="[
        'flex-1 transition-all duration-300 flex flex-col min-h-screen',
        isSidebarOpen ? 'ml-60' : 'ml-[72px]'
      ]"
    >
      <!-- Header -->
      <header class="h-14 bg-white border-b border-slate-200 flex items-center px-6 sticky top-0 z-20">
        <div class="flex-1">
          <h1 class="text-base font-medium text-slate-800">
            {{ route.meta.title || '债权审查方案' }}
          </h1>
        </div>
        <div class="flex items-center gap-3">
          <slot name="header-actions" />
          <UserButton />
        </div>
      </header>

      <!-- Content Area -->
      <div class="flex-1 p-6">
        <slot />
      </div>
    </main>
  </div>
</template>
