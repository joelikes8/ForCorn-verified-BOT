#!/bin/bash

# This script directly starts the Discord bot in complete isolation
# without importing any web application modules.

# Set environment variables to avoid conflicts
export PORT=9000
export DISCORD_BOT_WORKFLOW=true
export BOT_ONLY_MODE=true
export NO_WEB_SERVER=true
export PYTHONPATH=.

# Print header
echo "====================================================="
echo "STARTING DISCORD BOT IN DIRECT ISOLATION MODE"
echo "This script bypasses all web app imports completely"
echo "====================================================="

# Run the standalone bot directly
exec python standalone_discord_bot.py