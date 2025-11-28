<script setup lang="ts">
/**
 * Sign Up Page
 *
 * Displays Clerk sign-up component for new user registration.
 */
import { SignUp } from '@clerk/vue'
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-800">债权审查系统</h1>
        <p class="text-gray-600 mt-2">创建新账户</p>
      </div>
      <SignUp
        :routing="'path'"
        path="/sign-up"
        sign-in-url="/sign-in"
      />
    </div>
  </div>
</template>
