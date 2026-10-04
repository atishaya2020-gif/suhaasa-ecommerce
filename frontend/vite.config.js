import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    // Allow ngrok's rotating public preview hostnames during local approval.
    allowedHosts: ['.ngrok-free.dev', '.ngrok-free.app'],
  },
})
