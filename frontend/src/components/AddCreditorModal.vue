<script setup lang="ts">
/**
 * Add Creditor Modal
 *
 * 统一的添加债权人弹窗，支持两种模式：
 * 1. 智能识别：上传材料后 AI 自动识别债权人名称
 * 2. 手动输入：用户手动填写债权人名称，材料可选上传
 */
import { ref, computed } from 'vue'
import { X, Plus, Trash2, Upload, Sparkles, FileText, Loader2, AlertCircle, CheckCircle } from 'lucide-vue-next'
import { useProjectStore } from '@/stores/project'
import { storeToRefs } from 'pinia'
import type { CreditorCreate } from '@/types'

// 生成唯一 ID
function generateId(): string {
  return Math.random().toString(36).substring(2, 9)
}

const props = defineProps<{
  projectId: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'success', count: number): void
}>()

const projectStore = useProjectStore()
const { batchNumbers } = storeToRefs(projectStore)

// ============== 类型定义 ==============

interface CreditorRow {
  id: string
  name: string
  files: File[]
  // 解析状态
  parseStatus: 'pending' | 'parsing' | 'success' | 'error'
  parsedName?: string
  parsedAmount?: number
  parseError?: string
  confidence?: number
}

type Mode = 'smart' | 'manual'
type Step = 'input' | 'preview'

// ============== 状态 ==============

const mode = ref<Mode>('smart')
const step = ref<Step>('input')
const isSubmitting = ref(false)
const submitError = ref<string | null>(null)

// 债权人行列表
const rows = ref<CreditorRow[]>([
  { id: generateId(), name: '', files: [], parseStatus: 'pending' }
])

// ============== 计算属性 ==============

const canSubmit = computed(() => {
  if (mode.value === 'smart') {
    // 智能模式：至少有一行上传了文件
    return rows.value.some(r => r.files.length > 0)
  } else {
    // 手动模式：至少有一行填写了名称
    return rows.value.some(r => r.name.trim())
  }
})

const submitButtonText = computed(() => {
  if (mode.value === 'smart') {
    if (step.value === 'input') return '开始解析'
    return '确认创建'
  }
  return '创建债权人'
})

// ============== 行操作 ==============

function addRow() {
  rows.value.push({
    id: generateId(),
    name: '',
    files: [],
    parseStatus: 'pending'
  })
}

function removeRow(id: string) {
  if (rows.value.length > 1) {
    rows.value = rows.value.filter(r => r.id !== id)
  }
}

// ============== 文件操作 ==============

function handleFileDrop(rowId: string, e: DragEvent) {
  e.preventDefault()
  const droppedFiles = e.dataTransfer?.files
  if (droppedFiles) {
    addFilesToRow(rowId, Array.from(droppedFiles))
  }
}

function handleFileSelect(rowId: string, e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files) {
    addFilesToRow(rowId, Array.from(input.files))
  }
  input.value = ''
}

function addFilesToRow(rowId: string, newFiles: File[]) {
  const row = rows.value.find(r => r.id === rowId)
  if (!row) return

  // 过滤支持的文件类型
  const validExtensions = ['.pdf', '.jpg', '.jpeg', '.png', '.webp', '.docx', '.xlsx']
  const validFiles = newFiles.filter(f => {
    const ext = '.' + f.name.split('.').pop()?.toLowerCase()
    return validExtensions.includes(ext)
  })

  row.files = [...row.files, ...validFiles]
  row.parseStatus = 'pending'
}

