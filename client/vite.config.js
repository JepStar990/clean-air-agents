import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Dev proxy so the client can call the backend on :8000
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
      '/a2a': 'http://localhost:8000'
    }
  },
  build: {
    outDir: 'dist'
  }
})

