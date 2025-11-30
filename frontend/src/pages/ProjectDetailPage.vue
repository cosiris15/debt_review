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
import { ArrowLeft, FileText, Lock, Loader2, CheckCircle, AlertCircle } from 'lucide-vue-next'

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
    // Clear selection after submission
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
  <div>
    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500" />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 text-red-700 p-4 rounded-lg">
      {{ error }}
      <button @click="router.back()" class="ml-4 underline">返回</button>
    </div>

    <!-- Content -->
    <div v-else-if="currentProject">
      <!-- Project header -->
      <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
        <div class="flex items-start justify-between">
          <div>
            <button
              @click="router.push('/bankruptcy')"
              class="text-gray-500 hover:text-gray-700 mb-2 flex items-center gap-1"
            >
              <ArrowLeft class="w-4 h-4" />
              返回破产案件
            </button>
            <h1 class="text-2xl font-bold text-gray-800">{{ currentProject.name }}</h1>
            <p class="text-gray-600 mt-1">{{ currentProject.debtor_name }}</p>
          </div>
          <div class="flex flex-col items-end gap-3">
            <!-- 案件文书入口 -->
            <button
              @click="showDocumentsModal = true"
              class="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
            >
              <FileText class="w-4 h-4" />
              案件文书
            </button>
            <!-- 锁定标识 -->
            <div
              class="flex items-center gap-1 text-gray-400 text-sm cursor-help"
              title="项目创建后基本信息不可修改"
            >
              <Lock class="w-3.5 h-3.5" />
              <span>已锁定</span>
            </div>
            <div class="text-right">
              <div class="text-sm text-gray-500">破产受理日期</div>
              <div class="font-semibold text-gray-800">{{ formatDate(currentProject.bankruptcy_date) }}</div>
              <div class="text-xs text-gray-400 mt-1">
                停止计息: {{ formatDate(currentProject.interest_stop_date) }}
              </div>
            </div>
          </div>
        </div>

        <!-- Stats -->
        <div class="grid grid-cols-4 gap-4 mt-6 pt-6 border-t">
          <div class="text-center">
            <div class="text-2xl font-bold text-gray-800">{{ currentProject.total_creditors }}</div>
            <div class="text-sm text-gray-500">总债权人</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-green-600">{{ currentProject.completed_creditors }}</div>
            <div class="text-sm text-gray-500">已完成</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-blue-600">
              {{ currentProject.total_creditors - currentProject.completed_creditors }}
            </div>
            <div class="text-sm text-gray-500">待处理</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-gray-800">
              {{ currentProject.total_creditors > 0
                ? Math.round((currentProject.completed_creditors / currentProject.total_creditors) * 100)
                : 0 }}%
            </div>
            <div class="text-sm text-gray-500">完成率</div>
          </div>
        </div>
      </div>

      <!-- 简化的任务状态指示条 -->
      <div
        v-if="currentTask"
        :class="[
          'mb-6 p-4 rounded-xl flex items-center gap-4',
          taskStatusDisplay.type === 'running' ? 'bg-blue-50 border border-blue-200' :
          taskStatusDisplay.type === 'complete' ? 'bg-green-50 border border-green-200' :
          taskStatusDisplay.type === 'error' ? 'bg-red-50 border border-red-200' :
          'bg-gray-50 border border-gray-200'
        ]"
      >
        <!-- 状态图标 -->
        <div class="flex-shrink-0">
          <Loader2 v-if="taskStatusDisplay.type === 'running'" class="w-6 h-6 text-blue-500 animate-spin" />
          <CheckCircle v-else-if="taskStatusDisplay.type === 'complete'" class="w-6 h-6 text-green-500" />
          <AlertCircle v-else-if="taskStatusDisplay.type === 'error'" class="w-6 h-6 text-red-500" />
        </div>

        <!-- 状态文字 -->
        <div class="flex-1 min-w-0">
          <p :class="[
            'font-medium truncate',
            taskStatusDisplay.type === 'running' ? 'text-blue-700' :
            taskStatusDisplay.type === 'complete' ? 'text-green-700' :
            taskStatusDisplay.type === 'error' ? 'text-red-700' :
            'text-gray-700'
          ]">
            {{ taskStatusDisplay.text }}
          </p>
        </div>

        <!-- 进度条（运行中时显示） -->
        <div v-if="taskStatusDisplay.type === 'running'" class="w-32">
          <div class="flex justify-between text-xs text-blue-600 mb-1">
            <span>进度</span>
            <span>{{ progressPercent }}%</span>
          </div>
          <div class="w-full bg-blue-200 rounded-full h-1.5">
            <div
              class="bg-blue-500 h-1.5 rounded-full transition-all duration-300"
              :style="{ width: `${progressPercent}%` }"
            />
          </div>
        </div>

        <!-- 清除按钮 -->
        <button
          v-if="!isRunning"
          @click="taskStore.reset()"
          class="text-sm text-gray-500 hover:text-gray-700"
        >
          清除
        </button>
      </div>

      <!-- Main content: Creditor list (full width) -->
      <CreditorList :project-id="projectId" @submit="handleSubmitTask" />
    </div>

    <!-- 案件文书弹窗 -->
    <div
      v-if="showDocumentsModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click.self="showDocumentsModal = false"
    >
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden">
        <div class="p-5 border-b flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
              <FileText class="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <h3 class="text-lg font-semibold text-gray-800">案件文书</h3>
              <p class="text-sm text-gray-500">裁定书、决定书等案件材料</p>
            </div>
          </div>
          <button
            @click="showDocumentsModal = false"
            class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6">
          <!-- 暂无文书提示 -->
          <div class="text-center py-8">
            <div class="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4">
              <FileText class="w-8 h-8 text-gray-400" />
            </div>
            <p class="text-gray-600 mb-2">暂无案件文书</p>
            <p class="text-sm text-gray-500">
              创建项目时上传的裁定书/决定书将显示在这里
            </p>
          </div>
        </div>
        <div class="px-6 py-4 bg-gray-50 border-t flex justify-end">
          <button
            @click="showDocumentsModal = false"
            class="px-4 py-2 text-gray-600 hover:text-gray-800"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
