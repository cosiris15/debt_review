/**
 * Task Store - Manages task state and polling
 *
 * Handles the async task pattern with real-time progress updates.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { tasksApi, TaskPoller } from '@/api/client'
import type { Task, TaskProgress, TaskCreate, TaskStatus, TaskLog } from '@/types'

export const useTaskStore = defineStore('task', () => {
  // State
  const currentTask = ref<Task | null>(null)
  const currentProgress = ref<TaskProgress | null>(null)
  const logs = ref<TaskLog[]>([])
  const isPolling = ref(false)
  const error = ref<string | null>(null)

  // Active poller instance
  let poller: TaskPoller | null = null

  // Computed
  const isRunning = computed(() =>
    currentProgress.value?.status === 'running'
  )

  const isComplete = computed(() =>
    ['completed', 'failed', 'cancelled'].includes(currentProgress.value?.status || '')
  )

  const progressPercent = computed(() =>
    currentProgress.value?.progress_percent || 0
  )

  const statusMessage = computed(() => {
    if (!currentProgress.value) return ''
    const p = currentProgress.value
    if (p.current_creditor) {
      return `正在处理: ${p.current_creditor}`
    }
    return `阶段: ${p.current_stage}`
  })

  // Actions
  async function submitTask(data: TaskCreate): Promise<string> {
    try {
      error.value = null
      const response = await tasksApi.submit(data)
      const taskId = response.task_id

      // Fetch full task info
      currentTask.value = await tasksApi.get(taskId)

      // Start polling
      startPolling(taskId)

      return taskId
    } catch (e) {
      error.value = (e as Error).message
      throw e
    }
  }

  function startPolling(taskId: string): void {
    // Stop any existing poller
    stopPolling()

    isPolling.value = true
    logs.value = []

    poller = new TaskPoller(taskId, {
      interval: 3000,
      onProgress: (progress) => {
        currentProgress.value = progress
        // Append new logs
        if (progress.logs) {
          const newLogs = progress.logs.filter(
            log => !logs.value.some(l => l.message === log)
          )
          logs.value.push(...newLogs.map(msg => ({
            id: crypto.randomUUID(),
            task_id: taskId,
            level: 'info' as const,
            message: msg,
            created_at: new Date().toISOString()
          })))
        }
      },
      onComplete: (progress) => {
        currentProgress.value = progress
        isPolling.value = false
      },
      onError: (e) => {
        error.value = e.message
        isPolling.value = false
      }
    })

    poller.start()
  }

  function stopPolling(): void {
    if (poller) {
      poller.stop()
      poller = null
    }
    isPolling.value = false
  }

  async function cancelTask(): Promise<void> {
    if (!currentTask.value) return

    try {
      await tasksApi.cancel(currentTask.value.id)
      stopPolling()
      if (currentProgress.value) {
        currentProgress.value.status = 'cancelled' as TaskStatus
      }
    } catch (e) {
      error.value = (e as Error).message
    }
  }

  async function loadTask(taskId: string): Promise<void> {
    try {
      error.value = null
      currentTask.value = await tasksApi.get(taskId)
      currentProgress.value = await tasksApi.getProgress(taskId)

      // If task is still running, start polling
      if (currentProgress.value.status === 'running') {
        startPolling(taskId)
      }
    } catch (e) {
      error.value = (e as Error).message
    }
  }

  async function fetchLogs(limit = 100): Promise<void> {
    if (!currentTask.value) return

    try {
      const response = await tasksApi.getLogs(currentTask.value.id, limit)
      logs.value = response.logs
    } catch (e) {
      console.error('Failed to fetch logs:', e)
    }
  }

  function reset(): void {
    stopPolling()
    currentTask.value = null
    currentProgress.value = null
    logs.value = []
    error.value = null
  }

  return {
    // State
    currentTask,
    currentProgress,
    logs,
    isPolling,
    error,

    // Computed
    isRunning,
    isComplete,
    progressPercent,
    statusMessage,

    // Actions
    submitTask,
    startPolling,
    stopPolling,
    cancelTask,
    loadTask,
    fetchLogs,
    reset
  }
})
