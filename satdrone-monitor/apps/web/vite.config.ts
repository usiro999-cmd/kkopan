import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    chunkSizeWarningLimit: 1100,
    rollupOptions: {
      output: {
        manualChunks: {
          map: ["maplibre-gl"],
          react: ["react", "react-dom", "@tanstack/react-query", "zustand"],
          mui: [
            "@emotion/react",
            "@emotion/styled",
            "@mui/icons-material",
            "@mui/material",
          ],
        },
      },
    },
  },
  server: {
    host: "0.0.0.0",
    port: 5173,
  },
});
