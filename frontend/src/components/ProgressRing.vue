<script setup lang="ts">
/**
 * Circular Progress Ring Component
 *
 * Displays progress as an animated circular ring.
 */
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  progress: number
  size?: number
  strokeWidth?: number
  showLabel?: boolean
}>(), {
  size: 120,
  strokeWidth: 8,
  showLabel: true
})

const radius = computed(() => (props.size - props.strokeWidth) / 2)
const circumference = computed(() => 2 * Math.PI * radius.value)
const strokeDashoffset = computed(() =>
  circumference.value - (props.progress / 100) * circumference.value
)

const progressColor = computed(() => {
  if (props.progress >= 100) return '#10b981' // green
  if (props.progress >= 50) return '#3b82f6'  // blue
  return '#6366f1' // indigo
})
</script>

<template>
  <div class="relative inline-flex items-center justify-center">
    <svg
      :width="size"
      :height="size"
      class="transform -rotate-90"
    >
      <!-- Background circle -->
      <circle
        :cx="size / 2"
        :cy="size / 2"
        :r="radius"
        fill="none"
        stroke="#e5e7eb"
        :stroke-width="strokeWidth"
      />
      <!-- Progress circle -->
      <circle
        :cx="size / 2"
        :cy="size / 2"
        :r="radius"
        fill="none"
        :stroke="progressColor"
        :stroke-width="strokeWidth"
        stroke-linecap="round"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="strokeDashoffset"
        class="transition-all duration-500 ease-out"
      />
    </svg>
    <!-- Center label -->
    <div
      v-if="showLabel"
      class="absolute inset-0 flex items-center justify-center"
    >
      <span class="text-2xl font-bold text-gray-700">
        {{ Math.round(progress) }}%
      </span>
    </div>
  </div>
</template>
