<script setup lang="ts">
/**
 * Ruling Upload Component
 *
 * 裁定书上传组件：上传破产裁定书 PDF，使用 LLM 提取项目信息
 * 提取字段：案号、债务人名称、破产受理日期、法院名称
 */
import { ref, computed } from 'vue'
import { Upload, FileText, X, Loader2, Sparkles, CheckCircle, AlertCircle } from 'lucide-vue-next'

// 解析结果类型
export interface ParsedProjectInfo {
  case_number: string        // 案号，如 (2025)沪03破399号
  debtor_name: string        // 债务人名称
  bankruptcy_date: string    // 破产受理日期 (YYYY-MM-DD 格式)
  court_name?: string        // 法院名称
  confidence?: number        // 解析置信度 0-1
}

const emit = defineEmits<{
  (e: 'parsed', info: ParsedProjectInfo): void
  (e: 'cancel'): void
}>()

// 状态
const files = ref<File[]>([])
const isDragging = ref(false)
const isParsing = ref(false)
const parseError = ref<string | null>(null)
const parsedInfo = ref<ParsedProjectInfo | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)

// 计算属性
const hasFiles = computed(() => files.value.length > 0)
const hasParsedInfo = computed(() => parsedInfo.value !== null)

// 格式化文件大小
function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

// 验证文件
function isValidFile(f: File): boolean {
  // 只接受 PDF
  if (f.type === 'application/pdf') return true
  const ext = '.' + f.name.split('.').pop()?.toLowerCase()
  return ext === '.pdf'
}

// 处理拖放
function handleDragOver(e: DragEvent) {
  e.preventDefault()
  isDragging.value = true
}

function handleDragLeave() {
  isDragging.value = false
}

function handleDrop(e: DragEvent) {
  e.preventDefault()
  isDragging.value = false

  const droppedFiles = e.dataTransfer?.files
  if (droppedFiles && droppedFiles.length > 0) {
    addFiles(Array.from(droppedFiles))
  }
}

// 处理文件选择
function handleFileSelect(e: Event) {
  const input = e.target as HTMLInputElement
  const selectedFiles = input.files
  if (selectedFiles && selectedFiles.length > 0) {
    addFiles(Array.from(selectedFiles))
  }
  input.value = ''
}

// 添加文件
function addFiles(newFiles: File[]) {
  parseError.value = null
  parsedInfo.value = null

  const validFiles: File[] = []
  const invalidFiles: string[] = []

  for (const f of newFiles) {
    if (isValidFile(f)) {
      // 检查是否已存在同名文件
      if (!files.value.some(existing => existing.name === f.name)) {
        validFiles.push(f)
      }
    } else {
      invalidFiles.push(f.name)
    }
  }

  if (invalidFiles.length > 0) {
    parseError.value = `以下文件格式不支持: ${invalidFiles.join(', ')}。请上传 PDF 格式文件。`
  }

  if (validFiles.length > 0) {
    files.value = [...files.value, ...validFiles]
  }
}

// 移除单个文件
function removeFile(index: number) {
  files.value = files.value.filter((_, i) => i !== index)
  if (files.value.length === 0) {
    parsedInfo.value = null
  }
}

// 清除所有文件
function clearFiles() {
  files.value = []
  parsedInfo.value = null
  parseError.value = null
}

// 触发文件选择
function triggerFileSelect() {
  fileInputRef.value?.click()
}

// 解析裁定书
async function parseRuling() {
  if (!hasFiles.value || files.value.length === 0) return

  isParsing.value = true
  parseError.value = null

  try {
    const { parseApi } = await import('@/api/client')
    const result = await parseApi.parseRulings(files.value)

    parsedInfo.value = result
  } catch (e) {
    parseError.value = (e as Error).message
  } finally {
    isParsing.value = false
  }
}

// 确认使用解析结果
function confirmParsedInfo() {
  if (parsedInfo.value) {
    emit('parsed', parsedInfo.value)
  }
}

// 格式化日期显示
function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 获取置信度颜色
function getConfidenceColor(confidence?: number): string {
  if (!confidence) return 'text-gray-400'
  if (confidence >= 0.8) return 'text-green-600'
  if (confidence >= 0.5) return 'text-yellow-600'
  return 'text-red-600'
}
</script>

