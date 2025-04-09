#!/bin/bash
# Script to run the Discord bot manually with all commands
set -e

echo "Starting Discord bot with full command set..."

# Kill any existing web server processes to free up the port
pkill -f "python.*main\.py" || true
pkill -f "gunicorn" || true
sleep 1

# Set environment variables
export DISCORD_BOT_WORKFLOW=true
export BOT_ONLY_MODE=true
export NO_WEB_SERVER=true

# Run the standalone bot which has all 20 commands
python standalone_discord_bot.py