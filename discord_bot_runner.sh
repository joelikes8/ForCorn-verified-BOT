#!/bin/bash

# Discord Bot Runner Script
# This script is designed to run the Discord bot in workflow mode
# without conflicting with the web server.

echo "=================================================================================="
echo "STARTING DISCORD BOT IN WORKFLOW MODE"
echo "=================================================================================="

# Set environment variables
export DISCORD_BOT_WORKFLOW=true
export BOT_ONLY_MODE=true
export NO_WEB_SERVER=true

# Try to run the optimized workflow runner
if [ -f "discord_bot_workflow_runner.py" ]; then
    echo "Starting bot using discord_bot_workflow_runner.py..."
    python discord_bot_workflow_runner.py
    exit $?
fi

# If the workflow runner isn't available, try the simplified runner
if [ -f "run_bot_only.py" ]; then
    echo "Starting bot using run_bot_only.py..."
    python run_bot_only.py
    exit $?
fi

# If all else fails, run the standalone bot directly
if [ -f "standalone_discord_bot.py" ]; then
    echo "Starting bot using standalone_discord_bot.py..."
    python standalone_discord_bot.py
    exit $?
fi

echo "No bot script found! Make sure one of the following exists:"
echo "- discord_bot_workflow_runner.py"
echo "- run_bot_only.py"
echo "- standalone_discord_bot.py"
exit 1