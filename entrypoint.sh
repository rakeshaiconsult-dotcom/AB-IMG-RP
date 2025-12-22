#!/bin/bash
set -e

echo "=========================================="
echo "Email Agent Container Starting"
echo "=========================================="
echo "Timezone: $TZ"
echo "Run mode: direct execution of main.py"
echo "=========================================="

if [ ! -f /app/.env ]; then
    echo "WARNING: .env file not found. Make sure environment variables are set."
fi

echo "Starting email agent..."
exec python /app/main.py
