import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { clerkPlugin } from '@clerk/vue'
import router from './router'
import App from './App.vue'
import './style.css'

const CLERK_PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!CLERK_PUBLISHABLE_KEY) {
  console.warn('Missing VITE_CLERK_PUBLISHABLE_KEY - auth will not work')
}

const app = createApp(App)

app.use(createPinia())
app.use(clerkPlugin, {
  publishableKey: CLERK_PUBLISHABLE_KEY
})
app.use(router)

app.mount('#app')
