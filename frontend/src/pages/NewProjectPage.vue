<script setup lang="ts">
/**
 * New Project Page
 *
 * 支持两种创建方式：
 * 1. 手动填写表单
 * 2. 上传裁定书自动提取信息
 */
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '@/stores/project'
import RulingUpload from '@/components/RulingUpload.vue'
import type { ParsedProjectInfo } from '@/api/client'
import { Sparkles, ChevronDown, ChevronUp, CheckCircle } from 'lucide-vue-next'

const router = useRouter()
const projectStore = useProjectStore()

// 表单数据
const form = ref({
  name: '',
  debtor_name: '',
  bankruptcy_date: '',
  description: ''
})

// 状态
const loading = ref(false)
const error = ref('')
const showRulingUpload = ref(false)
const parsedInfo = ref<ParsedProjectInfo | null>(null)

// 是否已从裁定书提取信息
const hasExtractedInfo = computed(() => parsedInfo.value !== null)

// 处理裁定书解析结果
function handleRulingParsed(info: ParsedProjectInfo) {
  parsedInfo.value = info
  showRulingUpload.value = false

  // 自动填充表单
  form.value.debtor_name = info.debtor_name
  form.value.bankruptcy_date = info.bankruptcy_date

  // 自动生成项目名称
  if (info.case_number) {
    form.value.name = `${info.debtor_name}破产清算案`
  }

  // 添加备注
  const notes: string[] = []
  if (info.case_number) notes.push(`案号：${info.case_number}`)
  if (info.court_name) notes.push(`法院：${info.court_name}`)
  if (notes.length > 0) {
    form.value.description = notes.join('\n')
  }
}

// 清除已提取的信息
function clearExtractedInfo() {
  parsedInfo.value = null
  form.value.name = ''
  form.value.debtor_name = ''
  form.value.bankruptcy_date = ''
  form.value.description = ''
}

async function handleSubmit() {
  if (!form.value.name || !form.value.debtor_name || !form.value.bankruptcy_date) {
    error.value = '请填写所有必填字段'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const project = await projectStore.createProject(form.value)
    router.push(`/projects/${project.id}`)
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <!-- Header -->
    <div class="mb-6">
      <button
        @click="router.back()"
        class="text-gray-500 hover:text-gray-700 mb-2 flex items-center gap-1"
      >
        ← 返回
      </button>
      <h1 class="text-2xl font-bold text-gray-800">创建新项目</h1>
      <p class="text-gray-600 mt-1">填写破产项目的基本信息，或上传裁定书自动提取</p>
    </div>

    <!-- 智能提取区域 -->
    <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
      <!-- 标题栏（可折叠） -->
      <button
        type="button"
        @click="showRulingUpload = !showRulingUpload"
        class="w-full flex items-center justify-between"
      >
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center">
            <Sparkles class="w-5 h-5 text-purple-600" />
          </div>
          <div class="text-left">
            <h3 class="font-semibold text-gray-800">智能提取</h3>
            <p class="text-sm text-gray-500">上传裁定书，AI 自动填写表单</p>
          </div>
        </div>
        <component
          :is="showRulingUpload ? ChevronUp : ChevronDown"
          class="w-5 h-5 text-gray-400"
        />
      </button>

      <!-- 已提取信息提示 -->
      <div
        v-if="hasExtractedInfo && !showRulingUpload"
        class="mt-4 p-3 bg-green-50 rounded-lg border border-green-200"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <CheckCircle class="w-5 h-5 text-green-600" />
            <span class="text-green-800 text-sm">已从裁定书提取信息，表单已自动填写</span>
          </div>
          <button
            type="button"
            @click="clearExtractedInfo"
            class="text-sm text-green-600 hover:text-green-800"
          >
            清除
          </button>
        </div>
      </div>

      <!-- 裁定书上传组件 -->
      <div v-if="showRulingUpload" class="mt-4 pt-4 border-t">
        <RulingUpload
          @parsed="handleRulingParsed"
          @cancel="showRulingUpload = false"
        />
      </div>
    </div>

    <!-- Form -->
    <form @submit.prevent="handleSubmit" class="bg-white rounded-xl shadow-sm p-6">
      <!-- Project name -->
      <div class="mb-6">
        <label class="block text-sm font-medium text-gray-700 mb-2">
          项目名称 <span class="text-red-500">*</span>
        </label>
        <input
          v-model="form.name"
          type="text"
          placeholder="例如：XX公司破产清算案"
          class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-colors"
        />
      </div>

      <!-- Debtor name -->
      <div class="mb-6">
        <label class="block text-sm font-medium text-gray-700 mb-2">
          债务人名称 <span class="text-red-500">*</span>
        </label>
        <input
          v-model="form.debtor_name"
          type="text"
          placeholder="例如：浙江XX有限公司"
          class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-colors"
        />
      </div>

      <!-- Bankruptcy date -->
      <div class="mb-6">
        <label class="block text-sm font-medium text-gray-700 mb-2">
          破产受理日期 <span class="text-red-500">*</span>
        </label>
        <input
          v-model="form.bankruptcy_date"
          type="date"
          class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-colors"
        />
        <p class="text-sm text-gray-500 mt-1">
          停止计息日期将自动设为破产受理日前一天
        </p>
      </div>

      <!-- Description -->
      <div class="mb-6">
        <label class="block text-sm font-medium text-gray-700 mb-2">
          项目描述
        </label>
        <textarea
          v-model="form.description"
          rows="3"
          placeholder="可选：添加项目备注信息"
          class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-colors resize-none"
        />
      </div>

      <!-- Error -->
      <div v-if="error" class="mb-6 p-4 bg-red-50 text-red-700 rounded-lg">
        {{ error }}
      </div>

      <!-- Actions -->
      <div class="flex justify-end gap-4">
        <button
          type="button"
          @click="router.back()"
          class="px-6 py-3 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
        >
          取消
        </button>
        <button
          type="submit"
          :disabled="loading"
          class="px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <span v-if="loading" class="animate-spin">⏳</span>
          {{ loading ? '创建中...' : '创建项目' }}
        </button>
      </div>
    </form>
  </div>
</template>
