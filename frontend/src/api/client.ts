/**
 * API Client with polling support
 *
 * Handles all HTTP communication with the backend.
 * Includes automatic polling for long-running tasks.
 * Automatically includes Clerk auth token in requests.
 */

import axios, { type AxiosInstance, type AxiosError } from 'axios'
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
  timeout: 120000,  // 2 分钟超时（OCR + LLM 处理需要时间）
  headers: {
    'Content-Type': 'application/json'
  }
})

// Function to set auth token (called from auth composable)
let getAuthToken: (() => Promise<string | null>) | null = null

export function setAuthTokenGetter(getter: () => Promise<string | null>) {
  getAuthToken = getter
}

// Request interceptor to add auth token
api.interceptors.request.use(async (config) => {
  if (getAuthToken) {
    const token = await getAuthToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
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

export interface Report {
  id: string
  creditor_id: string
  task_id: string
  report_type: 'fact_check' | 'legal_diagram' | 'analysis' | 'final'
  file_name: string
  file_path: string
  content_preview?: string
  created_at: string
}

export interface Calculation {
  id: string
  creditor_id: string
  calculation_type: string
  principal: number
  interest: number
  total: number
  parameters: Record<string, unknown>
  created_at: string
}

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
  },

  async getReports(id: string): Promise<{ creditor_id: string; creditor_name: string; reports: Report[] }> {
    try {
      const response = await api.get<{ creditor_id: string; creditor_name: string; reports: Report[] }>(`/creditors/${id}/reports`)
      return response.data
    } catch (error) {
      handleError(error as AxiosError)
    }
  },

  async getCalculations(id: string): Promise<{ creditor_id: string; creditor_name: string; calculations: Calculation[] }> {
    try {
      const response = await api.get<{ creditor_id: string; creditor_name: string; calculations: Calculation[] }>(`/creditors/${id}/calculations`)
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

// ============== Reports API ==============

export const reportsApi = {
  async get(id: string): Promise<Report> {
    try {
      const response = await api.get<Report>(`/reports/${id}`)
      return response.data
    } catch (error) {
      handleError(error as AxiosError)
    }
  },

  async getFullContent(id: string): Promise<string> {
    try {
      const response = await api.get(`/reports/${id}/content`, {
        responseType: 'text'
      })
      return response.data
    } catch (error) {
      handleError(error as AxiosError)
    }
  },

  async downloadContent(id: string): Promise<Blob> {
    try {
      const response = await api.get(`/reports/${id}/content`, {
        params: { download: true },
        responseType: 'blob'
      })
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

// ============== Parse API ==============

export interface ParsedCreditor {
  creditor_name: string
  declared_amount?: number
  source_file: string
  batch_number: number
  creditor_number: number
  confidence: number
}

export interface MaterialParseResponse {
  creditors: ParsedCreditor[]
  confidence: number
  warnings: string[]
  file_count: number
}

// 裁定书解析结果类型
export interface ParsedProjectInfo {
  case_number: string        // 案号
  debtor_name: string        // 债务人名称
  bankruptcy_date: string    // 破产受理日期 (YYYY-MM-DD)
  court_name?: string        // 法院名称
  confidence?: number        // 置信度 0-1
}

export const parseApi = {
  /**
   * 解析上传的债权申报材料，使用 LLM 提取债权人信息
   */
  async parseMaterials(projectId: string, files: File[]): Promise<MaterialParseResponse> {
    const formData = new FormData()
    formData.append('project_id', projectId)

    files.forEach(file => {
      formData.append('files', file)
    })

    try {
      const response = await api.post<MaterialParseResponse>('/parse/materials', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: 120000  // 2 分钟超时（LLM 处理需要时间）
      })
      return response.data
    } catch (error) {
      handleError(error as AxiosError)
    }
  },

  /**
   * 解析裁定书 PDF，提取项目基本信息（单文件）
   */
  async parseRuling(file: File): Promise<ParsedProjectInfo> {
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await api.post<ParsedProjectInfo>('/parse/ruling', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: 60000  // 1 分钟超时
      })
      return response.data
    } catch (error) {
      handleError(error as AxiosError)
    }
  },

  /**
   * 解析多个裁定书 PDF，提取项目基本信息
   */
  async parseRulings(files: File[]): Promise<ParsedProjectInfo> {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files', file)
    })

    try {
      const response = await api.post<ParsedProjectInfo>('/parse/rulings', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: 120000  // 2 分钟超时（多文件处理需要更长时间）
      })
      return response.data
    } catch (error) {
      handleError(error as AxiosError)
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
