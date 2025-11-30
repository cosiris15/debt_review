<script setup lang="ts">
/**
 * Creditor List Component
 *
 * Displays creditors grouped by batch with selection support.
 * Uses unified AddCreditorModal for adding creditors.
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useProjectStore } from '@/stores/project'
import { CreditorStatus } from '@/types'
import { Plus, ExternalLink } from 'lucide-vue-next'
import AddCreditorModal from './AddCreditorModal.vue'

const router = useRouter()

const props = defineProps<{
  projectId: string
}>()

const projectStore = useProjectStore()
const { creditors, selectedCreditors, creditorsByBatch, batchNumbers } = storeToRefs(projectStore)

const emit = defineEmits<{
  (e: 'submit', creditorIds: string[]): void
}>()

// Modal state
const showAddModal = ref(false)

// Navigate to creditor detail
function viewCreditorDetail(creditorId: string, event: Event) {
  event.stopPropagation()
  router.push(`/projects/${props.projectId}/creditors/${creditorId}`)
}

// Handle successful add
function handleAddSuccess(_count: number) {
  showAddModal.value = false
  projectStore.fetchCreditors(props.projectId)
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
      <button
        @click="showAddModal = true"
        class="flex items-center gap-1 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
      >
        <Plus class="w-4 h-4" />
        添加债权人
      </button>
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
      <p class="text-sm mt-1">点击上方"添加债权人"开始添加</p>
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

    <!-- Add Creditor Modal -->
    <AddCreditorModal
      v-if="showAddModal"
      :project-id="projectId"
      @close="showAddModal = false"
      @success="handleAddSuccess"
    />
  </div>
</template>
