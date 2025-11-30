<script setup lang="ts">
/**
 * Smart Import Modal
 *
 * 智能导入弹窗：整合材料上传和解析结果预览
 * 流程：上传材料 → AI解析 → 用户确认/编辑 → 批量创建债权人
 */
import { ref, computed } from 'vue'
import { X, Sparkles } from 'lucide-vue-next'
import MaterialUpload from './MaterialUpload.vue'
import CreditorPreview from './CreditorPreview.vue'
import { useProjectStore } from '@/stores/project'
import type { CreditorCreate } from '@/types'

// 解析结果类型（与 MaterialUpload 组件一致）
interface ParsedCreditor {
  creditor_name: string
  declared_amount?: number
  source_file: string
  batch_number: number
  creditor_number: number
  confidence?: number
}

const props = defineProps<{
  projectId: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'success', count: number): void
}>()

const projectStore = useProjectStore()

// 步骤状态
type Step = 'upload' | 'preview'
const currentStep = ref<Step>('upload')

// 解析结果
const parsedCreditors = ref<ParsedCreditor[]>([])

// 提交状态
const isSubmitting = ref(false)
const submitError = ref<string | null>(null)

// 步骤标题
const stepTitle = computed(() => {
  return currentStep.value === 'upload' ? '上传债权申报材料' : 'AI 解析结果确认'
})

// 处理解析完成
function handleParsed(creditors: ParsedCreditor[]) {
  parsedCreditors.value = creditors
  currentStep.value = 'preview'
}

// 返回上传步骤
function backToUpload() {
  currentStep.value = 'upload'
  parsedCreditors.value = []
}

// 确认创建债权人
async function handleConfirmCreate(creditors: ParsedCreditor[]) {
  isSubmitting.value = true
  submitError.value = null

  let successCount = 0
  const errors: string[] = []

  for (const creditor of creditors) {
    try {
      const data: CreditorCreate = {
        project_id: props.projectId,
        batch_number: creditor.batch_number,
        creditor_number: creditor.creditor_number,
        creditor_name: creditor.creditor_name,
        declared_amount: creditor.declared_amount
      }
      await projectStore.createCreditor(data)
      successCount++
    } catch (e) {
      errors.push(`${creditor.creditor_name}: ${(e as Error).message}`)
    }
  }

  isSubmitting.value = false

  if (errors.length > 0) {
    submitError.value = `${successCount} 个创建成功，${errors.length} 个失败`
    console.error('创建失败的债权人:', errors)
  }

  if (successCount > 0) {
    emit('success', successCount)
    emit('close')
  }
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
            <Sparkles class="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <h3 class="text-lg font-semibold text-gray-800">智能导入</h3>
            <p class="text-sm text-gray-500">{{ stepTitle }}</p>
          </div>
        </div>
        <button
          @click="emit('close')"
          class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Step Indicator -->
      <div class="px-5 py-3 border-b bg-gray-50 flex-shrink-0">
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-2">
            <div
              :class="[
                'w-6 h-6 rounded-full flex items-center justify-center text-sm font-medium',
                currentStep === 'upload'
                  ? 'bg-primary-500 text-white'
                  : 'bg-green-500 text-white'
              ]"
            >
              {{ currentStep === 'upload' ? '1' : '✓' }}
            </div>
            <span :class="currentStep === 'upload' ? 'text-gray-800 font-medium' : 'text-gray-500'">
              上传材料
            </span>
          </div>
          <div class="w-8 h-0.5 bg-gray-300"></div>
          <div class="flex items-center gap-2">
            <div
              :class="[
                'w-6 h-6 rounded-full flex items-center justify-center text-sm font-medium',
                currentStep === 'preview'
                  ? 'bg-primary-500 text-white'
                  : 'bg-gray-300 text-gray-500'
              ]"
            >
              2
            </div>
            <span :class="currentStep === 'preview' ? 'text-gray-800 font-medium' : 'text-gray-500'">
              确认结果
            </span>
          </div>
        </div>
      </div>

      <!-- Content -->
      <div class="p-5 overflow-y-auto flex-1">
        <!-- 提交错误提示 -->
        <div v-if="submitError" class="mb-4 p-4 bg-red-50 text-red-700 rounded-lg text-sm">
          {{ submitError }}
        </div>

        <!-- 上传步骤 -->
        <MaterialUpload
          v-if="currentStep === 'upload'"
          :project-id="projectId"
          @parsed="handleParsed"
          @cancel="emit('close')"
        />

        <!-- 预览步骤 -->
        <CreditorPreview
          v-else
          :creditors="parsedCreditors"
          :project-id="projectId"
          @confirm="handleConfirmCreate"
          @cancel="emit('close')"
          @back="backToUpload"
        />
      </div>

      <!-- Loading Overlay -->
      <div
        v-if="isSubmitting"
        class="absolute inset-0 bg-white/80 flex items-center justify-center rounded-2xl"
      >
        <div class="text-center">
          <div class="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p class="text-gray-600">正在创建债权人...</p>
        </div>
      </div>
    </div>
  </div>
</template>
