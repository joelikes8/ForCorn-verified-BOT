#!/bin/bash
# This script launches the Discord bot directly
set -e

# Print some debug information
echo "Starting Discord bot..."
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"

# Set environment variables
export DISCORD_BOT_WORKFLOW=true
export BOT_ONLY_MODE=true
export NO_WEB_SERVER=true
export PORT=9000

# Kill any Flask/Gunicorn processes that might be running
pkill -f "python.*main\.py" || true
pkill -f "gunicorn" || true
sleep 1

# Launch the Discord bot
python discord_bot_main.py