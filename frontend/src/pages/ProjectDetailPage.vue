<script setup lang="ts">
/**
 * Project Detail Page
 *
 * 项目详情页，展示：
 * - 项目基本信息（含案件文书入口）
 * - 债权人列表（主体部分）
 * - 简化的任务进度指示器
 */
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useProjectStore } from '@/stores/project'
import { useTaskStore } from '@/stores/task'
import CreditorList from '@/components/CreditorList.vue'
import {
  ArrowLeft, FileText, Lock, Loader2, CheckCircle, AlertCircle,
  Users, CheckCircle2, Clock, X, Calendar
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()
const taskStore = useTaskStore()

const { currentProject, loading, error } = storeToRefs(projectStore)
const { currentTask, isRunning, isComplete, progressPercent, statusMessage, error: taskError } = storeToRefs(taskStore)
const projectId = route.params.id as string

// 案件文书弹窗
const showDocumentsModal = ref(false)

onMounted(() => {
  projectStore.fetchProject(projectId)
})

onUnmounted(() => {
  projectStore.reset()
  taskStore.reset()
})

async function handleSubmitTask(creditorIds: string[]) {
  try {
    await taskStore.submitTask({
      project_id: projectId,
      creditor_ids: creditorIds,
      processing_mode: 'auto'
    })
    projectStore.clearSelection()
  } catch (e) {
    console.error('Failed to submit task:', e)
  }
}

function formatDate(date: string): string {
  return new Date(date).toLocaleDateString('zh-CN')
}

// 任务状态显示
const taskStatusDisplay = computed(() => {
  if (!currentTask.value) {
    return { type: 'idle', text: '无运行中任务' }
  }
  if (isRunning.value) {
    return { type: 'running', text: statusMessage.value || '任务处理中...' }
  }
  if (isComplete.value) {
    return { type: 'complete', text: '任务已完成' }
  }
  if (taskError.value) {
    return { type: 'error', text: taskError.value }
  }
  return { type: 'idle', text: '等待任务' }
})
</script>

<template>
  <div class="max-w-6xl mx-auto">
    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-16">
      <div class="animate-spin rounded-full h-8 w-8 border-2 border-blue-600 border-t-transparent" />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl flex items-center justify-between">
      <span>{{ error }}</span>
      <button @click="router.back()" class="text-red-600 hover:text-red-800 font-medium">返回</button>
    </div>

    <!-- Content -->
    <div v-else-if="currentProject">
      <!-- Back Button -->
      <button
        @click="router.push('/bankruptcy')"
        class="text-slate-500 hover:text-slate-700 mb-4 flex items-center gap-1.5 text-sm font-medium transition-colors"
      >
        <ArrowLeft class="w-4 h-4" />
        返回破产案件
      </button>

      <!-- Project Header Card -->
      <div class="bg-white rounded-xl border border-slate-200 mb-6">
        <div class="p-6">
          <div class="flex items-start justify-between">
            <div>
              <h1 class="text-xl font-semibold text-slate-800">{{ currentProject.name }}</h1>
              <p class="text-slate-500 mt-1">{{ currentProject.debtor_name }}</p>
            </div>
            <div class="flex items-center gap-3">
              <!-- 案件文书入口 -->
              <button
                @click="showDocumentsModal = true"
                class="flex items-center gap-2 px-3 py-2 text-sm text-slate-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors border border-slate-200"
              >
                <FileText class="w-4 h-4" />
                案件文书
              </button>
              <!-- 锁定标识 -->
              <div
                class="flex items-center gap-1.5 px-3 py-2 text-slate-400 text-sm bg-slate-50 rounded-lg cursor-help"
                title="项目创建后基本信息不可修改"
              >
                <Lock class="w-3.5 h-3.5" />
                <span>已锁定</span>
              </div>
            </div>
          </div>

          <!-- Info Grid -->
          <div class="flex items-center gap-6 mt-4 text-sm">
            <div class="flex items-center gap-1.5 text-slate-500">
              <Calendar class="w-4 h-4" />
              <span>受理日期: {{ formatDate(currentProject.bankruptcy_date) }}</span>
            </div>
            <div class="flex items-center gap-1.5 text-slate-500">
              <Clock class="w-4 h-4" />
              <span>停止计息: {{ formatDate(currentProject.interest_stop_date) }}</span>
            </div>
          </div>
        </div>

        <!-- Stats Bar -->
        <div class="grid grid-cols-4 border-t border-slate-100">
          <div class="p-4 text-center border-r border-slate-100">
            <div class="flex items-center justify-center gap-2 mb-1">
              <Users class="w-4 h-4 text-slate-400" />
              <span class="text-2xl font-semibold text-slate-800">{{ currentProject.total_creditors }}</span>
            </div>
            <div class="text-xs text-slate-500">总债权人</div>
          </div>
          <div class="p-4 text-center border-r border-slate-100">
            <div class="flex items-center justify-center gap-2 mb-1">
              <CheckCircle2 class="w-4 h-4 text-emerald-500" />
              <span class="text-2xl font-semibold text-emerald-600">{{ currentProject.completed_creditors }}</span>
            </div>
            <div class="text-xs text-slate-500">已完成</div>
          </div>
          <div class="p-4 text-center border-r border-slate-100">
            <div class="flex items-center justify-center gap-2 mb-1">
              <Clock class="w-4 h-4 text-amber-500" />
              <span class="text-2xl font-semibold text-amber-600">
                {{ currentProject.total_creditors - currentProject.completed_creditors }}
              </span>
            </div>
            <div class="text-xs text-slate-500">待处理</div>
          </div>
          <div class="p-4 text-center">
            <div class="text-2xl font-semibold" :class="[
              currentProject.total_creditors > 0 && currentProject.completed_creditors === currentProject.total_creditors
                ? 'text-emerald-600'
                : 'text-slate-800'
            ]">
              {{ currentProject.total_creditors > 0
                ? Math.round((currentProject.completed_creditors / currentProject.total_creditors) * 100)
                : 0 }}%
            </div>
            <div class="text-xs text-slate-500">完成率</div>
          </div>
        </div>
      </div>

      <!-- 简化的任务状态指示条 -->
      <div
        v-if="currentTask"
        :class="[
          'mb-6 p-4 rounded-xl flex items-center gap-4 border',
          taskStatusDisplay.type === 'running' ? 'bg-blue-50 border-blue-200' :
          taskStatusDisplay.type === 'complete' ? 'bg-emerald-50 border-emerald-200' :
          taskStatusDisplay.type === 'error' ? 'bg-red-50 border-red-200' :
          'bg-slate-50 border-slate-200'
        ]"
      >
        <!-- 状态图标 -->
        <div class="flex-shrink-0">
          <Loader2 v-if="taskStatusDisplay.type === 'running'" class="w-5 h-5 text-blue-600 animate-spin" />
          <CheckCircle v-else-if="taskStatusDisplay.type === 'complete'" class="w-5 h-5 text-emerald-600" />
          <AlertCircle v-else-if="taskStatusDisplay.type === 'error'" class="w-5 h-5 text-red-600" />
        </div>

        <!-- 状态文字 -->
        <div class="flex-1 min-w-0">
          <p :class="[
            'font-medium truncate text-sm',
            taskStatusDisplay.type === 'running' ? 'text-blue-700' :
            taskStatusDisplay.type === 'complete' ? 'text-emerald-700' :
            taskStatusDisplay.type === 'error' ? 'text-red-700' :
            'text-slate-700'
          ]">
            {{ taskStatusDisplay.text }}
          </p>
        </div>

        <!-- 进度条（运行中时显示） -->
        <div v-if="taskStatusDisplay.type === 'running'" class="w-36">
          <div class="flex justify-between text-xs text-blue-600 mb-1">
            <span>进度</span>
            <span class="font-medium">{{ progressPercent }}%</span>
          </div>
          <div class="w-full bg-blue-200 rounded-full h-1.5">
            <div
              class="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
              :style="{ width: `${progressPercent}%` }"
            />
          </div>
        </div>

        <!-- 清除按钮 -->
        <button
          v-if="!isRunning"
          @click="taskStore.reset()"
          class="text-slate-400 hover:text-slate-600 p-1"
        >
          <X class="w-4 h-4" />
        </button>
      </div>

      <!-- Main content: Creditor list (full width) -->
      <CreditorList :project-id="projectId" @submit="handleSubmitTask" />
    </div>

    <!-- 案件文书弹窗 -->
    <div
      v-if="showDocumentsModal"
      class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
      @click.self="showDocumentsModal = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden">
        <div class="p-5 border-b border-slate-100 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center">
              <FileText class="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h3 class="text-lg font-semibold text-slate-800">案件文书</h3>
              <p class="text-sm text-slate-500">裁定书、决定书等</p>
            </div>
          </div>
          <button
            @click="showDocumentsModal = false"
            class="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <X class="w-5 h-5" />
          </button>
        </div>
        <div class="p-8">
          <!-- 暂无文书提示 -->
          <div class="text-center">
            <div class="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center mx-auto mb-4">
              <FileText class="w-8 h-8 text-slate-400" />
            </div>
            <p class="text-slate-700 font-medium mb-1">暂无案件文书</p>
            <p class="text-sm text-slate-500">
              创建项目时上传的裁定书/决定书将显示在这里
            </p>
          </div>
        </div>
        <div class="px-5 py-4 bg-slate-50 border-t border-slate-100 flex justify-end">
          <button
            @click="showDocumentsModal = false"
            class="px-4 py-2 text-slate-600 hover:text-slate-800 font-medium"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
