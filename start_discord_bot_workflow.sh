#!/bin/bash
# Discord Bot Workflow Launcher
# This script sets the environment variables needed for the bot-only mode

echo "========================================================="
echo "          STARTING DISCORD BOT WORKFLOW MODE            "
echo "========================================================="

# Set the environment variables
export DISCORD_BOT_WORKFLOW=true
export NO_WEB_SERVER=true
export BOT_ONLY_MODE=true

# Run the discord bot via the main.py script
python main.py
