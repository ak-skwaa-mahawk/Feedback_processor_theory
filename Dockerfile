# syntax=docker/dockerfile:1.7
FROM rust:1.85-slim AS chef
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install cargo-chef for dependency caching
RUN cargo install cargo-chef --version 0.1.67 --locked

FROM chef AS planner
COPY . .
RUN cargo chef prepare --recipe-path recipe.json

FROM chef AS builder
WORKDIR /app

# Copy cached dependencies
COPY --from=planner /app/recipe.json recipe.json
RUN cargo chef cook --release --recipe-path recipe.json

# Copy full source
COPY . .

# Build only the inference backend binary (workspace-aware)
RUN cargo build --release -p isst-toft-inference-backend --bin isst-toft-backend

# Runtime stage (minimal)
FROM debian:bookworm-slim AS runtime
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

# Copy the compiled binary
COPY --from=builder /app/target/release/isst-toft-backend /usr/local/bin/isst-toft-backend

# Expose gRPC port
EXPOSE 50051

# Run as non-root for security
USER 1000:1000

ENTRYPOINT ["isst-toft-backend"]