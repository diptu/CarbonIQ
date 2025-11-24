#!/bin/bash
set -e

echo "Running user_service..."


exec uvicorn user_service.app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload
