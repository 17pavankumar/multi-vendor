# Development image for the Vite dev server. Production builds get a
# separate multi-stage Dockerfile (vite build -> nginx) in a later phase.
FROM node:20-alpine

WORKDIR /app

# package*.json copied alone first so `npm install` is cached across
# rebuilds that only touch src/ — the same layer-caching trick as the
# backend Dockerfile.
COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173
