import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  // Base path for GitHub Pages or any static host
  base: './',
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
