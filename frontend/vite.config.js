import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // listen on all interfaces — required so the Dockerized dev server is reachable from the host browser
    port: 5173,
  },
});
