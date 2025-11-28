<script setup lang="ts">
/**
 * Interest Calculator Page
 */
import { ref, computed } from 'vue'
import { toolsApi } from '@/api/client'
import type { InterestCalculationRequest, InterestCalculationResponse } from '@/types'

const form = ref<InterestCalculationRequest>({
  calculation_type: 'lpr',
  principal: 100000,
  start_date: '',
  end_date: '',
  rate: 4.35,
  multiplier: 1.0,
  lpr_term: '1y'
})

const result = ref<InterestCalculationResponse | null>(null)
const loading = ref(false)
const error = ref('')

const calculationTypes = [
  { value: 'simple', label: '单利计算', description: '固定年利率单利' },
  { value: 'lpr', label: 'LPR浮动利率', description: '随LPR调整的浮动利率' },
  { value: 'delay', label: '迟延履行利息', description: '1.75倍LPR' },
  { value: 'penalty', label: '罚息/违约金', description: '固定利率，24%上限' }
]

const needsRate = computed(() =>
  ['simple', 'penalty'].includes(form.value.calculation_type)
)

const needsLprOptions = computed(() =>
  ['lpr', 'delay'].includes(form.value.calculation_type)
)

async function calculate() {
  if (!form.value.start_date || !form.value.end_date) {
    error.value = '请填写开始和结束日期'
    return
  }

  loading.value = true
  error.value = ''
  result.value = null

  try {
    result.value = await toolsApi.calculateInterest(form.value)
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    loading.value = false
  }
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY'
  }).format(amount)
}

function reset() {
  result.value = null
  error.value = ''
}
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <h1 class="text-2xl font-bold text-gray-800 mb-6">利息计算器</h1>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Form -->
      <div class="bg-white rounded-xl shadow-sm p-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">计算参数</h2>

        <!-- Calculation type -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">计算类型</label>
          <div class="grid grid-cols-2 gap-2">
            <div
              v-for="type in calculationTypes"
              :key="type.value"
              @click="form.calculation_type = type.value as any; reset()"
              :class="[
                'p-3 rounded-lg border-2 cursor-pointer transition-colors',
                form.calculation_type === type.value
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              ]"
            >
              <div class="font-medium text-gray-800">{{ type.label }}</div>
              <div class="text-xs text-gray-500 mt-1">{{ type.description }}</div>
            </div>
          </div>
        </div>

        <!-- Principal -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">本金 (元)</label>
          <input
            v-model.number="form.principal"
            type="number"
            min="0"
            step="0.01"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
          />
        </div>

        <!-- Date range -->
        <div class="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">开始日期</label>
            <input
              v-model="form.start_date"
              type="date"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">结束日期</label>
            <input
              v-model="form.end_date"
              type="date"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
            />
          </div>
        </div>

        <!-- Rate (conditional) -->
        <div v-if="needsRate" class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">年利率 (%)</label>
          <input
            v-model.number="form.rate"
            type="number"
            min="0"
            max="100"
            step="0.01"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
          />
        </div>

        <!-- LPR options (conditional) -->
        <div v-if="needsLprOptions" class="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">LPR期限</label>
            <select
              v-model="form.lpr_term"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
            >
              <option value="1y">1年期</option>
              <option value="5y">5年期以上</option>
            </select>
          </div>
          <div v-if="form.calculation_type === 'lpr'">
            <label class="block text-sm font-medium text-gray-700 mb-2">利率倍数</label>
            <input
              v-model.number="form.multiplier"
              type="number"
              min="0"
              step="0.1"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
            />
          </div>
        </div>

        <!-- Error -->
        <div v-if="error" class="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">
          {{ error }}
        </div>

        <!-- Submit -->
        <button
          @click="calculate"
          :disabled="loading"
          class="w-full py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors disabled:opacity-50"
        >
          {{ loading ? '计算中...' : '计算利息' }}
        </button>
      </div>

      <!-- Result -->
      <div class="bg-white rounded-xl shadow-sm p-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">计算结果</h2>

        <div v-if="!result" class="py-12 text-center text-gray-500">
          <div class="text-4xl mb-4">🧮</div>
          <p>填写参数后点击计算</p>
        </div>

        <div v-else>
          <!-- Summary -->
          <div class="bg-primary-50 rounded-lg p-4 mb-6">
            <div class="text-center">
              <div class="text-sm text-gray-600 mb-1">利息总额</div>
              <div class="text-3xl font-bold text-primary-700">
                {{ formatCurrency(result.interest) }}
              </div>
            </div>
          </div>

          <!-- Details -->
          <div class="space-y-3">
            <div class="flex justify-between py-2 border-b">
              <span class="text-gray-600">本金</span>
              <span class="font-medium">{{ formatCurrency(result.principal) }}</span>
            </div>
            <div class="flex justify-between py-2 border-b">
              <span class="text-gray-600">利息</span>
              <span class="font-medium text-primary-600">{{ formatCurrency(result.interest) }}</span>
            </div>
            <div class="flex justify-between py-2 border-b">
              <span class="text-gray-600">本息合计</span>
              <span class="font-bold text-lg">{{ formatCurrency(result.total) }}</span>
            </div>
            <div class="flex justify-between py-2 border-b">
              <span class="text-gray-600">计息天数</span>
              <span class="font-medium">{{ result.days }} 天</span>
            </div>
            <div class="flex justify-between py-2">
              <span class="text-gray-600">使用利率</span>
              <span class="font-medium">{{ result.rate_used.toFixed(2) }}%</span>
            </div>
          </div>

          <!-- Calculation details (if LPR periods) -->
          <div v-if="result.calculation_details.periods" class="mt-6">
            <h3 class="text-sm font-medium text-gray-700 mb-2">分段明细</h3>
            <div class="bg-gray-50 rounded-lg p-3 text-sm max-h-48 overflow-auto">
              <div
                v-for="(period, index) in result.calculation_details.periods"
                :key="index"
                class="py-2 border-b last:border-0"
              >
                <div class="flex justify-between">
                  <span class="text-gray-600">{{ period.start }} ~ {{ period.end }}</span>
                  <span class="font-medium">{{ formatCurrency(period.interest) }}</span>
                </div>
                <div class="text-xs text-gray-500 mt-1">
                  {{ period.days }}天 × {{ period.effective_rate.toFixed(2) }}%
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
