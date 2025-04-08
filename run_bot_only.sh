#!/bin/bash
# Discord Bot Only Workflow Script
# This script runs the bot-only implementation

# Force the bot-only environment
export DISCORD_BOT_WORKFLOW=true
export NO_WEB_SERVER=true
export BOT_ONLY_MODE=true

# Run the dedicated bot_only script
python bot_only.py
