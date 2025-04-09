#!/bin/bash

# Start the Discord bot in the background using nohup
# This script should be used for manual testing only, not for production

echo "Starting Discord bot in the background..."

# Set environment variables
export DISCORD_BOT_WORKFLOW=true
export BOT_ONLY_MODE=true
export NO_WEB_SERVER=true
export PORT=9000

# Start the bot with nohup
nohup python workflow_bot.py > bot_output.log 2>&1 &

# Get and display the process ID
BOT_PID=$!
echo "Bot started with process ID: $BOT_PID"
echo "View logs with: tail -f bot_output.log"
echo "Stop bot with: kill $BOT_PID"