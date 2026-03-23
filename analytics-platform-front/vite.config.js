import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"

export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 5173,
    proxy: {
      "/api": {
        // In Docker, "localhost" points to the frontend container itself.
        // Use VITE_PROXY_TARGET=http://backend:8000 (service name) when running via docker-compose.
        target:
          process.env.VITE_PROXY_TARGET ||
          process.env.VITE_API_URL ||
          "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
})