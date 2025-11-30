<script setup lang="ts">
/**
 * Bankruptcy Page (破产案件)
 *
 * 破产案件主页，直接展示项目列表，允许新建项目。
 */
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useProjectStore } from '@/stores/project'
import { Plus, Building2, Calendar, Users, ArrowRight, FolderOpen } from 'lucide-vue-next'

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

function getProgressColor(percent: number): string {
  if (percent >= 100) return 'bg-emerald-500'
  if (percent >= 50) return 'bg-blue-500'
  return 'bg-amber-500'
}
</script>

<template>
  <div class="max-w-6xl mx-auto">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-semibold text-slate-800">破产案件</h1>
        <p class="text-slate-500 mt-1">管理破产项目，审查债权人申报</p>
      </div>
      <button
        @click="router.push('/projects/new')"
        class="px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 font-medium shadow-sm"
      >
        <Plus class="w-4 h-4" />
        新建项目
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-16">
      <div class="animate-spin rounded-full h-8 w-8 border-2 border-blue-600 border-t-transparent" />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl">
      {{ error }}
    </div>

    <!-- Empty state -->
    <div v-else-if="projects.length === 0" class="bg-white rounded-2xl border border-slate-200 p-16 text-center">
      <div class="w-20 h-20 rounded-2xl bg-slate-100 flex items-center justify-center mx-auto mb-6">
        <FolderOpen class="w-10 h-10 text-slate-400" />
      </div>
      <h3 class="text-xl font-semibold text-slate-800 mb-2">暂无项目</h3>
      <p class="text-slate-500 mb-8 max-w-sm mx-auto">创建您的第一个破产项目，开始使用债权审查方案</p>
      <button
        @click="router.push('/projects/new')"
        class="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors inline-flex items-center gap-2 font-medium shadow-sm"
      >
        <Plus class="w-5 h-5" />
        创建项目
      </button>
    </div>

    <!-- Projects grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
      <div
        v-for="project in projects"
        :key="project.id"
        @click="router.push(`/projects/${project.id}`)"
        class="bg-white rounded-xl border border-slate-200 hover:border-blue-300 hover:shadow-lg transition-all cursor-pointer group overflow-hidden"
      >
        <!-- Card header -->
        <div class="p-5 pb-4">
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0 flex-1">
              <h3 class="text-base font-semibold text-slate-800 truncate group-hover:text-blue-600 transition-colors">
                {{ project.name }}
              </h3>
              <p class="text-sm text-slate-500 mt-0.5 truncate">{{ project.debtor_name }}</p>
            </div>
            <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center group-hover:bg-blue-100 transition-colors">
              <Building2 class="w-5 h-5 text-blue-600" />
            </div>
          </div>
        </div>

        <!-- Card body -->
        <div class="px-5 pb-4">
          <div class="flex items-center gap-6 text-sm">
            <div class="flex items-center gap-1.5 text-slate-500">
              <Calendar class="w-4 h-4" />
              <span>{{ formatDate(project.bankruptcy_date) }}</span>
            </div>
            <div class="flex items-center gap-1.5 text-slate-500">
              <Users class="w-4 h-4" />
              <span>{{ project.total_creditors }} 人</span>
            </div>
          </div>

          <!-- Progress -->
          <div class="mt-4">
            <div class="flex justify-between text-sm mb-1.5">
              <span class="text-slate-500">审查进度</span>
              <span class="font-medium" :class="getProgressPercent(project) >= 100 ? 'text-emerald-600' : 'text-slate-700'">
                {{ project.completed_creditors }}/{{ project.total_creditors }}
              </span>
            </div>
            <div class="w-full bg-slate-100 rounded-full h-1.5">
              <div
                :class="['h-1.5 rounded-full transition-all', getProgressColor(getProgressPercent(project))]"
                :style="{ width: `${getProgressPercent(project)}%` }"
              />
            </div>
          </div>
        </div>

        <!-- Card footer -->
        <div class="px-5 py-3 bg-slate-50 border-t border-slate-100 flex justify-between items-center">
          <span class="text-xs text-slate-400">
            创建于 {{ formatDate(project.created_at) }}
          </span>
          <span class="text-blue-600 text-sm font-medium flex items-center gap-1 group-hover:gap-2 transition-all">
            进入项目
            <ArrowRight class="w-4 h-4" />
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
