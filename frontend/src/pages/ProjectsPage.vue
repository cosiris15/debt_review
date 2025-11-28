<script setup lang="ts">
/**
 * Projects List Page
 */
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useProjectStore } from '@/stores/project'

const router = useRouter()
const projectStore = useProjectStore()
const { projects, loading, error } = storeToRefs(projectStore)

onMounted(() => {
  projectStore.fetchProjects()
})

function formatDate(date: string): string {
  return new Date(date).toLocaleDateString('zh-CN')
}

function getProgressPercent(project: typeof projects.value[0]): number {
  if (project.total_creditors === 0) return 0
  return Math.round((project.completed_creditors / project.total_creditors) * 100)
}
</script>

<template>
  <div>
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-800">项目管理</h1>
      <button
        @click="router.push('/projects/new')"
        class="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors flex items-center gap-2"
      >
        <span class="text-lg">+</span>
        新建项目
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500" />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 text-red-700 p-4 rounded-lg">
      {{ error }}
    </div>

    <!-- Empty state -->
    <div v-else-if="projects.length === 0" class="bg-white rounded-xl shadow-sm p-12 text-center">
      <div class="text-6xl mb-4">📁</div>
      <h3 class="text-xl font-semibold text-gray-800 mb-2">暂无项目</h3>
      <p class="text-gray-600 mb-6">创建您的第一个破产项目开始使用</p>
      <button
        @click="router.push('/projects/new')"
        class="px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
      >
        创建项目
      </button>
    </div>

    <!-- Projects grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="project in projects"
        :key="project.id"
        @click="router.push(`/projects/${project.id}`)"
        class="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow cursor-pointer overflow-hidden"
      >
        <!-- Card header -->
        <div class="p-5 border-b">
          <h3 class="text-lg font-semibold text-gray-800 truncate">{{ project.name }}</h3>
          <p class="text-sm text-gray-500 mt-1">{{ project.debtor_name }}</p>
        </div>

        <!-- Card body -->
        <div class="p-5">
          <div class="grid grid-cols-2 gap-4 text-sm mb-4">
            <div>
              <p class="text-gray-500">破产受理日</p>
              <p class="font-medium text-gray-800">{{ formatDate(project.bankruptcy_date) }}</p>
            </div>
            <div>
              <p class="text-gray-500">债权人数</p>
              <p class="font-medium text-gray-800">{{ project.total_creditors }} 人</p>
            </div>
          </div>

          <!-- Progress -->
          <div>
            <div class="flex justify-between text-sm mb-1">
              <span class="text-gray-500">完成进度</span>
              <span class="text-gray-700">{{ getProgressPercent(project) }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div
                class="bg-primary-500 h-2 rounded-full transition-all"
                :style="{ width: `${getProgressPercent(project)}%` }"
              />
            </div>
          </div>
        </div>

        <!-- Card footer -->
        <div class="px-5 py-3 bg-gray-50 flex justify-between items-center">
          <span class="text-xs text-gray-500">
            创建于 {{ formatDate(project.created_at) }}
          </span>
          <span class="text-primary-600 text-sm">查看详情 →</span>
        </div>
      </div>
    </div>
  </div>
</template>
