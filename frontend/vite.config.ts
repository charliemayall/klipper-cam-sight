import path from "path"
import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

const moonrakerTarget =
  process.env.MOONRAKER_URL ?? "http://127.0.0.1:7125"

/** Mainsail/Fluidd serve /webcam on nginx :80, not Moonraker :7125. */
function defaultWebcamTarget(moonraker: string): string {
  try {
    const u = new URL(moonraker)
    u.port = ""
    u.pathname = ""
    u.search = ""
    u.hash = ""
    return u.origin
  } catch {
    return moonraker
  }
}

const webcamTarget =
  process.env.WEBCAM_URL ?? defaultWebcamTarget(moonrakerTarget)

export default defineConfig({
  base: "/server/files/cam_sight/",
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    proxy: {
      "/machine": {
        target: moonrakerTarget,
        changeOrigin: true,
      },
      "/webcam": {
        target: webcamTarget,
        changeOrigin: true,
      },
    },
  },
})
