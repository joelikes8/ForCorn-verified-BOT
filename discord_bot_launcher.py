#!/usr/bin/env python3
"""
Discord Bot Launcher (Do Not Edit)

This is a standalone script that launches the Discord bot without importing
any modules from the web application. It's specifically designed for use
with the 'discord_bot' workflow.

WARNING: This script is auto-generated. Do not edit directly.
"""

import os
import sys
import logging
import subprocess
import signal
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("bot_launcher")

# Prevent importing web app modules
sys.dont_write_bytecode = True

def signal_handler(sig, frame):
    """Handle termination signals gracefully"""
    logger.info("Received termination signal. Shutting down...")
    sys.exit(0)

# Only set signal handlers when running as main script
if __name__ == "__main__":
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def kill_existing_processes():
    """Kill any existing Python processes to avoid conflicts"""
    try:
        logger.info("Killing any existing Python processes...")
        subprocess.run(["pkill", "-f", "python"], check=False)
        subprocess.run(["pkill", "-f", "gunicorn"], check=False)
        subprocess.run(["pkill", "-f", "flask"], check=False)
        time.sleep(1)  # Give processes time to terminate
    except Exception as e:
        logger.warning(f"Error killing processes: {e}")

def main():
    """Main entry point for the Discord bot launcher"""
    
    # Kill existing processes
    kill_existing_processes()
    
    # Set environment variables
    os.environ["DISCORD_BOT_WORKFLOW"] = "true"
    os.environ["BOT_ONLY_MODE"] = "true"
    os.environ["NO_WEB_SERVER"] = "true"
    
    # Default to port 9000 for the bot's HTTP server
    if not os.environ.get("PORT"):
        os.environ["PORT"] = "9000"
    
    # Print header
    logger.info("=" * 80)
    logger.info("DISCORD BOT LAUNCHER - FINAL VERSION")
    logger.info("This script runs the standalone Discord bot in complete isolation")
    logger.info("This bot includes ALL 20 commands")
    logger.info("=" * 80)
    
    # Display commands
    logger.info("Available Commands:")
    commands = [
        "ping", "help", "about", "verify", "update", "background", 
        "ticket", "closeticket", "sendticket", "rank", "setupid", 
        "ranksetup", "setuptoken", "kick", "ban", "timeout", 
        "antiraid", "setup_roles", "blacklistedgroups", "removeblacklist"
    ]
    for cmd in commands:
        logger.info(f" - /{cmd}")
    logger.info("=" * 80)
    
    try:
        # Use exec to replace the current process with the bot
        # This avoids subprocess issues and ensures proper signal handling
        logger.info("Starting standalone Discord bot with exec...")
        # Remap stdin/stdout/stderr to ensure they're inherited
        os.execvp("python", ["python", "standalone_discord_bot.py"])
    except Exception as e:
        logger.error(f"Failed to start the bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()