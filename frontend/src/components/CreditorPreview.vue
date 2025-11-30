<script setup lang="ts">
/**
 * Creditor Preview Component
 *
 * 显示 LLM 解析出的债权人列表，支持编辑、删除、合并后确认创建
 */
import { ref, computed } from 'vue'
import { Trash2, Edit3, Check, AlertCircle, FileText } from 'lucide-vue-next'

// 解析结果类型
interface ParsedCreditor {
  creditor_name: string
  declared_amount?: number
  source_file: string
  batch_number: number
  creditor_number: number
  confidence?: number
}

const props = defineProps<{
  creditors: ParsedCreditor[]
  projectId: string
}>()

const emit = defineEmits<{
  (e: 'confirm', creditors: ParsedCreditor[]): void
  (e: 'cancel'): void
  (e: 'back'): void
}>()

// 可编辑的债权人列表
const editableCreditors = ref<ParsedCreditor[]>(
  props.creditors.map((c, index) => ({
    ...c,
    batch_number: c.batch_number || 1,
    creditor_number: c.creditor_number || (index + 1)
  }))
)

// 编辑状态
const editingIndex = ref<number | null>(null)

// 计算属性
const totalAmount = computed(() => {
  return editableCreditors.value.reduce((sum, c) => sum + (c.declared_amount || 0), 0)
})

const validCreditors = computed(() => {
  return editableCreditors.value.filter(c => c.creditor_name.trim())
})

const hasEmptyNames = computed(() => {
  return editableCreditors.value.some(c => !c.creditor_name.trim())
})

// 格式化金额
function formatAmount(amount?: number): string {
  if (!amount) return '-'
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 2
  }).format(amount)
}

// 开始编辑
function startEdit(index: number) {
  editingIndex.value = index
}

// 完成编辑
function finishEdit() {
  editingIndex.value = null
}

// 删除债权人
function removeCreditor(index: number) {
  editableCreditors.value = editableCreditors.value.filter((_, i) => i !== index)
  // 重新编号
  editableCreditors.value.forEach((c, i) => {
    c.creditor_number = i + 1
  })
}

// 更新债权人信息
function updateCreditor(index: number, field: keyof ParsedCreditor, value: any) {
  if (editableCreditors.value[index]) {
    (editableCreditors.value[index] as any)[field] = value
  }
}

// 确认创建
function confirmCreate() {
  if (hasEmptyNames.value) {
    alert('请填写所有债权人名称')
    return
  }
  emit('confirm', validCreditors.value)
}
</script>

<template>
  <div class="creditor-preview">
    <!-- 标题栏 -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h3 class="text-lg font-semibold text-gray-800">AI 解析结果</h3>
        <p class="text-sm text-gray-500 mt-1">
          共识别 {{ editableCreditors.length }} 个债权人，总申报金额 {{ formatAmount(totalAmount) }}
        </p>
      </div>
      <button
        @click="emit('back')"
        class="text-primary-600 hover:text-primary-700 text-sm"
      >
        ← 重新上传
      </button>
    </div>

    <!-- 警告提示 -->
    <div v-if="hasEmptyNames" class="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg flex items-center gap-2">
      <AlertCircle class="w-5 h-5 text-yellow-600 flex-shrink-0" />
      <span class="text-sm text-yellow-700">部分债权人名称为空，请补充完整后再提交</span>
    </div>

    <!-- 债权人列表 -->
    <div class="space-y-3 max-h-[400px] overflow-y-auto pr-2">
      <div
        v-for="(creditor, index) in editableCreditors"
        :key="index"
        :class="[
          'border rounded-lg p-4 transition-all',
          editingIndex === index ? 'border-primary-300 bg-primary-50' : 'border-gray-200 hover:border-gray-300'
        ]"
      >
        <!-- 编辑模式 -->
        <div v-if="editingIndex === index" class="space-y-3">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-gray-500 mb-1">债权人名称 *</label>
              <input
                :value="creditor.creditor_name"
                @input="updateCreditor(index, 'creditor_name', ($event.target as HTMLInputElement).value)"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
                placeholder="请输入债权人名称"
              />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-500 mb-1">申报金额（元）</label>
              <input
                :value="creditor.declared_amount"
                @input="updateCreditor(index, 'declared_amount', parseFloat(($event.target as HTMLInputElement).value) || undefined)"
                type="number"
                step="0.01"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
                placeholder="选填"
              />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-gray-500 mb-1">批次号</label>
              <input
                :value="creditor.batch_number"
                @input="updateCreditor(index, 'batch_number', parseInt(($event.target as HTMLInputElement).value) || 1)"
                type="number"
                min="1"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
              />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-500 mb-1">序号</label>
              <input
                :value="creditor.creditor_number"
                @input="updateCreditor(index, 'creditor_number', parseInt(($event.target as HTMLInputElement).value) || 1)"
                type="number"
                min="1"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
              />
            </div>
          </div>
          <div class="flex justify-end">
            <button
              @click="finishEdit"
              class="flex items-center gap-1 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600"
            >
              <Check class="w-4 h-4" />
              完成编辑
            </button>
          </div>
        </div>

        <!-- 查看模式 -->
        <div v-else class="flex items-center gap-4">
          <div class="flex-shrink-0 w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-sm font-medium text-gray-600">
            {{ creditor.creditor_number }}
          </div>

          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span
                :class="[
                  'font-medium truncate',
                  creditor.creditor_name ? 'text-gray-800' : 'text-red-500 italic'
                ]"
              >
                {{ creditor.creditor_name || '(未填写名称)' }}
              </span>
              <span class="text-xs text-gray-400">第{{ creditor.batch_number }}批</span>
            </div>
            <div class="flex items-center gap-3 mt-1 text-sm text-gray-500">
              <span>申报金额: {{ formatAmount(creditor.declared_amount) }}</span>
              <span class="flex items-center gap-1 text-xs">
                <FileText class="w-3 h-3" />
                {{ creditor.source_file }}
              </span>
            </div>
          </div>

          <div class="flex items-center gap-2 flex-shrink-0">
            <button
              @click="startEdit(index)"
              class="p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
              title="编辑"
            >
              <Edit3 class="w-4 h-4" />
            </button>
            <button
              @click="removeCreditor(index)"
              class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              title="删除"
            >
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="editableCreditors.length === 0" class="py-8 text-center text-gray-500">
      <p>所有债权人已被移除</p>
      <button
        @click="emit('back')"
        class="mt-2 text-primary-600 hover:text-primary-700"
      >
        重新上传材料
      </button>
    </div>

    <!-- 操作按钮 -->
    <div class="flex justify-between items-center mt-6 pt-4 border-t">
      <span class="text-sm text-gray-500">
        将创建 {{ validCreditors.length }} 个债权人
      </span>
      <div class="flex gap-3">
        <button
          @click="emit('cancel')"
          class="px-6 py-2.5 text-gray-600 hover:text-gray-800 transition-colors"
        >
          取消
        </button>
        <button
          @click="confirmCreate"
          :disabled="validCreditors.length === 0"
          :class="[
            'px-6 py-2.5 rounded-lg font-medium transition-all',
            validCreditors.length > 0
              ? 'bg-primary-500 text-white hover:bg-primary-600'
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
          ]"
        >
          确认创建 ({{ validCreditors.length }})
        </button>
      </div>
    </div>
  </div>
</template>
