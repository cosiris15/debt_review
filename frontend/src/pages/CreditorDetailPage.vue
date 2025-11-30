<script setup lang="ts">
/**
 * Creditor Detail Page
 *
 * Shows creditor info, processing status, reports, and calculations.
 * Supports Markdown rendering with Mermaid diagrams.
 */
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { creditorsApi, reportsApi, type Report, type Calculation } from '@/api/client'
import type { Creditor } from '@/types'
import { CreditorStatus, STAGE_LABELS } from '@/types'
import { FileText, Calculator, ArrowLeft, Download, Eye, Clock, CheckCircle, XCircle, Loader, X, GitBranch } from 'lucide-vue-next'
import MarkdownViewer from '@/components/MarkdownViewer.vue'

const route = useRoute()
const router = useRouter()

const projectId = route.params.projectId as string
const creditorId = route.params.creditorId as string

// State
const creditor = ref<Creditor | null>(null)
const reports = ref<Report[]>([])
const calculations = ref<Calculation[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const activeTab = ref<'reports' | 'calculations'>('reports')

// Default status config
const defaultStatusConfig = { icon: Clock, class: 'text-gray-500 bg-gray-100', label: '未知' }

// Computed
const statusConfig = computed(() => {
  if (!creditor.value) return defaultStatusConfig

  const configs: Record<string, { icon: typeof Clock, class: string, label: string }> = {
    [CreditorStatus.NOT_STARTED]: { icon: Clock, class: 'text-gray-500 bg-gray-100', label: '待处理' },
    [CreditorStatus.IN_PROGRESS]: { icon: Loader, class: 'text-blue-600 bg-blue-100', label: '处理中' },
    [CreditorStatus.COMPLETED]: { icon: CheckCircle, class: 'text-green-600 bg-green-100', label: '已完成' },
    [CreditorStatus.FAILED]: { icon: XCircle, class: 'text-red-600 bg-red-100', label: '失败' }
  }

  return configs[creditor.value.status] || defaultStatusConfig
})

const reportTypeLabels: Record<string, string> = {
  fact_check: '事实核查报告',
  legal_diagram: '法律关系图',
  analysis: '债权分析报告',
  final: '审查意见表'
}

// 报告图标
const reportTypeIcons: Record<string, typeof FileText> = {
  fact_check: FileText,
  legal_diagram: GitBranch,
  analysis: FileText,
  final: FileText
}

// 全屏查看状态
const viewingReport = ref<Report | null>(null)
const reportFullContent = ref<string>('')
const loadingContent = ref(false)

// Methods
async function fetchData() {
  loading.value = true
  error.value = null

  try {
    // Fetch creditor details
    creditor.value = await creditorsApi.get(creditorId)

    // Fetch reports and calculations in parallel
    const [reportsData, calcData] = await Promise.all([
      creditorsApi.getReports(creditorId),
      creditorsApi.getCalculations(creditorId)
    ])

    reports.value = reportsData.reports
    calculations.value = calcData.calculations
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    loading.value = false
  }
}

function formatAmount(amount?: number): string {
  if (amount === undefined || amount === null) return '-'
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 2
  }).format(amount)
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 打开报告全屏预览
async function openReportViewer(report: Report) {
  viewingReport.value = report
  loadingContent.value = true
  reportFullContent.value = ''

  try {
    const content = await reportsApi.getFullContent(report.id)
    reportFullContent.value = content
  } catch (e) {
    console.error('Failed to load report content:', e)
    // 回退到预览内容
    reportFullContent.value = report.content_preview || '无法加载报告内容'
  } finally {
    loadingContent.value = false
  }
}

// 关闭报告预览
function closeReportViewer() {
  viewingReport.value = null
  reportFullContent.value = ''
}

function goBack() {
  router.push(`/projects/${projectId}`)
}

