#!/bin/bash

# Set environment variables for the bot only
export PORT=9000
export DISCORD_BOT_WORKFLOW=true
export BOT_ONLY_MODE=true
export NO_WEB_SERVER=true

# Run the standalone bot directly
exec python standalone_discord_bot.py