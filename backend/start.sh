#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

mkdir -p logs

echo "========================================="
echo "  SeeDance Backend Startup"
echo "========================================="
echo "URL: http://localhost:8000"
echo "Docs: http://localhost:8000/docs"
echo "========================================="

exec python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
