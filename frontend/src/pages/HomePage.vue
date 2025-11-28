<script setup lang="ts">
/**
 * Home Page
 *
 * Dashboard with quick access to main features.
 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { checkHealth } from '@/api/client'
import { useProjectStore } from '@/stores/project'

const router = useRouter()
const projectStore = useProjectStore()

const healthStatus = ref<{ status: string; services: Record<string, string> } | null>(null)

onMounted(async () => {
  healthStatus.value = await checkHealth()
  await projectStore.fetchProjects()
})

const features = [
  {
    title: '项目管理',
    description: '创建和管理破产项目，添加债权人',
    icon: '📁',
    path: '/projects',
    color: 'bg-blue-50 text-blue-600'
  },
  {
    title: '债权审查',
    description: '一键启动自动化债权审查流程',
    icon: '🔍',
    path: '/projects',
    color: 'bg-green-50 text-green-600'
  },
  {
    title: '利息计算',
    description: '支持LPR、单利、复利等多种计算',
    icon: '🧮',
    path: '/calculator',
    color: 'bg-purple-50 text-purple-600'
  }
]
</script>

<template>
  <div>
    <!-- Welcome section -->
    <div class="bg-gradient-to-r from-primary-500 to-primary-700 rounded-2xl p-8 text-white mb-8">
      <h1 class="text-3xl font-bold mb-2">债权审查系统</h1>
      <p class="text-primary-100 text-lg">自动化破产债权审查解决方案</p>
      <div class="mt-6 flex gap-4">
        <button
          @click="router.push('/projects/new')"
          class="px-6 py-3 bg-white text-primary-600 rounded-lg font-medium hover:bg-primary-50 transition-colors"
        >
          创建新项目
        </button>
        <button
          @click="router.push('/projects')"
          class="px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-800 transition-colors"
        >
          查看项目
        </button>
      </div>
    </div>

    <!-- Features -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div
        v-for="feature in features"
        :key="feature.title"
        @click="router.push(feature.path)"
        class="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
      >
        <div :class="['w-12 h-12 rounded-lg flex items-center justify-center text-2xl mb-4', feature.color]">
          {{ feature.icon }}
        </div>
        <h3 class="text-lg font-semibold text-gray-800 mb-2">{{ feature.title }}</h3>
        <p class="text-gray-600 text-sm">{{ feature.description }}</p>
      </div>
    </div>

    <!-- Recent projects -->
    <div class="bg-white rounded-xl shadow-sm p-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">最近项目</h2>
      <div v-if="projectStore.projects.length === 0" class="text-center py-8 text-gray-500">
        <p>暂无项目</p>
        <button
          @click="router.push('/projects/new')"
          class="mt-2 text-primary-600 hover:text-primary-700"
        >
          创建第一个项目 →
        </button>
      </div>
      <div v-else class="divide-y">
        <div
          v-for="project in projectStore.projects.slice(0, 5)"
          :key="project.id"
          @click="router.push(`/projects/${project.id}`)"
          class="py-4 flex items-center justify-between hover:bg-gray-50 -mx-4 px-4 cursor-pointer transition-colors"
        >
          <div>
            <h3 class="font-medium text-gray-800">{{ project.name }}</h3>
            <p class="text-sm text-gray-500">{{ project.debtor_name }}</p>
          </div>
          <div class="text-right">
            <p class="text-sm text-gray-600">
              {{ project.completed_creditors }} / {{ project.total_creditors }} 完成
            </p>
            <p class="text-xs text-gray-400">
              {{ new Date(project.created_at).toLocaleDateString() }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- System status -->
    <div class="mt-6 bg-gray-50 rounded-lg p-4 flex items-center justify-between">
      <span class="text-sm text-gray-600">系统状态</span>
      <div class="flex items-center gap-2">
        <span
          :class="[
            'w-2 h-2 rounded-full',
            healthStatus?.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
          ]"
        />
        <span class="text-sm text-gray-600">
          {{ healthStatus?.status === 'healthy' ? '正常运行' : '连接异常' }}
        </span>
      </div>
    </div>
  </div>
</template>
