#!/usr/bin/env bash
set -euo pipefail

echo "=== Building frontend ==="
cd frontend
npm ci
npm run build
cd ..

echo "=== Copying dist → backend/static ==="
rm -rf backend/static
cp -r frontend/dist backend/static

echo "=== Build complete ==="
echo "Run: cd backend && uvicorn app.main:app --port 8000"
