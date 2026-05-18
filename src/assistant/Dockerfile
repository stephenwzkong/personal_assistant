# Multi-stage build: Vite frontend + FastAPI backend
FROM node:22-slim AS frontend-build
WORKDIR /build
RUN corepack enable
COPY frontend/package.json frontend/pnpm-workspace.yaml frontend/pnpm-lock.yaml* ./frontend/
WORKDIR /build/frontend
ENV PNPM_ALLOW_EXEC_INSTALL_SCRIPTS=true
RUN pnpm install --frozen-lockfile || pnpm install
COPY frontend/ ./
RUN pnpm build


FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Copy the built frontend into the location api/main.py serves from
COPY --from=frontend-build /build/frontend/dist ./frontend/dist

EXPOSE 8082

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8082/api/session/init -X POST || exit 1

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8082"]
