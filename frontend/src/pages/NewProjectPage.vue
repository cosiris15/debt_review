<script setup lang="ts">
/**
 * New Project Page
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '@/stores/project'

const router = useRouter()
const projectStore = useProjectStore()

const form = ref({
  name: '',
  debtor_name: '',
  bankruptcy_date: '',
  description: ''
})

const loading = ref(false)
const error = ref('')

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
      <p class="text-gray-600 mt-1">填写破产项目的基本信息</p>
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
