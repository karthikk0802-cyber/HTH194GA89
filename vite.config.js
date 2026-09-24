import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// React frontend talks to the FastAPI backend directly (see src/services/api.js).
// No Streamlit server exists anymore, so no proxy entries are configured.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173
  }
})
