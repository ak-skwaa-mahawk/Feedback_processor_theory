# syntax=docker/dockerfile:1.6
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl && rm -rf /var/lib/apt/lists/*
COPY requirements*.txt ./
RUN pip install --no-cache-dir -r requirements-test.txt && pip install --no-cache-dir -e .
COPY . .
EXPOSE 8081
CMD ["uvicorn","synara_core.modules.handshake.service:app","--host","0.0.0.0","--port","8081"]
