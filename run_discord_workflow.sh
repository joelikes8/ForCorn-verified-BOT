#!/bin/bash
# Discord Bot Workflow Runner - BOT ONLY
# This script runs only the Discord bot with no web components

echo "Starting Discord bot in dedicated workflow..."

# Set environment variables to indicate we are in bot-only mode
export DISCORD_BOT_WORKFLOW=true
export NO_WEB_SERVER=true
export BOT_ONLY_MODE=true

# Run the dedicated bot-only script
python discord_bot_only.py
