<script setup lang="ts">
/**
 * User Button Component
 *
 * Displays current user avatar with dropdown menu for account management.
 */
import { UserButton, useAuth } from '@clerk/vue'

const { isSignedIn } = useAuth()
</script>

<template>
  <div v-if="isSignedIn" class="flex items-center">
    <UserButton
      :appearance="{
        elements: {
          avatarBox: 'w-9 h-9'
        }
      }"
      :after-sign-out-url="'/sign-in'"
    />
  </div>
  <div v-else>
    <router-link
      to="/sign-in"
      class="px-4 py-2 text-sm font-medium text-white bg-primary-500 rounded-lg hover:bg-primary-600 transition-colors"
    >
      登录
    </router-link>
  </div>
</template>
