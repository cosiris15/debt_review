<script setup lang="ts">
/**
 * Sign In Page
 *
 * Displays Clerk sign-in component for user authentication.
 */
import { SignIn } from '@clerk/vue'
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-800">债权审查系统</h1>
        <p class="text-gray-600 mt-2">请登录以继续</p>
      </div>
      <SignIn
        :routing="'path'"
        path="/sign-in"
        sign-up-url="/sign-up"
      />
    </div>
  </div>
</template>
