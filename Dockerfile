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
FROM rust:1.85-slim AS builder
WORKDIR /app
COPY . .
RUN cargo build --release --bin isst-toft-backend

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/target/release/isst-toft-backend /usr/local/bin/
EXPOSE 50051
CMD ["isst-toft-backend"]