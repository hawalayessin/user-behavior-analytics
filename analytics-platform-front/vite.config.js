import { defineConfig, loadEnv } from "vite"
import react from "@vitejs/plugin-react"

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, ".", "")
  const proxyTarget =
    env.VITE_PROXY_TARGET || env.VITE_API_URL || "http://analytics_backend:8000"

  return {
    plugins: [react()],
    server: {
      host: "0.0.0.0",
      port: 5173,
      proxy: {
        "/api": {
          // In Docker, "localhost" points to the frontend container itself.
          // Use VITE_PROXY_TARGET=http://analytics_backend:8000 (service name) when running via docker-compose.
          target: proxyTarget,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ""),
        },
      },
    },
  }
})