#!/bin/bash
#
# Discord Bot With Reaction Actions Launcher
# This script starts the Discord bot with the reaction actions feature
#

# Set environment variables 
export DISCORD_BOT_WORKFLOW=true
export NO_WEB_SERVER=true
export BOT_ONLY_MODE=true
export PORT=9000

# Print banner
echo "============================================="
echo "  DISCORD BOT WITH REACTION ACTIONS FEATURE  "
echo "============================================="
echo "PID: $$"
echo "Running from: $(pwd)"
echo "Date: $(date)"
echo "============================================="

# Run the Discord bot with cogs
python final_discord_bot.py

# Exit with bot's exit code
exit $?