"""
Docker Manager Module - KIRA AI Operating System (Phase 10)
Provides containerization tools: generates optimized multi-stage Dockerfiles and docker-compose.yml files,
builds Docker images, manages container lifecycles, and performs AI log diagnosis.
"""

import os
import json
import subprocess
from typing import Dict, Any, List, Optional
from utils.logger import logger
from router.model_router import model_router


class DockerManager:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = os.path.abspath(workspace_root)

    def generate_dockerfile(self, project_type: str = "node") -> Dict[str, Any]:
        """Generates an optimized multi-stage Dockerfile for Python, Node, React, Go, Rust, etc."""
        dockerfiles = {
            "node": """# Multi-stage Dockerfile for Node.js / React / Express
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build || true

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY package*.json ./
RUN npm ci --only=production
COPY --from=builder /app/dist ./dist
EXPOSE 3000
CMD ["node", "dist/server.cjs"]
""",
            "python": """# Multi-stage Dockerfile for Python FastAPI / AI OS Engine
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim AS runner
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
EXPOSE 8000
CMD ["python", "-m", "api.main"]
""",
            "go": """# Dockerfile for Go Microservices
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o app .

FROM alpine:3.19
WORKDIR /app
COPY --from=builder /app/app .
EXPOSE 8080
CMD ["./app"]
"""
        }

        content = dockerfiles.get(project_type.lower(), dockerfiles["node"])
        dest = os.path.join(self.workspace_root, "Dockerfile")
        with open(dest, 'w', encoding='utf-8') as f:
            f.write(content)

        return {
            "status": "success",
            "dockerfile_path": "Dockerfile",
            "project_type": project_type,
            "content": content
        }

    def generate_docker_compose(self) -> Dict[str, Any]:
        """Generates a complete docker-compose.yml file."""
        compose_content = """version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
      - "8000:8000"
    environment:
      - NODE_ENV=production
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
"""
        dest = os.path.join(self.workspace_root, "docker-compose.yml")
        with open(dest, 'w', encoding='utf-8') as f:
            f.write(compose_content)

        return {
            "status": "success",
            "compose_path": "docker-compose.yml",
            "content": compose_content
        }

    def build_image(self, tag: str = "kira-app:latest") -> Dict[str, Any]:
        """Builds Docker image using system CLI."""
        cmd = f"docker build -t {tag} ."
        try:
            proc = subprocess.run(cmd, shell=True, cwd=self.workspace_root, capture_output=True, text=True, timeout=120)
            return {
                "status": "success" if proc.returncode == 0 else "error",
                "tag": tag,
                "output": proc.stdout[:1000] or proc.stderr[:1000]
            }
        except Exception as e:
            return {"status": "error", "message": f"Docker build exception: {str(e)}"}

    async def analyze_container_logs(self, log_output: str) -> Dict[str, Any]:
        """Diagnoses errors in container logs."""
        prompt = f"Analyze these Docker container logs and identify root cause and resolution steps:\n\n{log_output[:1500]}"
        res = await model_router.execute_with_failover(prompt=prompt, category="debugging")
        return {
            "status": "success",
            "diagnosis": res.get("response")
        }


docker_manager = DockerManager()