// Download report
async function downloadReport(report: Report) {
  try {
    const blob = await reportsApi.downloadContent(report.id)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = report.file_name
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  } catch (e) {
    console.error('Download failed:', e)
    // If download fails, try showing content preview
    if (report.content_preview) {
      const blob = new Blob([report.content_preview], { type: 'text/markdown' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = report.file_name
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    }
  }
}

onMounted(() => {
  fetchData()
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
      <button @click="goBack" class="ml-4 underline">返回</button>
    </div>

    <!-- Content -->
    <div v-else-if="creditor">
      <!-- Header -->
      <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
        <button
          @click="goBack"
          class="flex items-center gap-2 text-gray-500 hover:text-gray-700 mb-4"
        >
          <ArrowLeft class="w-4 h-4" />
          返回项目详情
        </button>

        <div class="flex items-start justify-between">
          <div>
            <div class="flex items-center gap-3">
              <h1 class="text-2xl font-bold text-gray-800">{{ creditor.creditor_name }}</h1>
              <span
                :class="[
                  'px-3 py-1 rounded-full text-sm font-medium flex items-center gap-1',
                  statusConfig.class
                ]"
              >
                <component :is="statusConfig.icon" class="w-4 h-4" />
                {{ statusConfig.label }}
              </span>
            </div>
            <p class="text-gray-500 mt-1">
              第 {{ creditor.batch_number }} 批 · 编号 {{ creditor.creditor_number }}
            </p>
          </div>

          <div v-if="creditor.current_stage" class="text-right">
            <div class="text-sm text-gray-500">当前阶段</div>
            <div class="font-semibold text-gray-800">
              {{ STAGE_LABELS[creditor.current_stage] || creditor.current_stage }}
            </div>
          </div>
        </div>

        <!-- Amount Summary -->
        <div class="grid grid-cols-3 gap-6 mt-6 pt-6 border-t">
          <div>
            <div class="text-sm text-gray-500">申报金额</div>
            <div class="text-xl font-bold text-gray-800">
              {{ formatAmount(creditor.declared_amount) }}
            </div>
          </div>
          <div>
            <div class="text-sm text-gray-500">确认金额</div>
            <div class="text-xl font-bold text-green-600">
              {{ formatAmount(creditor.confirmed_amount) }}
            </div>
          </div>
          <div>
            <div class="text-sm text-gray-500">差异金额</div>
            <div class="text-xl font-bold" :class="creditor.declared_amount && creditor.confirmed_amount
              ? (creditor.declared_amount - creditor.confirmed_amount > 0 ? 'text-red-600' : 'text-gray-800')
              : 'text-gray-400'">
              {{ creditor.declared_amount && creditor.confirmed_amount
                ? formatAmount(creditor.declared_amount - creditor.confirmed_amount)
                : '-' }}
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="bg-white rounded-xl shadow-sm overflow-hidden">
        <div class="flex border-b">
          <button
            @click="activeTab = 'reports'"
            :class="[
              'flex-1 py-4 text-center font-medium transition-colors flex items-center justify-center gap-2',
              activeTab === 'reports'
                ? 'text-primary-600 border-b-2 border-primary-500 bg-primary-50/50'
                : 'text-gray-500 hover:text-gray-700'
            ]"
          >
            <FileText class="w-5 h-5" />
            审查报告 ({{ reports.length }})
          </button>
          <button
            @click="activeTab = 'calculations'"
            :class="[
              'flex-1 py-4 text-center font-medium transition-colors flex items-center justify-center gap-2',
              activeTab === 'calculations'
                ? 'text-primary-600 border-b-2 border-primary-500 bg-primary-50/50'
                : 'text-gray-500 hover:text-gray-700'
            ]"
          >
            <Calculator class="w-5 h-5" />
            利息计算 ({{ calculations.length }})
          </button>
        </div>

        <!-- Reports Tab -->
        <div v-if="activeTab === 'reports'" class="p-6">
          <div v-if="reports.length === 0" class="text-center py-12 text-gray-500">
            <FileText class="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>暂无审查报告</p>
            <p class="text-sm mt-1">处理完成后将显示报告</p>
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="report in reports"
              :key="report.id"
              class="border border-slate-200 rounded-lg overflow-hidden hover:border-blue-300 transition-colors"
            >
              <div
                @click="openReportViewer(report)"
                class="flex items-center justify-between p-4 cursor-pointer hover:bg-slate-50"
              >
                <div class="flex items-center gap-3">
                  <div :class="[
                    'w-10 h-10 rounded-lg flex items-center justify-center',
                    report.report_type === 'legal_diagram' ? 'bg-purple-100' : 'bg-blue-100'
                  ]">
                    <component
                      :is="reportTypeIcons[report.report_type] || FileText"
                      :class="[
                        'w-5 h-5',
                        report.report_type === 'legal_diagram' ? 'text-purple-600' : 'text-blue-600'
                      ]"
                    />
                  </div>
                  <div>
                    <h4 class="font-medium text-slate-800">
                      {{ reportTypeLabels[report.report_type] || report.report_type }}
                    </h4>
                    <p class="text-sm text-slate-500">{{ report.file_name }}</p>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-xs text-slate-400">{{ formatDate(report.created_at) }}</span>
                  <button
                    @click.stop="openReportViewer(report)"
                    class="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="查看完整内容"
                  >
                    <Eye class="w-5 h-5" />
                  </button>
                  <button
                    @click.stop="downloadReport(report)"
                    class="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="下载"
                  >
                    <Download class="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Calculations Tab -->
        <div v-if="activeTab === 'calculations'" class="p-6">
          <div v-if="calculations.length === 0" class="text-center py-12 text-gray-500">
            <Calculator class="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>暂无计算记录</p>
            <p class="text-sm mt-1">Agent分析时会自动调用计算器</p>
          </div>

          <div v-else class="overflow-x-auto">
            <table class="w-full">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-sm font-medium text-gray-700">计算类型</th>
                  <th class="px-4 py-3 text-right text-sm font-medium text-gray-700">本金</th>
                  <th class="px-4 py-3 text-right text-sm font-medium text-gray-700">利息</th>
                  <th class="px-4 py-3 text-right text-sm font-medium text-gray-700">合计</th>
                  <th class="px-4 py-3 text-left text-sm font-medium text-gray-700">时间</th>
                </tr>
              </thead>
              <tbody class="divide-y">
                <tr v-for="calc in calculations" :key="calc.id" class="hover:bg-gray-50">
                  <td class="px-4 py-3">
                    <span class="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm">
                      {{ calc.calculation_type }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-right text-gray-800">{{ formatAmount(calc.principal) }}</td>
                  <td class="px-4 py-3 text-right text-gray-800">{{ formatAmount(calc.interest) }}</td>
                  <td class="px-4 py-3 text-right font-medium text-gray-800">{{ formatAmount(calc.total) }}</td>
                  <td class="px-4 py-3 text-sm text-gray-500">{{ formatDate(calc.created_at) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- 报告预览弹窗 -->
    <div
      v-if="viewingReport"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      @click.self="closeReportViewer"
    >
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-5xl max-h-[90vh] flex flex-col overflow-hidden">
        <!-- 弹窗头部 -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-slate-50">
          <div class="flex items-center gap-3">
            <div :class="[
              'w-10 h-10 rounded-lg flex items-center justify-center',
              viewingReport.report_type === 'legal_diagram' ? 'bg-purple-100' : 'bg-blue-100'
            ]">
              <component
                :is="reportTypeIcons[viewingReport.report_type] || FileText"
                :class="[
                  'w-5 h-5',
                  viewingReport.report_type === 'legal_diagram' ? 'text-purple-600' : 'text-blue-600'
                ]"
              />
            </div>
            <div>
              <h3 class="font-semibold text-slate-800">
                {{ reportTypeLabels[viewingReport.report_type] || viewingReport.report_type }}
              </h3>
              <p class="text-sm text-slate-500">{{ viewingReport.file_name }}</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="downloadReport(viewingReport)"
              class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            >
              <Download class="w-4 h-4" />
              下载
            </button>
            <button
              @click="closeReportViewer"
              class="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
            >
              <X class="w-5 h-5" />
            </button>
          </div>
        </div>

        <!-- 弹窗内容 -->
        <div class="flex-1 overflow-hidden">
          <!-- 加载中 -->
          <div v-if="loadingContent" class="flex items-center justify-center h-64">
            <Loader class="w-8 h-8 text-blue-500 animate-spin" />
          </div>

          <!-- Markdown 渲染 -->
          <div v-else class="h-full overflow-auto">
            <MarkdownViewer
              :content="reportFullContent"
              :title="reportTypeLabels[viewingReport.report_type]"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
