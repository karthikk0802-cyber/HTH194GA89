import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      // Proxy all Streamlit page routes to the backend
      '/dashboard':        { target: 'http://localhost:8501', changeOrigin: true },
      '/learning_path':    { target: 'http://localhost:8501', changeOrigin: true },
      '/qa':               { target: 'http://localhost:8501', changeOrigin: true },
      '/learning_quiz':    { target: 'http://localhost:8501', changeOrigin: true },
      '/scenarios_voice':  { target: 'http://localhost:8501', changeOrigin: true },
      '/manager_dashboard':{ target: 'http://localhost:8501', changeOrigin: true },
      '/admin_knowledge':  { target: 'http://localhost:8501', changeOrigin: true },
      '/_stcore':          { target: 'http://localhost:8501', changeOrigin: true, ws: true },
      '/static':           { target: 'http://localhost:8501', changeOrigin: true },
      '/vendor':           { target: 'http://localhost:8501', changeOrigin: true },
    }
  }
})
