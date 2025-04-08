#!/bin/bash
# Discord Bot Runner Script
# This script sets an environment variable before starting

# Set BOT_ONLY_MODE environment variable
export DISCORD_BOT_WORKFLOW=true
export NO_WEB_SERVER=true
export BOT_ONLY_MODE=true

# Run the standalone_discord_bot.py script directly
python standalone_discord_bot.py
