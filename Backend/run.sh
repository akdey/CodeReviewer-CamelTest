#!/usr/bin/env bash

# Exit on first failure
set -e

echo "🔄 Syncing python dependencies with uv..."
uv sync

echo "🚀 Starting FastAPI server on port 8000..."
# Start the uvicorn server directly using the synced uv environment mapping
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
