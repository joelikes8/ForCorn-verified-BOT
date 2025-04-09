#!/bin/bash
# Discord bot workflow script
set -e

# Set environment variables to ensure we're running the bot
export DISCORD_BOT_WORKFLOW=true
export BOT_ONLY_MODE=true
export NO_WEB_SERVER=true
export PORT=9000

# Kill any lingering web processes
pkill -f "python.*main\.py" || true
pkill -f "gunicorn" || true
sleep 1

echo "Starting Discord bot via workflow script..."

# Run the standalone bot to ensure all commands are available
python standalone_discord_bot.py