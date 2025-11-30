/**
 * TypeScript type definitions for the Debt Review System
 */

// ============== Enums ==============

export const TaskStatus = {
  PENDING: 'pending',
  RUNNING: 'running',
  COMPLETED: 'completed',
  FAILED: 'failed',
  CANCELLED: 'cancelled'
} as const
export type TaskStatus = typeof TaskStatus[keyof typeof TaskStatus]

export const TaskStage = {
  INIT: 'init',
  FACT_CHECK: 'fact_check',
  LEGAL_DIAGRAM: 'legal_diagram',  // 新增：法律关系图生成
  ANALYSIS: 'analysis',
  REPORT: 'report',
  VALIDATION: 'validation',
  COMPLETE: 'complete',
  ERROR: 'error'  // 新增：错误状态
} as const
export type TaskStage = typeof TaskStage[keyof typeof TaskStage]

export const CreditorStatus = {
  NOT_STARTED: 'not_started',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  FAILED: 'failed'
} as const
export type CreditorStatus = typeof CreditorStatus[keyof typeof CreditorStatus]

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
  calculation_type: 'simple' | 'lpr' | 'delay' | 'compound' | 'penalty' | 'share_ratio' | 'confirmed' | 'max_limit'
  // 原有字段（利息计算）
  principal?: number
  start_date?: string
  end_date?: string
  rate?: number
  multiplier?: number
  lpr_term?: '1y' | '5y'
  // 新增字段（份额计算 share_ratio）
  total_amount?: number
  share_ratio?: number
  // 新增字段（最高额封顶 max_limit）
  calculated_total?: number
  max_limit?: number
  // 新增字段（判决确认金额 confirmed）
  confirmed_amount?: number
  source?: string
  // 通用字段
  description?: string
}

export interface CalculationPeriod {
  start: string
  end: string
  days: number
  interest: number
  effective_rate: number
}

export interface InterestCalculationResponse {
  principal: number
  interest: number
  total: number
  days: number
  rate_used: number
  calculation_details: {
    periods?: CalculationPeriod[]
    [key: string]: unknown
  }
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
  [TaskStage.LEGAL_DIAGRAM]: '法律关系图',  // 新增
  [TaskStage.ANALYSIS]: '债权分析',
  [TaskStage.REPORT]: '报告生成',
  [TaskStage.VALIDATION]: '质量验证',
  [TaskStage.COMPLETE]: '完成',
  [TaskStage.ERROR]: '错误'  // 新增
}

// 新增：向后兼容的阶段显示函数
// 如果收到未知阶段，显示原始值并标记为未知（醒目样式）
export function getStageLabelSafe(stage: string): { label: string; isUnknown: boolean } {
  const knownStages = Object.values(TaskStage) as string[]
  if (knownStages.includes(stage)) {
    return { label: STAGE_LABELS[stage as TaskStage], isUnknown: false }
  }
  // 未知阶段：返回原始值，标记为未知
  return { label: stage, isUnknown: true }
}

// 新增：未知阶段的醒目样式（灰底红字+警告图标）
export const UNKNOWN_STAGE_STYLE = 'bg-gray-200 text-red-600 border border-red-300'

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
