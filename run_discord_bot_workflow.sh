#!/bin/bash

# Explicitly set port to avoid conflicts with the web application
export PORT=9000
export DISCORD_BOT_WORKFLOW=true
export BOT_ONLY_MODE=true
export NO_WEB_SERVER=true

# Run the standalone bot directly
python standalone_discord_bot.py