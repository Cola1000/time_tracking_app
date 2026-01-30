import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

export default defineConfig({
  plugins: [svelte()],
  server: {
    port: parseInt(process.env.FRONTEND_PORT) || 5173,
    host: '0.0.0.0'
  }
})
