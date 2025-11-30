<script setup lang="ts">
/**
 * Creditor List Component
 *
 * Displays creditors grouped by batch with selection support.
 * Includes add creditor form and batch import.
 */
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useProjectStore } from '@/stores/project'
import { CreditorStatus } from '@/types'
import type { CreditorCreate } from '@/types'
import { Plus, Upload, X, ExternalLink, Sparkles } from 'lucide-vue-next'
import SmartImportModal from './SmartImportModal.vue'

const router = useRouter()

const props = defineProps<{
  projectId: string
}>()

const projectStore = useProjectStore()
const { creditors, selectedCreditors, creditorsByBatch, batchNumbers } = storeToRefs(projectStore)

const emit = defineEmits<{
  (e: 'submit', creditorIds: string[]): void
}>()

// Form state
const showAddForm = ref(false)
const showBatchImport = ref(false)
const showSmartImport = ref(false)  // 智能导入弹窗
const isSubmitting = ref(false)
const formError = ref<string | null>(null)

// Single creditor form
const newCreditor = ref({
  batch_number: 1,
  creditor_number: 1,
  creditor_name: '',
  declared_amount: undefined as number | undefined,
  materials_path: ''
})

// Batch import text
const batchImportText = ref('')

// Get next creditor number for selected batch
const nextCreditorNumber = computed(() => {
  const batch = newCreditor.value.batch_number
  const batchCreditors = creditorsByBatch.value[batch] || []
  if (batchCreditors.length === 0) return 1
  return Math.max(...batchCreditors.map(c => c.creditor_number)) + 1
})

// Reset form
function resetForm() {
  newCreditor.value = {
    batch_number: batchNumbers.value.length > 0 ? Math.max(...batchNumbers.value) : 1,
    creditor_number: nextCreditorNumber.value,
    creditor_name: '',
    declared_amount: undefined,
    materials_path: ''
  }
  formError.value = null
}

// Add single creditor
async function handleAddCreditor() {
  if (!newCreditor.value.creditor_name.trim()) {
    formError.value = '请输入债权人名称'
    return
  }

  isSubmitting.value = true
  formError.value = null

  try {
    const data: CreditorCreate = {
      project_id: props.projectId,
      batch_number: newCreditor.value.batch_number,
      creditor_number: newCreditor.value.creditor_number,
      creditor_name: newCreditor.value.creditor_name.trim(),
      declared_amount: newCreditor.value.declared_amount,
      materials_path: newCreditor.value.materials_path || undefined
    }

    await projectStore.createCreditor(data)
    showAddForm.value = false
    resetForm()
  } catch (e) {
    formError.value = (e as Error).message
  } finally {
    isSubmitting.value = false
  }
}

// Parse batch import text (format: each line is "number,name,amount")
function parseBatchImport(text: string): CreditorCreate[] {
  const lines = text.trim().split('\n').filter(line => line.trim())
  const results: CreditorCreate[] = []
  const currentBatch = batchNumbers.value.length > 0 ? Math.max(...batchNumbers.value) : 1

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]?.trim()
    if (!line) continue

    // Try to parse: number,name,amount or just name
    const parts = line.split(/[,，\t]/).map(p => p.trim())

    let creditorNumber: number
    let creditorName: string
    let declaredAmount: number | undefined

    const firstPart = parts[0] || ''
    const secondPart = parts[1] || ''
    const thirdPart = parts[2] || ''

    if (parts.length >= 2 && !isNaN(parseInt(firstPart))) {
      // Format: number,name,amount
      creditorNumber = parseInt(firstPart)
      creditorName = secondPart
      declaredAmount = thirdPart ? parseFloat(thirdPart.replace(/[,，]/g, '')) : undefined
    } else {
      // Format: just name
      creditorNumber = i + 1
      creditorName = firstPart
      declaredAmount = secondPart ? parseFloat(secondPart.replace(/[,，]/g, '')) : undefined
    }

    if (creditorName) {
      results.push({
        project_id: props.projectId,
        batch_number: currentBatch,
        creditor_number: creditorNumber,
        creditor_name: creditorName,
        declared_amount: declaredAmount && !isNaN(declaredAmount) ? declaredAmount : undefined
      })
    }
  }

  return results
}

// Navigate to creditor detail
function viewCreditorDetail(creditorId: string, event: Event) {
  event.stopPropagation()  // Prevent triggering selection
  router.push(`/projects/${props.projectId}/creditors/${creditorId}`)
}

// Handle batch import
async function handleBatchImport() {
  if (!batchImportText.value.trim()) {
    formError.value = '请输入债权人信息'
    return
  }

  const creditorList = parseBatchImport(batchImportText.value)
  if (creditorList.length === 0) {
    formError.value = '未能解析任何债权人信息'
    return
  }

  isSubmitting.value = true
  formError.value = null

  try {
    let successCount = 0
    for (const data of creditorList) {
      try {
        await projectStore.createCreditor(data)
        successCount++
      } catch (e) {
        console.error(`Failed to create creditor ${data.creditor_name}:`, e)
      }
    }

    if (successCount > 0) {
      showBatchImport.value = false
      batchImportText.value = ''
    }

    if (successCount < creditorList.length) {
      formError.value = `成功导入 ${successCount}/${creditorList.length} 个债权人`
    }
  } catch (e) {
    formError.value = (e as Error).message
  } finally {
    isSubmitting.value = false
  }
}

