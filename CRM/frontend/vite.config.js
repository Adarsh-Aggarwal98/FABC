import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/crm/',
  server: {
    port: 5173,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: process.env.DOCKER ? 'http://crm-backend:5000' : 'http://localhost:5001',
        changeOrigin: true
      }
    }
  }
})
