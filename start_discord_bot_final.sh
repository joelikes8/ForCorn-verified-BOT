#!/bin/bash
# Discord Bot Starter Script
# This is the final version that directly starts the standalone Discord bot
# with all necessary environment variables and proper process cleanup

echo "========================================================"
echo "STARTING DISCORD BOT IN ISOLATED MODE"
echo "========================================================"

# Kill any existing processes to avoid port conflicts
echo "Killing any existing Python processes..."
pkill -f "python" || true
pkill -f "gunicorn" || true
pkill -f "flask" || true
sleep 1

# Set all required environment variables
export DISCORD_BOT_WORKFLOW=true
export BOT_ONLY_MODE=true
export NO_WEB_SERVER=true
export PORT=9000
export PYTHONPATH=.

# Print environment information
echo "Environment variables set:"
echo "DISCORD_BOT_WORKFLOW=$DISCORD_BOT_WORKFLOW"
echo "BOT_ONLY_MODE=$BOT_ONLY_MODE" 
echo "NO_WEB_SERVER=$NO_WEB_SERVER"
echo "PORT=$PORT"

# Run the standalone bot
echo "Starting standalone Discord bot..."
exec python standalone_discord_bot.py