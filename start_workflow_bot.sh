#!/bin/bash

# This script is designed to start the workflow-specific Discord bot
# It uses a dedicated bot implementation that avoids port conflicts with the web application

echo "========================================================================="
echo "STARTING DISCORD BOT IN WORKFLOW MODE (PORT 9000)"
echo "========================================================================="

# Set environment variables
export DISCORD_BOT_WORKFLOW=true
export BOT_ONLY_MODE=true
export NO_WEB_SERVER=true
export PORT=9000

# Run the workflow-specific bot implementation
python workflow_bot.py