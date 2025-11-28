/**
 * TypeScript type definitions for the Debt Review System
 */

// ============== Enums ==============

export enum TaskStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

export enum TaskStage {
  INIT = 'init',
  FACT_CHECK = 'fact_check',
  ANALYSIS = 'analysis',
  REPORT = 'report',
  VALIDATION = 'validation',
  COMPLETE = 'complete'
}

export enum CreditorStatus {
  NOT_STARTED = 'not_started',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

// ============== Project ==============

export interface Project {
  id: string
  name: string
  debtor_name: string
  bankruptcy_date: string
  interest_stop_date: string
  description?: string
  created_at: string
  updated_at: string
  total_creditors: number
  completed_creditors: number
}

export interface ProjectCreate {
  name: string
  debtor_name: string
  bankruptcy_date: string
  description?: string
}

// ============== Creditor ==============

export interface Creditor {
  id: string
  project_id: string
  batch_number: number
  creditor_number: number
  creditor_name: string
  declared_amount?: number
  confirmed_amount?: number
  status: CreditorStatus
  current_stage?: TaskStage
  materials_path?: string
  output_path?: string
  created_at: string
  updated_at: string
}

export interface CreditorCreate {
  project_id: string
  batch_number: number
  creditor_number: number
  creditor_name: string
  declared_amount?: number
  materials_path?: string
}

// ============== Task ==============

export interface Task {
  id: string
  project_id: string
  status: TaskStatus
  current_stage: TaskStage
  progress_percent: number
  creditors_total: number
  creditors_completed: number
  started_at?: string
  completed_at?: string
  error_message?: string
  created_at: string
}

export interface TaskCreate {
  project_id: string
  creditor_ids: string[]
  processing_mode?: 'auto' | 'serial' | 'parallel'
}

export interface TaskSubmitResponse {
  task_id: string
  message: string
  status: TaskStatus
}

export interface TaskProgress {
  task_id: string
  status: TaskStatus
  current_stage: TaskStage
  progress_percent: number
  current_creditor?: string
  stage_details?: {
    creditors_total: number
    creditors_completed: number
  }
  logs: string[]
}

export interface TaskLog {
  id: string
  task_id: string
  creditor_id?: string
  stage?: string
  level: 'debug' | 'info' | 'warning' | 'error'
  message: string
  details?: Record<string, unknown>
  created_at: string
}

// ============== Calculation ==============

export interface InterestCalculationRequest {
  calculation_type: 'simple' | 'lpr' | 'delay' | 'compound' | 'penalty'
  principal: number
  start_date: string
  end_date: string
  rate?: number
  multiplier?: number
  lpr_term?: '1y' | '5y'
}

export interface InterestCalculationResponse {
  principal: number
  interest: number
  total: number
  days: number
  rate_used: number
  calculation_details: Record<string, unknown>
}

// ============== API Response ==============

export interface ApiResponse<T> {
  data: T
  error?: string
}

// ============== UI Helpers ==============

export const STAGE_LABELS: Record<TaskStage, string> = {
  [TaskStage.INIT]: '初始化',
  [TaskStage.FACT_CHECK]: '事实核查',
  [TaskStage.ANALYSIS]: '债权分析',
  [TaskStage.REPORT]: '报告生成',
  [TaskStage.VALIDATION]: '质量验证',
  [TaskStage.COMPLETE]: '完成'
}

export const STATUS_LABELS: Record<TaskStatus, string> = {
  [TaskStatus.PENDING]: '等待中',
  [TaskStatus.RUNNING]: '运行中',
  [TaskStatus.COMPLETED]: '已完成',
  [TaskStatus.FAILED]: '失败',
  [TaskStatus.CANCELLED]: '已取消'
}

export const STATUS_COLORS: Record<TaskStatus, string> = {
  [TaskStatus.PENDING]: 'bg-gray-100 text-gray-800',
  [TaskStatus.RUNNING]: 'bg-blue-100 text-blue-800',
  [TaskStatus.COMPLETED]: 'bg-green-100 text-green-800',
  [TaskStatus.FAILED]: 'bg-red-100 text-red-800',
  [TaskStatus.CANCELLED]: 'bg-yellow-100 text-yellow-800'
}
