#!/usr/bin/env bash
set -euo pipefail

# NeonCompliance - Development Environment Startup Script
# Starts all services: Docker (Postgres, NATS, LocalStack), Phoenix, Rust agents, Next.js frontend

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🚀 Starting NeonCompliance Development Environment..."

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
  export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
fi

# Start Docker services
echo "🐳 Starting Docker services (PostgreSQL, NATS, LocalStack)..."
cd "$PROJECT_ROOT"
docker compose up -d --wait

# Verify all services are healthy
echo "✅ All services are healthy!"
docker compose ps

# Start Phoenix server in background
echo "🔥 Starting Phoenix backend server..."
cd "$PROJECT_ROOT/backend"
iex -S mix phx.server &
PHOENIX_PID=$!

# Start Rust agents in background
echo "🦀 Starting Rust agent workers..."
cd "$PROJECT_ROOT/agents"
cargo run &
RUST_PID=$!

# Start Next.js frontend
echo "⚛️  Starting Next.js frontend..."
cd "$PROJECT_ROOT/frontend"
npm run dev &
NEXT_PID=$!

echo ""
echo "✅ All services started!"
echo ""
echo "📍 Service URLs:"
echo "  - Frontend:    http://localhost:3000"
echo "  - Backend API: http://localhost:4000/api/v1"
echo "  - Phoenix Dashboard: http://localhost:4000/dev/dashboard"
echo "  - PostgreSQL:  localhost:5432"
echo "  - NATS:        localhost:4222"
echo "  - LocalStack:  http://localhost:4566"
echo ""
echo "🛑 To stop all services: docker compose down"
echo "   PIDs: Phoenix=$PHOENIX_PID, Rust=$RUST_PID, Next=$NEXT_PID"
echo ""
echo "Press Ctrl+C to stop"

# Wait for user interrupt with graceful shutdown
trap "echo ''; echo '🛑 Graceful shutdown...'; \
  kill -TERM $PHOENIX_PID $RUST_PID $NEXT_PID 2>/dev/null; \
  echo '⏳ Waiting 5s for services to shut down...'; \
  sleep 5; \
  kill -KILL $PHOENIX_PID $RUST_PID $NEXT_PID 2>/dev/null; \
  docker compose down -t 10; \
  echo '✅ All services stopped'; \
  exit 0" INT TERM

wait
