<script setup lang="ts">
/**
 * Material Upload Component
 *
 * 智能材料上传组件：支持拖拽上传多种格式文件
 * 使用阿里云 qwen-vl-ocr 进行 OCR（支持手写体），再由 LLM 提取结构化信息
 */
import { ref, computed } from 'vue'
import { Upload, FileText, Image, X, Loader2, Sparkles, FileSpreadsheet } from 'lucide-vue-next'

const props = defineProps<{
  projectId: string
}>()

const emit = defineEmits<{
  (e: 'parsed', creditors: ParsedCreditor[]): void
  (e: 'cancel'): void
}>()

// 解析结果类型
interface ParsedCreditor {
  creditor_name: string
  declared_amount?: number
  source_file: string
  batch_number?: number
  creditor_number?: number
}

// 状态
const files = ref<File[]>([])
const isDragging = ref(false)
const isParsing = ref(false)
const parseError = ref<string | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)

// 支持的文件类型
const SUPPORTED_TYPES = [
  'application/pdf',
  'image/jpeg',
  'image/png',
  'image/webp',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
]

const SUPPORTED_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png', '.webp', '.docx', '.xlsx']

// 计算属性
const totalSize = computed(() => {
  return files.value.reduce((sum, file) => sum + file.size, 0)
})

const hasFiles = computed(() => files.value.length > 0)

// 文件图标
function getFileIcon(type: string, filename: string) {
  if (type === 'application/pdf' || filename.endsWith('.pdf')) return FileText
  if (type.startsWith('image/')) return Image
  if (filename.endsWith('.xlsx') || filename.endsWith('.docx')) return FileSpreadsheet
  return FileText
}

// 格式化文件大小
function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

// 验证文件
function isValidFile(file: File): boolean {
  // 检查 MIME 类型
  if (SUPPORTED_TYPES.includes(file.type)) return true

  // 检查扩展名（某些系统可能不设置 MIME）
  const ext = '.' + file.name.split('.').pop()?.toLowerCase()
  return SUPPORTED_EXTENSIONS.includes(ext)
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
  if (droppedFiles) {
    addFiles(Array.from(droppedFiles))
  }
}

// 处理文件选择
function handleFileSelect(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files) {
    addFiles(Array.from(input.files))
  }
  // 重置 input 以允许重复选择相同文件
  input.value = ''
}

// 添加文件
function addFiles(newFiles: File[]) {
  parseError.value = null

  const validFiles = newFiles.filter(file => {
    if (!isValidFile(file)) {
      console.warn(`不支持的文件类型: ${file.name}`)
      return false
    }
    // 检查是否已存在
    if (files.value.some(f => f.name === file.name && f.size === file.size)) {
      return false
    }
    return true
  })

  files.value = [...files.value, ...validFiles]
}

// 移除文件
function removeFile(index: number) {
  files.value = files.value.filter((_, i) => i !== index)
}

// 清空所有文件
function clearFiles() {
  files.value = []
  parseError.value = null
}

// 触发文件选择
function triggerFileSelect() {
  fileInputRef.value?.click()
}

// 解析文件
async function parseFiles() {
  if (!hasFiles.value) return

  isParsing.value = true
  parseError.value = null

  try {
    // 使用 parseApi 调用后端
    const { parseApi } = await import('@/api/client')
    const result = await parseApi.parseMaterials(props.projectId, files.value)

    // 发送解析结果
    emit('parsed', result.creditors)

  } catch (e) {
    parseError.value = (e as Error).message
  } finally {
    isParsing.value = false
  }
}
</script>

<template>
  <div class="material-upload">
    <!-- 上传区域 -->
    <div
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @drop="handleDrop"
      :class="[
        'border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer',
        isDragging
          ? 'border-primary-500 bg-primary-50'
          : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
      ]"
      @click="triggerFileSelect"
    >
      <input
        ref="fileInputRef"
        type="file"
        @change="handleFileSelect"
        multiple
        :accept="SUPPORTED_EXTENSIONS.join(',')"
        class="hidden"
      />

      <div class="flex flex-col items-center">
        <div
          :class="[
            'w-16 h-16 rounded-full flex items-center justify-center mb-4',
            isDragging ? 'bg-primary-100' : 'bg-gray-100'
          ]"
        >
          <Upload :class="['w-8 h-8', isDragging ? 'text-primary-600' : 'text-gray-400']" />
        </div>

        <p class="text-gray-700 font-medium">
          {{ isDragging ? '松开鼠标上传文件' : '拖拽文件到此处，或点击选择' }}
        </p>
        <p class="text-sm text-gray-500 mt-2">
          支持 PDF、Word、Excel、图片格式（含扫描件和手写体）
        </p>
      </div>
    </div>

    <!-- 文件列表 -->
    <div v-if="hasFiles" class="mt-4 space-y-2">
      <div class="flex items-center justify-between text-sm text-gray-500 mb-2">
        <span>已选择 {{ files.length }} 个文件（{{ formatSize(totalSize) }}）</span>
        <button @click="clearFiles" class="text-red-500 hover:text-red-600">
          清空全部
        </button>
      </div>

      <div
        v-for="(file, index) in files"
        :key="`${file.name}-${file.size}`"
        class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg"
      >
        <component
          :is="getFileIcon(file.type, file.name)"
          class="w-5 h-5 text-gray-400 flex-shrink-0"
        />
        <span class="flex-1 truncate text-gray-700">{{ file.name }}</span>
        <span class="text-sm text-gray-500 flex-shrink-0">{{ formatSize(file.size) }}</span>
        <button
          @click.stop="removeFile(index)"
          class="p-1 text-gray-400 hover:text-red-500 transition-colors"
        >
          <X class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="parseError" class="mt-4 p-4 bg-red-50 text-red-700 rounded-lg text-sm">
      {{ parseError }}
    </div>

    <!-- 操作按钮 -->
    <div class="flex justify-end gap-3 mt-6">
      <button
        @click="emit('cancel')"
        class="px-6 py-2.5 text-gray-600 hover:text-gray-800 transition-colors"
      >
        取消
      </button>
      <button
        @click="parseFiles"
        :disabled="!hasFiles || isParsing"
        :class="[
          'flex items-center gap-2 px-6 py-2.5 rounded-lg font-medium transition-all',
          hasFiles && !isParsing
            ? 'bg-primary-500 text-white hover:bg-primary-600'
            : 'bg-gray-200 text-gray-400 cursor-not-allowed'
        ]"
      >
        <Loader2 v-if="isParsing" class="w-5 h-5 animate-spin" />
        <Sparkles v-else class="w-5 h-5" />
        {{ isParsing ? '智能解析中...' : '开始智能解析' }}
      </button>
    </div>
  </div>
</template>
