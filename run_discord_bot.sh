#!/bin/bash
#
# Discord Bot Launcher Script
# This script starts the Discord bot as a standalone process
#

# Set environment variables to indicate bot-only mode
export DISCORD_BOT_WORKFLOW=true
export NO_WEB_SERVER=true
export BOT_ONLY_MODE=true
export PORT=9000

# Print banner
echo "============================================="
echo "         STARTING DISCORD BOT ONLY           "
echo "============================================="
echo "PID: $$"
echo "Running from: $(pwd)"
echo "Date: $(date)"
echo "============================================="

# Run the Discord bot with cogs
python final_discord_bot.py

# Exit with bot's exit code
exit $?