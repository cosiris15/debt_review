<script setup lang="ts">
import { RouterView, useRoute } from 'vue-router'
import { useAuth, useSession } from '@clerk/vue'
import { watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import { setAuthTokenGetter } from '@/api/client'

const route = useRoute()
const router = useRouter()
const { isSignedIn, isLoaded } = useAuth()
const { session } = useSession()

// Set up auth token getter for API client
onMounted(() => {
  setAuthTokenGetter(async () => {
    if (session.value) {
      return await session.value.getToken()
    }
    return null
  })
})

// Auth guard: redirect to sign-in if not authenticated
watch([isLoaded, isSignedIn, () => route.path], ([loaded, signedIn, path]) => {
  if (!loaded) return

  const isPublicRoute = route.meta.public === true

  if (!signedIn && !isPublicRoute) {
    router.push('/sign-in')
  } else if (signedIn && (path === '/sign-in' || path === '/sign-up')) {
    router.push('/')
  }
}, { immediate: true })

// Check if current route is a public auth page
const isAuthPage = () => route.meta.public === true
</script>

<template>
  <!-- Show loading while Clerk initializes -->
  <div v-if="!isLoaded" class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="text-center">
      <div class="animate-spin w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full mx-auto mb-4"></div>
      <p class="text-gray-600">加载中...</p>
    </div>
  </div>

  <!-- Auth pages without layout -->
  <RouterView v-else-if="isAuthPage()" />

  <!-- Protected pages with layout -->
  <AppLayout v-else>
    <RouterView />
  </AppLayout>
</template>
