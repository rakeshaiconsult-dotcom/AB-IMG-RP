#!/bin/bash
set -e

echo "=========================================="
echo "Email Agent Container Starting"
echo "=========================================="
echo "Timezone: $TZ"
echo "Schedule: Every 30 minutes"
echo "=========================================="

if [ ! -f /app/.env ]; then
    echo "WARNING: .env file not found. Make sure environment variables are set."
fi

echo "Starting cron service (executes every 30 minutes)..."
cron

echo "Cron service started. Tailing logs..."
tail -f /var/log/cron.log