function isSelected(id: string): boolean {
  return selectedCreditors.value.includes(id)
}

function getStatusLabel(status: CreditorStatus): string {
  const labels: Record<CreditorStatus, string> = {
    [CreditorStatus.NOT_STARTED]: '待处理',
    [CreditorStatus.IN_PROGRESS]: '处理中',
    [CreditorStatus.COMPLETED]: '已完成',
    [CreditorStatus.FAILED]: '失败'
  }
  return labels[status]
}

function getStatusClass(status: CreditorStatus): string {
  const classes: Record<CreditorStatus, string> = {
    [CreditorStatus.NOT_STARTED]: 'bg-gray-100 text-gray-600',
    [CreditorStatus.IN_PROGRESS]: 'bg-blue-100 text-blue-700',
    [CreditorStatus.COMPLETED]: 'bg-green-100 text-green-700',
    [CreditorStatus.FAILED]: 'bg-red-100 text-red-700'
  }
  return classes[status]
}

function handleSubmit() {
  if (selectedCreditors.value.length > 0) {
    emit('submit', selectedCreditors.value)
  }
}

function formatAmount(amount?: number): string {
  if (!amount) return '-'
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 2
  }).format(amount)
}
</script>

<template>
  <div class="bg-white rounded-xl shadow-lg">
    <!-- Header -->
    <div class="p-4 border-b flex items-center justify-between">
      <h3 class="text-lg font-semibold text-gray-800">债权人列表</h3>
      <div class="flex items-center gap-2">
        <button
          @click="showAddForm = true; resetForm()"
          class="flex items-center gap-1 px-3 py-1.5 text-sm bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
        >
          <Plus class="w-4 h-4" />
          添加
        </button>
        <button
          @click="showBatchImport = true; formError = null"
          class="flex items-center gap-1 px-3 py-1.5 text-sm border border-gray-300 text-gray-600 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <Upload class="w-4 h-4" />
          批量导入
        </button>
        <!-- 智能导入按钮（突出显示） -->
        <button
          @click="showSmartImport = true"
          class="flex items-center gap-1 px-3 py-1.5 text-sm bg-gradient-to-r from-purple-500 to-primary-500 text-white rounded-lg hover:from-purple-600 hover:to-primary-600 transition-all shadow-sm"
        >
          <Sparkles class="w-4 h-4" />
          智能导入
        </button>
      </div>
    </div>

    <!-- Add Single Creditor Modal -->
    <div v-if="showAddForm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-md mx-4">
        <div class="flex items-center justify-between p-4 border-b">
          <h4 class="text-lg font-semibold">添加债权人</h4>
          <button @click="showAddForm = false" class="text-gray-400 hover:text-gray-600">
            <X class="w-5 h-5" />
          </button>
        </div>
        <div class="p-4 space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">批次号</label>
              <input
                v-model.number="newCreditor.batch_number"
                type="number"
                min="1"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">债权人编号</label>
              <input
                v-model.number="newCreditor.creditor_number"
                type="number"
                min="1"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">债权人名称 <span class="text-red-500">*</span></label>
            <input
              v-model="newCreditor.creditor_name"
              type="text"
              placeholder="请输入债权人名称"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">申报金额（元）</label>
            <input
              v-model.number="newCreditor.declared_amount"
              type="number"
              step="0.01"
              placeholder="选填"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">材料路径</label>
            <input
              v-model="newCreditor.materials_path"
              type="text"
              placeholder="选填，如：/data/creditor_001"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <div v-if="formError" class="text-red-500 text-sm">{{ formError }}</div>
        </div>
        <div class="flex justify-end gap-3 p-4 border-t bg-gray-50">
          <button
            @click="showAddForm = false"
            class="px-4 py-2 text-gray-600 hover:text-gray-800"
          >
            取消
          </button>
          <button
            @click="handleAddCreditor"
            :disabled="isSubmitting"
            class="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ isSubmitting ? '添加中...' : '确认添加' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Batch Import Modal -->
    <div v-if="showBatchImport" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-lg mx-4">
        <div class="flex items-center justify-between p-4 border-b">
          <h4 class="text-lg font-semibold">批量导入债权人</h4>
          <button @click="showBatchImport = false" class="text-gray-400 hover:text-gray-600">
            <X class="w-5 h-5" />
          </button>
        </div>
        <div class="p-4 space-y-4">
          <div class="text-sm text-gray-600">
            <p class="mb-2">支持格式（每行一个债权人）：</p>
            <ul class="list-disc list-inside space-y-1 text-gray-500">
              <li>编号,名称,金额（如：1,张三,100000）</li>
              <li>名称,金额（如：张三,100000）</li>
              <li>仅名称（如：张三）</li>
            </ul>
          </div>
          <div>
            <textarea
              v-model="batchImportText"
              rows="10"
              placeholder="1,债权人A,1000000&#10;2,债权人B,2000000&#10;3,债权人C"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 font-mono text-sm"
            ></textarea>
          </div>
          <div v-if="formError" class="text-red-500 text-sm">{{ formError }}</div>
        </div>
        <div class="flex justify-end gap-3 p-4 border-t bg-gray-50">
          <button
            @click="showBatchImport = false"
            class="px-4 py-2 text-gray-600 hover:text-gray-800"
          >
            取消
          </button>
          <button
            @click="handleBatchImport"
            :disabled="isSubmitting"
            class="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ isSubmitting ? '导入中...' : '开始导入' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Selection controls (shown when has creditors) -->
    <div v-if="creditors.length > 0" class="px-4 py-2 border-b bg-gray-50 flex items-center gap-4">
      <button
        @click="projectStore.selectPendingCreditors()"
        class="text-sm text-primary-600 hover:text-primary-700"
      >
        选择待处理
      </button>
      <button
        @click="projectStore.selectAllCreditors()"
        class="text-sm text-primary-600 hover:text-primary-700"
      >
        全选
      </button>
      <button
        @click="projectStore.clearSelection()"
        class="text-sm text-gray-500 hover:text-gray-600"
      >
        清除选择
      </button>
    </div>

    <!-- Empty state -->
    <div v-if="creditors.length === 0" class="p-8 text-center text-gray-500">
      <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
        <Plus class="w-8 h-8 text-gray-400" />
      </div>
      <p class="text-lg">暂无债权人</p>
      <p class="text-sm mt-1">点击上方"添加"或"批量导入"添加债权人</p>
    </div>

    <!-- Creditor list by batch -->
    <div v-else class="divide-y">
      <div v-for="batch in batchNumbers" :key="batch" class="p-4">
        <h4 class="text-sm font-medium text-gray-500 mb-3">
          第 {{ batch }} 批 ({{ creditorsByBatch[batch]?.length || 0 }} 人)
        </h4>
        <div class="space-y-2">
          <div
            v-for="creditor in creditorsByBatch[batch]"
            :key="creditor.id"
            @click="projectStore.toggleCreditorSelection(creditor.id)"
            :class="[
              'flex items-center gap-4 p-3 rounded-lg cursor-pointer transition-colors',
              isSelected(creditor.id) ? 'bg-primary-50 border border-primary-200' : 'hover:bg-gray-50'
            ]"
          >
            <!-- Checkbox -->
            <div
              :class="[
                'w-5 h-5 rounded border-2 flex items-center justify-center transition-colors',
                isSelected(creditor.id) ? 'bg-primary-500 border-primary-500' : 'border-gray-300'
              ]"
            >
              <svg
                v-if="isSelected(creditor.id)"
                class="w-3 h-3 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
              </svg>
            </div>

            <!-- Info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span class="text-sm text-gray-500">{{ creditor.creditor_number }}.</span>
                <span class="font-medium text-gray-800 truncate">{{ creditor.creditor_name }}</span>
              </div>
              <div class="text-sm text-gray-500 mt-1">
                申报金额: {{ formatAmount(creditor.declared_amount) }}
                <span v-if="creditor.confirmed_amount" class="ml-3">
                  确认金额: {{ formatAmount(creditor.confirmed_amount) }}
                </span>
              </div>
            </div>

            <!-- Status -->
            <span
              :class="[
                'px-2 py-1 rounded-full text-xs font-medium',
                getStatusClass(creditor.status)
              ]"
            >
              {{ getStatusLabel(creditor.status) }}
            </span>

            <!-- View Detail Button -->
            <button
              @click="viewCreditorDetail(creditor.id, $event)"
              class="p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
              title="查看详情"
            >
              <ExternalLink class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="p-4 border-t bg-gray-50 flex items-center justify-between">
      <span class="text-sm text-gray-600">
        已选择 {{ selectedCreditors.length }} / {{ creditors.length }} 人
      </span>
      <button
        @click="handleSubmit"
        :disabled="selectedCreditors.length === 0"
        :class="[
          'px-6 py-2 rounded-lg font-medium transition-colors',
          selectedCreditors.length > 0
            ? 'bg-primary-500 text-white hover:bg-primary-600'
            : 'bg-gray-200 text-gray-400 cursor-not-allowed'
        ]"
      >
        开始处理 ({{ selectedCreditors.length }})
      </button>
    </div>

    <!-- 智能导入弹窗 -->
    <SmartImportModal
      v-if="showSmartImport"
      :project-id="projectId"
      @close="showSmartImport = false"
      @success="(count) => { showSmartImport = false; projectStore.fetchCreditors(projectId) }"
    />
  </div>
</template>
