#!/bin/bash
set -e

echo "Running auth_service..."


exec uvicorn auth_service.app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload
