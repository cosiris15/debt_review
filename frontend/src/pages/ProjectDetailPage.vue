<script setup lang="ts">
/**
 * Project Detail Page
 *
 * Shows project info, creditors list, and task monitor.
 */
import { onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useProjectStore } from '@/stores/project'
import { useTaskStore } from '@/stores/task'
import CreditorList from '@/components/CreditorList.vue'
import TaskMonitor from '@/components/TaskMonitor.vue'

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()
const taskStore = useTaskStore()

const { currentProject, loading, error } = storeToRefs(projectStore)
const projectId = route.params.id as string

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
              @click="router.push('/projects')"
              class="text-gray-500 hover:text-gray-700 mb-2 flex items-center gap-1"
            >
              ← 返回项目列表
            </button>
            <h1 class="text-2xl font-bold text-gray-800">{{ currentProject.name }}</h1>
            <p class="text-gray-600 mt-1">{{ currentProject.debtor_name }}</p>
          </div>
          <div class="flex flex-col items-end">
            <!-- 锁定标识：项目创建后基本信息不可修改 -->
            <div
              class="flex items-center gap-1 text-gray-400 text-sm mb-3 cursor-help"
              title="项目创建后基本信息不可修改"
            >
              <span>🔒</span>
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

      <!-- Main content -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Creditor list -->
        <div>
          <CreditorList :project-id="projectId" @submit="handleSubmitTask" />
        </div>

        <!-- Task monitor -->
        <div>
          <TaskMonitor />
        </div>
      </div>
    </div>
  </div>
</template>
