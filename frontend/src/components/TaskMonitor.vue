<script setup lang="ts">
/**
 * Task Monitor Component
 *
 * Real-time display of task progress with stage indicators and logs.
 */
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useTaskStore } from '@/stores/task'
import ProgressRing from './ProgressRing.vue'
import { TaskStage, STAGE_LABELS, STATUS_LABELS, STATUS_COLORS } from '@/types'

const taskStore = useTaskStore()
const {
  currentTask,
  currentProgress,
  logs,
  isRunning,
  isComplete,
  progressPercent,
  statusMessage,
  error
} = storeToRefs(taskStore)

const stages = [
  TaskStage.INIT,
  TaskStage.FACT_CHECK,
  TaskStage.LEGAL_DIAGRAM,
  TaskStage.ANALYSIS,
  TaskStage.REPORT,
  TaskStage.VALIDATION,
  TaskStage.COMPLETE
]

const currentStageIndex = computed(() => {
  if (!currentProgress.value) return -1
  const stage = currentProgress.value.current_stage
  // 处理 error 状态：不在正常流程中，返回 -1
  if (stage === TaskStage.ERROR) return -1
  return stages.indexOf(stage)
})

function getStageStatus(index: number): 'completed' | 'current' | 'pending' {
  if (index < currentStageIndex.value) return 'completed'
  if (index === currentStageIndex.value) return 'current'
  return 'pending'
}

function handleCancel() {
  if (confirm('确定要取消当前任务吗？')) {
    taskStore.cancelTask()
  }
}
</script>

<template>
  <div class="bg-white rounded-xl shadow-lg p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-semibold text-gray-800">任务监控</h2>
      <span
        v-if="currentProgress"
        :class="[
          'px-3 py-1 rounded-full text-sm font-medium',
          STATUS_COLORS[currentProgress.status]
        ]"
      >
        {{ STATUS_LABELS[currentProgress.status] }}
      </span>
    </div>

    <!-- No task -->
    <div v-if="!currentTask" class="text-center py-12 text-gray-500">
      <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
      <p>暂无运行中的任务</p>
      <p class="text-sm mt-1">选择债权人并提交任务开始处理</p>
    </div>

    <!-- Task progress -->
    <div v-else>
      <!-- Progress ring -->
      <div class="flex justify-center mb-8">
        <ProgressRing :progress="progressPercent" :size="160" :stroke-width="10" />
      </div>

      <!-- Status message -->
      <p class="text-center text-gray-600 mb-6">{{ statusMessage }}</p>

      <!-- Creditor progress -->
      <div v-if="currentProgress?.stage_details" class="mb-6">
        <div class="flex justify-between text-sm text-gray-600 mb-2">
          <span>债权人进度</span>
          <span>
            {{ currentProgress.stage_details.creditors_completed }} /
            {{ currentProgress.stage_details.creditors_total }}
          </span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div
            class="bg-blue-500 h-2 rounded-full transition-all duration-300"
            :style="{
              width: `${(currentProgress.stage_details.creditors_completed / currentProgress.stage_details.creditors_total) * 100}%`
            }"
          />
        </div>
      </div>

      <!-- Stage indicators -->
      <div class="mb-8">
        <div class="flex justify-between">
          <div
            v-for="(stage, index) in stages"
            :key="stage"
            class="flex flex-col items-center flex-1"
          >
            <!-- Stage dot -->
            <div
              :class="[
                'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all duration-300',
                getStageStatus(index) === 'completed' ? 'bg-green-500 text-white' :
                getStageStatus(index) === 'current' ? 'bg-blue-500 text-white animate-pulse' :
                'bg-gray-200 text-gray-500'
              ]"
            >
              <svg v-if="getStageStatus(index) === 'completed'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
              </svg>
              <span v-else>{{ index + 1 }}</span>
            </div>
            <!-- Stage label -->
            <span
              :class="[
                'text-xs mt-2 text-center',
                getStageStatus(index) === 'current' ? 'text-blue-600 font-medium' : 'text-gray-500'
              ]"
            >
              {{ STAGE_LABELS[stage] }}
            </span>
          </div>
        </div>
        <!-- Connector line -->
        <div class="relative -mt-[52px] mx-4 h-[2px] bg-gray-200 -z-10">
          <div
            class="absolute h-full bg-green-500 transition-all duration-500"
            :style="{ width: `${(currentStageIndex / (stages.length - 1)) * 100}%` }"
          />
        </div>
      </div>

      <!-- Logs -->
      <div class="bg-gray-900 rounded-lg p-4 max-h-48 overflow-y-auto">
        <div class="font-mono text-sm">
          <div
            v-for="log in logs.slice(-20)"
            :key="log.id"
            :class="[
              'py-1',
              log.level === 'error' ? 'text-red-400' :
              log.level === 'warning' ? 'text-yellow-400' :
              'text-green-400'
            ]"
          >
            <span class="text-gray-500">{{ new Date(log.created_at).toLocaleTimeString() }}</span>
            <span class="ml-2">{{ log.message }}</span>
          </div>
          <div v-if="logs.length === 0" class="text-gray-500">
            等待日志...
          </div>
        </div>
      </div>

      <!-- Error message -->
      <div v-if="error" class="mt-4 p-4 bg-red-50 text-red-700 rounded-lg">
        <p class="font-medium">错误</p>
        <p class="text-sm">{{ error }}</p>
      </div>

      <!-- Actions -->
      <div class="mt-6 flex justify-end gap-3">
        <button
          v-if="isRunning"
          @click="handleCancel"
          class="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
        >
          取消任务
        </button>
        <button
          v-if="isComplete"
          @click="taskStore.reset()"
          class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
        >
          清除
        </button>
      </div>
    </div>
  </div>
</template>
