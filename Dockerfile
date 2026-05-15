FROM node:22-alpine AS frontend-builder

WORKDIR /frontend

COPY frontend/package.json frontend/tsconfig.json frontend/tsconfig.app.json frontend/vite.config.ts frontend/index.html ./
COPY frontend/.env.example ./
COPY frontend/src ./src

RUN npm install
RUN npm run build

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

WORKDIR /app

RUN pip install --no-cache-dir uv==0.7.18

COPY pyproject.toml README.md ./
COPY src ./src
COPY frontend ./frontend

RUN uv sync --no-dev

COPY --from=frontend-builder /frontend/dist ./frontend/dist

EXPOSE 8000

CMD ["uv", "run", "agentic-starter", "serve", "--host", "0.0.0.0", "--port", "8000"]
