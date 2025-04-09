#!/bin/bash
# Final Discord Bot Runner
# This script directly runs the final Discord bot with all 20 commands

echo "========================================================"
echo "STARTING FINAL DISCORD BOT WITH ALL 20 COMMANDS"
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

# Make sure the required directories exist
mkdir -p data

# Run the bot directly
echo "Starting final Discord bot with all 20 commands..."
exec python final_discord_bot.py