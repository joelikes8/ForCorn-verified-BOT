#!/bin/bash
# Discord Bot Workflow Runner Script
# This script is designed to be used with the "discord_bot" workflow in Replit
# and runs a completely isolated version of the Discord bot

echo "Starting Discord bot in completely isolated mode..."

# Set environment variables to prevent any web components from starting
export DISCORD_BOT_WORKFLOW=true
export NO_WEB_SERVER=true
export BOT_ONLY_MODE=true

# Check if DISCORD_TOKEN is set
if [ -z "$DISCORD_TOKEN" ]; then
  echo "ERROR: DISCORD_TOKEN environment variable not set!"
  echo "Please set your Discord bot token in the Secrets tab or .env file"
  exit 1
fi

# Run the completely isolated Discord bot
echo "Running isolated Discord bot..."
python run_discord_bot_only.py