<template>
  <div class="ruling-upload">
    <!-- 上传区域 -->
    <div
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @drop="handleDrop"
      :class="[
        'border-2 border-dashed rounded-xl p-6 text-center transition-all cursor-pointer',
        isDragging
          ? 'border-purple-500 bg-purple-50'
          : 'border-gray-300 hover:border-purple-400 hover:bg-gray-50'
      ]"
      @click="triggerFileSelect"
    >
      <input
        ref="fileInputRef"
        type="file"
        @change="handleFileSelect"
        accept=".pdf"
        multiple
        class="hidden"
      />

      <div class="flex flex-col items-center">
        <div
          :class="[
            'w-14 h-14 rounded-full flex items-center justify-center mb-3',
            isDragging ? 'bg-purple-100' : 'bg-gray-100'
          ]"
        >
          <Upload :class="['w-7 h-7', isDragging ? 'text-purple-600' : 'text-gray-400']" />
        </div>

        <p class="text-gray-700 font-medium">
          {{ isDragging ? '松开鼠标上传文件' : '拖拽裁定书到此处，或点击选择' }}
        </p>
        <p class="text-sm text-gray-500 mt-1">
          支持上传多个 PDF 文件（民事裁定书、决定书等）
        </p>
      </div>
    </div>

    <!-- 已选择的文件列表 -->
    <div v-if="hasFiles" class="mt-4 space-y-2">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm text-gray-600">已选择 {{ files.length }} 个文件</span>
        <button
          v-if="!isParsing"
          @click="clearFiles"
          class="text-sm text-red-500 hover:text-red-600"
        >
          清除全部
        </button>
      </div>

      <div
        v-for="(file, index) in files"
        :key="file.name"
        class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg"
      >
        <FileText class="w-6 h-6 text-purple-500 flex-shrink-0" />
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-700 truncate">{{ file.name }}</p>
          <p class="text-xs text-gray-500">{{ formatSize(file.size) }}</p>
        </div>
        <button
          v-if="!isParsing"
          @click.stop="removeFile(index)"
          class="p-1.5 text-gray-400 hover:text-red-500 transition-colors"
        >
          <X class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- 解析状态和结果区域 -->
    <div v-if="hasFiles" class="mt-4 space-y-4">

      <!-- 解析状态 -->
      <div v-if="isParsing" class="p-6 bg-purple-50 rounded-lg text-center">
        <Loader2 class="w-10 h-10 text-purple-500 animate-spin mx-auto mb-3" />
        <p class="text-purple-700 font-medium">AI 正在解析裁定书...</p>
        <p class="text-sm text-purple-600 mt-1">正在识别文档内容，提取案号、债务人、受理日期等信息</p>
      </div>

      <!-- 解析结果 -->
      <div v-else-if="hasParsedInfo && parsedInfo" class="p-4 bg-green-50 rounded-lg border border-green-200">
        <div class="flex items-center gap-2 mb-4">
          <CheckCircle class="w-5 h-5 text-green-600" />
          <span class="font-medium text-green-800">解析成功</span>
          <span
            v-if="parsedInfo.confidence"
            :class="['text-sm ml-auto', getConfidenceColor(parsedInfo.confidence)]"
          >
            置信度: {{ Math.round((parsedInfo.confidence || 0) * 100) }}%
          </span>
        </div>

        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span class="text-gray-500">案号：</span>
            <span class="text-gray-800 font-medium">{{ parsedInfo.case_number || '-' }}</span>
          </div>
          <div>
            <span class="text-gray-500">债务人：</span>
            <span class="text-gray-800 font-medium">{{ parsedInfo.debtor_name || '-' }}</span>
          </div>
          <div>
            <span class="text-gray-500">受理日期：</span>
            <span class="text-gray-800 font-medium">{{ formatDate(parsedInfo.bankruptcy_date) }}</span>
          </div>
          <div>
            <span class="text-gray-500">法院：</span>
            <span class="text-gray-800 font-medium">{{ parsedInfo.court_name || '-' }}</span>
          </div>
        </div>
      </div>

      <!-- 未解析提示 -->
      <div v-else-if="!parseError" class="p-4 bg-blue-50 rounded-lg border border-blue-200">
        <div class="flex items-center gap-2">
          <Sparkles class="w-5 h-5 text-blue-600" />
          <span class="text-blue-800">点击下方按钮，AI 将自动识别并提取裁定书中的项目信息</span>
        </div>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="parseError" class="mt-4 p-4 bg-red-50 rounded-lg border border-red-200">
      <div class="flex items-center gap-2">
        <AlertCircle class="w-5 h-5 text-red-600 flex-shrink-0" />
        <span class="text-red-700">{{ parseError }}</span>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="flex justify-end gap-3 mt-6">
      <button
        @click="emit('cancel')"
        class="px-6 py-2.5 text-gray-600 hover:text-gray-800 transition-colors"
      >
        取消
      </button>

      <!-- 解析按钮 -->
      <button
        v-if="hasFiles && !hasParsedInfo"
        @click="parseRuling"
        :disabled="isParsing"
        :class="[
          'flex items-center gap-2 px-6 py-2.5 rounded-lg font-medium transition-all',
          isParsing
            ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
            : 'bg-purple-500 text-white hover:bg-purple-600'
        ]"
      >
        <Loader2 v-if="isParsing" class="w-5 h-5 animate-spin" />
        <Sparkles v-else class="w-5 h-5" />
        {{ isParsing ? '解析中...' : '开始智能解析' }}
      </button>

      <!-- 确认使用按钮 -->
      <button
        v-if="hasParsedInfo"
        @click="confirmParsedInfo"
        class="flex items-center gap-2 px-6 py-2.5 bg-green-500 text-white rounded-lg font-medium hover:bg-green-600 transition-all"
      >
        <CheckCircle class="w-5 h-5" />
        使用此信息
      </button>
    </div>
  </div>
</template>
