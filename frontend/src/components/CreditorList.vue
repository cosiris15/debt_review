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
import { Plus, ArrowRight, UserPlus, Check } from 'lucide-vue-next'
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
    [CreditorStatus.NOT_STARTED]: 'bg-slate-100 text-slate-600',
    [CreditorStatus.IN_PROGRESS]: 'bg-blue-100 text-blue-700',
    [CreditorStatus.COMPLETED]: 'bg-emerald-100 text-emerald-700',
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
  <div class="bg-white rounded-xl border border-slate-200">
    <!-- Header -->
    <div class="p-5 border-b border-slate-100 flex items-center justify-between">
      <h3 class="text-base font-semibold text-slate-800">债权人列表</h3>
      <button
        @click="showAddModal = true"
        class="flex items-center gap-1.5 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
      >
        <Plus class="w-4 h-4" />
        添加债权人
      </button>
    </div>

    <!-- Selection controls (shown when has creditors) -->
    <div v-if="creditors.length > 0" class="px-5 py-3 border-b border-slate-100 bg-slate-50 flex items-center gap-4">
      <button
        @click="projectStore.selectPendingCreditors()"
        class="text-sm text-blue-600 hover:text-blue-700 font-medium"
      >
        选择待处理
      </button>
      <button
        @click="projectStore.selectAllCreditors()"
        class="text-sm text-blue-600 hover:text-blue-700 font-medium"
      >
        全选
      </button>
      <button
        @click="projectStore.clearSelection()"
        class="text-sm text-slate-500 hover:text-slate-600"
      >
        清除选择
      </button>
      <div class="flex-1" />
      <span class="text-sm text-slate-500">
        已选择 <span class="font-medium text-slate-700">{{ selectedCreditors.length }}</span> / {{ creditors.length }}
      </span>
    </div>

    <!-- Empty state -->
    <div v-if="creditors.length === 0" class="p-12 text-center">
      <div class="w-16 h-16 mx-auto mb-4 bg-slate-100 rounded-2xl flex items-center justify-center">
        <UserPlus class="w-8 h-8 text-slate-400" />
      </div>
      <p class="text-slate-700 font-medium mb-1">暂无债权人</p>
      <p class="text-sm text-slate-500">点击上方"添加债权人"开始添加</p>
    </div>

    <!-- Creditor list by batch -->
    <div v-else class="divide-y divide-slate-100 max-h-[500px] overflow-y-auto">
      <div v-for="batch in batchNumbers" :key="batch" class="p-4">
        <h4 class="text-xs font-medium text-slate-400 uppercase tracking-wider mb-3 px-1">
          第 {{ batch }} 批 ({{ creditorsByBatch[batch]?.length || 0 }} 人)
        </h4>
        <div class="space-y-2">
          <div
            v-for="creditor in creditorsByBatch[batch]"
            :key="creditor.id"
            @click="projectStore.toggleCreditorSelection(creditor.id)"
            :class="[
              'flex items-center gap-4 p-3 rounded-lg cursor-pointer transition-all',
              isSelected(creditor.id)
                ? 'bg-blue-50 border border-blue-200'
                : 'hover:bg-slate-50 border border-transparent'
            ]"
          >
            <!-- Checkbox -->
            <div
              :class="[
                'w-5 h-5 rounded flex items-center justify-center transition-colors flex-shrink-0',
                isSelected(creditor.id)
                  ? 'bg-blue-600 border-blue-600'
                  : 'border-2 border-slate-300'
              ]"
            >
              <Check
                v-if="isSelected(creditor.id)"
                class="w-3.5 h-3.5 text-white"
                stroke-width="3"
              />
            </div>

            <!-- Info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span class="text-sm text-slate-400 font-mono">{{ String(creditor.creditor_number).padStart(2, '0') }}</span>
                <span class="font-medium text-slate-800 truncate">{{ creditor.creditor_name }}</span>
              </div>
              <div class="text-sm text-slate-500 mt-0.5">
                申报: {{ formatAmount(creditor.declared_amount) }}
                <span v-if="creditor.confirmed_amount" class="ml-3 text-emerald-600">
                  确认: {{ formatAmount(creditor.confirmed_amount) }}
                </span>
              </div>
            </div>

            <!-- Status -->
            <span
              :class="[
                'px-2.5 py-1 rounded-full text-xs font-medium',
                getStatusClass(creditor.status)
              ]"
            >
              {{ getStatusLabel(creditor.status) }}
            </span>

            <!-- View Detail Button -->
            <button
              @click="viewCreditorDetail(creditor.id, $event)"
              class="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              title="查看详情"
            >
              <ArrowRight class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="p-4 border-t border-slate-100 bg-slate-50 flex items-center justify-end">
      <button
        @click="handleSubmit"
        :disabled="selectedCreditors.length === 0"
        :class="[
          'px-5 py-2.5 rounded-lg font-medium transition-all flex items-center gap-2',
          selectedCreditors.length > 0
            ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm'
            : 'bg-slate-200 text-slate-400 cursor-not-allowed'
        ]"
      >
        开始处理
        <span v-if="selectedCreditors.length > 0" class="bg-blue-500 px-2 py-0.5 rounded text-xs">
          {{ selectedCreditors.length }}
        </span>
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
