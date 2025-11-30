<script setup lang="ts">
/**
 * Markdown Viewer Component
 *
 * 支持 Markdown 渲染和 Mermaid 图表渲染
 * 可切换原始文本和渲染视图
 */
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { marked } from 'marked'
import mermaid from 'mermaid'
import { Code, Eye, Copy, Check } from 'lucide-vue-next'

const props = defineProps<{
  content: string
  title?: string
}>()

// 初始化 mermaid
mermaid.initialize({
  startOnLoad: false,
  theme: 'default',
  securityLevel: 'loose',
  fontFamily: 'inherit'
})

// 状态
const viewMode = ref<'rendered' | 'raw'>('rendered')
const copied = ref(false)
const mermaidContainer = ref<HTMLElement | null>(null)

// 解析 Markdown，保留 mermaid 代码块
const parsedHtml = computed(() => {
  if (!props.content) return ''

  // 处理 mermaid 代码块：将 ```mermaid 替换为特殊容器
  let processedContent = props.content.replace(
    /```mermaid\n([\s\S]*?)```/g,
    (_match, code) => `<div class="mermaid-wrapper"><pre class="mermaid">${code.trim()}</pre></div>`
  )

  // 解析其余的 Markdown
  return marked(processedContent) as string
})

// 渲染 Mermaid 图表
async function renderMermaid() {
  await nextTick()

  const mermaidElements = document.querySelectorAll('.mermaid-wrapper .mermaid')
  if (mermaidElements.length === 0) return

  for (let i = 0; i < mermaidElements.length; i++) {
    const el = mermaidElements[i] as HTMLElement
    const code = el.textContent || ''

    try {
      const { svg } = await mermaid.render(`mermaid-${Date.now()}-${i}`, code)
      el.innerHTML = svg
      el.classList.add('mermaid-rendered')
    } catch (e) {
      console.error('Mermaid rendering error:', e)
      el.innerHTML = `<div class="text-red-500 text-sm p-2">图表渲染失败: ${(e as Error).message}</div><pre class="text-xs">${code}</pre>`
    }
  }
}

// 复制内容
async function copyContent() {
  try {
    await navigator.clipboard.writeText(props.content)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch (e) {
    console.error('Copy failed:', e)
  }
}

// 监听内容变化重新渲染 Mermaid
watch(() => props.content, () => {
  if (viewMode.value === 'rendered') {
    renderMermaid()
  }
})

watch(viewMode, (mode) => {
  if (mode === 'rendered') {
    renderMermaid()
  }
})

onMounted(() => {
  if (viewMode.value === 'rendered') {
    renderMermaid()
  }
})
</script>

<template>
  <div class="markdown-viewer">
    <!-- 工具栏 -->
    <div class="flex items-center justify-between px-4 py-2 bg-slate-100 border-b border-slate-200">
      <span v-if="title" class="text-sm font-medium text-slate-700">{{ title }}</span>
      <div v-else></div>

      <div class="flex items-center gap-2">
        <!-- 视图切换 -->
        <div class="flex bg-slate-200 rounded-lg p-0.5">
          <button
            @click="viewMode = 'rendered'"
            :class="[
              'flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-colors',
              viewMode === 'rendered'
                ? 'bg-white text-slate-800 shadow-sm'
                : 'text-slate-600 hover:text-slate-800'
            ]"
          >
            <Eye class="w-3.5 h-3.5" />
            渲染
          </button>
          <button
            @click="viewMode = 'raw'"
            :class="[
              'flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-colors',
              viewMode === 'raw'
                ? 'bg-white text-slate-800 shadow-sm'
                : 'text-slate-600 hover:text-slate-800'
            ]"
          >
            <Code class="w-3.5 h-3.5" />
            源码
          </button>
        </div>

        <!-- 复制按钮 -->
        <button
          @click="copyContent"
          class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-800 hover:bg-slate-200 rounded-md transition-colors"
        >
          <Check v-if="copied" class="w-3.5 h-3.5 text-green-600" />
          <Copy v-else class="w-3.5 h-3.5" />
          {{ copied ? '已复制' : '复制' }}
        </button>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="overflow-auto max-h-[70vh]">
      <!-- 渲染视图 -->
      <div
        v-if="viewMode === 'rendered'"
        ref="mermaidContainer"
        class="markdown-content p-6 prose prose-slate max-w-none"
        v-html="parsedHtml"
      />

      <!-- 原始文本视图 -->
      <pre
        v-else
        class="p-6 text-sm text-slate-700 whitespace-pre-wrap font-mono bg-slate-50"
      >{{ content }}</pre>
    </div>
  </div>
</template>

<style>
.markdown-viewer {
  @apply bg-white rounded-lg border border-slate-200 overflow-hidden;
}

/* Markdown 样式 */
.markdown-content {
  @apply text-slate-800;
}

.markdown-content h1 {
  @apply text-2xl font-bold text-slate-900 border-b border-slate-200 pb-2 mb-4;
}

.markdown-content h2 {
  @apply text-xl font-semibold text-slate-800 border-b border-slate-100 pb-2 mb-3 mt-6;
}

.markdown-content h3 {
  @apply text-lg font-semibold text-slate-800 mb-2 mt-4;
}

.markdown-content h4 {
  @apply text-base font-semibold text-slate-700 mb-2 mt-3;
}

.markdown-content p {
  @apply mb-4 leading-relaxed;
}

.markdown-content ul, .markdown-content ol {
  @apply mb-4 pl-6;
}

.markdown-content li {
  @apply mb-1;
}

.markdown-content table {
  @apply w-full border-collapse mb-4;
}

.markdown-content th, .markdown-content td {
  @apply border border-slate-300 px-3 py-2 text-left;
}

.markdown-content th {
  @apply bg-slate-100 font-semibold;
}

.markdown-content code {
  @apply bg-slate-100 px-1.5 py-0.5 rounded text-sm font-mono text-slate-700;
}

.markdown-content pre {
  @apply bg-slate-900 text-slate-100 p-4 rounded-lg overflow-x-auto mb-4;
}

.markdown-content pre code {
  @apply bg-transparent p-0 text-inherit;
}

.markdown-content blockquote {
  @apply border-l-4 border-slate-300 pl-4 italic text-slate-600 my-4;
}

.markdown-content hr {
  @apply border-slate-200 my-6;
}

.markdown-content a {
  @apply text-blue-600 hover:underline;
}

.markdown-content strong {
  @apply font-semibold text-slate-900;
}

/* Mermaid 样式 */
.mermaid-wrapper {
  @apply my-4 p-4 bg-white border border-slate-200 rounded-lg overflow-x-auto;
}

.mermaid-rendered {
  @apply flex justify-center;
}

.mermaid-rendered svg {
  @apply max-w-full h-auto;
}
</style>
