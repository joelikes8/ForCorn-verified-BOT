#!/usr/bin/env python3
"""
Direct Bot Launcher

This script imports and runs the completely isolated bot.
It avoids any imports from the main project to prevent conflicts.
"""
import os
import sys
import subprocess

# Set environment variables to avoid conflicts with web app
os.environ["PORT"] = "9000"
os.environ["DISCORD_BOT_WORKFLOW"] = "true"
os.environ["BOT_ONLY_MODE"] = "true"
os.environ["NO_WEB_SERVER"] = "true"
os.environ["SKIP_WEBAPP"] = "true"

# Print header
print("="*80)
print("DIRECT BOT LAUNCHER")
print("This script avoids any imports from the main project")
print("="*80)

# Run the standalone_discord_bot.py directly
try:
    print("Starting standalone Discord bot...")
    subprocess.run([sys.executable, "standalone_discord_bot.py"], check=True)
except Exception as e:
    print(f"Error starting bot: {e}")
    sys.exit(1)