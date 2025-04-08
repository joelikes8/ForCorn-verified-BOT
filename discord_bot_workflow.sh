#!/bin/bash
# Discord Bot Workflow Script for Replit workflows
# This script is meant to be referenced in the .replit file

echo "========================================================="
echo "          DISCORD BOT WORKFLOW SCRIPT                   "
echo "========================================================="

# Set the environment variables
export DISCORD_BOT_WORKFLOW=true
export NO_WEB_SERVER=true
export BOT_ONLY_MODE=true

# Run the main.py script which will detect the environment variables
# and start the standalone bot
python main.py