function removeFile(rowId: string, fileIndex: number) {
  const row = rows.value.find(r => r.id === rowId)
  if (row) {
    row.files = row.files.filter((_, i) => i !== fileIndex)
  }
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

// ============== 模式切换 ==============

function switchMode(newMode: Mode) {
  if (mode.value !== newMode) {
    mode.value = newMode
    step.value = 'input'
    // 重置解析状态
    rows.value.forEach(r => {
      r.parseStatus = 'pending'
      r.parsedName = undefined
      r.parsedAmount = undefined
      r.parseError = undefined
    })
  }
}

// ============== 提交处理 ==============

async function handleSubmit() {
  submitError.value = null

  if (mode.value === 'smart') {
    if (step.value === 'input') {
      // 智能模式第一步：解析
      await parseAllRows()
    } else {
      // 智能模式第二步：创建
      await createCreditors()
    }
  } else {
    // 手动模式：直接创建
    await createCreditors()
  }
}

// 解析所有行
async function parseAllRows() {
  const rowsWithFiles = rows.value.filter(r => r.files.length > 0)
  if (rowsWithFiles.length === 0) {
    submitError.value = '请至少为一个债权人上传材料'
    return
  }

  isSubmitting.value = true

  try {
    // 逐个解析
    for (const row of rowsWithFiles) {
      row.parseStatus = 'parsing'

      try {
        const result = await parseCreditorMaterials(row.files)
        row.parsedName = result.creditor_name
        row.parsedAmount = result.declared_amount
        row.confidence = result.confidence
        row.parseStatus = 'success'
      } catch (e) {
        row.parseError = (e as Error).message
        row.parseStatus = 'error'
      }
    }

    // 进入预览步骤
    step.value = 'preview'
  } finally {
    isSubmitting.value = false
  }
}

// 调用解析 API
async function parseCreditorMaterials(files: File[]): Promise<{
  creditor_name: string
  declared_amount?: number
  confidence: number
}> {
  const { parseApi } = await import('@/api/client')
  const result = await parseApi.parseMaterials(props.projectId, files)

  if (result.creditors.length === 0) {
    throw new Error('未能识别出债权人信息')
  }

  // 返回第一个识别出的债权人
  const creditor = result.creditors[0]!
  return {
    creditor_name: creditor.creditor_name,
    declared_amount: creditor.declared_amount,
    confidence: creditor.confidence ?? result.confidence
  }
}

// 创建债权人
async function createCreditors() {
  isSubmitting.value = true
  submitError.value = null

  try {
    // 计算新批次号
    const newBatchNumber = batchNumbers.value.length > 0
      ? Math.max(...batchNumbers.value) + 1
      : 1

    let successCount = 0
    const errors: string[] = []

    // 根据模式获取要创建的债权人
    const creditorRows = mode.value === 'smart'
      ? rows.value.filter(r => r.parseStatus === 'success')
      : rows.value.filter(r => r.name.trim())

    for (let i = 0; i < creditorRows.length; i++) {
      const row = creditorRows[i]
      if (!row) continue

      const creditorName = mode.value === 'smart'
        ? (row.parsedName || row.name)
        : row.name

      try {
        const data: CreditorCreate = {
          project_id: props.projectId,
          batch_number: newBatchNumber,
          creditor_number: i + 1,
          creditor_name: creditorName.trim(),
          declared_amount: mode.value === 'smart' ? row.parsedAmount : undefined
        }

        await projectStore.createCreditor(data)
        successCount++
      } catch (e) {
        errors.push(`${creditorName}: ${(e as Error).message}`)
      }
    }

    if (errors.length > 0) {
      console.error('创建失败的债权人:', errors)
    }

    if (successCount > 0) {
      emit('success', successCount)
      emit('close')
    } else {
      submitError.value = '所有债权人创建失败，请重试'
    }
  } finally {
    isSubmitting.value = false
  }
}

// 返回上一步
function goBack() {
  step.value = 'input'
}
</script>

<template>
  <!-- Modal Backdrop -->
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
    <!-- Modal Content -->
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl mx-4 max-h-[90vh] flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between p-5 border-b flex-shrink-0">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
            <Plus class="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <h3 class="text-lg font-semibold text-gray-800">添加债权人</h3>
            <p class="text-sm text-gray-500">
              {{ mode === 'smart' ? '上传材料，AI 自动识别' : '手动输入债权人信息' }}
            </p>
          </div>
        </div>
        <button
          @click="emit('close')"
          class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Mode Tabs -->
      <div class="px-5 py-3 border-b bg-gray-50 flex-shrink-0">
        <div class="flex gap-2">
          <button
            @click="switchMode('smart')"
            :class="[
              'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all',
              mode === 'smart'
                ? 'bg-primary-500 text-white shadow-sm'
                : 'bg-white text-gray-600 hover:bg-gray-100 border'
            ]"
          >
            <Sparkles class="w-4 h-4" />
            智能识别
          </button>
          <button
            @click="switchMode('manual')"
            :class="[
              'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all',
              mode === 'manual'
                ? 'bg-primary-500 text-white shadow-sm'
                : 'bg-white text-gray-600 hover:bg-gray-100 border'
            ]"
          >
            <FileText class="w-4 h-4" />
            手动输入
          </button>
        </div>
        <p class="text-xs text-gray-500 mt-2">
          {{ mode === 'smart'
            ? '上传材料后，系统将自动识别债权人名称和申报金额'
            : '手动填写债权人名称，材料可选择上传'
          }}
        </p>
      </div>

      <!-- Content -->
      <div class="p-5 overflow-y-auto flex-1 space-y-4">
        <!-- Error Message -->
        <div v-if="submitError" class="p-4 bg-red-50 text-red-700 rounded-lg text-sm flex items-center gap-2">
          <AlertCircle class="w-5 h-5 flex-shrink-0" />
          {{ submitError }}
        </div>

        <!-- Creditor Rows -->
        <div
          v-for="(row, index) in rows"
          :key="row.id"
          class="border rounded-xl p-4 space-y-3"
          :class="{
            'border-green-300 bg-green-50/50': row.parseStatus === 'success',
            'border-red-300 bg-red-50/50': row.parseStatus === 'error',
            'border-blue-300 bg-blue-50/50': row.parseStatus === 'parsing'
          }"
        >
          <!-- Row Header -->
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium text-gray-700">
              债权人 {{ index + 1 }}
              <span v-if="row.parseStatus === 'success'" class="text-green-600 ml-2">
                <CheckCircle class="w-4 h-4 inline" /> 已识别
              </span>
              <span v-if="row.parseStatus === 'parsing'" class="text-blue-600 ml-2">
                <Loader2 class="w-4 h-4 inline animate-spin" /> 解析中...
              </span>
              <span v-if="row.parseStatus === 'error'" class="text-red-600 ml-2">
                <AlertCircle class="w-4 h-4 inline" /> 解析失败
              </span>
            </span>
            <button
              v-if="rows.length > 1"
              @click="removeRow(row.id)"
              class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors"
            >
              <Trash2 class="w-4 h-4" />
            </button>
          </div>

          <!-- Name Input (Manual mode or Preview) -->
          <div v-if="mode === 'manual' || step === 'preview'">
            <label class="block text-sm text-gray-600 mb-1">债权人名称</label>
            <input
              v-if="mode === 'manual'"
              v-model="row.name"
              type="text"
              placeholder="请输入债权人名称"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
            />
            <input
              v-else
              v-model="row.parsedName"
              type="text"
              :placeholder="row.parseStatus === 'error' ? '请手动输入' : ''"
              class="w-full px-3 py-2 border rounded-lg outline-none"
              :class="row.parseStatus === 'error'
                ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
                : 'border-gray-300 focus:ring-primary-500 focus:border-primary-500'"
            />
          </div>

          <!-- Amount (Preview only) -->
          <div v-if="step === 'preview' && row.parsedAmount !== undefined">
            <label class="block text-sm text-gray-600 mb-1">申报金额</label>
            <input
              v-model.number="row.parsedAmount"
              type="number"
              step="0.01"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
            />
          </div>

          <!-- File Upload Zone -->
          <div
            @drop.prevent="handleFileDrop(row.id, $event)"
            @dragover.prevent
            @dragenter.prevent
            :class="[
              'border-2 border-dashed rounded-lg p-4 transition-colors cursor-pointer',
              row.files.length > 0
                ? 'border-gray-200 bg-gray-50'
                : 'border-gray-300 hover:border-primary-400 hover:bg-primary-50/30'
            ]"
            @click="($refs[`fileInput-${row.id}`] as HTMLInputElement)?.click()"
          >
            <input
              :ref="`fileInput-${row.id}`"
              type="file"
              multiple
              accept=".pdf,.jpg,.jpeg,.png,.webp,.docx,.xlsx"
              class="hidden"
              @change="handleFileSelect(row.id, $event)"
            />

            <!-- Uploaded Files -->
            <div v-if="row.files.length > 0" class="space-y-2">
              <div
                v-for="(file, fileIndex) in row.files"
                :key="fileIndex"
                class="flex items-center gap-2 bg-white rounded-lg px-3 py-2 border"
                @click.stop
              >
                <FileText class="w-4 h-4 text-gray-400 flex-shrink-0" />
                <span class="flex-1 text-sm text-gray-700 truncate">{{ file.name }}</span>
                <span class="text-xs text-gray-400">{{ formatFileSize(file.size) }}</span>
                <button
                  @click.stop="removeFile(row.id, fileIndex)"
                  class="p-1 text-gray-400 hover:text-red-500 transition-colors"
                >
                  <X class="w-3 h-3" />
                </button>
              </div>
              <p class="text-xs text-gray-500 text-center mt-2">
                点击或拖入更多文件
              </p>
            </div>

            <!-- Empty State -->
            <div v-else class="text-center py-4">
              <Upload class="w-8 h-8 text-gray-400 mx-auto mb-2" />
              <p class="text-sm text-gray-600">
                {{ mode === 'smart' ? '拖入或点击上传材料' : '可选：上传申报材料' }}
              </p>
              <p class="text-xs text-gray-400 mt-1">
                支持 PDF、图片、Word、Excel
              </p>
            </div>
          </div>

          <!-- Parse Error -->
          <div v-if="row.parseError" class="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">
            {{ row.parseError }}
          </div>

          <!-- Confidence -->
          <div v-if="row.confidence !== undefined && row.confidence < 0.8" class="text-sm text-amber-600 bg-amber-50 rounded-lg px-3 py-2">
            置信度较低 ({{ (row.confidence * 100).toFixed(0) }}%)，请确认信息是否正确
          </div>
        </div>

        <!-- Add Row Button -->
        <button
          @click="addRow"
          class="w-full py-3 border-2 border-dashed border-gray-300 rounded-xl text-gray-500 hover:border-primary-400 hover:text-primary-600 hover:bg-primary-50/30 transition-colors flex items-center justify-center gap-2"
        >
          <Plus class="w-5 h-5" />
          添加债权人
        </button>
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-between p-5 border-t bg-gray-50 flex-shrink-0">
        <div class="text-sm text-gray-500">
          共 {{ rows.length }} 个债权人
          <span v-if="mode === 'smart' && step === 'preview'">
            ，{{ rows.filter(r => r.parseStatus === 'success').length }} 个识别成功
          </span>
        </div>
        <div class="flex gap-3">
          <button
            v-if="step === 'preview'"
            @click="goBack"
            class="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            返回修改
          </button>
          <button
            @click="emit('close')"
            class="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            取消
          </button>
          <button
            @click="handleSubmit"
            :disabled="!canSubmit || isSubmitting"
            :class="[
              'flex items-center gap-2 px-6 py-2 rounded-lg font-medium transition-all',
              canSubmit && !isSubmitting
                ? 'bg-primary-500 text-white hover:bg-primary-600'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            ]"
          >
            <Loader2 v-if="isSubmitting" class="w-4 h-4 animate-spin" />
            <Sparkles v-else-if="mode === 'smart' && step === 'input'" class="w-4 h-4" />
            {{ isSubmitting ? '处理中...' : submitButtonText }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
