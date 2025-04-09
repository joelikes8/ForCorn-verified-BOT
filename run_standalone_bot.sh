#!/bin/bash

# Kill any existing processes
pkill -f "python" || true
pkill -f "gunicorn" || true
pkill -f "flask" || true

# Set environment variables for bot-only mode
export DISCORD_BOT_WORKFLOW=true
export BOT_ONLY_MODE=true
export NO_WEB_SERVER=true
export PORT=9000
export PYTHONPATH=.

# Print header
echo "================================================="
echo "RUNNING STANDALONE DISCORD BOT WITH ALL COMMANDS"
echo "================================================="

# Run the standalone bot directly with nohup to keep it running
nohup python standalone_discord_bot.py > bot_output.log 2>&1 &

# Wait a moment
sleep 2

# Show log
echo "Bot started! Recent log output:"
tail -f bot_output.log