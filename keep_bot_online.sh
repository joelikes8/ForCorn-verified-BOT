#!/bin/bash
# Keep Bot Online Shell Script
# This runs the bot monitor in the background so it stays online even if you close the terminal

# Kill any existing monitor or bot processes first
echo "Killing existing bot processes..."
pkill -f "python.*final_discord_bot.py" || true
pkill -f "python.*keep_bot_online.py" || true
sleep 2

# Make script executable if it isn't already
chmod +x keep_bot_online.py

# Setup log directory
mkdir -p logs

# Start the monitor in the background with output redirected to log file
echo "Starting bot monitor in the background..."
nohup python keep_bot_online.py > logs/bot_monitor_output.log 2>&1 &

# Get the process ID to show the user
PID=$!
echo "Bot monitor started with PID: $PID"
echo "The bot will remain online even if you close this terminal"
echo "To view logs: cat logs/bot_monitor_output.log"
echo "To stop the bot: pkill -f keep_bot_online.py"