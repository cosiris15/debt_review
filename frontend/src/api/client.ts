/**
 * API Client with polling support
 *
 * Handles all HTTP communication with the backend.
 * Includes automatic polling for long-running tasks.
 */

import axios, { AxiosInstance, AxiosError } from 'axios'
import type {
  Project, ProjectCreate,
  Creditor, CreditorCreate,
  Task, TaskCreate, TaskSubmitResponse, TaskProgress, TaskLog,
  InterestCalculationRequest, InterestCalculationResponse
} from '@/types'

// API base URL from environment or default
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Error handler
function handleError(error: AxiosError): never {
  if (error.response) {
    const message = (error.response.data as { detail?: string })?.detail || error.message
    throw new Error(message)
  }
  throw error
}

// ============== Projects API ==============

export const projectsApi = {
  async list(): Promise<Project[]> {
    try {
      const response = await api.get<Project[]>('/projects')
      return response.data
    } catch (error) {
      handleError(error as AxiosError)
    }
  },

  async get(id: string): Promise<Project> {
    try {
      const response = await api.get<Project>(`/projects/${id}`)
      return response.data
    } catch (error) {
      handleError(error as AxiosError)
    }
  },

  async create(data: ProjectCreate): Promise<Project> {
    try {
      const response = await api.post<Project>('/projects', data)
      return response.data
    } catch (error) {
      handleError(error as AxiosError)
    }
  }
}

// ============== Creditors API ==============

export const creditorsApi = {
  async list(projectId: string, batchNumber?: number): Promise<Creditor[]> {
    try {
      const params = batchNumber ? { batch_number: batchNumber } : {}
      const response = await api.get<Creditor[]>(`/creditors/project/${projectId}`, { params })
      return response.data
    } catch (error) {
      handleError(error as AxiosError)
    }
  },

  async get(id: string): Promise<Creditor> {
    try {
      const response = await api.get<Creditor>(`/creditors/${id}`)
      return response.data
    } catch (error) {
      handleError(error as AxiosError)
    }
  },

  async create(data: CreditorCreate): Promise<Creditor> {
    try {
      const response = await api.post<Creditor>('/creditors', data)
      return response.data
    } catch (error) {
      handleError(error as AxiosError)
    }
  }
}

// ============== Tasks API ==============

export const tasksApi = {
  async submit(data: TaskCreate): Promise<TaskSubmitResponse> {
    try {
      const response = await api.post<TaskSubmitResponse>('/tasks', data)
      return response.data
    } catch (error) {
      handleError(error as AxiosError)
    }
  },

  async get(id: string): Promise<Task> {
    try {
      const response = await api.get<Task>(`/tasks/${id}`)
      return response.data
    } catch (error) {
      handleError(error as AxiosError)
    }
  },

  async getProgress(id: string): Promise<TaskProgress> {
    try {
      const response = await api.get<TaskProgress>(`/tasks/${id}/status`)
      return response.data
    } catch (error) {
      handleError(error as AxiosError)
    }
  },

  async getLogs(id: string, limit = 100): Promise<{ logs: TaskLog[] }> {
    try {
      const response = await api.get<{ task_id: string; logs: TaskLog[] }>(
        `/tasks/${id}/logs`,
        { params: { limit } }
      )
      return response.data
    } catch (error) {
      handleError(error as AxiosError)
    }
  },

  async cancel(id: string): Promise<void> {
    try {
      await api.post(`/tasks/${id}/cancel`)
    } catch (error) {
      handleError(error as AxiosError)
    }
  },

  async listByProject(projectId: string): Promise<Task[]> {
    try {
      const response = await api.get<Task[]>(`/tasks/project/${projectId}`)
      return response.data
    } catch (error) {
      handleError(error as AxiosError)
    }
  }
}

// ============== Tools API ==============

export const toolsApi = {
  async calculateInterest(data: InterestCalculationRequest): Promise<InterestCalculationResponse> {
    try {
      const response = await api.post<InterestCalculationResponse>('/tools/calculate-interest', data)
      return response.data
    } catch (error) {
      handleError(error as AxiosError)
    }
  }
}

// ============== Polling Utility ==============

export interface PollingOptions {
  interval?: number  // Polling interval in ms (default: 3000)
  maxAttempts?: number  // Max polling attempts (default: unlimited)
  onProgress?: (progress: TaskProgress) => void
  onComplete?: (progress: TaskProgress) => void
  onError?: (error: Error) => void
}

export class TaskPoller {
  private taskId: string
  private options: Required<PollingOptions>
  private intervalId: ReturnType<typeof setInterval> | null = null
  private attempts = 0

  constructor(taskId: string, options: PollingOptions = {}) {
    this.taskId = taskId
    this.options = {
      interval: options.interval || 3000,
      maxAttempts: options.maxAttempts || Infinity,
      onProgress: options.onProgress || (() => {}),
      onComplete: options.onComplete || (() => {}),
      onError: options.onError || (() => {})
    }
  }

  start(): void {
    this.poll() // Initial poll
    this.intervalId = setInterval(() => this.poll(), this.options.interval)
  }

  stop(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId)
      this.intervalId = null
    }
  }

  private async poll(): Promise<void> {
    try {
      this.attempts++

      if (this.options.maxAttempts !== Infinity && this.attempts > this.options.maxAttempts) {
        this.stop()
        this.options.onError(new Error('Max polling attempts reached'))
        return
      }

      const progress = await tasksApi.getProgress(this.taskId)
      this.options.onProgress(progress)

      // Check if task is done
      if (['completed', 'failed', 'cancelled'].includes(progress.status)) {
        this.stop()
        this.options.onComplete(progress)
      }
    } catch (error) {
      this.stop()
      this.options.onError(error as Error)
    }
  }
}

// ============== Health Check ==============

export async function checkHealth(): Promise<{ status: string; services: Record<string, string> }> {
  try {
    const response = await axios.get(`${API_BASE_URL}/health`)
    return response.data
  } catch {
    return { status: 'unreachable', services: {} }
  }
}

export default api
