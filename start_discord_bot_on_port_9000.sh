#!/bin/bash

# Script to start Discord bot on port 9000 to avoid conflicts
echo "Starting Discord bot on port 9000..."

# Set environment variables
export DISCORD_BOT_WORKFLOW=true
export BOT_ONLY_MODE=true
export NO_WEB_SERVER=true
export PORT=9000

# Run the bot with dedicated script
python run_discord_bot_workflow.py